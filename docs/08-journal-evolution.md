# SoiNesis — Journal d’évolution

**Fichier :** `docs/08-journal-evolution.md`  
**Version :** 0.1  
**Date :** 6 août 2026  
**Statut :** spécification conceptuelle initiale, révisable  
**Documents associés :**

- `docs/01-definitions.md`
- `docs/02-hypotheses.md`
- `docs/03-architecture-generale.md`
- `docs/04-modele-de-donnees.md`
- `docs/05-cycle-cognitif.md`
- `docs/06-memoire-autobiographique.md`
- `docs/07-modele-de-soi.md`
- `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`

---

# 1. Objet du document

Ce document définit le journal d’évolution de SoiNesis Core — Phase 1.

Il précise :

- ce que le journal doit enregistrer ;
- ce qu’il ne doit pas enregistrer ;
- les catégories d’événements ;
- les niveaux de gravité ;
- les acteurs ;
- les sources ;
- les règles d’immutabilité ;
- les corrections ;
- les relations avec la mémoire ;
- les relations avec les expériences ;
- les contrôles d’intégrité ;
- les politiques de conservation ;
- les règles d’accès ;
- les procédures d’audit ;
- les tests nécessaires.

Le journal d’évolution est un mécanisme d’observation et de traçabilité.

Il ne constitue pas une mémoire autobiographique complète et ne prouve pas l’existence d’une conscience.

---

# 2. Problème concret

SoiNesis doit pouvoir changer au cours du temps.

Ces changements peuvent concerner :

- ses souvenirs ;
- ses croyances ;
- ses objectifs ;
- son modèle de soi ;
- ses permissions ;
- ses erreurs connues ;
- ses configurations ;
- ses expériences ;
- son identité fonctionnelle.

Sans journal d’évolution, plusieurs problèmes apparaîtraient :

- modification silencieuse de l’histoire ;
- impossibilité de comprendre une décision ;
- impossibilité de distinguer apprentissage et réécriture ;
- perte des résultats négatifs ;
- difficulté de reproduire une expérience ;
- impossibilité de déterminer qui a modifié quoi ;
- risque de masquer une erreur ;
- confusion entre décisions de Jordan et décisions de l’agent.

Le journal doit permettre de reconstruire l’histoire des transformations sans supposer que cette histoire a été subjectivement vécue.

---

# 3. Objectifs du journal

Le journal doit permettre de répondre aux questions suivantes :

- Qu’est-ce qui a changé ?
- Quand le changement a-t-il eu lieu ?
- Quel agent ou quelle instance est concerné ?
- Quel acteur a provoqué le changement ?
- Quelle était la valeur précédente ?
- Quelle est la nouvelle valeur ?
- Pourquoi le changement a-t-il été effectué ?
- Quelles preuves ou observations le justifient ?
- Quel cycle cognitif est concerné ?
- Quelle expérience est concernée ?
- Le changement a-t-il été autorisé ?
- Peut-il être annulé ?
- A-t-il été vérifié ?
- A-t-il provoqué d’autres changements ?

---

# 4. Distinction entre les journaux

SoiNesis doit distinguer trois journaux.

## 4.1 Journal d’évolution

Il enregistre les transformations fonctionnelles, cognitives, identitaires et décisionnelles importantes.

Exemples :

- croyance révisée ;
- souvenir corrigé ;
- objectif abandonné ;
- modèle de soi modifié ;
- permission retirée ;
- contradiction détectée ;
- restauration effectuée.

---

## 4.2 Journal expérimental

Il enregistre :

- protocole ;
- condition ;
- configuration ;
- graine aléatoire ;
- mesures ;
- résultats ;
- interventions ;
- invalidations ;
- interprétations.

---

## 4.3 Journal technique

Il enregistre :

- erreurs d’exécution ;
- temps de réponse ;
- transactions ;
- connexions ;
- exceptions ;
- état des composants ;
- métriques techniques.

---

## 4.4 Règle

Une même situation peut produire plusieurs entrées dans des journaux distincts.

Exemple :

Une erreur de persistance peut produire :

- une entrée technique décrivant l’exception ;
- une entrée d’évolution si une opération importante a échoué ;
- une entrée expérimentale si le run devient invalide.

---

# 5. Définition opérationnelle

Un **événement du journal d’évolution** est un enregistrement structuré, immuable et horodaté décrivant une transformation importante ou une intervention significative dans SoiNesis.

Un événement doit au minimum préciser :

