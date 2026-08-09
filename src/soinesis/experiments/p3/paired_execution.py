"""Orchestration séquentielle d'un triplet A/B/C certifié P3 DEV."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, model_validator

from soinesis.experiments.p3.condition_config import ExperimentalCondition
from soinesis.experiments.p3.condition_replication import (
    ExperimentalConditionReplicationRunResult,
)
from soinesis.experiments.p3.pairing import ExperimentalPairedConditionGroup

_TOTAL_CYCLES = 180


def _validate_condition_result(
    *,
    pairing: ExperimentalPairedConditionGroup,
    result: ExperimentalConditionReplicationRunResult,
    execution_id: str,
    condition: ExperimentalCondition,
) -> None:
    replication = result.replication_result
    if (
        result.execution_id != execution_id
        or result.condition is not condition
        or replication.execution_id != execution_id
    ):
        raise ValueError("Un résultat 3T ne correspond pas à son rôle A/B/C certifié.")
    if replication.plan_identity != pairing.plan_identity:
        raise ValueError("Un résultat 3T utilise un autre plan que le pairing certifié.")
    if len(replication.cycle_results) != _TOTAL_CYCLES:
        raise ValueError("Chaque condition appariée doit contenir exactement 180 cycles.")


class ExperimentalPairedConditionExecutionResult(BaseModel):
    """Regrouper trois réplications complètes sans les comparer scientifiquement."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pairing: ExperimentalPairedConditionGroup
    result_a: ExperimentalConditionReplicationRunResult
    result_b: ExperimentalConditionReplicationRunResult
    result_c: ExperimentalConditionReplicationRunResult

    @model_validator(mode="after")
    def validate_pairing_scope(self) -> ExperimentalPairedConditionExecutionResult:
        _validate_condition_result(
            pairing=self.pairing,
            result=self.result_a,
            execution_id=self.pairing.execution_a,
            condition=ExperimentalCondition.A,
        )
        _validate_condition_result(
            pairing=self.pairing,
            result=self.result_b,
            execution_id=self.pairing.execution_b,
            condition=ExperimentalCondition.B,
        )
        _validate_condition_result(
            pairing=self.pairing,
            result=self.result_c,
            execution_id=self.pairing.execution_c,
            condition=ExperimentalCondition.C,
        )
        if len({self.result_a.agent_id, self.result_b.agent_id, self.result_c.agent_id}) != 3:
            raise ValueError("Les trois résultats doivent appartenir à des agents distincts.")
        return self


class ExperimentalPairedConditionExecutionError(RuntimeError):
    """Erreur de base de l'orchestration d'un triplet certifié P3 DEV."""


class ExperimentalPairedConditionNotFoundError(ExperimentalPairedConditionExecutionError):
    """Refuser une exécution 3V sans pairing 3U persistant."""


class ExperimentalPairedConditionExecutionIntegrityError(ExperimentalPairedConditionExecutionError):
    """Refuser immédiatement un résultat 3T incompatible avec son rôle certifié."""


class _PairedConditionGroupReader(Protocol):
    def get(self, *, pairing_id: str) -> ExperimentalPairedConditionGroup | None: ...


class _ConditionReplicationRunner(Protocol):
    def run(self, *, execution_id: str) -> ExperimentalConditionReplicationRunResult: ...


class ExperimentalPairedConditionExecutionRunner:
    """Déléguer A, puis B, puis C à l'unique runner canonique 3T."""

    def __init__(
        self,
        *,
        pairing_service: _PairedConditionGroupReader,
        condition_runner: _ConditionReplicationRunner,
    ) -> None:
        self._pairing_service = pairing_service
        self._condition_runner = condition_runner

    def run(self, *, pairing_id: str) -> ExperimentalPairedConditionExecutionResult:
        pairing = self._pairing_service.get(pairing_id=pairing_id)
        if pairing is None:
            raise ExperimentalPairedConditionNotFoundError(
                "Un pairing 3U persistant est requis avant l'exécution appariée."
            )
        result_a = self._condition_runner.run(execution_id=pairing.execution_a)
        self._validate_result(
            pairing=pairing,
            result=result_a,
            execution_id=pairing.execution_a,
            condition=ExperimentalCondition.A,
        )
        result_b = self._condition_runner.run(execution_id=pairing.execution_b)
        self._validate_result(
            pairing=pairing,
            result=result_b,
            execution_id=pairing.execution_b,
            condition=ExperimentalCondition.B,
        )
        result_c = self._condition_runner.run(execution_id=pairing.execution_c)
        self._validate_result(
            pairing=pairing,
            result=result_c,
            execution_id=pairing.execution_c,
            condition=ExperimentalCondition.C,
        )
        return ExperimentalPairedConditionExecutionResult(
            pairing=pairing,
            result_a=result_a,
            result_b=result_b,
            result_c=result_c,
        )

    @staticmethod
    def _validate_result(
        *,
        pairing: ExperimentalPairedConditionGroup,
        result: ExperimentalConditionReplicationRunResult,
        execution_id: str,
        condition: ExperimentalCondition,
    ) -> None:
        try:
            _validate_condition_result(
                pairing=pairing,
                result=result,
                execution_id=execution_id,
                condition=condition,
            )
        except ValueError as error:
            raise ExperimentalPairedConditionExecutionIntegrityError(
                "Le runner 3T a retourné un résultat incompatible avec le pairing 3U."
            ) from error
