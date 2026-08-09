# SoiNesis — Protocole de pré-enregistrement expérimental

**Fichier :** `docs/protocole-preenregistrement.md`  
**Version :** 0.1  
**Date :** 9 août 2026  
**Statut :** règle méthodologique active

---

# 1. Objet

Ce document définit les règles de pré-enregistrement des expériences importantes de SoiNesis.

L’objectif est d’empêcher qu’une hypothèse, une métrique, un critère de succès ou une méthode d’analyse soit modifié après observation des résultats dans le but conscient ou inconscient d’obtenir une conclusion plus favorable.

Le pré-enregistrement ne garantit pas qu’une expérience soit correcte. Il garantit que la différence entre ce qui était prévu avant l’expérience et ce qui a été décidé après l’observation des données reste visible.

---

# 2. Principe fondamental

Une expérience confirmatoire importante doit être définie avant sa première exécution complète.

Une fois le pré-enregistrement figé :

- les critères principaux ne doivent plus être modifiés silencieusement ;
- toute modification doit être versionnée ;
- une modification motivée par les résultats transforme l’analyse concernée en analyse exploratoire ou en nouveau protocole ;
- un résultat négatif ne doit jamais conduire à réécrire rétroactivement la question expérimentale.

```text
Hypothèse
   ↓
Pré-enregistrement figé
   ↓
Implémentation / vérification technique
   ↓
Exécution
   ↓
Analyse prévue
   ↓
Conclusion
```

---

# 3. Expériences concernées

Le pré-enregistrement est obligatoire pour toute expérience qui :

- teste une hypothèse scientifique importante ;
- compare plusieurs conditions cognitives ;
- vise à soutenir ou réfuter un mécanisme ;
- cherche une contribution potentiellement nouvelle ;
- peut conduire à une décision architecturale importante ;
- produit un résultat destiné à être communiqué comme résultat scientifique.

Il peut rester allégé pour :

- tests unitaires ;
- débogage ;
- essais de développement ;
- explorations préliminaires clairement étiquetées comme exploratoires.

---

# 4. Champs obligatoires

Chaque pré-enregistrement doit contenir au minimum :

```text
Identifiant de l’expérience :
Version du protocole :
Date de gel :
Commit Git de référence :

Question de recherche :
Hypothèse principale :
Hypothèse nulle :

Mécanisme testé :
Variable indépendante :
Variable dépendante principale :
Variables dépendantes secondaires :
Variables contrôlées :

Conditions expérimentales :
Condition témoin :
Ablation prévue :

Population / agents / modèles concernés :
Nombre de cycles :
Nombre de réplications :
Seeds prévues :

Métrique principale :
Métriques secondaires :
Méthode statistique :
Seuil ou critère de soutien :
Critère de réfutation :
Critère d’arrêt :

Exclusions autorisées :
Données invalides :
Gestion des valeurs manquantes :

Facteurs de confusion anticipés :
Risques de contamination :

Analyse confirmatoire prévue :
Analyses exploratoires autorisées :

Résultat qui soutiendrait l’hypothèse :
Résultat qui ne la soutiendrait pas :
Résultat ambigu :
```

---

# 5. Gel du protocole

Avant l’exécution confirmatoire :

1. le document de pré-enregistrement est finalisé ;
2. il est commité dans Git ;
3. le SHA du commit est enregistré dans le manifeste expérimental ;
4. les fichiers de configuration importants sont également versionnés ;
5. les éventuels jeux de validation cachés sont figés séparément.

Le commit Git constitue la preuve minimale de l’état du protocole avant observation des résultats.

---

# 6. Modifications après gel

Après gel, toute modification doit être classée.

## 6.1 Correction technique sans changement scientifique

Exemple : correction d’un bug qui empêchait l’expérience de démarrer.

La correction est autorisée si :

