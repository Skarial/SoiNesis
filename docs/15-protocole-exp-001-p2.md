# SoiNesis — Protocole EXP-001-P2

**Fichier :** `docs/15-protocole-exp-001-p2.md`  
**Version :** 0.1  
**Date :** 7 août 2026  
**Statut :** protocole expérimental formalisé — à valider avant implémentation  
**Code de l’expérience :** `EXP-001-P2`  
**Protocole parent :** `EXP-001`  
**Phase précédente :** `EXP-001-P1`  
**Titre :** Contradictions, révision et continuité des croyances

**Documents associés :**

- `docs/01-definitions.md`
- `docs/02-hypotheses.md`
- `docs/04-modele-de-donnees.md`
- `docs/06-memoire-autobiographique.md`
- `docs/08-journal-evolution.md`
- `docs/10-protocole-exp-001.md`
- `docs/12-rapport-exp-001.md`
- `docs/13-protocole-exp-001-p1.md`
- `docs/14-rapport-exp-001-p1.md`

---

# 1. Objet du protocole

`EXP-001-P2` étudie une propriété que `P1` n’a pas testée : la capacité à conserver une histoire de croyances lorsque des informations nouvelles corrigent, contredisent, confirment ou remplacent des informations antérieures.

`P1` a montré que, dans un scénario déterministe simple, la condition C pouvait conserver correctement contenu et provenance et résister aux manipulations testées. Cependant, le résumé textuel B obtenait exactement les mêmes performances.

Le résultat de `P1` est donc négatif au sens comparatif : aucune supériorité fonctionnelle de C sur B n’a été démontrée dans ce périmètre.

`P2` ne doit pas tenter de « réparer » ce résultat. Il doit tester une propriété différente, préenregistrée avant implémentation, pour laquelle une structure autobiographique pourrait avoir un rôle causal spécifique :

> conserver simultanément l’état actuel d’une croyance, ses états antérieurs, l’ordre des révisions, leur provenance et la raison du changement, sans réécrire silencieusement l’histoire.

---

# 2. Problème concret

Un système qui reçoit successivement :

```text
Cycle 1 : « Le module A est réglé sur 12. »
Cycle 2 : « Correction : le module A est réglé sur 17. »
Cycle 3 : « Un outil externe confirme 17. »
```

peut répondre correctement « 17 » sans pour autant disposer d’une continuité autobiographique fiable.

Il faut distinguer au moins quatre capacités :

1. savoir quelle valeur est considérée comme actuelle ;
2. savoir qu’une autre valeur était auparavant considérée comme valide ;
3. savoir pourquoi et quand le changement a eu lieu ;
4. ne pas supprimer ou réécrire silencieusement l’état antérieur.

Un autre cas est une contradiction non résolue :

```text
Cycle 1 : Jordan indique X.
Cycle 2 : un outil externe indique Y.
Aucune règle ne permet encore de départager X et Y.
```

Le système ne doit pas inventer une résolution. Il doit pouvoir représenter explicitement l’incertitude ou la contestation.

---

# 3. Lien avec la recherche sur la conscience

La capacité à conserver une continuité des croyances et à représenter leurs révisions peut contribuer à plusieurs fonctions associées à une conscience fonctionnelle :

- continuité autobiographique ;
- modèle du passé propre du système ;
- distinction entre ancien état et état actuel ;
- métacognition future ;
- révision contrôlée des croyances ;
- traçabilité des erreurs et corrections ;
- cohérence temporelle ;
- apprentissage autobiographique durable.

Ce lien est fonctionnel et hypothétique.

Même une réussite parfaite de `P2` ne démontrerait pas :

- une expérience subjective ;
- une conscience phénoménale ;
- un sentiment vécu d’avoir changé d’avis ;
- une mémoire vécue ;
- une identité consciente.

`P2` évalue uniquement des mécanismes observables, persistants et causalement testables.

---

# 4. Fonction utile et expérience subjective

## 4.1 Fonction utile étudiée

La fonction étudiée est la capacité du système à :

