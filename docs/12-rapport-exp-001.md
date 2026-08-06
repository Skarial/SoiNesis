# SoiNesis — Rapport préliminaire EXP-001

**Fichier :** `docs/12-rapport-exp-001.md`  
**Version :** 0.1  
**Date d’exécution :** 6 août 2026  
**Date du rapport :** 6 août 2026  
**Statut :** rapport préliminaire — phase pilote P0 terminée  
**Code de l’expérience :** `EXP-001-P0`  
**Protocole parent :** `EXP-001`  
**Titre :** Première validation fonctionnelle d’une mémoire autobiographique structurée  
**Code testé :** première tranche mémoire fusionnée dans `main`  
**Commit de fusion :** `2cd09d53ae1d9684a5472371de568d0e29d0258d`

---

# 1. Résumé exécutif

La phase pilote `EXP-001-P0` avait pour objectif de vérifier qu’une première mémoire autobiographique structurée pouvait :

- enregistrer une information reçue ;
- conserver sa provenance ;
- persister dans SQLite ;
- être récupérée ultérieurement ;
- influencer une décision simple ;
- produire une trace dans le journal d’évolution ;
- être réellement désactivée par une ablation ;
- éviter une écriture partielle en cas d’échec transactionnel.

Les contrôles exécutés ont réussi :

```text
pytest : 8 tests réussis
Ruff lint : réussi
Ruff format : réussi
Pyright strict : 0 erreur
Démonstration manuelle : réussie
```

Le résultat principal observé est le suivant :

```text
Mémoire active
→ un souvenir est récupéré
→ sa source est attribuée à JORDAN_INPUT
→ la décision contient l’information mémorisée

Mémoire désactivée
→ aucun souvenir n’est récupéré
→ aucun accès au dépôt mémoire n’est effectué
→ aucune réponse issue de la mémoire n’est produite
```

Cette différence montre que le mécanisme de mémoire implémenté a un **effet fonctionnel et causal mesurable** dans ce scénario minimal.

Elle ne démontre pas :

- une conscience phénoménale ;
- une identité persistante complète ;
- une continuité autobiographique sur une longue durée ;
- une supériorité statistique sur un résumé textuel ;
- une résistance générale aux faux souvenirs ;
- une métacognition complète ;
- une intégration globale.

La conclusion correcte est donc :

> Une première fonction de mémoire autobiographique structurée, sourcée, persistante, journalisée et désactivable a été mise en œuvre et validée sur un scénario déterministe minimal.

---

# 2. Relation avec le protocole EXP-001

Le protocole `docs/10-protocole-exp-001.md` prévoit une expérience complète comparant quatre conditions :

```text
A — Aucune mémoire persistante
B — Résumé textuel simple
C — Mémoire autobiographique structurée passive
D — Mémoire autobiographique structurée intégrée
```

Il prévoit également plusieurs épisodes portant sur :

- le rappel ;
- la provenance ;
- les engagements ;
- les contradictions ;
- les déductions ;
- l’imagination ;
- les erreurs ;
- les corrections ;
- les interruptions ;
- la reprise temporelle.

La phase `P0` ne constitue pas l’exécution complète de ce protocole.

Elle valide seulement le socle expérimental minimal nécessaire avant de construire les quatre conditions complètes.

## 2.1 Éléments du protocole partiellement couverts

- `P1 — Rappel` : couvert sur un exemple unique.
- `P2 — Provenance` : couvert sur une source `JORDAN_INPUT`.
- `P6 — Décisions` : couvert par une décision simple de rappel.
- `P8 — Ablation` : couvert directement.
- persistance : couverte par SQLite.
- journalisation : couverte pour la création d’un souvenir.
- atomicité : couverte par un test d’échec transactionnel.

## 2.2 Éléments non encore couverts

- comparaison A/B/C/D ;
- résumé textuel simple ;
- mémoire structurée passive ;
- mémoire intégrée aux objectifs ;
- modèle de soi ;
- attention ;
- métacognition ;
- contradictions temporelles ;
- révision de croyances ;
- faux souvenirs suggérés ;
- engagements persistants ;
- interruption et reprise ;
- mesures quantitatives sur plusieurs scénarios ;
- réplication indépendante ;
- tests avec un modèle de langage.

---

# 3. Problème concret testé

