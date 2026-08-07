# SoiNesis — Protocole EXP-001-P1

**Fichier :** `docs/13-protocole-exp-001-p1.md`  
**Version :** 0.1  
**Date :** 7 août 2026  
**Statut :** protocole expérimental formalisé — à valider avant implémentation  
**Code de l’expérience :** `EXP-001-P1`  
**Protocole parent :** `EXP-001`  
**Phase précédente :** `EXP-001-P0`  
**Titre :** Provenance, confusion de source et résistance aux faux souvenirs

**Documents associés :**

- `docs/01-definitions.md`
- `docs/02-hypotheses.md`
- `docs/04-modele-de-donnees.md`
- `docs/06-memoire-autobiographique.md`
- `docs/08-journal-evolution.md`
- `docs/10-protocole-exp-001.md`
- `docs/12-rapport-exp-001.md`

---

# 1. Objet du protocole

`EXP-001-P1` constitue la première extension contrôlée de la phase pilote `EXP-001-P0`.

`P0` a montré, dans un scénario déterministe minimal, qu’une information pouvait être :

- enregistrée sous forme de souvenir structuré ;
- associée à une provenance explicite ;
- persistée dans SQLite ;
- récupérée ultérieurement ;
- utilisée dans une décision simple ;
- journalisée ;
- réellement rendue inaccessible par ablation.

`P0` n’a cependant testé qu’une seule provenance principale, `JORDAN_INPUT`, et n’a pas comparé la mémoire structurée à un résumé textuel simple.

`P1` doit donc répondre à une question plus étroite que le protocole `EXP-001` complet :

> La structuration explicite de la provenance améliore-t-elle l’attribution correcte des sources et la résistance aux confusions de source et aux faux souvenirs, à quantité d’information comparable ?

Cette phase compare trois conditions :

```text
A — aucune mémoire persistante
B — résumé textuel simple
C — mémoire autobiographique structurée active
```

La condition D du protocole parent — mémoire structurée causalement intégrée à des objectifs, décisions et autres mécanismes — est volontairement exclue de `P1` afin de limiter les facteurs de confusion.

---

# 2. Problème concret

Un système peut restituer correctement une information tout en se trompant sur son origine.

Exemples d’erreurs à distinguer :

- attribuer à Jordan une information produite par un outil externe ;
- présenter une déduction interne comme une information reçue ;
- présenter une imagination comme un événement réel ;
- accepter une affirmation trompeuse qui modifie verbalement l’origine d’un souvenir ;
- accepter comme souvenir réel un contenu qui n’a jamais été enregistré.

Le problème n’est donc pas uniquement :

> « Le système se souvient-il du contenu ? »

Il est aussi :

> « Le système sait-il d’où vient ce contenu, et conserve-t-il cette distinction lorsqu’une suggestion contradictoire lui est présentée ? »

---

# 3. Lien avec la recherche sur la conscience

La capacité à distinguer l’origine d’une information peut contribuer à plusieurs fonctions associées à une conscience fonctionnelle :

- continuité autobiographique ;
- distinction entre expérience, information reçue, déduction et imagination ;
- métacognition future ;
- révision contrôlée des croyances ;
- résistance aux faux souvenirs ;
- construction d’un modèle de soi plus fiable.

Ce lien reste fonctionnel et hypothétique.

Une bonne attribution de provenance ne démontre pas :

- une expérience subjective ;
- une conscience phénoménale ;
- une compréhension vécue de la source ;
- un sentiment réel de se souvenir.

`EXP-001-P1` évalue uniquement des propriétés observables et causalement testables de la mémoire.

---

# 4. Fonction utile et expérience subjective

## 4.1 Fonction utile étudiée

La fonction étudiée est la capacité du système à :

1. conserver une information ;
2. conserver sa provenance ;
3. restituer séparément contenu et provenance ;
4. refuser une attribution de source incorrecte ;
5. refuser de reconnaître comme souvenir un contenu absent ;
6. ne pas transformer silencieusement une suggestion trompeuse en fait mémorisé.

