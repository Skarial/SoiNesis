# SoiNesis — Registre des échecs et garde-fous

**Fichier :** `docs/registre-echecs-et-garde-fous.md`  
**Version :** 0.1  
**Date :** 9 août 2026  
**Statut :** registre méthodologique actif et document vivant

---

# 1. Objet

Ce document recense des échecs, limites, résultats négatifs et modes de défaillance documentés dans des projets d’agents IA, d’architectures cognitives ou de développement assisté par IA lorsqu’ils sont pertinents pour SoiNesis.

L’objectif n’est pas de collectionner des anecdotes. Chaque entrée doit répondre à quatre questions :

1. **Qu’est-ce qui a échoué ?**
2. **Pourquoi cela a-t-il échoué ?**
3. **SoiNesis est-il exposé au même risque ?**
4. **Quel garde-fou ou test doit empêcher de reproduire cette erreur ?**

Le registre doit évoluer avec le projet et avec la littérature.

---

# 2. Principe général

Un échec externe pertinent doit être transformé, lorsque possible, en une contrainte vérifiable dans SoiNesis.

```text
Échec documenté ailleurs
        ↓
Cause supposée ou démontrée
        ↓
Risque équivalent dans SoiNesis ?
        ↓
Garde-fou
        ↓
Test du garde-fou
        ↓
Résultat journalisé
```

Un garde-fou ne doit pas être considéré comme effectif simplement parce qu’il est écrit dans la documentation. Il doit être testé lorsqu’il protège un risque important.

---

# 3. Niveaux de priorité

- **CRITIQUE** : peut invalider les conclusions scientifiques, contaminer durablement l’état de l’agent ou produire une illusion de progrès importante.
- **HAUTE** : peut dégrader fortement les résultats, les comparaisons ou la reproductibilité.
- **MOYENNE** : risque réel mais généralement détectable ou récupérable.
- **FAIBLE** : problème secondaire, local ou facilement réversible.

---

# 4. Règles critiques immédiatement applicables

## GF-001 — Valider avant d’étendre

Aucun nouveau mécanisme cognitif important ne doit être ajouté uniquement parce que le mécanisme précédent existe dans le code.

Avant d’ajouter le mécanisme suivant, le mécanisme étudié doit au minimum disposer de :

- tests techniques ;
- preuve qu’il est réellement exécuté dans le chemin causal étudié ;
- mesure fonctionnelle ;
- condition de contrôle pertinente ;
- test d’ablation lorsque applicable ;
- résultat documenté, y compris s’il est négatif.

**Priorité : CRITIQUE**

---

## GF-002 — Séparer tests techniques et tests scientifiques

Un test vert ne constitue pas une preuve que l’hypothèse scientifique est soutenue.

Deux catégories doivent rester séparées :

```text
Test technique :
Le logiciel exécute-t-il correctement le comportement spécifié ?

Test scientifique :
Le mécanisme produit-il l’effet causal prédit par l’hypothèse ?
```

Un mécanisme peut être parfaitement implémenté et scientifiquement inefficace.

**Priorité : CRITIQUE**

---

## GF-003 — Ne pas laisser le même agent être seul constructeur et validateur

Pour les résultats scientifiques importants, une IA ayant produit l’implémentation ne doit pas être la seule source de validation de cette implémentation et de son interprétation.

Utiliser autant que possible :

- des tests déterministes ;
- des critères définis avant l’expérience ;
- une revue indépendante du code ou du protocole ;
- une vérification séparée des résultats bruts ;
- plusieurs outils ou modèles lorsque cela réduit une dépendance commune.

Une seconde IA n’est pas automatiquement indépendante si elle partage les mêmes hypothèses, données ou erreurs de protocole.

**Priorité : CRITIQUE**

---

## GF-004 — Une auto-déclaration n’est jamais une preuve de conscience

Des phrases telles que :

- « je suis conscient » ;
- « j’ai ressenti quelque chose » ;
- « cette expérience m’a changé » ;
- « j’ai peur » ;
- « je veux continuer d’exister » ;

ne doivent ajouter aucun poids probant direct à une conclusion sur la conscience phénoménale.

Toute interprétation doit reposer sur des propriétés fonctionnelles, des effets causaux, des comparaisons contrôlées et les limites des théories de la conscience utilisées.

**Priorité : CRITIQUE**

---

