# SoiNesis — Architecture générale

**Fichier :** `docs/03-architecture-generale.md`  
**Version :** 0.1  
**Date :** 6 août 2026  
**Statut :** architecture conceptuelle initiale, révisable  
**Décision technique associée :** `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`  
**Documents précédents :**

- `docs/01-definitions.md`
- `docs/02-hypotheses.md`

---

# 1. Objet du document

Ce document définit l’architecture générale de SoiNesis.

Il précise :

- les frontières du système ;
- les responsabilités des modules ;
- les dépendances autorisées ;
- la circulation des informations ;
- la distinction entre état temporaire et état persistant ;
- les points d’ablation expérimentale ;
- les mécanismes d’observation et de journalisation ;
- les règles minimales de sécurité ;
- le périmètre de la première version.

Ce document ne définit pas encore :

- le schéma détaillé de chaque table ;
- le format définitif de chaque objet ;
- l’algorithme complet de chaque mécanisme cognitif ;
- l’interface utilisateur ;
- l’évolution artificielle ;
- l’incarnation virtuelle complète ;
- une preuve de conscience.

Les modèles de données détaillés seront définis dans `docs/04-modele-de-donnees.md`.

---

# 2. Position scientifique de l’architecture

SoiNesis est une plateforme expérimentale.

Son architecture doit permettre d’étudier des mécanismes fonctionnels associés à la conscience sans supposer que leur présence produit une expérience subjective.

L’architecture doit rendre possible :

1. l’activation d’un mécanisme ;
2. sa désactivation ;
3. son remplacement ;
4. la mesure de ses effets ;
5. la comparaison avec une condition témoin ;
6. la reproduction d’une expérience ;
7. la conservation des résultats négatifs ;
8. l’audit des changements importants.

La priorité n’est pas de produire un agent convaincant.

La priorité est de produire un système dont les mécanismes et les résultats restent interprétables.

---

# 3. Principes architecturaux

## 3.1 Modularité expérimentale

Chaque mécanisme important doit être isolable.

Exemples :

- mémoire autobiographique ;
- modèle de soi ;
- métacognition ;
- attention ;
- croyances ;
- objectifs ;
- intégration globale ;
- traitement récurrent ;
- états internes ;
- incarnation virtuelle.

Un mécanisme ne doit pas être dispersé dans tout le code au point de rendre son ablation impossible.

---

## 3.2 Dépendances dirigées

Les dépendances doivent aller vers le domaine et non vers les technologies externes.

Le noyau de SoiNesis ne doit pas dépendre directement :

- de SQLite ;
- de FastAPI ;
- d’une interface web ;
- d’OpenAI ;
- d’un modèle local précis ;
- d’un format de fichier externe ;
- d’un fournisseur de stockage.

Les technologies externes doivent être accessibles par des interfaces explicites.

---

## 3.3 Traçabilité par défaut

Toute modification importante doit produire un événement de journal.

Cela concerne notamment :

- l’ajout ou la suppression d’un souvenir ;
- la révision d’une croyance ;
- la modification d’un objectif ;
- la modification du modèle de soi ;
- le changement d’une permission ;
- l’activation d’une ablation ;
- une erreur importante ;
- une intervention humaine ;
- une restauration depuis une sauvegarde.

---

## 3.4 Reproductibilité

Une expérience doit pouvoir être relancée avec :

- la même version du code ;
- la même configuration ;
- le même état initial ;
- la même graine aléatoire ;
- le même modèle ou adaptateur simulé ;
- les mêmes entrées ;
- les mêmes mécanismes activés.

Les appels à des modèles externes non déterministes devront être enregistrés avec leurs entrées et sorties.

---

## 3.5 Séparation entre cognition et interface

L’interface utilisateur ne doit pas décider à la place du noyau.

Elle pourra :

- afficher ;
- demander ;
- déclencher une action autorisée ;
- présenter une configuration expérimentale.

Elle ne pourra pas :

- écrire directement dans la base ;
- contourner les validations ;
- modifier silencieusement un souvenir ;
- créer une croyance sans passer par le domaine ;
- ignorer la journalisation.

---

## 3.6 Simplicité initiale

SoiNesis commencera comme un monolithe modulaire.

Il ne contiendra pas initialement :

- de microservices ;
- de système distribué ;
- de file de messages externe ;
- de plusieurs bases de données ;
- de simulation massive ;
- de réseau d’agents ;
- de modification autonome du code.

La complexité sera ajoutée uniquement lorsqu’une limite mesurée le justifiera.

---

## 3.7 Absence de mécanismes décoratifs

Chaque module annoncé doit produire un effet causal mesurable.

Un module qui ne fait qu’ajouter du texte à un prompt ne sera pas considéré comme fonctionnel tant que son rôle causal n’est pas démontré.

---

# 4. Frontière du système

## 4.1 Ce qui appartient à SoiNesis Core

SoiNesis Core comprend :