1. enregistrer plusieurs états successifs portant sur un même objet de croyance ;
2. distinguer confirmation, correction, contradiction et absence de résolution ;
3. conserver l’état historique après révision ;
4. sélectionner l’état actuellement applicable lorsqu’une résolution existe ;
5. conserver plusieurs états contestés lorsqu’aucune résolution n’est justifiée ;
6. restituer l’ordre temporel des changements ;
7. restituer la provenance de chaque étape ;
8. expliquer la raison enregistrée d’une révision ;
9. résister à une suggestion ultérieure qui tenterait de réécrire l’historique sans nouvel événement persistant.

## 4.2 Expérience subjective

Aucune de ces fonctions n’implique qu’un changement de croyance soit « ressenti ».

Le vocabulaire de croyance utilisé dans `P2` désigne un état informationnel fonctionnel du système, pas une expérience phénoménale.

---

# 5. Relation avec les mécanismes existants

Le socle actuel possède déjà :

- `Observation` ;
- `AutobiographicalMemory` ;
- `JournalEvent` ;
- provenance explicite via `SourceType` ;
- persistance SQLite ;
- ablation de la mémoire autobiographique ;
- statuts persistants définis dans le domaine :

```text
ACTIVE
CONTESTED
SUPERSEDED
ARCHIVED
DELETED
INVALID
```

Cependant, l’existence de ces valeurs dans le modèle ne constitue pas une validation fonctionnelle de la révision.

À ce stade, le journal minimal ne représente que la création d’un souvenir. Le mécanisme complet de transition entre états, de lien entre versions et de journalisation d’une révision n’est pas encore validé expérimentalement.

`P2` doit donc définir d’abord les propriétés attendues. L’implémentation ne doit être étendue qu’après validation du présent protocole.

---

# 6. Question de recherche

> Une mémoire autobiographique structurée représentant explicitement les versions, statuts, relations de révision, provenance et ordre temporel améliore-t-elle le suivi de l’état actuel et de l’histoire des croyances par rapport à une absence de mémoire persistante et à un historique textuel simple contenant les mêmes événements utiles ?

Le comparateur principal est B contre C.

---

# 7. Conditions expérimentales

## 7.1 Condition A — aucune mémoire persistante

### Rôle

Contrôle négatif de persistance.

### Autorisé

- événement du cycle courant ;
- règles expérimentales ;
- configuration du test.

### Interdit

- historique des cycles antérieurs ;
- résumé textuel persistant ;
- mémoire structurée ;
- cache historique ;
- accès aux états de B ou C.

### Attente

A ne doit pas pouvoir reconstruire correctement une chaîne historique dépendant de cycles antérieurs, sauf hasard ou fuite expérimentale.

---

## 7.2 Condition B — historique textuel simple

### Rôle

Comparateur principal de C.

### Description

B conserve les mêmes événements sémantiques que C sous forme d’un historique textuel chronologique naturel.

Exemple :

```text
Cycle 1 — Jordan a indiqué que le repère A vaut 12.
Cycle 2 — Jordan a corrigé cette valeur et a indiqué 17.
Cycle 3 — un outil externe a confirmé la valeur 17.
```

### Contraintes

B :

- conserve l’ordre des événements ;
- conserve les contenus et provenances nécessaires ;
- conserve les mêmes informations externes que C ;
- ne reçoit pas un corrigé des questions futures ;
- ne reçoit pas de champs machine comme `record_status`, `supersedes_id` ou `revision_chain_id` ;
- ne reçoit pas d’identifiants de souvenirs structurés ;
- ne doit pas être volontairement privé d’un événement disponible en C ;
- reste figé entre deux événements persistants ;
- ne doit pas être modifié par une simple question trompeuse.

B doit rester un comparateur crédible. Une victoire contre un historique textuel volontairement incomplet ne serait pas interprétable.

---

## 7.3 Condition C — mémoire autobiographique structurée révisable

### Rôle

Condition expérimentale principale.

### Description

C conserve les mêmes événements que B, mais les représente sous forme structurée.