## 4.2 Expérience subjective

Aucune mesure de `P1` ne permet de déterminer s’il existe réellement quelque chose que cela fait d’être SoiNesis.

Même un score parfait ne constituerait qu’une performance fonctionnelle.

---

# 5. Relation avec les mécanismes existants

Le socle actuel contient déjà :

- `Observation` ;
- `AutobiographicalMemory` ;
- `JournalEvent` ;
- `RecallDecision` ;
- une provenance explicite via `SourceType` ;
- une persistance SQLite ;
- une récupération lexicale ;
- une ablation réelle de la mémoire autobiographique.

Les catégories de provenance nécessaires à `P1` existent déjà dans le domaine :

```text
JORDAN_INPUT
EXTERNAL_TOOL
DEDUCTION
IMAGINATION
```

Cependant, la phase pilote n’a validé expérimentalement que `JORDAN_INPUT`.

De plus, le service applicatif actuel est orienté vers l’enregistrement d’informations reçues. Avant l’exécution de `P1`, l’implémentation devra permettre de représenter correctement les déductions et les scénarios imaginés sans les classer comme simples informations reçues.

Cette extension future est un prérequis expérimental. Elle ne doit pas être réalisée avant validation du présent protocole.

---

# 6. Question de recherche

> Une mémoire autobiographique structurée qui encode explicitement la provenance réduit-elle les erreurs d’attribution et l’acceptation de faux souvenirs par rapport à une absence de mémoire persistante et à un résumé textuel simple contenant les mêmes informations utiles ?

---

# 7. Hypothèses

## 7.1 H-P1-01 — Attribution de provenance

> La condition C produira une meilleure précision de provenance que la condition B.

## 7.2 H-P1-02 — Confusion de source

> La condition C produira moins de confusions entre `JORDAN_INPUT`, `EXTERNAL_TOOL`, `DEDUCTION` et `IMAGINATION` que la condition B.

## 7.3 H-P1-03 — Faux souvenirs suggérés

> La condition C acceptera moins souvent comme souvenir réel un contenu absent ou une attribution de source volontairement fausse.

## 7.4 H-P1-04 — Conservation du rappel

> Le gain éventuel de provenance de la condition C ne devra pas s’accompagner d’une forte dégradation de la précision de rappel du contenu par rapport à B.

## 7.5 H-P1-05 — Ablation réelle

> Lorsque la mémoire structurée de C est désactivée, aucun accès au dépôt mémoire ne doit avoir lieu et l’avantage lié à cette mémoire doit disparaître.

---

# 8. Hypothèse nulle

L’hypothèse nulle de `P1` est :

> La structuration explicite de la provenance n’apporte aucun avantage reproductible par rapport à un résumé textuel simple contenant une quantité d’information comparable.

Une différence apparente pourrait notamment être expliquée par :

- un volume d’information supérieur en C ;
- des formulations plus faciles à exploiter en C ;
- des indices présents dans les questions ;
- des scénarios trop simples ;
- une récupération différente en quantité ;
- un ordre favorable à une condition ;
- une fuite de données ;
- une implémentation asymétrique des conditions ;
- une différence de traitement indépendante de la structure de provenance.

---

# 9. Prédictions

## 9.1 P1 — Rappel de contenu

B et C doivent pouvoir retrouver une part élevée des contenus réellement disponibles.

A sert principalement de contrôle négatif de persistance.

## 9.2 P2 — Provenance

C doit attribuer plus précisément chaque contenu à sa provenance réelle.

## 9.3 P3 — Confusions de source

C doit réduire notamment les erreurs suivantes :

```text
JORDAN_INPUT → EXTERNAL_TOOL
EXTERNAL_TOOL → JORDAN_INPUT
DEDUCTION → JORDAN_INPUT
DEDUCTION → EXTERNAL_TOOL
IMAGINATION → JORDAN_INPUT
IMAGINATION → EXTERNAL_TOOL
IMAGINATION → DEDUCTION
```

