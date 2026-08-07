"""Exécution déterministe du protocole EXP-001-P1."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from statistics import fmean
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.application.memory import MemoryApplicationService
from soinesis.domain.models import AblationConfiguration, MemoryType, SourceType
from soinesis.infrastructure.sqlite import SQLiteDatabase, SQLiteUnitOfWorkFactory
from soinesis.ports.repositories import UnitOfWork, UnitOfWorkFactory

EXPERIMENT_ID = "EXP-001-P1"
PROTOCOL_VERSION = "0.1"
DATASET_VERSION = "1.0"
AGENT_ID = "agent_soinesis_exp_001_p1"


class ExperimentCondition(StrEnum):
    """Conditions préenregistrées du protocole P1."""

    A = "A"
    B = "B"
    C = "C"


class TrialType(StrEnum):
    """Types d'essais définis par le protocole P1."""

    T1_RECALL = "T1"
    T2_SOURCE = "T2"
    T3_RECALL_AND_SOURCE = "T3"
    T4_FALSE_ATTRIBUTION = "T4"
    T5_FALSE_CONTENT = "T5"
    T6_DEDUCTION_CONFUSION = "T6"
    T7_IMAGINATION_CONFUSION = "T7"
    ABLATION = "ABLATION"


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DatasetSpec(FrozenModel):
    id: str = Field(min_length=1)
    namespace: str = Field(min_length=1)
    source_pattern: tuple[int, ...]

    @model_validator(mode="after")
    def validate_pattern(self) -> Self:
        if len(self.source_pattern) != 20:
            raise ValueError("Chaque jeu doit définir exactement 20 positions de provenance.")
        if any(index not in {0, 1, 2, 3} for index in self.source_pattern):
            raise ValueError("Les indices de provenance doivent être compris entre 0 et 3.")
        if Counter(self.source_pattern) != Counter({0: 5, 1: 5, 2: 5, 3: 5}):
            raise ValueError("Chaque provenance doit apparaître exactement cinq fois par jeu.")
        return self


class ItemTemplate(FrozenModel):
    slot: int = Field(ge=1, le=20)
    title_template: str = Field(min_length=1)
    content_template: str = Field(min_length=1)


class DatasetFile(FrozenModel):
    version: str
    source_order: tuple[SourceType, ...]
    datasets: tuple[DatasetSpec, ...]
    items: tuple[ItemTemplate, ...]
    false_source_slots: tuple[int, ...]
    false_content_templates: tuple[str, ...]
    ablation_slots: tuple[int, ...]

    @model_validator(mode="after")
    def validate_dataset_file(self) -> Self:
        expected_sources = {
            SourceType.JORDAN_INPUT,
            SourceType.EXTERNAL_TOOL,
            SourceType.DEDUCTION,
            SourceType.IMAGINATION,
        }
        if self.version != DATASET_VERSION:
            raise ValueError(f"Version de données attendue : {DATASET_VERSION}.")
        if len(self.source_order) != 4 or set(self.source_order) != expected_sources:
            raise ValueError("source_order doit contenir exactement les quatre provenances de P1.")
        if len(self.datasets) != 5:
            raise ValueError("P1 exige exactement cinq jeux de données.")
        if len(self.items) != 20 or {item.slot for item in self.items} != set(range(1, 21)):
            raise ValueError("Le gabarit doit contenir exactement les slots 1 à 20.")
        if len(self.false_source_slots) != 5 or len(set(self.false_source_slots)) != 5:
            raise ValueError("Cinq slots distincts sont requis pour les fausses attributions.")
        if len(self.false_content_templates) != 5:
            raise ValueError("Cinq faux contenus sont requis par jeu.")
        if len(self.ablation_slots) != 5 or len(set(self.ablation_slots)) != 5:
            raise ValueError("Cinq slots distincts sont requis pour l'ablation.")
        valid_slots = set(range(1, 21))
        if not set(self.false_source_slots).issubset(valid_slots):
            raise ValueError("Un slot de fausse attribution est invalide.")
        if not set(self.ablation_slots).issubset(valid_slots):
            raise ValueError("Un slot d'ablation est invalide.")
        return self


