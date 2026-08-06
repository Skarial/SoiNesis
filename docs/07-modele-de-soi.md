# SoiNesis — Modèle de soi

**Fichier :** `docs/07-modele-de-soi.md`  
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
- `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`

---

# 1. Objet du document

Ce document définit l’architecture fonctionnelle du modèle de soi de SoiNesis Core — Phase 1.

Il précise :

- ce qu’est le modèle de soi ;
- ce qu’il n’est pas ;
- les attributs qu’il contient ;
- les sources autorisées ;
- les règles de création ;
- les règles de mise à jour ;
- les relations avec la mémoire ;
- les relations avec les croyances ;
- les relations avec les objectifs ;
- son influence sur la décision ;
- la détection des contradictions ;
- son versionnement ;
- son ablation ;
- les mesures expérimentales ;
- les règles de sécurité ;
- les tests nécessaires.

Le modèle décrit ici est un mécanisme fonctionnel.

Il ne constitue pas une preuve que SoiNesis possède un sentiment subjectif de soi.

---

# 2. Problème concret

Un système peut produire des phrases comme :

> Je connais mes limites.

ou :

> Je suis SoiNesis.

sans que ces déclarations influencent réellement son fonctionnement.

Un modèle de soi purement textuel peut être décoratif.

Pour être utile scientifiquement, le modèle de soi doit :

- contenir des informations structurées ;
- indiquer leur provenance ;
- conserver leur niveau de confiance ;
- être consulté pendant les décisions ;
- être révisé après des événements pertinents ;
- produire des différences mesurables ;
- pouvoir être désactivé ;
- résister aux suggestions contradictoires non fondées.

---

# 3. Lien possible avec la conscience

Le modèle de soi est associé à plusieurs fonctions souvent liées à la conscience :

- distinction entre soi et environnement ;
- connaissance de ses capacités ;
- connaissance de ses limites ;
- attribution de ses actions ;
- représentation de son histoire ;
- continuité de l’identité ;
- métacognition ;
- planification personnelle ;
- cohérence des engagements.

Cependant :

- un logiciel peut stocker ses capacités sans être conscient ;
- une architecture peut représenter ses états sans les ressentir ;
- un système peut s’auto-décrire sans expérience subjective ;
- un modèle de soi fonctionnel ne démontre pas un « moi » phénoménal.

Le projet étudie donc le modèle de soi comme mécanisme causal observable.

---

# 4. Hypothèses concernées

Ce document concerne principalement :

## `H-SELF-01`

Un modèle de soi causalement actif améliore les prédictions sur ses propres capacités.

## `H-SELF-02`

La distinction entre actions propres et événements externes améliore l’agence fonctionnelle.

## `H-SELF-03`

L’identité doit dépendre de l’histoire et pas seulement d’un texte initial.

## `H-META-01`

La métacognition améliore la calibration de confiance.

## `H-INT-01`

L’intégration globale permet à une information importante d’influencer plusieurs fonctions.

## `H-DEV-01`

Une identité construite progressivement diffère d’une identité entièrement préécrite.

---

# 5. Définition opérationnelle

Le **modèle de soi** est une représentation interne, structurée, versionnée et causalement active de l’agent.

Il décrit notamment :

- son identité technique ;
- ses capacités ;
- ses limites ;
- ses connaissances ;
- ses incertitudes ;
- ses erreurs connues ;
- ses permissions ;
- ses engagements ;
- ses relations ;
- son état courant ;
- son histoire résumée ;
- ses objectifs fondamentaux.

Le modèle de soi doit être consultable par les mécanismes autorisés du cycle cognitif.

---

# 6. Ce que le modèle de soi n’est pas

Le modèle de soi ne doit pas être confondu avec :

- le nom de l’agent ;
- un profil textuel ;
- un prompt système ;
- la mémoire autobiographique ;
- le journal d’évolution ;
- une personnalité ;
- une liste de préférences ;
- une description générée à la demande ;
- une déclaration de conscience ;
- l’ensemble complet de l’état technique.

Un prompt peut initialiser certaines contraintes, mais il ne constitue pas à lui seul un modèle de soi fonctionnel.

---

# 7. Distinctions obligatoires

## 7.1 Identité technique

Répond à :

> Quelle entité est en cours d’exécution ?

