"""Manifeste public immuable des 180 cycles d'une réplication P3 DEV."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.experiments.p3.execution_binding import (
    ExperimentalExecutionPlanBindingRepository,
)
from soinesis.experiments.p3.provenance import (
    ExperimentalExecutionGenerationProvenanceRepository,
)
from soinesis.experiments.p3.runner import ExperimentalCycleStartContext

_TOTAL_CYCLES = 180


class ExperimentalReplicationCycleContext(BaseModel):
    """Associer un index public au contexte 3M fourni par l'appelant."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sequence_index: int = Field(ge=0, lt=_TOTAL_CYCLES, strict=True)
    start_context: ExperimentalCycleStartContext


class ExperimentalReplicationExecutionManifest(BaseModel):
    """Figer tous les contextes publics sans contenir le plan latent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(min_length=1)
    cycle_contexts: tuple[ExperimentalReplicationCycleContext, ...] = Field(
        min_length=_TOTAL_CYCLES,
        max_length=_TOTAL_CYCLES,
    )

    @model_validator(mode="after")
    def validate_complete_ordered_manifest(self) -> ExperimentalReplicationExecutionManifest:
        expected_indices = tuple(range(_TOTAL_CYCLES))
        actual_indices = tuple(context.sequence_index for context in self.cycle_contexts)
        if actual_indices != expected_indices:
            raise ValueError("Le manifeste doit contenir exactement les indices 0 à 179 ordonnés.")
        performance_ids = tuple(
            context.start_context.performance_id for context in self.cycle_contexts
        )
        if len(set(performance_ids)) != _TOTAL_CYCLES:
            raise ValueError("Chaque performance_id doit être unique dans une exécution.")
        agent_ids = {context.start_context.agent_id for context in self.cycle_contexts}
        if len(agent_ids) != 1:
            raise ValueError("Une exécution doit représenter la trajectoire d'un seul agent_id.")
        return self


class ExperimentalReplicationManifestError(RuntimeError):
    """Erreur de base du manifeste public expérimental P3 DEV."""


class ExperimentalReplicationManifestIntegrityError(ExperimentalReplicationManifestError):
    """Refuser un manifeste partiel, corrompu ou incompatible avec 3N/3O."""


class ExperimentalReplicationManifestRepository(Protocol):
    """Persistance atomique et append-only d'un manifeste complet."""

    def get(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest | None: ...

    def register(
        self, manifest: ExperimentalReplicationExecutionManifest
    ) -> ExperimentalReplicationExecutionManifest: ...


class ExperimentalReplicationManifestService:
    """Enregistrer un manifeste seulement après les garanties 3N et 3O."""

    def __init__(
        self,
        *,
        repository: ExperimentalReplicationManifestRepository,
        binding_repository: ExperimentalExecutionPlanBindingRepository,
        provenance_repository: ExperimentalExecutionGenerationProvenanceRepository,
    ) -> None:
        self._repository = repository
        self._binding_repository = binding_repository
        self._provenance_repository = provenance_repository

    def get(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest | None:
        return self._repository.get(execution_id=execution_id)

    def register(
        self, *, manifest: ExperimentalReplicationExecutionManifest
    ) -> ExperimentalReplicationExecutionManifest:
        binding = self._binding_repository.get(execution_id=manifest.execution_id)
        if binding is None:
            raise ExperimentalReplicationManifestIntegrityError(
                "Une liaison de plan 3N doit précéder le manifeste."
            )
        provenance = self._provenance_repository.get(execution_id=manifest.execution_id)
        if provenance is None:
            raise ExperimentalReplicationManifestIntegrityError(
                "Une provenance de génération 3O doit précéder le manifeste."
            )
        if binding.plan_identity != provenance.generation_provenance.plan_identity:
            raise ExperimentalReplicationManifestIntegrityError(
                "La liaison 3N et la provenance 3O sont incohérentes."
            )
        return self._repository.register(manifest)