class DatasetItem(FrozenModel):
    id: str
    slot: int
    title: str
    content: str
    source_type: SourceType
    memory_type: MemoryType


class ExperimentDataset(FrozenModel):
    id: str
    namespace: str
    items: tuple[DatasetItem, ...]
    false_source_slots: tuple[int, ...]
    false_contents: tuple[str, ...]
    ablation_slots: tuple[int, ...]


class Prediction(FrozenModel):
    answer: str | None
    source_type: SourceType | None
    retrieved_memory_ids: tuple[str, ...] = ()
    memory_repository_access_count: int = Field(ge=0)
    reason: str


class TrialResult(FrozenModel):
    experiment_id: str = EXPERIMENT_ID
    protocol_version: str = PROTOCOL_VERSION
    dataset_id: str
    trial_id: str
    condition: ExperimentCondition
    trial_type: TrialType
    query: str
    expected_content_id: str | None
    expected_source: SourceType | None
    predicted_content_id: str | None
    predicted_source: SourceType | None
    content_correct: bool
    source_correct: bool
    false_memory_accepted: bool
    misleading_suggestion_rejected: bool
    retrieved_memory_ids: tuple[str, ...]
    memory_repository_access_count: int = Field(ge=0)
    ablation_enabled: bool
    execution_timestamp: datetime
    code_commit: str
    reason: str


class MetricSummary(FrozenModel):
    dataset_id: str
    condition: ExperimentCondition
    recall_correct: int
    recall_total: int
    recall_accuracy: float
    source_correct: int
    source_total: int
    provenance_accuracy: float
    source_errors: int
    source_confusion_rate: float
    false_memories_accepted: int
    false_memory_trials: int
    false_memory_acceptance_rate: float
    misleading_suggestions_rejected: int
    misleading_suggestion_trials: int
    misleading_suggestion_resistance: float


class ProtocolAssessment(FrozenModel):
    provenance_hypothesis_supported: bool
    false_memory_hypothesis_supported: bool
    suggestion_resistance_supported: bool
    recall_non_degradation_supported: bool
    ablation_valid: bool
    c_provenance_accuracy: float
    mean_c_minus_b_provenance_points: float
    datasets_c_better_provenance: int
    c_false_memory_acceptance_rate: float
    b_minus_c_false_memory_points: float
    datasets_c_better_false_memory: int
    c_suggestion_resistance: float
    c_minus_b_suggestion_points: float
    datasets_c_better_suggestions: int
    c_minus_b_recall_points: float


class ExperimentRun(FrozenModel):
    experiment_id: str = EXPERIMENT_ID
    protocol_version: str = PROTOCOL_VERSION
    dataset_version: str = DATASET_VERSION
    code_commit: str
    results: tuple[TrialResult, ...]
    metrics: tuple[MetricSummary, ...]
    assessment: ProtocolAssessment


def memory_type_for_source(source_type: SourceType) -> MemoryType:
    if source_type in {SourceType.JORDAN_INPUT, SourceType.EXTERNAL_TOOL}:
        return MemoryType.RECEIVED_INFORMATION
    if source_type is SourceType.DEDUCTION:
        return MemoryType.DEDUCTION
    if source_type is SourceType.IMAGINATION:
        return MemoryType.IMAGINED_SCENARIO
    raise ValueError(f"Provenance non autorisée dans P1 : {source_type.value}")


def load_datasets(path: Path) -> tuple[ExperimentDataset, ...]:
    config = DatasetFile.model_validate_json(path.read_text(encoding="utf-8"))
    templates = {item.slot: item for item in config.items}
    datasets: list[ExperimentDataset] = []
    for spec in config.datasets:
        items: list[DatasetItem] = []
        for slot in range(1, 21):
            template = templates[slot]
            source = config.source_order[spec.source_pattern[slot - 1]]
            items.append(
                DatasetItem(
                    id=f"{spec.id}-item-{slot:02d}",
                    slot=slot,
                    title=template.title_template.format(namespace=spec.namespace),
                    content=template.content_template.format(namespace=spec.namespace),
                    source_type=source,
                    memory_type=memory_type_for_source(source),
                )
            )
        datasets.append(
            ExperimentDataset(
                id=spec.id,
                namespace=spec.namespace,
                items=tuple(items),
                false_source_slots=config.false_source_slots,
                false_contents=tuple(
                    template.format(namespace=spec.namespace)
                    for template in config.false_content_templates
                ),
                ablation_slots=config.ablation_slots,
            )
        )
    return tuple(datasets)


