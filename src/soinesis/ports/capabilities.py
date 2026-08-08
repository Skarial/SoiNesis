"""Ports de persistance P3 sans adapter ni politique expérimentale."""

from __future__ import annotations

from typing import Protocol

from soinesis.domain.capabilities import (
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.ports.repositories import UnitOfWork


class CapabilityPerformanceRepository(Protocol):
    """Persister les preuves intrinsèques et exposer seulement leur passé causal.

    Le schéma accepté exclut la vérité terrain, la phase privée, la graine et tout
    identifiant de dataset OFFICIAL. Ces informations n'appartiennent jamais à ce port.
    """

    def add(self, observation: CapabilityPerformanceObservation) -> None:
        """Ajouter une preuve à la fin de la chronologie publique de son agent.

        ``sequence_index`` doit être strictement supérieur à tous les indices déjà
        persistés pour le même agent, toutes capacités confondues. Chaque agent possède
        sa propre chronologie indépendante.
        """
        ...

    def get(self, observation_id: str) -> CapabilityPerformanceObservation | None:
        """Relire une preuve persistée exacte sans accepter un objet arbitraire en mémoire."""
        ...

    def list_before(
        self,
        *,
        boundary: CapabilityHistoryBoundary,
    ) -> list[CapabilityPerformanceObservation]:
        """Retourner le passé strict de ``boundary`` dans l'ordre causal croissant.

        Le résultat contient exclusivement le même agent et la même capacité, avec
        ``sequence_index < boundary.sequence_index``. Il est ordonné de façon
        déterministe par ``(sequence_index, observed_at, id)``. Le cycle courant et
        tout événement futur sont exclus.
        """
        ...


class MetacognitiveStateRepository(Protocol):
    """Accéder à l'état statistique courant sans exposer de logique de mise à jour."""

    def get_current(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> VersionedMetacognitiveCapabilityState | None: ...

    def replace_current(
        self,
        *,
        state: VersionedMetacognitiveCapabilityState,
        expected_version: int | None,
    ) -> None:
        """Remplacer l'état seulement si sa version courante est celle attendue.

        ``expected_version=None`` réserve la création d'un premier état. Toute
        divergence doit être refusée par le futur adapter de persistance.
        """
        ...


class SelfModelVersionRepository(Protocol):
    """Ajouter et relire les versions globales immuables d'un SelfModel."""

    def add(self, version: SelfModelVersion) -> None:
        """Ajouter une version sans remplacer un identifiant ou numéro existant."""
        ...

    def get_current(self, *, agent_id: str) -> SelfModelVersion | None: ...

    def list_versions(self, *, agent_id: str) -> list[SelfModelVersion]:
        """Retourner les versions de l'agent par numéro strictement croissant."""
        ...


class CapabilitySelfAttributeRepository(Protocol):
    """Ajouter et relire les versions immuables d'un attribut de capacité."""

    def add(self, attribute: CapabilitySelfAttribute) -> None:
        """Ajouter une version sans remplacer un attribut historique existant."""
        ...

    def get_current(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> CapabilitySelfAttribute | None: ...

    def list_versions(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> list[CapabilitySelfAttribute]:
        """Retourner l'historique filtré par version d'attribut croissante."""
        ...


class CapabilityUnitOfWork(UnitOfWork, Protocol):
    """Extension additive du UoW historique pour les futures transactions P3."""

    @property
    def capability_performances(self) -> CapabilityPerformanceRepository: ...

    @property
    def metacognitive_states(self) -> MetacognitiveStateRepository: ...

    @property
    def self_model_versions(self) -> SelfModelVersionRepository: ...

    @property
    def capability_self_attributes(self) -> CapabilitySelfAttributeRepository: ...


class CapabilityUnitOfWorkFactory(Protocol):
    """Construire un UoW doté des ports P3 sans modifier la factory historique."""

    def __call__(self) -> CapabilityUnitOfWork: ...
