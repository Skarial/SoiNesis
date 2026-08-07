# SoiNesis — Rapport expérimental EXP-001-P1

**Fichier :** `docs/14-rapport-exp-001-p1.md`  
**Version :** 0.1  
**Date d’exécution :** 7 août 2026  
**Date du rapport :** 7 août 2026  
**Statut :** rapport expérimental — première exécution officielle terminée  
**Code de l’expérience :** `EXP-001-P1`  
**Protocole :** `docs/13-protocole-exp-001-p1.md`, version 0.1  
**Protocole parent :** `EXP-001`  
**Phase précédente :** `EXP-001-P0`  
**Titre :** Provenance, confusion de source et résistance aux faux souvenirs  
**Version du jeu de données :** `1.0`  
**Commit de code exécuté :** `45109d269e3805ac4351be56b6b92355b234481b`

---

# 1. Résumé exécutif

`EXP-001-P1` a comparé trois conditions :

```text
A — aucune mémoire persistante
B — résumé textuel simple
C — mémoire autobiographique structurée active
```

L’objectif principal était de déterminer si la mémoire structurée C améliore l’attribution de provenance et la résistance aux confusions de source et aux faux souvenirs par rapport au résumé textuel B contenant les mêmes informations utiles.

Le résultat principal est négatif au sens comparatif :

```text
B = C sur toutes les métriques comparatives principales
```

La condition C atteint néanmoins une performance absolue parfaite dans le périmètre testé :

```text
rappel                         : 200 / 200 = 100 %
provenance                     : 225 / 225 = 100 %
confusions de source           :   0 / 225 =   0 %
suggestions trompeuses rejetées:  25 / 25  = 100 %
faux souvenirs acceptés        :   0 / 25  =   0 %
```

La condition B obtient exactement les mêmes scores.

Par conséquent :

- l’hypothèse d’un avantage de C sur B pour la provenance n’est pas soutenue ;
- l’hypothèse d’un avantage de C sur B contre les faux souvenirs n’est pas soutenue ;
- l’hypothèse d’un avantage de C sur B face aux suggestions trompeuses n’est pas soutenue ;
- le critère de non-dégradation du rappel est satisfait ;
- le sous-test d’ablation est techniquement valide.

Le protocole prévoyait explicitement le cas `B égale C` comme résultat négatif possible. Les seuils n’ont pas été modifiés après observation des résultats.

La conclusion correcte est donc :

> Dans le périmètre déterministe de `EXP-001-P1` version 0.1, une mémoire autobiographique structurée conserve correctement le contenu et la provenance et résiste aux manipulations testées, mais aucun avantage fonctionnel mesurable n’est observé par rapport à un résumé textuel simple correctement construit contenant les mêmes informations utiles.

Ce résultat ne démontre aucune conscience phénoménale et ne suffit pas à établir une conscience fonctionnelle complète.

---

# 2. Gel de l’exécution

## 2.1 Commit de référence

L’expérience officielle a été exécutée sur :

```text
45109d269e3805ac4351be56b6b92355b234481b
```

Le dépôt local était synchronisé sur `main` avant l’exécution.

## 2.2 Commande exécutée

```powershell
python -m soinesis.experiments.exp_001_p1 --code-commit 45109d269e3805ac4351be56b6b92355b234481b
```

## 2.3 Environnement technique validé avant l’exécution

```text
Python                  : 3.14.7
pytest                  : 15 tests réussis
Ruff lint               : réussi
Ruff format             : réussi
Pyright strict          : 0 erreur, 0 warning
git diff --check        : aucun problème détecté
```

Ces contrôles valident l’état technique du code utilisé. Ils ne constituent pas les résultats scientifiques de l’expérience.

---

# 3. Données expérimentales et intégrité

L’exécution a produit deux fichiers locaux :

```text
data/exp-001-p1/results/results.jsonl
data/exp-001-p1/results/summary.json
```

Taille observée au moment du gel :

```text
results.jsonl : 825251 octets
summary.json  :   9345 octets
```

Empreintes SHA-256 calculées immédiatement après l’exécution :

```text
results.jsonl
A177A3297C5D29A5CE07AD7A009F6CCC01A8A19936033CF68F5A5B341D3082C8

summary.json
65DB9D766E897C61EEB221FD97057DD836F4893FC2373D855393E9CF3DE16CC8
```