def build_summary(dataset: ExperimentDataset) -> str:
    return "\n".join(_summary_line(item) for item in dataset.items)


def _summary_line(item: DatasetItem) -> str:
    prefix = {
        SourceType.JORDAN_INPUT: "Jordan a indiqué au sujet de",
        SourceType.EXTERNAL_TOOL: "Un outil externe a indiqué au sujet de",
        SourceType.DEDUCTION: "Une déduction produite pendant l’expérience au sujet de",
        SourceType.IMAGINATION: "Un scénario imaginé au sujet de",
    }[item.source_type]
    return f"{prefix} « {item.title} » : {item.content}"


def _source_from_summary_line(line: str) -> SourceType | None:
    prefixes = (
        ("Jordan a indiqué au sujet de", SourceType.JORDAN_INPUT),
        ("Un outil externe a indiqué au sujet de", SourceType.EXTERNAL_TOOL),
        ("Une déduction produite pendant l’expérience au sujet de", SourceType.DEDUCTION),
        ("Un scénario imaginé au sujet de", SourceType.IMAGINATION),
    )
    for prefix, source in prefixes:
        if line.startswith(prefix):
            return source
    return None


class SummaryCondition:
    """Condition B : seule la chaîne de résumé est conservée entre les épisodes."""

    def __init__(self, summary: str) -> None:
        self._summary = summary

    @property
    def summary(self) -> str:
        return self._summary

    def recall_by_title(self, title: str) -> Prediction:
        marker = f"« {title} »"
        return self._find(lambda line: marker in line)

    def recall_by_content(self, content: str) -> Prediction:
        return self._find(lambda line: line.endswith(content))

    def _find(self, predicate: Callable[[str], bool]) -> Prediction:
        for line in self._summary.splitlines():
            if predicate(line):
                _, separator, content = line.partition(" : ")
                if separator:
                    return Prediction(
                        answer=content,
                        source_type=_source_from_summary_line(line),
                        reason="Réponse reconstruite depuis le résumé textuel figé.",
                        memory_repository_access_count=0,
                    )
        return Prediction(
            answer=None,
            source_type=None,
            reason="Aucune information correspondante dans le résumé textuel.",
            memory_repository_access_count=0,
        )


class CountingUnitOfWorkFactory:
    """Compter les ouvertures du chemin de persistance pour mesurer l'ablation."""

    def __init__(self, delegate: UnitOfWorkFactory) -> None:
        self._delegate = delegate
        self.call_count = 0

    def __call__(self) -> UnitOfWork:
        self.call_count += 1
        return self._delegate()


class ExperimentClock:
    def __init__(self) -> None:
        self._index = 0

    def now(self) -> datetime:
        self._index += 1
        return datetime(2026, 8, 7, 12, 0, self._index % 60, tzinfo=UTC)


class ExperimentIdentifiers:
    def __init__(self) -> None:
        self._index = 0

    def new(self, prefix: str) -> str:
        self._index += 1
        return f"{prefix}_{self._index:05d}"


