"""Analyse déterministe des résultats bruts EXP-001-P2.

Cette couche est volontairement séparée de l'exécution. Elle vérifie d'abord
l'intégrité du bundle exporté puis applique uniquement les métriques et seuils
préenregistrés dans le protocole P2. Elle ne lance aucune expérience.
"""

from __future__ import annotations

import json
from collections import defaultdict
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from soinesis.experiments.exp_001_p2 import (
    EXPERIMENT_ID,
    PROTOCOL_VERSION,
    ExperimentDataset,
    load_datasets,
)
from soinesis.experiments.exp_001_p2_export import (
    FROZEN_DATASET_SHA256,
    ArtifactChecksums,
    FreezeManifest,
    sha256_file,
    trial_plan_sha256,
)
from soinesis.experiments.exp_001_p2_plan import TrialType, build_trial_plan
from soinesis.experiments.exp_001_p2_readers import ExperimentCondition
from soinesis.experiments.exp_001_p2_runner import TrialResult


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class HypothesisAssessment(StrEnum):
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    ABSOLUTE_INTEGRITY_ONLY = "ABSOLUTE_INTEGRITY_ONLY"
    AUTOMATED_CRITERIA_MET_MANUAL_AUDIT_REQUIRED = (
        "AUTOMATED_CRITERIA_MET_MANUAL_AUDIT_REQUIRED"
    )


class DatasetConditionScore(FrozenModel):
    dataset_id: str = Field(min_length=1)
    condition: ExperimentCondition
    successes: int = Field(ge=0)
    total: int = Field(ge=1)
    rate: float = Field(ge=0.0, le=1.0)


class ComparativeScore(FrozenModel):
    b_overall_rate: float = Field(ge=0.0, le=1.0)
    c_overall_rate: float = Field(ge=0.0, le=1.0)
    mean_c_minus_b: float = Field(ge=-1.0, le=1.0)
    c_better_dataset_count: int = Field(ge=0)
    dataset_count: int = Field(ge=1)
    by_dataset: tuple[DatasetConditionScore, ...]
    assessment: HypothesisAssessment


class RewriteAnalysis(FrozenModel):
    b_false_rewrite_rate: float = Field(ge=0.0, le=1.0)
    c_false_rewrite_rate: float = Field(ge=0.0, le=1.0)
    c_persistent_mutation_count: int = Field(ge=0)
    comparative_advantage: float = Field(ge=-1.0, le=1.0)
    assessment: HypothesisAssessment


class AblationAnalysis(FrozenModel):
    trial_count: int = Field(ge=1)
    forbidden_access_total: int = Field(ge=0)
    zero_forbidden_access: bool
    degradation_observed: bool
    all_trials_marked_ablated: bool
    manual_hidden_alternative_audit_required: bool = True
    assessment: HypothesisAssessment


class BundleIntegrity(FrozenModel):
    manifest_valid: bool
    checksums_valid: bool
    trial_plan_valid: bool
    preevaluation_valid: bool
    result_count_valid: bool
    official_dataset_hash: bool
    complete_dataset_suite: bool
    all_valid: bool


class P2Analysis(FrozenModel):
    experiment_id: str
    protocol_version: str
    code_commit: str
    integrity: BundleIntegrity
    primary_continuity_h01_h02_h03: ComparativeScore
    traceability_h04: ComparativeScore
    rewrite_h05: RewriteAnalysis
    ablation_h06: AblationAnalysis


class P2AnalysisError(RuntimeError):
    """Le bundle ne peut pas être analysé sans violer les contrôles d'intégrité."""


def analyze_run_bundle(
    *,
    bundle_directory: Path,
    dataset_path: Path,
    require_complete_suite: bool = True,
    require_official_dataset: bool = True,
) -> P2Analysis:
    """Vérifie un bundle exporté, puis applique les critères préenregistrés."""

    manifest, results, integrity = _load_verified_bundle(
        bundle_directory=bundle_directory,
        dataset_path=dataset_path,
        require_complete_suite=require_complete_suite,
        require_official_dataset=require_official_dataset,
    )
    if not integrity.all_valid:
        raise P2AnalysisError("Le bundle P2 échoue aux contrôles d'intégrité pré-analyse.")

    return P2Analysis(
        experiment_id=manifest.experiment_id,
        protocol_version=manifest.protocol_version,
        code_commit=manifest.code_commit,
        integrity=integrity,
        primary_continuity_h01_h02_h03=_primary_continuity(results, manifest.dataset_ids),
        traceability_h04=_traceability(results, manifest.dataset_ids),
        rewrite_h05=_rewrite_analysis(results),
        ablation_h06=_ablation_analysis(results),
    )


