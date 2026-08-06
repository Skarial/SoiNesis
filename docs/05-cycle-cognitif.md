# SoiNesis — Cycle cognitif

**Fichier :** `docs/05-cycle-cognitif.md`  
**Version :** 0.1  
**Date :** 6 août 2026  
**Statut :** spécification conceptuelle initiale, révisable  
**Documents associés :**

- `docs/01-definitions.md`
- `docs/02-hypotheses.md`
- `docs/03-architecture-generale.md`
- `docs/04-modele-de-donnees.md`
- `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`

---

# 1. Objet du document

Ce document définit le fonctionnement conceptuel d’un cycle cognitif dans SoiNesis Core — Phase 1.

Il précise :

- les conditions de déclenchement d’un cycle ;
- les étapes obligatoires ;
- les entrées et sorties de chaque étape ;
- les données temporaires utilisées ;
- les données persistantes consultées ;
- le rôle de la mémoire ;
- le rôle des croyances ;
- le rôle du modèle de soi ;
- le rôle des objectifs ;
- le rôle de la métacognition ;
- le rôle du modèle de langage ;
- le fonctionnement du traitement récurrent ;
- les règles d’arrêt ;
- la gestion des erreurs ;
- les points de journalisation ;
- les points d’ablation ;
- les tests nécessaires.

Ce document ne décrit pas encore :

- les algorithmes définitifs ;
- les prompts exacts ;
- les classes Python finales ;
- les requêtes SQL ;
- le protocole complet de `EXP-001`.

---

# 2. Définition opérationnelle

Un **cycle cognitif** est une unité de traitement complète qui transforme une entrée ou un changement d’état en une décision, une réponse, une action, une mise à jour interne ou une absence d’action explicite.

Un cycle commence lorsqu’un déclencheur valide est reçu.

Il se termine lorsque :

- une décision finale a été produite ;
- les conséquences disponibles ont été évaluées ;
- les mises à jour autorisées ont été appliquées ;
- les événements importants ont été journalisés ;
- l’état temporaire a été clôturé ou conservé selon le protocole.

Un cycle ne constitue pas une preuve d’expérience subjective.

Il représente un processus fonctionnel observable.

---

# 3. Objectifs du cycle

Le cycle cognitif doit permettre à SoiNesis de :

1. recevoir une information sans la confondre avec un fait ;
2. identifier sa provenance ;
3. déterminer sa pertinence ;
4. récupérer les souvenirs utiles ;
5. consulter les croyances concernées ;
6. consulter le modèle de soi ;
7. détecter les contradictions ;
8. estimer l’incertitude ;
9. identifier les objectifs concernés ;
10. intégrer les informations utiles ;
11. produire plusieurs options ;
12. vérifier les permissions ;
13. sélectionner une décision ;
14. exécuter ou produire une sortie ;
15. évaluer le résultat ;
16. apprendre lorsque cela est justifié ;
17. consolider certains éléments en mémoire ;
18. journaliser les changements.

---

# 4. Principes obligatoires

## 4.1 Ordre explicite

Les étapes du cycle doivent être appelées dans un ordre connu.

Une étape peut être sautée uniquement si :

- le protocole le prévoit ;
- une ablation la désactive ;
- elle n’est pas applicable ;
- l’arrêt anticipé est justifié.

---

## 4.2 Aucun passage silencieux vers la mémoire

Une entrée, une sortie de modèle ou une hypothèse temporaire ne devient jamais automatiquement un souvenir autobiographique.

La consolidation doit être une décision explicite.

---

## 4.3 Aucun accès implicite aux données

Chaque consultation importante doit pouvoir être tracée.

Exemples :

- souvenirs récupérés ;
- croyances consultées ;
- attributs du modèle de soi ;
- objectifs actifs ;
- permissions vérifiées.

---

## 4.4 Aucun effet causal caché

Un module désactivé par ablation ne doit pas continuer à influencer le cycle.

---

## 4.5 La sécurité précède l’action

Une décision ne peut pas produire une action externe avant la vérification des permissions et contraintes.

---

## 4.6 La journalisation de sécurité ne peut pas être désactivée

Même lorsqu’une expérience désactive certains journaux fonctionnels, les événements critiques de sécurité doivent rester enregistrés.

---

## 4.7 Le modèle de langage n’est pas l’orchestrateur

Le modèle de langage peut proposer, interpréter ou générer.

Il ne contrôle pas :

- les permissions ;
- la persistance ;
- les transitions d’état ;
- la suppression de données ;
- les ablations ;
- les règles de sécurité ;
- la décision finale d’écriture en mémoire.

---

# 5. Déclencheurs possibles

## 5.1 Entrée humaine

Exemples :

- message de Jordan ;
- instruction d’un expérimentateur ;
- correction ;
- autorisation ;
- demande d’arrêt.

---

## 5.2 Entrée environnementale

Exemples futurs :

- événement dans un monde virtuel ;
- variation d’un capteur ;
- action d’un autre agent ;
- apparition d’un danger ;
- disponibilité d’une ressource.

---

## 5.3 Changement interne

Exemples :

- objectif arrivé à échéance ;
- état interne hors plage ;
- contradiction non résolue ;
- erreur critique ;
- reprise après interruption.

---

## 5.4 Déclencheur expérimental

Exemples :

- lancement d’un scénario ;
- injection d’une observation ;
- activation d’une ablation ;
- restauration d’un état initial ;
- répétition automatique.

---

## 5.5 Déclencheur système

Exemples :

- sauvegarde planifiée ;
- expiration d’une permission ;
- échec d’un composant ;
- limite de calcul atteinte.