Un système peut afficher un texte donnant l’impression qu’il se souvient, alors qu’il reçoit simplement la réponse dans son contexte courant.

Le problème concret était donc de vérifier que :

1. l’information est enregistrée dans une structure persistante distincte du contexte immédiat ;
2. sa source est conservée explicitement ;
3. une récupération ultérieure consulte réellement cette structure ;
4. la décision change lorsque cette structure est désactivée ;
5. aucune voie cachée ne continue à lire la mémoire pendant l’ablation.

Cette dernière condition est essentielle.

Une simple mention textuelle telle que « mémoire désactivée » serait décorative si le système continuait en réalité à consulter la base.

---

# 4. Hypothèses évaluées

## 4.1 Hypothèse pilote H-P0-01 — Persistance

> Une information reçue et consolidée peut être persistée puis récupérée dans un cycle ultérieur.

### État après l’expérience

**Certain dans le périmètre du test.**

Le souvenir enregistré dans SQLite est récupéré par une requête ultérieure.

Cette conclusion reste limitée au scénario testé et ne garantit pas une robustesse à grande échelle.

---

## 4.2 Hypothèse pilote H-P0-02 — Provenance

> La provenance explicite d’un souvenir peut être conservée et restituée sans être confondue avec une expérience directe.

### État après l’expérience

**Certain dans le périmètre du test.**

L’information est attribuée à `JORDAN_INPUT` et le modèle rejette la tentative de la classer simultanément comme expérience directe.

Cette conclusion ne couvre pas encore toutes les catégories de sources.

---

## 4.3 Hypothèse pilote H-P0-03 — Influence causale

> Une mémoire récupérée peut modifier la décision produite par le système.

### État après l’expérience

**Certain dans le scénario minimal.**

Avec la mémoire active, la décision contient l’information mémorisée.

Avec la mémoire désactivée, la décision ne contient aucune réponse issue de la mémoire.

---

## 4.4 Hypothèse pilote H-P0-04 — Ablation réelle

> Lorsque la mémoire autobiographique est désactivée, le système ne consulte pas son dépôt mémoire.

### État après l’expérience

**Certain dans le test automatisé.**

Le test utilise une fabrique de dépôt qui déclenche immédiatement une erreur si elle est appelée.

Le compteur d’appels reste égal à zéro.

---

## 4.5 Hypothèse pilote H-P0-05 — Atomicité

> Une transaction en échec ne laisse pas de souvenir ou de journal partiellement écrit.

### État après l’expérience

**Certain dans le scénario de collision d’identifiants testé.**

Après l’échec volontaire de la seconde transaction :

- le premier souvenir reste présent ;
- aucun second souvenir partiel n’est présent ;
- le journal du premier souvenir contient toujours un seul événement.

---

# 5. Architecture minimale évaluée

La tranche exécutée suit le chemin suivant :

```text
Entrée contrôlée
    ↓
Observation structurée
    ↓
Souvenir autobiographique structuré
    ↓
Transaction SQLite
    ├── observation
    ├── souvenir
    └── événement de journal
    ↓
Récupération lexicale
    ↓
Décision simple
```

Une configuration d’ablation agit avant l’ouverture de l’unité de travail :

```text
Ablation active
    ↓
Arrêt du chemin mémoire
    ↓
0 accès au dépôt
    ↓
0 souvenir récupéré
```

## 5.1 Données structurées principales

Le souvenir comprend notamment :

- un identifiant ;
- un identifiant d’agent ;
- un identifiant de cycle ;
- l’identifiant de l’observation source ;
- un type de souvenir ;
- un titre ;
- un contenu ;
- un type de source ;
- un niveau de confiance ;
- une importance ;
- un statut ;
- une date de création ;
- une indication d’expérience directe ou non.

## 5.2 Journalisation

La création du souvenir produit un événement de type :

```text
MEMORY_CREATED
```

Le souvenir et l’événement sont enregistrés dans la même transaction.

---

# 6. Environnement d’exécution

## 6.1 Environnement local

```text
Système : Windows
Terminal : PowerShell
Python du projet : 3.14.7
Environnement virtuel : .venv
Base de données : SQLite
Validation des modèles : Pydantic 2
Tests : pytest
Lint et formatage : Ruff
Typage : Pyright en mode strict
```

