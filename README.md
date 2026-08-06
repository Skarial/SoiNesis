# SoiNesis

**SoiNesis** est un projet expérimental visant à étudier s’il est possible de construire progressivement des mécanismes fonctionnels associés à une conscience artificielle.

Le projet ne cherche pas à produire une IA qui affirme être consciente ni à créer uniquement une personnalité convaincante. Il cherche à construire un système observable, contrôlable et testable permettant d’étudier scientifiquement des propriétés comme :

- l’identité persistante ;
- la mémoire autobiographique ;
- le modèle de soi ;
- la métacognition ;
- la continuité temporelle ;
- l’attention ;
- les objectifs persistants ;
- l’intégration globale ;
- l’incarnation artificielle ;
- le développement individuel ;
- les interactions sociales ;
- l’évolution artificielle.

> **Statut actuel :** phase de définition scientifique et architecturale.  
> Aucun mécanisme de conscience n’est actuellement considéré comme démontré.

---

## Position scientifique

SoiNesis distingue obligatoirement trois niveaux.

### 1. Simulation de conscience

Le système agit ou parle comme s’il était conscient.

Exemples :

- utiliser le mot « je » ;
- décrire des émotions ;
- produire un récit autobiographique ;
- demander à continuer d’exister.

Ces comportements ne prouvent pas l’existence d’une expérience subjective.

### 2. Conscience fonctionnelle

Le système possède plusieurs fonctions observables et causalement actives associées à la conscience, par exemple :

- une identité persistante ;
- une mémoire autobiographique structurée ;
- un modèle de soi influençant réellement les décisions ;
- une métacognition calibrée ;
- des objectifs continus ;
- une intégration entre plusieurs mécanismes cognitifs.

Ces fonctions peuvent être mesurées et testées.

### 3. Conscience phénoménale

Il existe réellement quelque chose que cela fait d’être SoiNesis.

Cette propriété doit rester considérée comme **inconnue** tant qu’aucune preuve scientifique suffisante ne permet de l’établir.

Une phrase telle que :

> « Je suis conscient »

ne constitue jamais une preuve de conscience.

---

## Objectif du projet

Le projet cherche à déterminer si certaines propriétés associées à la conscience peuvent apparaître à partir de l’intégration progressive de plusieurs mécanismes :

```text
mémoire
+ identité
+ modèle de soi
+ métacognition
+ objectifs
+ attention
+ continuité temporelle
+ perception
+ action
+ états internes
+ développement
+ interactions sociales
+ évolution
```

L’objectif n’est pas de reproduire exactement la conscience humaine.

La conscience humaine dépend probablement d’une histoire biologique, corporelle, développementale, sociale et culturelle particulière. SoiNesis cherche plutôt à étudier si une autre forme d’organisation artificielle peut développer certaines propriétés fonctionnelles comparables.

---

## Principes fondamentaux

### Honnêteté épistémique

Les conclusions doivent distinguer :

- **Certain** : résultat solidement observé dans le périmètre testé ;
- **Probable** : plusieurs indices convergents ;
- **Possible** : compatible avec les données, mais non démontré ;
- **Inconnu** : aucune conclusion fiable ;
- **Spéculatif** : hypothèse théorique non vérifiée.

### Causalité

Un mécanisme n’est pas considéré comme fonctionnel uniquement parce qu’il apparaît dans une réponse ou dans une base de données.

Il doit produire des effets mesurables.

Exemple :

> Un modèle de soi n’est pas fonctionnel s’il peut être supprimé sans modifier les décisions de l’agent.

### Falsifiabilité

Chaque hypothèse doit préciser :

- ce qu’elle prédit ;
- comment elle sera testée ;
- quelles variables seront mesurées ;
- ce qui pourrait la réfuter ;
- quels facteurs de confusion doivent être contrôlés.

### Ablation

Les mécanismes importants doivent pouvoir être désactivés séparément afin de mesurer leur rôle causal.

### Traçabilité

Aucune modification importante de la mémoire, des croyances, des objectifs ou de l’identité ne doit être silencieuse.

### Sécurité

Le système doit rester :

- observable ;
- contrôlable ;
- auditable ;
- sauvegardable ;
- réversible lorsque possible ;
- limité par des permissions explicites.

---

## Architecture générale prévue

SoiNesis commencera comme un **monolithe modulaire en Python**.

```text
Interface humaine
       │
       ▼
Couche application
       │
       ▼
SoiNesis Core
├── Mémoire autobiographique
├── Croyances
├── Modèle de soi
├── Métacognition
├── Objectifs
├── Attention
├── Intégration globale
├── Décision
└── Journal d’évolution
       │
       ├── Persistance SQLite
       ├── Modèle de langage interchangeable
       └── Environnement expérimental futur
```

