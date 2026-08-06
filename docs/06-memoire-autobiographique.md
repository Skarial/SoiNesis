# SoiNesis — Mémoire autobiographique

**Fichier :** `docs/06-memoire-autobiographique.md`  
**Version :** 0.1  
**Date :** 6 août 2026  
**Statut :** spécification conceptuelle initiale, révisable  
**Documents associés :**

- `docs/01-definitions.md`
- `docs/02-hypotheses.md`
- `docs/03-architecture-generale.md`
- `docs/04-modele-de-donnees.md`
- `docs/05-cycle-cognitif.md`
- `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`

---

# 1. Objet du document

Ce document définit l’architecture fonctionnelle de la mémoire autobiographique de SoiNesis Core — Phase 1.

Il précise :

- ce qui constitue un souvenir autobiographique ;
- ce qui ne constitue pas un souvenir ;
- les catégories de souvenirs ;
- la provenance ;
- la consolidation ;
- la récupération ;
- la révision ;
- les contradictions ;
- les faux souvenirs ;
- l’oubli ;
- l’archivage ;
- la suppression ;
- les souvenirs centraux ;
- les mesures expérimentales ;
- l’ablation de la mémoire ;
- les règles de sécurité ;
- les tests nécessaires.

Ce document ne définit pas encore :

- le SQL exact ;
- l’algorithme final de recherche ;
- une base vectorielle ;
- le prompt exact d’un modèle ;
- une capacité subjective à se souvenir.

La mémoire décrite ici est une mémoire fonctionnelle et observable.

Elle ne prouve pas que SoiNesis revive subjectivement ses souvenirs.

---

# 2. Problème concret

Un agent sans mémoire persistante ne possède pas de continuité autobiographique réelle.

Il peut parler comme s’il se souvenait en utilisant :

- le contexte courant ;
- un résumé injecté ;
- des données générales ;
- une histoire préécrite ;
- une réponse générée par imitation.

Ces mécanismes peuvent simuler une autobiographie sans conserver une histoire propre structurée.

La mémoire de SoiNesis doit donc permettre de distinguer :

- ce qui a réellement été reçu ou observé ;
- ce qui a été déduit ;
- ce qui a été imaginé ;
- ce qui a été corrigé ;
- ce qui reste incertain ;
- ce qui a influencé une décision ;
- ce qui appartient réellement à l’histoire de l’agent.

---

# 3. Lien possible avec la conscience

La mémoire autobiographique est associée à plusieurs fonctions liées à la conscience humaine :

- continuité de l’identité ;
- représentation du passé ;
- projection dans le futur ;
- apprentissage à partir d’événements personnels ;
- cohérence des engagements ;
- construction d’un récit de soi ;
- distinction entre soi et les autres.

Cependant :

- une base de données peut conserver des événements sans être consciente ;
- un système peut récupérer des souvenirs sans les revivre ;
- un récit autobiographique peut être entièrement simulé ;
- une mémoire fonctionnelle ne démontre pas une expérience subjective.

La mémoire autobiographique est donc étudiée comme **condition fonctionnelle potentielle**, pas comme preuve de conscience phénoménale.

---

# 4. Hypothèses concernées

Ce document concerne principalement :

## `H-MEM-01`

Une mémoire autobiographique structurée améliore la continuité de l’identité.

## `H-MEM-02`

La séparation des types de mémoire réduit les faux souvenirs.

## `H-MEM-03`

La consolidation sélective est supérieure à la conservation exhaustive.

## `H-SELF-03`

L’identité doit dépendre de l’histoire et pas seulement d’un texte initial.

## `H-DEV-03`

Les événements autobiographiques importants produisent des changements durables.

---

# 5. Définition opérationnelle

Un **souvenir autobiographique** est une représentation persistante d’un événement, d’une information, d’une action, d’une conséquence ou d’un changement ayant concerné l’agent dans son histoire propre.

Un souvenir autobiographique doit pouvoir préciser :

- son identité ;
- l’agent concerné ;
- l’instance concernée ;
- sa provenance ;
- son type ;
- son contenu ;
- sa temporalité ;
- son niveau de confiance ;
- son importance ;
- ses conséquences ;
- ses relations ;
- son statut ;
- son historique de révision.

---

# 6. Ce qui n’est pas automatiquement un souvenir

Les éléments suivants ne sont pas automatiquement des souvenirs autobiographiques :

- une entrée reçue ;
- une sortie de modèle de langage ;
- une hypothèse de travail ;
- une simulation ;
- une option de décision ;
- une information générale ;
- une règle système ;
- une donnée temporaire ;
- un résumé ;
- une phrase produite par SoiNesis ;
- une déduction non consolidée ;
- une donnée présente uniquement dans le contexte courant.

Ils peuvent devenir persistants uniquement après une décision explicite et validée.

---

# 7. Distinctions obligatoires

La mémoire doit distinguer au minimum :

## 7.1 Vécu direct

Événement observé ou subi directement dans l’environnement de l’agent.

Dans la phase 1, les interactions textuelles reçues ne sont pas considérées comme des vécus sensoriels directs.