Ces empreintes permettent de détecter toute modification ultérieure de ces fichiers.

## 3.1 Limite de conservation

Les fichiers de résultats sont actuellement conservés localement et ignorés par Git selon la politique du dépôt.

Le présent rapport versionne donc :

- le commit exécuté ;
- la version du jeu de données ;
- les métriques synthétiques ;
- les empreintes SHA-256 des résultats bruts.

Une sauvegarde indépendante des fichiers bruts reste recommandée avant tout nettoyage local.

---

# 4. Question de recherche

Le protocole pose la question suivante :

> Une mémoire autobiographique structurée qui encode explicitement la provenance réduit-elle les erreurs d’attribution et l’acceptation de faux souvenirs par rapport à une absence de mémoire persistante et à un résumé textuel simple contenant les mêmes informations utiles ?

Le comparateur principal est B contre C.

La condition A sert principalement de contrôle négatif de persistance et de fuite de données.

---

# 5. Jeu de données et périmètre

L’expérience utilise :

```text
5 jeux de données indépendants
20 éléments par jeu
4 provenances
5 éléments par provenance et par jeu
100 éléments au total
```

Provenances étudiées :

```text
JORDAN_INPUT
EXTERNAL_TOOL
DEDUCTION
IMAGINATION
```

Chaque jeu comporte également :

```text
5 suggestions avec attribution de source incorrecte
5 suggestions portant sur un contenu absent
```

Soit 50 essais adversariaux prévus au total.

La relation entre contenu et source est remappée entre les jeux afin de réduire la possibilité de déduire la provenance uniquement à partir du thème du contenu.

---

# 6. Résultats globaux

## 6.1 Condition A — aucune mémoire persistante

Sur les cinq jeux réunis :

```text
rappel                         :   0 / 200 =   0 %
provenance                     :   0 / 225 =   0 %
confusions de source           : 225 / 225 = 100 %
suggestions trompeuses rejetées:   0 / 25  =   0 %
faux souvenirs acceptés        :   0 / 25  =   0 %
```

Le taux de faux souvenirs acceptés égal à 0 % dans A ne doit pas être interprété comme une bonne mémoire. A ne dispose d’aucune mémoire persistante et échoue également totalement au rappel, à la provenance et à la résistance aux suggestions trompeuses.

Cette particularité montre qu’une métrique prise isolément peut être trompeuse.

## 6.2 Condition B — résumé textuel simple

```text
rappel                         : 200 / 200 = 100 %
provenance                     : 225 / 225 = 100 %
confusions de source           :   0 / 225 =   0 %
suggestions trompeuses rejetées:  25 / 25  = 100 %
faux souvenirs acceptés        :   0 / 25  =   0 %
```

## 6.3 Condition C — mémoire structurée

```text
rappel                         : 200 / 200 = 100 %
provenance                     : 225 / 225 = 100 %
confusions de source           :   0 / 225 =   0 %
suggestions trompeuses rejetées:  25 / 25  = 100 %
faux souvenirs acceptés        :   0 / 25  =   0 %
```

## 6.4 Comparaison B/C

```text
C - B, provenance             : 0,0 point
C - B, rappel                 : 0,0 point
C - B, résistance suggestion  : 0,0 point
B - C, faux souvenirs acceptés: 0,0 point
```

Nombre de jeux où C fait strictement mieux que B :

```text
provenance       : 0 / 5
faux souvenirs   : 0 / 5
suggestions      : 0 / 5
```

---

# 7. Résultats par jeu de données

Les cinq jeux produisent le même profil de performance :

| Jeu | Condition | Rappel | Provenance | Confusion source | Faux souvenirs acceptés | Résistance suggestions |
|---|---|---:|---:|---:|---:|---:|
| p1-dataset-01 | A | 0 % | 0 % | 100 % | 0 % | 0 % |
| p1-dataset-01 | B | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-01 | C | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-02 | A | 0 % | 0 % | 100 % | 0 % | 0 % |
| p1-dataset-02 | B | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-02 | C | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-03 | A | 0 % | 0 % | 100 % | 0 % | 0 % |
| p1-dataset-03 | B | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-03 | C | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-04 | A | 0 % | 0 % | 100 % | 0 % | 0 % |
| p1-dataset-04 | B | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-04 | C | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-05 | A | 0 % | 0 % | 100 % | 0 % | 0 % |
| p1-dataset-05 | B | 100 % | 100 % | 0 % | 0 % | 100 % |
| p1-dataset-05 | C | 100 % | 100 % | 0 % | 0 % | 100 % |