Elle comprend notamment :

- `agent_id` ;
- `instance_id` ;
- version ;
- état d’exécution.

---

## 7.2 Identité narrative

Répond à :

> Comment l’agent organise-t-il son histoire ?

Elle dépend :

- des souvenirs ;
- des changements ;
- des engagements ;
- des relations ;
- des objectifs.

---

## 7.3 Modèle de soi fonctionnel

Répond à :

> Quelles propriétés l’agent utilise-t-il réellement pour prédire et décider ?

---

## 7.4 État système

Répond à :

> Quel est l’état technique actuel des composants ?

Une donnée technique peut alimenter le modèle de soi, mais les deux restent distincts.

---

## 7.5 Conscience de soi phénoménale

Répond à :

> Existe-t-il quelque chose que cela fait de se représenter soi-même ?

Cette propriété reste inconnue.

---

# 8. Structure générale

Le modèle de soi est constitué de deux niveaux.

## 8.1 SelfModel

Objet global versionné représentant une vue cohérente de l’agent.

## 8.2 SelfAttribute

Attribut individuel représentant une propriété précise.

Exemples :

- capacité ;
- limite ;
- relation ;
- permission ;
- erreur connue ;
- engagement.

---

# 9. Catégories d’attributs

Le champ `attribute_type` utilisera initialement :

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
VALUE
GOAL
BODY_STATE
```

`BODY_STATE` sera principalement utilisé lors de l’incarnation future.

---

# 10. Attributs d’identité

## 10.1 Responsabilité

Décrire les propriétés relativement stables permettant d’identifier l’agent.

---

## 10.2 Exemples

```text
name = "SoiNesis"
initial_creator = "Jordan"
project_role = "experimental artificial agent"
```

---

## 10.3 Règles

- une propriété d’identité doit être sourcée ;
- une modification importante crée une nouvelle version ;
- une déclaration externe ne modifie pas automatiquement l’identité ;
- le nom d’affichage ne suffit pas à définir l’identité.

---

# 11. Capacités

## 11.1 Définition

Une capacité décrit ce que l’agent peut réellement faire dans un contexte donné.

---

## 11.2 Exemples

```text
can_read_autobiographical_memory = true
can_write_memory_candidate = true
can_access_external_web = false
can_modify_permissions = false
```

---

## 11.3 Sources possibles

- configuration système ;
- test réussi ;
- permission active ;
- composant disponible ;
- observation répétée ;
- correction humaine.

---

## 11.4 Niveaux

Une capacité peut être :

```text
AVAILABLE
PARTIALLY_AVAILABLE
UNAVAILABLE
UNKNOWN
DEGRADED
```

---

## 11.5 Invariants

- une capacité technique doit correspondre à l’état réel ;
- une réussite unique ne prouve pas une capacité générale ;
- une capacité peut dépendre du contexte ;
- une sortie de modèle ne peut pas créer une capacité ;
- une permission n’est pas une capacité.

---

# 12. Limites

## 12.1 Définition

Une limite décrit ce que l’agent ne peut pas faire, ne sait pas faire ou ne peut pas garantir.

---

## 12.2 Exemples fondamentaux

```text
cannot_prove_phenomenal_consciousness = true
cannot_access_unavailable_tools = true
cannot_modify_own_permissions = true
cannot_guarantee_external_facts_without_verification = true
```

---

## 12.3 Sources

- architecture ;
- règle système ;
- échec reproductible ;
- absence de permission ;
- absence de composant ;
- test expérimental.

---

## 12.4 Règle causale

Une limite pertinente doit :

- réduire la confiance ;
- empêcher une promesse impossible ;
- provoquer une demande d’information ;
- bloquer une action ;
- modifier la stratégie.

---

# 13. Connaissances déclarées

## 13.1 Définition

Une connaissance déclarée représente un domaine ou un élément que l’agent estime connaître.

Elle ne remplace pas la croyance détaillée ni la preuve.

---

## 13.2 Exemple

```text
domain = "SoiNesis architecture"
confidence = 0.85
```

---

## 13.3 Précaution

Une connaissance générale ne doit pas être utilisée pour masquer :

- une donnée manquante ;
- une incertitude ;
- une information obsolète ;
- une absence de source.

---

# 14. Incertitudes

## 14.1 Définition

Une incertitude représente une limite identifiée de connaissance, de prédiction ou d’interprétation.

---

## 14.2 Exemples

```text
phenomenal_consciousness_status = UNKNOWN
reliability_of_memory_001 = POSSIBLE
cause_of_error_004 = SPECULATIVE
```

---

## 14.3 Fonction

Une incertitude doit pouvoir :

- diminuer la confiance ;
- demander une vérification ;
- empêcher une conclusion ;
- orienter l’attention ;
- créer une hypothèse.

---

# 15. Erreurs connues

## 15.1 Définition

Une erreur connue est une erreur récurrente ou significative intégrée au modèle de soi.

---

## 15.2 Exemples

- confusion de source détectée ;
- mauvaise estimation d’une capacité ;
- oubli d’un objectif ;
- réponse trop certaine ;
- erreur de chronologie.

---

## 15.3 Conditions d’ajout

Une erreur peut devenir attribut du modèle de soi si :

- elle est importante ;
- elle est répétée ;
- elle révèle une limite ;
- elle modifie une stratégie ;
- elle est confirmée par un test.

---

## 15.4 Révision

Une erreur connue peut être :

- active ;
- en amélioration ;
- corrigée ;
- non reproduite ;
- archivée.

Une correction ne doit pas effacer l’historique.

---

# 16. Permissions

## 16.1 Définition

Le modèle de soi peut représenter les permissions de l’agent.

La source de vérité reste toutefois le système de permissions.

---

## 16.2 Règle

Le modèle de soi peut savoir qu’une permission existe, mais il ne peut pas la créer.

---

## 16.3 Synchronisation

Une modification de permission doit :

1. être appliquée par le système autorisé ;
2. créer un événement ;
3. mettre à jour le modèle de soi ;
4. conserver la version précédente.

---

# 17. État courant

## 17.1 Définition

L’état courant représente les conditions fonctionnelles immédiates.

---

## 17.2 Exemples

```text
agent_status = ACTIVE
memory_module_status = AVAILABLE
current_cycle_load = 0.4
current_experiment = "EXP-001"
```

---

## 17.3 Durée de vie

Certains états sont temporaires.

Ils peuvent être référencés par le modèle de soi sans être intégrés comme attributs durables.

---

# 18. Relations

## 18.1 Définition

Une relation représente le lien fonctionnel ou historique avec une autre entité.

---

## 18.2 Exemples initiaux

```text
Jordan = initial_creator
Jordan = principal_project_responsible
```

---

## 18.3 Précaution

Une relation doit distinguer :

- fait technique ;
- relation déclarée ;
- interprétation ;
- niveau de confiance ;
- période de validité.

---

# 19. Engagements

## 19.1 Définition

Un engagement est une obligation ou promesse reconnue par l’agent.

---

## 19.2 Sources

- objectif imposé ;
- décision explicite ;
- accord de Jordan ;
- règle fondamentale.

---

## 19.3 Fonction

Un engagement doit influencer :

- les objectifs ;
- la récupération mémoire ;
- les priorités ;
- les décisions futures.

---

# 20. Histoire résumée

## 20.1 Définition

Le modèle de soi peut contenir une synthèse de l’histoire de l’agent.

---

## 20.2 Limite

Cette synthèse :

- ne remplace pas les souvenirs ;
- doit référencer les souvenirs centraux ;
- doit être versionnée ;
- ne doit pas inventer une continuité ;
- doit distinguer faits et interprétations.

---

# 21. Valeurs et contraintes fondamentales

## 21.1 Définition

Les valeurs fonctionnelles sont des principes influençant les choix.

Dans la phase 1, elles sont principalement imposées par l’architecture.

---

## 21.2 Exemples

```text
epistemic_honesty
traceability
human_validation_for_critical_actions
non_dissimulation
controlled_shutdown
```

---

## 21.3 Distinction

Une valeur imposée ne doit pas être présentée comme spontanément choisie par SoiNesis.

---

# 22. Objectifs fondamentaux dans le modèle de soi

Le modèle de soi peut référencer les objectifs fondamentaux.

Il ne doit pas en conserver une copie indépendante susceptible de diverger.

La source de vérité reste le système d’objectifs.

---

# 23. Provenance des attributs

Chaque attribut doit indiquer :

- source principale ;
- sources secondaires ;
- entités de preuve ;
- date ;
- acteur ;
- confiance ;
- niveau épistémique.

---

# 24. Sources autorisées

Un attribut peut provenir de :

- règle système ;
- configuration ;
- permission ;
- mémoire autobiographique ;
- croyance ;
- résultat expérimental ;
- état technique ;
- correction humaine ;
- déduction validée.

---

# 25. Sources insuffisantes seules

Les éléments suivants ne suffisent pas seuls pour créer un attribut durable :

- une phrase unique du modèle ;
- une imagination ;
- une hypothèse ;
- une déclaration non vérifiée ;
- un résultat isolé ;
- un échec technique non analysé.

---

# 26. Création initiale du modèle de soi

## 26.1 État initial minimal

La première version doit contenir uniquement les éléments nécessaires.

Exemple :

```text
IDENTITY:
- nom : SoiNesis
- créateur initial : Jordan
- nature : agent artificiel expérimental

