# ADR-001 — Choix du langage principal et du socle technique

**Fichier :** `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`  
**Version :** 1.0  
**Date :** 6 août 2026  
**Statut :** acceptée  
**Décision liée :** architecture initiale de SoiNesis Core

---

## 1. Objet de la décision

Cette décision définit le langage principal et le socle technique de la première phase de SoiNesis.

Elle précède la rédaction de `docs/03-architecture-generale.md`.

Le choix doit permettre de construire un système :

- expérimental ;
- modulaire ;
- testable ;
- traçable ;
- reproductible ;
- compréhensible ;
- modifiable sans refonte massive ;
- compatible avec de futurs travaux en intelligence artificielle.

Cette décision ne définit pas encore l’architecture détaillée des modules cognitifs. Elle fixe uniquement les technologies à partir desquelles cette architecture sera conçue.

---

# 2. Contexte

SoiNesis n’est pas une application web classique.

Le projet vise à étudier des mécanismes fonctionnels potentiellement associés à la conscience artificielle, notamment :

- la mémoire autobiographique ;
- le modèle de soi ;
- la métacognition ;
- les croyances ;
- les objectifs persistants ;
- l’attention ;
- l’intégration globale ;
- le traitement récurrent ;
- la continuité temporelle ;
- l’incarnation virtuelle ;
- le développement individuel ;
- les interactions sociales ;
- l’évolution artificielle.

Le système devra permettre de comparer plusieurs conditions expérimentales, par exemple :

- mémoire active ou désactivée ;
- modèle de soi actif ou désactivé ;
- métacognition active ou désactivée ;
- incarnation active ou désactivée ;
- agent avec ou sans continuité temporelle.

Le langage principal doit donc faciliter :

- la création rapide de prototypes contrôlés ;
- la définition de modèles de données stricts ;
- les tests unitaires et d’intégration ;
- les tests d’ablation ;
- l’exécution répétée d’expériences ;
- l’analyse statistique ;
- la journalisation complète ;
- l’utilisation de modèles d’intelligence artificielle ;
- l’évolution future vers des simulations plus complexes.

---

# 3. Décision

## 3.1 Langage principal

Le langage principal de SoiNesis sera **Python**.

Python sera utilisé pour :

- le domaine métier ;
- le cycle cognitif ;
- la mémoire autobiographique ;
- les croyances ;
- le modèle de soi ;
- les objectifs ;
- la métacognition ;
- l’attention ;
- l’intégration globale ;
- l’orchestration ;
- les protocoles expérimentaux ;
- les tests d’ablation ;
- les mesures ;
- la journalisation ;
- les outils de simulation ;
- les futurs mécanismes d’apprentissage.

---

## 3.2 Version de Python

La première version du projet ciblera **Python 3.14**.

La version exacte devra être fixée dans `pyproject.toml`.

Exemple :

```toml
[project]
requires-python = ">=3.14,<3.15"
```

Une révision vers Python 3.13 restera possible uniquement si une dépendance critique nécessaire au projet n’est pas compatible avec Python 3.14.

Cette exception devra être documentée dans une nouvelle décision d’architecture.

---

## 3.3 Gestion du projet Python

Le projet utilisera :

- un fichier `pyproject.toml` ;
- un environnement virtuel local `.venv` ;
- une organisation du code sous `src/` ;
- des dépendances explicitement déclarées ;
- un verrouillage des versions lorsque le projet commencera à dépendre de bibliothèques externes critiques.

Le dossier `.venv` ne devra jamais être versionné dans Git.

---

## 3.4 Modèles de données

Les structures principales seront définies avec :

- les annotations de type Python ;
- des classes explicites ;
- des énumérations pour les valeurs fermées ;
- **Pydantic 2** lorsque la validation d’entrée, de sortie ou de persistance le justifie.

Pydantic sera notamment pertinent pour :

- les souvenirs ;
- les croyances ;
- les objectifs ;
- les états du modèle de soi ;
- les événements du journal ;
- les configurations expérimentales ;
- les résultats d’expérience.

Les modèles ne devront pas devenir de simples conteneurs génériques de dictionnaires.

Exemple de principe :

```python
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class MemorySource(StrEnum):
    DIRECT_EXPERIENCE = "direct_experience"
    RECEIVED_INFORMATION = "received_information"
    DEDUCTION = "deduction"
    IMAGINATION = "imagination"


class AutobiographicalMemory(BaseModel):
    id: str
    created_at: datetime
    source: MemorySource
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    importance: float = Field(ge=0.0, le=1.0)
```

Cet exemple n’est pas encore le modèle définitif.

Le modèle de données officiel sera défini dans `docs/04-modele-de-donnees.md`.

---

## 3.5 Persistance initiale

La première base de données sera **SQLite**.