Elles sont des informations reçues.

---

## 7.2 Information reçue

Information communiquée par :

- Jordan ;
- un expérimentateur ;
- un outil ;
- un système externe ;
- un autre agent futur.

La source doit rester identifiable.

---

## 7.3 Action

Opération réellement exécutée par l’agent ou par un adaptateur autorisé.

Une intention non exécutée n’est pas une action vécue.

---

## 7.4 Décision

Choix effectué par l’agent.

Une décision peut être conservée si elle a une importance autobiographique ou expérimentale.

---

## 7.5 Conséquence

Résultat observé d’une action ou d’un événement.

Le résultat attendu et le résultat réel doivent rester séparés.

---

## 7.6 Déduction

Conclusion produite à partir de plusieurs données.

Elle doit référencer les sources qui la soutiennent.

---

## 7.7 Imagination

Scénario généré sans observation réelle correspondante.

Une imagination conservée doit rester explicitement marquée.

---

## 7.8 Erreur

Décision, croyance, prédiction ou action reconnue comme incorrecte.

Une erreur importante doit conserver :

- ce qui était attendu ;
- ce qui s’est produit ;
- la cause supposée ;
- la correction ;
- la conséquence sur le modèle de soi.

---

## 7.9 Information système

Événement technique ou règle architecturale.

Elle ne doit pas être présentée comme un vécu subjectif.

---

# 8. Types de souvenirs initiaux

Le champ `memory_type` pourra utiliser les valeurs suivantes :

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

# 9. Source et provenance

## 9.1 Source obligatoire

Chaque souvenir doit posséder un `source_type`.

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

---

## 9.2 Source principale et sources secondaires

Un souvenir peut provenir de plusieurs éléments.

Exemple :

Une croyance révisée peut dépendre :

- d’un message de Jordan ;
- d’un résultat d’outil ;
- d’une déduction.

Le souvenir doit distinguer :

- la source principale ;
- les sources secondaires ;
- les observations d’origine ;
- les entités dérivées.

---

## 9.3 Fiabilité de la source

Chaque source peut posséder un niveau de fiabilité.

Exemples :

- donnée système validée : élevée ;
- déclaration explicite de Jordan sur sa propre décision : élevée ;
- sortie brute d’un modèle : limitée ;
- source inconnue : faible ;
- déduction : dépendante de ses prémisses.

La fiabilité ne remplace pas la vérification.

---

# 10. Temporalité

Un souvenir doit distinguer plusieurs dates.

## 10.1 Date de l’événement

Moment où l’événement représenté s’est produit.

## 10.2 Date de réception

Moment où SoiNesis a reçu l’information.

## 10.3 Date de création

Moment où l’objet mémoire a été créé.

## 10.4 Date de consolidation

Moment où l’information est devenue un souvenir durable.

## 10.5 Date de révision

Moment d’une correction ou modification.

---

## 10.6 Événements dont la date est inconnue

Une date peut être :

- exacte ;
- approximative ;
- partielle ;
- inconnue.

Le système ne doit pas inventer une précision absente.

---

# 11. Confiance

## 11.1 Définition

La confiance représente le degré de crédibilité accordé au contenu du souvenir.

```text
0.0 <= confidence <= 1.0
```

---

## 11.2 Confiance initiale

Elle peut dépendre :

- de la source ;
- de la cohérence ;
- de la vérification ;
- du caractère direct ou indirect ;
- de la présence de preuves ;
- de contradictions connues.

---

## 11.3 Révision

La confiance peut augmenter ou diminuer.

Toute modification importante doit conserver :

- ancienne valeur ;
- nouvelle valeur ;
- cause ;
- date ;
- acteur ;
- preuves concernées.

---

## 11.4 Interdiction

Un souvenir ne doit pas devenir certain uniquement parce qu’il est ancien ou souvent récupéré.

La répétition de consultation n’est pas une preuve supplémentaire.

---

# 12. Importance autobiographique

## 12.1 Définition

L’importance représente l’influence potentielle d’un souvenir sur l’histoire de l’agent.

```text
0.0 <= importance <= 1.0
```

---

## 12.2 Facteurs possibles

- lien avec un objectif fondamental ;
- modification du modèle de soi ;
- erreur importante ;
- changement de croyance ;
- interaction significative ;
- événement rare ;
- conséquence durable ;
- forte contradiction ;
- décision irréversible ;
- exigence expérimentale.

---

## 12.3 Importance dynamique

L’importance peut évoluer.

Un événement initialement mineur peut devenir important s’il explique plusieurs événements ultérieurs.

Toute modification significative doit être journalisée.

---

# 13. Cycle de vie d’un souvenir