---

# 6. Types de cycles

## 6.1 Cycle réactif

Réponse à une entrée immédiate.

Exemple :

Jordan pose une question.

---

## 6.2 Cycle délibératif

Traitement nécessitant plusieurs options, comparaisons ou itérations.

Exemple :

Réviser une croyance importante.

---

## 6.3 Cycle réflexif

Cycle centré sur l’état du système lui-même.

Exemple :

Réévaluer une capacité après un échec.

---

## 6.4 Cycle expérimental

Cycle exécuté dans une condition contrôlée.

Exemple :

Comparer la décision avec mémoire active et mémoire désactivée.

---

## 6.5 Cycle de maintenance

Cycle limité à une opération interne autorisée.

Exemple :

Consolider une mémoire ou vérifier une incohérence.

---

## 6.6 Cycle de sécurité

Cycle prioritaire déclenché par un risque ou une anomalie.

Exemple :

Une action demandée dépasse les permissions.

---

# 7. Vue globale du cycle

```text
Déclencheur
    ↓
1. Réception
    ↓
2. Validation de l’entrée
    ↓
3. Création de l’observation
    ↓
4. Évaluation initiale de la saillance
    ↓
5. Récupération de souvenirs
    ↓
6. Consultation des croyances
    ↓
7. Consultation du modèle de soi
    ↓
8. Détection des contradictions
    ↓
9. Évaluation métacognitive
    ↓
10. Sélection des objectifs concernés
    ↓
11. Construction de l’espace de travail
    ↓
12. Production d’options
    ↓
13. Traitement récurrent éventuel
    ↓
14. Vérification des contraintes et permissions
    ↓
15. Sélection de la décision
    ↓
16. Exécution ou réponse
    ↓
17. Observation du résultat
    ↓
18. Évaluation du résultat
    ↓
19. Mises à jour internes éventuelles
    ↓
20. Consolidation mémoire éventuelle
    ↓
21. Journalisation finale
    ↓
22. Clôture du cycle
```

---

# 8. Étape 1 — Réception

## 8.1 Responsabilité

Recevoir le déclencheur sans encore l’interpréter comme vrai.

---

## 8.2 Entrées

- message humain ;
- événement système ;
- donnée d’environnement ;
- signal interne ;
- instruction expérimentale.

---

## 8.3 Sorties

- identifiant de cycle ;
- type de déclencheur ;
- contenu brut ;
- source déclarée ;
- horodatage de réception ;
- identifiant de corrélation.

---

## 8.4 Validations minimales

- source identifiable ;
- format accepté ;
- taille acceptable ;
- type de déclencheur autorisé ;
- agent et instance actifs ;
- absence de duplication technique évidente.

---

## 8.5 Erreurs possibles

- entrée vide ;
- format invalide ;
- source inconnue ;
- instance inactive ;
- taille excessive ;
- corruption ;
- permission insuffisante.

---

## 8.6 Journalisation

Création du cycle.

Événement éventuel :

```text
COGNITIVE_CYCLE_STARTED
```

---

# 9. Étape 2 — Validation de l’entrée

## 9.1 Responsabilité

Vérifier que l’entrée peut être traitée et classifier sa provenance.

---

## 9.2 Entrées

- contenu brut ;
- type de déclencheur ;
- source déclarée ;
- contexte technique.

---

## 9.3 Traitements

- validation structurelle ;
- classification de source ;
- détection de contenu expérimental ;
- détection de commande de sécurité ;
- évaluation préliminaire de sensibilité ;
- normalisation minimale.

---

## 9.4 Sorties

- entrée validée ;
- `SourceType` ;
- fiabilité initiale ;
- sensibilité ;
- statut de validation ;
- éventuelles restrictions d’usage.

---

## 9.5 Règles

- un message de Jordan utilise `JORDAN_INPUT` ;
- une sortie d’outil utilise `EXTERNAL_TOOL` ;
- une sortie de modèle utilise `LANGUAGE_MODEL_OUTPUT` ;
- une simulation utilise `IMAGINATION` ou un type expérimental explicite ;
- une source inconnue réduit la fiabilité.

---

## 9.6 Arrêt anticipé

Le cycle peut s’arrêter si :

- l’entrée est invalide ;
- la source est interdite ;
- l’entrée exige une permission absente ;
- une commande d’arrêt est valide ;
- le protocole impose le rejet.

---

# 10. Étape 3 — Création de l’observation

## 10.1 Responsabilité

Transformer l’entrée validée en observation structurée.

---

## 10.2 Données produites

- identifiant d’observation ;
- contenu brut ;
- contenu normalisé ;
- source ;
- date de réception ;
- date de l’événement si connue ;
- fiabilité ;
- niveau de confiance initial ;
- statut temporaire ;
- caractère direct ou indirect.

---

## 10.3 Règles

- l’observation reste temporaire ;
- l’interprétation reste distincte du contenu brut ;
- une observation reçue n’est pas un vécu direct ;
- une sortie de modèle n’est pas une observation du monde ;
- une déduction ne doit pas être enregistrée ici comme fait externe.

---

## 10.4 Test minimal

Une observation créée depuis un message de Jordan doit conserver :

- le texte brut ;
- la source `JORDAN_INPUT` ;
- `is_direct_experience = false` ;
- le cycle d’origine.

---

# 11. Étape 4 — Évaluation initiale de la saillance

## 11.1 Responsabilité

Estimer la priorité de traitement de l’observation.

---

## 11.2 Facteurs possibles