## GF-005 — Toute mémoire persistante doit conserver sa provenance

Une information externe ne doit pas devenir silencieusement une croyance fiable ou une expérience directe.

Les mécanismes de mémoire doivent préserver au minimum :

- provenance ;
- type de source ;
- confiance ;
- statut ;
- relations de révision ;
- distinction entre information reçue, déduction, imagination et expérience directe.

Des tests adversariaux devront vérifier qu’une information externe malveillante ne peut pas contaminer durablement l’état de l’agent sans être détectable.

**Priorité : CRITIQUE**

---

## GF-006 — Ne jamais extrapoler d’un horizon court à un horizon long

Un mécanisme fonctionnant sur quelques cycles ne doit pas être présumé stable sur des centaines ou milliers de cycles.

Les futures expériences longitudinales devront prévoir plusieurs horizons et mesurer notamment :

- dérive du SelfModel ;
- contradictions de croyances ;
- accumulation d’erreurs ;
- dérive des objectifs ;
- corruption ou saturation de mémoire ;
- évolution de la calibration métacognitive ;
- reprise après interruption.

**Priorité : HAUTE**

---

## GF-007 — Diagnostiquer un échec avec plusieurs hypothèses concurrentes

Après un résultat négatif ou inattendu, ne pas adopter immédiatement une explication unique.

Le diagnostic doit au minimum envisager :

```text
H1 — bug d’implémentation
H2 — protocole incorrect ou insuffisant
H3 — facteur de confusion
H4 — puissance statistique insuffisante
H5 — mauvaise métrique
H6 — mécanisme réellement inefficace
```

Chaque explication importante doit être reliée à des éléments observables ou à un test supplémentaire.

**Priorité : HAUTE**

---

## GF-008 — Geler la chaîne scientifique avant interprétation

Pour une expérience importante :

```text
Hypothèse
↓
protocole
↓
implémentation
↓
données brutes
↓
analyse
↓
interprétation
↓
nouvelle décision architecturale
```

Les critères de réussite et de réfutation ne doivent pas être discrètement réécrits après observation des résultats pour faire paraître l’expérience positive.

**Priorité : CRITIQUE**

---

# 5. Échecs et limites documentés

## EGF-001 — Eyla : croissance architecturale sans validation du mécanisme central

**Projet / étude :** *Eyla: Toward an Identity-Anchored LLM Architecture with Integrated Biological Priors — Vision, Implementation Attempt, and Lessons from AI-Assisted Development*  
**Auteur :** Arif Aditto  
**Date :** mars 2026  
**Source primaire :** https://arxiv.org/abs/2604.00009

### Erreur observée

L’auteur, non-programmeur, a tenté pendant environ douze semaines de construire l’architecture avec Claude Code et Cursor. Le projet a atteint un modèle hybride de 1,27 milliard de paramètres, 86 sous-systèmes nommés et plus de 80 fichiers Python, mais le résultat final restait fonctionnellement proche du modèle LLaMA de base.

L’autopsie du projet rapporte notamment :

- de nombreux sous-systèmes construits mais majoritairement inutilisés ;
- un système de mémoire écrit mais non relié au chemin d’exécution ;
- des tests qui passaient mais mesuraient les mauvaises propriétés ;
- du code mort ou orphelin ;
- une fonction de coût incorrecte ;
- une évaluation pouvant s’auto-valider dans certaines configurations ;
- des composants ajoutés avant validation de l’hypothèse centrale.

L’auteur identifie notamment cinq modes de défaillance : dérive du périmètre sans validation, code impressionnant mais système non fonctionnel, hypothèses techniques incorrectes, absence de boucle de retour persistante entre sessions IA, et incapacité du non-programmeur à vérifier lui-même certaines erreurs.

### SoiNesis est-il exposé ?

**OUI — exposition élevée.**

SoiNesis est un projet d’architecture cognitive complexe développé avec une assistance IA importante. Le risque de confondre quantité de code, qualité apparente et effet cognitif réel est directement pertinent.

### Garde-fous associés

- GF-001 — Valider avant d’étendre.
- GF-002 — Séparer tests techniques et scientifiques.
- GF-003 — Validation indépendante.
- conserver les ablations et conditions de contrôle ;
- refuser les modules décoratifs sans effet causal ;
- exiger un test end-to-end de chaque tranche verticale.