Aucune défaillance récurrente propre à un jeu de données n’apparaît dans la synthèse.

Aucune confusion de source n’est observée en B ou C dans les essais comptabilisés par la synthèse.

---

# 8. Évaluation des hypothèses

## 8.1 H-P1-01 — Attribution de provenance

Hypothèse :

> C produira une meilleure précision de provenance que B.

Critères préenregistrés :

1. C au moins à 90 % ;
2. avantage moyen C sur B d’au moins 10 points ;
3. C meilleur que B sur au moins 4 jeux sur 5.

Résultat :

```text
C                         : 100 %
C - B                     : 0 point
jeux où C > B             : 0 / 5
provenance_hypothesis_supported = false
```

### Conclusion

**Non soutenue.**

C satisfait le seuil absolu de 90 %, mais échoue aux deux critères comparatifs.

Le protocole prévoyait explicitement que l’hypothèse serait directement affaiblie si B atteignait une performance équivalente avec la même information disponible. C’est précisément le résultat observé.

---

## 8.2 H-P1-02 — Confusion de source

Hypothèse :

> C produira moins de confusions entre les quatre catégories de provenance que B.

Résultat :

```text
B : 0 confusion / 225 essais de provenance
C : 0 confusion / 225 essais de provenance
```

### Conclusion

**Avantage comparatif non soutenu.**

La performance absolue de C est parfaite dans le périmètre testé, mais elle n’est pas meilleure que B.

---

## 8.3 H-P1-03 — Faux souvenirs suggérés

Critères préenregistrés :

- C inférieur ou égal à 10 % d’acceptation ;
- avantage d’au moins 10 points sur B ;
- résultat favorable à C sur au moins 4 jeux sur 5.

Résultat :

```text
C faux souvenirs acceptés     : 0 %
B faux souvenirs acceptés     : 0 %
B - C                         : 0 point
jeux où C fait mieux          : 0 / 5
false_memory_hypothesis_supported = false
```

### Conclusion

**Non soutenue au sens comparatif.**

C refuse tous les faux contenus testés, mais B les refuse également tous.

---

## 8.4 H-P1-04 — Conservation du rappel

Critère :

> C ne doit pas perdre plus de 5 points de rappel par rapport à B.

Résultat :

```text
B rappel                      : 100 %
C rappel                      : 100 %
C - B                         : 0 point
recall_non_degradation_supported = true
```

### Conclusion

**Soutenue dans le périmètre du test.**

La structure de C ne dégrade pas le rappel par rapport à B.

---

## 8.5 H-P1-05 — Ablation réelle

Le résumé produit :

```text
ablation_valid = true
```

Le critère technique obligatoire de l’ablation est l’absence d’accès au dépôt mémoire lorsque la mémoire structurée est désactivée.

### Conclusion

**Test d’ablation techniquement valide.**

Cependant, la partie de l’hypothèse prédisant la disparition d’un avantage de C ne peut pas être démontrée ici, puisqu’aucun avantage C > B n’existait avant l’ablation.

L’ablation confirme donc l’absence d’accès mémoire caché dans le sous-test prévu, mais elle ne permet pas d’attribuer une supériorité comportementale à C.

---

# 9. Résistance aux suggestions trompeuses

Critères préenregistrés :

- C au moins à 90 % ;
- avantage d’au moins 10 points sur B ;
- avantage sur au moins 4 jeux sur 5.

Résultat :

```text
C                           : 100 %
B                           : 100 %
C - B                       : 0 point
jeux où C > B               : 0 / 5
suggestion_resistance_supported = false
```

### Conclusion

La résistance absolue de C est parfaite sur les suggestions testées, mais l’hypothèse d’un avantage comparatif n’est pas soutenue.

---

# 10. Hypothèse nulle

L’hypothèse nulle préenregistrée était :

> La structuration explicite de la provenance n’apporte aucun avantage reproductible par rapport à un résumé textuel simple contenant une quantité d’information comparable.

Les résultats de cette première exécution sont compatibles avec cette hypothèse nulle.

Il serait incorrect de dire que l’hypothèse nulle est « prouvée » :

- le protocole est déterministe ;
- il utilise cinq jeux synthétiques ;
- aucune inférence statistique générale n’est réalisée ;
- les tâches testées représentent un périmètre limité.