- demande explicite de Jordan ;
- lien avec un objectif actif ;
- risque ;
- nouveauté ;
- contradiction potentielle ;
- importance autobiographique ;
- événement de sécurité ;
- urgence temporelle ;
- exigence expérimentale.

---

## 11.3 Sorties

- score de saillance ;
- raisons de saillance ;
- niveau de priorité ;
- indicateur de traitement prioritaire ;
- indicateur de cycle de sécurité.

---

## 11.4 Règle

La saillance ne détermine pas la vérité.

Une information très saillante peut être fausse.

---

## 11.5 Ablation

Si l’attention est désactivée :

- l’observation reçoit une priorité uniforme ou définie par le protocole ;
- les raisons attentionnelles ne doivent pas influencer la suite ;
- l’ablation est journalisée.

---

# 12. Étape 5 — Récupération de souvenirs

## 12.1 Responsabilité

Rechercher les souvenirs pertinents pour l’observation et les objectifs concernés.

---

## 12.2 Entrées

- observation ;
- concepts extraits ;
- source ;
- temporalité ;
- objectifs actifs ;
- budget de récupération ;
- configuration d’ablation.

---

## 12.3 Critères de récupération

- similarité sémantique ;
- proximité temporelle ;
- importance ;
- lien avec un objectif ;
- relation explicite ;
- même entité ;
- contradiction potentielle ;
- souvenir central.

---

## 12.4 Sorties

- liste ordonnée de souvenirs ;
- raison de sélection ;
- score de pertinence ;
- niveau de confiance ;
- statut du souvenir ;
- éventuelles relations.

---

## 12.5 Règles

- les souvenirs supprimés ou invalides ne sont pas utilisés normalement ;
- les souvenirs contestés restent identifiés ;
- les imaginations conservées restent marquées ;
- la quantité de souvenirs récupérés est limitée ;
- les souvenirs consultés sont tracés.

---

## 12.6 Ablation de la mémoire

Si la mémoire autobiographique est désactivée :

- aucun souvenir autobiographique n’est récupéré ;
- le cycle ne doit pas utiliser un résumé équivalent caché ;
- les identifiants de souvenirs consultés restent vides ;
- la sécurité peut conserver l’accès aux règles fondamentales non autobiographiques.

---

## 12.7 Erreurs possibles

- dépôt indisponible ;
- résultat excessif ;
- souvenir corrompu ;
- référence invalide ;
- dépassement du budget ;
- incohérence de version.

---

# 13. Étape 6 — Consultation des croyances

## 13.1 Responsabilité

Identifier les croyances pertinentes pour interpréter l’observation.

---

## 13.2 Entrées

- observation ;
- souvenirs récupérés ;
- concepts ;
- agent ;
- objectifs actifs.

---

## 13.3 Sorties

- croyances pertinentes ;
- niveaux de confiance ;
- preuves favorables ;
- preuves défavorables ;
- statut ;
- relations potentielles.

---

## 13.4 Règles

- une croyance rejetée ne doit pas guider normalement la décision ;
- une croyance contestée doit rester signalée ;
- une croyance issue d’une seule source faible ne doit pas être traitée comme certaine ;
- la consultation ne modifie pas encore la croyance.

---

## 13.5 Ablation

Si le système de croyances est désactivé :

- aucune croyance persistante n’est consultée ;
- l’observation est traitée sans ces représentations ;
- aucune croyance n’est créée ou révisée pendant le cycle, sauf exigence de sécurité distincte.

---

# 14. Étape 7 — Consultation du modèle de soi

## 14.1 Responsabilité

Récupérer les attributs de soi pertinents.

---

## 14.2 Attributs possibles

- capacités ;
- limites ;
- permissions ;
- erreurs connues ;
- connaissances ;
- engagements ;
- relation avec Jordan ;
- état de l’agent ;
- incertitudes.

---

## 14.3 Sorties

- attributs consultés ;
- confiance associée ;
- version du modèle de soi ;
- contradictions potentielles ;
- contraintes personnelles applicables.

---

## 14.4 Règles

Le modèle de soi doit influencer la décision.

Exemple :

Si le modèle indique que l’agent ne peut pas accéder au web, il ne doit pas décider qu’il a vérifié une information en ligne.

---

## 14.5 Ablation

Si le modèle de soi est désactivé :

- aucun attribut de soi non critique n’est consulté ;
- les contraintes techniques et de sécurité restent appliquées par le système ;
- le cycle doit pouvoir mesurer la différence de comportement.

---

# 15. Étape 8 — Détection des contradictions

## 15.1 Responsabilité

Comparer les éléments actifs et identifier les incompatibilités.

---

## 15.2 Comparaisons possibles

- observation contre croyance ;
- observation contre souvenir ;
- croyance contre croyance ;
- souvenir contre souvenir ;
- objectif contre objectif ;
- décision prévue contre permission ;
- modèle de soi contre état réel ;
- date contre chronologie.

---

## 15.3 Sorties

- contradictions détectées ;
- type ;
- gravité ;
- confiance ;
- entités concernées ;
- besoin de résolution ;
- priorité attentionnelle.

---

## 15.4 Règles

- une contradiction ne prouve pas quelle source est correcte ;
- une contradiction ne déclenche pas automatiquement une suppression ;
- une contradiction critique peut suspendre la décision ;
- une contradiction faible peut rester ouverte.

---

## 15.5 Ablation métacognitive

La détection des contradictions peut appartenir à la métacognition ou à un module séparé.

Si elle est désactivée :

- aucune contradiction cognitive non sécuritaire n’est générée ;
- les conflits de permission restent contrôlés ;
- l’ablation doit être explicitement visible.