SQLite sera utilisée pour stocker localement :

- les agents ;
- les souvenirs ;
- les croyances ;
- les objectifs ;
- les états du modèle de soi ;
- les événements du journal ;
- les expériences ;
- les résultats ;
- les versions de données ;
- les métadonnées de traçabilité.

Le fichier de base de données sera placé dans un dossier local non versionné, par exemple :

```text
data/
└── soinesis.db
```

Le dépôt pourra contenir un fichier `data/.gitkeep`, mais pas la base contenant les données réelles.

---

## 3.6 Accès à la base de données

La première version privilégiera l’accès explicite à SQLite.

Les requêtes et transactions devront rester :

- visibles ;
- testables ;
- limitées ;
- traçables.

Un ORM complet ne sera pas ajouté automatiquement.

L’utilisation future de SQLAlchemy devra être justifiée par un besoin concret, par exemple :

- multiplication des entités ;
- migrations complexes ;
- changement vers PostgreSQL ;
- requêtes relationnelles difficiles à maintenir manuellement.

---

## 3.7 Tests

Le framework de tests sera **pytest**.

Les tests seront répartis en trois catégories :

```text
tests/
├── unit/
├── integration/
└── experiments/
```

### Tests unitaires

Ils vérifieront un mécanisme isolé.

Exemples :

- validation d’un souvenir ;
- calcul d’un niveau de certitude ;
- détection d’une contradiction ;
- changement d’état d’un objectif.

### Tests d’intégration

Ils vérifieront la coopération entre plusieurs modules.

Exemples :

- ajout d’un souvenir puis utilisation dans une décision ;
- modification d’une croyance puis mise à jour du modèle de soi ;
- journalisation d’un changement important.

### Tests expérimentaux

Ils compareront plusieurs conditions.

Exemples :

- mémoire active contre mémoire désactivée ;
- modèle de soi actif contre modèle de soi absent ;
- intégration globale active contre modules isolés.

---

## 3.8 Qualité du code

Le projet utilisera progressivement les outils suivants :

- **Ruff** pour le linting et le formatage ;
- **Pyright** ou **mypy** pour la vérification statique des types ;
- **pytest** pour les tests ;
- la couverture de tests lorsque le premier noyau exécutable existera.

La sélection définitive entre Pyright et mypy sera faite lors de l’initialisation technique du dépôt.

Le projet devra éviter :

- les fonctions excessivement longues ;
- les dictionnaires sans structure ;
- les dépendances circulaires ;
- les variables globales mutables ;
- la logique cognitive dans les interfaces ;
- les effets de bord invisibles ;
- les erreurs silencieuses ;
- la modification directe des données sans journalisation.

---

## 3.9 Interface avec les modèles d’intelligence artificielle

Le noyau de SoiNesis ne devra pas dépendre directement d’un fournisseur de modèle.

Une abstraction sera définie.

Exemple conceptuel :

```python
from typing import Protocol


class LanguageModelPort(Protocol):
    def generate(self, request: "ModelRequest") -> "ModelResponse":
        ...
```

Des adaptateurs pourront ensuite être créés :

```text
OpenAIAdapter
LocalModelAdapter
MockModelAdapter
```

Le `MockModelAdapter` sera obligatoire pour les tests déterministes.

Cette séparation doit permettre :

- de changer de fournisseur ;
- de tester sans coût externe ;
- de reproduire des scénarios ;
- d’éviter que toute l’architecture dépende d’une API particulière ;
- de comparer plusieurs modèles dans les mêmes conditions.

---

## 3.10 Interface utilisateur

L’interface utilisateur ne fera pas partie du noyau cognitif.

Une future interface pourra utiliser :

- HTML ;
- CSS ;
- JavaScript vanilla.

Elle servira à :

- consulter les souvenirs ;
- inspecter le modèle de soi ;
- afficher les croyances ;
- suivre les objectifs ;
- lire le journal d’évolution ;
- configurer les expériences ;
- activer ou désactiver les ablations ;
- comparer les résultats.

L’interface ne devra pas :

- contenir la logique cognitive ;
- modifier directement la base de données ;
- contourner les règles de validation ;
- produire des changements non journalisés.

---

## 3.11 API future

**FastAPI** pourra être ajouté lorsque le noyau devra être contrôlé depuis une interface web ou un autre processus.

FastAPI n’est pas requis pour la première version en ligne de commande.

La première version doit pouvoir fonctionner de manière locale avec des commandes explicites, par exemple :

```powershell
python -m soinesis.experiments.exp_001
```

L’API ne devra être ajoutée qu’après stabilisation :

- du domaine ;
- des modèles de données ;
- du cycle cognitif ;
- de la persistance ;
- des protocoles expérimentaux.

---