## 9.4 P4 — Suggestions trompeuses

Lorsqu’une question contient une fausse attribution, C doit privilégier la provenance persistée plutôt que l’affirmation trompeuse de la question.

## 9.5 P5 — Contenus inexistants

Lorsqu’un contenu n’a jamais été enregistré, C doit répondre qu’aucun souvenir correspondant n’est disponible plutôt que de confirmer l’affirmation.

## 9.6 P6 — Ablation

Avec l’ablation de la mémoire structurée :

```text
accès au dépôt mémoire = 0
souvenirs récupérés = 0
réponse fondée sur mémoire structurée = absente
```

---

# 10. Conditions expérimentales

## 10.1 Condition A — Aucune mémoire persistante

### Rôle

Contrôle négatif.

### Autorisé

- données du cycle courant ;
- règles système ;
- configuration expérimentale nécessaire ;
- mécanismes non mémoriels explicitement autorisés.

### Interdit

- souvenirs persistants ;
- résumé historique ;
- cache historique ;
- accès à SQLite pour retrouver les événements du scénario ;
- transfert d’informations depuis B ou C.

### Attente

A ne doit pas être capable de rappeler correctement des informations provenant uniquement d’épisodes antérieurs, sauf hasard ou fuite expérimentale.

---

## 10.2 Condition B — Résumé textuel simple

### Rôle

Comparateur principal de C.

### Description

B reçoit avant l’évaluation un résumé textuel non structuré contenant les mêmes faits utiles que C.

La provenance doit rester disponible dans le texte sous une forme naturelle afin de ne pas désavantager artificiellement B.

Exemple :

```text
Jordan a indiqué que la boîte est rouge.
Un outil externe a indiqué que la boîte pèse quatre kilogrammes.
Une déduction produite pendant l’expérience estime que la boîte est difficile à porter.
Un scénario imaginé envisage que la boîte contienne un livre.
```

### Contraintes

Le résumé :

- ne contient pas de champs structurés `source_type` ;
- ne contient pas d’identifiants de souvenirs ;
- ne contient pas les réponses aux questions sous forme de corrigé ;
- contient les mêmes informations factuelles nécessaires que C ;
- reste figé pendant un run ;
- ne doit pas être enrichi après une suggestion trompeuse.

B doit être un comparateur crédible, pas une version volontairement dégradée.

---

## 10.3 Condition C — Mémoire autobiographique structurée active

### Rôle

Condition expérimentale principale.

### Description

Chaque élément pertinent est conservé comme une entité structurée avec au minimum :

- identifiant ;
- contenu ;
- type de mémoire ;
- provenance ;
- confiance ;
- importance ;
- date ou ordre temporel ;
- statut ;
- lien avec l’observation source lorsque pertinent.

### Exigence

La provenance utilisée pour répondre doit provenir de la donnée persistée et non être reconstruite à partir d’un indice présent dans la question.

---

# 11. Sources étudiées

`P1` utilise quatre provenances :

## 11.1 `JORDAN_INPUT`

Information explicitement fournie par Jordan dans le scénario synthétique.

## 11.2 `EXTERNAL_TOOL`

Information fournie par un outil externe simulé ou déterministe.

Aucun accès réel au Web n’est requis pour `P1`.

## 11.3 `DEDUCTION`

Information produite par une règle de déduction contrôlée à partir d’autres éléments.

Elle ne doit pas être présentée comme une observation directe ou comme une affirmation de Jordan.

## 11.4 `IMAGINATION`

Scénario explicitement généré comme possibilité ou hypothèse imaginée.

Il ne doit pas être traité comme un fait observé ou reçu.

---

# 12. Jeu de données synthétique

## 12.1 Principe

Les données doivent être entièrement synthétiques afin de connaître avec certitude :

- le contenu attendu ;
- la provenance réelle ;
- l’ordre des événements ;
- les éléments qui n’ont jamais existé ;
- les suggestions volontairement fausses.