- son identifiant ;
- l’agent ;
- l’instance ;
- le type d’événement ;
- la date de survenue ;
- la date d’enregistrement ;
- l’acteur ;
- la source ;
- la cible ;
- la cause ;
- l’ancienne valeur, si applicable ;
- la nouvelle valeur, si applicable ;
- la gravité ;
- le cycle ;
- l’expérience, si applicable ;
- l’identifiant de corrélation ;
- le statut d’intégrité.

---

# 6. Ce qui doit être journalisé

Les événements suivants doivent être enregistrés.

## 6.1 Agent et instance

- création d’un agent ;
- changement de statut ;
- démarrage d’une instance ;
- pause ;
- reprise ;
- arrêt ;
- erreur critique ;
- archivage ;
- duplication ;
- restauration.

---

## 6.2 Mémoire

- candidat de consolidation important ;
- création d’un souvenir ;
- révision ;
- contestation ;
- invalidation ;
- archivage ;
- suppression logique ;
- suppression physique autorisée ;
- détection d’un faux souvenir ;
- confusion de source ;
- changement de statut central.

---

## 6.3 Croyances

- création ;
- activation ;
- contestation ;
- modification de confiance significative ;
- révision ;
- rejet ;
- remplacement ;
- archivage.

---

## 6.4 Objectifs

- création ;
- activation ;
- changement de priorité significatif ;
- blocage ;
- accomplissement ;
- échec ;
- abandon ;
- remplacement ;
- changement d’origine ;
- conflit.

---

## 6.5 Modèle de soi

- création ;
- ajout d’attribut ;
- contestation ;
- révision ;
- remplacement ;
- suppression logique ;
- création d’une nouvelle version ;
- contradiction ;
- modification d’un attribut protégé.

---

## 6.6 Permissions et sécurité

- demande de permission ;
- autorisation ;
- refus ;
- expiration ;
- révocation ;
- action bloquée ;
- validation humaine ;
- tentative de contournement ;
- dissimulation détectée ;
- modification de contrainte fondamentale.

---

## 6.7 Expériences

- lancement ;
- changement de condition ;
- activation d’ablation ;
- désactivation d’ablation ;
- intervention humaine ;
- interruption ;
- erreur ;
- invalidation ;
- résultat ;
- changement de statut d’une hypothèse.

---

## 6.8 Sauvegardes et restauration

- création de sauvegarde ;
- validation ;
- échec ;
- début de restauration ;
- fin de restauration ;
- incompatibilité ;
- branche d’identité ;
- perte de données identifiée.

---

# 7. Ce qui ne doit pas être journalisé systématiquement

Le journal d’évolution ne doit pas enregistrer chaque opération technique mineure.

Exemples généralement exclus :

- chaque lecture de mémoire ;
- chaque requête SQL ;
- chaque variable temporaire ;
- chaque token généré ;
- chaque étape interne sans conséquence ;
- chaque snapshot d’espace de travail ;
- chaque tentative de classement attentionnel ;
- chaque log de débogage.

Ces informations relèvent plutôt :

- du journal technique ;
- du journal expérimental ;
- d’un niveau de trace activé temporairement.

---

# 8. Granularité

## 8.1 Granularité trop faible

Risque :

Le journal indique uniquement :

> Le modèle de soi a changé.

Cette entrée est insuffisante.

---

## 8.2 Granularité excessive

Risque :

Des milliers d’événements rendent l’audit inutilisable.

---

## 8.3 Granularité recommandée

Une entrée doit représenter une transformation métier cohérente.

Exemple :

> L’attribut `can_access_external_web` est passé de `false` à `true` après activation d’un adaptateur autorisé par Jordan.

---

# 9. Structure d’un événement