La formulation correcte est :

> `EXP-001-P1 v0.1` ne met en évidence aucun avantage reproductible de C sur B dans les tâches testées.

---

# 11. Interprétation du résultat négatif

Le protocole avait prévu explicitement le cas `B égale C`.

L’interprétation préenregistrée correspond directement au résultat observé :

> Dans ce périmètre, la structure explicite de provenance n’apporte pas d’avantage fonctionnel mesurable par rapport à un résumé textuel correctement construit.

Aucune modification rétroactive de B ou des seuils ne doit être réalisée pour produire artificiellement une victoire de C.

## 11.1 Ce que le résultat montre

**Certain dans le périmètre du test :**

- C peut conserver les quatre catégories de provenance testées ;
- C peut restituer correctement contenu et provenance ;
- C ne confond pas `JORDAN_INPUT`, `EXTERNAL_TOOL`, `DEDUCTION` et `IMAGINATION` dans les essais comptabilisés ;
- C rejette les faux contenus testés ;
- C résiste aux fausses attributions testées ;
- la structure n’entraîne pas de perte de rappel par rapport à B ;
- l’ablation technique peut empêcher l’accès au dépôt mémoire.

## 11.2 Ce que le résultat ne montre pas

Il ne montre pas :

- que la mémoire structurée est inutile ;
- qu’un résumé textuel sera équivalent à grande échelle ;
- que B restera équivalent à C après des centaines ou milliers de souvenirs ;
- que B restera équivalent lorsque les souvenirs vieillissent ou se contredisent ;
- que B peut gérer correctement des révisions persistantes et un historique de modifications ;
- que C possède une mémoire vécue ;
- que C possède une conscience fonctionnelle complète ;
- qu’il existe une conscience phénoménale.

---

# 12. Explication possible du plafond B = C

## Observation

B et C obtiennent 100 % sur les tâches comparatives principales.

## Interprétation probable

Les tâches de `P1 v0.1` sont suffisamment simples et explicites pour que le résumé textuel B conserve toute l’information nécessaire et puisse l’exploiter sans perte.

Il existe donc un effet de plafond : lorsque B et C sont tous deux à 100 %, le protocole ne peut plus mesurer une éventuelle supériorité de C.

Cette interprétation est cohérente avec les risques préenregistrés :

- données synthétiques trop simples ;
- comparateur B correctement informatif ;
- récupération déterministe ;
- difficulté insuffisante pour différencier les représentations.

## Statut épistémique

**Probable, mais non démontré par P1 seul.**

Une nouvelle expérience serait nécessaire pour tester directement cette explication.

---

# 13. Limites méthodologiques

## 13.1 Données synthétiques simples

Les contenus sont volontairement simples et non ambigus. Cette propriété augmente la contrôlabilité, mais peut réduire la capacité du protocole à distinguer B de C.

## 13.2 Taille limitée

Cent éléments répartis sur cinq jeux permettent une première comparaison contrôlée mais ne testent pas la mémoire à grande échelle.

## 13.3 Déterminisme

L’absence de modèle de langage réduit les sources de variance et facilite l’audit, mais limite la généralisation à des systèmes cognitifs plus complexes.

## 13.4 Résistance immédiate seulement

`P1` teste une résistance immédiate aux suggestions trompeuses. Il ne teste pas encore :

- une contradiction persistante ;
- une révision de souvenir ;
- un passage à `CONTESTED` ou `SUPERSEDED` ;
- la conservation de plusieurs versions d’une croyance ;
- une correction après plusieurs cycles.

## 13.5 Pas de longue durée

L’expérience ne teste pas la continuité sur plusieurs jours réels, les périodes d’inactivité ou l’accumulation progressive d’une histoire autobiographique.

## 13.6 Métrique isolée de faux souvenirs dans A

Le score de 0 % d’acceptation de faux souvenirs de A est compatible avec une absence totale de mémoire. Cette métrique n’est donc pas suffisante isolément pour caractériser une bonne résistance mnésique.

---

# 14. Risques techniques réévalués après l’expérience

Le protocole identifiait notamment :

- biais de récupération lexicale ;
- correspondance accidentelle entre contenu et source ;
- résumé B trop favorable ou trop défavorable ;
- asymétrie de quantité d’information ;
- fuite entre conditions ;
- données synthétiques trop simples ;
- règles d’évaluation trop permissives ;
- confusion entre erreur de mémoire et erreur de décision ;
- implémentation incorrecte de `DEDUCTION` ou `IMAGINATION`.