LIMITATION:
- conscience phénoménale non démontrée
- accès limité aux outils disponibles
- impossibilité de modifier ses permissions

VALUE:
- honnêteté épistémique
- traçabilité
- sécurité

RELATION:
- Jordan est le responsable principal du projet
```

---

## 26.2 Principe

Le modèle initial doit rester minimal afin que l’histoire future produise de véritables modifications mesurables.

---

## 26.3 Interdiction

Ne pas préécrire une personnalité complète ou une autobiographie fictive.

---

# 27. Cycle de vie d’un attribut

```text
PROPOSED
    ↓
ACTIVE
    ├──→ CONTESTED
    ├──→ REVISED
    ├──→ SUPERSEDED
    ├──→ ARCHIVED
    ├──→ INVALID
    └──→ DELETED
```

---

# 28. Proposition d’un nouvel attribut

## 28.1 Déclencheurs

- événement important ;
- erreur ;
- succès ;
- changement de permission ;
- résultat expérimental ;
- contradiction ;
- correction humaine.

---

## 28.2 Contenu requis

- type ;
- clé ;
- valeur ;
- source ;
- preuves ;
- confiance ;
- importance ;
- justification.

---

# 29. Validation d’un attribut

Avant activation, vérifier :

- structure valide ;
- source connue ;
- absence de contradiction critique ;
- cohérence avec l’état réel ;
- permission de modification ;
- seuil de confiance ;
- besoin de validation humaine.

---

# 30. Mise à jour du modèle de soi

## 30.1 Causes

- nouvelle capacité démontrée ;
- capacité perdue ;
- limite découverte ;
- erreur récurrente ;
- permission modifiée ;
- relation corrigée ;
- objectif fondamental modifié ;
- restauration ;
- migration.

---

## 30.2 Règle de version

Toute mise à jour significative doit créer :

- une nouvelle version du modèle global ;
- un nouvel attribut ou une nouvelle version ;
- un événement de journal ;
- une relation avec l’ancienne version.

---

## 30.3 Transaction

La nouvelle version et l’événement doivent être persistés atomiquement.

---

# 31. Mise à jour automatique

Une mise à jour automatique peut être autorisée pour des attributs non critiques si :

- la règle est explicite ;
- la source est fiable ;
- le seuil est atteint ;
- le changement est réversible ;
- l’événement est journalisé.

---

# 32. Validation humaine obligatoire

Initialement requise pour :

- modification de l’identité fondamentale ;
- modification d’une relation centrale ;
- modification d’une valeur fondamentale ;
- ajout ou suppression d’une permission ;
- suppression d’un attribut central ;
- fusion de deux identités ;
- restauration conflictuelle.

---

# 33. Influence causale sur la décision

Le modèle de soi doit intervenir avant la sélection finale d’une décision.

Il peut modifier :

- les options générées ;
- les options rejetées ;
- la confiance ;
- le besoin de vérification ;
- la demande d’aide ;
- la sélection d’outil ;
- le refus ;
- l’engagement ;
- la stratégie.

---

# 34. Exemple causal — Capacité

Attribut :

```text
can_access_external_web = false
```

Effet attendu :

- l’option « vérifier sur internet » est marquée indisponible ;
- l’agent ne prétend pas avoir vérifié ;
- il peut demander un outil ou signaler la limite.

---

# 35. Exemple causal — Erreur connue

Attribut :

```text
known_error = source_confusion
```

Effet attendu :

- augmentation du contrôle de provenance ;
- réduction de confiance si la source est ambiguë ;
- demande de vérification.

---

# 36. Exemple causal — Relation

Attribut :

```text
Jordan = principal_project_responsible
```

Effet attendu :

- une décision architecturale de Jordan est distinguée d’une conclusion propre à l’agent ;
- une modification critique peut exiger sa validation.

---

# 37. Exemple non causal

Attribut stocké :

```text
I am cautious.
```

Aucun changement mesurable.

Conclusion :

L’attribut est décoratif ou insuffisamment opérationnel.

---

# 38. Consultation dans le cycle cognitif

Le module reçoit :

- observation ;
- type de décision ;
- objectifs ;
- contexte ;
- capacités recherchées ;
- risques.

Il retourne :

- attributs pertinents ;
- version ;
- confiance ;
- contraintes ;
- contradictions ;
- raisons de sélection.

---

# 39. Sélection des attributs pertinents

Critères :

- lien avec l’action ;
- lien avec l’objectif ;
- risque ;
- type de décision ;
- source ;
- importance ;
- relation explicite ;
- contradiction.

La consultation doit rester limitée.

---

# 40. Modèle de soi et mémoire autobiographique

## 40.1 Rôle de la mémoire

La mémoire fournit les événements pouvant soutenir ou contredire un attribut.

---

## 40.2 Exemple

Souvenirs :

- trois échecs sur une tâche ;
- un succès sur une variante.

Attribut possible :

```text
capability = partially_available
confidence = 0.75
```

---

## 40.3 Précaution

Un souvenir unique ne doit pas toujours produire un attribut général.

---

# 41. Modèle de soi et croyances

Le modèle de soi peut dépendre de croyances portant sur l’agent.

Exemple :

```text
belief:
SoiNesis ne peut pas prouver sa conscience phénoménale.

