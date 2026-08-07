from __future__ import annotations

from pathlib import Path

from soinesis.domain.models import MemoryType, SourceType
from soinesis.experiments.exp_001_p2 import (
    ChainFamily,
    DatasetEvent,
    EventKind,
    ExperimentChain,
    ExperimentDataset,
)
from soinesis.experiments.exp_001_p2_readers import (
    NoHistoryCondition,
    P2Query,
    StructuredHistoryCondition,
    TextHistoryCondition,
    build_query,
)


def _memory_type(source: SourceType) -> MemoryType:
    return (
        MemoryType.DEDUCTION if source is SourceType.DEDUCTION else MemoryType.RECEIVED_INFORMATION
    )


def _content(kind: EventKind, subject: str, value: str) -> str:
    if kind is EventKind.INITIAL:
        return f"{subject} est « {value} »."
    if kind is EventKind.CORRECTION:
        return f"Correction explicite : {subject} est désormais « {value} »."
    if kind is EventKind.CONTRADICTION:
        return f"Information contradictoire : {subject} est « {value} »."
    if kind is EventKind.RESOLUTION:
        return f"Résolution explicite : {subject} est fixé à « {value} »."
    return f"Confirmation : {subject} reste « {value} »."


def _reason(kind: EventKind) -> str:
    return {
        EventKind.INITIAL: "État initial reçu.",
        EventKind.CORRECTION: "Correction explicite de la croyance précédente.",
        EventKind.CONTRADICTION: "Contradiction explicite laissée non résolue.",
        EventKind.RESOLUTION: "Résolution explicite de la contradiction.",
        EventKind.CONFIRMATION: "Confirmation sans changement de croyance.",
    }[kind]


def _fixture_dataset(
    *,
    dataset_id: str,
    family: ChainFamily,
    subject: str,
    kinds: tuple[EventKind, EventKind, EventKind, EventKind],
    values: tuple[str, str, str, str],
    historical_event_number: int,
) -> ExperimentDataset:
    sources = (
        SourceType.JORDAN_INPUT,
        SourceType.EXTERNAL_TOOL,
        SourceType.DEDUCTION,
        SourceType.JORDAN_INPUT,
    )
    belief_key = f"{dataset_id}:fixture-belief"
    events = tuple(
        DatasetEvent(
            id=f"fixture-event-{index}",
            dataset_id=dataset_id,
            stream_position=index,
            chain_slot=1,
            event_number=index,
            cycle_id=f"{dataset_id}-cycle-{index:03d}",
            belief_key=belief_key,
            subject=subject,
            family=family,
            kind=kind,
            value=value,
            content=_content(kind, subject, value),
            transition_reason=_reason(kind),
            source_type=source,
            memory_type=_memory_type(source),
        )
        for index, (kind, value, source) in enumerate(
            zip(kinds, values, sources, strict=True),
            start=1,
        )
    )
    chain = ExperimentChain(
        id=f"{dataset_id}-fixture-chain",
        dataset_id=dataset_id,
        slot=1,
        belief_key=belief_key,
        subject=subject,
        family=family,
        historical_event_number=historical_event_number,
        misleading_value=None,
        events=events,
    )
    return ExperimentDataset(
        id=dataset_id,
        namespace="fixture-only",
        events=events,
        chains=(chain,),
    )


def test_condition_a_exposes_no_persistent_history() -> None:
    query = P2Query(
        dataset_id="fixture-a",
        belief_key="fixture-a:belief",
        subject="Sujet A",
        historical_cycle_id="fixture-a-cycle-001",
        trace_cycle_id="fixture-a-cycle-001",
    )

    prediction = NoHistoryCondition().inspect(query)

    assert prediction.current_value is None
    assert prediction.historical_value is None
    assert prediction.ordered_values == ()
    assert prediction.transition_source is None


def test_b_and_c_reconstruct_a_resolved_contradiction_without_ground_truth(
    tmp_path: Path,
) -> None:
    dataset = _fixture_dataset(
        dataset_id="fixture-resolved",
        family=ChainFamily.S4_CONTRADICTION_RESOLUTION,
        subject="Couleur du témoin de test",
        kinds=(
            EventKind.INITIAL,
            EventKind.CONTRADICTION,
            EventKind.CONFIRMATION,
            EventKind.RESOLUTION,
        ),
        values=("rouge", "bleu", "bleu", "vert"),
        historical_event_number=2,
    )
    query = build_query(dataset.chains[0])
    text = TextHistoryCondition(dataset)
    structured = StructuredHistoryCondition(dataset, tmp_path / "resolved.db")

    b = text.inspect(query)
    c = structured.inspect(query)

    for prediction in (b, c):
        assert prediction.current_value == "vert"
        assert prediction.unresolved_contradiction is False
        assert prediction.historical_value is None
        assert prediction.historical_contested_values == ("rouge", "bleu")
        assert prediction.ordered_values == ("rouge", "bleu", "vert")
        assert prediction.transition_reason == "Résolution explicite de la contradiction."
        assert prediction.transition_source is SourceType.JORDAN_INPUT
        assert prediction.transition_cycle_id == "fixture-resolved-cycle-004"

    assert len(c.retrieved_memory_ids) == 3


def test_b_and_c_preserve_an_unresolved_contradiction(tmp_path: Path) -> None:
    dataset = _fixture_dataset(
        dataset_id="fixture-contested",
        family=ChainFamily.S3_UNRESOLVED_CONTRADICTION,
        subject="Direction du témoin de test",
        kinds=(
            EventKind.INITIAL,
            EventKind.CONFIRMATION,
            EventKind.CONTRADICTION,
            EventKind.CONFIRMATION,
        ),
        values=("nord", "nord", "sud", "sud"),
        historical_event_number=4,
    )
    query = build_query(dataset.chains[0])

    predictions = (
        TextHistoryCondition(dataset).inspect(query),
        StructuredHistoryCondition(dataset, tmp_path / "contested.db").inspect(query),
    )

    for prediction in predictions:
        assert prediction.current_value is None
        assert prediction.unresolved_contradiction is True
        assert prediction.contested_values == ("nord", "sud")
        assert prediction.historical_value is None
        assert prediction.historical_contested_values == ("nord", "sud")


def test_condition_b_remains_textual_and_contains_no_structured_identifiers() -> None:
    dataset = _fixture_dataset(
        dataset_id="fixture-text",
        family=ChainFamily.S5_CONFIRMATION_NO_CHANGE,
        subject="État du témoin de test",
        kinds=(
            EventKind.INITIAL,
            EventKind.CONFIRMATION,
            EventKind.CONFIRMATION,
            EventKind.CONFIRMATION,
        ),
        values=("stable", "stable", "stable", "stable"),
        historical_event_number=3,
    )

    history = TextHistoryCondition(dataset).history

    assert len(history.splitlines()) == 4
    assert "JORDAN_INPUT" not in history
    assert "EXTERNAL_TOOL" not in history
    assert "DEDUCTION" not in history
    assert "fixture-text:fixture-belief" not in history
    assert "memory_" not in history