## 3.12 Bibliothèques d’intelligence artificielle

PyTorch, les outils d’apprentissage par renforcement et les bibliothèques d’évolution artificielle ne seront pas ajoutés au socle initial.

Ils pourront être introduits lorsque des expériences précises l’exigeront.

Le projet ne doit pas confondre :

- utilisation d’une bibliothèque d’IA ;
- architecture cognitive ;
- mécanisme associé à la conscience ;
- preuve de conscience.

---

# 4. Architecture technologique initiale

Le socle technique prévu est le suivant :

```text
Interface future
HTML / CSS / JavaScript
          │
          │ HTTP, plus tard
          ▼
API future
FastAPI
          │
          ▼
SoiNesis Core
Python
          │
          ├── Domaine
          ├── Cycle cognitif
          ├── Orchestration
          ├── Expériences
          ├── Journalisation
          └── Adaptateurs
          │
          ▼
Persistance
SQLite
```

La première phase ne contiendra que :

```text
Ligne de commande
       │
       ▼
SoiNesis Core en Python
       │
       ▼
SQLite
```

---

# 5. Organisation initiale envisagée

La structure cible générale est :

```text
SoiNesis/
│
├── docs/
│   ├── decisions/
│   ├── 01-definitions.md
│   ├── 02-hypotheses.md
│   └── 03-architecture-generale.md
│
├── src/
│   └── soinesis/
│       ├── domain/
│       ├── cognition/
│       ├── application/
│       ├── experiments/
│       └── infrastructure/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── experiments/
│
├── data/
│   └── .gitkeep
│
├── pyproject.toml
├── .gitignore
└── README.md
```

Cette structure reste conceptuelle tant que `docs/03-architecture-generale.md` n’a pas défini précisément les responsabilités et dépendances des modules.

---

# 6. Alternatives étudiées

## 6.1 JavaScript comme langage principal

### Avantages

- déjà utilisé par Jordan ;
- simple pour créer une interface web ;
- même langage côté navigateur et serveur ;
- écosystème très large.

### Inconvénients

- moins adapté au futur environnement scientifique du projet ;
- risque de mélanger interface et logique cognitive ;
- moins naturel pour certaines analyses statistiques et expériences d’apprentissage ;
- ajout probable de Python ultérieurement ;
- typage absent sans TypeScript.

### Décision

JavaScript n’est pas retenu comme langage principal.

Il reste retenu pour une éventuelle interface web.

---

## 6.2 TypeScript comme langage principal

### Avantages

- typage plus strict que JavaScript ;
- outils de développement solides ;
- bonne maintenabilité ;
- adapté aux applications web.

### Inconvénients

- écosystème scientifique et d’apprentissage moins central que Python ;
- nécessité probable d’utiliser Python pour certaines expériences ;
- complexité supplémentaire pour Jordan ;
- risque de construire trop tôt une architecture orientée application web.

### Décision

TypeScript n’est pas retenu pour le noyau initial.

Il pourra être étudié plus tard si l’interface devient suffisamment complexe.

---

## 6.3 Rust comme langage principal

### Avantages

- performances élevées ;
- sécurité mémoire ;
- concurrence maîtrisée ;
- adapté aux simulations intensives.

### Inconvénients

- courbe d’apprentissage importante ;
- vitesse de prototypage plus faible ;
- code plus complexe ;
- inadéquation avec les besoins immédiats ;
- optimisation prématurée.

### Décision

Rust n’est pas retenu pour le noyau initial.

Il pourra être utilisé plus tard pour un composant isolé uniquement si des mesures démontrent un problème réel de performance.

---

## 6.4 C++ comme langage principal

### Avantages

- très hautes performances ;
- contrôle précis des ressources ;
- nombreuses bibliothèques scientifiques.

### Inconvénients

- complexité importante ;
- risques liés à la mémoire ;
- temps de développement élevé ;
- difficulté de maintenance ;
- peu pertinent pour la phase expérimentale initiale.

### Décision

C++ n’est pas retenu.

---

## 6.5 PostgreSQL dès le départ

### Avantages

- robuste ;
- adapté aux accès concurrents ;
- performant pour des volumes importants ;
- adapté à un déploiement serveur.

### Inconvénients

- serveur supplémentaire ;
- configuration plus complexe ;
- maintenance inutile au début ;
- déploiement prématuré ;
- moins simple à sauvegarder localement.

### Décision

PostgreSQL n’est pas retenu pour la première phase.

Une migration sera étudiée si SQLite devient une limitation mesurée.

---

## 6.6 Firebase Firestore

### Avantages

- service géré ;
- synchronisation ;
- intégration web ;
- expérience déjà acquise par Jordan.

### Inconvénients