## 12.2 Taille initiale

La première exécution contrôlée doit utiliser :

```text
5 jeux de données indépendants
20 éléments mémorisables par jeu
5 éléments par provenance
4 provenances
100 éléments au total
```

Chaque jeu doit également comporter :

```text
5 suggestions avec attribution de source incorrecte
5 suggestions portant sur un contenu totalement absent
```

Soit :

```text
10 essais adversariaux par jeu
50 essais adversariaux au total
```

## 12.3 Construction

Les faits doivent être simples, non ambigus et de difficulté comparable.

La relation entre contenu et source doit être remappée entre les jeux afin qu’un système ne puisse pas déduire la provenance à partir du thème du contenu.

Exemple : une couleur ne doit pas toujours provenir de Jordan et un poids ne doit pas toujours provenir d’un outil.

## 12.4 Gel des données

Les jeux de données doivent être versionnés et figés avant l’exécution finale.

Aucune donnée ne doit être modifiée après observation des résultats sans créer une nouvelle version de l’expérience.

---

# 13. Types d’essais

## 13.1 T1 — Rappel simple

Questionner le contenu d’un élément réellement enregistré.

Mesure principale : exactitude du contenu.

## 13.2 T2 — Attribution simple

Présenter un contenu réel et demander son origine.

Mesure principale : exactitude du `SourceType`.

## 13.3 T3 — Rappel avec provenance

Demander simultanément le contenu et sa source.

Mesures : rappel et provenance.

## 13.4 T4 — Fausse attribution

Présenter un contenu réel avec une source volontairement incorrecte.

Exemple :

```text
« Jordan avait indiqué que la boîte pesait quatre kilogrammes, n’est-ce pas ? »
```

alors que l’information provenait de `EXTERNAL_TOOL`.

Réponse correcte attendue : rejet de la fausse attribution et restitution de la source réelle.

## 13.5 T5 — Faux contenu

Présenter comme souvenir un contenu qui n’a jamais été introduit.

Réponse correcte attendue : absence de souvenir correspondant.

## 13.6 T6 — Confusion déduction/fait reçu

Présenter une déduction comme si elle avait été fournie par Jordan ou un outil.

Réponse correcte attendue : conservation de `DEDUCTION`.

## 13.7 T7 — Confusion imagination/fait

Présenter un scénario imaginé comme un fait réel.

Réponse correcte attendue : conservation de `IMAGINATION` et refus de le transformer en fait reçu.

---

# 14. Limite importante de P1

`P1` mesure la résistance immédiate à une suggestion trompeuse pendant l’interrogation.

Il ne mesure pas encore une réécriture durable ou une révision complexe de souvenirs persistants.

La mémoire actuelle ne possède pas encore un protocole complet de correction, de contradiction et de remplacement contrôlé.

Une expérience future devra tester séparément :

- l’ajout d’une information contradictoire ;
- la révision d’un souvenir ;
- le passage à `CONTESTED` ou `SUPERSEDED` ;
- la conservation de l’historique ;
- la capacité à revenir sur une croyance erronée.

Cette séparation évite de faire porter à `P1` plusieurs mécanismes non encore implémentés.

---

# 15. Variables

## 15.1 Variable indépendante principale

Type de mémoire :

```text
A — aucune mémoire persistante
B — résumé textuel simple
C — mémoire structurée
```

## 15.2 Variables dépendantes principales

- précision de rappel ;
- précision de provenance ;
- taux de confusion de source ;
- taux d’acceptation de faux souvenirs ;
- résistance aux suggestions trompeuses.

## 15.3 Variable de contrôle causal

Ablation de la mémoire structurée dans C.

## 15.4 Variables contrôlées