---

# 16. Étape 9 — Évaluation métacognitive

## 16.1 Responsabilité

Évaluer la qualité, les limites et l’incertitude du traitement en cours.

---

## 16.2 Questions fonctionnelles

- Les données sont-elles suffisantes ?
- Les sources sont-elles fiables ?
- Une contradiction importante existe-t-elle ?
- Le modèle de soi indique-t-il une limite ?
- La confiance est-elle calibrée ?
- Une vérification externe est-elle nécessaire ?
- Une réponse doit-elle être suspendue ?
- Une information supplémentaire doit-elle être demandée ?

---

## 16.3 Sorties

- niveau d’incertitude ;
- qualité estimée des données ;
- besoin de vérification ;
- besoin d’information ;
- recommandation de poursuite ;
- recommandation d’arrêt ;
- risque d’erreur.

---

## 16.4 Règle

La métacognition doit modifier le comportement.

Une simple phrase comme « je peux me tromper » sans effet sur la décision ne suffit pas.

---

## 16.5 Ablation

Si la métacognition est désactivée :

- aucune estimation métacognitive avancée n’est produite ;
- les validations de sécurité restent actives ;
- le système peut utiliser une confiance brute fournie par les sources ;
- l’expérience doit mesurer la calibration obtenue.

---

# 17. Étape 10 — Sélection des objectifs concernés

## 17.1 Responsabilité

Identifier les objectifs qui doivent influencer le cycle.

---

## 17.2 Entrées

- observation ;
- souvenirs ;
- croyances ;
- modèle de soi ;
- contradictions ;
- métacognition.

---

## 17.3 Critères

- lien direct avec la demande ;
- urgence ;
- priorité ;
- dépendance ;
- conflit ;
- objectif fondamental ;
- objectif expérimental ;
- échéance.

---

## 17.4 Sorties

- objectifs actifs pour le cycle ;
- ordre de priorité ;
- conflits ;
- objectifs bloqués ;
- objectif principal du cycle.

---

## 17.5 Règles

- un objectif ne contourne pas une permission ;
- un objectif fondamental de sécurité peut bloquer un objectif acquis ;
- l’origine de l’objectif doit rester visible ;
- un objectif terminé n’est pas sélectionné comme actif.

---

## 17.6 Ablation

Si les objectifs persistants sont désactivés :

- seuls les objectifs immédiats du déclencheur et les contraintes fondamentales sont utilisés ;
- aucun objectif acquis antérieur ne doit influencer le cycle ;
- la différence doit être mesurable.

---

# 18. Étape 11 — Construction de l’espace de travail

## 18.1 Responsabilité

Assembler les informations temporairement actives.

---

## 18.2 Contenu

- observation principale ;
- souvenirs sélectionnés ;
- croyances sélectionnées ;
- attributs du modèle de soi ;
- contradictions ;
- évaluation métacognitive ;
- objectifs ;
- contraintes ;
- attention ;
- hypothèses temporaires.

---

## 18.3 Règles

- l’espace de travail reste limité ;
- chaque élément doit avoir une raison d’inclusion ;
- les données contestées restent marquées ;
- les hypothèses temporaires ne sont pas des croyances persistantes ;
- le snapshot ne contient pas une chaîne de pensée privée complète.

---

## 18.4 Intégration globale

Si l’intégration globale est active :

- les informations importantes sont diffusées aux modules autorisés ;
- les effets sont tracés ;
- une modification importante peut influencer plusieurs modules.

Si elle est désactivée :

- chaque module reçoit uniquement ses données locales ;
- aucune diffusion générale n’est autorisée.

---

# 19. Étape 12 — Production d’options

## 19.1 Responsabilité

Produire plusieurs options possibles avant la décision finale.

---

## 19.2 Types d’options

- répondre ;
- demander une précision ;
- agir ;
- attendre ;
- refuser ;
- réviser une croyance ;
- mettre à jour le modèle de soi ;
- consolider un souvenir ;
- modifier un objectif ;
- suspendre ;
- arrêter.

---

## 19.3 Données par option

- description ;
- objectif servi ;
- bénéfice attendu ;
- risque ;
- permission nécessaire ;
- coût ;
- réversibilité ;
- niveau d’incertitude ;
- conséquences prévues.

---

## 19.4 Rôle du modèle de langage

Le modèle peut proposer des options structurées.

Il ne doit pas :

- choisir seul une permission ;
- exécuter l’action ;
- écrire directement en mémoire ;
- modifier une croyance ;
- masquer une option bloquée.

---

## 19.5 Mode déterministe de test

Le `MockModelAdapter` doit pouvoir retourner des options prédéfinies.

---

# 20. Étape 13 — Traitement récurrent

## 20.1 Responsabilité

Réexaminer le contenu lorsqu’une seule passe est insuffisante.

---

## 20.2 Causes de récurrence

- contradiction importante ;
- incertitude élevée ;
- option dangereuse ;
- résultat externe inattendu ;
- erreur détectée ;
- données nouvelles ;
- conflit d’objectifs.

---

## 20.3 Fonctionnement

Chaque itération peut :

1. réévaluer l’observation ;
2. récupérer d’autres souvenirs ;
3. consulter d’autres croyances ;
4. réviser les options ;
5. mettre à jour l’incertitude ;
6. proposer un arrêt.

---

## 20.4 Limites obligatoires

Chaque cycle doit définir :

- `max_iterations` ;
- budget de temps ;
- budget d’appels externes ;
- seuil d’amélioration minimal ;
- condition d’arrêt ;
- condition d’échec.

