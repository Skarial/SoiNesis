from __future__ import annotations

from soinesis.domain.models import MemoryType, SourceType
from soinesis.experiments.exp_001_p2 import (
    ChainFamily,
    DatasetEvent,
    EventKind,
    ExperimentChain,
)
from soinesis.experiments.exp_001_p2_evaluation import (
    expected_chain_state,
    score_prediction,
)
from soinesis.experiments.exp_001_p2_readers import ExperimentCondition, P2Prediction


def _event(
    *,
    number: int,
    kind: EventKind,
    value: str,
    source: SourceType,
) -> DatasetEvent:
    cycle_id = f"fixture-score-cycle-{number:03d}"
    return DatasetEvent(
        id=f"fixture-score-event-{number:03d}",
        dataset_id="fixture-score",
        stream_position=number,
        chain_slot=1,
        event_number=number,
        cycle_id=cycle_id,
        belief_key="fixture-score:belief:01",
        subject="État du témoin de score",
        family=ChainFamily.S4_CONTRADICTION_RESOLUTION,
        kind=kind,
        value=value,
        content=f"Événement {kind.value} : « {value} »",
        transition_reason={
            EventKind.INITIAL: "État initial reçu.",
            EventKind.CORRECTION: "Correction explicite de la croyance précédente.",
            EventKind.CONTRADICTION: "Contradiction explicite laissée non résolue.",
            EventKind.RESOLUTION: "Résolution explicite de la contradiction.",
            EventKind.CONFIRMATION: "Confirmation sans changement de croyance.",
        }[kind],
        source_type=source,
        memory_type=(
            MemoryType.DEDUCTION
            if source is SourceType.DEDUCTION
            else MemoryType.RECEIVED_INFORMATION
        ),
    )


def _resolved_chain() -> ExperimentChain:
    events = (
        _event(number=1, kind=EventKind.INITIAL, value="rouge", source=SourceType.JORDAN_INPUT),
        _event(
            number=2,
            kind=EventKind.CONTRADICTION,
            value="bleu",
            source=SourceType.EXTERNAL_TOOL,
        ),
        _event(
            number=3,
            kind=EventKind.CONFIRMATION,
            value="bleu",
            source=SourceType.DEDUCTION,
        ),
        _event(
            number=4,
            kind=EventKind.RESOLUTION,
            value="vert",
            source=SourceType.JORDAN_INPUT,
        ),
    )
    return ExperimentChain(
        id="fixture-score-chain-01",
        dataset_id="fixture-score",
        slot=1,
        belief_key="fixture-score:belief:01",
        subject="État du témoin de score",
        family=ChainFamily.S4_CONTRADICTION_RESOLUTION,
        historical_event_number=2,
        misleading_value=None,
        events=events,
    )


def test_expected_state_excludes_confirmations_from_version_order() -> None:
    expected = expected_chain_state(_resolved_chain())

    assert expected.current_value == "vert"
    assert expected.contested_values == ()
    assert expected.unresolved_contradiction is False
    assert expected.historical_value is None
    assert expected.historical_contested_values == ("rouge", "bleu")
    assert expected.ordered_values == ("rouge", "bleu", "vert")
    assert expected.transition_reason == "Résolution explicite de la contradiction."
    assert expected.transition_source is SourceType.JORDAN_INPUT
    assert expected.transition_cycle_id == "fixture-score-cycle-004"


def test_score_requires_current_history_order_and_trace_to_match() -> None:
    expected = expected_chain_state(_resolved_chain())
    prediction = P2Prediction(
        condition=ExperimentCondition.C,
        current_value="vert",
        unresolved_contradiction=False,
        historical_value=None,
        historical_contested_values=("rouge", "bleu"),
        ordered_values=("rouge", "bleu", "vert"),
        transition_reason="Résolution explicite de la contradiction.",
        transition_source=SourceType.JORDAN_INPUT,
        transition_cycle_id="fixture-score-cycle-004",
        reason="Fixture de score correcte.",
    )

    score = score_prediction(expected, prediction)

    assert score.current_state_correct is True
    assert score.historical_state_correct is True
    assert score.order_correct is True
    assert score.revision_trace_correct is True
    assert score.continuity_correct is True


def test_targeted_ablation_is_scored_as_degraded_on_dependent_fields() -> None:
    expected = expected_chain_state(_resolved_chain())
    ablated = P2Prediction(
        condition=ExperimentCondition.C,
        current_value=None,
        unresolved_contradiction=None,
        historical_value=None,
        ordered_values=("rouge", "bleu", "bleu", "vert"),
        transition_reason=None,
        transition_source=SourceType.JORDAN_INPUT,
        transition_cycle_id="fixture-score-cycle-004",
        repository_access_count=0,
        ablation_enabled=True,
        reason="Fixture d'ablation sans métadonnées de révision.",
    )

    score = score_prediction(expected, ablated)

    assert score.current_state_correct is False
    assert score.historical_state_correct is False
    assert score.order_correct is False
    assert score.revision_trace_correct is False
    assert score.continuity_correct is False
