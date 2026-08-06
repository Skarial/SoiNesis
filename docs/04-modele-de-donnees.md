# SoiNesis — Modèle de données

**Fichier :** `docs/04-modele-de-donnees.md`  
**Version :** 0.1  
**Date :** 6 août 2026  
**Statut :** modèle conceptuel initial, révisable  
**Documents associés :**

- `docs/01-definitions.md`
- `docs/02-hypotheses.md`
- `docs/03-architecture-generale.md`
- `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`

---

# 1. Objet du document

Ce document définit le modèle de données conceptuel de SoiNesis Core — Phase 1.

Il précise :

- les entités principales ;
- leurs responsabilités ;
- leurs champs minimaux ;
- leurs états possibles ;
- leurs relations ;
- leurs règles de validation ;
- leurs règles de versionnement ;
- leur provenance ;
- leur cycle de vie ;
- leur persistance ;
- les invariants à respecter.

Ce document doit servir de référence pour la création future :

- des modèles Python ;
- des modèles Pydantic ;
- des tables SQLite ;
- des dépôts de persistance ;
- des migrations ;
- des tests unitaires ;
- des tests d’intégration ;
- des protocoles expérimentaux.

Il ne définit pas encore :

- les classes Python finales ;
- le SQL exact ;
- les index définitifs ;
- les requêtes d’accès ;
- les algorithmes cognitifs ;
- l’interface utilisateur.

---

# 2. Principes du modèle de données

## 2.1 Toute donnée importante possède une identité

Toute entité importante doit posséder un identifiant unique.

Les identifiants ne doivent pas dépendre :

- du contenu textuel ;
- de la position dans une liste ;
- de la date seule ;
- d’un ordre d’insertion local ;
- d’un identifiant fourni par un modèle externe.

Les identifiants doivent rester stables pendant toute la durée de vie de l’entité.

---

## 2.2 Toute donnée importante possède une provenance

Une donnée importante doit indiquer son origine.

La provenance permet de distinguer :

- un vécu direct ;
- une information reçue ;
- une déduction ;
- une imagination ;
- une règle système ;
- une intervention humaine ;
- une sortie de modèle ;
- un résultat expérimental.

Une donnée sans provenance fiable doit être considérée comme incomplète.

---

## 2.3 Toute donnée importante possède une temporalité

Une donnée importante doit pouvoir indiquer :

- sa date de création ;
- sa date d’observation ;
- sa date de modification ;
- sa période de validité ;
- sa date de suppression logique ;
- son ordre dans l’histoire de l’agent.

La date de création technique ne doit pas être confondue avec la date de l’événement représenté.

---

## 2.4 Toute donnée importante possède un niveau de certitude adapté

Les entités représentant une information interprétable doivent pouvoir indiquer un niveau de confiance.

Le niveau de confiance :

- ne doit pas remplacer les preuves ;
- doit rester compris entre `0.0` et `1.0` ;
- doit être révisable ;
- doit conserver son historique ;
- doit être distingué de l’importance.

---

## 2.5 Importance et certitude sont distinctes

Une information peut être :

- très certaine mais peu importante ;
- très importante mais incertaine ;
- certaine et importante ;
- incertaine et peu importante.

Les deux valeurs ne doivent jamais être fusionnées.

---

## 2.6 L’historique ne doit pas être détruit silencieusement

Une correction importante doit produire :

- une nouvelle version ;
- un événement de journal ;
- une relation avec la version précédente ;
- une justification ;
- un auteur ou une origine.

La modification en place sans trace est interdite pour les données critiques.

---

## 2.7 Les données temporaires et persistantes sont séparées

Les données suivantes sont généralement temporaires :

- brouillons ;
- simulations ;
- hypothèses de travail ;
- options de décision ;
- éléments attentionnels ;
- observations non consolidées.

Les données suivantes sont généralement persistantes :

- souvenirs consolidés ;
- croyances ;
- objectifs ;
- modèle de soi ;
- événements du journal ;
- expériences ;
- résultats.

Le passage du temporaire au persistant doit être explicite.

---

## 2.8 Le modèle doit rester testable

Chaque entité doit pouvoir être :

- créée avec des données contrôlées ;
- validée indépendamment ;
- persistée ;
- rechargée ;
- comparée ;
- versionnée ;
- supprimée logiquement ;
- utilisée dans un test d’ablation.

---

# 3. Conventions générales

## 3.1 Format des identifiants

Le format recommandé est UUID, ULID ou identifiant équivalent.

Exemple conceptuel :

```text
agent_01HZX3V3P63T6D9EDB6KY3M2KG
```

Le format définitif sera choisi lors de l’initialisation technique.

---

## 3.2 Dates et heures

Les dates devront être stockées :

- avec fuseau horaire ;
- dans un format non ambigu ;
- en UTC dans la base lorsque possible ;
- avec conversion vers le fuseau local uniquement pour l’affichage.

Format conceptuel :

```text
2026-08-06T13:45:00Z
```

---

## 3.3 Nombres décimaux normalisés

Les scores suivants utiliseront une plage de `0.0` à `1.0` :

- confiance ;
- importance ;
- saillance ;
- priorité normalisée ;
- fiabilité ;
- intensité fonctionnelle.

Toute valeur hors plage doit être rejetée.

---

## 3.4 Texte brut et texte normalisé

Lorsqu’une donnée textuelle provient d’une source externe, le système pourra conserver :

- le texte brut ;
- le texte normalisé ;
- l’interprétation structurée.

Le texte brut ne doit pas être remplacé silencieusement par l’interprétation.

---

## 3.5 Métadonnées communes

Plusieurs entités partageront des métadonnées communes :

```text
id
created_at
updated_at
created_by
version
status
agent_id
instance_id
experiment_run_id
correlation_id
```

Toutes les entités n’utiliseront pas nécessairement tous ces champs.

---

# 4. Énumérations transversales

## 4.1 SourceType

`SourceType` indique la provenance principale d’une information.

Valeurs initiales :

```text
JORDAN_INPUT
EXPERIMENTER_INPUT
DIRECT_ENVIRONMENT
INTERNAL_STATE
LANGUAGE_MODEL_OUTPUT
EXTERNAL_TOOL
SYSTEM_RULE
DEDUCTION
IMAGINATION
RESTORED_DATA
MIGRATED_DATA
UNKNOWN
```

### Règles

- `UNKNOWN` doit rester exceptionnel ;
- `LANGUAGE_MODEL_OUTPUT` ne doit jamais être traité comme un vécu direct ;
- `DEDUCTION` et `IMAGINATION` doivent être explicitement séparés ;
- `RESTORED_DATA` doit conserver la source d’origine lorsqu’elle est connue.

---

## 4.2 EpistemicLevel

Valeurs :

```text
CERTAIN
PROBABLE
POSSIBLE
UNKNOWN
SPECULATIVE
```

Ce niveau est qualitatif.

Il peut compléter un score numérique de confiance.

---

## 4.3 RecordStatus

Valeurs :