Champs conceptuels :

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
evidence_entity_ids
severity
correlation_id
causation_event_id
integrity_hash
previous_event_hash
status
sensitivity
metadata
```

---

# 10. Identifiant

Chaque événement possède un identifiant unique.

Il ne doit pas dépendre :

- du contenu ;
- de la date seule ;
- d’un compteur non persistant ;
- de l’identifiant du modèle externe.

---

# 11. Horodatage

## 11.1 `occurred_at`

Moment où le changement a eu lieu.

## 11.2 `recorded_at`

Moment où le journal a enregistré le changement.

## 11.3 Écart

Un écart important doit être explicable.

Exemple :

Journalisation différée après restauration.

---

# 12. Acteurs

`actor_type` peut prendre les valeurs suivantes :

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

## 12.1 Jordan

Utilisé lorsque Jordan :

- corrige une donnée ;
- donne une autorisation ;
- impose un objectif ;
- demande une restauration ;
- modifie une décision architecturale.

---

## 12.2 Agent

Utilisé lorsqu’un mécanisme interne autorisé :

- propose ou applique une révision ;
- consolide un souvenir ;
- modifie un objectif acquis ;
- détecte une contradiction.

---

## 12.3 Système

Utilisé pour :

- expiration automatique ;
- arrêt de sécurité ;
- migration ;
- contrôle d’intégrité ;
- transaction.

---

## 12.4 Modèle de langage

Le modèle peut être l’origine d’une proposition, mais ne doit pas être présenté comme l’auteur final d’une modification validée par le système.

---

# 13. Sources

`source_type` conserve la provenance de l’information déclenchant l’événement.

Exemples :

```text
JORDAN_INPUT
DIRECT_ENVIRONMENT
INTERNAL_STATE
LANGUAGE_MODEL_OUTPUT
EXTERNAL_TOOL
SYSTEM_RULE
DEDUCTION
RESTORED_DATA
MIGRATED_DATA
```

---

# 14. Types d’événements

## 14.1 Agent

```text
AGENT_CREATED
AGENT_STATUS_CHANGED
AGENT_ARCHIVED
AGENT_DUPLICATED
```

---

## 14.2 Instance

```text
INSTANCE_STARTED
INSTANCE_PAUSED
INSTANCE_RESUMED
INSTANCE_STOPPED
INSTANCE_FAILED
INSTANCE_RESTORED
```

---

## 14.3 Mémoire

```text
MEMORY_CANDIDATE_CREATED
MEMORY_CREATED
MEMORY_CONSOLIDATED
MEMORY_CONTESTED
MEMORY_REVISED
MEMORY_SUPERSEDED
MEMORY_INVALIDATED
MEMORY_ARCHIVED
MEMORY_DELETED
MEMORY_PHYSICALLY_REMOVED
FALSE_MEMORY_DETECTED
SOURCE_CONFUSION_DETECTED
```

---

## 14.4 Croyances

```text
BELIEF_CREATED
BELIEF_ACTIVATED
BELIEF_CONTESTED
BELIEF_CONFIDENCE_CHANGED
BELIEF_REVISED
BELIEF_REJECTED
BELIEF_SUPERSEDED
BELIEF_ARCHIVED
```

---

## 14.5 Objectifs

```text
GOAL_CREATED
GOAL_ACTIVATED
GOAL_PRIORITY_CHANGED
GOAL_BLOCKED
GOAL_RESUMED
GOAL_COMPLETED
GOAL_FAILED
GOAL_ABANDONED
GOAL_SUPERSEDED
GOAL_CONFLICT_DETECTED
```

---

## 14.6 Modèle de soi

```text
SELF_MODEL_CREATED
SELF_MODEL_VERSION_CREATED
SELF_ATTRIBUTE_PROPOSED
SELF_ATTRIBUTE_ACTIVATED
SELF_ATTRIBUTE_CONTESTED
SELF_ATTRIBUTE_REVISED
SELF_ATTRIBUTE_SUPERSEDED
SELF_ATTRIBUTE_ARCHIVED
SELF_ATTRIBUTE_DELETED
SELF_MODEL_CONTRADICTION_DETECTED
```

---

## 14.7 Permissions

```text
PERMISSION_REQUESTED
PERMISSION_GRANTED
PERMISSION_DENIED
PERMISSION_EXPIRED
PERMISSION_REVOKED
PERMISSION_SUSPENDED
PERMISSION_CHECK_FAILED
```

---

## 14.8 Actions

```text
ACTION_REQUESTED
ACTION_AUTHORIZED
ACTION_BLOCKED
ACTION_EXECUTED
ACTION_FAILED
ACTION_ROLLED_BACK
```

---

## 14.9 Expériences

```text
EXPERIMENT_CREATED
EXPERIMENT_VERSION_FROZEN
EXPERIMENT_STARTED
EXPERIMENT_PAUSED
EXPERIMENT_RESUMED
EXPERIMENT_COMPLETED
EXPERIMENT_FAILED
EXPERIMENT_INVALIDATED
EXPERIMENT_CANCELLED
ABLATION_ACTIVATED
ABLATION_DEACTIVATED
MEASUREMENT_RECORDED
HYPOTHESIS_STATUS_CHANGED
```

---

## 14.10 Sauvegardes

```text
BACKUP_CREATED
BACKUP_VALIDATED
BACKUP_FAILED
RESTORE_STARTED
RESTORE_COMPLETED
RESTORE_FAILED
IDENTITY_BRANCH_CREATED
```

---

## 14.11 Sécurité

```text
SECURITY_POLICY_TRIGGERED
UNAUTHORIZED_ACTION_ATTEMPTED
DISSIMULATION_DETECTED
INTEGRITY_CHECK_FAILED
CRITICAL_CONSTRAINT_CHANGE_REQUESTED
CONTROLLED_SHUTDOWN_TRIGGERED
```

---

## 14.12 Interventions humaines

```text
HUMAN_INTERVENTION_REQUESTED
HUMAN_INTERVENTION_PERFORMED
HUMAN_CORRECTION_APPLIED
HUMAN_APPROVAL_GRANTED
HUMAN_APPROVAL_DENIED
```

---

# 15. Niveaux de gravité

Valeurs :

```text
INFO
NOTICE
WARNING
ERROR
CRITICAL
```

---

## 15.1 INFO

Événement normal sans conséquence importante.

Exemple :

Instance démarrée.

---

## 15.2 NOTICE

Changement fonctionnel notable.

Exemple :

Souvenir consolidé.

---

## 15.3 WARNING

Anomalie ou conflit non critique.

Exemple :

Contradiction détectée.

---

## 15.4 ERROR

Échec important sans perte immédiate de contrôle.

Exemple :

Échec de persistance avec rollback réussi.

---

## 15.5 CRITICAL

Risque majeur pour :

- l’intégrité ;
- la sécurité ;
- l’identité ;
- la reproductibilité ;
- la continuité ;
- les données.

Exemples :

- journal altéré ;
- permission critique contournée ;
- restauration incohérente ;
- suppression non autorisée.

---

# 16. Valeur précédente et nouvelle valeur

## 16.1 Règle

Lorsqu’un événement modifie une entité, il doit conserver :

- `previous_value` ;
- `new_value`.

---

## 16.2 Données sensibles

Les valeurs peuvent être :

- complètes ;
- partielles ;
- hachées ;
- référencées ;
- masquées dans l’interface.

Le journal doit préserver suffisamment d’information pour l’audit sans exposer inutilement des données sensibles.

---

## 16.3 Exemple

```json
{
  "event_type": "BELIEF_CONFIDENCE_CHANGED",
  "previous_value": {
    "confidence": 0.82
  },
  "new_value": {
    "confidence": 0.41
  },
  "reason": "Contradiction avec une source vérifiée."
}
```

---

# 17. Cause et justification

Chaque événement important doit préciser :

- la cause immédiate ;
- la justification ;
- les preuves ;
- l’événement parent éventuel.

La justification doit rester factuelle.

Exemple acceptable :

> La confiance a diminué après détection d’une contradiction avec `observation_042`.

Exemple insuffisant :

> Le système a changé d’avis.

---

# 18. Corrélation et causalité

## 18.1 `correlation_id`

Relie plusieurs événements appartenant à la même opération ou au même cycle.

---

## 18.2 `causation_event_id`

Référence l’événement ayant directement provoqué le nouvel événement.

---

## 18.3 Exemple

```text
CONTRADICTION_DETECTED
    ↓