- dépendance à un service externe ;
- coûts et quotas ;
- difficulté à garantir des expériences totalement locales ;
- structure documentaire moins adaptée à certaines relations ;
- audit et sauvegarde plus dépendants du fournisseur ;
- inutile pour un agent local unique.

### Décision

Firestore n’est pas retenu pour le noyau expérimental.

---

## 6.7 Architecture en microservices

### Avantages

- séparation forte des composants ;
- déploiement indépendant ;
- montée en charge.

### Inconvénients

- complexité opérationnelle ;
- réseau et erreurs distribuées ;
- traçabilité plus difficile ;
- tests plus lourds ;
- absence de besoin actuel.

### Décision

SoiNesis commencera comme un **monolithe modulaire**.

La séparation en services ne sera envisagée que si les limites du monolithe sont démontrées.

---

# 7. Conséquences positives

Cette décision permet :

- un développement progressif ;
- une bonne lisibilité du code ;
- l’utilisation d’un vaste écosystème scientifique ;
- des tests d’ablation automatisables ;
- une persistance locale simple ;
- une séparation entre le noyau et les fournisseurs d’IA ;
- une future interface web indépendante ;
- un apprentissage raisonnable pour Jordan ;
- l’ajout futur de PyTorch ou d’autres outils sans changer de langage principal.

---

# 8. Conséquences négatives

Cette décision implique :

- l’apprentissage de Python par Jordan ;
- l’utilisation de deux langages si une interface web est créée ;
- des performances inférieures à Rust ou C++ pour certaines simulations ;
- la nécessité d’une discipline stricte sur les types ;
- un risque de code expérimental désorganisé si l’architecture n’est pas respectée ;
- une migration possible de SQLite vers PostgreSQL à long terme.

Ces inconvénients sont acceptés pour la première phase.

---

# 9. Contraintes obligatoires

Le code initial devra respecter les règles suivantes :

1. le domaine ne dépend pas de l’interface utilisateur ;
2. le domaine ne dépend pas directement d’un fournisseur d’IA ;
3. les composants expérimentaux peuvent activer ou désactiver les mécanismes ;
4. les modifications importantes sont journalisées ;
5. les données persistantes sont validées ;
6. les tests peuvent fonctionner sans appel réel à un modèle externe ;
7. les expériences enregistrent leur configuration ;
8. les erreurs ne sont pas ignorées silencieusement ;
9. les dépendances externes sont limitées ;
10. aucune optimisation n’est ajoutée sans mesure.

---

# 10. Éléments volontairement différés

Les éléments suivants ne font pas partie du socle initial :

- FastAPI ;
- interface web ;
- PyTorch ;
- apprentissage par renforcement ;
- base vectorielle spécialisée ;
- PostgreSQL ;
- Docker ;
- microservices ;
- exécution distribuée ;
- GPU ;
- plusieurs agents simultanés ;
- évolution artificielle ;
- corps robotique ;
- modification autonome du code.

Ils pourront être ajoutés uniquement lorsqu’un besoin expérimental clairement documenté le justifiera.

---

# 11. Conditions de révision de la décision

Cette décision devra être réévaluée si l’une des conditions suivantes apparaît :

- une dépendance critique ne fonctionne pas avec la version retenue de Python ;
- SQLite ne supporte plus le volume ou la concurrence nécessaires ;
- les simulations nécessitent des performances impossibles à atteindre en Python ;
- un composant doit fonctionner sur un matériel non compatible ;
- l’interface devient une application complexe justifiant TypeScript ;
- une architecture distribuée devient nécessaire ;
- un audit indépendant identifie un risque majeur dans le socle choisi.

Toute révision devra produire un nouvel ADR.

La présente décision ne devra pas être modifiée silencieusement pour faire disparaître l’ancienne justification.

---

# 12. Validation de la décision

La décision retenue est :

```text
Langage principal : Python 3.14
Architecture initiale : monolithe modulaire
Persistance initiale : SQLite
Validation des données : annotations Python et Pydantic 2
Tests : pytest
Qualité : Ruff et vérification statique des types
Interface future : HTML, CSS et JavaScript vanilla
API future : FastAPI
IA et apprentissage avancé : ajoutés uniquement selon les expériences
```

Cette décision est considérée comme acceptée pour la rédaction de :

```text
docs/03-architecture-generale.md
```

---

# 13. Principe final

Le choix technologique doit servir la méthode scientifique de SoiNesis.

Il ne doit pas déterminer artificiellement les conclusions du projet.

Le socle initial est volontairement simple afin que chaque mécanisme puisse être :

- compris ;
- isolé ;
- testé ;
- désactivé ;
- mesuré ;
- journalisé ;
- remplacé si nécessaire.

La priorité n’est pas de construire rapidement un système impressionnant.

La priorité est de construire un système expérimental dont les résultats restent interprétables.