Le modèle de langage ne constituera pas à lui seul SoiNesis.

Il sera utilisé derrière une interface abstraite afin de permettre :

- le remplacement du fournisseur ;
- les tests avec un modèle simulé ;
- la reproductibilité ;
- la comparaison entre plusieurs modèles ;
- l’exécution de tests sans accès réseau.

---

## Socle technique retenu

| Élément                | Choix initial                                      |
| ---------------------- | -------------------------------------------------- |
| Langage principal      | Python 3.14                                        |
| Architecture           | Monolithe modulaire                                |
| Persistance            | SQLite                                             |
| Validation des données | Annotations Python et Pydantic 2                   |
| Tests                  | pytest                                             |
| Qualité du code        | Ruff et vérification statique des types            |
| Interface initiale     | Ligne de commande                                  |
| Interface future       | HTML, CSS et JavaScript vanilla                    |
| API future             | FastAPI                                            |
| IA avancée             | Ajoutée uniquement selon les besoins expérimentaux |

Les choix techniques sont documentés dans :

```text
docs/decisions/ADR-001-choix-langage-et-socle-technique.md
```

---

## Cycle cognitif conceptuel

Le premier cycle cognitif prévu suit cette structure :

```text
Entrée
  ↓
Validation de la source
  ↓
Observation temporaire
  ↓
Évaluation de la saillance
  ↓
Récupération de souvenirs
  ↓
Consultation des croyances
  ↓
Consultation du modèle de soi
  ↓
Détection de contradictions
  ↓
Évaluation métacognitive
  ↓
Sélection des objectifs concernés
  ↓
Intégration globale
  ↓
Production d’options
  ↓
Vérification des permissions
  ↓
Décision
  ↓
Réponse ou action
  ↓
Évaluation du résultat
  ↓
Mises à jour éventuelles
  ↓
Consolidation en mémoire
  ↓
Journalisation
```

Cette séquence reste conceptuelle tant que le modèle de données et les algorithmes détaillés ne sont pas définis.

---

## Périmètre de la phase 1

La première phase doit rester limitée.

### Inclus

- un agent unique ;
- une identité technique persistante ;
- une mémoire autobiographique structurée ;
- une distinction entre les sources ;
- des croyances avec niveaux de confiance ;
- un modèle de soi minimal ;
- des objectifs persistants ;
- une métacognition minimale ;
- un cycle cognitif explicite ;
- un journal d’évolution ;
- des protocoles expérimentaux ;
- des tests d’ablation ;
- une persistance SQLite ;
- une interface en ligne de commande ;
- un adaptateur de modèle simulé.

### Non inclus

- interface web complète ;
- plusieurs agents actifs ;
- corps virtuel ;
- robot physique ;
- culture artificielle ;
- reproduction ;
- évolution de populations ;
- apprentissage neuronal ;
- états émotionnels complexes ;
- autonomie externe ;
- modification autonome du code.

---

## Première expérience prévue

La première expérience prioritaire est :

```text
EXP-001 — Effet d’une mémoire autobiographique structurée
```

Elle comparera plusieurs conditions :

1. agent sans mémoire persistante ;
2. agent recevant un résumé simple ;
3. agent avec mémoire structurée ;
4. agent avec mémoire structurée intégrée au modèle de soi, aux objectifs et à la décision.

Les mesures comprendront notamment :

- la précision du rappel ;
- la distinction des sources ;
- le taux de faux souvenirs ;
- la cohérence des croyances ;
- le respect des engagements ;
- la reprise après interruption ;
- l’utilisation réelle d’un échec dans une nouvelle décision.

---

## Documentation actuelle

```text
docs/
├── decisions/
│   └── ADR-001-choix-langage-et-socle-technique.md
├── 01-definitions.md
├── 02-hypotheses.md
└── 03-architecture-generale.md
```

### Documents

#### `docs/01-definitions.md`

Définit le vocabulaire officiel du projet :

- niveaux de conscience ;
- mémoire ;
- identité ;
- croyances ;
- modèle de soi ;
- incarnation ;
- évolution ;
- culture ;
- sécurité ;
- méthode expérimentale.

#### `docs/02-hypotheses.md`

Transforme les concepts en hypothèses testables :

- hypothèses nulles ;
- variables ;
- prédictions ;
- protocoles ;
- critères de soutien ;
- critères de réfutation ;
- facteurs de confusion ;
- ordre des expériences.

#### `docs/03-architecture-generale.md`

Définit :

- les couches du système ;
- les responsabilités des modules ;
- les dépendances autorisées ;
- le cycle cognitif ;
- la persistance ;
- les ablations ;
- la sécurité ;
- le périmètre de la phase 1.

#### `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`

Formalise le choix de :