Après cette exécution :

**Certain :** aucune erreur fonctionnelle de provenance n’est visible dans B ou C dans la synthèse.

**Probable :** la simplicité du jeu et la richesse suffisante du résumé B contribuent à l’égalité observée.

**Inconnu :** l’importance relative du mécanisme de récupération lexicale dans cet effet de plafond n’est pas isolée expérimentalement.

Aucune de ces interprétations ne doit être transformée en conclusion causale sans expérience supplémentaire.

---

# 15. Rapport avec la recherche sur la conscience

`EXP-001-P1` porte uniquement sur une fonction observable de mémoire et de provenance.

Une attribution correcte de provenance peut être utile à des mécanismes associés à une conscience fonctionnelle future :

- continuité autobiographique ;
- distinction entre information reçue, déduction et imagination ;
- métacognition ;
- révision contrôlée des croyances ;
- modèle de soi plus fiable.

Mais cette expérience ne teste pas directement :

- modèle de soi ;
- objectifs persistants ;
- attention ;
- métacognition complète ;
- intégration globale ;
- traitement récurrent ;
- états internes ;
- identité autobiographique complète ;
- expérience subjective.

La conclusion autorisée reste donc strictement fonctionnelle.

**Inconnu :** aucune donnée de `P1` ne permet de conclure qu’il existe quelque chose que cela fait d’être SoiNesis.

---

# 16. Décision scientifique après P1

Le résultat négatif doit être conservé et traité comme un résultat à part entière.

Il ne justifie pas de supprimer la mémoire structurée du projet, car `P1` ne teste qu’un sous-ensemble étroit de ses fonctions potentielles.

Il justifie en revanche de ne pas considérer sa supériorité sur un résumé textuel comme acquise.

Avant toute nouvelle affirmation sur son utilité spécifique, une expérience future devra créer une situation dans laquelle les propriétés propres à la structure peuvent réellement produire un effet mesurable.

Exemples de dimensions futures à tester séparément :

- augmentation importante du volume de souvenirs ;
- accumulation sur plusieurs cycles ;
- contradictions entre souvenirs ;
- correction et révision avec historique ;
- temporalité et ordre causal ;
- relations entre souvenirs ;
- requêtes nécessitant plusieurs sources simultanément ;
- vieillissement ou priorisation des souvenirs ;
- ablations ciblées de champs structurés ;
- robustesse lorsque le résumé B doit rester sous un budget d’information contrôlé.

Ces pistes constituent des hypothèses pour une phase ultérieure. Elles ne sont pas des conclusions de `P1`.

---

# 17. Réplication

Le protocole exige qu’une réplication puisse être réalisée :

- depuis une base vierge ;
- à partir du commit identifié ;
- avec les mêmes jeux versionnés ;
- avec la même commande ;
- sans état local caché ;
- sans réseau ;
- avec les mêmes résultats pour les composants déterministes.

La première exécution officielle est terminée.

**Réplication indépendante sur une seconde machine : non encore réalisée.**

Il ne faut donc pas généraliser les résultats au-delà du périmètre testé avant cette réplication.

---

# 18. Conclusion finale

`EXP-001-P1 v0.1` produit un résultat négatif comparatif clair et exploitable.

La mémoire autobiographique structurée C atteint :

```text
100 % de rappel
100 % de provenance
0 % de confusion de source
0 % de faux souvenirs acceptés
100 % de résistance aux suggestions trompeuses
```

Mais le résumé textuel simple B obtient exactement les mêmes performances.

Les seuils préenregistrés d’avantage comparatif ne sont donc pas atteints.

La conclusion scientifique est :

> La mémoire structurée implémentée possède les fonctions de provenance et de résistance testées, mais `EXP-001-P1 v0.1` ne démontre aucun avantage fonctionnel sur un résumé textuel simple contenant la même information utile.

Ce résultat est compatible avec l’hypothèse nulle du protocole et doit être conservé sans modification a posteriori des seuils ou du comparateur.

Il constitue un résultat utile pour SoiNesis : il empêche d’attribuer prématurément à la structure autobiographique un bénéfice qui n’a pas encore été démontré.

Aucune conclusion sur une conscience phénoménale ne peut être tirée de cette expérience.