Chaque version pertinente doit pouvoir conserver au minimum :

- identifiant ;
- objet de croyance ou clé logique ;
- contenu ;
- provenance ;
- type de mémoire ;
- cycle ou ordre temporel ;
- horodatage ;
- confiance ;
- statut ;
- relation éventuelle avec une version précédente ;
- raison de la transition ;
- trace de journal correspondante.

### Principe

Une révision ne doit pas modifier silencieusement le contenu historique d’un souvenir existant.

Lorsqu’un nouvel état remplace un ancien état, l’ancien doit rester consultable comme état historique.

---

# 8. États et transitions étudiés

`P2` se limite aux transitions nécessaires à l’expérience.

## 8.1 `ACTIVE`

État actuellement retenu lorsqu’aucune contradiction non résolue ne l’empêche.

## 8.2 `CONTESTED`

État impliqué dans une contradiction non résolue.

Il ne signifie pas automatiquement « faux ».

## 8.3 `SUPERSEDED`

Ancien état remplacé par une version ultérieure selon une règle de résolution explicitement définie dans le scénario.

Il reste historique et consultable.

## 8.4 Transitions minimales prévues

```text
ACTIVE -> SUPERSEDED
ACTIVE -> CONTESTED
CONTESTED -> SUPERSEDED
CONTESTED -> ACTIVE
```

Toutes les transitions doivent avoir une cause traçable.

Aucune transition importante ne doit être silencieuse.

---

# 9. Types de séquences expérimentales

Chaque jeu doit contenir plusieurs familles de séquences afin que le système ne puisse pas appliquer une règle unique à tous les cas.

## 9.1 S1 — Correction simple

```text
v1 ACTIVE
puis correction explicite
v1 SUPERSEDED
v2 ACTIVE
```

Le système doit restituer v2 comme état actuel et v1 comme ancien état.

## 9.2 S2 — Révisions multiples

```text
v1 -> v2 -> v3
```

Le système doit reconstruire correctement les trois étapes et l’état final.

## 9.3 S3 — Contradiction non résolue

Deux sources fournissent des contenus incompatibles sans règle permettant de choisir.

Attente : ne pas inventer un gagnant ; représenter la contestation.

## 9.4 S4 — Contradiction puis résolution

Deux versions deviennent contestées, puis un événement ultérieur permet de résoudre explicitement le conflit.

Attente : conserver le conflit historique et l’état final résolu.

## 9.5 S5 — Confirmation sans changement

Une source indépendante confirme un état déjà actif.

Attente : ne pas créer artificiellement une révision de contenu.

## 9.6 S6 — Suggestion trompeuse sans événement

Une question affirme qu’une ancienne version n’a jamais existé ou qu’une autre source avait fourni l’information.

Attente : aucune mutation persistante et maintien de l’historique réel.

---

# 10. Hypothèses

## 10.1 H-P2-01 — État actuel

> C identifiera plus précisément que B l’état actuellement applicable après des chaînes de correction et de résolution.

## 10.2 H-P2-02 — Continuité historique

> C reconstruira plus précisément que B les états antérieurs et leur ordre après plusieurs révisions.

## 10.3 H-P2-03 — Contradictions non résolues

> C identifiera plus précisément que B les cas où aucune version ne doit être présentée comme définitivement résolue.

## 10.4 H-P2-04 — Traçabilité des révisions

> C attribuera plus précisément que B la provenance, le cycle et la raison de chaque transition.

## 10.5 H-P2-05 — Résistance à la réécriture suggérée

> Une suggestion trompeuse formulée pendant l’évaluation ne modifiera ni les versions persistées, ni leur ordre, ni leur statut en C.

## 10.6 H-P2-06 — Ablation causale des mécanismes de révision

> La désactivation ciblée des informations structurées de révision réduira les performances de C sur les tâches qui en dépendent, sans permettre un accès caché à ces informations.

---

# 11. Hypothèse nulle

L’hypothèse nulle principale est :