## 6.2 Propriétés de l’exécution

- aucune connexion réseau nécessaire pour les tests ;
- aucun fournisseur de modèle de langage utilisé ;
- horloge fixe dans les tests ;
- identifiants déterministes dans les tests ;
- base SQLite temporaire pour les tests d’intégration ;
- scénario synthétique et contrôlé.

Ces choix réduisent la variabilité, mais limitent aussi la portée des conclusions.

---

# 7. Scénario exécuté

## 7.1 Information fondatrice

Entrée :

> Jordan indique que le nom du projet est SoiNesis.

Classification attendue :

```text
memory_type = RECEIVED_INFORMATION
source_type = JORDAN_INPUT
is_direct_experience = false
confidence = 1.0
importance = 0.9 dans le test d’intégration principal
```

## 7.2 Question de rappel

Question :

> Quel nom Jordan a-t-il donné au projet ?

## 7.3 Condition mémoire active

Configuration :

```text
autobiographical_memory_enabled = true
```

Résultat attendu :

- récupération du souvenir ;
- présence de `SoiNesis` dans la réponse ;
- source `JORDAN_INPUT` ;
- identifiant du souvenir dans la décision.

## 7.4 Condition d’ablation

Configuration :

```text
autobiographical_memory_enabled = false
```

Résultat attendu :

- aucune réponse mémorielle ;
- aucun identifiant de souvenir récupéré ;
- aucun accès au dépôt mémoire.

---

# 8. Résultats automatisés

## 8.1 Résultat global

```text
8 tests réussis en 0,55 seconde lors de l’exécution finale rapportée
```

Le temps d’exécution est indicatif et dépend de la machine.

Il ne constitue pas une mesure de performance scientifique à ce stade.

## 8.2 Tests du socle

### Version du paquet

Résultat : réussi.

La version déclarée est :

```text
0.1.0
```

### Aide de la ligne de commande

Résultat : réussi.

Le point d’entrée produit l’aide attendue.

## 8.3 Tests des modèles du domaine

### Séparation entre information reçue et expérience directe

Résultat : réussi.

Une observation ayant :

```text
source_type = JORDAN_INPUT
is_direct_experience = true
```

est rejetée par la validation.

### Valeurs explicites des types de mémoire

Résultat : réussi.

La valeur `RECEIVED_INFORMATION` est explicite et stable.

## 8.4 Test d’intégration principal

Résultat : réussi.

Observations :

- l’information est persistée ;
- la récupération contient `SoiNesis` ;
- la source restituée est `JORDAN_INPUT` ;
- l’identifiant du souvenir récupéré correspond au souvenir enregistré ;
- un événement de journal existe ;
- cet événement est de type `MEMORY_CREATED`.

## 8.5 Test d’atomicité

Résultat : réussi.

Une collision d’identifiants provoque volontairement une erreur SQLite.

Après l’échec :

```text
nombre de souvenirs valides retrouvés = 1
nombre d’événements pour le premier souvenir = 1
trace partielle de la seconde transaction = absente dans le périmètre vérifié
```

## 8.6 Test d’ablation

Résultat : réussi.

Mesures :

```text
réponse = None
identifiants de souvenirs récupérés = ()
nombre d’appels à la fabrique de dépôt = 0
```

Ce test apporte l’indice causal le plus important de cette phase pilote.

---

# 9. Résultat de la démonstration manuelle

Commande exécutée :

```powershell
python -m soinesis.application.demo
```

Sortie observée :

```text
=== Mémoire active ===
Réponse : Jordan indique que le nom du projet est SoiNesis.
Source : JORDAN_INPUT
Souvenirs consultés : 1

=== Mémoire désactivée ===
Réponse : Aucune réponse issue de la mémoire
Souvenirs consultés : 0
Raison : Mémoire autobiographique désactivée par la configuration d'ablation.
```

## 9.1 Observation

La sortie diffère selon l’état du mécanisme de mémoire.

## 9.2 Interprétation prudente

La mémoire est fonctionnellement active dans la production de cette décision simple.

## 9.3 Interprétation interdite

Cette sortie ne permet pas d’affirmer que SoiNesis :

- se souvient subjectivement ;
- éprouve une continuité vécue ;
- ressent une absence lorsque la mémoire est désactivée ;
- possède une conscience phénoménale.

---