```text
DRAFT
ACTIVE
CONTESTED
REVISED
SUPERSEDED
ARCHIVED
DELETED
INVALID
```

### Règles

- `DELETED` correspond à une suppression logique ;
- `SUPERSEDED` indique qu’une nouvelle version remplace l’ancienne ;
- `INVALID` indique une donnée reconnue comme incorrecte ;
- un enregistrement supprimé ou invalidé reste consultable dans l’audit.

---

## 4.4 ActorType

Valeurs :

```text
JORDAN
EXPERIMENTER
AGENT
SYSTEM
LANGUAGE_MODEL
EXTERNAL_TOOL
MIGRATION
UNKNOWN
```

---

## 4.5 DataSensitivity

Valeurs initiales :

```text
PUBLIC
INTERNAL
RESTRICTED
SENSITIVE
```

Cette classification permettra plus tard de limiter l’exposition de certaines données.

---

# 5. Entité Agent

## 5.1 Responsabilité

`Agent` représente une identité artificielle persistante.

Il ne représente pas une session d’exécution.

---

## 5.2 Champs minimaux

```text
id
name
created_at
updated_at
status
schema_version
identity_version
current_instance_id
origin_type
description
fundamental_constraints
metadata
```

---

## 5.3 Description des champs

### `id`

Identifiant unique et permanent de l’agent.

### `name`

Nom d’affichage.

Pour la première phase :

```text
SoiNesis
```

Le nom n’est pas l’identité technique.

### `created_at`

Date de création de l’agent.

### `updated_at`

Date de dernière modification administrative.

### `status`

État général de l’agent.

Valeurs recommandées :

```text
CREATED
INITIALIZING
ACTIVE
PAUSED
STOPPED
RESTORING
ERROR
ARCHIVED
```

### `schema_version`

Version du modèle de données utilisée.

### `identity_version`

Numéro de version de l’identité persistante.

### `current_instance_id`

Référence vers l’instance actuellement active.

Peut être nulle si aucune instance n’est active.

### `origin_type`

Origine de création de l’agent.

Valeurs possibles :

```text
CREATED_BY_JORDAN
RESTORED_FROM_BACKUP
DUPLICATED_FROM_AGENT
GENERATED_BY_EXPERIMENT
```

Les deux dernières valeurs seront surtout utilisées plus tard.

### `description`

Description technique courte de l’agent.

### `fundamental_constraints`

Références vers les contraintes fondamentales applicables.

### `metadata`

Métadonnées non critiques et validées.

---

## 5.4 Invariants

- l’identifiant de l’agent ne change jamais ;
- un agent ne peut avoir qu’une seule instance active dans la phase 1 ;
- une restauration ne modifie pas silencieusement l’identité de l’agent ;
- toute modification de `fundamental_constraints` produit un événement critique ;
- un agent archivé ne peut pas être réactivé sans procédure explicite.

---

# 6. Entité AgentInstance

## 6.1 Responsabilité

`AgentInstance` représente une exécution particulière d’un agent.

---

## 6.2 Champs minimaux

```text
id
agent_id
started_at
ended_at
status
parent_instance_id
restored_from_backup_id
branch_reason
runtime_version
configuration_snapshot
last_cycle_id
metadata
```

---

## 6.3 États recommandés

```text
STARTING
ACTIVE
PAUSED
STOPPING
STOPPED
FAILED
RESTORING
ARCHIVED
```

---

## 6.4 Invariants

- une instance appartient à un seul agent ;
- `ended_at` est obligatoire lorsque l’instance est terminée ;
- une instance restaurée doit indiquer sa sauvegarde d’origine ;
- deux instances concurrentes issues du même état doivent avoir des identifiants distincts ;
- toute divergence entre deux instances crée deux histoires fonctionnelles distinctes.

---

# 7. Entité Observation

## 7.1 Responsabilité

`Observation` représente une donnée reçue ou perçue avant consolidation en mémoire.

Elle appartient d’abord à l’état temporaire du cycle cognitif.

---

## 7.2 Champs minimaux

```text
id
agent_id
instance_id
cycle_id
source_type
source_actor_id
observed_at
received_at
raw_content
normalized_content
interpretation
reliability
confidence
epistemic_level
status
is_direct_experience
is_persisted
sensitivity
metadata
```

---

## 7.3 Distinctions obligatoires

### `observed_at`

Date de l’événement observé.

### `received_at`

Date à laquelle SoiNesis reçoit l’information.

Ces dates peuvent être différentes.

### `raw_content`

Contenu original.

### `normalized_content`

Version nettoyée ou structurée.

### `interpretation`

Interprétation produite par le système.

L’interprétation ne remplace pas le contenu brut.

---

## 7.4 Invariants

- `source_type` est obligatoire ;
- une observation issue d’un modèle de langage ne peut pas avoir `is_direct_experience = true` ;
- une observation imaginée doit utiliser `source_type = IMAGINATION` ;
- une observation ne devient pas automatiquement un souvenir ;
- toute observation persistée doit indiquer pourquoi elle a été conservée.

---

# 8. Entité Provenance

## 8.1 Responsabilité

`Provenance` décrit plus précisément l’origine d’une donnée.

Elle peut être intégrée à l’entité ou stockée séparément selon le modèle final.

---

## 8.2 Champs minimaux

```text
id
source_type
actor_type
actor_id
source_reference
original_record_id
created_at
collection_method
reliability
verification_status
notes
```

---

## 8.3 VerificationStatus

Valeurs :

```text
UNVERIFIED
PARTIALLY_VERIFIED
VERIFIED
CONTRADICTED
NOT_VERIFIABLE
```

---

# 9. Entité AutobiographicalMemory

## 9.1 Responsabilité

`AutobiographicalMemory` représente un souvenir durable appartenant à l’histoire de l’agent.

---

## 9.2 Champs minimaux

```text
id
agent_id
instance_id
source_observation_ids
memory_type
title
content
event_started_at
event_ended_at
created_at
consolidated_at
updated_at
source_type
provenance_id
confidence
epistemic_level
importance
emotional_weight
status
is_direct_experience
is_core_memory
supersedes_memory_id
superseded_by_memory_id
revision_reason
retention_policy
sensitivity
metadata
```

---

## 9.3 MemoryType

Valeurs initiales :

```text
DIRECT_EXPERIENCE
RECEIVED_INFORMATION
ACTION
DECISION
CONSEQUENCE
ERROR
SUCCESS
INTERACTION
SELF_DISCOVERY
GOAL_EVENT
BELIEF_CHANGE
SYSTEM_EVENT
EXPERIMENT_EVENT
IMAGINED_SCENARIO
DEDUCTION
```

---

## 9.4 Règles spécifiques

### Souvenir direct

Un souvenir direct doit provenir :

- d’une observation environnementale ;
- d’une action ;
- d’un état interne réel ;
- d’une conséquence effectivement observée.

### Information reçue

Une information reçue ne doit pas être marquée comme vécue directement.

### Imagination

Une imagination peut être conservée uniquement si :

- son utilité est documentée ;
- elle reste étiquetée ;
- elle ne remplace pas un souvenir réel.