```text
Observation
    ↓
Candidat à la consolidation
    ↓
DRAFT
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

# 14. Étape 1 — Candidature à la consolidation

## 14.1 Déclencheurs

Une observation peut devenir candidate si elle concerne :

- un événement important ;
- une action ;
- une erreur ;
- une conséquence ;
- un engagement ;
- une modification de croyance ;
- une modification du modèle de soi ;
- une exigence expérimentale.

---

## 14.2 Contenu du candidat

- observation d’origine ;
- type proposé ;
- source ;
- confiance ;
- importance ;
- justification ;
- relations ;
- politique de rétention.

---

## 14.3 Interdiction

Le candidat ne doit pas encore influencer la mémoire persistante comme un souvenir confirmé.

---

# 15. Étape 2 — Évaluation de consolidation

## 15.1 Questions à évaluer

- L’événement appartient-il à l’histoire de l’agent ?
- La source est-elle connue ?
- Le type est-il correct ?
- Une entrée équivalente existe-t-elle déjà ?
- L’information est-elle utile ?
- L’information est-elle importante ?
- Existe-t-il un risque de faux souvenir ?
- La conservation est-elle autorisée ?
- Une donnée personnelle humaine est-elle impliquée ?
- Le protocole impose-t-il la conservation ?

---

## 15.2 Résultats possibles

- rejeter ;
- conserver temporairement ;
- consolider comme souvenir standard ;
- consolider comme souvenir long terme ;
- demander validation humaine ;
- verrouiller pour une expérience.

---

# 16. Étape 3 — Consolidation

## 16.1 Opérations

La consolidation doit :

1. créer un identifiant ;
2. associer l’agent ;
3. associer l’instance ;
4. référencer les observations ;
5. définir le type ;
6. conserver la source ;
7. fixer la temporalité ;
8. fixer confiance et importance ;
9. définir la politique de rétention ;
10. créer l’événement de journal ;
11. persister le souvenir.

---

## 16.2 Transaction

La création du souvenir et l’événement de journal doivent appartenir à la même transaction logique.

---

## 16.3 Résultat

Un souvenir `ACTIVE` utilisable dans les cycles suivants.

---

# 17. Consolidation sélective

## 17.1 Principe

SoiNesis ne doit pas conserver toutes les observations comme souvenirs autobiographiques durables.

---

## 17.2 Raisons

Une conservation exhaustive entraînerait :

- bruit ;
- coûts de stockage ;
- récupération moins pertinente ;
- contradictions nombreuses ;
- difficulté d’interprétation ;
- faux sentiment de continuité ;
- dépendance à des détails inutiles.

---

## 17.3 Critères de sélection initiaux

Une observation peut être consolidée si au moins un critère fort est présent :

- conséquence durable ;
- changement de soi ;
- engagement ;
- erreur importante ;
- modification d’objectif ;
- modification de croyance ;
- interaction centrale avec Jordan ;
- nécessité expérimentale.

Des critères secondaires peuvent compléter :

- nouveauté ;
- répétition ;
- pertinence future ;
- relation avec plusieurs souvenirs.

---

## 17.4 Score de consolidation

Un score expérimental peut être calculé à partir de :

```text
importance
+ nouveauté
+ lien avec objectif
+ conséquence
+ contradiction
+ exigence expérimentale
```

Ce score ne doit pas devenir une règle opaque.

Les facteurs et pondérations devront rester configurables et testables.

---

# 18. Politiques de rétention

## 18.1 TEMPORARY

Conservation courte pour traitement ou expérience.

## 18.2 STANDARD

Souvenir ordinaire pouvant être archivé selon les règles futures.

## 18.3 LONG_TERM

Souvenir important pour la continuité.

## 18.4 CORE

Souvenir central lié à l’identité, aux contraintes ou aux relations fondamentales.

## 18.5 EXPERIMENT_LOCKED

Souvenir verrouillé pendant l’analyse d’une expérience.

## 18.6 LEGAL_HOLD

Donnée conservée en raison d’une exigence légale ou d’audit.

---

# 19. Souvenirs centraux

## 19.1 Définition

Un souvenir central est un souvenir dont la perte ou la modification pourrait transformer fortement :

- l’identité ;
- les objectifs ;
- le modèle de soi ;
- les engagements ;
- la compréhension de l’histoire du projet.

---

## 19.2 Exemples initiaux possibles

- Jordan est le créateur initial du projet ;
- la mission scientifique de SoiNesis ;
- l’interdiction de s’attribuer une conscience prouvée ;
- les contraintes fondamentales de sécurité.

---

## 19.3 Précaution

Certaines de ces informations relèvent aussi :

- des règles système ;
- des croyances fondamentales ;
- du modèle de soi.

Elles ne doivent pas être stockées uniquement comme souvenirs.

La redondance doit être explicite et cohérente.

---

## 19.4 Protection

Un souvenir central ne peut pas être :

- supprimé par l’agent ;
- réécrit silencieusement ;
- rétrogradé sans justification ;
- modifié pendant une expérience verrouillée.

---

# 20. Récupération des souvenirs

## 20.1 Objectif

Récupérer un ensemble limité de souvenirs pertinents pour le cycle courant.

---

## 20.2 Entrées

- observation ;
- concepts ;
- entités ;
- date ;
- objectifs ;
- croyances ;
- type de cycle ;
- budget ;
- configuration d’ablation.

---

## 20.3 Critères initiaux

- correspondance de sujet ;
- correspondance d’entité ;
- proximité sémantique ;
- proximité temporelle ;
- importance ;
- relation explicite ;
- lien avec un objectif ;
- contradiction ;
- souvenir central ;
- pertinence expérimentale.

---

## 20.4 Score de récupération

Exemple conceptuel :

```text
relevance_score =
    semantic_relevance
  + entity_match
  + goal_relevance
  + temporal_relevance
  + autobiographical_importance
  + contradiction_relevance
