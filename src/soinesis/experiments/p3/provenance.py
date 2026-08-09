"""Provenance reproductible de la génération des plans P3 DEV."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from soinesis.experiments.p3.execution_binding import (
    ExperimentalExecutionPlanBindingRepository,
)
from soinesis.experiments.p3.plan import (
    ExperimentalReplicationPlan,
    ExperimentalReplicationPlanIdentity,
)


class ExperimentalPlanGenerationProvenance(BaseModel):
    """Décrire l'entrée et le runtime déclarés d'une génération de plan."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scheme: Literal["p3-plan-generation-provenance-v1"]
    plan_identity: ExperimentalReplicationPlanIdentity
    seed: StrictInt
    generator_version: str = Field(min_length=1)
    python_implementation: str = Field(min_length=1)
    python_version: str = Field(min_length=1, pattern=r"^\d+\.\d+\.\d+$")


@dataclass(frozen=True, slots=True)
class ExperimentalGeneratedReplicationPlan:
    """Rapprocher un plan généré de sa provenance sans exposer ses latents."""

    plan: ExperimentalReplicationPlan
    provenance: ExperimentalPlanGenerationProvenance

    def __post_init__(self) -> None:
        if self.provenance.plan_identity != self.plan.identity():
            raise ExperimentalPlanGenerationIntegrityError(
                "La provenance ne correspond pas au contenu du plan généré."
            )


class ExperimentalPlanGenerationError(RuntimeError):
    """Erreur de reproduction d'un plan expérimental P3 DEV."""


class ExperimentalPlanGenerationEnvironmentError(ExperimentalPlanGenerationError):
    """Refuser une reproduction sous un générateur ou runtime différent."""


class ExperimentalPlanGenerationIntegrityError(ExperimentalPlanGenerationError):
    """Refuser une reproduction dont le contenu obtenu diverge du digest déclaré."""


class ExperimentalExecutionGenerationProvenance(BaseModel):
    """Associer une exécution à la provenance du plan déjà lié par 3N."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(min_length=1)
    generation_provenance: ExperimentalPlanGenerationProvenance


class ExperimentalExecutionGenerationProvenanceError(RuntimeError):
    """Erreur de persistance de provenance expérimentale P3 DEV."""


class ExperimentalExecutionGenerationProvenanceIntegrityError(
    ExperimentalExecutionGenerationProvenanceError
):
    """Refuser une provenance sans binding cohérent ou un remplacement."""


class ExperimentalExecutionGenerationProvenanceRepository(Protocol):
    """Persistance append-only de la provenance de génération d'une exécution."""

    def get(self, *, execution_id: str) -> ExperimentalExecutionGenerationProvenance | None: ...

    def register(
        self, provenance: ExperimentalExecutionGenerationProvenance
    ) -> ExperimentalExecutionGenerationProvenance: ...


class ExperimentalExecutionGenerationProvenanceService:
    """Enregistrer une provenance uniquement après un binding 3N cohérent."""

    def __init__(
        self,
        *,
        repository: ExperimentalExecutionGenerationProvenanceRepository,
        binding_repository: ExperimentalExecutionPlanBindingRepository,
    ) -> None:
        self._repository = repository
        self._binding_repository = binding_repository

    def get(self, *, execution_id: str) -> ExperimentalExecutionGenerationProvenance | None:
        return self._repository.get(execution_id=execution_id)

    def register(
        self,
        *,
        execution_id: str,
        generation_provenance: ExperimentalPlanGenerationProvenance,
    ) -> ExperimentalExecutionGenerationProvenance:
        candidate = ExperimentalExecutionGenerationProvenance(
            execution_id=execution_id,
            generation_provenance=generation_provenance,
        )
        binding = self._binding_repository.get(execution_id=execution_id)
        if binding is None:
            raise ExperimentalExecutionGenerationProvenanceIntegrityError(
                "Une liaison de plan 3N doit précéder la provenance de génération."
            )
        if binding.plan_identity != generation_provenance.plan_identity:
            raise ExperimentalExecutionGenerationProvenanceIntegrityError(
                "La provenance ne correspond pas au plan lié à cette exécution."
            )
        return self._repository.register(candidate)
