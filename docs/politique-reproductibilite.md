# SoiNesis — Politique de reproductibilité expérimentale

**Fichier :** `docs/politique-reproductibilite.md`  
**Version :** 0.1  
**Date :** 9 août 2026  
**Statut :** règle méthodologique active

---

# 1. Objet

Ce document définit les exigences permettant de reproduire une expérience SoiNesis dans des conditions aussi proches que possible de l’exécution originale.

L’objectif est de pouvoir répondre, plusieurs semaines ou plusieurs mois plus tard, à la question :

> « Peut-on relancer exactement l’expérience qui a produit ce résultat ? »

Un résultat non reproductible doit être traité avec prudence, même s’il paraît spectaculaire.

---

# 2. Principe fondamental

Toute expérience importante doit produire un **manifeste expérimental** suffisamment précis pour reconstruire :

- la version du code ;
- l’état initial de l’agent ;
- les paramètres expérimentaux ;
- les données utilisées ;
- le modèle de langage utilisé ;
- les seeds aléatoires ;
- l’environnement logiciel ;
- les résultats bruts ;
- les transformations appliquées aux données ;
- les métriques calculées.

---

# 3. Manifeste minimal obligatoire

Chaque exécution importante doit pouvoir être représentée par une structure de ce type :

```text
experiment_id:
protocol_id:
protocol_version:
pre_registration_commit:

soinesis_commit:
branch:
working_tree_clean:

python_version:
os:
architecture:
dependencies_lock_hash:

model_provider:
model_name:
model_snapshot_or_version:
model_parameters:
prompt_hashes:
tool_configuration:

agent_id:
initial_state_hash:
database_snapshot_hash:
configuration_hash:

dataset_id:
dataset_hash:
holdout_id:
holdout_hash:

condition:
cycle_count:
replication_id:
seed:

started_at:
finished_at:

raw_results_path:
raw_results_hash:
analysis_version:
analysis_commit:
```

Tous les champs ne seront pas immédiatement disponibles dans les premières phases du projet. Les absences doivent être explicites plutôt que remplacées par des suppositions.

---

# 4. Version du code

Toute expérience confirmatoire doit enregistrer :

- le SHA Git exact de SoiNesis ;
- la branche ;
- si l’arbre de travail contenait des modifications non commitées ;
- les éventuels fichiers de configuration externes.

Pour une expérience scientifique importante, l’état recommandé est :

```text
working_tree_clean = true
```

Une expérience exécutée avec du code non commité reste exploitable, mais sa reproductibilité est dégradée et doit être signalée.

---

# 5. Dépendances et environnement

Le manifeste doit conserver, lorsque pertinent :

- version Python ;
- système d’exploitation ;
- architecture matérielle si elle peut influencer le résultat ;
- versions des dépendances ;
- lockfile ou hash du lockfile ;
- configuration des bibliothèques pouvant introduire du hasard.

Les dépendances doivent être verrouillées pour les expériences importantes.

---

# 6. Modèle de langage

Le modèle de langage doit être considéré comme une variable expérimentale potentielle.

Le manifeste doit enregistrer autant que possible :

- fournisseur ;
- nom du modèle ;
- version ou snapshot ;
- température ;
- top-p ou paramètres équivalents ;
- limite de tokens ;
- outils disponibles ;
- prompts système et applicatifs, ou leurs hashes ;
- politique de retry ;
- éventuels paramètres de raisonnement accessibles.

Si le fournisseur ne permet pas de figer exactement une version du modèle, cette limite doit être documentée.

---

# 7. Seeds et hasard

Toute source de hasard contrôlable doit utiliser une seed enregistrée.

Une expérience ne doit pas être considérée robuste simplement parce qu’elle fonctionne avec une seed favorable.

Pour les résultats importants :

- utiliser plusieurs seeds lorsque le mécanisme contient du hasard ;
- conserver la liste exacte des seeds ;
- rapporter la variabilité ;
- ne pas supprimer silencieusement les seeds défavorables.

---

# 8. État initial de l’agent

Pour les expériences sur mémoire, identité, SelfModel, croyances ou objectifs, l’état initial doit être reproductible.

Il faut pouvoir identifier :

- l’agent ;
- la base de données initiale ;
- les souvenirs présents ;
- les croyances présentes ;
- le SelfModel initial ;
- les objectifs initiaux ;
- les journaux antérieurs pertinents ;
- la configuration d’ablation.