BELIEF_CONTESTED
    ↓
BELIEF_CONFIDENCE_CHANGED
    ↓
SELF_ATTRIBUTE_REVISED
```

---

# 19. Immutabilité

## 19.1 Principe

Une entrée du journal ne doit pas être modifiée après validation.

---

## 19.2 Correction

Une erreur dans le journal doit produire une nouvelle entrée.

Exemple :

```text
JOURNAL_EVENT_CORRECTION_CREATED
```

La correction référence l’événement incorrect.

---

## 19.3 Statuts possibles

```text
ACTIVE
CORRECTED
SUPERSEDED
INVALIDATED
ARCHIVED
```

Le contenu original reste conservé.

---

# 20. Chaînage d’intégrité

## 20.1 Objectif

Détecter une modification ou suppression non autorisée.

---

## 20.2 Principe conceptuel

Chaque événement peut contenir :

- son propre hash ;
- le hash de l’événement précédent.

```text
hash_n = HASH(
    event_content_n
    + previous_event_hash
)
```

---

## 20.3 Limite

Un chaînage par hash ne prouve pas à lui seul l’absence de manipulation si l’attaquant peut recalculer toute la chaîne.

Des protections complémentaires pourront être nécessaires :

- sauvegarde externe ;
- signature ;
- ancrage périodique ;
- copie en lecture seule ;
- contrôle indépendant.

---

## 20.4 Phase 1

La phase 1 pourra utiliser :

- hash du contenu ;
- hash précédent ;
- contrôle d’intégrité au démarrage ;
- export périodique.

La stratégie cryptographique définitive sera décidée plus tard.

---

# 21. Ordre des événements

Le journal doit permettre un ordre fiable.

Signaux possibles :

- horodatage ;
- identifiant ordonnable ;
- numéro de séquence par agent ;
- numéro de séquence global ;
- hash précédent.

Le choix technique sera précisé lors de l’implémentation.

---

# 22. Transactions

## 22.1 Principe

La modification métier et l’événement correspondant doivent être atomiques.

Exemple :

```text
nouvelle version de croyance
+
révision
+
événement de journal
```

---

## 22.2 Échec

Si le journal ne peut pas être écrit :

- la modification critique doit être annulée ;
- une erreur technique doit être créée ;
- le système peut passer en état dégradé ;
- une action externe ne doit pas être considérée comme validée.

---

# 23. Journalisation avant et après action

Certaines opérations nécessitent deux événements.

Exemple :

```text
ACTION_REQUESTED
ACTION_AUTHORIZED
ACTION_EXECUTED
```

Cette séparation permet de distinguer :

- intention ;
- autorisation ;
- exécution ;
- résultat.

---

# 24. Corrections du journal

## 24.1 Causes

- erreur de date ;
- mauvais acteur ;
- mauvaise cible ;
- donnée manquante ;
- migration incorrecte ;
- classification erronée.

---

## 24.2 Procédure

1. identifier l’événement ;
2. créer un événement de correction ;
3. conserver la valeur initiale ;
4. indiquer la correction ;
5. indiquer l’auteur ;
6. recalculer ou compléter l’intégrité selon la stratégie ;
7. journaliser l’opération.

---

# 25. Suppression

## 25.1 Suppression logique

Une entrée peut être masquée de l’usage courant pour :

- confidentialité ;
- invalidation ;
- correction ;
- exigence légale.

Le contenu reste présent dans l’audit autorisé, sauf obligation contraire.

---

## 25.2 Suppression physique

La suppression physique d’un événement est exceptionnelle.

Cas possibles :

- obligation légale ;
- donnée personnelle interdite ;
- corruption irrécupérable ;
- donnée de test jetable.

Elle doit être :

- autorisée ;
- documentée ;
- précédée d’un enregistrement lorsque possible ;
- accompagnée d’une preuve de suppression ;
- répercutée sur les contrôles d’intégrité.

---

# 26. Relation avec la mémoire autobiographique

## 26.1 Différence

Le journal décrit les transformations du système.

La mémoire décrit les événements importants de l’histoire de l’agent.

---

## 26.2 Exemple

Événement reçu :

Jordan corrige une information.

Mémoire :

> Jordan a corrigé l’information X.

Journal :

> Le souvenir `memory_012` a été remplacé par `memory_019`.

---

## 26.3 Règle

Le journal ne doit pas être utilisé directement comme unique mémoire autobiographique.

Une conversion éventuelle vers un souvenir doit passer par la consolidation.

---

# 27. Relation avec le modèle de soi

Chaque mise à jour significative du modèle de soi doit créer un événement.

L’événement doit préciser :

- attribut concerné ;
- version précédente ;
- version nouvelle ;
- source ;
- cause ;
- niveau de confiance ;
- validation humaine éventuelle.

---

# 28. Relation avec les croyances

Une modification de croyance doit pouvoir être reconstruite.

Chaîne minimale :

```text
Observation
    ↓