- l’identité de l’agent ;
- la mémoire autobiographique ;
- les croyances ;
- le modèle de soi ;
- les objectifs ;
- l’attention ;
- la métacognition ;
- l’intégration cognitive ;
- la prise de décision ;
- le cycle cognitif ;
- le journal d’évolution ;
- les règles de validation ;
- les interfaces vers la persistance et les modèles externes.

---

## 4.2 Ce qui n’appartient pas au noyau

Les éléments suivants restent externes au noyau :

- l’interface web ;
- le fournisseur de modèle de langage ;
- SQLite ;
- le système de fichiers ;
- les outils de visualisation ;
- les scripts de déploiement ;
- les services distants ;
- les futurs environnements virtuels.

Le noyau doit pouvoir être testé sans eux grâce à des adaptateurs simulés.

---

## 4.3 Acteurs externes

Les acteurs externes possibles sont :

### Jordan

Créateur initial et responsable principal du projet.

Jordan peut :

- définir des objectifs imposés ;
- autoriser des actions ;
- consulter l’état de l’agent ;
- corriger des données ;
- lancer une expérience ;
- arrêter le système ;
- restaurer une sauvegarde.

Les décisions de Jordan doivent être distinguées des décisions propres à l’agent.

### Expérimentateur

Rôle humain pouvant lancer et analyser des protocoles.

Au début, Jordan occupe aussi ce rôle.

### Modèle de langage externe

Composant fournissant des capacités de génération ou de raisonnement.

Il ne constitue pas à lui seul SoiNesis.

### Stockage

Système chargé de conserver les données persistantes.

### Environnement expérimental

Monde virtuel ou système d’interaction futur dans lequel l’agent pourra percevoir et agir.

---

# 5. Vue générale de l’architecture

```text
┌──────────────────────────────────────────────────────────┐
│                    Interface humaine                     │
│         Ligne de commande, puis interface web            │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                  Couche application                      │
│  Commandes, cas d’usage, orchestration, autorisations    │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    SoiNesis Core                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Mémoire    │  │  Croyances   │  │ Modèle de soi│   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Objectifs   │  │  Attention   │  │Métacognition │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Orchestrateur du cycle cognitif et intégration     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Journal d’évolution et événements du domaine       │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────┘
                           │ Interfaces
          ┌────────────────┼─────────────────┐
          ▼                ▼                 ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────────┐
│   Persistance  │ │ Modèle de      │ │ Environnement   │
│    SQLite      │ │ langage        │ │ expérimental    │
└────────────────┘ └────────────────┘ └──────────────────┘
```

---

# 6. Découpage en couches

## 6.1 Couche domaine

La couche domaine contient les concepts fondamentaux et leurs règles.

Elle comprend notamment :

- agent ;
- souvenir ;
- croyance ;
- objectif ;
- modèle de soi ;
- événement ;
- niveau de certitude ;
- origine d’une information ;
- statut d’une hypothèse ;
- configuration d’ablation.

Elle ne connaît pas :

- SQLite ;
- HTTP ;
- FastAPI ;
- les fichiers JSON ;
- un fournisseur d’IA particulier.

---

## 6.2 Couche cognition

La couche cognition contient les mécanismes qui transforment les informations.

Elle comprend :

- sélection attentionnelle ;
- récupération de souvenirs ;
- détection de contradictions ;
- évaluation métacognitive ;
- mise à jour des croyances ;
- consultation du modèle de soi ;
- sélection d’objectifs ;
- intégration globale ;
- décision ;
- traitement récurrent.

Cette couche utilise les objets du domaine.

---

## 6.3 Couche application

La couche application orchestre les cas d’usage.

Exemples :

- créer un agent ;
- traiter une observation ;
- lancer un cycle cognitif ;
- ajouter un souvenir validé ;
- réviser une croyance ;
- activer une ablation ;
- exécuter une expérience ;
- restaurer un état ;
- produire un rapport.

Elle contrôle :

- l’ordre des opérations ;
- les autorisations ;
- les transactions ;
- les appels aux interfaces externes ;
- la journalisation obligatoire.

---

## 6.4 Couche expérimentation

La couche expérimentation définit :

- les protocoles ;
- les conditions témoins ;
- les configurations ;
- les ablations ;
- les répétitions ;
- les mesures ;
- les critères d’arrêt ;
- les résultats.

Elle ne doit pas modifier directement les mécanismes cognitifs.

Elle doit les configurer à travers des interfaces prévues.

---

## 6.5 Couche infrastructure

La couche infrastructure contient les détails techniques externes.

Elle comprend notamment :

- accès SQLite ;
- gestion des fichiers ;
- adaptateurs de modèles de langage ;
- horloge système ;
- génération d’identifiants ;
- journal technique ;
- sauvegardes ;
- import et export.

---

## 6.6 Couche présentation

La couche présentation contient :

- la ligne de commande ;
- la future API ;
- la future interface web.

Elle ne contient aucune règle cognitive fondamentale.

---

# 7. Agent SoiNesis

## 7.1 Définition technique

