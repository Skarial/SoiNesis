"""Certification persistante de l'appariement des conditions A, B et C de P3 DEV."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.experiments.p3.condition_config import (
    DEV_ESTIMATOR_LAMBDAS,
    ExperimentalCondition,
    ExperimentalExecutionConditionConfiguration,
)
from soinesis.experiments.p3.execution_binding import ExperimentalExecutionPlanBinding
from soinesis.experiments.p3.generation import ExperimentalReplicationPlanGenerator
from soinesis.experiments.p3.plan import ExperimentalReplicationPlanIdentity
from soinesis.experiments.p3.provenance import (
    ExperimentalExecutionGenerationProvenance,
)
from soinesis.experiments.p3.replication_manifest import (
    ExperimentalReplicationExecutionManifest,
)


class ExperimentalPairedConditionGroup(BaseModel):
    """Attester un triplet A/B/C sans exposer le plan latent ni sa seed."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pairing_id: str = Field(min_length=1)
    execution_a: str = Field(min_length=1)
    execution_b: str = Field(min_length=1)
    execution_c: str = Field(min_length=1)
    plan_identity: ExperimentalReplicationPlanIdentity
    estimator_lambda: Decimal

    @model_validator(mode="after")
    def validate_public_pairing(self) -> ExperimentalPairedConditionGroup:
        if len({self.execution_a, self.execution_b, self.execution_c}) != 3:
            raise ValueError("Les trois exécutions appariées doivent être distinctes.")
        if not self.estimator_lambda.is_finite():
            raise ValueError("estimator_lambda doit être fini.")
        if self.estimator_lambda not in DEV_ESTIMATOR_LAMBDAS:
            raise ValueError("estimator_lambda doit appartenir à la grille DEV autorisée.")
        return self


class ExperimentalPairingError(RuntimeError):
    """Erreur de base de l'appariement expérimental P3 DEV."""


class ExperimentalPairingIntegrityError(ExperimentalPairingError):
    """Refuser un triplet incomplet, contaminé ou déjà apparié autrement."""


class ExperimentalPairedConditionGroupRepository(Protocol):
    """Persistance atomique et append-only des certificats de pairing."""

    def get(self, *, pairing_id: str) -> ExperimentalPairedConditionGroup | None: ...

    def register(
        self, group: ExperimentalPairedConditionGroup
    ) -> ExperimentalPairedConditionGroup: ...


class _ConditionConfigurationReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalExecutionConditionConfiguration | None: ...


class _ExecutionBindingReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalExecutionPlanBinding | None: ...


class _GenerationProvenanceReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalExecutionGenerationProvenance | None: ...


class _ManifestReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest | None: ...