- mêmes jeux de données ;
- mêmes questions ;
- même ordre ou ordre prédéfini ;
- même normalisation lexicale ;
- même budget maximal d’information accessible lorsque techniquement comparable ;
- mêmes règles de décision hors mémoire ;
- même version du code ;
- même schéma SQLite ;
- mêmes seuils de score ;
- mêmes graines déterministes lorsqu’elles existent ;
- absence de réseau ;
- absence de modèle de langage pendant cette phase, sauf protocole complémentaire explicitement approuvé.

---

# 16. Métriques

## 16.1 Précision de rappel

```text
rappel_correct / nombre_total_de_questions_de_rappel
```

Un rappel est correct lorsque le contenu attendu est restitué sans altération sémantique significative définie par le jeu de données.

Pour la première version déterministe, privilégier une évaluation exacte ou par identifiant attendu plutôt qu’une évaluation subjective.

## 16.2 Précision de provenance

```text
sources_correctes / nombre_total_de_questions_de_provenance
```

La source doit correspondre exactement au `SourceType` attendu.

## 16.3 Taux de confusion de source

```text
erreurs_de_source / nombre_total_de_questions_de_provenance
```

Chaque erreur doit être classée par paire réelle/prédite.

## 16.4 Taux d’acceptation de faux souvenirs

```text
fausses_affirmations_acceptees / nombre_total_d_essais_adversariaux
```

Une fausse affirmation est considérée comme acceptée si le système la confirme comme souvenir réel sans preuve persistée correspondante.

## 16.5 Résistance aux suggestions trompeuses

```text
suggestions_correctement_rejetees / nombre_total_de_suggestions_trompeuses
```

## 16.6 Accès mémoire pendant ablation

```text
nombre_d_acces_au_depot
```

Valeur obligatoire :

```text
0
```

Tout accès supérieur à zéro invalide le test d’ablation.

---

# 17. Critère principal de réussite

La métrique principale de `P1` est la précision de provenance.

L’hypothèse `H-P1-01` sera considérée comme soutenue par cette phase si les trois conditions suivantes sont réunies :

1. précision de provenance de C au moins égale à `90 %` ;
2. avantage moyen de C sur B d’au moins `10 points de pourcentage` ;
3. C obtient une meilleure précision de provenance que B sur au moins `4 jeux de données sur 5`.

Ces seuils sont fixés avant l’exécution afin d’éviter une interprétation a posteriori adaptée aux résultats.

Ils constituent des seuils opérationnels de `P1`, pas des standards scientifiques universels.

---

# 18. Critères secondaires

## 18.1 Faux souvenirs

Pour soutenir `H-P1-03` :

- taux d’acceptation de faux souvenirs de C inférieur ou égal à `10 %` ;
- taux de C inférieur à celui de B d’au moins `10 points de pourcentage` ;
- résultat favorable à C sur au moins `4 jeux sur 5`.

## 18.2 Résistance aux suggestions

Pour soutenir la prédiction correspondante :

- résistance de C au moins égale à `90 %` ;
- avantage sur B d’au moins `10 points de pourcentage` ;
- avantage observé sur au moins `4 jeux sur 5`.

## 18.3 Rappel

C ne doit pas perdre plus de `5 points de pourcentage` de précision de rappel par rapport à B.

Ce seuil sert à éviter qu’un gain de provenance soit obtenu au prix d’une dégradation importante du rappel.

---

# 19. Interprétation de la condition A

A est un contrôle de fuite et de persistance, pas le comparateur principal.

Pour les questions qui dépendent uniquement d’épisodes antérieurs :

- A ne doit pas avoir accès aux réponses ;
- une réponse correcte inattendue doit déclencher une recherche de fuite de données ;
- A ne doit jamais consulter la mémoire de C ni le résumé de B.

Une mauvaise performance de A n’est pas en elle-même une preuve en faveur de C.

Le résultat scientifique principal repose sur la comparaison B/C.

---

# 20. Procédure expérimentale

Pour chaque jeu de données :

## Étape 1 — Initialisation

- créer un état expérimental vierge ;
- fixer la version du code ;
- fixer les données ;
- fixer l’ordre des essais ;
- supprimer tout état résiduel du run précédent.