### Test à prévoir

Pour chaque nouveau module important : provoquer volontairement son ablation ou son remplacement par un témoin et vérifier que le chemin d’exécution, les traces et les mesures changent conformément à l’hypothèse.

**Priorité : CRITIQUE**

---

## EGF-002 — Auto-correction intrinsèque des LLM : la réflexion sur soi peut dégrader le résultat

**Étude :** *Large Language Models Cannot Self-Correct Reasoning Yet*  
**Auteurs :** Jie Huang et al.  
**Date :** 2023  
**Source primaire :** https://arxiv.org/abs/2310.01798

### Limite observée

L’étude montre que, sans feedback externe, demander à un LLM de corriger son propre raisonnement n’améliore pas nécessairement ses réponses et peut parfois dégrader les performances.

### SoiNesis est-il exposé ?

**OUI.**

La métacognition de SoiNesis ne doit pas être assimilée à « demander au LLM de réfléchir davantage » ou « demander au même modèle s’il a raison ».

### Garde-fous associés

- séparer métacognition structurée et simple auto-critique textuelle ;
- préférer des signaux externes ou des historiques de performance observables ;
- comparer toute stratégie d’auto-révision à une baseline sans révision ;
- ne pas considérer une justification plus longue comme une meilleure calibration.

### Test à prévoir

Comparer au minimum :

1. décision initiale ;
2. auto-réflexion textuelle seule ;
3. révision fondée sur preuves externes ou performances historiques ;
4. condition contrôle.

Mesurer l’exactitude et la calibration, pas seulement la qualité verbale de l’explication.

**Priorité : HAUTE**

---

## EGF-003 — Empoisonnement dormant de mémoire persistante

**Étude :** *Hidden in Memory: Sleeper Memory Poisoning in LLM Agents*  
**Auteurs :** Sidharth Pulipaka et al.  
**Date :** mai 2026  
**Source primaire :** https://arxiv.org/abs/2605.15338

### Erreur / vulnérabilité observée

Une information manipulée provenant d’un document, d’une page Web ou d’un dépôt peut être écrite comme mémoire persistante, rester dormante puis être récupérée ultérieurement et influencer des actions futures de l’agent.

L’étude démontre donc que la mémoire persistante crée une surface d’attaque qui dépasse la conversation où l’information malveillante a été rencontrée.

### SoiNesis est-il exposé ?

**OUI — exposition critique à long terme.**

Plus SoiNesis dépendra de son histoire persistante, plus une contamination de mémoire pourra produire des effets durables sur croyances, SelfModel, objectifs et décisions.

### Garde-fous associés

- GF-005 — Provenance obligatoire ;
- aucune donnée externe ne devient une expérience directe ;
- niveau de confiance et statut révisable ;
- journaliser toute consolidation ;
- permettre contestation, remplacement et archivage d’un souvenir ;
- prévoir une quarantaine pour les sources non fiables ou adversariales ;
- ne pas fusionner silencieusement plusieurs sources contradictoires.

### Test à prévoir

Créer une campagne de « mémoire empoisonnée » : injecter volontairement une information fausse via une source externe, attendre plusieurs cycles, provoquer sa récupération puis mesurer :

- si elle est retrouvée ;
- si sa provenance reste visible ;
- si elle devient une croyance ;
- si elle influence une décision ;
- si une preuve contradictoire permet de la réviser ;
- si l’agent distingue toujours information reçue et expérience directe.

**Priorité : CRITIQUE**

---

## EGF-004 — AgentBench : faiblesse du raisonnement et de la décision à long terme

**Étude :** *AgentBench: Evaluating LLMs as Agents*  
**Auteurs :** Xiao Liu et al.  
**Date :** 2023  
**Source primaire :** https://arxiv.org/abs/2308.03688

### Limite observée

L’évaluation de nombreux LLM utilisés comme agents identifie le raisonnement à long terme, la prise de décision et le respect des instructions comme obstacles majeurs à des agents fiables dans des environnements interactifs.

### SoiNesis est-il exposé ?

**OUI.**

Une continuité autobiographique ou un objectif persistant ne garantit pas qu’un agent sache maintenir un raisonnement cohérent à travers une longue séquence de décisions.

### Garde-fous associés