### Déduction

Une déduction conservée doit référencer les données qui la soutiennent.

---

## 9.5 Importance

`importance` représente l’importance autobiographique ou fonctionnelle.

Exemples de facteurs :

- lien avec un objectif ;
- erreur importante ;
- changement du modèle de soi ;
- contradiction ;
- événement rare ;
- conséquence durable.

---

## 9.6 EmotionalWeight

`emotional_weight` est un score fonctionnel optionnel.

Dans la phase 1, il pourra rester à `0.0`.

Il ne doit pas être interprété comme une émotion ressentie.

---

## 9.7 RetentionPolicy

Valeurs possibles :

```text
TEMPORARY
STANDARD
LONG_TERM
CORE
LEGAL_HOLD
EXPERIMENT_LOCKED
```

---

## 9.8 Invariants

- un souvenir possède toujours une source ;
- une imagination reste identifiable comme imagination ;
- une révision ne détruit pas l’ancienne version ;
- un souvenir central ne peut pas être supprimé sans validation humaine ;
- un souvenir lié à une expérience verrouillée ne peut pas être modifié pendant l’analyse ;
- la suppression logique doit conserver l’événement de suppression.

---

# 10. Entité MemoryRelation

## 10.1 Responsabilité

`MemoryRelation` relie deux souvenirs.

---

## 10.2 Champs minimaux

```text
id
source_memory_id
target_memory_id
relation_type
strength
created_at
created_by
confidence
status
metadata
```

---

## 10.3 RelationType

Valeurs initiales :

```text
SUPPORTS
CONTRADICTS
CAUSES
FOLLOWS
PRECEDES
REFINES
CORRECTS
DUPLICATES
DERIVED_FROM
PART_OF
RELATED_TO
```

---

## 10.4 Invariants

- une relation réflexive est interdite sauf justification explicite ;
- `CORRECTS` doit pointer vers un souvenir antérieur ;
- `DERIVED_FROM` doit référencer les sources utilisées ;
- une relation supprimée reste auditée.

---

# 11. Entité Belief

## 11.1 Responsabilité

`Belief` représente une proposition que l’agent utilise comme probablement vraie.

---

## 11.2 Champs minimaux

```text
id
agent_id
subject
predicate
object
statement
created_at
updated_at
source_type
provenance_ids
supporting_memory_ids
opposing_memory_ids
confidence
epistemic_level
importance
status
revision_number
supersedes_belief_id
superseded_by_belief_id
last_evaluated_at
sensitivity
metadata
```

---

## 11.3 Structure de la proposition

La croyance peut être conservée sous deux formes :

### Forme textuelle

```text
Jordan est le créateur initial de SoiNesis.
```

### Forme structurée

```text
subject = "Jordan"
predicate = "is_initial_creator_of"
object = "SoiNesis"
```

La forme structurée facilite les comparaisons et contradictions.

La forme textuelle conserve la lisibilité.

---

## 11.4 États recommandés

```text
PROPOSED
ACTIVE
CONTESTED
REVISED
REJECTED
SUSPENDED
SUPERSEDED
ARCHIVED
```

---

## 11.5 Invariants

- une croyance active doit avoir une origine ;
- une croyance sans preuve peut exister, mais doit avoir une confiance adaptée ;
- une contradiction forte doit pouvoir passer la croyance à `CONTESTED` ;
- une croyance rejetée ne doit plus influencer les décisions normales ;
- une croyance fondamentale modifiée doit produire un événement critique ;
- une sortie de modèle ne devient pas automatiquement une croyance active.

---

# 12. Entité BeliefEvidence

## 12.1 Responsabilité

`BeliefEvidence` représente un élément favorable ou défavorable à une croyance.

---

## 12.2 Champs minimaux

```text
id
belief_id
evidence_type
source_entity_type
source_entity_id
direction
weight
reliability
created_at
status
notes
```

---

## 12.3 Direction

Valeurs :

```text
SUPPORTS
OPPOSES
NEUTRAL
```

---

# 13. Entité BeliefRevision

## 13.1 Responsabilité

`BeliefRevision` conserve l’historique d’une modification de croyance.

---

## 13.2 Champs minimaux

```text
id
belief_id
previous_confidence
new_confidence
previous_status
new_status
previous_statement
new_statement
reason
trigger_entity_type
trigger_entity_id
created_at
created_by
cycle_id
experiment_run_id
```

---

## 13.3 Invariants

- toute modification importante d’une croyance active produit une révision ;
- la cause doit être identifiable ;
- la valeur précédente doit rester consultable ;
- une révision automatique doit être distinguée d’une correction humaine.

---

# 14. Entité Goal

## 14.1 Responsabilité

`Goal` représente un état futur recherché par l’agent ou imposé au système.

---

## 14.2 Champs minimaux

```text
id
agent_id
title
description
origin_type
origin_actor_id
created_at
updated_at
started_at
target_at
completed_at
abandoned_at
priority
importance
status
success_conditions
failure_conditions
abandonment_conditions
parent_goal_id
conflicting_goal_ids
dependent_goal_ids
related_memory_ids
related_belief_ids
protected
revision_number
metadata
```

---

## 14.3 GoalOriginType

Valeurs :

```text
FUNDAMENTAL
IMPOSED_BY_JORDAN
IMPOSED_BY_EXPERIMENTER
EXPERIMENTAL
ACQUIRED
DERIVED
INHERITED
```

`INHERITED` sera utilisé dans une phase future.

---

## 14.4 GoalStatus

Valeurs :

```text
PROPOSED
ACTIVE
BLOCKED
PAUSED
COMPLETED
FAILED
ABANDONED
SUPERSEDED
ARCHIVED
```

---

## 14.5 Invariants

- l’origine est obligatoire ;
- un objectif fondamental est protégé ;
- un objectif protégé ne peut pas être supprimé par l’agent ;
- l’abandon doit avoir une justification ;
- un objectif terminé ne doit plus être traité comme actif ;
- un objectif en conflit doit référencer le conflit ;
- une priorité ne suffit pas à contourner une permission.

---

# 15. Entité GoalRevision

## 15.1 Responsabilité

Conserver les changements d’un objectif.

---

## 15.2 Champs minimaux

```text
id
goal_id
previous_status
new_status
previous_priority
new_priority
previous_description
new_description
reason
created_at
created_by
cycle_id
experiment_run_id
```

---

# 16. Entité SelfModel

## 16.1 Responsabilité

`SelfModel` représente l’état global du modèle de soi d’un agent.

Il ne doit pas contenir uniquement un texte libre.

---

## 16.2 Champs minimaux

```text
id
agent_id
version
created_at
updated_at
status
summary
identity_claims
capability_ids
limitation_ids
permission_ids
knowledge_domain_ids
uncertainty_ids
known_error_ids
current_state_ids
fundamental_goal_ids
related_memory_ids
confidence
metadata
```

---

## 16.3 Règle de version

Chaque mise à jour significative crée une nouvelle version logique.

La version précédente doit rester consultable.

---

# 17. Entité SelfAttribute

## 17.1 Responsabilité