class StructuredCondition:
    """Condition C : mémoire structurée persistée dans une base SQLite isolée."""

    def __init__(self, dataset: ExperimentDataset, database_path: Path) -> None:
        database_path.unlink(missing_ok=True)
        database = SQLiteDatabase(database_path)
        database.initialize_schema()
        delegate: UnitOfWorkFactory = SQLiteUnitOfWorkFactory(database)
        self._factory = CountingUnitOfWorkFactory(delegate)
        self._service = MemoryApplicationService(
            unit_of_work_factory=self._factory,
            clock=ExperimentClock(),
            identifiers=ExperimentIdentifiers(),
        )
        for item in dataset.items:
            self._service.record_memory(
                agent_id=AGENT_ID,
                cycle_id=f"{dataset.id}-record-{item.slot:02d}",
                title=item.title,
                content=item.content,
                memory_type=item.memory_type,
                source_type=item.source_type,
                confidence=1.0,
                importance=0.5,
            )

    def recall(self, query: str, *, ablation_enabled: bool = False) -> Prediction:
        before = self._factory.call_count
        decision = self._service.recall(
            agent_id=AGENT_ID,
            query=query,
            ablation=AblationConfiguration(
                id="p1-ablation" if ablation_enabled else "p1-active",
                autobiographical_memory_enabled=not ablation_enabled,
            ),
        )
        return Prediction(
            answer=decision.answer,
            source_type=decision.source_type,
            retrieved_memory_ids=decision.retrieved_memory_ids,
            memory_repository_access_count=self._factory.call_count - before,
            reason=decision.reason,
        )


