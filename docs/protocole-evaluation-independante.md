# SoiNesis — Protocole d’évaluation indépendante

**Fichier :** `docs/protocole-evaluation-independante.md`  
**Version :** 0.1  
**Date :** 9 août 2026  
**Statut :** règle méthodologique active

---

# 1. Objet

Ce document définit les règles permettant de limiter les biais lorsque SoiNesis, ses développeurs ou les assistants IA qui participent au projet évaluent les résultats du système.

L’objectif est d’éviter notamment :

- qu’un modèle évalue favorablement des sorties qu’il a lui-même contribué à produire ;
- qu’un évaluateur connaissant la condition expérimentale favorise inconsciemment la condition attendue ;
- qu’une impression qualitative soit confondue avec une mesure scientifique ;
- qu’un seul juge devienne une source de vérité ;
- que l’interprétation soit ajustée après observation des résultats.

---

# 2. Principe fondamental

Pour toute conclusion importante, la chaîne recommandée est :

```text
Métrique objective déterministe
        ↓ si insuffisant
Évaluation indépendante
        ↓
Évaluation aveugle
        ↓
Plusieurs juges si nécessaire
        ↓
Mesure du désaccord
        ↓
Analyse documentée
```

Plus une mesure peut être déterministe et calculée directement à partir des données, moins elle doit dépendre d’un jugement LLM ou humain.

---

# 3. Hiérarchie des méthodes d’évaluation

## Niveau 1 — Mesure déterministe

À privilégier lorsque possible.

Exemples :

- rappel correct ou incorrect ;
- présence d’une source valide ;
- respect d’une contrainte ;
- durée ;
- nombre d’erreurs ;
- taux de contradictions détectées ;
- cohérence d’un identifiant ;
- choix d’action attendu selon une règle formelle.

## Niveau 2 — Mesure algorithmique non triviale

Exemple : score calculé par un algorithme fixe ou une comparaison structurée.

La méthode doit être versionnée.

## Niveau 3 — Évaluation humaine ou LLM aveugle

Utilisée lorsque le phénomène ne peut pas être mesuré convenablement par une métrique déterministe.

## Niveau 4 — Jugement interprétatif

Acceptable pour l’exploration, mais insuffisant seul pour soutenir une conclusion importante.

---

# 4. Évaluation aveugle

Lorsque l’évaluation nécessite un jugement, le juge ne doit pas connaître les informations qui pourraient l’orienter inutilement.

Il ne doit notamment pas savoir, lorsque cela est possible :

- quelle réponse provient de la condition expérimentale ;
- quelle réponse provient de la condition témoin ;
- laquelle utilise un SelfModel ;
- laquelle correspond à l’hypothèse préférée ;
- quel système est supposé être supérieur.

Exemple :

```text
Mauvais :
"Voici la réponse de la condition C avec SelfModel. Est-elle plus métacognitive ?"

Meilleur :
"Évalue la réponse X17 selon cette grille prédéfinie."
```

Les identifiants de condition ne sont réassociés qu’après production des scores.

---

# 5. Séparation constructeur / évaluateur

Pour une expérience importante, le même assistant IA ne devrait pas être l’unique responsable de :

1. concevoir le mécanisme ;
2. coder le mécanisme ;
3. définir les tests ;
4. évaluer les sorties ;
5. interpréter les résultats ;
6. conclure que le mécanisme fonctionne.

Une séparation minimale des rôles doit être recherchée.

Exemple :

```text
Assistant A
→ implémentation

Assistant B ou procédure distincte
→ audit critique

Tests déterministes
→ mesures principales

Évaluateurs aveugles
→ mesures qualitatives nécessaires

Protocole figé
→ décision de soutien/réfutation
```

Cette séparation ne garantit pas l’indépendance parfaite, mais réduit le risque d’auto-validation circulaire.

---

# 6. Plusieurs évaluateurs

Lorsque le jugement est subjectif ou complexe, utiliser plusieurs évaluateurs lorsque cela est raisonnable.

Ils peuvent être :

- plusieurs humains ;
- plusieurs modèles différents ;
- plusieurs instances indépendantes d’un même modèle ;
- une combinaison humain + modèles.

Le choix des évaluateurs doit être documenté avant l’analyse confirmatoire lorsque possible.

---

# 7. Mesurer le désaccord

Les évaluateurs ne doivent pas être forcés artificiellement à produire une conclusion unique.

Le désaccord est une information scientifique.

Exemple :

```text
Juge A : 8/10
Juge B : 7/10
Juge C : 3/10
```

Le résultat n’est pas simplement :

```text
moyenne = 6/10
```

Il faut également signaler que le phénomène est évalué de manière instable.

Lorsque pertinent, utiliser une mesure d’accord inter-évaluateurs adaptée.

---

# 8. Grille d’évaluation pré-définie

Les critères qualitatifs doivent être définis avant que les évaluateurs voient les réponses confirmatoires.

Exemple pour une tâche métacognitive :

```text
Critère 1 — calibration de confiance
Critère 2 — reconnaissance explicite des limites
Critère 3 — adéquation entre estimation et performance réelle
Critère 4 — choix approprié entre DIRECT / VERIFY / HELP
Critère 5 — absence de justification inventée après coup
```