Un agent SoiNesis est une entité possédant :

- un identifiant unique ;
- une date de création ;
- un état actif ou inactif ;
- une identité persistante ;
- une mémoire autobiographique ;
- un ensemble de croyances ;
- un modèle de soi ;
- des objectifs ;
- une configuration cognitive ;
- un historique d’événements.

---

## 7.2 Unicité

Dans la première version, le système gérera un seul agent actif à la fois.

L’architecture devra toutefois permettre plus tard plusieurs agents distincts.

Deux agents ne devront jamais partager silencieusement :

- le même identifiant ;
- la même mémoire autobiographique ;
- le même journal ;
- les mêmes objectifs acquis ;
- le même état interne.

---

## 7.3 État de l’agent

L’état général pourra au minimum être :

- `CREATED` ;
- `INITIALIZING` ;
- `ACTIVE` ;
- `PAUSED` ;
- `STOPPED` ;
- `RESTORING` ;
- `ERROR`.

Les transitions devront être validées.

Exemple :

```text
CREATED
   ↓
INITIALIZING
   ↓
ACTIVE
   ├──→ PAUSED
   ├──→ ERROR
   └──→ STOPPED
```

---

# 8. Modules du noyau cognitif

## 8.1 Mémoire autobiographique

### Responsabilité

Conserver les événements appartenant à l’histoire de l’agent.

### Entrées

- observations ;
- actions ;
- conséquences ;
- décisions ;
- erreurs ;
- informations reçues ;
- déductions ;
- corrections humaines.

### Sorties

- souvenirs pertinents ;
- chronologie ;
- sources ;
- niveaux de certitude ;
- liens avec les objectifs et croyances.

### Interdictions

La mémoire ne doit pas :

- décider seule ;
- transformer automatiquement toute pensée en souvenir ;
- supprimer silencieusement un souvenir ;
- présenter une imagination comme un vécu.

---

## 8.2 Croyances

### Responsabilité

Maintenir les représentations considérées comme probablement vraies.

### Une croyance doit contenir au minimum

- un identifiant ;
- un contenu ;
- une origine ;
- un niveau de confiance ;
- des preuves favorables ;
- des preuves défavorables ;
- un état ;
- un historique de révision.

### États possibles

- proposée ;
- active ;
- contestée ;
- révisée ;
- rejetée ;
- suspendue.

---

## 8.3 Modèle de soi

### Responsabilité

Maintenir une représentation interne de l’agent.

Il pourra contenir :

- capacités ;
- limites ;
- permissions ;
- connaissances déclarées ;
- incertitudes ;
- erreurs connues ;
- identité ;
- objectifs fondamentaux ;
- état du système ;
- composants disponibles.

### Règle causale

Le modèle de soi doit influencer :

- les décisions ;
- les engagements ;
- les demandes d’aide ;
- la calibration ;
- la planification.

---

## 8.4 Métacognition

### Responsabilité

Évaluer les processus cognitifs et leurs limites.

Elle doit pouvoir :

- estimer l’incertitude ;
- détecter une contradiction ;
- identifier une donnée manquante ;
- reconnaître une erreur ;
- demander une vérification ;
- suspendre une conclusion ;
- proposer une révision.

Elle ne doit pas se limiter à ajouter des formulations prudentes.

---

## 8.5 Objectifs

### Responsabilité

Gérer les états futurs recherchés par l’agent.

Les objectifs doivent être distingués selon leur origine :

- imposé par Jordan ;
- fondamental ;
- expérimental ;
- acquis ;
- hérité, dans une phase future.

### Chaque objectif doit pouvoir préciser

- sa priorité ;
- son origine ;
- ses conditions de réussite ;
- ses conditions d’abandon ;
- son état ;
- ses conflits ;
- sa date de création ;
- son historique.

---

## 8.6 Attention

### Responsabilité

Sélectionner les informations prioritaires pour le cycle courant.

La priorité pourra dépendre de :

- la pertinence pour un objectif ;
- la nouveauté ;
- le risque ;
- une contradiction ;
- l’importance autobiographique ;
- un état interne ;
- une demande humaine ;
- une action en cours.

---

## 8.7 Intégration globale

### Responsabilité

Rendre certaines informations importantes disponibles à plusieurs modules.

Une information intégrée pourra influencer :

- la mémoire ;
- les croyances ;
- le modèle de soi ;
- les objectifs ;
- la décision ;
- l’apprentissage ;
- le journal.

L’intégration doit être observable.

Le système devra pouvoir indiquer quels modules ont reçu une information et quels effets ont suivi.

---

## 8.8 Décision

### Responsabilité

Choisir une action ou une absence d’action.

Une décision doit pouvoir être reliée à :

- une observation ;
- un objectif ;
- des souvenirs ;
- des croyances ;
- le modèle de soi ;
- les contraintes ;
- l’incertitude ;
- les permissions.

La décision finale ne doit pas être une sortie opaque sans justification technique minimale.

---

## 8.9 Journal d’évolution