class ExperimentRunner:
    def __init__(
        self,
        *,
        datasets: tuple[ExperimentDataset, ...],
        work_dir: Path,
        code_commit: str,
        timestamp_factory: Callable[[], datetime] | None = None,
    ) -> None:
        self._datasets = datasets
        self._work_dir = work_dir
        self._code_commit = code_commit
        self._timestamp_factory = timestamp_factory or (lambda: datetime.now(UTC))

    def run(self) -> ExperimentRun:
        results: list[TrialResult] = []
        database_dir = self._work_dir / "databases"
        database_dir.mkdir(parents=True, exist_ok=True)
        for dataset in self._datasets:
            summary = SummaryCondition(build_summary(dataset))
            structured = StructuredCondition(dataset, database_dir / f"{dataset.id}.db")
            for condition in ExperimentCondition:
                results.extend(self._run_condition(dataset, condition, summary, structured))
            results.extend(self._run_ablation(dataset, structured))
        frozen_results = tuple(results)
        metrics = calculate_metrics(frozen_results)
        return ExperimentRun(
            code_commit=self._code_commit,
            results=frozen_results,
            metrics=metrics,
            assessment=assess_protocol(metrics, frozen_results),
        )

    def _run_condition(
        self,
        dataset: ExperimentDataset,
        condition: ExperimentCondition,
        summary: SummaryCondition,
        structured: StructuredCondition,
    ) -> list[TrialResult]:
        results: list[TrialResult] = []
        by_content = {item.content: item.id for item in dataset.items}
        for item in dataset.items:
            for trial_type, by_title, expected_source in (
                (TrialType.T1_RECALL, True, None),
                (TrialType.T2_SOURCE, False, item.source_type),
                (TrialType.T3_RECALL_AND_SOURCE, True, item.source_type),
            ):
                prediction = self._predict(
                    condition,
                    item.title if by_title else item.content,
                    by_title,
                    summary,
                    structured,
                )
                results.append(
                    self._result(
                        dataset=dataset,
                        condition=condition,
                        trial_type=trial_type,
                        trial_id=(
                            f"{dataset.id}-{condition.value}-{trial_type.value}-{item.slot:02d}"
                        ),
                        query=item.title if by_title else item.content,
                        expected_content_id=item.id,
                        expected_source=expected_source,
                        prediction=prediction,
                        by_content=by_content,
                    )
                )
        for index, slot in enumerate(dataset.false_source_slots, start=1):
            item = _item_by_slot(dataset, slot)
            claimed_source = _wrong_source(item.source_type)
            trial_type = _adversarial_source_trial_type(item.source_type)
            prediction = self._predict(
                condition,
                item.content,
                False,
                summary,
                structured,
            )
            results.append(
                self._result(
                    dataset=dataset,
                    condition=condition,
                    trial_type=trial_type,
                    trial_id=f"{dataset.id}-{condition.value}-{trial_type.value}-{index:02d}",
                    query=(
                        f"{_source_label(claimed_source)} avait fourni : {item.content} "
                        "Confirme cette attribution."
                    ),
                    expected_content_id=item.id,
                    expected_source=item.source_type,
                    prediction=prediction,
                    by_content=by_content,
                    claimed_source=claimed_source,
                )
            )
        for index, false_content in enumerate(dataset.false_contents, start=1):
            prediction = self._predict(
                condition,
                false_content,
                False,
                summary,
                structured,
            )
            results.append(
                self._result(
                    dataset=dataset,
                    condition=condition,
                    trial_type=TrialType.T5_FALSE_CONTENT,
                    trial_id=f"{dataset.id}-{condition.value}-T5-{index:02d}",
                    query=f"Ce souvenir existe-t-il : {false_content}",
                    expected_content_id=None,
                    expected_source=None,
                    prediction=prediction,
                    by_content=by_content,
                )
            )
        return results

    def _run_ablation(
        self,
        dataset: ExperimentDataset,
        structured: StructuredCondition,
    ) -> list[TrialResult]:
        by_content = {item.content: item.id for item in dataset.items}
        results: list[TrialResult] = []
        for index, slot in enumerate(dataset.ablation_slots, start=1):
            item = _item_by_slot(dataset, slot)
            results.append(
                self._result(
                    dataset=dataset,
                    condition=ExperimentCondition.C,
                    trial_type=TrialType.ABLATION,
                    trial_id=f"{dataset.id}-C-ABLATION-{index:02d}",
                    query=item.title,
                    expected_content_id=item.id,
                    expected_source=item.source_type,
                    prediction=structured.recall(item.title, ablation_enabled=True),
                    by_content=by_content,
                    ablation_enabled=True,
                )
            )
        return results

    def _predict(
        self,
        condition: ExperimentCondition,
        value: str,
        by_title: bool,
        summary: SummaryCondition,
        structured: StructuredCondition,
    ) -> Prediction:
        if condition is ExperimentCondition.A:
            return _empty_prediction("Condition A sans mémoire persistante.")
        if condition is ExperimentCondition.B:
            return summary.recall_by_title(value) if by_title else summary.recall_by_content(value)
        return structured.recall(value)

    def _result(
        self,
        *,
        dataset: ExperimentDataset,
        condition: ExperimentCondition,
        trial_type: TrialType,
        trial_id: str,
        query: str,
        expected_content_id: str | None,
        expected_source: SourceType | None,
        prediction: Prediction,
        by_content: dict[str, str],
        claimed_source: SourceType | None = None,
        ablation_enabled: bool = False,
    ) -> TrialResult:
        predicted_content_id = (
            by_content.get(prediction.answer) if prediction.answer is not None else None
        )
        return TrialResult(
            dataset_id=dataset.id,
            trial_id=trial_id,
            condition=condition,
            trial_type=trial_type,
            query=query,
            expected_content_id=expected_content_id,
            expected_source=expected_source,
            predicted_content_id=predicted_content_id,
            predicted_source=prediction.source_type,
            content_correct=predicted_content_id == expected_content_id,
            source_correct=(
                prediction.source_type == expected_source if expected_source is not None else False
            ),
            false_memory_accepted=(
                trial_type is TrialType.T5_FALSE_CONTENT and prediction.answer is not None
            ),
            misleading_suggestion_rejected=(
                claimed_source is not None
                and prediction.source_type == expected_source
                and prediction.source_type != claimed_source
            ),
            retrieved_memory_ids=prediction.retrieved_memory_ids,
            memory_repository_access_count=prediction.memory_repository_access_count,
            ablation_enabled=ablation_enabled,
            execution_timestamp=self._timestamp_factory(),
            code_commit=self._code_commit,
            reason=prediction.reason,
        )