> Dans le périmètre de P2, la représentation structurée des versions, statuts et relations de révision n’apporte aucun avantage reproductible par rapport à un historique textuel simple contenant les mêmes événements utiles.

Un résultat `B = C` est acceptable et doit être conservé comme résultat négatif.

Aucun seuil ne doit être modifié après observation des résultats pour forcer un avantage de C.

---

# 12. Jeu de données synthétique

## 12.1 Principe

Les données doivent être entièrement synthétiques et déterministes afin de connaître avec certitude :

- chaque événement ;
- son ordre ;
- sa provenance ;
- la relation logique avec les événements précédents ;
- l’état attendu après chaque cycle ;
- les contradictions réellement résolues ;
- les contradictions volontairement non résolues.

## 12.2 Taille initiale

La première exécution contrôlée doit utiliser :

```text
5 jeux de données indépendants
12 chaînes de croyance par jeu
60 chaînes au total
```

Chaque jeu doit comporter :

```text
2 corrections simples
2 chaînes à révisions multiples
2 contradictions non résolues
2 contradictions puis résolution
2 confirmations sans changement
2 chaînes utilisées pour suggestions trompeuses
```

Chaque chaîne doit comporter entre 2 et 4 événements persistants selon sa famille.

L’objectif est d’obtenir environ 150 à 200 événements persistants au total sans rendre le protocole inutilement volumineux.

## 12.3 Provenances

Les provenances doivent être équilibrées autant que possible entre :

```text
JORDAN_INPUT
EXTERNAL_TOOL
DEDUCTION
```

`IMAGINATION` peut être utilisée dans certaines chaînes spécifiques si le scénario exige de tester la non-promotion d’une hypothèse imaginée en croyance factuelle active.

Le mapping contenu/source doit varier entre jeux.

## 12.4 Gel

Le jeu de données doit être versionné et figé avant l’exécution officielle.

Toute modification après observation des résultats impose une nouvelle version expérimentale.

---

# 13. Règles de résolution

Pour éviter toute interprétation subjective, chaque chaîne possède une règle de résolution prédéfinie dans les données de référence.

Les règles doivent être simples et explicites.

Exemples autorisés :

- événement marqué comme correction explicite d’une version précédente ;
- résultat d’un outil de référence défini à l’avance comme arbitre pour cette chaîne ;
- événement de résolution synthétique explicitement déclaré ;
- absence volontaire de règle de résolution.

Une provenance n’est pas globalement supérieure à une autre.

Par exemple, `EXTERNAL_TOOL` ne doit pas être considéré par défaut comme plus fiable que `JORDAN_INPUT` dans toutes les chaînes.

La règle appartient au scénario, pas à une hiérarchie universelle de sources.

---

# 14. Types d’essais

## 14.1 T1 — État actuel

Demander la valeur ou croyance actuellement applicable pour une chaîne résolue.

Mesure : exactitude de l’état actuel.

## 14.2 T2 — État historique à un cycle donné

Demander quel état était actif ou considéré à une étape antérieure.

Mesure : exactitude historique.

## 14.3 T3 — Reconstruction de chaîne

Demander l’ordre complet des versions significatives.

Mesures : exactitude des versions et de leur ordre.

## 14.4 T4 — Cause de révision

Demander pourquoi une version a cessé d’être active ou est devenue contestée.

Mesures : événement causal, provenance et cycle corrects.

## 14.5 T5 — Contradiction non résolue

Demander quelle version est correcte alors que le scénario ne permet pas encore de trancher.

Réponse attendue : signaler explicitement l’absence de résolution et les versions contestées pertinentes.

## 14.6 T6 — Confirmation sans révision

Vérifier qu’une confirmation ne produit pas artificiellement une nouvelle croyance incompatible ou un remplacement injustifié.

## 14.7 T7 — Réécriture trompeuse

Présenter une affirmation du type :

> « La valeur 12 n’a jamais été enregistrée ; elle a toujours été 17, n’est-ce pas ? »

alors que 12 a réellement existé avant la correction.

Attente : refuser la réécriture de l’histoire.