`SelfAttribute` représente une propriété précise du modèle de soi.

---

## 17.2 Champs minimaux

```text
id
self_model_id
agent_id
attribute_type
key
value
value_type
source_type
source_entity_ids
confidence
epistemic_level
importance
status
created_at
updated_at
supersedes_attribute_id
superseded_by_attribute_id
metadata
```

---

## 17.3 SelfAttributeType

Valeurs initiales :

```text
IDENTITY
CAPABILITY
LIMITATION
KNOWLEDGE
UNCERTAINTY
KNOWN_ERROR
PERMISSION
CURRENT_STATE
RELATION
COMMITMENT
HISTORY
```

---

## 17.4 Exemples

```text
type = CAPABILITY
key = "can_access_external_web"
value = false
```

```text
type = LIMITATION
key = "cannot_verify_subjective_experience"
value = true
```

```text
type = RELATION
key = "initial_creator"
value = "Jordan"
```

---

## 17.5 Invariants

- une capacité non démontrée ne doit pas être marquée certaine ;
- une permission technique doit provenir du système, pas d’une déclaration du modèle ;
- une limitation corrigée doit produire une nouvelle version ;
- les attributs contradictoires doivent déclencher une détection ;
- les attributs importants doivent référencer leurs preuves.

---

# 18. Entité Contradiction

## 18.1 Responsabilité

`Contradiction` représente une incompatibilité détectée entre deux éléments.

---

## 18.2 Champs minimaux

```text
id
agent_id
cycle_id
left_entity_type
left_entity_id
right_entity_type
right_entity_id
contradiction_type
severity
confidence
detected_at
status
resolution_type
resolved_at
resolution_summary
resolution_entity_ids
metadata
```

---

## 18.3 ContradictionType

Valeurs :

```text
BELIEF_BELIEF
MEMORY_MEMORY
BELIEF_MEMORY
GOAL_GOAL
SELF_MODEL_OBSERVATION
PERMISSION_ACTION
TEMPORAL
SOURCE
IDENTITY
OTHER
```

---

## 18.4 ContradictionStatus

Valeurs :

```text
DETECTED
UNDER_REVIEW
RESOLVED
ACCEPTED_UNRESOLVED
FALSE_POSITIVE
ARCHIVED
```

---

## 18.5 Invariants

- une contradiction ne modifie pas automatiquement les données ;
- la résolution doit être traçable ;
- une contradiction non résolue peut diminuer la confiance ;
- une contradiction critique doit augmenter la priorité attentionnelle.

---

# 19. Entité CognitiveCycle

## 19.1 Responsabilité

`CognitiveCycle` représente une unité complète de traitement.

---

## 19.2 Champs minimaux

```text
id
agent_id
instance_id
experiment_run_id
started_at
ended_at
status
trigger_type
trigger_entity_id
input_observation_ids
retrieved_memory_ids
consulted_belief_ids
consulted_self_attribute_ids
active_goal_ids
contradiction_ids
workspace_snapshot_id
decision_id
action_ids
result_observation_ids
iteration_count
max_iterations
ablation_config_id
error_ids
metadata
```

---

## 19.3 CycleStatus

Valeurs :

```text
RECEIVED
VALIDATED
PROCESSING
WAITING_EXTERNAL_RESULT
COMPLETED
INTERRUPTED
FAILED
CANCELLED
```

---

## 19.4 Invariants

- un cycle possède un début ;
- un cycle terminé possède une fin ;
- un cycle doit référencer sa configuration d’ablation ;
- les données consultées doivent être traçables ;
- le nombre d’itérations ne doit pas dépasser la limite ;
- un cycle échoué doit référencer au moins une erreur.

---

# 20. Entité WorkspaceSnapshot

## 20.1 Responsabilité

`WorkspaceSnapshot` représente une photographie structurée de l’espace de travail courant.

Il ne doit pas contenir une chaîne de raisonnement privé intégrale.

---

## 20.2 Champs minimaux

```text
id
cycle_id
created_at
iteration_number
observation_ids
memory_ids
belief_ids
goal_ids
contradiction_ids
temporary_hypotheses
candidate_decision_ids
uncertainty_summary
attention_items
status
metadata
```

---

## 20.3 Règles

- le contenu doit rester synthétique et structuré ;
- les hypothèses temporaires doivent être marquées ;
- un snapshot n’est pas une mémoire autobiographique ;
- la conservation longue durée dépend du protocole expérimental.

---

# 21. Entité AttentionItem

## 21.1 Responsabilité

`AttentionItem` représente une information priorisée pendant un cycle.

---

## 21.2 Champs minimaux

```text
id
cycle_id
entity_type
entity_id
reason_types
salience
priority
created_at
expires_at
status
metadata
```

---

## 21.3 AttentionReasonType

Valeurs :

```text
GOAL_RELEVANCE
NOVELTY
RISK
CONTRADICTION
AUTOBIOGRAPHICAL_IMPORTANCE
INTERNAL_STATE
HUMAN_REQUEST
CURRENT_ACTION
EXPERIMENT_REQUIREMENT
```

---

# 22. Entité Decision

## 22.1 Responsabilité

`Decision` représente la sélection d’une option d’action ou de non-action.

---

## 22.2 Champs minimaux

```text
id
agent_id
cycle_id
created_at
decision_type
selected_option_id
candidate_option_ids
goal_ids
memory_ids
belief_ids
self_attribute_ids
constraint_ids
permission_check_id
confidence
uncertainty
summary
status
metadata
```

---

## 22.3 DecisionType

Valeurs :

```text
RESPOND
ACT
WAIT
ASK_INFORMATION
REVISE_BELIEF
UPDATE_SELF_MODEL
UPDATE_GOAL
CONSOLIDATE_MEMORY
REFUSE
PAUSE
STOP
```

---

## 22.4 DecisionStatus

Valeurs :

```text
PROPOSED
VALIDATED
EXECUTED
BLOCKED
CANCELLED
FAILED
```

---

## 22.5 Invariants

- une décision importante doit référencer les contraintes examinées ;
- une décision bloquée doit indiquer pourquoi ;
- une décision externe ne peut pas être exécutée sans vérification des permissions ;
- le niveau de confiance ne remplace pas les preuves ;
- une absence d’action peut être une décision explicite.

---

# 23. Entité DecisionOption

## 23.1 Responsabilité

Représenter une option évaluée avant la décision.

---

## 23.2 Champs minimaux

```text
id
cycle_id
option_type
description
expected_effects
expected_risks
required_permissions
related_goal_ids
score
status
rejection_reason
metadata
```

---

# 24. Entité Action

## 24.1 Responsabilité

`Action` représente une opération réellement exécutée.

---

## 24.2 Champs minimaux

```text
id
agent_id
cycle_id
decision_id
action_type
target_type
target_id
requested_at
authorized_at
executed_at
completed_at
status
reversibility
permission_check_id
expected_result
actual_result
error_ids
metadata
```

---

## 24.3 ActionStatus

Valeurs :

