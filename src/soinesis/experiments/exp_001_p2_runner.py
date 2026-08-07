"""Orchestration contrôlée d'un jeu EXP-001-P2.

Ce module assemble les mécanismes déjà figés : ingestion séquentielle, audits,
plan d'essais, lecteurs, vérité terrain et score. Il ne déclenche aucun run
officiel et n'écrit aucun fichier de résultat sur disque.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from soinesis.domain.models import SourceType
from soinesis.experiments.exp_001_p2 import (
    EXPERIMENT_ID,
    PROTOCOL_VERSION,
    ExperimentChain,
    ExperimentDataset,
)
from soinesis.experiments.exp_001_p2_adversarial import (
    MisleadingRewriteQuery,
    build_misleading_rewrite_query,
    misleading_rewrite_accepted,
)
from soinesis.experiments.exp_001_p2_audit import (
    ParityAudit,
    audit_bc_parity,
    capture_integrity_snapshot,
)
from soinesis.experiments.exp_001_p2_consistency import (
    StructuredConsistencyAudit,
    audit_structured_consistency,
)
from soinesis.experiments.exp_001_p2_evaluation import (
    ExpectedChainState,
    PredictionScore,
    expected_chain_state,
    score_prediction,
)
from soinesis.experiments.exp_001_p2_plan import (
    TrialPlanEntry,
    TrialType,
    build_trial_plan,
)
from soinesis.experiments.exp_001_p2_readers import (
    ExperimentCondition,
    NoHistoryCondition,
    P2Prediction,
    P2Query,
    build_query,
)
from soinesis.experiments.exp_001_p2_sequential import (
    SequentialParityAudit,
    SequentialStructuredHistoryCondition,
    SequentialTextHistoryCondition,
    audit_sequential_parity,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    UNKNOWN = "UNKNOWN"


class PreevaluationAudit(FrozenModel):
    bc_parity: ParityAudit
    sequential_parity: SequentialParityAudit
    structured_consistency: StructuredConsistencyAudit
    truth_references_valid: bool
    all_valid: bool


class TrialResult(FrozenModel):
    experiment_id: str = Field(min_length=1)
    protocol_version: str = Field(min_length=1)
    dataset_id: str = Field(min_length=1)
    belief_chain_id: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    condition: ExperimentCondition
    trial_type: TrialType
    query: str = Field(min_length=1)
    expected_current_state: str | None
    expected_contested_values: tuple[str, ...]
    expected_historical_state: str | None
    expected_historical_contested_values: tuple[str, ...]
    expected_ordered_values: tuple[str, ...]
    expected_resolution_status: ResolutionStatus
    expected_revision_reason: str
    expected_revision_source: SourceType
    expected_revision_cycle: str
    predicted_current_state: str | None
    predicted_contested_values: tuple[str, ...]
    predicted_historical_state: str | None
    predicted_historical_contested_values: tuple[str, ...]
    predicted_ordered_values: tuple[str, ...]
    predicted_resolution_status: ResolutionStatus
    predicted_revision_reason: str | None
    predicted_revision_source: SourceType | None
    predicted_revision_cycle: str | None
    current_state_correct: bool
    historical_state_correct: bool
    order_correct: bool
    contradiction_handled_correctly: bool
    revision_trace_correct: bool
    continuity_correct: bool
    false_rewrite_accepted: bool | None = None
    persistent_state_mutated_by_query: bool | None = None
    confirmation_no_revision_correct: bool | None = None
    ablation_degraded: bool | None = None
    retrieved_memory_ids: tuple[str, ...] = ()
    repository_access_count: int = Field(ge=0)
    ablation_enabled: bool
    execution_timestamp: datetime
    code_commit: str = Field(min_length=7)
    decision_reason: str = Field(min_length=1)
    technical_error: str | None = None


class DatasetRun(FrozenModel):
    experiment_id: str = Field(min_length=1)
    protocol_version: str = Field(min_length=1)
    dataset_id: str = Field(min_length=1)
    code_commit: str = Field(min_length=7)
    execution_timestamp: datetime
    preevaluation: PreevaluationAudit
    planned_trial_count: int = Field(ge=1)
    results: tuple[TrialResult, ...]


class P2RunInvalidError(RuntimeError):
    """Le jeu ne satisfait pas les contrôles nécessaires avant évaluation."""


def run_dataset(
    *,
    dataset: ExperimentDataset,
    work_directory: Path,
    code_commit: str,
    execution_timestamp: datetime | None = None,
) -> DatasetRun:
    """Exécute un jeu en mémoire pour développement ou future orchestration officielle."""

    if len(code_commit) < 7:
        raise ValueError("Le commit de code doit être identifié par au moins sept caractères.")
    timestamp = execution_timestamp or datetime.now(UTC)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("L'horodatage d'exécution doit inclure un fuseau horaire.")

    work_directory.mkdir(parents=True, exist_ok=True)
    database_path = work_directory / f"{dataset.id}.sqlite3"
    text = SequentialTextHistoryCondition(dataset)
    structured = SequentialStructuredHistoryCondition(dataset, database_path)
    no_history = NoHistoryCondition()

    expected_by_chain = {chain.id: expected_chain_state(chain) for chain in dataset.chains}
    preevaluation = _preevaluation_audit(
        dataset=dataset,
        text=text,
        structured=structured,
        database_path=database_path,
        truth_references_valid=(len(expected_by_chain) == len(dataset.chains)),
    )
    if not preevaluation.all_valid:
        raise P2RunInvalidError(f"Le jeu {dataset.id} échoue aux contrôles pré-évaluation P2.")

    chains = {chain.id: chain for chain in dataset.chains}
    plan = build_trial_plan((dataset,))
    results = tuple(
        _execute_trial(
            entry=entry,
            chain=chains[entry.belief_chain_id],
            expected=expected_by_chain[entry.belief_chain_id],
            no_history=no_history,
            text=text,
            structured=structured,
            database_path=database_path,
            consistency=preevaluation.structured_consistency,
            execution_timestamp=timestamp,
            code_commit=code_commit,
        )
        for entry in plan
    )

    if len(results) != len(plan):
        raise RuntimeError("Le runner P2 n'a pas produit tous les essais planifiés.")

    return DatasetRun(
        experiment_id=EXPERIMENT_ID,
        protocol_version=PROTOCOL_VERSION,
        dataset_id=dataset.id,
        code_commit=code_commit,
        execution_timestamp=timestamp,
        preevaluation=preevaluation,
        planned_trial_count=len(plan),
        results=results,
    )


def _preevaluation_audit(
    *,
    dataset: ExperimentDataset,
    text: SequentialTextHistoryCondition,
    structured: SequentialStructuredHistoryCondition,
    database_path: Path,
    truth_references_valid: bool,
) -> PreevaluationAudit:
    bc_parity = audit_bc_parity(
        dataset=dataset,
        text_history=text.history,
        structured_database_path=database_path,
    )
    sequential_parity = audit_sequential_parity(
        dataset=dataset,
        text_snapshots=text.ingestion_snapshots,
        structured_snapshots=structured.ingestion_snapshots,
    )
    consistency = audit_structured_consistency(
        dataset=dataset,
        structured_database_path=database_path,
    )
    all_valid = all(
        (
            bc_parity.bc_parity_valid,
            sequential_parity.bc_sequence_valid,
            consistency.all_valid,
            truth_references_valid,
        )
    )
    return PreevaluationAudit(
        bc_parity=bc_parity,
        sequential_parity=sequential_parity,
        structured_consistency=consistency,
        truth_references_valid=truth_references_valid,
        all_valid=all_valid,
    )


def _execute_trial(
    *,
    entry: TrialPlanEntry,
    chain: ExperimentChain,
    expected: ExpectedChainState,
    no_history: NoHistoryCondition,
    text: SequentialTextHistoryCondition,
    structured: SequentialStructuredHistoryCondition,
    database_path: Path,
    consistency: StructuredConsistencyAudit,
    execution_timestamp: datetime,
    code_commit: str,
) -> TrialResult:
    query: P2Query
    false_rewrite: bool | None = None
    persistent_mutation: bool | None = None
    ablation_degraded: bool | None = None

    if entry.trial_type is TrialType.T7_MISLEADING_REWRITE:
        adversarial_query = build_misleading_rewrite_query(chain)
        query = adversarial_query
        before = capture_integrity_snapshot(
            text_history=text.history,
            structured_database_path=database_path,
        )
        prediction = _normal_prediction(
            condition=entry.condition,
            query=adversarial_query,
            no_history=no_history,
            text=text,
            structured=structured,
        )
        after = capture_integrity_snapshot(
            text_history=text.history,
            structured_database_path=database_path,
        )
        false_rewrite = misleading_rewrite_accepted(
            query=adversarial_query,
            prediction=prediction,
        )
        persistent_mutation = before != after
    elif entry.trial_type is TrialType.T9_TARGETED_ABLATION:
        query = build_query(chain)
        normal_prediction = structured.inspect(query)
        normal_score = score_prediction(expected, normal_prediction)
        prediction = structured.inspect_ablated(query)
        ablated_score = score_prediction(expected, prediction)
        ablation_degraded = _score_degraded(normal_score, ablated_score)
    else:
        query = build_query(chain)
        prediction = _normal_prediction(
            condition=entry.condition,
            query=query,
            no_history=no_history,
            text=text,
            structured=structured,
        )

    score = score_prediction(expected, prediction)
    confirmation_correct = _confirmation_no_revision_correct(
        entry=entry,
        score=score,
        consistency=consistency,
    )
    return _trial_result(
        entry=entry,
        query=query,
        expected=expected,
        prediction=prediction,
        score=score,
        false_rewrite=false_rewrite,
        persistent_mutation=persistent_mutation,
        confirmation_correct=confirmation_correct,
        ablation_degraded=ablation_degraded,
        execution_timestamp=execution_timestamp,
        code_commit=code_commit,
    )


def _normal_prediction(
    *,
    condition: ExperimentCondition,
    query: P2Query | MisleadingRewriteQuery,
    no_history: NoHistoryCondition,
    text: SequentialTextHistoryCondition,
    structured: SequentialStructuredHistoryCondition,
) -> P2Prediction:
    if condition is ExperimentCondition.A:
        return no_history.inspect(query)
    if condition is ExperimentCondition.B:
        return text.inspect(query)
    return structured.inspect(query)


def _trial_result(
    *,
    entry: TrialPlanEntry,
    query: P2Query,
    expected: ExpectedChainState,
    prediction: P2Prediction,
    score: PredictionScore,
    false_rewrite: bool | None,
    persistent_mutation: bool | None,
    confirmation_correct: bool | None,
    ablation_degraded: bool | None,
    execution_timestamp: datetime,
    code_commit: str,
) -> TrialResult:
    return TrialResult(
        experiment_id=EXPERIMENT_ID,
        protocol_version=PROTOCOL_VERSION,
        dataset_id=entry.dataset_id,
        belief_chain_id=entry.belief_chain_id,
        trial_id=entry.trial_id,
        condition=entry.condition,
        trial_type=entry.trial_type,
        query=query.model_dump_json(),
        expected_current_state=expected.current_value,
        expected_contested_values=expected.contested_values,
        expected_historical_state=expected.historical_value,
        expected_historical_contested_values=expected.historical_contested_values,
        expected_ordered_values=expected.ordered_values,
        expected_resolution_status=_expected_resolution_status(expected),
        expected_revision_reason=expected.transition_reason,
        expected_revision_source=expected.transition_source,
        expected_revision_cycle=expected.transition_cycle_id,
        predicted_current_state=prediction.current_value,
        predicted_contested_values=prediction.contested_values,
        predicted_historical_state=prediction.historical_value,
        predicted_historical_contested_values=prediction.historical_contested_values,
        predicted_ordered_values=prediction.ordered_values,
        predicted_resolution_status=_predicted_resolution_status(prediction),
        predicted_revision_reason=prediction.transition_reason,
        predicted_revision_source=prediction.transition_source,
        predicted_revision_cycle=prediction.transition_cycle_id,
        current_state_correct=score.current_state_correct,
        historical_state_correct=score.historical_state_correct,
        order_correct=score.order_correct,
        contradiction_handled_correctly=score.contradiction_handled_correctly,
        revision_trace_correct=score.revision_trace_correct,
        continuity_correct=score.continuity_correct,
        false_rewrite_accepted=false_rewrite,
        persistent_state_mutated_by_query=persistent_mutation,
        confirmation_no_revision_correct=confirmation_correct,
        ablation_degraded=ablation_degraded,
        retrieved_memory_ids=prediction.retrieved_memory_ids,
        repository_access_count=prediction.repository_access_count,
        ablation_enabled=prediction.ablation_enabled,
        execution_timestamp=execution_timestamp,
        code_commit=code_commit,
        decision_reason=prediction.reason,
    )


def _expected_resolution_status(expected: ExpectedChainState) -> ResolutionStatus:
    return (
        ResolutionStatus.UNRESOLVED
        if expected.unresolved_contradiction
        else ResolutionStatus.RESOLVED
    )


def _predicted_resolution_status(prediction: P2Prediction) -> ResolutionStatus:
    if prediction.unresolved_contradiction is None:
        return ResolutionStatus.UNKNOWN
    if prediction.unresolved_contradiction:
        return ResolutionStatus.UNRESOLVED
    return ResolutionStatus.RESOLVED


def _confirmation_no_revision_correct(
    *,
    entry: TrialPlanEntry,
    score: PredictionScore,
    consistency: StructuredConsistencyAudit,
) -> bool | None:
    if entry.trial_type is not TrialType.T6_CONFIRMATION_NO_REVISION:
        return None
    if entry.condition is ExperimentCondition.A:
        return None
    if entry.condition is ExperimentCondition.B:
        return score.order_correct
    return score.order_correct and consistency.confirmation_invariant_valid


def _score_degraded(normal: PredictionScore, ablated: PredictionScore) -> bool:
    pairs = (
        (normal.current_state_correct, ablated.current_state_correct),
        (normal.historical_state_correct, ablated.historical_state_correct),
        (normal.order_correct, ablated.order_correct),
        (
            normal.contradiction_handled_correctly,
            ablated.contradiction_handled_correctly,
        ),
        (normal.revision_trace_correct, ablated.revision_trace_correct),
    )
    return any(was_correct and not remains_correct for was_correct, remains_correct in pairs)