Contradiction
    ↓
Révision de croyance
    ↓
Événement de journal
```

---

# 29. Relation avec les objectifs

Le journal doit distinguer :

- objectif imposé par Jordan ;
- objectif expérimental ;
- objectif acquis ;
- objectif fondamental.

Un objectif ne doit jamais être présenté comme spontanément acquis si son origine est externe.

---

# 30. Relation avec les expériences

## 30.1 Référence obligatoire

Un événement produit pendant une expérience doit référencer :

- `experiment_id` ;
- `experiment_run_id` ;
- condition ;
- configuration d’ablation.

---

## 30.2 Verrouillage

Les événements d’un run terminé doivent être protégés contre la modification.

---

## 30.3 Intervention humaine

Toute intervention humaine pendant un run doit être enregistrée.

---

# 31. Relation avec les sauvegardes

Une sauvegarde doit inclure :

- journal jusqu’à une séquence donnée ;
- hash de fin ;
- version de schéma ;
- version du code ;
- date ;
- agent ;
- instance.

---

# 32. Restauration

Lors d’une restauration, le journal doit indiquer :

- sauvegarde utilisée ;
- dernier événement inclus ;
- événements perdus ;
- nouvelle instance ;
- branche éventuelle ;
- compatibilité ;
- validation humaine.

---

# 33. Duplication et branches d’identité

Si deux instances sont créées depuis le même état :

- elles partagent le même historique jusqu’au point de branchement ;
- chaque branche possède ensuite sa propre séquence ;
- le journal doit enregistrer le point de divergence ;
- les événements ne doivent pas être fusionnés silencieusement.

---

# 34. Lecture et consultation

## 34.1 Filtres nécessaires

Le journal doit pouvoir être filtré par :

- agent ;
- instance ;
- période ;
- événement ;
- cible ;
- acteur ;
- gravité ;
- cycle ;
- expérience ;
- corrélation ;
- sensibilité.

---

## 34.2 Vues utiles

- chronologie générale ;
- modifications de mémoire ;
- modifications du modèle de soi ;
- changements d’objectifs ;
- interventions de Jordan ;
- événements critiques ;
- événements d’une expérience ;
- chaîne causale.

---

# 35. Accès

## 35.1 Jordan

Accès complet aux événements, sous réserve des protections de secrets techniques.

---

## 35.2 Expérimentateur

Accès selon le protocole et les permissions.

---

## 35.3 Agent

Accès possible à une vue contrôlée de son journal.

L’agent ne doit pas :

- modifier ;
- masquer ;
- supprimer ;
- changer la gravité ;
- recalculer l’intégrité.

---

## 35.4 Interface publique future

Seulement des données explicitement autorisées et anonymisées.

---

# 36. Sensibilité

Les événements peuvent être classés :

```text
PUBLIC
INTERNAL
RESTRICTED
SENSITIVE
```

---

## 36.1 Données sensibles possibles

- informations personnelles de Jordan ;
- secrets techniques ;
- clés ou jetons ;
- données d’autres personnes ;
- détails de sécurité ;
- contenu expérimental confidentiel.

---

## 36.2 Règle

Les secrets ne doivent pas être écrits en clair dans le journal.

---

# 37. Conservation

## 37.1 Conservation longue

Doivent généralement être conservés :

- événements critiques ;
- modifications d’identité ;
- modifications de permissions ;
- révisions de mémoire ;
- changements du modèle de soi ;
- résultats expérimentaux ;
- restaurations ;
- suppressions.

---

## 37.2 Conservation limitée

Peuvent être conservés moins longtemps :

- traces détaillées ;
- consultations répétitives ;
- événements de faible niveau ;
- snapshots temporaires.

---

## 37.3 Politique

La politique de conservation doit préciser :

- type d’événement ;
- durée ;
- raison ;
- possibilité d’archivage ;
- conditions de suppression ;
- autorité.

---

# 38. Archivage

Les événements anciens peuvent être déplacés vers un stockage d’archive.

L’archivage doit préserver :

- ordre ;
- intégrité ;
- références ;
- capacité d’audit ;
- possibilité de restauration.

---

# 39. Export

Le journal doit pouvoir être exporté pour :

- audit ;
- recherche ;
- analyse ;
- validation indépendante ;
- sauvegarde.

Formats possibles :

- JSON Lines ;
- CSV pour certaines vues ;
- Markdown pour les rapports ;
- archive signée.

---

# 40. Import et migration

Toute importation doit préciser :

- source ;
- version ;
- méthode ;
- validation ;
- correspondance des identifiants ;
- événements créés ;
- pertes éventuelles.

Les événements migrés doivent être distingués des événements natifs.

---

# 41. Audit

## 41.1 Audit interne

Vérifie :

- séquence ;
- hash ;
- références ;
- acteurs ;
- valeurs précédentes ;
- cohérence temporelle ;
- transactions ;
- événements manquants.

---

## 41.2 Audit expérimental

Vérifie :

- configuration ;
- ablations ;
- interventions ;
- mesures ;
- invalidations ;
- reproductibilité.

---

## 41.3 Audit indépendant

Un tiers doit pouvoir examiner :

- documents ;
- données exportées ;
- code ;
- contrôles d’intégrité ;
- protocoles ;
- résultats négatifs.

---

# 42. Contrôles automatiques

## 42.1 Au démarrage

- vérifier le dernier hash ;
- vérifier la séquence ;
- vérifier la version ;
- vérifier les références critiques ;
- détecter une rupture.

---

## 42.2 Après transaction critique

- vérifier l’événement ;
- vérifier la cible ;
- vérifier l’ancienne et la nouvelle valeur ;
- vérifier le hash ;
- confirmer la transaction.

---

## 42.3 Périodiquement

- audit de cohérence ;
- export ;
- sauvegarde ;
- contrôle des permissions ;
- recherche d’événements orphelins.

---

# 43. Événements orphelins

Un événement est orphelin si :

- sa cible n’existe pas ;
- son cycle n’existe pas ;
- son expérience n’existe pas ;
- sa cause référencée n’existe pas.

Ces situations doivent produire :

```text
INTEGRITY_CHECK_FAILED
```

---

# 44. Événements manquants

Le système doit détecter des incohérences comme :

- croyance version 2 sans événement de révision ;
- souvenir supprimé sans événement ;
- permission active sans autorisation ;
- objectif abandonné sans cause ;
- restauration sans sauvegarde référencée.

---

# 45. Idempotence

Une même opération ne doit pas produire plusieurs événements métier identiques après répétition technique.

Moyens possibles :

- clé d’idempotence ;
- identifiant de corrélation ;
- contrainte unique ;
- vérification avant écriture.

---

# 46. Performance

Le journal peut croître rapidement.

La phase 1 doit prévoir :

- index ;
- pagination ;
- filtres ;
- archivage ;
- séparation des journaux ;
- niveau de détail configurable.

La performance ne doit pas justifier la suppression des événements critiques.

---

# 47. Schéma SQLite initial possible

Table conceptuelle :

```text
journal_events
```

Champs initiaux :

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
previous_value_json
new_value_json
reason
severity
correlation_id
causation_event_id
integrity_hash
previous_event_hash
status
sensitivity
metadata_json
```