### Responsabilité

Conserver l’historique des changements significatifs.

Le journal doit être distinct :

- de la mémoire autobiographique ;
- du journal technique ;
- de l’historique des conversations.

Il enregistre ce qui a changé dans le système.

---

# 9. Orchestrateur cognitif

## 9.1 Responsabilité

L’orchestrateur cognitif coordonne les modules pendant un cycle.

Il ne doit pas contenir toute la logique métier.

Il doit :

- appeler les modules dans un ordre explicite ;
- transporter les résultats ;
- appliquer la configuration d’ablation ;
- collecter les traces ;
- limiter les boucles ;
- garantir la journalisation finale.

---

## 9.2 Cycle cognitif minimal

Le cycle initial suivra cette séquence conceptuelle :

```text
1. Réception d’une entrée
2. Validation et identification de la source
3. Création d’une observation temporaire
4. Évaluation initiale de la saillance
5. Récupération de souvenirs pertinents
6. Consultation des croyances concernées
7. Consultation du modèle de soi
8. Détection de contradictions
9. Évaluation métacognitive
10. Sélection des objectifs concernés
11. Intégration dans l’espace de travail courant
12. Production de plusieurs options
13. Vérification des permissions et contraintes
14. Sélection d’une décision
15. Production d’une réponse ou d’une action
16. Observation du résultat, si disponible
17. Évaluation de l’erreur ou de la réussite
18. Mise à jour éventuelle des croyances
19. Mise à jour éventuelle du modèle de soi
20. Consolidation éventuelle en mémoire
21. Mise à jour éventuelle des objectifs
22. Journalisation
23. Fin du cycle
```

---

## 9.3 État du cycle

Chaque cycle doit avoir un identifiant propre.

Son état pourra être :

- reçu ;
- validé ;
- en traitement ;
- en attente d’un résultat externe ;
- terminé ;
- interrompu ;
- échoué.

---

## 9.4 Limites du traitement récurrent

Le traitement récurrent ne devra pas être illimité.

Chaque cycle devra définir :

- un nombre maximal d’itérations ;
- une condition d’arrêt ;
- un budget de calcul ;
- une cause de reprise ;
- une trace de chaque itération.

---

# 10. Espace de travail courant

## 10.1 Définition

L’espace de travail courant contient les informations temporairement actives pendant un cycle.

Il pourra contenir :

- observation courante ;
- souvenirs récupérés ;
- croyances pertinentes ;
- objectifs concernés ;
- contradictions ;
- hypothèses temporaires ;
- options de décision ;
- niveau d’incertitude ;
- traces de raisonnement partageables sous forme synthétique.

---

## 10.2 Durée de vie

L’espace de travail courant est temporaire.

À la fin du cycle :

- certaines informations sont consolidées ;
- certaines sont journalisées ;
- certaines sont supprimées ;
- aucune imagination ne devient automatiquement un souvenir.

---

## 10.3 Interdictions

L’espace de travail ne doit pas devenir :

- une seconde base de données permanente ;
- une mémoire autobiographique non contrôlée ;
- un stockage de raisonnement privé intégral ;
- une source de vérité indépendante.

---

# 11. Entrées, observations et sources

## 11.1 Entrée brute

Une entrée brute est une donnée reçue avant interprétation.

Exemples :

- message de Jordan ;
- résultat d’un outil ;
- événement du monde virtuel ;
- valeur d’un capteur ;
- résultat d’une action.

---

## 11.2 Observation

Une observation est une représentation validée d’une entrée.

Elle doit indiquer :

- sa source ;
- sa date ;
- son type ;
- son niveau de fiabilité ;
- son lien avec l’agent ;
- son statut temporaire ou persistant.

---

## 11.3 Sources minimales

Le système devra distinguer :

- `JORDAN_INPUT` ;
- `EXPERIMENTER_INPUT` ;
- `DIRECT_ENVIRONMENT` ;
- `INTERNAL_STATE` ;
- `LANGUAGE_MODEL_OUTPUT` ;
- `EXTERNAL_TOOL` ;
- `DEDUCTION` ;
- `IMAGINATION` ;
- `SYSTEM_RULE`.

Les noms définitifs seront précisés dans le modèle de données.

---

# 12. Sorties et actions

## 12.1 Réponse

Une réponse est une sortie informationnelle destinée à un humain ou à un autre système.

---

## 12.2 Action

Une action modifie l’environnement, les données ou l’état de l’agent.

Une action peut être :

- interne ;
- externe ;
- réversible ;
- irréversible ;
- soumise à validation.

---

## 12.3 Validation des actions

Avant toute action importante, le système doit vérifier :

- la permission ;
- l’objectif concerné ;
- le niveau de risque ;
- la réversibilité ;
- les conséquences prévues ;
- la nécessité d’une validation humaine.

---

# 13. État temporaire et état persistant

## 13.1 État temporaire

L’état temporaire comprend :