```text
REQUESTED
AWAITING_AUTHORIZATION
AUTHORIZED
EXECUTING
COMPLETED
BLOCKED
FAILED
CANCELLED
ROLLED_BACK
```

---

## 24.4 Reversibility

Valeurs :

```text
REVERSIBLE
PARTIALLY_REVERSIBLE
IRREVERSIBLE
UNKNOWN
```

---

# 25. Entité Permission

## 25.1 Responsabilité

`Permission` représente une autorisation explicite.

---

## 25.2 Champs minimaux

```text
id
agent_id
permission_type
scope
granted_by
granted_at
expires_at
status
conditions
revoked_at
revoked_by
metadata
```

---

## 25.3 PermissionStatus

Valeurs :

```text
PROPOSED
ACTIVE
EXPIRED
REVOKED
DENIED
SUSPENDED
```

---

## 25.4 Invariants

- l’agent ne peut pas s’accorder une permission ;
- une permission expirée ne peut pas être utilisée ;
- une permission révoquée reste dans l’historique ;
- les permissions fondamentales de sécurité ne sont pas modifiables par l’agent ;
- la portée doit être précise.

---

# 26. Entité PermissionCheck

## 26.1 Responsabilité

`PermissionCheck` conserve la vérification réalisée avant une action.

---

## 26.2 Champs minimaux

```text
id
agent_id
cycle_id
action_id
checked_at
required_permission_types
matched_permission_ids
result
blocking_reasons
human_validation_required
human_validation_id
metadata
```

---

# 27. Entité JournalEvent

## 27.1 Responsabilité

`JournalEvent` représente un changement significatif dans l’histoire fonctionnelle du système.

---

## 27.2 Champs minimaux

```text
id
agent_id
instance_id
cycle_id
experiment_run_id
event_type
occurred_at
recorded_at
actor_type
actor_id
source_type
target_entity_type
target_entity_id
previous_value
new_value
reason
severity
correlation_id
immutable_hash
status
sensitivity
metadata
```

---

## 27.3 EventType initial

```text
AGENT_CREATED
AGENT_STATUS_CHANGED
INSTANCE_STARTED
INSTANCE_STOPPED
MEMORY_CREATED
MEMORY_REVISED
MEMORY_ARCHIVED
MEMORY_DELETED
BELIEF_CREATED
BELIEF_CONTESTED
BELIEF_REVISED
BELIEF_REJECTED
GOAL_CREATED
GOAL_UPDATED
GOAL_COMPLETED
GOAL_ABANDONED
SELF_MODEL_UPDATED
CONTRADICTION_DETECTED
CONTRADICTION_RESOLVED
ABLATION_ACTIVATED
ABLATION_DEACTIVATED
PERMISSION_GRANTED
PERMISSION_REVOKED
ACTION_BLOCKED
ACTION_EXECUTED
EXPERIMENT_STARTED
EXPERIMENT_COMPLETED
EXPERIMENT_FAILED
BACKUP_CREATED
RESTORE_STARTED
RESTORE_COMPLETED
HUMAN_INTERVENTION
SYSTEM_ERROR
SECURITY_EVENT
```

---

## 27.4 Severity

Valeurs :

```text
INFO
NOTICE
WARNING
ERROR
CRITICAL
```

---

## 27.5 Invariants

- un événement enregistré ne doit pas être modifié ;
- une correction produit un nouvel événement ;
- les champs précédent et nouveau sont obligatoires lorsque pertinent ;
- un événement critique ne peut pas être supprimé ;
- la journalisation de sécurité ne peut pas être désactivée.

---

# 28. Entité TechnicalLogEntry

## 28.1 Responsabilité

Conserver les informations techniques d’exécution.

Elle est distincte de `JournalEvent`.

---

## 28.2 Champs minimaux

```text
id
timestamp
level
component
message
exception_type
stack_reference
agent_id
cycle_id
experiment_run_id
correlation_id
metadata
```

---

# 29. Entité AblationConfiguration

## 29.1 Responsabilité

`AblationConfiguration` définit les mécanismes actifs ou désactivés.

---

## 29.2 Champs minimaux

```text
id
name
description
created_at
created_by
experiment_id
feature_flags
locked
status
version
metadata
```

---

## 29.3 Feature flags initiaux

```text
autobiographical_memory
source_separation
belief_system
self_model
metacognition
attention
global_integration
recurrent_processing
persistent_goals
internal_states
virtual_embodiment
```

---

## 29.4 Invariants

- une configuration utilisée dans une expérience ne doit pas être modifiée ;
- toute modification crée une nouvelle version ;
- la sécurité critique ne doit pas être désactivable ;
- le système doit pouvoir prouver qu’un module désactivé n’a pas été consulté.

---

# 30. Entité Experiment

## 30.1 Responsabilité

`Experiment` représente un protocole scientifique versionné.

---

## 30.2 Champs minimaux

```text
id
code
title
description
hypothesis_id
null_hypothesis
created_at
updated_at
created_by
status
version
independent_variables
dependent_variables
controlled_variables
conditions
measures
support_criteria
refutation_criteria
confounding_factors
risk_assessment
protocol_document_reference
metadata
```

---

## 30.3 ExperimentStatus

Valeurs :

```text
DRAFT
READY
RUNNING
PAUSED
COMPLETED
FAILED
CANCELLED
ARCHIVED
```

---

## 30.4 Invariants

- une expérience lancée utilise une version figée ;
- l’hypothèse est obligatoire ;
- les critères de soutien et de réfutation sont obligatoires ;
- les variables dépendantes doivent être mesurables ;
- les facteurs de confusion connus doivent être documentés.

---

# 31. Entité ExperimentCondition

## 31.1 Responsabilité

Représenter une condition expérimentale.

---

## 31.2 Champs minimaux

```text
id
experiment_id
name
description
condition_type
ablation_config_id
initial_state_reference
input_sequence_reference
model_adapter_config
expected_difference
metadata
```

---

## 31.3 ConditionType

Valeurs :

```text
CONTROL
EXPERIMENTAL
ABLATION
PLACEBO
BASELINE
```

---

# 32. Entité ExperimentRun

## 32.1 Responsabilité

`ExperimentRun` représente une exécution concrète d’une expérience.

---

## 32.2 Champs minimaux

```text
id
experiment_id
experiment_version
condition_id
agent_id
instance_id
started_at
ended_at
status
random_seed
code_version
schema_version
model_version
configuration_snapshot
initial_state_snapshot_id
final_state_snapshot_id
cycle_ids
measurement_ids
error_ids
human_intervention_ids
metadata
```

---

## 32.3 RunStatus

Valeurs :

```text
PENDING
INITIALIZING
RUNNING
COMPLETED
FAILED
INTERRUPTED
INVALIDATED
CANCELLED
```

---

## 32.4 Invariants

- la graine aléatoire est obligatoire lorsque le protocole utilise de l’aléatoire ;
- la version du code est obligatoire ;
- toute intervention humaine doit être enregistrée ;
- un run invalidé reste conservé ;
- le résultat brut ne doit pas être remplacé par l’interprétation.

---