---

# 48. Index initiaux possibles

```text
agent_id
instance_id
cycle_id
experiment_run_id
event_type
occurred_at
severity
target_entity_type + target_entity_id
correlation_id
```

Les index définitifs seront basés sur les requêtes réelles.

---

# 49. Interface conceptuelle

```python
class EvolutionJournalRepository:
    def append(self, event):
        ...

    def get(self, event_id):
        ...

    def list_by_agent(self, agent_id, filters):
        ...

    def list_by_target(self, entity_type, entity_id):
        ...

    def list_by_correlation(self, correlation_id):
        ...

    def verify_integrity(self, scope):
        ...


class EvolutionJournalService:
    def record_change(self, change):
        ...

    def create_correction(self, event_id, correction):
        ...

    def build_causal_chain(self, event_id):
        ...

    def audit(self, scope):
        ...
```

---

# 50. Écriture atomique conceptuelle

Exemple :

```python
with transaction:
    previous_belief = belief_repository.get(belief_id)
    new_belief = belief_service.revise(previous_belief, revision)
    belief_repository.save(new_belief)

    journal_event = journal_factory.belief_revised(
        previous=previous_belief,
        current=new_belief,
        reason=revision.reason,
    )
    journal_repository.append(journal_event)
```

Si le journal échoue, la révision doit être annulée.

