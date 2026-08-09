"""Configuration cognitive immuable d'une exécution expérimentale P3 DEV."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.experiments.p3.execution_binding import (
    ExperimentalExecutionPlanBindingRepository,
)
from soinesis.experiments.p3.provenance import (
    ExperimentalExecutionGenerationProvenanceRepository,
)
from soinesis.experiments.p3.replication_manifest import (
    ExperimentalReplicationManifestRepository,
)

CONDITION_CONFIGURATION_SCHEME = "p3-condition-config-v1"
DEV_ESTIMATOR_LAMBDAS = frozenset(
    Decimal(value) for value in ("0.90", "0.92", "0.94", "0.95", "0.96", "0.97")
)


class ExperimentalCondition(StrEnum):
    """Conditions cognitives autorisées dans la tranche P3 DEV 3R."""

    A = "A"
    B = "B"
    C = "C"


class ExperimentalConditionConfiguration(BaseModel):
    """Figer uniquement la condition et son éventuel facteur d'oubli."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scheme: Literal["p3-condition-config-v1"]
    condition: ExperimentalCondition
    estimator_lambda: Decimal | None

    @model_validator(mode="after")
    def validate_condition_lambda(self) -> ExperimentalConditionConfiguration:
        if self.condition is ExperimentalCondition.A:
            if self.estimator_lambda is not None:
                raise ValueError("La condition A n'accepte aucun estimator_lambda.")
            return self
        if self.estimator_lambda is None:
            raise ValueError("Les conditions B et C exigent estimator_lambda.")
        if not self.estimator_lambda.is_finite():
            raise ValueError("estimator_lambda doit être fini.")
        if self.estimator_lambda not in DEV_ESTIMATOR_LAMBDAS:
            raise ValueError("estimator_lambda doit appartenir à la grille DEV autorisée.")
        return self


class ExperimentalExecutionConditionConfiguration(BaseModel):
    """Associer une configuration cognitive immuable à une exécution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(min_length=1)
    configuration: ExperimentalConditionConfiguration


class ExperimentalConditionConfigurationError(RuntimeError):
    """Erreur de base de configuration de condition P3 DEV."""


class ExperimentalConditionConfigurationIntegrityError(ExperimentalConditionConfigurationError):
    """Refuser un prérequis incohérent ou le remplacement d'une configuration."""


class ExperimentalExecutionConditionConfigurationRepository(Protocol):
    """Persistance append-only d'une configuration de condition par exécution."""

    def get(self, *, execution_id: str) -> ExperimentalExecutionConditionConfiguration | None: ...

    def register(
        self, configuration: ExperimentalExecutionConditionConfiguration
    ) -> ExperimentalExecutionConditionConfiguration: ...


class ExperimentalExecutionConditionConfigurationService:
    """Enregistrer 3R seulement après les artefacts immuables 3N, 3O et 3P."""

    def __init__(
        self,
        *,
        repository: ExperimentalExecutionConditionConfigurationRepository,
        binding_repository: ExperimentalExecutionPlanBindingRepository,
        provenance_repository: ExperimentalExecutionGenerationProvenanceRepository,
        manifest_repository: ExperimentalReplicationManifestRepository,
    ) -> None:
        self._repository = repository
        self._binding_repository = binding_repository
        self._provenance_repository = provenance_repository
        self._manifest_repository = manifest_repository

    def get(self, *, execution_id: str) -> ExperimentalExecutionConditionConfiguration | None:
        return self._repository.get(execution_id=execution_id)

    def register(
        self,
        *,
        execution_id: str,
        configuration: ExperimentalConditionConfiguration,
    ) -> ExperimentalExecutionConditionConfiguration:
        binding = self._binding_repository.get(execution_id=execution_id)
        if binding is None:
            raise ExperimentalConditionConfigurationIntegrityError(
                "Un binding 3N doit précéder la configuration de condition."
            )
        provenance = self._provenance_repository.get(execution_id=execution_id)
        if provenance is None:
            raise ExperimentalConditionConfigurationIntegrityError(
                "Une provenance 3O doit précéder la configuration de condition."
            )
        manifest = self._manifest_repository.get(execution_id=execution_id)
        if manifest is None:
            raise ExperimentalConditionConfigurationIntegrityError(
                "Un manifeste 3P doit précéder la configuration de condition."
            )
        if (
            binding.execution_id != execution_id
            or provenance.execution_id != execution_id
            or manifest.execution_id != execution_id
        ):
            raise ExperimentalConditionConfigurationIntegrityError(
                "Les prérequis 3N, 3O et 3P appartiennent à une autre exécution."
            )
        if binding.plan_identity != provenance.generation_provenance.plan_identity:
            raise ExperimentalConditionConfigurationIntegrityError(
                "Le binding 3N et la provenance 3O sont incohérents."
            )
        return self._repository.register(
            ExperimentalExecutionConditionConfiguration(
                execution_id=execution_id,
                configuration=configuration,
            )
        )