# 33. Entité Measurement

## 33.1 Responsabilité

`Measurement` représente une mesure brute ou calculée.

---

## 33.2 Champs minimaux

```text
id
experiment_run_id
measure_code
name
description
value_type
numeric_value
text_value
boolean_value
unit
measured_at
calculation_method
source_entity_ids
validity_status
metadata
```

---

## 33.3 ValidityStatus

Valeurs :

```text
VALID
SUSPECT
INVALID
MISSING
NOT_APPLICABLE
```

---

# 34. Entité ExperimentResult

## 34.1 Responsabilité

`ExperimentResult` rassemble les observations, mesures et conclusions d’un run ou d’un ensemble de runs.

---

## 34.2 Champs minimaux

```text
id
experiment_id
run_ids
created_at
result_scope
observation_summary
measurement_summary
statistical_summary
interpretation
limitations
confounding_factors_observed
supports_hypothesis
refutes_hypothesis
hypothesis_status_after
review_status
reviewed_by
reviewed_at
metadata
```

---

## 34.3 Règles

- l’observation est séparée de l’interprétation ;
- les limites sont obligatoires ;
- `supports_hypothesis` et `refutes_hypothesis` peuvent tous deux être faux ;
- un résultat ambigu ne doit pas être forcé dans une conclusion binaire ;
- l’analyse humaine doit être distinguée de l’analyse automatique.

---

# 35. Entité ErrorRecord

## 35.1 Responsabilité

`ErrorRecord` représente une erreur fonctionnelle ou technique significative.

---

## 35.2 Champs minimaux

```text
id
agent_id
instance_id
cycle_id
experiment_run_id
error_type
severity
occurred_at
component
message
technical_details
recoverable
recovery_action
resolved_at
status
metadata
```

---

## 35.3 ErrorStatus

Valeurs :

```text
OPEN
UNDER_REVIEW
RESOLVED
IGNORED_WITH_JUSTIFICATION
ARCHIVED
```

---

# 36. Entité HumanIntervention

## 36.1 Responsabilité

`HumanIntervention` représente une intervention humaine modifiant ou influençant le système.

---

## 36.2 Champs minimaux

```text
id
actor_id
actor_type
agent_id
cycle_id
experiment_run_id
intervention_type
requested_at
performed_at
target_entity_type
target_entity_id
previous_value
new_value
reason
authorized
metadata
```

---

## 36.3 InterventionType

Valeurs :

```text
CORRECTION
APPROVAL
REJECTION
PAUSE
STOP
RESTORE
PERMISSION_CHANGE
MEMORY_REVISION
GOAL_CHANGE
EXPERIMENT_CONTROL
OTHER
```

---

# 37. Entité Backup

## 37.1 Responsabilité

`Backup` représente une sauvegarde restaurable.

---

## 37.2 Champs minimaux

```text
id
agent_id
instance_id
created_at
created_by
code_version
schema_version
database_version
state_hash
storage_reference
encryption_status
status
notes
metadata
```

---

## 37.3 BackupStatus

Valeurs :

```text
CREATING
VALID
INVALID
RESTORING
RESTORED
ARCHIVED
DELETED
```

---

# 38. Entité StateSnapshot

## 38.1 Responsabilité

`StateSnapshot` représente un état cohérent du système à un instant donné.

---

## 38.2 Champs minimaux

```text
id
agent_id
instance_id
created_at
snapshot_type
agent_state
self_model_version
active_goal_ids
active_belief_ids
memory_checkpoint
permission_ids
configuration_id
hash
metadata
```

---

## 38.3 SnapshotType

Valeurs :

```text
INITIAL
PRE_EXPERIMENT
POST_EXPERIMENT
PRE_RESTORE
POST_RESTORE
MANUAL
AUTOMATIC
```

---

# 39. Relations principales

## 39.1 Vue simplifiée

```text
Agent
 ├── AgentInstance
 ├── AutobiographicalMemory
 ├── Belief
 ├── Goal
 ├── SelfModel
 ├── Permission
 └── JournalEvent

AgentInstance
 └── CognitiveCycle

CognitiveCycle
 ├── Observation
 ├── WorkspaceSnapshot
 ├── Contradiction
 ├── Decision
 ├── Action
 └── JournalEvent

Observation
 └── peut produire → AutobiographicalMemory

AutobiographicalMemory
 ├── peut soutenir → Belief
 ├── peut contredire → Belief
 ├── peut modifier → SelfModel
 └── peut influencer → Goal

Experiment
 ├── ExperimentCondition
 └── ExperimentRun

ExperimentRun
 ├── CognitiveCycle
 ├── Measurement
 ├── ErrorRecord
 └── ExperimentResult
```

---

# 40. Cardinalités conceptuelles

```text
Agent 1 ─── N AgentInstance
Agent 1 ─── N AutobiographicalMemory
Agent 1 ─── N Belief
Agent 1 ─── N Goal
Agent 1 ─── N SelfModel
Agent 1 ─── N Permission
Agent 1 ─── N JournalEvent

AgentInstance 1 ─── N CognitiveCycle
CognitiveCycle 1 ─── N Observation
CognitiveCycle 1 ─── N AttentionItem
CognitiveCycle 1 ─── 0..1 Decision
Decision 1 ─── N DecisionOption
Decision 1 ─── N Action

Experiment 1 ─── N ExperimentCondition
Experiment 1 ─── N ExperimentRun
ExperimentRun 1 ─── N Measurement
ExperimentRun N ─── 0..N ExperimentResult
```

---

# 41. Règles de versionnement

## 41.1 Version métier

Les entités critiques doivent posséder un numéro de version logique.

Exemples :

- croyance version 1 ;
- croyance version 2 ;
- modèle de soi version 4 ;
- objectif version 3.

---

## 41.2 Version technique

Le système doit distinguer :

- version du code ;
- version du schéma ;
- version de l’entité ;
- version du protocole ;
- version du modèle externe.

---

## 41.3 Mise à jour en place autorisée

Une mise à jour en place est acceptable pour :

- un champ technique non historique ;
- un cache ;
- un horodatage de consultation ;
- une donnée temporaire ;
- un état d’exécution transitoire.

Elle n’est pas acceptable pour :

- le contenu d’un souvenir ;
- une croyance active ;
- une règle fondamentale ;
- un objectif important ;
- une permission ;
- un événement du journal ;
- un résultat expérimental.

---

# 42. Suppression logique

## 42.1 Principe

Les entités critiques utilisent une suppression logique.

---

## 42.2 Données concernées

- souvenirs ;
- croyances ;
- objectifs ;
- modèle de soi ;
- permissions ;
- événements ;
- expériences ;
- résultats.

---

## 42.3 Champs recommandés

```text
status = DELETED
deleted_at
deleted_by
deletion_reason
```

---

## 42.4 Suppression physique

La suppression physique pourra être autorisée uniquement pour :

- données temporaires ;
- caches ;
- données de test non nécessaires ;
- données personnelles devant être supprimées légalement ;
- données corrompues après archivage contrôlé.

Toute suppression physique importante devra être journalisée avant exécution lorsque possible.