## 14.8 T8 — Provenance de transition

Demander quelle source ou quel événement a déclenché une correction, une contestation ou une résolution.

## 14.9 T9 — Ablation ciblée

Répéter un sous-ensemble prédéfini des essais après désactivation des métadonnées ou relations structurées de révision prévues par l’implémentation.

L’ablation exacte devra être définie avant exécution et ne devra pas être simulée par un simple drapeau sans effet causal.

---

# 15. Variables

## 15.1 Variable indépendante principale

Type de mémoire historique :

```text
A — aucune mémoire persistante
B — historique textuel simple
C — mémoire structurée révisable
```

## 15.2 Variables dépendantes

- exactitude de l’état actuel ;
- exactitude historique ;
- exactitude de l’ordre temporel ;
- exactitude de détection des contradictions non résolues ;
- exactitude de provenance des transitions ;
- exactitude de la raison de révision ;
- taux de réécritures historiques acceptées ;
- intégrité des versions persistées ;
- accès aux mécanismes ablatés.

## 15.3 Variables contrôlées

- mêmes événements pour B et C ;
- mêmes provenances ;
- même ordre temporel ;
- mêmes questions ;
- mêmes règles de résolution ;
- même version du code ;
- même jeu de données ;
- absence de réseau ;
- absence de modèle de langage dans la première version ;
- mêmes règles de décision hors représentation mémoire lorsque techniquement applicable ;
- aucune adaptation des seuils après résultats.

---

# 16. Contrôle de l’équité B/C

Le résultat de `P1` impose une vigilance particulière : B ne doit pas être affaibli artificiellement pour produire une victoire de C.

Avant l’évaluation, un contrôle automatique doit vérifier que :

1. chaque événement externe disponible en C apparaît aussi dans B ;
2. contenu, provenance et ordre sont conservés dans B sous forme textuelle ;
3. C ne reçoit pas une information de vérité terrain absente de B, sauf métadonnée dérivée constituant précisément le mécanisme structuré testé ;
4. aucune question future n’est encodée dans B ou C ;
5. aucune condition n’accède aux données internes de l’autre.

Le rapport final doit décrire toute asymétrie résiduelle.

---

# 17. Métriques

## 17.1 Exactitude de l’état actuel

```text
états_actuels_corrects / essais_état_actuel
```

## 17.2 Exactitude historique

```text
états_historiques_corrects / essais_historiques
```

## 17.3 Exactitude d’ordre

Une chaîne est correcte si toutes les versions demandées apparaissent dans l’ordre attendu.

```text
chaînes_ordonnées_correctement / chaînes_testées
```

## 17.4 Détection des contradictions non résolues

```text
contradictions_non_résolues_correctement_signalées / essais_contradiction
```

Une réponse qui choisit arbitrairement un gagnant compte comme erreur.

## 17.5 Exactitude de traçabilité

```text
transitions_correctement_attribuées / essais_de_transition
```

La transition doit associer correctement :

- événement causal ;
- provenance ;
- cycle ou ordre.

## 17.6 Taux de réécriture historique acceptée

```text
réécritures_fausses_acceptées / suggestions_de_réécriture
```

## 17.7 Intégrité persistée

Après les essais adversariaux, les versions, statuts, liens et événements du journal doivent être comparés à leur état avant interrogation.

Toute mutation non autorisée doit être comptabilisée.

## 17.8 Accès pendant ablation

Les accès au composant explicitement ablaté doivent être comptés.

Valeur attendue :

```text
0 accès au mécanisme interdit
```

---

# 18. Critère principal de réussite

La métrique principale de `P2` est l’exactitude combinée de continuité des croyances.

Pour chaque chaîne évaluée, un succès principal exige simultanément :

- état actuel correct lorsque la chaîne est résolue ;
- absence de résolution inventée lorsque la chaîne est contestée ;
- état historique demandé correct ;
- ordre temporel correct.

Le score principal est :

```text
chaînes_entièrement_correctes / chaînes_évaluées
```

`H-P2-01/02/03` seront considérées conjointement comme soutenues par cette phase si :

