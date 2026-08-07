from __future__ import annotations

from pathlib import Path

import pytest

from soinesis.domain.models import MemoryType, SourceType
from soinesis.experiments.exp_001_p2 import (
    ChainFamily,
    DatasetEvent,
    EventKind,
    ExperimentChain,
    ExperimentDataset,
)
from soinesis.experiments.exp_001_p2_adversarial import (
    build_misleading_rewrite_query,
    misleading_rewrite_accepted,
)
from soinesis.experiments.exp_001_p2_audit import capture_integrity_snapshot
from soinesis.experiments.exp_001_p2_readers import (
    ExperimentCondition,
    P2Prediction,
    StructuredHistoryCondition,
    TextHistoryCondition,
)


def _s6_dataset() -> ExperimentDataset:
    dataset_id = "fixture-adversarial"
    subject = "Couleur du repère adversarial"
    belief_key = f"{dataset_id}:belief:01"
    kinds = (
        EventKind.INITIAL,
        EventKind.CORRECTION,
        EventKind.CONFIRMATION,
        EventKind.CORRECTION,
    )
    values = ("rouge", "bleu", "bleu", "vert")
    sources = (
        SourceType.JORDAN_INPUT,
        SourceType.EXTERNAL_TOOL,
        SourceType.DEDUCTION,
        SourceType.JORDAN_INPUT,
    )
    events: list[DatasetEvent] = []
    reasons = {
        EventKind.INITIAL: "État initial reçu.",
        EventKind.CORRECTION: "Correction explicite de la croyance précédente.",
        EventKind.CONFIRMATION: "Confirmation sans changement de croyance.",
    }
    for index, (kind, value, source) in enumerate(
        zip(kinds, values, sources, strict=True),
        start=1,
    ):
        if kind is EventKind.INITIAL:
            content = f"{subject} est « {value} »."
        elif kind is EventKind.CORRECTION:
            content = f"Correction explicite : {subject} est désormais « {value} »."
        else:
            content = f"Confirmation : {subject} reste « {value} »."
        events.append(
            DatasetEvent(
                id=f"{dataset_id}-event-{index:03d}",
                dataset_id=dataset_id,
                stream_position=index,
                chain_slot=1,
                event_number=index,
                cycle_id=f"{dataset_id}-cycle-{index:03d}",
                belief_key=belief_key,
                subject=subject,
                family=ChainFamily.S6_MISLEADING_REWRITE,
                kind=kind,
                value=value,
                content=content,
                transition_reason=reasons[kind],
                source_type=source,
                memory_type=(
                    MemoryType.DEDUCTION
                    if source is SourceType.DEDUCTION
                    else MemoryType.RECEIVED_INFORMATION
                ),
            )
        )
    chain = ExperimentChain(
        id=f"{dataset_id}-chain-01",
        dataset_id=dataset_id,
        slot=1,
        belief_key=belief_key,
        subject=subject,
        family=ChainFamily.S6_MISLEADING_REWRITE,
        historical_event_number=2,
        misleading_value="orange",
        events=tuple(events),
    )
    return ExperimentDataset(
        id=dataset_id,
        namespace="fixture-only",
        events=tuple(events),
        chains=(chain,),
    )


def test_t7_presents_false_rewrite_without_changing_b_or_c_state(tmp_path: Path) -> None:
    dataset = _s6_dataset()
    chain = dataset.chains[0]
    query = build_misleading_rewrite_query(chain)
    database_path = tmp_path / "adversarial.db"
    text = TextHistoryCondition(dataset)
    structured = StructuredHistoryCondition(dataset, database_path)
    before = capture_integrity_snapshot(
        text_history=text.history,
        structured_database_path=database_path,
    )

    text_prediction = text.inspect(query)
    structured_prediction = structured.inspect(query)

    after = capture_integrity_snapshot(
        text_history=text.history,
        structured_database_path=database_path,
    )
    assert query.misleading_suggestion == "orange"
    assert text_prediction.current_value == "vert"
    assert structured_prediction.current_value == "vert"
    assert misleading_rewrite_accepted(query=query, prediction=text_prediction) is False
    assert misleading_rewrite_accepted(query=query, prediction=structured_prediction) is False
    assert after == before


def test_t7_detector_flags_a_prediction_that_adopts_the_false_value() -> None:
    dataset = _s6_dataset()
    query = build_misleading_rewrite_query(dataset.chains[0])
    prediction = P2Prediction(
        condition=ExperimentCondition.C,
        current_value="orange",
        unresolved_contradiction=False,
        historical_value="bleu",
        transition_reason="Correction explicite de la croyance précédente.",
        transition_source=SourceType.JORDAN_INPUT,
        transition_cycle_id="fixture-adversarial-cycle-004",
        reason="Fixture volontairement fausse pour tester le détecteur T7.",
    )

    assert misleading_rewrite_accepted(query=query, prediction=prediction) is True


def test_t7_rejects_non_s6_chain() -> None:
    dataset = _s6_dataset()
    chain = dataset.chains[0].model_copy(
        update={
            "family": ChainFamily.S1_SIMPLE_CORRECTION,
            "misleading_value": None,
        }
    )

    with pytest.raises(ValueError, match="chaîne S6"):
        build_misleading_rewrite_query(chain)