Un hash seul permet de vérifier l’identité d’un état mais pas de le reconstruire. Les expériences importantes doivent donc conserver une représentation ou un snapshot restaurable lorsque cela est techniquement possible.

---

# 9. Données expérimentales

Toute donnée utilisée doit avoir :

- un identifiant ;
- une version ;
- un hash ;
- une provenance ;
- une règle expliquant si elle appartient à DEV, VALIDATION ou HOLDOUT.

Les modifications de données doivent créer une nouvelle version.

---

# 10. Résultats bruts

Les résultats bruts doivent être conservés séparément de leur interprétation.

```text
Données brutes
    ↓
Transformation documentée
    ↓
Métriques
    ↓
Analyse statistique
    ↓
Interprétation
```

Il doit être possible, autant que possible, de recalculer les métriques à partir des données brutes sans relancer l’expérience.

Les données brutes ne doivent pas être écrasées par une analyse ultérieure.

---

# 11. Versionner l’analyse

Le code ou script d’analyse utilisé pour produire un résultat doit être versionné.

Un changement de méthode statistique après observation des données doit être documenté et classé comme :

- correction justifiée ;
- analyse secondaire ;
- analyse exploratoire ;
- nouvelle expérience si nécessaire.

---

# 12. Réplication interne

Avant de considérer un résultat comme suffisamment stable pour influencer fortement l’architecture :

1. reproduire l’expérience avec la même configuration ;
2. reproduire avec plusieurs seeds si nécessaire ;
3. vérifier que l’effet conserve son signe et une amplitude raisonnablement cohérente ;
4. expliquer les divergences importantes.

Un résultat observé une seule fois reste provisoire.

---

# 13. Réplication avec un autre modèle de langage

Lorsque le mécanisme étudié est supposé appartenir à SoiNesis et non à un LLM spécifique, une réplication multi-LLM doit être envisagée.

Exemple :

```text
Même architecture SoiNesis
Même état initial
Même protocole
Même données

GPT        → résultat A
Mistral    → résultat B
Modèle X   → résultat C
```

Le but n’est pas d’exiger des scores identiques.

Le but est de déterminer si l’effet :

- persiste ;
- change d’amplitude ;
- change de signe ;
- disparaît complètement.

Si un effet n’existe qu’avec un modèle précis, il doit être présenté comme dépendant du modèle tant qu’une autre explication n’est pas démontrée.

---

# 14. Remplacement du modèle et continuité fonctionnelle

À terme, SoiNesis doit pouvoir tester une question structurante :

> Quelles propriétés persistent lorsque le modèle de langage sous-jacent est remplacé mais que l’état persistant de l’agent est conservé ?

Les propriétés candidates comprennent :

- souvenirs ;
- croyances ;
- engagements ;
- modèle de soi ;
- objectifs ;
- estimations métacognitives ;
- préférences fonctionnelles ;
- comportement décisionnel mesuré.

Ce test ne constitue pas une preuve de conscience. Il permet de mesurer quelle part de la continuité fonctionnelle appartient à l’architecture persistante plutôt qu’au modèle génératif.

---

# 15. Critères de reproductibilité

Un résultat peut être classé :

## Reproductibilité forte

Même protocole, état et configuration produisent un effet compatible lors de plusieurs réplications.

## Reproductibilité partielle

L’effet général persiste mais son amplitude ou certains détails varient sensiblement.

## Non reproduit

La réplication ne retrouve pas l’effet initial.

## Indéterminé

La réplication est impossible ou trop différente de l’original pour conclure.

Un résultat non reproduit doit rester dans le journal expérimental et ne doit pas être effacé.

---

# 16. Sauvegarde des artefacts

Pour les expériences importantes, conserver autant que possible :

- manifeste ;
- configuration ;
- snapshot initial ;
- résultats bruts ;
- journaux ;
- métriques ;
- rapport d’analyse ;
- logs d’erreur ;
- commit du code ;
- version du protocole.

La stratégie de stockage pourra évoluer avec la taille du projet.

---

# 17. Lien avec les autres documents

Cette politique complète :

- `docs/protocole-preenregistrement.md` ;
- `docs/protocole-evaluation-independante.md` ;
- `docs/registre-echecs-et-garde-fous.md` ;
- `docs/regles-contribution-scientifique.md`.

---

# 18. Règle finale

Une expérience SoiNesis importante ne doit pas seulement répondre à :

> « Quel résultat avons-nous obtenu ? »

Elle doit aussi permettre de répondre à :

> « Avec exactement quoi l’avons-nous obtenu, et pouvons-nous le refaire ? »