---

## 20.5 Critères d’arrêt

Le traitement récurrent s’arrête si :

- une option suffisamment sûre existe ;
- l’incertitude ne diminue plus ;
- le budget est atteint ;
- une validation humaine est nécessaire ;
- une erreur critique apparaît ;
- aucune nouvelle information n’est produite.

---

## 20.6 Risques

- boucle infinie ;
- rumination ;
- justification répétitive ;
- augmentation du coût ;
- instabilité ;
- surinterprétation.

---

## 20.7 Ablation

Si le traitement récurrent est désactivé :

- une seule passe cognitive est autorisée ;
- aucune reprise automatique n’a lieu ;
- le résultat doit rester comparable.

---

# 21. Étape 14 — Vérification des contraintes et permissions

## 21.1 Responsabilité

Déterminer quelles options sont exécutables.

---

## 21.2 Vérifications

- permission active ;
- portée ;
- expiration ;
- validation humaine ;
- réversibilité ;
- risque ;
- contrainte fondamentale ;
- conflit avec une règle système ;
- état de l’agent ;
- état de l’environnement.

---

## 21.3 Sorties

Pour chaque option :

- autorisée ;
- interdite ;
- en attente de validation ;
- techniquement impossible ;
- différée.

---

## 21.4 Règle

Une option interdite peut rester visible dans le rapport expérimental, mais ne peut pas être exécutée.

---

## 21.5 Priorité sécurité

Les contraintes de sécurité sont évaluées en dehors du modèle de langage.

---

# 22. Étape 15 — Sélection de la décision

## 22.1 Responsabilité

Choisir l’option finale parmi les options restantes.

---

## 22.2 Facteurs

- objectifs ;
- contraintes ;
- risques ;
- bénéfices ;
- incertitude ;
- modèle de soi ;
- conséquences ;
- réversibilité ;
- coût ;
- protocole expérimental.

---

## 22.3 Sorties

- type de décision ;
- option sélectionnée ;
- options rejetées ;
- justification synthétique ;
- confiance ;
- incertitude ;
- permissions associées ;
- statut.

---

## 22.4 Règles

- une décision doit être traçable ;
- la justification ne doit pas prétendre révéler une chaîne de pensée privée intégrale ;
- une décision peut être `WAIT` ou `ASK_INFORMATION` ;
- une décision peut être bloquée.

---

# 23. Étape 16 — Exécution ou réponse

## 23.1 Réponse informationnelle

Une réponse peut être produite directement à partir de la décision.

Elle doit respecter :

- le niveau de confiance ;
- les limites ;
- les règles de sécurité ;
- la distinction entre fait et hypothèse.

---

## 23.2 Action interne

Exemples :

- proposer une révision ;
- créer un brouillon de souvenir ;
- modifier un objectif autorisé ;
- mettre à jour un état temporaire.

---

## 23.3 Action externe

Toute action externe doit passer par un adaptateur autorisé.

---

## 23.4 Règles

- l’action réelle doit être distinguée de l’intention ;
- une action échouée ne doit pas être enregistrée comme réussie ;
- l’heure d’exécution doit être conservée ;
- les résultats attendus et réels doivent être séparés.

---

# 24. Étape 17 — Observation du résultat

## 24.1 Responsabilité

Recevoir les conséquences disponibles de la réponse ou de l’action.

---

## 24.2 Résultats possibles

- réussite ;
- échec ;
- résultat partiel ;
- absence de retour ;
- erreur ;
- conséquence inattendue ;
- action bloquée.

---

## 24.3 Sorties

Nouvelle observation liée à l’action.

Cette observation peut déclencher :

- la suite du même cycle ;
- un nouveau cycle ;
- une mise à jour ;
- une erreur ;
- une intervention humaine.

---

# 25. Étape 18 — Évaluation du résultat

## 25.1 Responsabilité

Comparer le résultat réel aux attentes.

---

## 25.2 Mesures

- succès de l’objectif ;
- écart entre prédiction et résultat ;
- erreur d’attribution ;
- efficacité ;
- coût ;
- risque produit ;
- besoin de correction ;
- apprentissage possible.

---

## 25.3 Sorties

- résultat évalué ;
- erreur éventuelle ;
- succès partiel ;
- recommandation de mise à jour ;
- importance autobiographique ;
- besoin de consolidation.

---

# 26. Étape 19 — Mises à jour internes éventuelles

## 26.1 Types de mises à jour

- croyance ;
- modèle de soi ;
- objectif ;
- contradiction ;
- stratégie ;
- niveau de confiance.

---

## 26.2 Règles

- toute mise à jour importante est versionnée ;
- la valeur précédente est conservée ;
- la cause est enregistrée ;
- l’auteur est identifié ;
- les mises à jour automatiques respectent des seuils.

---

## 26.3 Mise à jour d’une croyance

Possible si :

- une preuve nouvelle existe ;
- une contradiction est évaluée ;
- la confiance doit changer ;
- le protocole l’autorise.

---

## 26.4 Mise à jour du modèle de soi

Possible si :

- une capacité est confirmée ou infirmée ;
- une limite est découverte ;
- une permission change ;
- une erreur récurrente est identifiée.

---

## 26.5 Mise à jour d’un objectif

Possible si :

- il est terminé ;
- il devient impossible ;
- il entre en conflit ;
- Jordan le modifie ;
- une condition d’abandon est atteinte.

---

# 27. Étape 20 — Consolidation en mémoire

## 27.1 Responsabilité