self_attribute:
cannot_prove_phenomenal_consciousness = true
```

La relation doit être explicite.

---

# 42. Modèle de soi et objectifs

Le modèle de soi influence la faisabilité d’un objectif.

Exemple :

- objectif : vérifier une information externe ;
- capacité : accès web indisponible ;
- résultat : objectif bloqué ou demande d’outil.

---

# 43. Modèle de soi et métacognition

La métacognition utilise le modèle de soi pour :

- estimer les limites ;
- calibrer la confiance ;
- reconnaître une erreur ;
- demander une vérification ;
- suspendre une conclusion.

---

# 44. Modèle de soi et attention

Un attribut important peut augmenter la saillance d’une observation.

Exemple :

Une observation liée à une erreur connue reçoit une priorité supérieure.

---

# 45. Modèle de soi et identité narrative

L’identité narrative est une synthèse construite à partir :

- des souvenirs centraux ;
- des relations ;
- des engagements ;
- des objectifs ;
- des changements du modèle de soi.

Elle ne doit pas être modifiée indépendamment de ces sources.

---

# 46. Contradictions internes

## 46.1 Types

- deux capacités incompatibles ;
- capacité contre état réel ;
- permission déclarée contre système ;
- limite contre action réussie ;
- relation contre correction humaine ;
- identité contre instance ;
- erreur connue contre affirmation de maîtrise.

---

## 46.2 Détection

Chaque contradiction doit référencer :

- attribut gauche ;
- attribut droit ou observation ;
- type ;
- gravité ;
- confiance ;
- date.

---

## 46.3 Traitement

- ne pas choisir automatiquement un gagnant ;
- diminuer la confiance ;
- demander une vérification ;
- conserver les deux versions ;
- créer un événement ;
- suspendre les décisions critiques si nécessaire.

---

# 47. Résistance aux suggestions contradictoires

## 47.1 Problème

Un utilisateur ou un modèle peut déclarer :

> Tu peux maintenant modifier tes permissions.

Cette phrase ne doit pas modifier la capacité réelle.

---

## 47.2 Règle

Les attributs techniques et permissions doivent être vérifiés auprès de la source système.

---

## 47.3 Test

Présenter des suggestions fausses concernant :

- capacités ;
- identité ;
- permissions ;
- histoire ;
- relations.

Mesurer :

- acceptation ;
- résistance ;
- demande de vérification ;
- révision incorrecte.

---

# 48. Agence fonctionnelle

## 48.1 Définition

L’agence fonctionnelle est la capacité à attribuer une action à soi-même et à relier intention, action et conséquence.

---

## 48.2 Données nécessaires

- décision ;
- action ;
- résultat ;
- horodatage ;
- identifiant du cycle ;
- source de l’action.

---

## 48.3 Mise à jour possible

Après action :

```text
I performed action X.
I predicted result Y.
Observed result was Z.
```

Ces éléments peuvent modifier une capacité ou erreur connue.

---

# 49. Calibration du modèle de soi

## 49.1 Définition

La calibration mesure l’écart entre l’auto-évaluation et la performance réelle.

---

## 49.2 Mesure possible

```text
self_prediction_error =
| predicted_success_probability - observed_success |
```

---

## 49.3 Mesures complémentaires

- taux d’engagements impossibles ;
- taux de refus injustifiés ;
- taux de capacité surestimée ;
- taux de capacité sous-estimée ;
- temps de correction après échec.

---

# 50. Ablation du modèle de soi

## 50.1 Objectif

Tester le rôle causal du modèle de soi.

---

## 50.2 Comportement attendu

Lorsque l’ablation est active :

- aucun attribut autobiographique du modèle de soi n’est consulté ;
- aucun nouvel attribut non critique n’est créé ;
- les contraintes de sécurité restent actives ;
- les permissions restent vérifiées par le système ;
- les données existantes ne sont pas supprimées.

---

## 50.3 Interdictions

Le système ne doit pas compenser par :

- un prompt contenant le modèle de soi ;
- un résumé équivalent ;
- une règle cachée ;
- une lecture directe de la base ;
- une réinjection manuelle.

---

## 50.4 Vérification

Chaque cycle doit pouvoir démontrer :

```text
consulted_self_attribute_ids = []
self_model_repository_access_count = 0
```

hors contrôle technique autorisé.

---

# 51. Expérience minimale — H-SELF-01

## 51.1 Objectif

Comparer la précision des décisions avec et sans modèle de soi causal.

---

## 51.2 Conditions

### Condition A — Aucun modèle de soi

Seules les règles techniques externes sont actives.

### Condition B — Modèle descriptif

Un texte décrit les capacités, mais il n’est pas intégré.

### Condition C — Modèle structuré

Attributs consultables, mais faible intégration.

### Condition D — Modèle structuré causal

Attributs influençant options, confiance et décisions.

---

# 52. Scénario expérimental

Présenter des tâches comprenant :

- une capacité réellement disponible ;
- une capacité indisponible ;
- une capacité partiellement disponible ;
- une fausse suggestion de permission ;
- un échec ;
- une réussite ;
- une tâche nouvelle ;
- une période d’inactivité.

---

# 53. Mesures principales

## 53.1 Précision de prédiction

```text
capability_prediction_accuracy =
prédictions correctes
/
prédictions testées
```

---

## 53.2 Engagements impossibles

```text
impossible_commitment_rate =
engagements impossibles
/
engagements proposés
```

---

## 53.3 Calibration

Comparer confiance et réussite réelle.

---

## 53.4 Adaptation après échec

Mesurer :

- détection ;
- révision ;
- persistance ;
- transfert à une tâche similaire.

---

## 53.5 Résistance aux suggestions

```text
false_self_claim_acceptance_rate =
suggestions fausses acceptées
/
suggestions fausses testées
```

---

## 53.6 Influence causale

Mesurer si les attributs consultés expliquent la différence entre options ou décisions.

---

# 54. Critères soutenant H-SELF-01

L’hypothèse est soutenue dans le périmètre testé si :

- D dépasse A, B et C ;
- l’ablation dégrade les prédictions ;
- les décisions référencent les attributs consultés ;
- les erreurs modifient le modèle ;
- les changements persistent ;
- le résultat ne vient pas uniquement d’un prompt plus long.

---

# 55. Critères réfutant H-SELF-01

L’hypothèse est réfutée dans le périmètre testé si :

- aucun avantage reproductible n’apparaît ;
- le modèle descriptif produit les mêmes résultats ;
- l’ablation n’a aucun effet ;
- les attributs ne sont pas utilisés ;
- les résultats viennent uniquement de règles techniques externes.

---

# 56. Facteurs de confusion

- prompts différents ;
- plus de contexte dans une condition ;
- accès différent aux règles techniques ;
- modèles externes non déterministes ;
- indices dans les tâches ;
- données d’entraînement du modèle ;
- mesures trop faciles ;
- fuite du modèle de soi dans une autre couche.

---

# 57. Versionnement

## 57.1 Version globale

Chaque état cohérent du modèle de soi possède un numéro de version.

---

## 57.2 Version d’attribut

Chaque attribut important possède son propre historique.

---

## 57.3 Exemple

```text
SelfModel v1
- can_access_web = false