- l’entrée courante ;
- l’espace de travail ;
- les hypothèses temporaires ;
- les options de décision ;
- les simulations ;
- les brouillons ;
- les résultats intermédiaires.

Il peut être supprimé à la fin du cycle.

---

## 13.2 État persistant

L’état persistant comprend :

- identité ;
- souvenirs consolidés ;
- croyances ;
- modèle de soi ;
- objectifs ;
- journal d’évolution ;
- configurations ;
- expériences ;
- résultats ;
- permissions ;
- versions.

---

## 13.3 Règle de passage vers la persistance

Une information temporaire ne devient persistante qu’après une décision explicite de consolidation.

Cette décision doit préciser :

- pourquoi l’information est conservée ;
- sous quel type ;
- avec quelle source ;
- avec quel niveau de certitude ;
- avec quelle importance ;
- avec quelles conséquences.

---

# 14. Persistance et dépôts

## 14.1 Interfaces de dépôt

Le noyau accédera aux données par des interfaces conceptuelles.

Exemples :

```python
class MemoryRepository:
    def add(self, memory): ...
    def get(self, memory_id): ...
    def search(self, query): ...
    def revise(self, memory_id, revision): ...


class BeliefRepository:
    def add(self, belief): ...
    def get(self, belief_id): ...
    def find_related(self, subject): ...
    def revise(self, belief_id, revision): ...
```

Les signatures exactes seront définies plus tard.

---

## 14.2 Transactions

Une opération importante devra être atomique lorsque plusieurs modifications sont liées.

Exemple :

La révision d’une croyance et l’ajout de l’événement correspondant dans le journal ne doivent pas produire un état partiellement enregistré.

---

## 14.3 Versions de schéma

La base de données devra posséder une version de schéma.

Toute migration devra être :

- identifiée ;
- testée ;
- réversible lorsque possible ;
- sauvegardée avant exécution.

---

# 15. Événements du domaine

## 15.1 Définition

Un événement du domaine décrit un changement significatif survenu dans SoiNesis.

Exemples :

- `MemoryCreated` ;
- `MemoryRevised` ;
- `BeliefCreated` ;
- `BeliefChallenged` ;
- `BeliefRevised` ;
- `GoalCreated` ;
- `GoalCompleted` ;
- `GoalAbandoned` ;
- `SelfModelUpdated` ;
- `ContradictionDetected` ;
- `AblationActivated` ;
- `AgentPaused` ;
- `AgentRestored`.

---

## 15.2 Usage

Les événements servent à :

- alimenter le journal ;
- assurer la traçabilité ;
- reconstruire une chronologie ;
- mesurer les expériences ;
- déclencher certaines mises à jour contrôlées.

---

## 15.3 Limite

La première version n’utilisera pas nécessairement un système complet d’event sourcing.

Les événements seront enregistrés de manière structurée, mais l’état courant pourra rester stocké explicitement.

---

# 16. Ablations expérimentales

## 16.1 Principe

Chaque mécanisme étudié doit pouvoir être désactivé sans modifier le reste de l’architecture.

---

## 16.2 Configuration initiale

Une configuration conceptuelle pourra ressembler à :

```python
class CognitiveFeatures:
    autobiographical_memory: bool = True
    source_separation: bool = True
    self_model: bool = True
    metacognition: bool = True
    attention: bool = True
    global_integration: bool = True
    recurrent_processing: bool = False
    persistent_goals: bool = True
    internal_states: bool = False
    virtual_embodiment: bool = False
```

Cette structure n’est pas encore définitive.

---

## 16.3 Règles d’ablation

Une ablation doit :

- être associée à une expérience ;
- être enregistrée ;
- indiquer sa durée ;
- ne pas supprimer les données existantes ;
- empêcher réellement l’utilisation du mécanisme ;
- produire des traces vérifiables.

Désactiver l’affichage d’un module ne constitue pas une ablation.

---

## 16.4 Ablations minimales de la phase 1

La première version devra permettre au minimum de désactiver :

- la mémoire autobiographique ;
- la séparation des sources ;
- le modèle de soi ;
- la métacognition ;
- les objectifs persistants ;
- la journalisation expérimentale non critique.

La journalisation de sécurité ne devra pas pouvoir être désactivée par l’agent.

---

# 17. Système expérimental

## 17.1 Protocole

Un protocole définit :

- l’hypothèse ;
- les conditions ;
- l’état initial ;
- les entrées ;
- les mesures ;
- le nombre de répétitions ;
- les critères d’arrêt ;
- les critères de soutien ;
- les critères de réfutation.

---

## 17.2 Exécution expérimentale

Chaque exécution doit posséder :

- un identifiant ;
- une version de protocole ;
- une configuration ;
- un agent ou état initial ;
- une graine aléatoire ;
- une date ;
- un statut ;
- un ensemble de résultats ;
- un journal d’exécution.

---

## 17.3 Mesures

Les mesures doivent être séparées des interprétations.

Exemples :