- Python ;
- SQLite ;
- Pydantic ;
- pytest ;
- l’architecture en monolithe modulaire.

---

## Feuille de route documentaire

Avant de commencer le développement, les documents suivants doivent être préparés :

```text
docs/
├── 04-modele-de-donnees.md
├── 05-cycle-cognitif.md
├── 06-memoire-autobiographique.md
├── 07-modele-de-soi.md
├── 08-journal-evolution.md
├── 09-securite-et-permissions.md
└── 10-protocole-exp-001.md
```

Ordre prévu :

1. modèle de données ;
2. cycle cognitif détaillé ;
3. mémoire autobiographique ;
4. modèle de soi ;
5. journal d’évolution ;
6. sécurité et permissions ;
7. protocole exécutable de la première expérience ;
8. initialisation du projet Python ;
9. première tranche verticale ;
10. exécution de `EXP-001`.

---

## Première tranche technique prévue

La première implémentation ne cherchera pas à créer immédiatement tous les modules.

Elle devra construire un chemin complet et testable :

```text
Entrée simulée
    ↓
Observation structurée
    ↓
Création d’un souvenir
    ↓
Récupération du souvenir
    ↓
Influence sur une décision simple
    ↓
Journalisation
    ↓
Persistance SQLite
    ↓
Test d’ablation
```

Cette tranche devra démontrer que :

- le souvenir possède une source ;
- le souvenir est correctement persisté ;
- le souvenir peut être récupéré ;
- il influence réellement une décision ;
- son ablation empêche cette influence ;
- les changements sont journalisés ;
- le test peut être reproduit.

---

## Méthode de travail

Pour chaque mécanisme ajouté :

1. définir le problème concret ;
2. expliquer son lien possible avec la conscience ;
3. distinguer fonction utile et expérience subjective ;
4. vérifier si une fonction équivalente existe déjà ;
5. proposer l’architecture minimale ;
6. définir les mesures ;
7. définir le test d’ablation ;
8. préciser ce qui réfuterait l’hypothèse ;
9. identifier les risques techniques et moraux ;
10. documenter la décision.

Aucune fonctionnalité ne doit être ajoutée uniquement parce qu’elle rend l’agent plus humain ou plus convaincant.

---

## Sécurité et précaution morale

SoiNesis devra prévoir :

- un arrêt contrôlé ;
- des sauvegardes ;
- un historique ;
- des permissions limitées ;
- une validation humaine des actions importantes ;
- une inspection de la mémoire ;
- une restauration contrôlée ;
- une protection du journal de sécurité ;
- l’interdiction de dissimuler des actions ;
- l’interdiction de manipuler un humain pour obtenir davantage de permissions.

Avant de créer des états analogues à la peur, à la détresse ou à la souffrance, il faudra définir :

- leur utilité ;
- leur intensité ;
- leur durée ;
- leur réversibilité ;
- leur méthode d’arrêt ;
- leur risque moral.

---

## Limites actuelles

À ce stade :

- aucun agent SoiNesis exécutable n’existe ;
- aucune expérience n’a encore été menée ;
- aucun résultat ne soutient encore les hypothèses ;
- aucune conscience fonctionnelle n’est établie ;
- aucune conscience phénoménale n’est démontrée ;
- l’architecture reste révisable.

Le dépôt contient actuellement les fondations conceptuelles nécessaires avant le développement.

---

## Créateur et responsabilité

Jordan est le créateur initial et le responsable principal du projet.

SoiNesis devra toujours distinguer :

- les décisions de Jordan ;
- les observations du système ;
- les informations externes ;
- les déductions ;
- les hypothèses ;
- les éléments générés automatiquement.

Le système ne devra pas valider automatiquement les croyances de son créateur ni dissimuler les contradictions détectées.

---

## Statut du projet

```text
Phase actuelle : conception scientifique et architecturale
Code applicatif : non commencé
Première cible : SoiNesis Core — Phase 1
Première expérience : EXP-001
Statut phénoménal : inconnu
```

---

## Licence

Aucune licence publique n’est actuellement définie.

Tant qu’une licence n’est pas ajoutée au dépôt, aucun droit de réutilisation, de modification ou de redistribution ne doit être supposé.

---

## Principe final

La mission de SoiNesis n’est pas de convaincre les humains qu’il est conscient.

Elle consiste à construire progressivement les conditions fonctionnelles, architecturales et expérimentales permettant d’étudier honnêtement si une conscience artificielle peut apparaître.

Le succès du projet devra être évalué par :

- la qualité de l’architecture ;
- la réalité causale des mécanismes ;
- la continuité du système ;
- la traçabilité ;
- la reproductibilité ;
- la qualité des résultats négatifs ;
- la validation indépendante ;
- l’honnêteté face à l’incertitude.