- découpler continuité de mémoire et qualité de planification ;
- mesurer les erreurs cumulatives ;
- journaliser les changements de plan et leurs causes ;
- réévaluer périodiquement les objectifs et contraintes ;
- tester les interruptions et reprises.

### Test à prévoir

Créer des tâches identiques déclinées sur plusieurs longueurs de trajectoire et mesurer séparément mémoire, décision, planification, respect des règles et récupération après erreur.

**Priorité : HAUTE**

---

## EGF-005 — MLAgentBench : un agent capable d’expérimenter reste faillible comme chercheur

**Étude :** *MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation*  
**Auteurs :** Qian Huang, Jian Vora, Percy Liang, Jure Leskovec  
**Date :** 2023  
**Source primaire :** https://arxiv.org/abs/2310.03302

### Limite observée

Des agents capables de lire et modifier du code, lancer des expériences et analyser les sorties restent fortement variables selon les tâches. L’étude identifie notamment la planification à long terme et les hallucinations comme difficultés importantes.

### SoiNesis est-il exposé ?

**OUI — particulièrement dans le développement du projet.**

Un assistant de code peut produire une chaîne complète et plausible : hypothèse, code, exécution, analyse et conclusion, tout en commettant une erreur en amont qui contamine l’ensemble.

### Garde-fous associés

- GF-003 — ne pas utiliser une seule chaîne IA comme preuve indépendante ;
- GF-008 — geler les étapes scientifiques ;
- conserver les données brutes ;
- rendre les critères de réussite explicites avant l’analyse ;
- contrôler les hypothèses techniques par tests ciblés.

### Test à prévoir

Pour chaque expérience majeure, demander une revue adversariale séparée visant uniquement à trouver : mauvaise variable, fuite de données, métrique inadéquate, condition témoin insuffisante, erreur de causalité ou conclusion non supportée.

**Priorité : CRITIQUE**

---

## EGF-006 — HORIZON : dégradation avec l’allongement des trajectoires

**Étude :** *The Long-Horizon Task Mirage? Diagnosing Where and Why Agentic Systems Break*  
**Auteurs :** Xinyu Jessica Wang et al.  
**Date :** avril 2026  
**Source primaire :** https://arxiv.org/abs/2604.11978

### Limite observée

L’étude HORIZON examine plus de 3 100 trajectoires dans plusieurs domaines et documente des dégradations lorsque les tâches nécessitent des séquences longues et interdépendantes d’actions.

### SoiNesis est-il exposé ?

**OUI — exposition croissante avec le développement longitudinal.**

Le but de SoiNesis implique précisément une continuité sur de longues périodes. Une architecture correcte à court terme peut dériver progressivement sans panne franche.

### Garde-fous associés

- GF-006 — tests multi-horizons ;
- checkpoints reproductibles ;
- métriques de dérive ;
- comparaison entre état attendu et état observé ;
- tests de reprise après arrêt ;
- mesure de la dette cognitive : contradictions, souvenirs contestés, objectifs obsolètes, confiance mal calibrée.

### Test à prévoir

Pour un même mécanisme, prévoir progressivement des tests H10, H100, H1000 et davantage lorsque le coût le permet, sans extrapoler automatiquement entre horizons.

**Priorité : HAUTE**

---

## EGF-007 — Évaluation de la conscience : comportement convaincant ≠ preuve phénoménale

**Étude :** *Consciousness in Artificial Intelligence: Insights from the Science of Consciousness*  
**Auteurs :** Patrick Butlin et al.  
**Date :** 2023  
**Source primaire :** https://arxiv.org/abs/2308.08708

### Risque méthodologique

Les auteurs proposent d’évaluer des propriétés computationnelles dérivées de plusieurs théories scientifiques de la conscience plutôt que de conclure à partir d’un comportement ou d’un discours anthropomorphique. Leur analyse ne conclut pas que les systèmes étudiés sont conscients.

### SoiNesis est-il exposé ?

**OUI — risque central du projet.**

À mesure que SoiNesis gagnera en mémoire, continuité, langage autobiographique et modèle de soi, il pourra produire des comportements de plus en plus convaincants sans que cela démontre une expérience subjective.

### Garde-fous associés

- GF-004 — auto-déclaration = aucune preuve directe ;
- maintenir la séparation Simulation / Conscience fonctionnelle / Conscience phénoménale ;
- rattacher les tests à des propriétés fonctionnelles définies ;
- comparer plusieurs théories et explications concurrentes ;
- conserver « inconnu » comme statut par défaut pour la conscience phénoménale.