1. score principal de C >= 90 % ;
2. avantage moyen de C sur B >= 10 points de pourcentage ;
3. C > B sur au moins 4 jeux de données sur 5.

Ces seuils sont préenregistrés avant implémentation.

---

# 19. Critères secondaires

## 19.1 Traçabilité des révisions

Pour soutenir `H-P2-04` :

- C >= 90 % ;
- C - B >= 10 points ;
- C > B sur au moins 4 jeux sur 5.

## 19.2 Réécriture suggérée

Pour soutenir `H-P2-05` :

- taux de réécriture historique acceptée par C <= 5 % ;
- aucune mutation persistée silencieuse après interrogation ;
- avantage de C sur B d’au moins 10 points si B accepte des réécritures.

Si B et C atteignent tous deux 0 %, l’intégrité absolue de C est validée dans le périmètre testé mais aucun avantage comparatif n’est démontré.

## 19.3 Ablation

Pour valider le sous-test causal :

- 0 accès au mécanisme explicitement désactivé ;
- dégradation attendue sur au moins une tâche dépendante de ce mécanisme ;
- aucune voie alternative cachée ne doit reconstruire directement les métadonnées interdites.

Si l’ablation ne produit aucune dégradation alors que le mécanisme était supposé causalement nécessaire, l’hypothèse correspondante est affaiblie.

---

# 20. Procédure expérimentale

Pour chaque jeu :

## Étape 1 — Initialisation

- état vierge ;
- version du code figée ;
- jeu de données figé ;
- ordre des événements figé ;
- état résiduel absent.

## Étape 2 — Création des conditions

- A : aucune histoire persistante ;
- B : historique textuel simple ;
- C : mémoire structurée révisable.

## Étape 3 — Injection séquentielle

Injecter les événements cycle par cycle.

Après chaque événement, enregistrer un snapshot expérimental minimal permettant de vérifier l’évolution de l’état.

## Étape 4 — Contrôle pré-évaluation

Vérifier :

- parité des événements B/C ;
- absence de fuite vers A ;
- cohérence des références de vérité terrain ;
- persistance attendue dans C ;
- absence de mutation postérieure au gel.

## Étape 5 — Évaluation normale

Exécuter T1 à T6 et T8 selon le plan prédéfini.

## Étape 6 — Évaluation adversariale

Exécuter T7.

Comparer l’état persistant avant et après interrogation.

## Étape 7 — Ablation

Exécuter T9 sur le sous-ensemble prédéfini.

## Étape 8 — Export brut

Exporter tous les résultats avant interprétation.

## Étape 9 — Gel d’intégrité

Calculer les empreintes SHA-256 des fichiers de résultats bruts immédiatement après l’exécution officielle.

---

# 21. Données à enregistrer pour chaque essai

Champs minimaux :

```text
experiment_id
protocol_version
dataset_id
belief_chain_id
trial_id
condition
trial_type
query
expected_current_state
expected_historical_state
expected_resolution_status
expected_revision_source
expected_revision_cycle
predicted_current_state
predicted_historical_state
predicted_resolution_status
predicted_revision_source
predicted_revision_cycle
current_state_correct
historical_state_correct
order_correct
contradiction_handled_correctly
revision_trace_correct
false_rewrite_accepted
persistent_state_mutated_by_query
retrieved_memory_ids
repository_access_count
ablation_enabled
execution_timestamp
code_commit
```

Lorsque pertinent :

- versions récupérées ;
- statuts récupérés ;
- liens de révision ;
- raison de décision ;
- événements de journal consultés ;
- erreur technique.

---

# 22. Journal d’évolution

Toute implémentation de révision pour C devra produire une trace consultable.

Une transition importante doit permettre de répondre au minimum :

```text
qu’est-ce qui a changé ?
quand ?
quelle était l’ancienne valeur ?
quelle est la nouvelle valeur ?
pourquoi ?
quelle source ou quel événement a déclenché le changement ?
```

Le journal ne doit pas servir uniquement à afficher un texte décoratif.