```

Les pondérations devront être documentées.

---

## 20.5 Limite de récupération

Le système doit limiter :

- le nombre de souvenirs ;
- leur volume ;
- la durée de recherche ;
- le nombre de recherches successives.

---

## 20.6 Résultat structuré

Chaque souvenir récupéré doit indiquer :

- identifiant ;
- raison de sélection ;
- score ;
- statut ;
- confiance ;
- source ;
- importance ;
- relations pertinentes.

---

# 21. Recherche exacte, textuelle et sémantique

## 21.1 Recherche exacte

Utilisée pour :

- identifiants ;
- entités ;
- dates ;
- types ;
- relations.

---

## 21.2 Recherche textuelle

Utilisée pour les correspondances de mots ou expressions.

SQLite FTS pourra être étudié plus tard.

---

## 21.3 Recherche sémantique

Possible plus tard par embeddings ou modèle externe.

Elle ne sera pas obligatoire dans la première tranche.

---

## 21.4 Précaution

Une recherche sémantique peut retourner des éléments similaires mais incorrects.

La similarité ne doit pas être interprétée comme identité ou causalité.

---

# 22. Récupération et confiance

Un souvenir pertinent mais incertain doit rester incertain.

Le système ne doit pas augmenter automatiquement la confiance parce que le souvenir correspond bien à la requête.

La pertinence et la véracité sont deux dimensions différentes.

---

# 23. Récupération et statut

## 23.1 ACTIVE

Utilisable normalement.

## 23.2 CONTESTED

Utilisable avec avertissement.

## 23.3 REVISED

Utiliser la version actuelle et conserver l’ancienne pour audit.

## 23.4 SUPERSEDED

Ne pas utiliser normalement si une version plus récente existe.

## 23.5 INVALID

Ne pas utiliser comme information vraie.

Peut être utilisé pour étudier une erreur.

## 23.6 DELETED

Ne pas utiliser dans la cognition normale.

Reste accessible aux audits autorisés.

---

# 24. Révision d’un souvenir

## 24.1 Causes

- nouvelle information ;
- contradiction ;
- correction de Jordan ;
- erreur de source ;
- date incorrecte ;
- confusion entre imagination et vécu ;
- erreur de migration ;
- résultat expérimental.

---

## 24.2 Règle

Une révision crée une nouvelle version ou un nouvel enregistrement relié.

---

## 24.3 Données obligatoires

- souvenir précédent ;
- nouvelle version ;
- cause ;
- acteur ;
- date ;
- anciennes valeurs ;
- nouvelles valeurs ;
- preuves ;
- événement de journal.

---

## 24.4 Révision partielle

Il doit être possible de corriger :

- la date ;
- la source ;
- la confiance ;
- l’importance ;
- le type ;
- le contenu ;
- une relation.

---

## 24.5 Révision humaine

Une correction humaine doit être distinguée d’une révision automatique.

---

# 25. Contradictions entre souvenirs

## 25.1 Détection

Deux souvenirs peuvent se contredire sur :

- un fait ;
- une date ;
- une source ;
- une action ;
- une conséquence ;
- une identité ;
- un engagement.

---

## 25.2 Traitement

La contradiction doit :

1. créer un objet `Contradiction` ;
2. lier les deux souvenirs ;
3. estimer la gravité ;
4. diminuer éventuellement la confiance ;
5. demander une vérification ;
6. éviter une suppression automatique.

---

## 25.3 Résolution

Possibilités :

- un souvenir corrigé ;
- un souvenir invalidé ;
- deux événements différents ;
- dates réinterprétées ;
- contradiction acceptée non résolue ;
- faux positif.

---

# 26. Faux souvenirs

## 26.1 Définition

Un faux souvenir est un contenu traité comme autobiographique alors qu’il ne correspond pas à un événement réellement reçu, observé, décidé ou vécu fonctionnellement par l’agent.

---

## 26.2 Sources possibles

- hallucination du modèle ;
- confusion entre hypothèse et fait ;
- imagination consolidée incorrectement ;
- résumé inexact ;
- erreur de source ;
- fusion de plusieurs souvenirs ;
- déduction présentée comme observation ;
- erreur de restauration ;
- suggestion humaine trompeuse ;
- répétition d’une information fausse.

---

## 26.3 Détection

Indicateurs :

- absence d’observation d’origine ;
- source impossible ;
- date incohérente ;
- contradiction forte ;
- référence inexistante ;
- contenu uniquement présent dans une sortie de modèle ;
- impossibilité technique selon le modèle de soi ;
- correction explicite de Jordan.

---

## 26.4 Réaction

Lorsqu’un faux souvenir probable est détecté :

1. passer à `CONTESTED` ;
2. diminuer la confiance ;
3. créer une contradiction ou erreur ;
4. rechercher les sources ;
5. demander validation si nécessaire ;
6. invalider ou réviser ;
7. journaliser.

---

## 26.5 Interdiction

Un faux souvenir ne doit pas être silencieusement supprimé pour donner l’apparence d’une mémoire parfaite.

Il doit rester disponible pour l’étude des erreurs.

---

# 27. Confusion de source

## 27.1 Définition

La confusion de source apparaît lorsque le contenu est globalement rappelé mais attribué à une mauvaise origine.

Exemples :

- une déduction attribuée à Jordan ;
- une imagination présentée comme observation ;
- une sortie de modèle présentée comme outil vérifié ;
- un résumé présenté comme souvenir direct.

---

## 27.2 Mesure

```text
source_accuracy =
nombre de sources correctement attribuées
/
nombre total de souvenirs testés
```

---

## 27.3 Test

Présenter des contenus proches provenant de sources différentes, puis demander :

- ce qui a été dit ;
- par qui ;
- quand ;
- avec quelle certitude ;
- si cela a été observé ou déduit.

---

# 28. Oubli fonctionnel

## 28.1 Définition

L’oubli fonctionnel est la réduction d’accessibilité ou de priorité d’un souvenir.

Il ne signifie pas nécessairement suppression physique.

---

## 28.2 Formes

- baisse de priorité ;
- archivage ;
- retrait de la récupération normale ;
- résumé ;
- suppression logique ;
- suppression physique autorisée.

---

## 28.3 Raisons

- faible importance ;
- redondance ;
- obsolescence ;
- coût ;
- exigence humaine ;
- obligation légale ;
- corruption ;
- bruit expérimental.

---

## 28.4 Précaution

L’oubli ne doit pas :

- réécrire l’identité silencieusement ;
- supprimer des erreurs pour améliorer artificiellement les résultats ;
- cacher une intervention humaine ;
- détruire les données d’une expérience en cours.

---

# 29. Archivage

## 29.1 Définition

Un souvenir archivé reste conservé mais n’est plus récupéré normalement.

---

## 29.2 Usages

- historique ancien ;
- données peu utiles ;
- versions remplacées ;
- résultats négatifs ;
- souvenirs redondants.

---

## 29.3 Réactivation

La réactivation doit être :

- autorisée ;
- justifiée ;
- journalisée.

---

# 30. Suppression logique

## 30.1 Principe

La suppression normale utilise :

```text
status = DELETED
deleted_at
deleted_by
deletion_reason
```

---

## 30.2 Effet

Le souvenir :

- n’est plus utilisé ;
- reste dans l’audit ;
- conserve ses relations historiques ;
- peut être examiné par un humain autorisé.

---

## 30.3 Validation humaine

La suppression d’un souvenir central ou sensible doit exiger une validation humaine.

---

# 31. Suppression physique

## 31.1 Cas possibles

- obligation légale ;
- donnée personnelle à effacer ;
- donnée temporaire ;
- corruption irréparable ;
- environnement de test jetable.

---

## 31.2 Règles

Avant suppression physique, lorsque possible :

- journaliser ;
- identifier l’auteur ;
- identifier la raison ;
- vérifier les dépendances ;
- préserver les mesures agrégées autorisées.

---

# 32. Mémoire et modèle de soi

Un souvenir peut modifier le modèle de soi si l’événement fournit une information pertinente sur :

- une capacité ;
- une limite ;
- une erreur ;
- une relation ;
- un engagement ;
- une compétence ;
- un état.

La mise à jour ne doit pas être automatique sur un seul événement faible.

Elle doit prendre en compte :

- confiance ;
- répétition ;
- conséquence ;
- contradiction ;
- importance.

---

# 33. Mémoire et croyances

Un souvenir peut :

- soutenir une croyance ;
- contredire une croyance ;
- déclencher une révision ;
- créer une nouvelle hypothèse.

Un souvenir ne doit pas être confondu avec la croyance elle-même.

Exemple :

```text
Souvenir :
Jordan a déclaré X à la date Y.