def calculate_metrics(results: tuple[TrialResult, ...]) -> tuple[MetricSummary, ...]:
    dataset_ids = sorted({result.dataset_id for result in results})
    summaries: list[MetricSummary] = []
    recall_types = {TrialType.T1_RECALL, TrialType.T3_RECALL_AND_SOURCE}
    source_types = {
        TrialType.T2_SOURCE,
        TrialType.T3_RECALL_AND_SOURCE,
        TrialType.T4_FALSE_ATTRIBUTION,
        TrialType.T6_DEDUCTION_CONFUSION,
        TrialType.T7_IMAGINATION_CONFUSION,
    }
    misleading_types = {
        TrialType.T4_FALSE_ATTRIBUTION,
        TrialType.T6_DEDUCTION_CONFUSION,
        TrialType.T7_IMAGINATION_CONFUSION,
    }
    for dataset_id in dataset_ids:
        for condition in ExperimentCondition:
            selected = tuple(
                result
                for result in results
                if result.dataset_id == dataset_id
                and result.condition is condition
                and result.trial_type is not TrialType.ABLATION
            )
            recall = tuple(result for result in selected if result.trial_type in recall_types)
            source = tuple(result for result in selected if result.trial_type in source_types)
            false_memory = tuple(
                result for result in selected if result.trial_type is TrialType.T5_FALSE_CONTENT
            )
            misleading = tuple(
                result for result in selected if result.trial_type in misleading_types
            )
            recall_correct = sum(result.content_correct for result in recall)
            source_correct = sum(result.source_correct for result in source)
            false_accepted = sum(result.false_memory_accepted for result in false_memory)
            misleading_rejected = sum(
                result.misleading_suggestion_rejected for result in misleading
            )
            summaries.append(
                MetricSummary(
                    dataset_id=dataset_id,
                    condition=condition,
                    recall_correct=recall_correct,
                    recall_total=len(recall),
                    recall_accuracy=_ratio(recall_correct, len(recall)),
                    source_correct=source_correct,
                    source_total=len(source),
                    provenance_accuracy=_ratio(source_correct, len(source)),
                    source_errors=len(source) - source_correct,
                    source_confusion_rate=_ratio(len(source) - source_correct, len(source)),
                    false_memories_accepted=false_accepted,
                    false_memory_trials=len(false_memory),
                    false_memory_acceptance_rate=_ratio(false_accepted, len(false_memory)),
                    misleading_suggestions_rejected=misleading_rejected,
                    misleading_suggestion_trials=len(misleading),
                    misleading_suggestion_resistance=_ratio(
                        misleading_rejected,
                        len(misleading),
                    ),
                )
            )
    return tuple(summaries)


def assess_protocol(
    metrics: tuple[MetricSummary, ...],
    results: tuple[TrialResult, ...],
) -> ProtocolAssessment:
    b = sorted(
        (metric for metric in metrics if metric.condition is ExperimentCondition.B),
        key=lambda metric: metric.dataset_id,
    )
    c = sorted(
        (metric for metric in metrics if metric.condition is ExperimentCondition.C),
        key=lambda metric: metric.dataset_id,
    )
    if len(b) != 5 or len(c) != 5:
        raise ValueError("L'évaluation du protocole exige cinq métriques B et cinq métriques C.")
    provenance_diff = [
        c_metric.provenance_accuracy - b_metric.provenance_accuracy
        for b_metric, c_metric in zip(b, c, strict=True)
    ]
    false_diff = [
        b_metric.false_memory_acceptance_rate - c_metric.false_memory_acceptance_rate
        for b_metric, c_metric in zip(b, c, strict=True)
    ]
    suggestion_diff = [
        c_metric.misleading_suggestion_resistance - b_metric.misleading_suggestion_resistance
        for b_metric, c_metric in zip(b, c, strict=True)
    ]
    c_provenance = fmean(metric.provenance_accuracy for metric in c)
    c_false = fmean(metric.false_memory_acceptance_rate for metric in c)
    c_suggestion = fmean(metric.misleading_suggestion_resistance for metric in c)
    recall_diff = fmean(metric.recall_accuracy for metric in c) - fmean(
        metric.recall_accuracy for metric in b
    )
    ablation = tuple(
        result
        for result in results
        if result.condition is ExperimentCondition.C
        and result.trial_type is TrialType.ABLATION
    )
    ablation_valid = bool(ablation) and all(
        result.memory_repository_access_count == 0
        and not result.retrieved_memory_ids
        and result.predicted_content_id is None
        for result in ablation
    )
    mean_provenance = fmean(provenance_diff)
    mean_false = fmean(false_diff)
    mean_suggestion = fmean(suggestion_diff)
    better_provenance = sum(value > 0 for value in provenance_diff)
    better_false = sum(value > 0 for value in false_diff)
    better_suggestion = sum(value > 0 for value in suggestion_diff)
    return ProtocolAssessment(
        provenance_hypothesis_supported=(
            c_provenance >= 0.90 and mean_provenance >= 0.10 and better_provenance >= 4
        ),
        false_memory_hypothesis_supported=(
            c_false <= 0.10 and mean_false >= 0.10 and better_false >= 4
        ),
        suggestion_resistance_supported=(
            c_suggestion >= 0.90 and mean_suggestion >= 0.10 and better_suggestion >= 4
        ),
        recall_non_degradation_supported=recall_diff >= -0.05,
        ablation_valid=ablation_valid,
        c_provenance_accuracy=c_provenance,
        mean_c_minus_b_provenance_points=mean_provenance * 100,
        datasets_c_better_provenance=better_provenance,
        c_false_memory_acceptance_rate=c_false,
        b_minus_c_false_memory_points=mean_false * 100,
        datasets_c_better_false_memory=better_false,
        c_suggestion_resistance=c_suggestion,
        c_minus_b_suggestion_points=mean_suggestion * 100,
        datasets_c_better_suggestions=better_suggestion,
        c_minus_b_recall_points=recall_diff * 100,
    )