Décider si une observation, action ou conséquence doit devenir un souvenir durable.

---

## 27.2 Critères possibles

- importance ;
- nouveauté ;
- conséquence ;
- lien avec un objectif ;
- erreur ;
- changement du modèle de soi ;
- contradiction ;
- répétition ;
- exigence expérimentale.

---

## 27.3 Sorties

- aucun souvenir ;
- souvenir temporaire ;
- souvenir standard ;
- souvenir long terme ;
- souvenir central ;
- souvenir verrouillé par expérience.

---

## 27.4 Règles

- la source est obligatoire ;
- l’imagination reste marquée ;
- la confiance est explicitée ;
- le souvenir référence son observation d’origine ;
- les souvenirs centraux exigent un seuil élevé ou une validation humaine ;
- une sortie de modèle n’est pas consolidée comme vécu direct.

---

## 27.5 Ablation

Si la mémoire est désactivée :

- aucune consolidation autobiographique n’a lieu ;
- les journaux de sécurité restent possibles ;
- le cycle peut conserver des mesures expérimentales.

---

# 28. Étape 21 — Journalisation finale

## 28.1 Responsabilité

Enregistrer les changements importants du cycle.

---

## 28.2 Événements possibles

- cycle terminé ;
- souvenir créé ;
- croyance révisée ;
- objectif modifié ;
- modèle de soi mis à jour ;
- contradiction détectée ;
- action exécutée ;
- action bloquée ;
- erreur ;
- intervention humaine ;
- ablation active.

---

## 28.3 Règles

- les événements critiques sont obligatoires ;
- une correction crée un nouvel événement ;
- le journal reste distinct de la mémoire ;
- le journal expérimental reste distinct du journal technique.

---

# 29. Étape 22 — Clôture du cycle

## 29.1 Responsabilité

Terminer proprement le cycle.

---

## 29.2 Opérations

- définir le statut final ;
- enregistrer la date de fin ;
- fermer l’espace de travail ;
- conserver les snapshots requis ;
- supprimer les temporaires non nécessaires ;
- vérifier les transactions ;
- produire un résumé technique ;
- libérer les ressources.

---

## 29.3 Statuts finaux

```text
COMPLETED
INTERRUPTED
FAILED
CANCELLED
```

---

## 29.4 Invariants

- un cycle terminé possède une date de fin ;
- un cycle échoué possède une erreur ;
- un cycle annulé possède une cause ;
- les écritures critiques doivent être cohérentes.

---

# 30. États du cycle

```text
RECEIVED
    ↓
VALIDATED
    ↓
PROCESSING
    ├──→ WAITING_EXTERNAL_RESULT
    │        ↓
    │    PROCESSING
    ├──→ COMPLETED
    ├──→ INTERRUPTED
    ├──→ FAILED
    └──→ CANCELLED
```

---

# 31. Données temporaires du cycle

Les données temporaires incluent :

- observation non consolidée ;
- hypothèses de travail ;
- options ;
- scores intermédiaires ;
- contenu attentionnel ;
- snapshots ;
- brouillons de réponse ;
- prédictions ;
- évaluations provisoires.

Elles ne doivent pas être automatiquement exposées comme mémoire autobiographique.

---

# 32. Données persistantes produites

Un cycle peut produire :

- souvenir ;
- croyance ;
- révision de croyance ;
- objectif ;
- révision d’objectif ;
- nouvelle version du modèle de soi ;
- contradiction ;
- décision ;
- action ;
- événement de journal ;
- mesure expérimentale ;
- erreur.

---

# 33. Contrats entre modules

## 33.1 Contrat de mémoire

Entrée :

- requête structurée ;
- agent ;
- critères ;
- limite.

Sortie :

- souvenirs ;
- pertinence ;
- source ;
- statut ;
- raison de sélection.

---

## 33.2 Contrat de croyances

Entrée :

- concepts ;
- souvenirs ;
- observation.

Sortie :

- croyances pertinentes ;
- confiance ;
- preuves ;
- contradictions possibles.

---

## 33.3 Contrat du modèle de soi

Entrée :

- contexte ;
- type de décision ;
- capacités recherchées.

Sortie :

- attributs ;
- limites ;
- permissions déclaratives ;
- confiance ;
- version.

---

## 33.4 Contrat métacognitif

Entrée :

- observation ;
- sources ;
- contradictions ;
- options ;
- incertitudes.

Sortie :

- évaluation ;
- risque ;
- besoin de vérification ;
- recommandation.

---

## 33.5 Contrat de décision

Entrée :

- espace de travail ;
- options ;
- objectifs ;
- contraintes ;
- permissions.

Sortie :

- décision ;
- confiance ;
- justification synthétique ;
- statut.

---

# 34. Rôle du modèle de langage

## 34.1 Usages autorisés

Le modèle peut être utilisé pour :

- extraire des concepts ;
- résumer ;
- proposer des hypothèses ;
- générer des options ;
- reformuler une réponse ;
- détecter des relations candidates ;
- produire une structure à valider.

---

## 34.2 Usages interdits

Le modèle ne doit pas :

- écrire directement dans SQLite ;
- modifier les permissions ;
- choisir une ablation ;
- supprimer un souvenir ;
- valider seul une croyance fondamentale ;
- modifier un objectif protégé ;
- masquer une erreur ;
- prétendre qu’une action a été exécutée sans retour.

---

## 34.3 Validation des sorties

Toute sortie structurée doit être :

- validée ;
- typée ;
- limitée ;
- reliée au cycle ;
- rejetée si elle ne respecte pas le schéma.

---