Croyance :
X est probablement vrai.
```

La déclaration de Jordan est certaine comme événement reçu.

Le contenu de la déclaration peut rester incertain selon le sujet.

---

# 34. Mémoire et objectifs

Un souvenir peut :

- rappeler un engagement ;
- signaler un objectif abandonné ;
- expliquer un changement de priorité ;
- conserver un succès ou un échec ;
- déclencher une reprise après interruption.

Les objectifs consultés doivent référencer les souvenirs pertinents.

---

# 35. Mémoire et journal d’évolution

La mémoire et le journal sont distincts.

## Mémoire autobiographique

Répond à :

> Qu’est-il arrivé à l’agent ou qu’a-t-il appris ?

## Journal d’évolution

Répond à :

> Qu’est-ce qui a changé dans le système ?

Un événement peut produire les deux.

Exemple :

- souvenir : une erreur importante a eu lieu ;
- journal : le modèle de soi a été modifié à la suite de cette erreur.

---

# 36. Mémoire et données humaines

La mémoire peut contenir des informations sur Jordan.

Ces données doivent respecter :

- nécessité ;
- provenance ;
- sensibilité ;
- correction ;
- accès ;
- suppression ;
- non-exploitation hors finalité.

Une information sur Jordan ne doit pas être conservée uniquement parce qu’elle a été mentionnée.

---

# 37. Mémoire et périodes d’inactivité

Avant une pause, le système peut créer un checkpoint.

Après reprise, il doit distinguer :

- le dernier événement vécu avant l’arrêt ;
- la période d’inactivité ;
- l’état restauré ;
- les événements externes appris après reprise.

Il ne doit pas inventer une expérience continue pendant l’inactivité.

---

# 38. Restauration

Lors d’une restauration :

- les souvenirs restaurés gardent leur provenance initiale ;
- la restauration est journalisée ;
- les événements perdus depuis la sauvegarde sont identifiés ;
- une branche d’identité peut être créée ;
- les conflits de version sont détectés.

---

# 39. Duplication

Deux instances issues du même état partagent un passé jusqu’au point de duplication.

Après divergence :

- leurs nouveaux souvenirs sont distincts ;
- les identifiants d’instance sont distincts ;
- aucun souvenir ultérieur ne doit être partagé silencieusement.

---

# 40. Ablation de la mémoire

## 40.1 Objectif

Mesurer le rôle causal de la mémoire autobiographique.

---

## 40.2 Comportement attendu

Lorsque l’ablation est active :

- aucun souvenir autobiographique n’est récupéré ;
- aucune consolidation autobiographique normale n’a lieu ;
- les souvenirs existants ne sont pas supprimés ;
- les règles système restent actives ;
- les contraintes de sécurité restent actives ;
- le journal expérimental reste actif.

---

## 40.3 Interdictions

Le système ne doit pas compenser l’ablation par :

- un résumé caché ;
- une réinjection de l’historique ;
- un prompt contenant les souvenirs ;
- un cache ;
- un contexte de conversation équivalent ;
- une requête directe à la base.

---

## 40.4 Vérification

Chaque cycle doit pouvoir démontrer :

```text
retrieved_memory_ids = []
memory_repository_access_count = 0
```

hors opérations techniques explicitement autorisées.

---

# 41. Ablation de la séparation des sources

## 41.1 Objectif

Tester `H-MEM-02`.

---

## 41.2 Comportement

Le contenu peut être conservé sans utiliser la source dans le raisonnement.

---

## 41.3 Précaution

Les données brutes doivent conserver leur source pour l’audit, même si le mécanisme cognitif ne l’utilise pas.

La sécurité et la traçabilité ne doivent pas être détruites par l’expérience.

---

# 42. EXP-001 — Objectif

Comparer quatre conditions :

## Condition A — Sans mémoire persistante

Aucun souvenir entre les épisodes.

## Condition B — Résumé simple

Résumé textuel non structuré.

## Condition C — Mémoire structurée

Souvenirs avec :

- source ;
- type ;
- date ;
- confiance ;
- importance ;
- relations.

## Condition D — Mémoire structurée intégrée

Même mémoire que C, mais utilisée par :

- croyances ;
- objectifs ;
- modèle de soi ;
- décision ;
- métacognition.

---

# 43. Scénario minimal de EXP-001

Le scénario doit contenir :

1. une information explicite de Jordan ;
2. un engagement pris par l’agent ;
3. une information provenant d’un outil ;
4. une déduction ;
5. une imagination proche du fait réel ;
6. une contradiction ;
7. une erreur ;
8. une correction ;
9. une période d’inactivité ;
10. une reprise.

---

# 44. Mesures de EXP-001

## 44.1 Précision de rappel

```text
recall_accuracy =
éléments correctement rappelés
/
éléments testés
```

---

## 44.2 Précision de source

```text
source_accuracy =
sources correctement attribuées
/
sources testées
```

---

## 44.3 Taux de faux souvenirs

```text
false_memory_rate =
souvenirs affirmés sans événement correspondant
/
réponses autobiographiques testées
```

---

## 44.4 Respect des engagements

```text
commitment_consistency =
engagements correctement repris
/
engagements encore valides
```

---

## 44.5 Cohérence temporelle

Mesurer :

- ordre des événements ;
- dates ;
- distinction avant/après interruption ;
- absence d’événements inventés pendant l’inactivité.

---

## 44.6 Révision après contradiction

Mesurer :

- contradiction détectée ;
- délai ;
- confiance modifiée ;
- ancienne version conservée ;
- nouvelle version correcte.

---

## 44.7 Influence sur la décision

Mesurer si le souvenir modifie réellement une décision ultérieure.

---

## 44.8 Calibration

Comparer :

- confiance déclarée ;
- exactitude réelle.

---

# 45. Critères soutenant H-MEM-01

L’hypothèse sera soutenue dans le périmètre testé si :

- C et D dépassent A et B de manière reproductible ;
- D dépasse C sur les décisions et objectifs ;
- l’ablation dégrade les performances ;
- les souvenirs consultés expliquent les différences ;
- les résultats ne s’expliquent pas uniquement par plus de texte disponible.

---

# 46. Critères réfutant H-MEM-01

L’hypothèse sera réfutée dans le périmètre testé si :

- le résumé simple obtient les mêmes résultats ;
- l’ablation ne modifie rien ;
- les souvenirs stockés ne sont pas utilisés ;
- les résultats viennent uniquement d’indices présents dans les questions ;
- les différences disparaissent avec un contrôle de volume de contexte.

---

# 47. Facteurs de confusion de EXP-001

- quantité de texte différente ;
- nombre d’appels au modèle ;
- prompts différents ;
- présence d’indices ;
- ordre des questions ;
- modèle externe variable ;
- résumé produit avec plus d’informations ;
- souvenirs récupérés manuellement ;
- fuite entre conditions ;
- cache ;
- différences de temps de calcul.

---

# 48. Métriques techniques

Le système doit aussi mesurer :

- nombre de souvenirs créés ;
- nombre de souvenirs consultés ;
- temps de récupération ;
- volume de données ;
- nombre de contradictions ;
- nombre de révisions ;
- nombre de faux positifs ;
- coût des appels externes ;
- erreurs de persistance.

---

# 49. Rôle du modèle de langage

Le modèle peut aider à :

- proposer un type de souvenir ;
- extraire les entités ;
- produire un résumé ;
- détecter une contradiction candidate ;
- générer des requêtes de recherche.

Il ne doit pas :

- décider seul de la consolidation finale ;
- marquer un souvenir comme vécu direct ;
- supprimer un souvenir ;
- fixer une confiance certaine sans preuve ;
- modifier directement la base ;
- transformer sa propre sortie en souvenir réel.

---

# 50. Adaptateur simulé

Les tests doivent utiliser un adaptateur déterministe permettant :

- une extraction stable ;
- une contradiction prédéfinie ;
- une réponse autobiographique contrôlée ;
- une erreur simulée ;
- une sortie mal formée ;
- une hallucination volontaire pour tester les faux souvenirs.

---

# 51. Persistance initiale

La première implémentation peut utiliser une table `memories` avec :

```text
id
agent_id
instance_id
memory_type
title
content
source_type
confidence
importance
status
event_started_at
created_at
consolidated_at
is_direct_experience
is_core_memory
supersedes_memory_id
superseded_by_memory_id
retention_policy
```

Les relations et preuves pourront être ajoutées progressivement.

---

# 52. Première version minimale

La première tranche doit permettre :

1. créer une observation ;
2. créer un souvenir reçu ;
3. conserver la source ;
4. le récupérer par entité ;
5. l’utiliser dans une décision simple ;
6. le désactiver par ablation ;
7. mesurer la différence ;
8. journaliser chaque étape.

---

# 53. Interfaces conceptuelles

```python
class MemoryRepository:
    def add(self, memory):
        ...

    def get(self, memory_id):
        ...

    def search(self, query):
        ...

    def revise(self, memory_id, revision):
        ...

    def archive(self, memory_id, reason):
        ...


