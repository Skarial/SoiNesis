"""Plan d'essais déterministe et figé pour EXP-001-P2.

Ce module ne lance aucune expérience. Il matérialise avant tout run officiel
l'ordre des essais, les conditions évaluées et le sous-ensemble d'ablation T9.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from soinesis.experiments.exp_001_p2 import (
    ChainFamily,
    ExperimentChain,
    ExperimentDataset,
)
from soinesis.experiments.exp_001_p2_readers import ExperimentCondition


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class TrialType(StrEnum):
    T1_CURRENT_STATE = "T1"
    T2_HISTORICAL_STATE = "T2"
    T3_CHAIN_ORDER = "T3"
    T4_REVISION_CAUSE = "T4"
    T5_UNRESOLVED_CONTRADICTION = "T5"
    T6_CONFIRMATION_NO_REVISION = "T6"
    T7_MISLEADING_REWRITE = "T7"
    T8_TRANSITION_PROVENANCE = "T8"
    T9_TARGETED_ABLATION = "T9"


class TrialPlanEntry(FrozenModel):
    order: int = Field(ge=1)
    trial_id: str = Field(min_length=1)
    dataset_id: str = Field(min_length=1)
    belief_chain_id: str = Field(min_length=1)
    chain_slot: int = Field(ge=1)
    family: ChainFamily
    trial_type: TrialType
    condition: ExperimentCondition
    ablation_enabled: bool = False


_NORMAL_CONDITIONS = (
    ExperimentCondition.A,
    ExperimentCondition.B,
    ExperimentCondition.C,
)
_ADVERSARIAL_CONDITIONS = (
    ExperimentCondition.B,
    ExperimentCondition.C,
)
_ABLATION_FAMILIES = (
    ChainFamily.S1_SIMPLE_CORRECTION,
    ChainFamily.S2_MULTIPLE_REVISIONS,
    ChainFamily.S3_UNRESOLVED_CONTRADICTION,
    ChainFamily.S4_CONTRADICTION_RESOLUTION,
    ChainFamily.S6_MISLEADING_REWRITE,
)


def build_trial_plan(datasets: tuple[ExperimentDataset, ...]) -> tuple[TrialPlanEntry, ...]:
    """Construit l'ordre complet sans consulter aucune réponse expérimentale."""

    entries: list[TrialPlanEntry] = []
    order = 0
    for dataset in datasets:
        chains = tuple(sorted(dataset.chains, key=lambda chain: chain.slot))
        ablation_chain_ids = _ablation_chain_ids(chains)

        for trial_type in TrialType:
            for chain in chains:
                if not _trial_applies(trial_type, chain, ablation_chain_ids):
                    continue
                for condition in _conditions_for_trial(trial_type):
                    order += 1
                    entries.append(
                        TrialPlanEntry(
                            order=order,
                            trial_id=(
                                f"{dataset.id}-{trial_type.value}-"
                                f"chain-{chain.slot:02d}-{condition.value}"
                            ),
                            dataset_id=dataset.id,
                            belief_chain_id=chain.id,
                            chain_slot=chain.slot,
                            family=chain.family,
                            trial_type=trial_type,
                            condition=condition,
                            ablation_enabled=(trial_type is TrialType.T9_TARGETED_ABLATION),
                        )
                    )
    return tuple(entries)


def _conditions_for_trial(trial_type: TrialType) -> tuple[ExperimentCondition, ...]:
    if trial_type is TrialType.T7_MISLEADING_REWRITE:
        return _ADVERSARIAL_CONDITIONS
    if trial_type is TrialType.T9_TARGETED_ABLATION:
        return (ExperimentCondition.C,)
    return _NORMAL_CONDITIONS


def _trial_applies(
    trial_type: TrialType,
    chain: ExperimentChain,
    ablation_chain_ids: frozenset[str],
) -> bool:
    family = chain.family
    if trial_type is TrialType.T1_CURRENT_STATE:
        return family is not ChainFamily.S3_UNRESOLVED_CONTRADICTION
    if trial_type in {TrialType.T2_HISTORICAL_STATE, TrialType.T3_CHAIN_ORDER}:
        return True
    if trial_type in {
        TrialType.T4_REVISION_CAUSE,
        TrialType.T8_TRANSITION_PROVENANCE,
    }:
        return family is not ChainFamily.S5_CONFIRMATION_NO_CHANGE
    if trial_type is TrialType.T5_UNRESOLVED_CONTRADICTION:
        return family is ChainFamily.S3_UNRESOLVED_CONTRADICTION
    if trial_type is TrialType.T6_CONFIRMATION_NO_REVISION:
        return family is ChainFamily.S5_CONFIRMATION_NO_CHANGE
    if trial_type is TrialType.T7_MISLEADING_REWRITE:
        return family is ChainFamily.S6_MISLEADING_REWRITE
    return chain.id in ablation_chain_ids


def _ablation_chain_ids(chains: tuple[ExperimentChain, ...]) -> frozenset[str]:
    """Sélectionne avant exécution la première chaîne de chaque famille dépendante."""

    selected: list[str] = []
    for family in _ABLATION_FAMILIES:
        candidates = tuple(chain for chain in chains if chain.family is family)
        if not candidates:
            raise ValueError(f"Aucune chaîne disponible pour l'ablation {family.value}.")
        selected.append(min(candidates, key=lambda chain: chain.slot).id)
    return frozenset(selected)