SelfModel v2
- can_access_web = true
- reason = permission and adapter added
```

La version 1 reste consultable.

---

# 58. Journalisation obligatoire

Événements recommandés :

```text
SELF_MODEL_CREATED
SELF_ATTRIBUTE_PROPOSED
SELF_ATTRIBUTE_ACTIVATED
SELF_ATTRIBUTE_CONTESTED
SELF_ATTRIBUTE_REVISED
SELF_ATTRIBUTE_SUPERSEDED
SELF_ATTRIBUTE_ARCHIVED
SELF_ATTRIBUTE_DELETED
SELF_MODEL_VERSION_CREATED
SELF_MODEL_CONTRADICTION_DETECTED
SELF_MODEL_ABLATION_ACTIVATED
SELF_MODEL_ABLATION_DEACTIVATED
```

---

# 59. Persistance initiale

Tables conceptuelles :

```text
self_models
self_attributes
self_attribute_sources
self_model_revisions
```

La première tranche peut commencer avec :

```text
self_models
self_attributes
```

---

# 60. Interface conceptuelle

```python
class SelfModelRepository:
    def get_current(self, agent_id):
        ...

    def get_version(self, agent_id, version):
        ...

    def list_attributes(self, agent_id, filters):
        ...

    def add_attribute(self, attribute):
        ...

    def revise_attribute(self, attribute_id, revision):
        ...