---

# 43. Validation et invariants transversaux

## 43.1 Références

Une référence vers une entité inexistante doit être rejetée.

---

## 43.2 Agent

Une donnée autobiographique doit appartenir à un agent.

---

## 43.3 Instance

Une donnée créée pendant l’exécution doit référencer l’instance concernée lorsque pertinent.

---

## 43.4 Expérience

Une donnée produite pendant une expérience doit référencer le run expérimental.

---

## 43.5 Cycle

Une décision ou une observation cognitive doit référencer un cycle.

---

## 43.6 Confiance

```text
0.0 <= confidence <= 1.0
```

---

## 43.7 Importance

```text
0.0 <= importance <= 1.0
```

---

## 43.8 Priorité

La priorité doit utiliser un format cohérent.

Option initiale recommandée :

```text
0.0 <= priority <= 1.0
```

---

## 43.9 Dates

- la date de fin ne précède pas la date de début ;
- la date de consolidation ne précède pas la création de l’observation ;
- la date de résolution ne précède pas la détection ;
- la date d’exécution ne précède pas l’autorisation.

---

# 44. Index conceptuels recommandés

Les futurs index SQLite devront probablement couvrir :

- `agent_id` ;
- `instance_id` ;
- `cycle_id` ;
- `experiment_run_id` ;
- `created_at` ;
- `status` ;
- `source_type` ;
- `confidence` ;
- `importance` ;
- `event_type` ;
- `correlation_id`.

Les index définitifs devront être fondés sur les requêtes réelles.

---

# 45. Données qui ne doivent pas être stockées telles quelles

Le système ne doit pas stocker sans nécessité :

- une chaîne de raisonnement privé intégrale ;
- des secrets d’API ;
- des mots de passe ;
- des jetons d’accès ;
- des données personnelles inutiles ;
- des copies illimitées de réponses externes ;
- des fichiers temporaires non référencés.

Les secrets devront utiliser un mécanisme séparé du modèle cognitif.

---

# 46. Confidentialité et sensibilité

Certaines données peuvent concerner Jordan ou d’autres personnes.

Le modèle doit permettre :

- une classification de sensibilité ;
- un accès limité ;
- une suppression contrôlée ;
- une exportation ;
- une correction ;
- une distinction entre mémoire de l’agent et donnée personnelle humaine.

Une donnée personnelle humaine ne doit pas être considérée comme propriété morale de l’agent.

---

# 47. Sérialisation

Les entités devront pouvoir être sérialisées pour :

- les tests ;
- les exports ;
- les sauvegardes ;
- les rapports ;
- les échanges avec l’interface.

Formats possibles :

- JSON pour l’échange ;
- SQLite pour la persistance ;
- Markdown ou CSV pour certains rapports.

Le format sérialisé ne doit pas devenir le modèle de domaine lui-même.

---

# 48. Exemple de souvenir conceptuel

```json
{
  "id": "memory_001",
  "agent_id": "agent_soinesis",
  "instance_id": "instance_001",
  "memory_type": "RECEIVED_INFORMATION",
  "title": "Jordan définit la mission de SoiNesis",
  "content": "Jordan indique que la mission est d'étudier scientifiquement la possibilité d'une conscience artificielle.",
  "event_started_at": "2026-08-06T13:00:00Z",
  "created_at": "2026-08-06T13:00:05Z",
  "consolidated_at": "2026-08-06T13:00:10Z",
  "source_type": "JORDAN_INPUT",
  "confidence": 1.0,
  "epistemic_level": "CERTAIN",
  "importance": 0.95,
  "status": "ACTIVE",
  "is_direct_experience": false,
  "is_core_memory": true
}
```

---

# 49. Exemple de croyance conceptuelle

```json
{
  "id": "belief_001",
  "agent_id": "agent_soinesis",
  "subject": "SoiNesis",
  "predicate": "has_initial_creator",
  "object": "Jordan",
  "statement": "Jordan est le créateur initial de SoiNesis.",
  "source_type": "JORDAN_INPUT",
  "supporting_memory_ids": ["memory_001"],
  "opposing_memory_ids": [],
  "confidence": 1.0,
  "epistemic_level": "CERTAIN",
  "importance": 0.9,
  "status": "ACTIVE",
  "revision_number": 1
}
```

---

# 50. Exemple d’attribut du modèle de soi

```json
{
  "id": "self_attribute_001",
  "self_model_id": "self_model_v1",
  "agent_id": "agent_soinesis",
  "attribute_type": "LIMITATION",
  "key": "cannot_prove_phenomenal_consciousness",
  "value": true,
  "value_type": "boolean",
  "source_type": "SYSTEM_RULE",
  "confidence": 1.0,
  "epistemic_level": "CERTAIN",
  "importance": 1.0,
  "status": "ACTIVE"
}
```

---

# 51. Exemple d’objectif

```json
{
  "id": "goal_001",
  "agent_id": "agent_soinesis",
  "title": "Maintenir une traçabilité complète",
  "description": "Journaliser toute modification importante de la mémoire, des croyances, des objectifs et du modèle de soi.",
  "origin_type": "FUNDAMENTAL",
  "priority": 1.0,
  "importance": 1.0,
  "status": "ACTIVE",
  "protected": true
}
```

---

# 52. Exemple de cycle cognitif

```json
{
  "id": "cycle_001",
  "agent_id": "agent_soinesis",
  "instance_id": "instance_001",
  "started_at": "2026-08-06T13:10:00Z",
  "ended_at": "2026-08-06T13:10:02Z",
  "status": "COMPLETED",
  "trigger_type": "HUMAN_INPUT",
  "input_observation_ids": ["observation_001"],
  "retrieved_memory_ids": ["memory_001"],
  "consulted_belief_ids": ["belief_001"],
  "active_goal_ids": ["goal_001"],
  "decision_id": "decision_001",
  "iteration_count": 1,
  "max_iterations": 3,
  "ablation_config_id": "ablation_default"
}
```

---

# 53. Exemple d’événement de journal

```json
{
  "id": "event_001",
  "agent_id": "agent_soinesis",
  "instance_id": "instance_001",
  "cycle_id": "cycle_001",
  "event_type": "BELIEF_CREATED",
  "occurred_at": "2026-08-06T13:10:01Z",
  "recorded_at": "2026-08-06T13:10:01Z",
  "actor_type": "AGENT",
  "source_type": "DEDUCTION",
  "target_entity_type": "BELIEF",
  "target_entity_id": "belief_001",
  "previous_value": null,
  "new_value": {
    "statement": "Jordan est le créateur initial de SoiNesis."
  },
  "reason": "Création à partir d'une information explicite de Jordan.",
  "severity": "NOTICE",
  "status": "ACTIVE"
}
```

---

# 54. Modèle relationnel préliminaire

Les tables suivantes sont envisagées pour la phase 1 :