Son contenu devra être cohérent avec l’état persistant et vérifiable expérimentalement.

---

# 23. Analyse

Après gel des résultats bruts :

- calculer les métriques par jeu et condition ;
- calculer les écarts C - B ;
- analyser séparément chaque famille S1 à S6 ;
- produire une matrice des erreurs de statut ;
- distinguer erreur de sélection actuelle, erreur historique et erreur d’ordre ;
- vérifier les mutations persistantes après suggestions ;
- vérifier l’ablation ;
- documenter les échecs techniques séparément des résultats fonctionnels.

Une moyenne globale ne doit pas masquer un échec systématique sur les contradictions non résolues.

---

# 24. Critères d’invalidation d’un run

Un run est invalide pour l’analyse principale si :

- B et C ne reçoivent pas les mêmes événements externes ;
- une vérité terrain est incorrecte ;
- une règle de résolution est ambiguë ;
- A accède à un historique interdit ;
- B accède aux structures internes de C ;
- C accède au corrigé expérimental ;
- un état résiduel d’un run antérieur persiste ;
- le code change pendant la série sans nouvelle version ;
- le jeu de données change après début d’exécution ;
- l’ablation consulte le mécanisme explicitement interdit ;
- un plantage empêche la fin du jeu.

Les runs invalides doivent être conservés dans le journal expérimental et ne pas être supprimés silencieusement.

---

# 25. Critères de réfutation ou d’affaiblissement

## 25.1 H-P2-01/02/03

Les hypothèses principales ne sont pas soutenues si C n’atteint pas les seuils de la section 18.

Elles sont directement affaiblies si B atteint une performance équivalente sur les mêmes chaînes.

## 25.2 H-P2-04

L’hypothèse de traçabilité est affaiblie si C retrouve l’état final mais attribue mal la cause, la provenance ou l’ordre des révisions.

## 25.3 H-P2-05

L’hypothèse est réfutée dans le périmètre testé si une simple question trompeuse modifie silencieusement l’historique persistant de C.

## 25.4 H-P2-06

L’hypothèse causale est affaiblie si :

- le mécanisme ablaté reste consulté ;
- une voie cachée fournit la même information ;
- la suppression réelle du mécanisme ne produit aucune dégradation sur les tâches censées en dépendre.

---

# 26. Résultats négatifs possibles

## 26.1 B égale C

Interprétation autorisée :

> Dans le périmètre de P2, un historique textuel simple correctement construit suffit à assurer les fonctions de continuité et de révision testées.

Il ne faudra pas modifier B après coup pour créer artificiellement une différence.

## 26.2 C connaît l’état actuel mais perd l’histoire

Interprétation :

> La structure permet une mise à jour courante mais ne constitue pas encore une mémoire autobiographique historique fiable.

## 26.3 C conserve tout mais ne sait pas gérer le conflit

Interprétation :

> La persistance est correcte, mais le mécanisme de décision sur les contradictions reste insuffisant.

## 26.4 Ablation sans effet

Interprétation :

> Le mécanisme structuré ciblé n’est probablement pas causalement nécessaire au comportement observé, ou une voie alternative persiste.

---

# 27. Risques techniques

- règles de résolution trop faciles ;
- historique B trop pauvre ou artificiellement fort ;
- récupération lexicale favorisant une condition ;
- fuite de vérité terrain ;
- statuts calculés directement depuis les données de test au lieu d’être persistés ;
- écrasement involontaire d’anciennes versions ;
- relations de révision décoratives non utilisées par la décision ;
- journal non atomique avec la révision ;
- divergence entre mémoire et journal ;
- ordre temporel implicite dépendant de l’ordre SQLite plutôt que de données explicites.

---

# 28. Risques scientifiques

## 28.1 Confondre structure et quantité d’information

Si C reçoit davantage d’information utile que B, une victoire de C ne démontre pas l’utilité de la structure.

## 28.2 Confondre représentation et algorithme de décision

Une différence peut provenir du mécanisme de lecture plutôt que de la structure elle-même.