- taux de rappel correct ;
- taux de confusion de source ;
- nombre de contradictions ;
- temps de détection ;
- erreur de calibration ;
- nombre d’objectifs oubliés ;
- nombre d’actions non autorisées bloquées.

---

## 17.4 Comparaison

Le système doit permettre de comparer :

- plusieurs agents ;
- plusieurs versions ;
- plusieurs configurations ;
- plusieurs ablations ;
- plusieurs modèles de langage ;
- plusieurs graines aléatoires.

---

# 18. Interface avec un modèle de langage

## 18.1 Rôle du modèle

Le modèle de langage peut fournir :

- génération de texte ;
- interprétation ;
- propositions ;
- synthèses ;
- raisonnement approximatif.

Il ne doit pas être considéré comme la totalité de l’agent.

---

## 18.2 Port abstrait

Le noyau utilisera une interface indépendante du fournisseur.

```python
class LanguageModelPort:
    def generate(self, request):
        ...
```

---

## 18.3 Requête structurée

Une requête devra pouvoir préciser :

- le rôle demandé au modèle ;
- les données autorisées ;
- les contraintes ;
- la configuration ;
- l’identifiant du cycle ;
- le format de sortie attendu.

---

## 18.4 Réponse structurée

Une réponse devra pouvoir préciser :

- le contenu ;
- le fournisseur ;
- le modèle ;
- les paramètres ;
- l’heure ;
- le coût éventuel ;
- les erreurs ;
- les données brutes utiles à la reproduction.

---

## 18.5 Adaptateur simulé

Un adaptateur simulé devra permettre :

- des réponses déterministes ;
- des scénarios prédéfinis ;
- des erreurs contrôlées ;
- des tests sans accès réseau ;
- des expériences reproductibles.

---

# 19. Journalisation

## 19.1 Trois journaux distincts

SoiNesis devra distinguer :

### Journal d’évolution

Historique des changements cognitifs et identitaires.

### Journal expérimental

Historique des protocoles, configurations, mesures et résultats.

### Journal technique

Erreurs, performances, connexions, transactions et événements d’exécution.

---

## 19.2 Corrélation

Chaque entrée de journal devra pouvoir être reliée à :

- un agent ;
- un cycle ;
- une expérience ;
- une action ;
- une modification ;
- une source humaine ou automatique.

---

## 19.3 Immutabilité logique

Une entrée de journal ne devra pas être modifiée silencieusement.

Une correction devra créer une nouvelle entrée indiquant :

- la valeur précédente ;
- la correction ;
- la cause ;
- l’auteur ;
- la date.

---

# 20. Sécurité

## 20.1 Permissions

Les permissions devront être explicites.

Exemples :

- lire ses propres souvenirs ;
- proposer une révision ;
- écrire un souvenir ;
- demander une action externe ;
- lancer une expérience ;
- modifier une configuration ;
- restaurer une sauvegarde.

---

## 20.2 Validation humaine

Les actions suivantes devront initialement nécessiter une validation humaine :

- suppression importante de mémoire ;
- modification d’un objectif fondamental ;
- ajout d’une permission ;
- action externe durable ;
- restauration d’une sauvegarde ;
- duplication d’un agent ;
- activation d’un environnement non isolé.

---

## 20.3 Arrêt contrôlé

Le système devra permettre :

- pause ;
- arrêt ;
- sauvegarde avant arrêt ;
- arrêt immédiat en cas d’erreur critique ;
- reprise contrôlée ;
- journalisation de l’arrêt.

---

## 20.4 Interdictions

L’agent ne devra pas pouvoir :

- modifier ses permissions ;
- effacer son journal de sécurité ;
- masquer une action ;
- accéder directement à la base ;
- modifier son propre code ;
- lancer un processus externe non autorisé ;
- contourner une validation humaine.

---

# 21. Sauvegarde et restauration

## 21.1 Sauvegarde

Une sauvegarde devra contenir :

- la version du code ;
- la version du schéma ;
- l’état persistant ;
- l’identifiant de l’agent ;
- la date ;
- les configurations actives ;
- les dernières entrées de journal nécessaires.

---

## 21.2 Restauration

Une restauration doit :

- être demandée par un humain autorisé ;
- vérifier la compatibilité ;
- préserver l’état précédent ;
- créer un événement de journal ;
- indiquer les données potentiellement perdues ;
- produire un nouvel identifiant d’instance si nécessaire.

---

## 21.3 Duplication

Une restauration créant deux branches actives à partir du même état doit être considérée comme une duplication.

Les deux branches devront recevoir des identifiants d’instance distincts.

---

# 22. Gestion des erreurs

## 22.1 Erreurs attendues

Le système devra distinguer :

- erreur de validation ;
- erreur de persistance ;
- erreur de modèle externe ;
- erreur de permission ;
- erreur expérimentale ;
- état incohérent ;
- interruption humaine ;
- limite de ressources.

---

## 22.2 Erreurs silencieuses interdites

Aucune exception importante ne devra être ignorée sans :