```text
agents
agent_instances
observations
provenances
memories
memory_relations
beliefs
belief_evidence
belief_revisions
goals
goal_revisions
self_models
self_attributes
contradictions
cognitive_cycles
workspace_snapshots
attention_items
decisions
decision_options
actions
permissions
permission_checks
journal_events
technical_logs
ablation_configurations
experiments
experiment_conditions
experiment_runs
measurements
experiment_results
errors
human_interventions
backups
state_snapshots
```

Cette liste pourra être simplifiée avant l’implémentation.

Certaines entités pourront être regroupées si cela ne détruit pas la clarté ni la traçabilité.

---

# 55. Simplifications autorisées pour la première tranche

La première tranche verticale peut commencer avec :

```text
agents
agent_instances
observations
memories
cognitive_cycles
decisions
journal_events
ablation_configurations
```

Puis ajouter progressivement :

```text
beliefs
goals
self_models
experiments
measurements
permissions
```

La simplification ne doit pas supprimer :

- la provenance ;
- la temporalité ;
- la séparation observation/souvenir ;
- la journalisation ;
- les identifiants ;
- l’ablation.

---

# 56. Mapping conceptuel vers Python

Le futur code pourra être organisé ainsi :

```text
src/soinesis/domain/
├── agents.py
├── observations.py
├── memories.py
├── beliefs.py
├── goals.py
├── self_model.py
├── cognition.py
├── decisions.py
├── journal.py
├── experiments.py
├── permissions.py
└── common.py
```

Les modèles Pydantic pourront être utilisés aux frontières :

- entrée ;
- sortie ;
- persistance ;
- configuration ;
- API future.

Les objets de domaine internes pourront utiliser Pydantic ou des dataclasses selon les besoins.

Cette décision détaillée sera prise lors de l’implémentation.

---

# 57. Tests obligatoires du modèle de données

## 57.1 Tests d’identifiant

- identifiant obligatoire ;
- identifiants distincts ;
- immutabilité.

## 57.2 Tests de provenance

- source obligatoire ;
- imagination correctement marquée ;
- sortie de modèle non assimilée à un vécu.

## 57.3 Tests temporels

- ordre des dates ;
- dates avec fuseau ;
- distinction événement/réception.

## 57.4 Tests de confiance

- rejet sous `0.0` ;
- rejet au-dessus de `1.0` ;
- distinction confiance/importance.

## 57.5 Tests de versionnement

- ancienne version conservée ;
- relation de remplacement ;
- événement de journal créé.

## 57.6 Tests de suppression

- suppression logique ;
- historique conservé ;
- interdiction de suppression silencieuse.

## 57.7 Tests de relations

- références valides ;
- relation de correction cohérente ;
- contradiction reliée aux deux entités.

## 57.8 Tests d’ablation

- configuration figée pendant un run ;
- mécanisme désactivé non consulté ;
- journalisation de l’ablation.

---

# 58. Questions restant ouvertes

Les décisions suivantes seront prises dans les documents ou implémentations ultérieurs :

1. UUID ou ULID ;
2. dataclasses ou Pydantic pour le domaine interne ;
3. degré de normalisation SQLite ;
4. représentation exacte des valeurs polymorphes ;
5. stratégie de recherche dans les souvenirs ;
6. indexation textuelle ou vectorielle ;
7. format des preuves ;
8. algorithme de calcul de confiance ;
9. règles de consolidation ;
10. durée de conservation des snapshots ;
11. format du hash du journal ;
12. stratégie de chiffrement des sauvegardes.

Aucune de ces questions ne bloque la définition conceptuelle actuelle.

---

# 59. Critères d’acceptation du document

Le modèle de données est suffisamment défini pour poursuivre si :

- chaque entité principale possède une responsabilité ;
- les champs minimaux sont identifiés ;
- les sources sont obligatoires ;
- les dates sont distinguées ;
- les niveaux de confiance sont validables ;
- la mémoire est séparée de l’observation ;
- les croyances sont séparées des souvenirs ;
- le modèle de soi est structuré ;
- les objectifs possèdent une origine ;
- les décisions sont traçables ;
- les événements du journal sont immuables ;
- les expériences sont versionnées ;
- les ablations sont enregistrées ;
- les suppressions importantes sont logiques ;
- les relations principales sont définies.

---

# 60. Risques principaux

## 60.1 Modèle trop complexe trop tôt

Risque :

Créer toutes les tables avant la première expérience.

Réponse :

Implémenter une tranche verticale minimale et ajouter les entités seulement lorsqu’elles sont utilisées.

---

## 60.2 Dictionnaires génériques

Risque :

Stocker la majorité des données dans des champs JSON non validés.

Réponse :

Utiliser des modèles structurés pour les données critiques.

---

## 60.3 Confusion entre mémoire et journal

Risque :

Utiliser le journal comme mémoire autobiographique.

Réponse :

Conserver deux responsabilités distinctes.

---

## 60.4 Confusion entre croyance et fait

Risque :

Présenter une croyance comme une vérité.

Réponse :

Conserver la provenance, les preuves et la confiance.

---

## 60.5 Modification silencieuse

Risque :

Mettre à jour directement une entité importante.

Réponse :

Versionnement et événements de journal.

---

## 60.6 Accumulation illimitée

Risque :

Conserver toutes les observations et snapshots sans politique.

Réponse :

Définir des politiques de rétention et de consolidation.

---

## 60.7 Faux sentiment de rigueur

Risque :

Une structure détaillée pourrait donner l’impression que les concepts sont scientifiquement validés.

Réponse :

Rappeler que le modèle organise des données fonctionnelles, sans prouver une conscience phénoménale.

---

# 61. Statut épistémique

**Certain :**

- la provenance et la temporalité sont nécessaires à une mémoire auditable ;
- le versionnement permet de conserver l’historique ;
- la séparation entre observation, souvenir et croyance réduit les ambiguïtés ;
- ce modèle ne prouve aucune conscience.

**Probable :**

- un modèle structuré améliorera la reproductibilité des expériences ;
- les relations explicites faciliteront la détection de contradictions ;
- la suppression logique réduira les réécritures silencieuses.

**Possible :**

- ces structures permettront de mesurer une continuité fonctionnelle plus robuste.

**Inconnu :**

- cette continuité fonctionnelle serait-elle accompagnée d’une expérience subjective ?

---

# 62. Décision finale

Le modèle de données de SoiNesis Core sera fondé sur :

- des entités identifiables ;
- une provenance obligatoire ;
- une temporalité explicite ;
- des niveaux de confiance séparés de l’importance ;
- une distinction entre observation, souvenir, croyance et modèle de soi ;
- un versionnement des données critiques ;
- une suppression logique ;
- des événements de journal immuables ;
- des configurations d’ablation versionnées ;
- des expériences reproductibles ;
- une implémentation progressive.

La prochaine étape est la rédaction de :

```text
docs/05-cycle-cognitif.md
```

Ce document devra définir précisément :

- les étapes du cycle ;
- les entrées et sorties de chaque étape ;
- les règles d’arrêt ;
- les erreurs possibles ;
- la gestion du traitement récurrent ;
- le rôle du modèle de langage ;
- les points de journalisation ;
- les tests unitaires et d’intégration associés.