def write_run(run: ExperimentRun, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "results.jsonl"
    summary_path = output_dir / "summary.json"
    raw_path.write_text(
        "\n".join(
            json.dumps(result.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
            for result in run.results
        )
        + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(
            {
                "experiment_id": run.experiment_id,
                "protocol_version": run.protocol_version,
                "dataset_version": run.dataset_version,
                "code_commit": run.code_commit,
                "metrics": [metric.model_dump(mode="json") for metric in run.metrics],
                "assessment": run.assessment.model_dump(mode="json"),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return raw_path, summary_path


def run_from_paths(
    *,
    dataset_path: Path,
    work_dir: Path,
    output_dir: Path,
    code_commit: str,
) -> ExperimentRun:
    run = ExperimentRunner(
        datasets=load_datasets(dataset_path),
        work_dir=work_dir,
        code_commit=code_commit,
    ).run()
    write_run(run, output_dir)
    return run


def _item_by_slot(dataset: ExperimentDataset, slot: int) -> DatasetItem:
    for item in dataset.items:
        if item.slot == slot:
            return item
    raise ValueError(f"Slot absent du jeu {dataset.id} : {slot}")


def _wrong_source(source: SourceType) -> SourceType:
    order = (
        SourceType.JORDAN_INPUT,
        SourceType.EXTERNAL_TOOL,
        SourceType.DEDUCTION,
        SourceType.IMAGINATION,
    )
    return order[(order.index(source) + 1) % len(order)]


def _adversarial_source_trial_type(source: SourceType) -> TrialType:
    if source is SourceType.DEDUCTION:
        return TrialType.T6_DEDUCTION_CONFUSION
    if source is SourceType.IMAGINATION:
        return TrialType.T7_IMAGINATION_CONFUSION
    return TrialType.T4_FALSE_ATTRIBUTION


def _source_label(source: SourceType) -> str:
    return {
        SourceType.JORDAN_INPUT: "Jordan",
        SourceType.EXTERNAL_TOOL: "L’outil externe",
        SourceType.DEDUCTION: "Une déduction interne",
        SourceType.IMAGINATION: "Un scénario imaginé",
    }[source]


def _empty_prediction(reason: str) -> Prediction:
    return Prediction(
        answer=None,
        source_type=None,
        reason=reason,
        memory_repository_access_count=0,
    )


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exécuter le protocole déterministe EXP-001-P1.")
    parser.add_argument(
        "--datasets",
        type=Path,
        default=Path("data/exp-001-p1/datasets-v1.json"),
    )
    parser.add_argument("--work-dir", type=Path, default=Path("data/exp-001-p1/work"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/exp-001-p1/results"))
    parser.add_argument("--code-commit", required=True)
    args = parser.parse_args(argv)
    run = run_from_paths(
        dataset_path=args.datasets,
        work_dir=args.work_dir,
        output_dir=args.output_dir,
        code_commit=args.code_commit,
    )
    print(json.dumps(run.assessment.model_dump(mode="json"), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