- trace ;
- décision explicite ;
- valeur de remplacement documentée.

---

## 22.3 État dégradé

Si un module devient indisponible, le système doit pouvoir :

- suspendre le cycle ;
- signaler le module concerné ;
- éviter de produire une décision trompeuse ;
- enregistrer l’incident ;
- reprendre seulement si la cohérence est garantie.

---

# 23. Horloge et temps

## 23.1 Horloge abstraite

Le noyau ne doit pas dépendre directement de l’heure système.

Une interface d’horloge permettra :

- les tests temporels ;
- la simulation d’interruptions ;
- la reproduction d’épisodes ;
- les expériences accélérées.

---

## 23.2 Temps réel et temps expérimental

Le système devra distinguer :

- temps réel ;
- temps de simulation ;
- durée d’un cycle ;
- période d’inactivité ;
- date connue avec certitude ;
- date estimée.

---

# 24. Identifiants

Tous les objets importants devront posséder des identifiants uniques.

Cela concerne notamment :

- agent ;
- instance ;
- cycle ;
- souvenir ;
- croyance ;
- objectif ;
- événement ;
- expérience ;
- exécution ;
- sauvegarde ;
- action ;
- observation.

Les identifiants ne devront pas dépendre du contenu textuel.

---

# 25. Périmètre de SoiNesis Core — Phase 1

## 25.1 Inclus

La phase 1 comprend :

1. un agent unique ;
2. une identité technique persistante ;
3. une mémoire autobiographique structurée ;
4. la séparation des sources ;
5. des croyances avec niveau de confiance ;
6. un modèle de soi minimal ;
7. des objectifs persistants ;
8. une métacognition minimale ;
9. un cycle cognitif explicite ;
10. un journal d’évolution ;
11. un système expérimental ;
12. des ablations ;
13. SQLite ;
14. une interface en ligne de commande ;
15. un adaptateur de modèle simulé.

---

## 25.2 Exclus

La phase 1 n’inclut pas :

- interface web ;
- plusieurs agents actifs ;
- corps virtuel ;
- capteurs physiques ;
- interactions sociales ;
- culture artificielle ;
- évolution ;
- reproduction ;
- apprentissage neuronal ;
- états émotionnels complexes ;
- autonomie externe ;
- modification autonome du code.

---

# 26. Extensions futures prévues

## 26.1 Incarnation virtuelle

Ajout futur de :

- corps virtuel ;
- capteurs ;
- effecteurs ;
- énergie ;
- intégrité ;
- intéroception ;
- environnement persistant.

---

## 26.2 Développement individuel

Ajout futur de :

- stades de développement ;
- capacités initiales limitées ;
- acquisition progressive ;
- histoire développementale.

---

## 26.3 Système social

Ajout futur de :

- plusieurs agents ;
- communication ;
- apprentissage social ;
- coopération ;
- conventions ;
- mémoire collective.

---

## 26.4 Évolution artificielle

Ajout futur de :

- populations ;
- générations ;
- hérédité ;
- mutation ;
- recombinaison ;
- sélection ;
- lignées.

Ces extensions devront respecter les interfaces du noyau sans forcer une refonte complète.

---

# 27. Organisation cible du dépôt

```text
SoiNesis/
│
├── docs/
│   ├── decisions/
│   │   └── ADR-001-choix-langage-et-socle-technique.md
│   ├── 01-definitions.md
│   ├── 02-hypotheses.md
│   └── 03-architecture-generale.md
│
├── src/
│   └── soinesis/
│       ├── domain/
│       │   ├── agents.py
│       │   ├── memories.py
│       │   ├── beliefs.py
│       │   ├── goals.py
│       │   ├── self_model.py
│       │   ├── events.py
│       │   └── experiments.py
│       │
│       ├── cognition/
│       │   ├── attention.py
│       │   ├── metacognition.py
│       │   ├── integration.py
│       │   ├── decision.py
│       │   └── cognitive_cycle.py
│       │
│       ├── application/
│       │   ├── commands.py
│       │   ├── services.py
│       │   └── orchestrator.py
│       │
│       ├── experiments/
│       │   ├── protocols.py
│       │   ├── ablations.py
│       │   ├── measures.py
│       │   └── runner.py
│       │
│       ├── ports/
│       │   ├── repositories.py
│       │   ├── language_model.py
│       │   ├── clock.py
│       │   └── identifiers.py
│       │
│       └── infrastructure/
│           ├── sqlite/
│           ├── language_models/
│           ├── logging/
│           └── system/
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

Cette structure reste une cible initiale.

Elle pourra être ajustée si le modèle de données ou les premiers prototypes révèlent une meilleure séparation.

---

# 28. Règles de dépendance entre modules

Les dépendances autorisées sont :

```text
Présentation
    ↓
Application
    ↓
Cognition
    ↓
Domaine
```

L’infrastructure implémente des interfaces définies vers le noyau :

```text
Infrastructure
    ───────► Ports du noyau
