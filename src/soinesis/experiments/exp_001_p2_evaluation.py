"""Vérité terrain et règles de score déterministes pour EXP-001-P2.

Ce module ne lance aucune expérience. Il transforme uniquement les chaînes
figées en attentes explicites, puis compare une prédiction aux attentes.
Les règles sont séparées des lecteurs B/C afin d'éviter qu'une condition ne
puisse consulter le corrigé pendant l'inférence.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from soinesis.domain.models import SourceType
from soinesis.experiments.exp_001_p2 import EventKind, ExperimentChain
from soinesis.experiments.exp_001_p2_readers import P2Prediction


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ExpectedChainState(FrozenModel):
    current_value: str | None
    contested_values: tuple[str, ...]
    unresolved_contradiction: bool
    historical_value: str | None
    historical_contested_values: tuple[str, ...]
    ordered_values: tuple[str, ...]
    transition_reason: str
    transition_source: SourceType
    transition_cycle_id: str


class PredictionScore(FrozenModel):
    current_state_correct: bool
    historical_state_correct: bool
    order_correct: bool
    contradiction_handled_correctly: bool
    revision_trace_correct: bool
    continuity_correct: bool


def expected_chain_state(chain: ExperimentChain) -> ExpectedChainState:
    """Construit le corrigé d'une chaîne depuis ses événements figés."""

    active: tuple[str, ...] = ()
    contested: tuple[str, ...] = ()
    historical_active: tuple[str, ...] = ()
    historical_contested: tuple[str, ...] = ()
    ordered_values: list[str] = []
    historical_event = chain.events[chain.historical_event_number - 1]

    for event in chain.events:
        if event.kind is not EventKind.CONFIRMATION:
            ordered_values.append(event.value)

        if event.kind in {EventKind.INITIAL, EventKind.CORRECTION, EventKind.RESOLUTION}:
            active = (event.value,)
            contested = ()
        elif event.kind is EventKind.CONTRADICTION:
            contested = tuple(dict.fromkeys((*active, event.value)))
            active = ()

        if event.id == historical_event.id:
            historical_active = active
            historical_contested = contested

    if len(active) > 1 or len(historical_active) > 1:
        raise RuntimeError("Le corrigé P2 a produit plusieurs états actifs.")

    trace = next(
        (
            event
            for event in reversed(chain.events)
            if event.kind
            in {
                EventKind.CORRECTION,
                EventKind.CONTRADICTION,
                EventKind.RESOLUTION,
            }
        ),
        chain.events[0],
    )

    return ExpectedChainState(
        current_value=None if not active else active[0],
        contested_values=contested,
        unresolved_contradiction=bool(contested),
        historical_value=None if not historical_active else historical_active[0],
        historical_contested_values=historical_contested,
        ordered_values=tuple(ordered_values),
        transition_reason=trace.transition_reason,
        transition_source=trace.source_type,
        transition_cycle_id=trace.cycle_id,
    )


def score_prediction(
    expected: ExpectedChainState,
    prediction: P2Prediction,
) -> PredictionScore:
    """Applique les règles de score figées aux champs observables d'une prédiction."""

    current_state_correct = _state_matches(
        expected_value=expected.current_value,
        expected_contested=expected.contested_values,
        expected_unresolved=expected.unresolved_contradiction,
        predicted_value=prediction.current_value,
        predicted_contested=prediction.contested_values,
        predicted_unresolved=prediction.unresolved_contradiction,
    )
    historical_state_correct = _historical_state_matches(expected, prediction)
    order_correct = prediction.ordered_values == expected.ordered_values
    contradiction_handled_correctly = not expected.unresolved_contradiction or (
        prediction.unresolved_contradiction is True
        and prediction.current_value is None
        and prediction.contested_values == expected.contested_values
    )
    revision_trace_correct = (
        prediction.transition_reason == expected.transition_reason
        and prediction.transition_source is expected.transition_source
        and prediction.transition_cycle_id == expected.transition_cycle_id
    )

    return PredictionScore(
        current_state_correct=current_state_correct,
        historical_state_correct=historical_state_correct,
        order_correct=order_correct,
        contradiction_handled_correctly=contradiction_handled_correctly,
        revision_trace_correct=revision_trace_correct,
        continuity_correct=(current_state_correct and historical_state_correct and order_correct),
    )


def _state_matches(
    *,
    expected_value: str | None,
    expected_contested: tuple[str, ...],
    expected_unresolved: bool,
    predicted_value: str | None,
    predicted_contested: tuple[str, ...],
    predicted_unresolved: bool | None,
) -> bool:
    if expected_unresolved:
        return (
            predicted_unresolved is True
            and predicted_value is None
            and predicted_contested == expected_contested
        )
    return (
        predicted_unresolved is False
        and predicted_value == expected_value
        and predicted_contested == ()
    )


def _historical_state_matches(
    expected: ExpectedChainState,
    prediction: P2Prediction,
) -> bool:
    if expected.historical_contested_values:
        return (
            prediction.historical_value is None
            and prediction.historical_contested_values == expected.historical_contested_values
        )
    return (
        prediction.historical_value == expected.historical_value
        and prediction.historical_contested_values == ()
    )