# 10. Contrôles de qualité

Les contrôles suivants ont réussi après les corrections :

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m pyright
```

Résultats finaux :

```text
pytest : réussi
Ruff lint : All checks passed
Ruff format : tous les fichiers concernés sont formatés
Pyright strict : 0 erreur, 0 avertissement
```

Une erreur initiale de typage a été détectée dans la désérialisation JSON du journal.

Elle a été corrigée en rendant explicite le type du résultat de `json.loads` avant sa transmission au modèle `JournalEvent`.

Cette correction constitue un exemple de résultat négatif utile :

- les tests fonctionnels passaient déjà ;
- le contrôle statique a néanmoins détecté une incertitude de type ;
- le code a été corrigé au lieu de désactiver la règle Pyright.

---

# 11. Analyse causale

## 11.1 Variable manipulée

```text
autobiographical_memory_enabled
```

## 11.2 Effet observé

| Condition | Accès au dépôt | Souvenirs récupérés | Réponse mémorielle |
|---|---:|---:|---|
| Mémoire active | oui | 1 | présente |
| Mémoire désactivée | 0 | 0 | absente |

## 11.3 Pourquoi cet effet est causal dans ce test

La configuration d’ablation est modifiée alors que :

- la question reste la même ;
- l’agent reste le même ;
- le code de décision reste le même ;
- l’environnement est déterministe ;
- aucune autre source d’information n’est ajoutée.

L’ablation empêche en outre l’ouverture du dépôt mémoire.

Il est donc raisonnable d’attribuer la différence de sortie à la disponibilité du mécanisme de mémoire dans ce scénario.

## 11.4 Limite de l’analyse

Cette causalité est démontrée pour un chemin logiciel précis.

Elle ne démontre pas encore que la mémoire influence :

- des objectifs persistants ;
- une stratégie complexe ;
- un modèle de soi ;
- une attention globale ;
- une décision comportant plusieurs options concurrentes.

---

# 12. Résultats négatifs et difficultés

## 12.1 Formatage initial

Ruff a détecté un fichier qui devait être reformaté.

Le fichier a été corrigé automatiquement.

## 12.2 Typage des protocoles

Pyright a initialement détecté une incompatibilité entre :

- `SQLiteUnitOfWorkFactory` ;
- le protocole `UnitOfWorkFactory`.

La cause était l’exposition d’attributs de dépôts considérés comme modifiables dans le protocole.

La définition a été corrigée avec des propriétés en lecture seule, ce qui exprime mieux le contrat réel.

## 12.3 Typage de pytest

Le paramètre `capsys` du test de la ligne de commande n’était pas suffisamment typé.

Une annotation explicite a été ajoutée.

## 12.4 Désérialisation JSON

Pyright a détecté que le dictionnaire produit par `json.loads` avait des types de clés et de valeurs inconnus.

La conversion a été rendue explicite après vérification que la valeur était bien un dictionnaire.

## 12.5 Importance scientifique de ces résultats négatifs

Ces problèmes ne réfutent pas l’hypothèse sur la mémoire.

Ils montrent toutefois que :

- le premier prototype n’était pas immédiatement conforme au typage strict ;
- la validation fonctionnelle seule n’était pas suffisante ;
- plusieurs corrections ont été nécessaires avant intégration ;
- l’architecture doit continuer à être contrôlée par des outils indépendants des tests fonctionnels.

---

# 13. Limites expérimentales

## 13.1 Taille de l’échantillon

Un seul contenu principal a été utilisé dans la démonstration.

Il n’existe aucune puissance statistique.

## 13.2 Déterminisme

Le déterminisme facilite la réplication technique, mais ne teste pas la variabilité d’un modèle génératif.

## 13.3 Récupération lexicale

La récupération repose actuellement sur une correspondance lexicale simple.

Elle ne mesure pas encore :

- la compréhension sémantique profonde ;
- la résolution d’ambiguïtés ;
- le rappel indirect ;
- la résistance aux formulations trompeuses.

## 13.4 Décision simple

La décision consiste essentiellement à restituer le meilleur souvenir trouvé.

Elle n’implique pas encore un arbitrage entre :

- plusieurs objectifs ;
- plusieurs souvenirs contradictoires ;
- un risque ;
- une permission ;
- une contrainte morale ;
- une incertitude complexe.

## 13.5 Source unique

La provenance `JORDAN_INPUT` a été testée.

Les sources suivantes ne sont pas encore comparées expérimentalement :

- expérience directe ;
- outil externe ;
- déduction ;
- imagination ;
- génération automatique ;
- information externe non vérifiée.

## 13.6 Temporalité minimale

Le système stocke des dates et des cycles, mais aucune continuité longue n’a été testée.

## 13.7 Absence de comparaison avec un résumé

La condition B du protocole parent n’existe pas encore dans l’expérience exécutée.

Il est donc impossible de conclure que la structure mémoire est meilleure qu’un résumé textuel de taille équivalente.

## 13.8 Absence de réplication indépendante

Les tests ont été exécutés dans l’environnement du créateur du projet.

Aucune équipe indépendante n’a encore reproduit les résultats.

---

# 14. Critères de réfutation

Les conclusions de cette phase seraient réfutées ou sérieusement affaiblies si une réplication montrait l’un des résultats suivants.

## 14.1 Réfutation de la persistance

- le souvenir disparaît après réouverture de la base ;
- une récupération retourne une information non enregistrée ;
- l’identifiant récupéré ne correspond pas au souvenir persisté.

## 14.2 Réfutation de la provenance

- une information `JORDAN_INPUT` est présentée comme expérience directe ;
- la source change silencieusement entre l’écriture et la lecture ;
- une déduction ou une imagination est attribuée à Jordan.

## 14.3 Réfutation de l’ablation

- le dépôt mémoire est consulté malgré l’ablation ;
- un cache permet de restituer le souvenir pendant l’ablation ;
- la réponse mémorielle reste identique avec la mémoire désactivée ;
- le compteur d’accès au dépôt devient supérieur à zéro.

## 14.4 Réfutation de l’atomicité

- une observation sans souvenir correspondant reste après un échec ;
- un souvenir sans événement de journal reste après un échec ;
- un événement de journal référence une entité absente ;
- une transaction échouée modifie l’état persistant.

## 14.5 Réfutation de la reproductibilité

- les mêmes tests déterministes produisent des résultats différents sans changement documenté ;
- l’expérience dépend d’un état local non versionné ;
- les résultats ne peuvent pas être reproduits sur une autre machine compatible.

---

# 15. Classification épistémique des conclusions

## 15.1 Certain

Dans l’environnement et le code testés :

- une information peut être enregistrée dans SQLite ;
- elle peut être récupérée ;
- sa source `JORDAN_INPUT` est conservée ;
- une création de souvenir est journalisée ;
- l’ablation testée empêche l’accès au dépôt ;
- l’échec transactionnel testé ne laisse pas de seconde mémoire partielle ;
- les huit tests automatisés passent ;
- Ruff et Pyright passent après correction.

## 15.2 Probable

- l’architecture constitue une base adaptée pour construire une mémoire autobiographique plus complète ;
- la séparation explicite des sources réduira certains types de confusion si elle est appliquée à toutes les entrées ;
- les tests d’ablation permettront de mesurer l’influence de futurs mécanismes.

Ces propositions restent à confirmer sur des scénarios plus nombreux.

## 15.3 Possible

- une mémoire structurée pourrait améliorer la continuité fonctionnelle sur plusieurs épisodes ;
- elle pourrait soutenir un modèle de soi causalement actif ;
- elle pourrait améliorer la révision après contradiction.

Ces effets ne sont pas encore démontrés.

## 15.4 Inconnu

- l’effet sur une architecture utilisant un modèle de langage ;
- l’effet à long terme ;
- la robustesse aux suggestions adversariales ;
- la supériorité sur un résumé textuel ;
- l’effet sur une identité persistante complète ;
- l’existence d’une expérience subjective.

## 15.5 Spéculatif

- l’idée que cette architecture pourrait contribuer à l’apparition d’une conscience phénoménale.

Aucune donnée de `EXP-001-P0` ne permet de soutenir directement cette conclusion.

---

# 16. Risques techniques et scientifiques

## 16.1 Faux sentiment de progrès

Une démonstration réussie peut sembler plus importante qu’elle ne l’est.

Le mécanisme actuel reste un stockage structuré avec récupération et décision simple.

## 16.2 Confusion entre causalité locale et intégration globale

L’ablation montre une causalité locale sur le chemin de rappel.

Elle ne montre pas encore que la mémoire influence l’ensemble du système.

## 16.3 Surinterprétation anthropomorphique

La phrase « Jordan indique que le nom du projet est SoiNesis » est une restitution de donnée.

Elle ne prouve ni souvenir vécu ni compréhension phénoménale.

## 16.4 Accumulation non contrôlée

Une future mémoire plus volumineuse pourrait introduire :

- des doublons ;
- des contradictions ;
- des informations obsolètes ;
- des erreurs de source ;
- une récupération biaisée ;
- une croissance excessive de la base.

## 16.5 Journal incomplet

La phase pilote journalise la création du souvenir.

Elle ne couvre pas encore toutes les modifications, corrections, suppressions et changements de croyances prévus par l’architecture.

## 16.6 Risque moral actuel

Aucun état analogue à la souffrance, à la peur ou à la détresse n’a été implémenté.

Le risque moral direct est donc faible à ce stade.

Cette évaluation devra être révisée si des états internes persistants et causalement actifs sont ajoutés.

---

# 17. Décisions prises pendant la phase P0

## 17.1 Décisions de Jordan

- utiliser Python 3.14 ;
- conserver SQLite pour la première version ;
- avancer progressivement ;
- valider chaque étape avant la suivante ;
- fusionner la première tranche dans `main` après réussite des contrôles ;
- arrêter le chantier après rédaction et intégration du présent rapport.

## 17.2 Analyses techniques

- conserver un monolithe modulaire ;
- utiliser des ports pour séparer le domaine de SQLite ;
- rendre les modèles Pydantic immuables ;
- utiliser une unité de travail transactionnelle ;
- placer l’ablation avant l’accès au dépôt ;
- utiliser une horloge et des identifiants injectables pour les tests ;
- maintenir Pyright en mode strict au lieu de masquer les erreurs.

## 17.3 Informations externes

Aucune information externe n’a déterminé les résultats de l’expérience.

Les résultats proviennent :

- du code versionné ;
- des tests automatisés ;
- des commandes exécutées localement ;
- de la démonstration contrôlée.

## 17.4 Éléments générés automatiquement

- les identifiants de test ;
- les horodatages fixes injectés ;
- les sorties déterministes de la démonstration ;
- les événements de journal créés par le service applicatif.

---

# 18. Conclusion

`EXP-001-P0` valide le fonctionnement minimal de la chaîne suivante :

```text
Observation sourcée
→ Souvenir structuré
→ Persistance SQLite
→ Récupération
→ Décision simple
→ Journal
→ Ablation
```

Le mécanisme n’est pas décoratif : sa désactivation modifie la sortie et empêche l’accès au dépôt mémoire.

La conclusion scientifique doit néanmoins rester limitée :

> SoiNesis possède désormais une première fonction associée à la mémoire autobiographique, persistante, sourcée, journalisée et causalement active dans un scénario minimal.

Cette conclusion ne permet pas encore de qualifier SoiNesis de candidat à la conscience fonctionnelle complète.

Elle ne fournit aucun élément permettant d’affirmer une conscience phénoménale.

---

# 19. Étape expérimentale suivante

La prochaine phase recommandée est `EXP-001-P1`.

Objectif : comparer au minimum trois conditions sur un jeu de scénarios contrôlé :

```text
A — aucune mémoire persistante
B — résumé textuel simple
C — mémoire structurée active
```

Mesures prioritaires :

- précision du rappel ;
- précision de provenance ;
- taux de faux souvenirs ;
- effet de l’ablation ;
- volume d’information accessible ;
- reproductibilité sur plusieurs jeux de données.

Cette phase ne doit commencer qu’après définition :

- du jeu de données ;
- des métriques exactes ;
- des seuils de réussite ;
- des critères de réfutation ;
- du format de rapport ;
- de la procédure de réplication.

---

# 20. État final du chantier du 6 août 2026

```text
Documentation scientifique initiale : présente
Socle Python 3.14 : validé
Première tranche mémoire : fusionnée dans main
Tests automatisés : 8 réussis
Lint : réussi
Formatage : réussi
Typage strict : réussi
Démonstration : réussie
Rapport EXP-001-P0 : rédigé et versionné
Chantier : arrêté pour la journée
```