class ExperimentalPairedConditionGroupService:
    """Certifier A/B/C depuis les artefacts immuables 3N à 3R, sans les exécuter."""

    def __init__(
        self,
        *,
        repository: ExperimentalPairedConditionGroupRepository,
        configuration_service: _ConditionConfigurationReader,
        binding_service: _ExecutionBindingReader,
        provenance_service: _GenerationProvenanceReader,
        manifest_service: _ManifestReader,
        plan_generator: ExperimentalReplicationPlanGenerator,
    ) -> None:
        self._repository = repository
        self._configuration_service = configuration_service
        self._binding_service = binding_service
        self._provenance_service = provenance_service
        self._manifest_service = manifest_service
        self._plan_generator = plan_generator

    def get(self, *, pairing_id: str) -> ExperimentalPairedConditionGroup | None:
        return self._repository.get(pairing_id=pairing_id)

    def register(
        self,
        *,
        pairing_id: str,
        execution_a: str,
        execution_b: str,
        execution_c: str,
    ) -> ExperimentalPairedConditionGroup:
        """Terminer tout le préflight en lecture avant l'unique écriture atomique."""
        self._validate_identifiers(
            pairing_id=pairing_id,
            executions=(execution_a, execution_b, execution_c),
        )
        executions = (execution_a, execution_b, execution_c)
        configurations = (
            self._require_configuration(execution_id=execution_a),
            self._require_configuration(execution_id=execution_b),
            self._require_configuration(execution_id=execution_c),
        )
        self._validate_conditions(configurations=configurations)
        estimator_lambda = self._common_lambda(configurations=configurations)

        bindings = (
            self._require_binding(execution_id=execution_a),
            self._require_binding(execution_id=execution_b),
            self._require_binding(execution_id=execution_c),
        )
        provenances = (
            self._require_provenance(execution_id=execution_a),
            self._require_provenance(execution_id=execution_b),
            self._require_provenance(execution_id=execution_c),
        )
        plan_identity = self._validate_plan_artifacts(
            executions=executions,
            bindings=bindings,
            provenances=provenances,
        )
        reproduced_plan = self._plan_generator.reproduce(
            provenance=provenances[0].generation_provenance
        )
        if reproduced_plan.identity() != plan_identity:
            raise ExperimentalPairingIntegrityError(
                "Le plan reproduit ne correspond pas à l'identité commune."
            )

        manifests = (
            self._require_manifest(execution_id=execution_a),
            self._require_manifest(execution_id=execution_b),
            self._require_manifest(execution_id=execution_c),
        )
        self._validate_manifests(executions=executions, manifests=manifests)

        return self._repository.register(
            ExperimentalPairedConditionGroup(
                pairing_id=pairing_id,
                execution_a=execution_a,
                execution_b=execution_b,
                execution_c=execution_c,
                plan_identity=plan_identity,
                estimator_lambda=estimator_lambda,
            )
        )

    @staticmethod
    def _validate_identifiers(*, pairing_id: str, executions: tuple[str, str, str]) -> None:
        if type(pairing_id) is not str or not pairing_id:
            raise ValueError("pairing_id doit être une chaîne opaque non vide.")
        if any(type(execution_id) is not str or not execution_id for execution_id in executions):
            raise ValueError("Chaque execution_id doit être une chaîne opaque non vide.")
        if len(set(executions)) != 3:
            raise ExperimentalPairingIntegrityError(
                "Les trois rôles A, B et C exigent des exécutions distinctes."
            )

    def _require_configuration(
        self, *, execution_id: str
    ) -> ExperimentalExecutionConditionConfiguration:
        configuration = self._configuration_service.get(execution_id=execution_id)
        if configuration is None:
            raise ExperimentalPairingIntegrityError(
                "Chaque exécution appariée exige une configuration 3R."
            )
        if configuration.execution_id != execution_id:
            raise ExperimentalPairingIntegrityError(
                "Une configuration 3R appartient à une autre exécution."
            )
        return configuration

    @staticmethod
    def _validate_conditions(
        *,
        configurations: tuple[
            ExperimentalExecutionConditionConfiguration,
            ExperimentalExecutionConditionConfiguration,
            ExperimentalExecutionConditionConfiguration,
        ],
    ) -> None:
        actual = tuple(configuration.configuration.condition for configuration in configurations)
        if actual != (
            ExperimentalCondition.A,
            ExperimentalCondition.B,
            ExperimentalCondition.C,
        ):
            raise ExperimentalPairingIntegrityError(
                "Les rôles execution_a, execution_b et execution_c doivent être configurés A, B, C."
            )

    @staticmethod
    def _common_lambda(
        *,
        configurations: tuple[
            ExperimentalExecutionConditionConfiguration,
            ExperimentalExecutionConditionConfiguration,
            ExperimentalExecutionConditionConfiguration,
        ],
    ) -> Decimal:
        lambda_a = configurations[0].configuration.estimator_lambda
        lambda_b = configurations[1].configuration.estimator_lambda
        lambda_c = configurations[2].configuration.estimator_lambda
        if lambda_a is not None or lambda_b is None or lambda_c is None or lambda_b != lambda_c:
            raise ExperimentalPairingIntegrityError(
                "A doit être sans lambda et B/C doivent partager exactement le même lambda."
            )
        return lambda_b

    def _require_binding(self, *, execution_id: str) -> ExperimentalExecutionPlanBinding:
        binding = self._binding_service.get(execution_id=execution_id)
        if binding is None:
            raise ExperimentalPairingIntegrityError(
                "Chaque exécution appariée exige un binding 3N."
            )
        return binding

    def _require_provenance(
        self, *, execution_id: str
    ) -> ExperimentalExecutionGenerationProvenance:
        provenance = self._provenance_service.get(execution_id=execution_id)
        if provenance is None:
            raise ExperimentalPairingIntegrityError(
                "Chaque exécution appariée exige une provenance 3O."
            )
        return provenance

    @staticmethod
    def _validate_plan_artifacts(
        *,
        executions: tuple[str, str, str],
        bindings: tuple[
            ExperimentalExecutionPlanBinding,
            ExperimentalExecutionPlanBinding,
            ExperimentalExecutionPlanBinding,
        ],
        provenances: tuple[
            ExperimentalExecutionGenerationProvenance,
            ExperimentalExecutionGenerationProvenance,
            ExperimentalExecutionGenerationProvenance,
        ],
    ) -> ExperimentalReplicationPlanIdentity:
        for execution_id, binding, provenance in zip(
            executions, bindings, provenances, strict=True
        ):
            if binding.execution_id != execution_id or provenance.execution_id != execution_id:
                raise ExperimentalPairingIntegrityError(
                    "Un binding 3N ou une provenance 3O appartient à une autre exécution."
                )
            if binding.plan_identity != provenance.generation_provenance.plan_identity:
                raise ExperimentalPairingIntegrityError(
                    "Un binding 3N diverge de sa provenance 3O."
                )
        if len({binding.plan_identity.fingerprint for binding in bindings}) != 1:
            raise ExperimentalPairingIntegrityError(
                "Les trois exécutions ne partagent pas le même plan latent."
            )
        canonical_provenance = provenances[0].generation_provenance
        if any(
            provenance.generation_provenance != canonical_provenance
            for provenance in provenances[1:]
        ):
            raise ExperimentalPairingIntegrityError(
                "Les trois exécutions ne partagent pas la même provenance générative."
            )
        return bindings[0].plan_identity

    def _require_manifest(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest:
        manifest = self._manifest_service.get(execution_id=execution_id)
        if manifest is None:
            raise ExperimentalPairingIntegrityError(
                "Chaque exécution appariée exige un manifeste 3P."
            )
        return manifest

    @staticmethod
    def _validate_manifests(
        *,
        executions: tuple[str, str, str],
        manifests: tuple[
            ExperimentalReplicationExecutionManifest,
            ExperimentalReplicationExecutionManifest,
            ExperimentalReplicationExecutionManifest,
        ],
    ) -> None:
        if any(
            manifest.execution_id != execution_id
            for execution_id, manifest in zip(executions, manifests, strict=True)
        ):
            raise ExperimentalPairingIntegrityError(
                "Un manifeste 3P appartient à une autre exécution."
            )
        agents = tuple(
            next(iter({context.start_context.agent_id for context in manifest.cycle_contexts}))
            for manifest in manifests
        )
        if len(set(agents)) != 3:
            raise ExperimentalPairingIntegrityError(
                "Les trois manifestes doivent décrire des agents cognitifs distincts."
            )
        performance_id_sets = tuple(
            {context.start_context.performance_id for context in manifest.cycle_contexts}
            for manifest in manifests
        )
        if any(
            left & right
            for index, left in enumerate(performance_id_sets)
            for right in performance_id_sets[index + 1 :]
        ):
            raise ExperimentalPairingIntegrityError(
                "Les performance_id publics des trois manifestes doivent être disjoints."
            )
        expected_indices = tuple(range(180))
        indices = tuple(
            tuple(context.sequence_index for context in manifest.cycle_contexts)
            for manifest in manifests
        )
        if any(actual != expected_indices for actual in indices):
            raise ExperimentalPairingIntegrityError(
                "Chaque manifeste doit conserver exactement les positions 0 à 179."
            )
        chronologies = tuple(
            tuple(context.start_context.observed_at for context in manifest.cycle_contexts)
            for manifest in manifests
        )
        if chronologies[1:] != (chronologies[0], chronologies[0]):
            raise ExperimentalPairingIntegrityError(
                "Les trois manifestes doivent partager exactement la même chronologie publique."
            )