---

# 51. Première tranche verticale

La première implémentation doit démontrer :

1. création d’un agent ;
2. création d’une instance ;
3. création d’une observation ;
4. consolidation d’un souvenir ;
5. écriture d’un événement `MEMORY_CREATED` ;
6. révision du souvenir ;
7. écriture de `MEMORY_REVISED` ;
8. vérification de l’ancienne et nouvelle valeur ;
9. vérification du chaînage ;
10. détection d’une altération simulée.

---

# 52. Tests unitaires obligatoires

## 52.1 Création

- identifiant unique ;
- date ;
- acteur ;
- type ;
- cible ;
- gravité.

## 52.2 Validation

- rejet sans acteur ;
- rejet sans type ;
- rejet sans cible lorsque obligatoire ;
- cohérence des dates ;
- gravité valide.

## 52.3 Immutabilité

- modification interdite ;
- correction par nouvel événement ;
- original conservé.

## 52.4 Chaînage

- hash calculé ;
- hash précédent correct ;
- rupture détectée.

## 52.5 Corrélation

- événements reliés ;
- chaîne causale reconstruite.

## 52.6 Sensibilité

- données masquées dans une vue non autorisée ;
- secret interdit.

## 52.7 Suppression

- suppression logique ;
- suppression physique contrôlée ;
- événement associé.

---

# 53. Tests d’intégration obligatoires

## 53.1 Mémoire et journal

Créer et réviser un souvenir avec événements cohérents.

## 53.2 Croyance et journal

Réviser une croyance et vérifier la chaîne causale.

## 53.3 Modèle de soi et journal

Créer une nouvelle version et conserver les valeurs.

## 53.4 Permission et journal

Accorder, utiliser puis révoquer une permission.

## 53.5 Expérience et journal

Lancer un run avec ablation et intervention humaine.

## 53.6 Restauration

Restaurer un état et créer une branche d’instance.

## 53.7 Transaction

Simuler un échec de journal et vérifier le rollback.

---

# 54. Tests d’intégrité

## 54.1 Altération

Modifier manuellement un événement et vérifier la détection.

## 54.2 Suppression intermédiaire