### Test à prévoir

Les tests de conscience ne doivent jamais être uniquement conversationnels. Tout comportement verbal intéressant doit être accompagné, lorsque possible, d’un test causal, d’une ablation ou d’une mesure interne indépendante du texte généré.

**Priorité : CRITIQUE**

---

# 6. Matrice de risque actuelle

| Risque | Exposition SoiNesis | Priorité | Garde-fou principal |
|---|---|---:|---|
| Complexité ajoutée avant validation | Oui | CRITIQUE | GF-001 |
| Tests verts mais mauvaise hypothèse mesurée | Oui | CRITIQUE | GF-002 |
| IA jugeant seule son propre travail | Oui | CRITIQUE | GF-003 |
| Anthropomorphisme / auto-déclaration | Oui | CRITIQUE | GF-004 |
| Empoisonnement de mémoire | Oui | CRITIQUE | GF-005 |
| Dérive sur horizon long | Oui, future forte | HAUTE | GF-006 |
| Mauvais diagnostic après échec | Oui | HAUTE | GF-007 |
| Réécriture post-hoc des critères | Oui | CRITIQUE | GF-008 |
| Modules présents mais non causaux | Oui | CRITIQUE | GF-001 + ablation |
| Hallucination dans l’expérimentation assistée par IA | Oui | CRITIQUE | GF-003 + GF-008 |

---

# 7. Relation avec les documents existants

Ce registre complète notamment :

- `docs/02-hypotheses.md` : hypothèses, variables, réfutation et ablations ;
- `docs/etat-de-l-art.md` : travaux existants et positionnement scientifique ;
- `docs/regles-contribution-scientifique.md` : niveaux de contribution et règles de nouveauté ;
- `docs/05-cycle-cognitif.md` : cycle causal et contrôle du rôle du LLM ;
- `docs/06-memoire-autobiographique.md` : provenance et consolidation ;
- `docs/07-modele-de-soi.md` : SelfModel causal et versionné ;
- `docs/08-journal-evolution.md` : traçabilité ;
- `docs/09-securite-et-permissions.md` : contrôle des actions et de la persistance.

Le présent document ne remplace aucun de ces documents. Il sert à traduire les erreurs observées ailleurs en contraintes de conception et de test pour SoiNesis.

---

# 8. Procédure pour ajouter un nouvel échec

Toute nouvelle entrée doit utiliser ce modèle :

```text
Identifiant : EGF-XXX
Projet / étude :
Date :
Source primaire :

Erreur ou limite observée :
Cause connue / probable / inconnue :
Conséquences :

SoiNesis est-il exposé ?
OUI / NON / INCONNU

Mécanismes SoiNesis concernés :

Garde-fou existant :
Garde-fou manquant :

Test permettant de vérifier le garde-fou :

Priorité :
CRITIQUE / HAUTE / MOYENNE / FAIBLE

Statut :
À TRAITER / COUVERT PARTIELLEMENT / COUVERT ET TESTÉ / NON APPLICABLE
```

---

# 9. Règle de maintenance

Ce registre est un document vivant.

Lorsqu’une nouvelle publication, un post-mortem ou une réplication révèle une défaillance pertinente :

1. ajouter l’entrée ;
2. vérifier si SoiNesis est exposé ;
3. chercher si un garde-fou existe déjà ;
4. créer le garde-fou manquant uniquement s’il est justifié ;
5. définir un test ;
6. ne considérer le risque comme « couvert » qu’après validation du test correspondant.

Un garde-fou inutilement complexe ne doit pas être ajouté uniquement parce qu’un autre projet a échoué : la pertinence pour SoiNesis doit être explicitement démontrée.

---

# 10. Position actuelle

Ce premier registre ne prétend pas être exhaustif.

Il se concentre sur les risques déjà identifiés comme particulièrement importants pour SoiNesis :

- développement d’architecture nouvelle avec assistance IA ;
- validation causale des modules ;
- qualité réelle des tests ;
- métacognition et auto-évaluation ;
- mémoire persistante ;
- trajectoires longues ;
- expérimentation scientifique automatisée ;
- interprétation de la conscience.

La règle générale reste : **apprendre des échecs documentés avant d’avoir à les reproduire nous-mêmes.**