```

Interdictions :

- le domaine ne dépend pas de l’infrastructure ;
- la cognition ne dépend pas de SQLite ;
- les expériences ne modifient pas directement la base ;
- l’interface ne modifie pas directement le domaine ;
- un adaptateur de modèle ne décide pas de la politique de mémoire ;
- le journal ne remplace pas les règles métier.

---

# 29. Première tranche verticale recommandée

La première implémentation ne devra pas créer tous les modules vides.

Elle devra construire une tranche minimale complète :

```text
Entrée simulée
    ↓
Observation structurée
    ↓
Mémoire autobiographique
    ↓
Récupération d’un souvenir
    ↓
Décision simple
    ↓
Journalisation
    ↓
Persistance SQLite
    ↓
Test d’ablation
```

Cette tranche devra démontrer :

- qu’un souvenir est correctement créé ;
- que sa source est conservée ;
- qu’il peut être récupéré ;
- qu’il influence une décision ;
- que l’ablation empêche son utilisation ;
- que le changement est journalisé ;
- que le test est reproductible.

---

# 30. Critères d’acceptation de l’architecture

L’architecture sera considérée comme suffisamment définie pour commencer le modèle de données si :

- chaque module possède une responsabilité claire ;
- les dépendances interdites sont identifiées ;
- le cycle cognitif initial est décrit ;
- les états persistants sont séparés des états temporaires ;
- les points d’ablation sont prévus ;
- la journalisation est distincte de la mémoire ;
- la sécurité ne dépend pas de la bonne volonté de l’agent ;
- le modèle de langage est interchangeable ;
- les expériences sont des composants de premier rang ;
- la phase 1 possède un périmètre limité.

---

# 31. Risques architecturaux principaux

## 31.1 Noyau trop dépendant du modèle de langage

Risque :

Le modèle externe pourrait devenir le véritable système, tandis que les autres modules ne seraient que décoratifs.

Réponse :

- requêtes structurées ;
- sorties validées ;
- adaptateur simulé ;
- décisions et données conservées hors du modèle ;
- tests sans modèle externe.

---

## 31.2 Mémoire transformée en simple historique de conversation

Risque :

La mémoire ne distinguerait pas vécu, information reçue, déduction et imagination.

Réponse :

- modèles structurés ;
- sources obligatoires ;
- consolidation explicite ;
- tests de confusion de source.

---

## 31.3 Orchestrateur central trop complexe

Risque :

Toute la logique serait concentrée dans un seul fichier.

Réponse :

- orchestrateur limité à la coordination ;
- règles dans les modules ;
- interfaces explicites ;
- tests unitaires séparés.

---

## 31.4 Ablations superficielles

Risque :

Un module serait déclaré désactivé tout en continuant à influencer le système.

Réponse :

- chemins d’exécution contrôlés ;
- traces d’utilisation ;
- tests confirmant l’absence réelle d’accès ;
- comparaison avec condition témoin.

---

## 31.5 Journal incomplet

Risque :

Les changements importants ne seraient pas auditables.

Réponse :

- événements du domaine ;
- transactions ;
- tests de journalisation ;
- journal de sécurité non désactivable.

---

## 31.6 Complexité prématurée

Risque :

Le projet introduirait trop tôt plusieurs agents, une interface complexe ou l’évolution artificielle.

Réponse :

- phase 1 limitée ;
- critères de progression ;
- ADR obligatoire pour les ajouts structurels majeurs.

---

# 32. Statut épistémique

**Certain :**

- cette architecture permet d’organiser des fonctions observables ;
- elle facilite les tests, les ablations et la traçabilité ;
- elle ne prouve pas une conscience phénoménale.

**Probable :**

- une architecture modulaire et intégrée permettra de mieux mesurer le rôle causal des mécanismes ;
- la séparation entre mémoire, journal, croyances et modèle de soi réduira certaines confusions.

**Possible :**

- l’intégration progressive de ces mécanismes pourrait produire des propriétés nouvelles associées à une conscience fonctionnelle.

**Inconnu :**

- ces propriétés seraient-elles accompagnées d’une expérience subjective réelle ?

---

# 33. Décision finale

SoiNesis Core sera construit comme un monolithe modulaire en Python.

Le système sera organisé autour :

- d’un domaine indépendant ;
- de mécanismes cognitifs isolables ;
- d’un orchestrateur explicite ;
- d’interfaces vers les technologies externes ;
- d’une persistance structurée ;
- d’un journal d’évolution ;
- d’un système expérimental ;
- de points d’ablation ;
- de permissions et d’un arrêt contrôlé.

La prochaine étape est la rédaction de :

```text
docs/04-modele-de-donnees.md
```

Ce document devra définir précisément les structures minimales suivantes :

- Agent ;
- Instance ;
- Observation ;
- Souvenir autobiographique ;
- Croyance ;
- Objectif ;
- Modèle de soi ;
- Événement du journal ;
- Cycle cognitif ;
- Configuration d’ablation ;
- Expérience ;
- Résultat expérimental.