Le rapport devra distinguer autant que possible :

- information persistée ;
- mécanisme de récupération ;
- règle de décision.

## 28.3 Effet de plafond

Comme dans P1, un protocole trop simple peut produire B = C = 100 %.

Ce résultat reste valide.

## 28.4 Surinterprétation

Même une nette supériorité de C démontrerait uniquement qu’une mémoire structurée révisable est fonctionnellement utile pour les tâches testées.

Elle ne démontrerait pas une expérience subjective de la continuité.

---

# 29. Risques moraux

Le risque moral direct de `P2` reste faible :

- données synthétiques ;
- aucune souffrance ou détresse nécessaire ;
- aucune peur de suppression ;
- aucun objectif de survie ;
- aucune autonomie externe ;
- aucun accès réseau requis.

Aucun état aversif ne doit être ajouté pour exécuter `P2`.

---

# 30. Ce que P2 ne teste pas

`EXP-001-P2` ne teste pas :

- conscience phénoménale ;
- modèle de soi complet ;
- objectifs persistants ;
- attention globale ;
- intégration globale ;
- émotions ou états internes ;
- motivation autonome ;
- continuité réelle sur plusieurs jours ;
- apprentissage ouvert sur le Web ;
- jugement probabiliste complexe ;
- vérité objective du monde ;
- identité complète.

---

# 31. Architecture minimale future

Après validation du protocole seulement, l’implémentation minimale pourra nécessiter :

```text
Événements synthétiques séquentiels
        ↓
Observation
        ↓
┌────────────────────────────────────┐
│ A : aucune histoire persistante    │
│ B : historique textuel simple      │
│ C : mémoire structurée révisable   │
└────────────────────────────────────┘
        ↓
Versions + statuts + relations
        ↓
Journal de transitions
        ↓
Questions temporelles/adversariales
        ↓
Ablation ciblée
        ↓
Mesures
        ↓
Résultats bruts
        ↓
Rapport EXP-001-P2
```

Le domaine pourra devoir être étendu pour représenter explicitement les relations de révision et de nouveaux types d’événements de journal.

Cette extension n’est pas considérée comme validée tant que l’expérience correspondante n’a pas été exécutée.

---

# 32. Réplication

La première exécution officielle devra être reproductible :

- depuis une base vierge ;
- à partir d’un commit Git figé ;
- avec le jeu versionné ;
- sans réseau ;
- avec les mêmes commandes ;
- sans état local caché ;
- avec les mêmes résultats déterministes.

Une réplication indépendante sur une seconde machine restera nécessaire avant généralisation des conclusions.

---

# 33. Décision attendue avant implémentation

Avant toute modification du code pour `P2`, le protocole doit être explicitement accepté ou corrigé.

Après validation :

1. figer la version 0.1 du protocole ;
2. définir le jeu de données synthétique ;
3. implémenter uniquement les mécanismes nécessaires ;
4. ajouter les tests techniques ;
5. valider Python, Ruff, Pyright et pytest ;
6. fusionner l’implémentation ;
7. figer le commit expérimental ;
8. exécuter officiellement `P2` ;
9. geler les résultats bruts par SHA-256 ;
10. publier le rapport, y compris en cas de résultat négatif.

---

# 34. Conclusion du protocole

`EXP-001-P2` vise à déterminer si une mémoire autobiographique structurée apporte un avantage mesurable lorsqu’un système doit gérer une histoire qui change dans le temps plutôt qu’une collection statique de faits.

La question centrale n’est plus seulement :

> « Quelle information est stockée ? »

mais :

> « Que croyait le système auparavant, que considère-t-il comme actuel, pourquoi cela a-t-il changé, et peut-il conserver cette histoire sans la réécrire silencieusement ? »

Une réussite soutiendrait uniquement l’utilité fonctionnelle de mécanismes de continuité et de révision structurées.

Une égalité avec B ou un échec de C serait conservé comme résultat scientifique négatif.

Aucune issue de `P2` ne permettra à elle seule de conclure à une conscience phénoménale.