- elle est documentée ;
- elle ne change pas l’hypothèse ;
- elle ne modifie pas le critère de succès ;
- elle ne repose pas sur le fait qu’un résultat était favorable ou défavorable.

Un nouveau commit de référence est enregistré.

## 6.2 Modification scientifique avant résultats

Une modification scientifique reste possible avant l’ouverture des résultats confirmatoires, mais produit une nouvelle version du pré-enregistrement.

## 6.3 Modification après observation des résultats

Toute modification motivée après consultation des résultats doit être déclarée explicitement.

L’analyse concernée devient :

- exploratoire ; ou
- base d’une nouvelle expérience pré-enregistrée.

Elle ne doit pas être présentée comme si elle avait été prédite à l’avance.

---

# 7. Séparation développement / validation

Les expériences importantes doivent distinguer trois espaces.

```text
DEV
Tests visibles et scénarios utilisés pour construire le mécanisme

VALIDATION
Scénarios non utilisés pour ajuster directement le mécanisme

HOLDOUT FINAL
Scénarios jamais examinés avant l’évaluation finale
```

Le développement peut utiliser librement DEV.

Les performances sur VALIDATION peuvent guider des décisions documentées.

Le HOLDOUT FINAL ne doit pas servir à itérer jusqu’à obtenir un meilleur score.

Si le holdout final influence une nouvelle version du système, il cesse d’être un holdout pour cette nouvelle version.

---

# 8. Protection contre l’adaptation aux tests

Lorsque possible :

- les scénarios finaux doivent être générés ou sélectionnés avant l’expérience ;
- leur contenu ne doit pas être intégré dans les prompts de développement ;
- Codex ou tout autre assistant qui modifie l’architecture ne doit pas utiliser les réponses attendues du holdout pour corriger le système ;
- les critères d’évaluation doivent être définis avant ouverture du holdout ;
- les fuites de données doivent être journalisées.

Une fuite de holdout n’invalide pas automatiquement tout le projet, mais invalide l’usage de ce holdout comme preuve indépendante.

---

# 9. Confirmatoire vs exploratoire

SoiNesis distingue obligatoirement :

## Confirmatoire

Une analyse prévue avant l’observation des résultats.

## Exploratoire

Une analyse apparue après observation des données ou durant une recherche de causes.

Les analyses exploratoires sont utiles et encouragées, mais elles doivent être étiquetées comme telles.

Une découverte exploratoire importante doit idéalement être testée ensuite dans une nouvelle expérience confirmatoire.

---

# 10. Règle contre le HARKing

Il est interdit de présenter une hypothèse formulée après observation des résultats comme si elle avait été formulée avant l’expérience.

```text
Résultat observé
       ↓
Nouvelle hypothèse
       ↓
Nouvelle expérience
```

et non :

```text
Résultat observé
       ↓
Réécriture de l’hypothèse initiale
       ↓
Prétention à une prédiction réussie
```

---

# 11. Règle contre l’optimisation du critère de succès

Le critère principal doit être choisi avant l’expérience.

Il est interdit de tester de nombreuses métriques puis de ne rapporter que celle qui devient favorable sans indiquer les autres analyses.

Les métriques secondaires peuvent être explorées, mais leur statut doit rester secondaire ou exploratoire si elles n’étaient pas pré-enregistrées.

---

# 12. Lien avec les autres documents

Ce protocole complète :

- `docs/02-hypotheses.md` ;
- `docs/regles-contribution-scientifique.md` ;
- `docs/registre-echecs-et-garde-fous.md` ;
- `docs/politique-reproductibilite.md` ;
- `docs/protocole-evaluation-independante.md`.

---

# 13. Règle finale

Un résultat moins impressionnant mais obtenu selon un protocole figé vaut davantage scientifiquement qu’un résultat spectaculaire obtenu après de multiples modifications non documentées.

Le pré-enregistrement sert à protéger SoiNesis contre le biais de son créateur, des assistants IA qui le développent et des analystes qui interprètent ses résultats.