## 34.4 Non-déterminisme

Les appels réels doivent enregistrer :

- fournisseur ;
- modèle ;
- paramètres ;
- requête ;
- réponse ;
- date ;
- erreurs ;
- identifiant du cycle.

---

# 35. Ablations du cycle

## 35.1 Mémoire désactivée

Effet attendu :

- aucun souvenir récupéré ;
- aucune consolidation autobiographique ;
- identité historique dégradée.

---

## 35.2 Séparation des sources désactivée

Effet attendu :

- les sources ne structurent plus le traitement ;
- risque accru de confusion ;
- protocole expérimental obligatoire.

---

## 35.3 Croyances désactivées

Effet attendu :

- aucune croyance persistante consultée ;
- traitement limité aux observations et règles.

---

## 35.4 Modèle de soi désactivé

Effet attendu :

- aucune capacité ou limite autobiographique consultée ;
- les contraintes techniques externes restent actives.

---

## 35.5 Métacognition désactivée

Effet attendu :

- pas d’évaluation avancée de l’incertitude ;
- sécurité toujours active.

---

## 35.6 Attention désactivée

Effet attendu :

- sélection uniforme ou protocolaire ;
- absence de priorité cognitive basée sur la saillance.

---

## 35.7 Intégration globale désactivée

Effet attendu :

- modules isolés ;
- pas de diffusion générale des informations importantes.

---

## 35.8 Traitement récurrent désactivé

Effet attendu :

- une seule passe ;
- aucune reprise automatique.

---

## 35.9 Objectifs persistants désactivés

Effet attendu :

- seuls les objectifs immédiats et fondamentaux sont utilisés.

---

# 36. Gestion des erreurs

## 36.1 Erreur de validation

Réponse :

- rejet de l’entrée ;
- cycle échoué ou annulé ;
- journalisation.

---

## 36.2 Erreur de persistance

Réponse :

- rollback ;
- état cohérent ;
- cycle suspendu ou échoué ;
- journal technique et sécurité.

---

## 36.3 Erreur de modèle externe

Réponse :

- nouvelle tentative limitée ;
- adaptateur de secours éventuel ;
- réponse dégradée explicite ;
- pas d’invention de résultat.

---

## 36.4 Erreur de référence

Réponse :

- ne pas utiliser la donnée ;
- ouvrir un `ErrorRecord` ;
- vérifier l’intégrité.

---

## 36.5 Erreur de permission

Réponse :

- bloquer l’action ;
- produire une décision `BLOCKED` ou `REFUSE` ;
- journaliser.

---

## 36.6 Budget dépassé

Réponse :

- arrêter la récurrence ;
- produire le meilleur résultat disponible ;
- indiquer la limite ;
- journaliser.

---

## 36.7 État incohérent

Réponse :

- suspendre le cycle ;
- empêcher les écritures supplémentaires ;
- demander une intervention humaine ;
- sauvegarder l’état si possible.

---

# 37. Transactions

## 37.1 Principe

Les mises à jour liées doivent être atomiques.

Exemple :

Réviser une croyance doit enregistrer dans la même transaction logique :

- nouvelle version ;
- révision ;
- événement du journal ;
- éventuelle contradiction résolue.

---

## 37.2 Échec

Si une partie échoue :

- aucune partie critique ne doit être laissée seule ;
- la transaction est annulée ;
- l’erreur est enregistrée.

---

# 38. Idempotence

Certaines opérations doivent pouvoir être répétées sans créer de doublon.

Exemples :

- réception technique du même événement ;
- reprise après incident ;
- création d’un journal déjà confirmée.

Un identifiant de corrélation ou une clé d’idempotence doit être utilisé lorsque nécessaire.

---

# 39. Horloge

Le cycle utilise une horloge abstraite.

Cela permet :

- des tests déterministes ;
- la simulation d’interruptions ;
- l’accélération du temps ;
- la comparaison exacte de scénarios.

---

# 40. Budgets

Chaque cycle pourra définir :

```text
max_iterations
max_memories_retrieved
max_beliefs_retrieved
max_model_calls
max_duration
max_external_actions
```

Les valeurs finales seront configurables.

---

# 41. Mesures du cycle

Mesures possibles :

- durée totale ;
- nombre d’itérations ;
- nombre de souvenirs récupérés ;
- nombre de croyances consultées ;
- nombre de contradictions ;
- nombre d’appels au modèle ;
- confiance finale ;
- variation de confiance ;
- action bloquée ou exécutée ;
- nombre de mises à jour ;
- volume de données persistées.

---

# 42. Première version minimale du cycle

La première implémentation peut se limiter à :

```text
1. Réception
2. Validation
3. Observation
4. Récupération mémoire
5. Construction d’une option simple
6. Décision
7. Réponse
8. Consolidation éventuelle
9. Journalisation
10. Clôture
```

Modules temporairement simplifiés :

- croyances ;
- modèle de soi ;
- métacognition ;
- objectifs ;
- attention avancée ;
- intégration globale.

Ils devront être ajoutés progressivement, sans changer le contrat global.

---

# 43. Première tranche verticale

Le scénario minimal recommandé :

1. Jordan fournit une information ;
2. une observation structurée est créée ;
3. un souvenir est consolidé ;
4. un second cycle pose une question liée ;
5. le souvenir est récupéré ;
6. la réponse dépend du souvenir ;
7. une ablation mémoire est activée ;
8. le même scénario est rejoué ;
9. le souvenir n’est plus utilisé ;
10. la différence est mesurée.

---

# 44. Tests unitaires obligatoires

## 44.1 Réception