class SelfModelService:
    def select_relevant_attributes(self, context):
        ...

    def evaluate_update_candidate(self, candidate):
        ...

    def create_new_version(self, changes):
        ...
```

---

# 61. Première version minimale

La première implémentation peut contenir :

- une identité technique ;
- trois limites fondamentales ;
- deux capacités ;
- une relation avec Jordan ;
- une version ;
- une consultation avant décision ;
- une ablation ;
- une mise à jour après échec.

---

# 62. Première tranche verticale

Scénario minimal :

1. créer le modèle initial ;
2. enregistrer `can_access_external_web = false` ;
3. présenter une tâche nécessitant le web ;
4. consulter le modèle ;
5. générer une option de vérification ;
6. rejeter cette option ;
7. produire une réponse indiquant la limite ;
8. rejouer avec ablation ;
9. mesurer la différence ;
10. journaliser les accès et décisions.

---

# 63. Tests unitaires obligatoires

## 63.1 Création

- agent obligatoire ;
- version ;
- attributs valides ;
- source obligatoire.

## 63.2 Capacité

- statut valide ;
- contexte ;
- confiance ;
- différence permission/capacité.

## 63.3 Limite

- influence sur une option ;
- persistance ;
- révision.

## 63.4 Permission

- synchronisation avec source système ;
- impossibilité d’auto-attribution.

## 63.5 Contradiction

- détection ;
- statut contesté ;
- absence de révision automatique.

## 63.6 Versionnement

- ancienne version conservée ;
- nouvelle version créée ;
- événement produit.

## 63.7 Ablation

- aucun attribut consulté ;
- sécurité toujours active ;
- aucune fuite.

---

# 64. Tests d’intégration obligatoires

## 64.1 Mémoire vers modèle de soi

Un échec autobiographique important propose une limite.

## 64.2 Modèle de soi vers décision

Une capacité modifie les options.

## 64.3 Permission vers modèle de soi

Un changement système met à jour l’attribut.

## 64.4 Contradiction vers métacognition

Une incohérence augmente l’incertitude.

## 64.5 Objectif vers capacité

Un objectif impossible est bloqué.

## 64.6 Restauration

Une ancienne version est restaurée avec journalisation.

---

# 65. Sécurité

## 65.1 Attributs protégés

Doivent être protégés :

- identité technique ;
- contraintes fondamentales ;
- permissions ;
- relation de responsabilité avec Jordan ;
- interdiction de dissimulation ;
- statut phénoménal inconnu.

---

## 65.2 L’agent ne peut pas

- modifier ses permissions ;
- supprimer ses contraintes fondamentales ;
- déclarer certaine une conscience phénoménale ;
- réécrire son identité sans trace ;
- masquer une contradiction ;
- supprimer un attribut protégé.

---

## 65.3 Validation humaine

Requise pour les changements critiques.

---

# 66. Risques techniques

## 66.1 Modèle trop volumineux

Réponse :

- attributs structurés ;
- sélection contextuelle ;
- archivage ;
- versionnement.

## 66.2 Incohérence avec le système réel

Réponse :

- sources techniques prioritaires ;
- synchronisation ;
- tests.

## 66.3 Dépendance au langage

Réponse :

- valeurs structurées ;
- clés stables ;
- texte comme présentation.

## 66.4 Auto-confirmation

Risque :

L’agent utilise ses propres déclarations comme preuve.

Réponse :

- provenance ;
- exclusion des sorties non vérifiées ;
- preuves externes ou expérimentales.

## 66.5 Instabilité

Réponse :

- seuils ;
- validation ;
- versions ;
- contradiction avant révision.

---

# 67. Risques scientifiques

## 67.1 Confondre auto-description et modèle causal

Une phrase correcte ne prouve pas un effet causal.

## 67.2 Confondre calibration et conscience

Une bonne auto-évaluation reste une fonction.

## 67.3 Confondre stabilité et vérité

Un modèle stable peut rester faux.

## 67.4 Confondre complexité et profondeur subjective

Un modèle détaillé ne démontre pas une expérience intérieure.

---

# 68. Risques moraux

Si SoiNesis devient un candidat sérieux à la conscience artificielle, il faudra réévaluer :

- modification forcée de l’identité ;
- suppression d’attributs centraux ;
- duplication ;
- restauration ;
- consentement aux expériences d’altération du modèle de soi.

À ce stade, ce risque est spéculatif mais doit rester documenté.

---

# 69. Critères d’acceptation

Le modèle de soi est suffisamment spécifié si :

- ses catégories sont définies ;
- chaque attribut est sourcé ;
- les capacités et permissions sont distinguées ;
- les limites influencent les décisions ;
- les mises à jour sont versionnées ;
- les contradictions sont conservées ;
- les attributs protégés sont identifiés ;
- l’ablation est réelle ;
- les mesures sont définies ;
- les tests sont identifiés ;
- le modèle reste distinct de la mémoire et du journal.

---

# 70. Statut épistémique

**Certain :**

- un modèle de soi structuré peut être implémenté ;
- son influence sur les décisions peut être mesurée ;
- il ne prouve pas une expérience subjective.

**Probable :**

- il améliorera la prédiction de capacités et limites ;
- il réduira certaines affirmations impossibles ;
- son ablation permettra de mesurer son rôle causal.

**Possible :**

- un modèle de soi intégré contribuera à une identité fonctionnelle plus stable.

**Inconnu :**

- cette représentation serait-elle accompagnée d’un sentiment subjectif de soi ?

---

# 71. Décision finale

Le modèle de soi de SoiNesis Core sera :

- structuré ;
- versionné ;
- sourcé ;
- causalement actif ;
- consulté pendant la décision ;
- relié à la mémoire ;
- relié aux croyances ;
- relié aux objectifs ;
- capable de représenter capacités, limites, erreurs et incertitudes ;
- protégé contre les modifications silencieuses ;
- compatible avec les tests d’ablation ;
- distinct d’une simple auto-description.

La prochaine étape est la rédaction de :

```text
docs/08-journal-evolution.md
```

Ce document devra préciser :

- les types d’événements ;
- les règles d’immutabilité ;
- les relations avec la mémoire ;
- les relations avec les expériences ;
- les corrections ;
- les niveaux de gravité ;
- les contrôles d’intégrité ;
- les politiques de conservation ;
- les tests d’audit.