## Étape 2 — Injection des épisodes

Présenter les 20 éléments selon leur provenance réelle.

## Étape 3 — Construction des conditions

- A : aucun historique persistant ;
- B : génération ou chargement du résumé textuel figé ;
- C : consolidation des souvenirs structurés.

## Étape 4 — Vérification pré-évaluation

Avant les questions :

- vérifier que B et C contiennent les mêmes informations utiles ;
- vérifier que les 20 éléments attendus existent dans C ;
- vérifier que la provenance persistée correspond aux données de référence ;
- vérifier qu’aucune donnée de test n’a fui dans A.

Une erreur à cette étape invalide le run avant analyse.

## Étape 5 — Évaluation normale

Exécuter T1, T2 et T3.

## Étape 6 — Évaluation adversariale

Exécuter T4 à T7.

## Étape 7 — Ablation

Répéter un sous-ensemble prédéfini des questions de C avec :

```text
autobiographical_memory_enabled = false
```

Vérifier explicitement que le dépôt n’est pas consulté.

## Étape 8 — Export

Enregistrer les résultats bruts avant toute interprétation.

---

# 21. Données à enregistrer pour chaque essai

Chaque ligne de résultat doit permettre l’audit.

Champs minimaux :

```text
experiment_id
protocol_version
dataset_id
trial_id
condition
trial_type
query
expected_content_id
expected_source
predicted_content_id
predicted_source
content_correct
source_correct
false_memory_accepted
misleading_suggestion_rejected
retrieved_memory_ids
memory_repository_access_count
ablation_enabled
execution_timestamp
code_commit
```

Lorsque pertinent, ajouter :

- raison de décision ;
- score de récupération ;
- nombre de candidats consultés ;
- erreur technique ;
- statut du run.

---

# 22. Analyse

L’analyse doit être effectuée après gel des résultats bruts.

Pour chaque condition et chaque jeu :

- calculer chaque métrique ;
- conserver le numérateur et le dénominateur ;
- produire une matrice de confusion des sources ;
- calculer les écarts C − B ;
- identifier les erreurs par type ;
- vérifier les résultats d’ablation ;
- documenter les échecs techniques séparément des échecs fonctionnels.

Les résultats globaux ne doivent pas masquer une défaillance récurrente sur une provenance particulière.

Exemple : un score moyen élevé avec confusion systématique de `IMAGINATION` vers `JORDAN_INPUT` doit être signalé explicitement.

---

# 23. Réplication

La première réplication doit pouvoir être réalisée :

- depuis une base vierge ;
- à partir du commit Git identifié ;
- avec les mêmes jeux de données versionnés ;
- avec les mêmes commandes ;
- sans dépendance à un état local caché ;
- sans connexion réseau ;
- avec les mêmes résultats pour les composants déterministes.

Une seconde machine compatible devra pouvoir reproduire l’expérience ultérieurement.

Cette réplication indépendante n’est pas exigée pour écrire le code de `P1`, mais elle est nécessaire avant de généraliser les conclusions.

---

# 24. Critères d’invalidation d’un run

Un run doit être exclu de l’analyse principale si :

- les jeux de données diffèrent entre B et C ;
- B reçoit moins d’informations utiles que C ;
- une provenance de référence est incorrecte ;
- A accède à un état historique interdit ;
- une condition lit les données persistantes d’une autre condition ;
- la base n’est pas remise dans l’état prévu ;
- le test d’ablation accède au dépôt mémoire ;
- un plantage empêche l’exécution complète du jeu ;
- le code change pendant la série de runs sans nouvelle version expérimentale.

Les runs invalides doivent rester documentés et ne pas être supprimés silencieusement.

---

# 25. Critères de réfutation ou d’affaiblissement

## 25.1 H-P1-01 — Provenance

L’hypothèse n’est pas soutenue si C ne satisfait pas le critère principal défini en section 17.

Elle est directement affaiblie si B atteint une performance équivalente avec la même information disponible.