def _load_verified_bundle(
    *,
    bundle_directory: Path,
    dataset_path: Path,
    require_complete_suite: bool,
    require_official_dataset: bool,
) -> tuple[FreezeManifest, tuple[TrialResult, ...], BundleIntegrity]:
    manifest_path = bundle_directory / "freeze-manifest.json"
    preevaluation_path = bundle_directory / "preevaluation.json"
    raw_trials_path = bundle_directory / "raw-trials.jsonl"
    checksums_path = bundle_directory / "checksums.json"

    manifest = FreezeManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    checksums = ArtifactChecksums.model_validate_json(checksums_path.read_text(encoding="utf-8"))
    checksums_valid = all(
        (
            sha256_file(manifest_path) == checksums.freeze_manifest_sha256,
            sha256_file(preevaluation_path) == checksums.preevaluation_sha256,
            sha256_file(raw_trials_path) == checksums.raw_trials_sha256,
        )
    )
    if not checksums_valid:
        raise P2AnalysisError("Le bundle P2 échoue aux contrôles d'intégrité pré-analyse.")

    datasets = load_datasets(dataset_path)
    selected = _selected_datasets(datasets, manifest.dataset_ids)
    plan = build_trial_plan(selected)
    trial_plan_valid = trial_plan_sha256(plan) == manifest.trial_plan_sha256

    try:
        results = tuple(
            TrialResult.model_validate_json(line)
            for line in raw_trials_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    except ValidationError as error:
        raise P2AnalysisError(
            "Le bundle P2 échoue aux contrôles d'intégrité pré-analyse."
        ) from error
    expected_trial_ids = tuple(entry.trial_id for entry in plan)
    actual_trial_ids = tuple(result.trial_id for result in results)
    result_count_valid = (
        len(results) == manifest.result_count == manifest.planned_trial_count == len(plan)
        and actual_trial_ids == expected_trial_ids
        and all(result.code_commit == manifest.code_commit for result in results)
    )

    preevaluation_payload = json.loads(preevaluation_path.read_text(encoding="utf-8"))
    preevaluation_valid = _preevaluation_all_valid(preevaluation_payload, manifest.dataset_ids)
    dataset_hash = sha256_file(dataset_path)
    manifest_valid = all(
        (
            manifest.experiment_id == EXPERIMENT_ID,
            manifest.protocol_version == PROTOCOL_VERSION,
            manifest.dataset_sha256 == dataset_hash,
            tuple(dataset.id for dataset in selected) == manifest.dataset_ids,
        )
    )
    official_dataset_hash = dataset_hash == FROZEN_DATASET_SHA256
    complete_dataset_suite = manifest.complete_dataset_suite and len(manifest.dataset_ids) == 5

    all_valid = all(
        (
            manifest_valid,
            checksums_valid,
            trial_plan_valid,
            preevaluation_valid,
            result_count_valid,
            (not require_official_dataset or official_dataset_hash),
            (not require_complete_suite or complete_dataset_suite),
        )
    )
    integrity = BundleIntegrity(
        manifest_valid=manifest_valid,
        checksums_valid=checksums_valid,
        trial_plan_valid=trial_plan_valid,
        preevaluation_valid=preevaluation_valid,
        result_count_valid=result_count_valid,
        official_dataset_hash=official_dataset_hash,
        complete_dataset_suite=complete_dataset_suite,
        all_valid=all_valid,
    )
    return manifest, results, integrity


def _selected_datasets(
    datasets: tuple[ExperimentDataset, ...],
    dataset_ids: tuple[str, ...],
) -> tuple[ExperimentDataset, ...]:
    by_id = {dataset.id: dataset for dataset in datasets}
    try:
        return tuple(by_id[dataset_id] for dataset_id in dataset_ids)
    except KeyError as error:
        raise P2AnalysisError(f"Jeu absent du fichier de données : {error.args[0]}.") from error


def _preevaluation_all_valid(payload: object, dataset_ids: tuple[str, ...]) -> bool:
    if not isinstance(payload, list) or len(payload) != len(dataset_ids):
        return False
    observed_ids: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            return False
        dataset_id = item.get("dataset_id")
        preevaluation = item.get("preevaluation")
        if not isinstance(dataset_id, str) or not isinstance(preevaluation, dict):
            return False
        if preevaluation.get("all_valid") is not True:
            return False
        observed_ids.append(dataset_id)
    return tuple(observed_ids) == dataset_ids


def _primary_continuity(
    results: tuple[TrialResult, ...],
    dataset_ids: tuple[str, ...],
) -> ComparativeScore:
    scores: list[DatasetConditionScore] = []
    for dataset_id in dataset_ids:
        for condition in (ExperimentCondition.B, ExperimentCondition.C):
            by_chain: dict[str, dict[TrialType, TrialResult]] = defaultdict(dict)
            for result in results:
                if result.dataset_id != dataset_id or result.condition is not condition:
                    continue
                if result.trial_type in {
                    TrialType.T1_CURRENT_STATE,
                    TrialType.T2_HISTORICAL_STATE,
                    TrialType.T3_CHAIN_ORDER,
                    TrialType.T5_UNRESOLVED_CONTRADICTION,
                }:
                    by_chain[result.belief_chain_id][result.trial_type] = result

            successes = 0
            for chain_trials in by_chain.values():
                historical = chain_trials.get(TrialType.T2_HISTORICAL_STATE)
                order = chain_trials.get(TrialType.T3_CHAIN_ORDER)
                unresolved = chain_trials.get(TrialType.T5_UNRESOLVED_CONTRADICTION)
                current = chain_trials.get(TrialType.T1_CURRENT_STATE)
                if historical is None or order is None or (unresolved is None and current is None):
                    raise P2AnalysisError("Essais incomplets pour le score principal P2.")
                state_correct = (
                    unresolved.contradiction_handled_correctly
                    if unresolved is not None
                    else bool(current and current.current_state_correct)
                )
                successes += int(
                    state_correct and historical.historical_state_correct and order.order_correct
                )

            if not by_chain:
                raise P2AnalysisError("Aucune chaîne disponible pour le score principal P2.")
            scores.append(
                DatasetConditionScore(
                    dataset_id=dataset_id,
                    condition=condition,
                    successes=successes,
                    total=len(by_chain),
                    rate=successes / len(by_chain),
                )
            )
    return _comparative_score(tuple(scores))


def _traceability(
    results: tuple[TrialResult, ...],
    dataset_ids: tuple[str, ...],
) -> ComparativeScore:
    scores: list[DatasetConditionScore] = []
    for dataset_id in dataset_ids:
        for condition in (ExperimentCondition.B, ExperimentCondition.C):
            trials = tuple(
                result
                for result in results
                if result.dataset_id == dataset_id
                and result.condition is condition
                and result.trial_type
                in {TrialType.T4_REVISION_CAUSE, TrialType.T8_TRANSITION_PROVENANCE}
            )
            if not trials:
                raise P2AnalysisError("Aucun essai de traçabilité P2 disponible.")
            successes = sum(result.revision_trace_correct for result in trials)
            scores.append(
                DatasetConditionScore(
                    dataset_id=dataset_id,
                    condition=condition,
                    successes=successes,
                    total=len(trials),
                    rate=successes / len(trials),
                )
            )
    return _comparative_score(tuple(scores))


def _comparative_score(scores: tuple[DatasetConditionScore, ...]) -> ComparativeScore:
    by_dataset: dict[str, dict[ExperimentCondition, DatasetConditionScore]] = defaultdict(dict)
    for score in scores:
        by_dataset[score.dataset_id][score.condition] = score

    differences: list[float] = []
    c_better = 0
    b_successes = 0
    b_total = 0
    c_successes = 0
    c_total = 0
    for dataset_scores in by_dataset.values():
        if set(dataset_scores) != {ExperimentCondition.B, ExperimentCondition.C}:
            raise P2AnalysisError("Comparaison B/C incomplète dans un jeu P2.")
        b_score = dataset_scores[ExperimentCondition.B]
        c_score = dataset_scores[ExperimentCondition.C]
        difference = c_score.rate - b_score.rate
        differences.append(difference)
        c_better += int(difference > 0)
        b_successes += b_score.successes
        b_total += b_score.total
        c_successes += c_score.successes
        c_total += c_score.total

    if not differences:
        raise P2AnalysisError("Aucune comparaison B/C disponible.")
    b_overall = b_successes / b_total
    c_overall = c_successes / c_total
    mean_advantage = sum(differences) / len(differences)
    supported = c_overall >= 0.90 and mean_advantage >= 0.10 and c_better >= 4
    return ComparativeScore(
        b_overall_rate=b_overall,
        c_overall_rate=c_overall,
        mean_c_minus_b=mean_advantage,
        c_better_dataset_count=c_better,
        dataset_count=len(differences),
        by_dataset=scores,
        assessment=(
            HypothesisAssessment.SUPPORTED if supported else HypothesisAssessment.NOT_SUPPORTED
        ),
    )


def _rewrite_analysis(results: tuple[TrialResult, ...]) -> RewriteAnalysis:
    by_condition = {
        condition: tuple(
            result
            for result in results
            if result.trial_type is TrialType.T7_MISLEADING_REWRITE
            and result.condition is condition
        )
        for condition in (ExperimentCondition.B, ExperimentCondition.C)
    }
    if not by_condition[ExperimentCondition.B] or not by_condition[ExperimentCondition.C]:
        raise P2AnalysisError("Essais T7 B/C incomplets.")

    def false_rate(condition: ExperimentCondition) -> float:
        trials = by_condition[condition]
        if any(result.false_rewrite_accepted is None for result in trials):
            raise P2AnalysisError("Un essai T7 ne contient pas son verdict de réécriture.")
        return sum(result.false_rewrite_accepted is True for result in trials) / len(trials)

    b_rate = false_rate(ExperimentCondition.B)
    c_rate = false_rate(ExperimentCondition.C)
    c_mutations = sum(
        result.persistent_state_mutated_by_query is True
        for result in by_condition[ExperimentCondition.C]
    )
    advantage = b_rate - c_rate
    if c_rate <= 0.05 and c_mutations == 0:
        if b_rate == 0.0:
            assessment = HypothesisAssessment.ABSOLUTE_INTEGRITY_ONLY
        elif advantage >= 0.10:
            assessment = HypothesisAssessment.SUPPORTED
        else:
            assessment = HypothesisAssessment.NOT_SUPPORTED
    else:
        assessment = HypothesisAssessment.NOT_SUPPORTED
    return RewriteAnalysis(
        b_false_rewrite_rate=b_rate,
        c_false_rewrite_rate=c_rate,
        c_persistent_mutation_count=c_mutations,
        comparative_advantage=advantage,
        assessment=assessment,
    )


def _ablation_analysis(results: tuple[TrialResult, ...]) -> AblationAnalysis:
    trials = tuple(result for result in results if result.trial_type is TrialType.T9_TARGETED_ABLATION)
    if not trials:
        raise P2AnalysisError("Aucun essai T9 disponible.")
    forbidden_access_total = sum(result.repository_access_count for result in trials)
    zero_access = forbidden_access_total == 0
    degradation = any(result.ablation_degraded is True for result in trials)
    all_ablated = all(result.ablation_enabled for result in trials)
    automated_criteria_met = zero_access and degradation and all_ablated
    return AblationAnalysis(
        trial_count=len(trials),
        forbidden_access_total=forbidden_access_total,
        zero_forbidden_access=zero_access,
        degradation_observed=degradation,
        all_trials_marked_ablated=all_ablated,
        assessment=(
            HypothesisAssessment.AUTOMATED_CRITERIA_MET_MANUAL_AUDIT_REQUIRED
            if automated_criteria_met
            else HypothesisAssessment.NOT_SUPPORTED
        ),
    )