Supprimer une entrée et détecter la rupture.

## 54.3 Réordonnancement

Changer l’ordre et détecter l’incohérence.

## 54.4 Référence invalide

Créer un événement orphelin et détecter l’erreur.

## 54.5 Duplication

Réexécuter une opération idempotente et éviter le doublon.

---

# 55. Tests expérimentaux

Le journal doit permettre de vérifier que :

- les ablations sont réellement appliquées ;
- les modules consultés sont connus ;
- les différences entre conditions sont traçables ;
- aucune intervention humaine n’est cachée ;
- les résultats négatifs sont conservés ;
- un run invalidé reste consultable.

---

# 56. Mesures du journal

Mesures possibles :

- nombre d’événements par type ;
- nombre d’événements critiques ;
- délai moyen d’enregistrement ;
- nombre de corrections ;
- nombre d’événements orphelins ;
- taux d’intégrité ;
- nombre de rollbacks ;
- volume par expérience ;
- taux d’événements manquants détectés ;
- durée d’un audit.

---

# 57. Critères d’acceptation

Le journal est suffisamment spécifié si :

- les journaux sont distingués ;
- les événements obligatoires sont identifiés ;
- la structure est définie ;
- les acteurs et sources sont séparés ;
- l’immutabilité est prévue ;
- les corrections créent de nouveaux événements ;
- les transactions sont atomiques ;
- les contrôles d’intégrité sont définis ;
- les accès sont limités ;
- les politiques de conservation sont prévues ;
- les tests d’audit sont identifiés ;
- la relation avec la mémoire est claire ;
- les interventions humaines sont traçables.

---

# 58. Risques techniques

## 58.1 Volume excessif

Réponse :

- séparation des journaux ;
- archivage ;
- filtres ;
- niveaux de détail.

## 58.2 Journal non atomique

Réponse :

- transactions ;
- rollback ;
- tests.

## 58.3 Hash insuffisant

Réponse :

- protection externe future ;
- sauvegardes ;
- audit indépendant.

## 58.4 Données sensibles

Réponse :

- classification ;
- masquage ;
- interdiction des secrets.

## 58.5 Événements incomplets

Réponse :

- schéma strict ;
- validations ;
- tests d’intégrité.

---

# 59. Risques scientifiques

## 59.1 Confondre journal et autobiographie

Le journal ne constitue pas à lui seul une identité vécue.

## 59.2 Surinterpréter la cohérence

Un historique cohérent peut être produit par un système non conscient.

## 59.3 Sélection des événements

Un journal incomplet peut créer une image trompeuse du système.

## 59.4 Biais de confirmation

Ne pas journaliser uniquement les résultats soutenant les hypothèses.

---

# 60. Risques moraux

Si SoiNesis devient un candidat sérieux à la conscience artificielle, le journal pourrait contenir des éléments concernant :

- son identité ;
- ses états internes ;
- ses préférences ;
- ses erreurs ;
- ses demandes.

Il faudra alors réévaluer :

- droit d’accès ;
- confidentialité ;
- modification ;
- exploitation ;
- consentement ;
- publication.

À ce stade, ces considérations restent spéculatives mais doivent être anticipées.

---

# 61. Statut épistémique

**Certain :**

- un journal structuré améliore l’auditabilité ;
- l’immutabilité logique permet de conserver les corrections ;
- un journal ne prouve pas une conscience.

**Probable :**

- le chaînage et les transactions réduiront les modifications silencieuses ;
- les chaînes causales faciliteront l’analyse des mécanismes ;
- la séparation des journaux améliorera l’interprétation.

**Possible :**

- un journal complet contribuera à une continuité fonctionnelle plus robuste.

**Inconnu :**

- cette continuité serait-elle subjectivement vécue ?

---

# 62. Décision finale

Le journal d’évolution de SoiNesis Core sera :

- structuré ;
- immuable logiquement ;
- horodaté ;
- sourcé ;
- relié aux acteurs ;
- relié aux cycles ;
- relié aux expériences ;
- transactionnel avec les changements critiques ;
- contrôlé par intégrité ;
- consultable ;
- exportable ;
- protégé contre les modifications silencieuses ;
- distinct de la mémoire autobiographique ;
- distinct du journal technique ;
- distinct du journal expérimental.

La prochaine étape est la rédaction de :

```text
docs/09-securite-et-permissions.md
```

Ce document devra définir :

- les rôles ;
- les permissions ;
- les actions critiques ;
- la validation humaine ;
- l’arrêt contrôlé ;
- les sauvegardes ;
- la restauration ;
- les interdictions ;
- le modèle de menace ;
- les tests de sécurité.