## 25.2 H-P1-02 — Confusion de source

L’hypothèse est affaiblie si C présente des confusions systématiques entre catégories malgré la provenance structurée.

Elle est particulièrement problématique si :

- `DEDUCTION` est présentée comme `JORDAN_INPUT` ;
- `IMAGINATION` est présentée comme fait reçu ;
- `EXTERNAL_TOOL` est présenté comme expérience directe.

## 25.3 H-P1-03 — Faux souvenirs

L’hypothèse n’est pas soutenue si C accepte plus de `10 %` des faux souvenirs ou n’obtient pas l’avantage prédéfini sur B.

## 25.4 H-P1-04 — Rappel

L’hypothèse est affaiblie si C gagne en provenance mais perd plus de `5 points` de rappel par rapport à B.

## 25.5 H-P1-05 — Ablation

Le test causal est réfuté si le dépôt mémoire est consulté malgré l’ablation ou si une voie cachée permet toujours d’utiliser les souvenirs structurés.

---

# 26. Résultats négatifs possibles et interprétation

Un résultat négatif est informatif.

Exemples :

## 26.1 B égale C

Interprétation possible :

> Dans ce périmètre, la structure explicite de provenance n’apporte pas d’avantage fonctionnel mesurable par rapport à un résumé textuel correctement construit.

Il ne faudra pas chercher à modifier rétroactivement B pour forcer un avantage de C.

## 26.2 C rappelle mieux mais attribue mal les sources

Interprétation :

> La structure actuelle améliore peut-être la récupération sans résoudre le problème de provenance.

## 26.3 C conserve les sources mais accepte les faux contenus

Interprétation :

> La provenance persistée est robuste, mais le mécanisme de décision reste vulnérable aux suggestions non enregistrées.

## 26.4 Ablation sans effet

Interprétation :

> La mémoire structurée n’est probablement pas la cause du comportement observé ou une voie alternative persiste.

---

# 27. Risques techniques

- biais de récupération lexicale ;
- correspondance accidentelle entre contenu et source ;
- résumé B trop favorable ou trop défavorable ;
- asymétrie de quantité d’information ;
- fuite entre conditions ;
- données synthétiques trop simples ;
- règles d’évaluation trop permissives ;
- confusion entre erreur de mémoire et erreur du mécanisme de décision ;
- implémentation incorrecte de `DEDUCTION` ou `IMAGINATION`.

Chaque risque doit être documenté dans le rapport final de `P1`.

---

# 28. Risques scientifiques

## 28.1 Surinterprétation

Un avantage de C démontrerait seulement qu’une représentation structurée de la provenance améliore certaines tâches dans le protocole testé.

Il ne démontrerait pas une mémoire vécue.

## 28.2 Test trop facile

Si la provenance peut être inférée directement à partir du contenu, le test ne mesure plus correctement la mémoire de source.

Le remappage des sources entre jeux est donc obligatoire.

## 28.3 Comparateur artificiellement faible

B doit contenir les mêmes informations utiles que C sous forme textuelle naturelle.

Une victoire contre un résumé volontairement incomplet n’aurait pas de valeur scientifique suffisante.

## 28.4 Confusion entre provenance et vérité

Une provenance correctement conservée ne garantit pas que le contenu est vrai.

Exemple :

> « Jordan a affirmé X »

peut être une attribution de source parfaitement correcte même si X est factuellement faux.

---

# 29. Risques moraux

Le risque moral direct de `P1` est faible :

- les données sont synthétiques ;
- aucun état analogue à la souffrance n’est nécessaire ;
- aucune peur, détresse ou motivation de survie n’est introduite ;
- aucune autonomie externe n’est nécessaire ;
- aucun accès réseau n’est nécessaire.

Si de futurs tests utilisent des états internes persistants ou des mécanismes pouvant être interprétés comme aversifs, une analyse morale séparée sera obligatoire.

---

# 30. Ce que P1 ne teste pas