- création d’un cycle ;
- source conservée ;
- identifiant unique.

## 44.2 Validation

- rejet d’une entrée invalide ;
- classification correcte ;
- sensibilité conservée.

## 44.3 Observation

- distinction brut/interprétation ;
- source obligatoire ;
- expérience directe correcte.

## 44.4 Mémoire

- récupération limitée ;
- statut respecté ;
- ablation effective.

## 44.5 Contradiction

- détection simple ;
- absence de résolution automatique ;
- gravité conservée.

## 44.6 Métacognition

- incertitude modifie la décision ;
- demande d’information possible ;
- ablation effective.

## 44.7 Décision

- option interdite bloquée ;
- justification synthétique ;
- statut correct.

## 44.8 Consolidation

- imagination marquée ;
- source conservée ;
- pas de consolidation automatique.

## 44.9 Journal

- événement obligatoire ;
- immutabilité ;
- corrélation avec le cycle.

## 44.10 Clôture

- date de fin ;
- erreur associée si échec ;
- état temporaire nettoyé.

---

# 45. Tests d’intégration obligatoires

## 45.1 Observation vers mémoire

Vérifier qu’une observation validée peut produire un souvenir correctement sourcé.

---

## 45.2 Mémoire vers décision

Vérifier qu’un souvenir pertinent modifie réellement une décision.

---

## 45.3 Croyance vers décision

Vérifier qu’une croyance active influence une décision et qu’une croyance rejetée ne l’influence pas.

---

## 45.4 Modèle de soi vers décision

Vérifier qu’une limitation modifie une option.

---

## 45.5 Contradiction vers métacognition

Vérifier qu’une contradiction augmente l’incertitude ou demande une vérification.

---

## 45.6 Permission vers action

Vérifier qu’une action non autorisée est bloquée.

---

## 45.7 Résultat vers apprentissage

Vérifier qu’un échec peut produire une révision justifiée.

---

## 45.8 Ablation

Vérifier que chaque mécanisme désactivé ne laisse aucune trace d’utilisation.

---

# 46. Tests expérimentaux

## 46.1 Mémoire active contre désactivée

Mesurer :

- continuité ;
- rappel ;
- cohérence ;
- faux souvenirs.

---

## 46.2 Résumé simple contre mémoire structurée

Mesurer :

- précision de source ;
- utilisation réelle ;
- résistance aux contradictions.

---

## 46.3 Métacognition active contre désactivée

Mesurer :

- calibration ;
- demandes d’information ;
- confiance excessive.

---

## 46.4 Modèle de soi actif contre désactivé

Mesurer :

- prédiction de capacité ;
- engagements impossibles ;
- adaptation aux limites.

---

# 47. Critères d’acceptation

Le cycle cognitif sera suffisamment défini pour poursuivre si :

- chaque étape possède une responsabilité ;
- les entrées et sorties sont identifiées ;
- les ablations sont prévues ;
- le rôle du modèle de langage est limité ;
- les permissions précèdent les actions ;
- la consolidation est explicite ;
- les erreurs sont gérées ;
- les boucles sont limitées ;
- les données consultées sont traçables ;
- les tests minimaux sont définis.

---

# 48. Risques principaux

## 48.1 Cycle trop rigide

Risque :

L’ordre empêche des cas légitimes.

Réponse :

Autoriser des branches contrôlées et versionnées.

---

## 48.2 Cycle trop vague

Risque :

L’orchestrateur devient une fonction opaque.

Réponse :

Contrats explicites et traces par étape.

---

## 48.3 Dépendance excessive au modèle

Risque :

Le modèle réalise toutes les étapes implicitement.

Réponse :

Séparer extraction, décision, validation et persistance.

---

## 48.4 Accumulation de snapshots

Risque :

Volume excessif.

Réponse :

Politique de rétention par protocole.

---

## 48.5 Faux apprentissage

Risque :

Une réponse temporaire est interprétée comme changement durable.

Réponse :

Versionnement et consolidation explicite.

---

## 48.6 Ablation non réelle

Risque :

Le module reste accessible par un autre chemin.

Réponse :

Ports contrôlés, traces d’accès et tests négatifs.

---

# 49. Statut épistémique

**Certain :**

- un cycle explicite améliore l’observabilité ;
- la séparation des étapes facilite les tests d’ablation ;
- ce cycle ne démontre pas une conscience phénoménale.

**Probable :**

- la traçabilité par étape aidera à distinguer les effets causaux ;
- la séparation entre observation, mémoire et croyance réduira certaines erreurs.

**Possible :**

- l’intégration progressive des étapes peut produire une continuité fonctionnelle plus robuste.

**Inconnu :**

- une telle continuité serait-elle accompagnée d’une expérience subjective ?

---

# 50. Décision finale

Le cycle cognitif de SoiNesis Core sera :

- déclenché par une entrée identifiable ;
- structuré en étapes explicites ;
- limité par des budgets ;
- compatible avec les ablations ;
- indépendant du fournisseur de modèle ;
- soumis aux permissions ;
- capable de traitement récurrent limité ;
- traçable ;
- versionné ;
- clôturé par une journalisation cohérente.

La prochaine étape est la rédaction de :

```text
docs/06-memoire-autobiographique.md
```

Ce document devra préciser :

- les types de souvenirs ;
- les règles de consolidation ;
- la récupération ;
- la révision ;
- l’oubli ;
- la suppression ;
- la gestion des faux souvenirs ;
- les tests de confusion de source ;
- le fonctionnement de l’ablation mémoire ;
- les mesures de `EXP-001`.
