"""Liaison immuable entre une exécution P3 DEV et son plan exact."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from soinesis.experiments.p3.plan import ExperimentalReplicationPlanIdentity


class ExperimentalExecutionPlanBinding(BaseModel):
    """Associer un identifiant opaque d'exécution à un digest de plan."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(min_length=1)
    plan_identity: ExperimentalReplicationPlanIdentity


class ExperimentalExecutionPlanBindingError(RuntimeError):
    """Erreur de base de la liaison plan/exécution expérimentale."""


class ExperimentalExecutionPlanBindingIntegrityError(ExperimentalExecutionPlanBindingError):
    """Refuser de remplacer le plan déjà lié à une exécution."""


class ExperimentalExecutionPlanBindingRepository(Protocol):
    """Persistance append-only de la liaison d'exécution P3 DEV."""

    def get(self, *, execution_id: str) -> ExperimentalExecutionPlanBinding | None: ...

    def bind(
        self, binding: ExperimentalExecutionPlanBinding
    ) -> ExperimentalExecutionPlanBinding: ...


class ExperimentalExecutionPlanBindingService:
    """Façade expérimentale d'une liaison idempotente et immuable."""

    def __init__(self, repository: ExperimentalExecutionPlanBindingRepository) -> None:
        self._repository = repository

    def get(self, *, execution_id: str) -> ExperimentalExecutionPlanBinding | None:
        return self._repository.get(execution_id=execution_id)

    def bind(
        self,
        *,
        execution_id: str,
        plan_identity: ExperimentalReplicationPlanIdentity,
    ) -> ExperimentalExecutionPlanBinding:
        return self._repository.bind(
            ExperimentalExecutionPlanBinding(
                execution_id=execution_id,
                plan_identity=plan_identity,
            )
        )