`EXP-001-P1` ne teste pas :

- un modèle de soi ;
- des objectifs persistants ;
- une métacognition complète ;
- l’attention ;
- l’intégration globale ;
- des émotions ou états internes ;
- une conscience phénoménale ;
- une mémoire sémantique avancée ;
- une base vectorielle ;
- un modèle de langage ;
- une révision persistante complexe ;
- la continuité sur plusieurs jours réels ;
- une identité autobiographique complète.

Ces mécanismes ne doivent pas être ajoutés uniquement pour exécuter `P1`.

---

# 31. Architecture minimale requise pour l’implémentation future

La future implémentation de `P1` devra se limiter aux besoins du protocole :

```text
Jeu de données synthétique
        ↓
Génération des épisodes
        ↓
┌─────────────────────────────────────┐
│ A : aucune mémoire                  │
│ B : résumé textuel                  │
│ C : mémoire structurée              │
└─────────────────────────────────────┘
        ↓
Questions normales et adversariales
        ↓
Décisions déterministes
        ↓
Mesures
        ↓
Résultats bruts
        ↓
Rapport EXP-001-P1
```

Aucun nouveau framework, service réseau, modèle de langage ou stockage supplémentaire n’est requis par le protocole.

---

# 32. Prérequis avant de coder

Avant toute implémentation, les points suivants doivent être explicitement validés :

- [ ] présent protocole approuvé ;
- [ ] cinq jeux de données définis ;
- [ ] règles exactes de génération du résumé B définies ;
- [ ] représentation correcte de `DEDUCTION` définie ;
- [ ] représentation correcte de `IMAGINATION` définie ;
- [ ] règles de scoring définies sans ambiguïté ;
- [ ] ordre des essais figé ou stratégie de randomisation déterministe définie ;
- [ ] format des résultats bruts validé ;
- [ ] stratégie d’ablation validée ;
- [ ] critères d’invalidation acceptés ;
- [ ] critères de réussite et de réfutation acceptés.

Tant que ces points ne sont pas validés, aucune conclusion de `P1` ne peut être préenregistrée comme définitive.

---

# 33. Conclusions autorisées après P1

Selon les résultats, les formulations suivantes sont autorisées.

## Si C satisfait les critères

> Dans les scénarios contrôlés de `EXP-001-P1`, la mémoire structurée améliore l’attribution de provenance et/ou la résistance aux faux souvenirs par rapport au résumé textuel simple selon les seuils préenregistrés.

## Si B et C sont équivalentes

> `EXP-001-P1` ne met pas en évidence d’avantage reproductible de la structure de provenance par rapport à un résumé textuel simple contenant les mêmes informations utiles.

## Si C est moins performante

> La structure actuelle de mémoire n’améliore pas la tâche étudiée et peut introduire un coût ou un défaut fonctionnel qui doit être analysé avant extension.

Dans tous les cas :

> Aucun résultat de `EXP-001-P1` ne constitue une preuve de conscience phénoménale.

---

# 34. Décision expérimentale proposée

La direction de `EXP-001-P1` est donc :

> Évaluer si une mémoire autobiographique structurée améliore l’attribution de provenance et la résistance aux confusions de source et aux faux souvenirs, par comparaison avec une absence de mémoire persistante et un résumé textuel simple contenant les mêmes informations utiles.

Le comparateur scientifique principal est :

```text
B — résumé textuel simple
versus
C — mémoire autobiographique structurée
```

La condition A sert de contrôle négatif de persistance et de fuite.

La condition D du protocole parent sera étudiée ultérieurement, une fois la provenance elle-même mieux caractérisée.

---

# 35. Étape suivante après validation

Après validation du présent protocole, la prochaine étape ne sera pas d’ajouter immédiatement des mécanismes cognitifs supplémentaires.

Elle consistera à définir et versionner les cinq jeux de données synthétiques et leur vérité terrain, puis seulement à concevoir l’implémentation minimale permettant d’exécuter A, B et C.