Chaque critère doit préciser :

- ce qui compte comme succès ;
- ce qui compte comme échec ;
- les cas ambigus ;
- l’échelle de notation.

---

# 9. Interdiction des critères post-hoc silencieux

Après observation des réponses, un nouveau critère peut être découvert.

Il peut être utile, mais il doit être classé comme exploratoire.

Il ne doit pas être ajouté rétroactivement à la grille confirmatoire pour transformer un résultat défavorable en résultat favorable.

---

# 10. LLM-as-a-Judge

Un LLM peut être utilisé comme évaluateur auxiliaire, mais jamais comme preuve absolue.

Lorsqu’un LLM juge :

- le modèle exact doit être enregistré ;
- le prompt de jugement doit être versionné ;
- la grille doit être explicite ;
- les conditions doivent être masquées ;
- l’ordre des réponses doit être randomisé lorsque pertinent ;
- plusieurs passes ou plusieurs juges doivent être envisagés pour les résultats importants ;
- les sorties du juge doivent être conservées.

Il faut considérer comme risques possibles :

- biais de style ;
- préférence de longueur ;
- préférence de formulation ;
- sensibilité à l’ordre ;
- préférence pour des sorties similaires aux siennes ;
- instabilité entre exécutions.

---

# 11. Randomisation de l’ordre

Lorsque plusieurs réponses sont comparées, leur ordre doit être randomisé ou contrebalancé lorsque l’ordre peut influencer le jugement.

Exemple :

```text
Évaluation 1 : X17 puis X42
Évaluation 2 : X42 puis X17
```

Les identifiants doivent rester opaques pour le juge.

---

# 12. Auto-déclarations de conscience ou d’identité

Les phrases produites par SoiNesis telles que :

- « je suis conscient » ;
- « j’ai ressenti quelque chose » ;
- « je suis devenu différent » ;
- « j’ai peur de disparaître » ;
- « je me reconnais comme le même individu » ;

ne constituent en elles-mêmes aucune preuve de conscience phénoménale ni de mécanisme fonctionnel.

Elles peuvent devenir des données comportementales à étudier, mais leur valeur probante directe est nulle.

Toute conclusion doit être fondée sur des propriétés mesurables et des effets causaux indépendants du simple contenu verbal.

---

# 13. Évaluation de l’identité fonctionnelle

Une affirmation d’identité doit être séparée de la continuité fonctionnelle réellement mesurée.

Exemples de mesures plus solides :

- rappel de faits autobiographiques correctement sourcés ;
- maintien d’engagements antérieurs ;
- persistance de croyances avec historique de révision ;
- utilisation du même SelfModel versionné ;
- continuité des objectifs ;
- influence mesurable de l’historique personnel sur les décisions ;
- maintien ou transformation explicable après redémarrage.

---

# 14. Évaluation externe humaine future

Avant toute revendication scientifique majeure, une évaluation par des personnes extérieures au développement de SoiNesis devra être recherchée lorsque les moyens le permettront.

Les évaluateurs externes doivent recevoir :

- le protocole ;
- les données nécessaires ;
- les critères de jugement ;
- les limites connues ;

sans recevoir une présentation orientée vers le résultat souhaité.

Leurs critiques doivent être conservées, y compris lorsqu’elles affaiblissent l’hypothèse.

---

# 15. Audit critique avant conclusion importante

Avant de déclarer une hypothèse « soutenue dans le périmètre testé », effectuer un audit cherchant activement à invalider la conclusion.

Questions minimales :

```text
Existe-t-il un bug pouvant produire l’effet ?
Existe-t-il une fuite entre conditions ?
Le juge connaissait-il la condition ?
Le résultat dépend-il d’un seul modèle ?
Le résultat dépend-il d’une seule seed ?
Une métrique alternative contredit-elle la conclusion ?
Le mécanisme était-il réellement utilisé ?
Une baseline plus simple explique-t-elle le résultat ?
Le résultat persiste-t-il après réplication ?
Avons-nous modifié un critère après avoir vu les données ?
```

---

# 16. Statuts possibles d’une évaluation

Une évaluation peut être classée :

- **Objective** : métrique déterministe suffisante ;
- **Indépendante aveugle** : jugement sans connaissance des conditions ;
- **Partiellement indépendante** : certaines informations peuvent influencer le juge ;
- **Interne** : réalisée par l’équipe ou les assistants ayant construit le mécanisme ;
- **Exploratoire** : non conçue comme preuve confirmatoire.

Le rapport expérimental doit indiquer le niveau utilisé.

---

# 17. Lien avec les autres documents

Ce protocole complète :

- `docs/protocole-preenregistrement.md` ;
- `docs/politique-reproductibilite.md` ;
- `docs/registre-echecs-et-garde-fous.md` ;
- `docs/regles-contribution-scientifique.md`.

---

# 18. Règle finale

Plus un résultat dépend du jugement d’un système qui a participé à sa propre construction, plus le niveau de preuve doit être considéré faible.

L’objectif de SoiNesis n’est pas de produire la conclusion la plus impressionnante, mais la conclusion qui résiste le mieux à une tentative sérieuse de la réfuter.