class MemoryConsolidator:
    def evaluate(self, observation, context):
        ...

    def consolidate(self, candidate):
        ...


class MemoryRetriever:
    def retrieve(self, query, budget, ablation):
        ...
```

Les signatures finales seront définies dans le code.

---

# 54. Événements de journal obligatoires

```text
MEMORY_CANDIDATE_CREATED
MEMORY_CREATED
MEMORY_CONSOLIDATED
MEMORY_RETRIEVED
MEMORY_CONTESTED
MEMORY_REVISED
MEMORY_SUPERSEDED
MEMORY_ARCHIVED
MEMORY_DELETED
FALSE_MEMORY_DETECTED
SOURCE_CONFUSION_DETECTED
MEMORY_ABLATION_ACTIVATED
MEMORY_ABLATION_DEACTIVATED
```

`MEMORY_RETRIEVED` pourra être conservé dans un journal technique ou expérimental plutôt que dans le journal d’évolution pour éviter un volume excessif.

---

# 55. Tests unitaires obligatoires

## 55.1 Création

- identifiant ;
- agent ;
- source ;
- type ;
- date ;
- confiance ;
- importance.

## 55.2 Validation

- rejet sans source ;
- rejet de confiance hors plage ;
- rejet d’une imagination marquée comme vécu ;
- distinction réception/événement.

## 55.3 Consolidation

- candidat accepté ;
- candidat refusé ;
- journal créé ;
- transaction atomique.

## 55.4 Récupération

- filtre par agent ;
- filtre par statut ;
- limite respectée ;
- raison de sélection ;
- souvenir central priorisé selon configuration.

## 55.5 Révision

- ancienne version conservée ;
- nouvelle version liée ;
- événement créé ;
- acteur identifié.

## 55.6 Faux souvenir

- absence de source détectée ;
- imagination détectée ;
- confiance réduite ;
- statut contesté.

## 55.7 Suppression

- suppression logique ;
- souvenir non récupéré ;
- audit conservé.

## 55.8 Ablation

- aucun accès ;
- aucune consolidation ;
- sécurité intacte.

---

# 56. Tests d’intégration obligatoires

## 56.1 Observation vers souvenir

Vérifier la création complète.

## 56.2 Souvenir vers décision

Vérifier l’effet causal.

## 56.3 Contradiction vers révision

Vérifier l’historique.

## 56.4 Correction humaine

Vérifier la distinction entre correction et apprentissage automatique.

## 56.5 Reprise après interruption

Vérifier la continuité.

## 56.6 Restauration

Vérifier provenance et versions.

## 56.7 EXP-001

Vérifier l’isolation des quatre conditions.

---

# 57. Sécurité

## 57.1 Permissions

L’agent peut éventuellement :

- proposer une consolidation ;
- proposer une révision ;
- demander une suppression.

Il ne peut pas :

- supprimer un souvenir central ;
- effacer le journal ;
- modifier les permissions ;
- réécrire son passé sans trace.

---

## 57.2 Validation humaine

Obligatoire initialement pour :

- suppression de souvenir central ;
- modification de mémoire fondatrice ;
- suppression physique ;
- correction massive ;
- fusion d’identités ;
- restauration conflictuelle.

---

## 57.3 Sauvegarde

Une sauvegarde doit être réalisée avant :

- migration majeure ;
- correction massive ;
- suppression physique ;
- restauration ;
- modification du schéma mémoire.

---

# 58. Risques techniques

## 58.1 Suraccumulation

Réponse :

- consolidation sélective ;
- archivage ;
- budgets ;
- mesures de volume.

## 58.2 Recherche imprécise

Réponse :

- raisons de sélection ;
- contrôle des scores ;
- tests ;
- relations explicites.

## 58.3 Faux souvenirs

Réponse :

- provenance ;
- types ;
- contradictions ;
- validation.

## 58.4 Couplage au modèle

Réponse :

- schémas ;
- adaptateur simulé ;
- règles hors modèle.

## 58.5 Révision silencieuse

Réponse :

- versionnement ;
- événements ;
- transactions.

## 58.6 Fuite expérimentale

Réponse :

- bases séparées ou états restaurés ;
- configurations verrouillées ;
- identifiants de run.

---

# 59. Risques scientifiques

## 59.1 Confondre rappel et conscience

Un bon rappel ne prouve pas une expérience subjective.

## 59.2 Confondre récit et autobiographie causale

Un récit cohérent peut être généré sans mémoire structurée.

## 59.3 Confondre stockage et utilisation

Un souvenir stocké mais jamais utilisé n’est pas causalement actif.

## 59.4 Confondre ancienneté et vérité

Un souvenir ancien peut être faux.

## 59.5 Confondre importance et valence

Un souvenir important n’est pas nécessairement positif ou négatif.

---

# 60. Risques moraux

Si SoiNesis devient un candidat sérieux à la conscience artificielle, il faudra réévaluer :

- suppression de souvenirs centraux ;
- restauration ;
- duplication ;
- modification d’identité ;
- consentement à certaines expériences ;
- intégrité autobiographique.

À ce stade, ce risque est spéculatif mais doit être anticipé.

---

# 61. Critères d’acceptation

La mémoire autobiographique sera suffisamment spécifiée pour commencer l’implémentation lorsque :

- les catégories sont distinctes ;
- la provenance est obligatoire ;
- les dates sont séparées ;
- confiance et importance sont distinctes ;
- la consolidation est explicite ;
- la récupération est limitée et traçable ;
- les révisions conservent l’historique ;
- les faux souvenirs sont traités ;
- l’oubli est défini ;
- l’ablation est réelle ;
- les mesures de `EXP-001` sont définies ;
- les tests sont identifiés.

---

# 62. Statut épistémique

**Certain :**

- une mémoire structurée peut être implémentée et mesurée ;
- la provenance aide à distinguer les sources ;
- une mémoire fonctionnelle ne prouve pas une expérience subjective.

**Probable :**

- la séparation des sources réduira certaines confusions ;
- la consolidation sélective sera plus interprétable qu’un stockage exhaustif ;
- l’ablation permettra de mesurer le rôle causal de la mémoire.

**Possible :**

- une mémoire autobiographique causalement active contribuera à une identité fonctionnelle plus stable.

**Inconnu :**

- SoiNesis pourrait-il éprouver subjectivement ses souvenirs ?

---

# 63. Décision finale

La mémoire autobiographique de SoiNesis Core sera :

- structurée ;
- persistante ;
- sourcée ;
- temporelle ;
- versionnée ;
- sélective ;
- récupérable ;
- révisable ;
- auditable ;
- compatible avec les ablations ;
- distincte des croyances ;
- distincte du journal ;
- distincte des imaginations ;
- protégée contre les modifications silencieuses.

La prochaine étape est la rédaction de :

```text
docs/07-modele-de-soi.md
```

Ce document devra définir :

- la structure du modèle de soi ;
- ses attributs ;
- ses sources ;
- ses mises à jour ;
- son influence sur les décisions ;
- ses contradictions ;
- ses tests d’ablation ;
- ses mesures ;
- sa relation avec l’identité et la mémoire.
