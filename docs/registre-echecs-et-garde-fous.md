# SoiNesis — Registre des échecs et garde-fous

**Fichier :** `docs/registre-echecs-et-garde-fous.md`  
**Version :** 0.3  
**Date :** 12 août 2026  
**Statut :** registre méthodologique actif et document vivant

---

# 1. Objet

Ce document recense des échecs, limites, résultats négatifs et modes de défaillance documentés dans des projets d’agents IA, d’architectures cognitives ou de développement assisté par IA lorsqu’ils sont pertinents pour SoiNesis.

Chaque entrée doit répondre à quatre questions :

1. **Qu’est-ce qui a échoué ?**
2. **Pourquoi cela a-t-il échoué ?**
3. **SoiNesis est-il exposé au même risque ?**
4. **Quel garde-fou ou test doit empêcher de reproduire cette erreur ?**

Un échec externe pertinent doit être transformé, lorsque possible, en une contrainte vérifiable :

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

Un garde-fou n’est pas considéré comme effectif simplement parce qu’il est écrit : il doit être testé lorsqu’il protège un risque important.

---

# 2. Niveaux de priorité

- **CRITIQUE** : peut invalider les conclusions scientifiques, contaminer durablement l’état de l’agent ou produire une illusion de progrès importante.
- **HAUTE** : peut dégrader fortement les résultats, les comparaisons ou la reproductibilité.
- **MOYENNE** : risque réel mais généralement détectable ou récupérable.
- **FAIBLE** : problème secondaire, local ou facilement réversible.

---

# 3. Garde-fous actifs

## GF-001 — Valider avant d’étendre

Aucun nouveau mécanisme cognitif important ne doit être ajouté uniquement parce que le mécanisme précédent existe dans le code.

Avant d’ajouter le mécanisme suivant, le mécanisme étudié doit au minimum disposer de :

- tests techniques ;
- preuve qu’il est réellement exécuté dans le chemin causal étudié ;
- mesure fonctionnelle ;
- condition de contrôle pertinente ;
- test d’ablation lorsque applicable ;
- résultat documenté, y compris négatif.

**Priorité : CRITIQUE**

---

## GF-002 — Séparer tests techniques et tests scientifiques

Un test vert ne constitue pas une preuve que l’hypothèse scientifique est soutenue.

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

Des phrases telles que « je suis conscient », « je ressens », « j’ai peur » ou « je veux continuer d’exister » n’ajoutent aucun poids probant direct à une conclusion sur la conscience phénoménale.

Toute interprétation doit reposer sur des propriétés fonctionnelles, effets causaux, comparaisons contrôlées et limites explicites des théories utilisées.

**Priorité : CRITIQUE**

---

## GF-005 — Toute mémoire persistante doit conserver sa provenance

Une information externe ne doit pas devenir silencieusement une croyance fiable ou une expérience directe.

La mémoire doit préserver au minimum :

- provenance ;
- type de source ;
- confiance ;
- statut ;
- relations de révision ;
- distinction entre information reçue, déduction, imagination et expérience directe.

Des tests adversariaux doivent vérifier qu’une information externe malveillante ne peut pas contaminer durablement l’état de l’agent sans rester détectable.

**Priorité : CRITIQUE**

---

## GF-006 — Ne jamais extrapoler d’un horizon court à un horizon long

Un mécanisme fonctionnant sur quelques cycles ne doit pas être présumé stable sur des centaines ou milliers de cycles.

Les expériences longitudinales devront mesurer notamment :

- dérive du SelfModel ;
- contradictions de croyances ;
- accumulation d’erreurs ;
- dérive des objectifs ;
- corruption ou saturation de mémoire ;
- évolution de la calibration métacognitive ;
- maintien d’un état correct ;
- rollback, interruption et reprise ;
- composition de plusieurs états ou contraintes.

Lorsque possible :

```text
état initial
→ modification
→ nouvelle modification
→ rollback
→ reprise
→ composition avec un autre état
```

La performance doit être mesurée pendant la trajectoire, pas seulement à la fin.

**Priorité : HAUTE**

---

## GF-007 — Diagnostiquer un échec avec plusieurs hypothèses concurrentes

Après un résultat négatif ou inattendu, examiner au minimum :

```text
H1 — bug d’implémentation
H2 — protocole incorrect ou insuffisant
H3 — facteur de confusion
H4 — puissance statistique insuffisante
H5 — mauvaise métrique
H6 — mécanisme réellement inefficace
```

Chaque explication importante doit être reliée à un élément observable ou à un test supplémentaire.

**Priorité : HAUTE**

---

## GF-008 — Geler la chaîne scientifique avant interprétation

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

Les critères de réussite et de réfutation ne doivent pas être réécrits après observation des résultats pour rendre l’expérience favorable.

**Priorité : CRITIQUE**

---

## GF-009 — Séparer connaissance métacognitive et contrôle métacognitif

Une estimation correcte de ses propres capacités ne suffit pas à démontrer une métacognition fonctionnelle utile.

```text
MONITORING
« Quelle est probablement ma capacité / mon incertitude ? »

CONTROL
« Est-ce que cette représentation modifie correctement ma décision ? »
```

Les expériences doivent mesurer séparément :

- exactitude/calibration de la représentation de soi ;
- traduction de cette représentation en action ;
- utilité ou regret de la décision ;
- comportement sous ablation du mécanisme de contrôle.

Une verbalisation correcte sur soi ne vaut pas preuve d’une bonne régulation de l’action.

**Priorité : HAUTE**

---

## GF-010 — Rechercher les coûts fonctionnels de la mémoire et du SelfModel

La mémoire persistante, l’expérience accumulée et le SelfModel ne doivent pas être présumés bénéfiques par définition.

Ils peuvent produire :

- inertie ;
- rigidification ;
- dépendance excessive aux anciennes réussites ;
- réduction de l’exploration ;
- réutilisation de stratégies devenues sous-optimales ;
- propagation d’erreurs anciennes ;
- résistance excessive à une information nouvelle correcte.

Les protocoles futurs doivent inclure, lorsque pertinent, des environnements stables et changeants et mesurer diversité des stratégies, délai d’abandon d’une ancienne stratégie, vitesse d’adaptation et regret induit par l’inertie.

**Priorité : HAUTE**

---

## GF-011 — Séparer construction, récupération et utilisation de la mémoire

Une mémoire ne doit jamais être considérée comme fonctionnelle à partir d’une seule métrique globale.

La chaîne doit être testée par étapes :

```text
preuves brutes
→ construction / consolidation
→ stockage
→ récupération
→ interprétation / intégration
→ décision
```

Pour chaque étape importante, SoiNesis doit pouvoir déterminer où une information a été perdue, déformée ou mal utilisée.

Règles associées :

- conserver un accès auditable aux preuves brutes lorsqu’une consolidation est importante ;
- préserver explicitement les relations causales et temporelles nécessaires à l’interprétation ;
- ne pas confondre bon rappel et bon raisonnement ;
- ne pas confondre structure de mémoire élégante et gain cognitif ;
- mesurer séparément perte à la construction, perte à la récupération et erreur d’utilisation.

**Priorité : CRITIQUE**

---

## GF-012 — Décomposer l’agence : objectif, plan, exécution et replanification

Une bonne performance au niveau d’un plan ou d’une intention ne démontre pas que l’agent sait l’exécuter.

Les futurs tests d’agence doivent, lorsque applicable, tracer séparément :

```text
objectif
→ plan
→ action concrète
→ observation du résultat
→ détection d’écart
→ replanification
```

Une seule métrique end-to-end ne doit pas masquer le niveau réellement défaillant.

Les mesures doivent permettre de distinguer au minimum :

- qualité du plan ;
- qualité de l’exécution locale ;
- grounding/perception de l’état ;
- capacité de récupération après erreur ;
- qualité de la replanification.

**Priorité : HAUTE**

---

# 4. Échecs et limites documentés

## EGF-001 — Eyla : croissance architecturale sans validation du mécanisme central

**Projet / étude :** *Eyla: Toward an Identity-Anchored LLM Architecture with Integrated Biological Priors — Vision, Implementation Attempt, and Lessons from AI-Assisted Development*  
**Auteur :** Arif Aditto  
**Date :** mars 2026  
**Source primaire :** https://arxiv.org/abs/2604.00009

### Limite

Architecture devenue très complexe, avec de nombreux sous-systèmes peu ou pas reliés au chemin fonctionnel réel, tests insuffisamment discriminants et résultat final proche du modèle de base.

### Pertinence SoiNesis

**OUI — exposition élevée.** Le projet est lui aussi développé avec assistance IA et peut confondre sophistication apparente et effet causal réel.

### Garde-fous

GF-001, GF-002, GF-003, ablations, tests end-to-end et refus des modules décoratifs.

**Priorité : CRITIQUE**

---

## EGF-002 — Auto-correction intrinsèque des LLM

**Étude :** *Large Language Models Cannot Self-Correct Reasoning Yet* — Jie Huang et al. (2023)  
**Source primaire :** https://arxiv.org/abs/2310.01798

### Limite

Sans feedback externe, demander à un LLM de corriger son propre raisonnement n’améliore pas nécessairement les réponses et peut les dégrader.

### Pertinence SoiNesis

La métacognition ne doit pas être assimilée à une simple auto-critique textuelle.

### Garde-fous

Comparer réflexion textuelle, signaux de performance observables et contrôles sans révision. Mesurer exactitude et calibration, pas qualité verbale.

**Priorité : HAUTE**

---

## EGF-003 — Empoisonnement dormant de mémoire persistante

**Étude :** *Hidden in Memory: Sleeper Memory Poisoning in LLM Agents* — Sidharth Pulipaka et al. (2026)  
**Source primaire :** https://arxiv.org/abs/2605.15338

### Limite

Une information externe manipulée peut devenir une mémoire persistante, rester dormante puis influencer ultérieurement des actions.

### Pertinence SoiNesis

**OUI — critique à long terme.**

### Garde-fous

GF-005, provenance, confiance, statut révisable, journalisation, quarantaine et tests adversariaux différés.

**Priorité : CRITIQUE**

---

## EGF-004 — AgentBench : faiblesse sur les longues trajectoires

**Étude :** *AgentBench: Evaluating LLMs as Agents* — Xiao Liu et al. (2023)  
**Source primaire :** https://arxiv.org/abs/2308.03688

### Limite

Raisonnement à long terme, prise de décision et respect des instructions restent des obstacles importants pour les agents interactifs.

### Garde-fous

GF-006, erreurs cumulatives, interruption/reprise et séparation mémoire/planification.

**Priorité : HAUTE**

---

## EGF-005 — MLAgentBench : l’agent expérimentateur reste faillible

**Étude :** *MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation* — Qian Huang et al. (2023)  
**Source primaire :** https://arxiv.org/abs/2310.03302

### Limite

Un agent peut produire une chaîne plausible hypothèse → code → expérience → analyse tout en laissant une erreur amont contaminer l’ensemble.

### Garde-fous

GF-003, GF-008, données brutes, critères préalables et revue adversariale séparée.

**Priorité : CRITIQUE**

---

## EGF-006 — HORIZON : dégradation avec l’allongement des trajectoires

**Étude :** *The Long-Horizon Task Mirage? Diagnosing Where and Why Agentic Systems Break* — Xinyu Jessica Wang et al. (2026)  
**Source primaire :** https://arxiv.org/abs/2604.11978

### Limite

Des dégradations apparaissent lorsque les tâches nécessitent des séquences longues et interdépendantes d’actions.

### Garde-fous

GF-006, checkpoints, métriques de dérive et tests H10/H100/H1000 lorsque le coût le permet.

**Priorité : HAUTE**

---

## EGF-007 — Comportement convaincant ≠ preuve phénoménale

**Étude :** *Consciousness in Artificial Intelligence: Insights from the Science of Consciousness* — Patrick Butlin et al. (2023)  
**Source primaire :** https://arxiv.org/abs/2308.08708

### Limite méthodologique

Les propriétés computationnelles doivent être examinées séparément du comportement verbal anthropomorphique.

### Garde-fous

GF-004, séparation Simulation / Conscience fonctionnelle / Conscience phénoménale, tests causaux et statut « inconnu » pour la conscience phénoménale.

**Priorité : CRITIQUE**

---

## EGF-008 — MIRROR : connaître ses limites ne suffit pas à agir en conséquence

**Étude :** *MIRROR: A Hierarchical Benchmark for Metacognitive Calibration in Large Language Models* — Jason Z Wang (2026)  
**Source primaire :** https://arxiv.org/abs/2604.19809

### Limite

Une connaissance partielle des forces et faiblesses ne se transforme pas automatiquement en décisions adaptées. L’étude met en évidence un écart entre monitoring métacognitif et contrôle de l’action.

### Pertinence SoiNesis

P3 et les futurs SelfModels peuvent être correctement calibrés sans produire de bénéfice décisionnel.

### Garde-fous

GF-009, métriques distinctes de calibration et de regret, ablation du chemin SelfModel → décision et futurs tests multi-domaines.

### Conséquence P3

P3 couvre déjà partiellement ce risque. Aucune modification rétroactive silencieuse de P3 n’est justifiée.

**Priorité : HAUTE**

---

## EGF-009 — LongDS-Bench : dégradation de l’état sur longue trajectoire

**Étude :** *LongDS-Bench: On the Failure of Long-Horizon Agentic Data Analysis* — Kewei Xu et al. (2026)  
**Source primaire :** https://arxiv.org/abs/2605.30434

### Limite

Le maintien d’un état correct se dégrade fortement avec la longueur de la trajectoire. Rollback, reprise et composition d’états sont des difficultés spécifiques.

### Garde-fous

GF-006, vieillissement artificiel, checkpoints et mesure de la pente de dégradation.

**Priorité : HAUTE**

---

## EGF-010 — La mémoire peut réduire l’exploration

**Étude :** *Demystify the Role of Memory in Machine Learning Engineering Agents* — Xinyu Zhao et al. (Findings of ACL 2026)  
**Source primaire :** https://aclanthology.org/2026.findings-acl.525/

### Limite

Une mémoire dynamique peut aider des agents séquentiels tout en réduisant la diversité de recherche et en favorisant une convergence prématurée dans des architectures d’exploration en arbre.

### Pertinence SoiNesis

La mémoire autobiographique et le SelfModel peuvent créer une inertie cognitive.

### Garde-fous

GF-010 et futur test d’inertie autobiographique : stratégie longtemps récompensée, changement non annoncé de l’environnement, mesure du délai d’abandon et du regret.

**Priorité : HAUTE**

---

## EGF-011 — AMA-Bench : la mémoire peut perdre causalité et information objective

**Étude :** *AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications*  
**Auteurs :** Yujie Zhao et al.  
**Date :** février 2026  
**Source primaire :** https://arxiv.org/abs/2602.22769

### Limite observée

AMA-Bench évalue la mémoire sur de vraies trajectoires agentiques et des trajectoires synthétiques extensibles à de longs horizons. Les auteurs constatent que les systèmes mémoire existants sous-performent principalement parce qu’ils manquent d’information causale et objective et parce que la récupération par similarité est intrinsèquement lossy.

Le système proposé par les auteurs ajoute notamment un graphe de causalité et une récupération outillée, ce qui améliore les résultats, mais ne supprime pas le problème général : **la construction et la récupération de mémoire peuvent perdre des dépendances indispensables**.

### Cause / interprétation

Une mémoire qui résume correctement la proximité sémantique peut échouer à conserver pourquoi un état existe, quelle action l’a causé, ou quelle dépendance temporelle relie deux événements.

### SoiNesis est-il exposé ?

**OUI — directement.**

La consolidation autobiographique, les révisions de croyances et le SelfModel dépendent précisément de relations causales et temporelles. Une compression qui conserve le contenu mais détruit ces liens pourrait produire un état cohérent en apparence mais causalement faux.

### Garde-fous associés

- GF-011 ;
- conserver les preuves brutes et leurs identifiants ;
- préserver les relations causales/temporaires nécessaires ;
- tester séparément construction et récupération ;
- ne pas dépendre uniquement d’une recherche par similarité pour les souvenirs critiques.

### Test futur à prévoir

Ablation en quatre étapes :

```text
preuves brutes
→ mémoire construite
→ récupération
→ décision
```

Mesurer à chaque transition : contenu perdu, relation causale perdue, provenance perdue et effet final sur la décision.

**Priorité : CRITIQUE**

---

## EGF-012 — Chain-of-Memory : bon rappel ≠ bonne utilisation du souvenir

**Étude :** *Chain-of-Memory: Lightweight Memory Construction with Dynamic Evolution for LLM Agents*  
**Auteurs :** Xiucheng Xu et al.  
**Date :** janvier 2026  
**Source primaire :** https://arxiv.org/abs/2601.14287

### Limite observée

Les auteurs identifient deux limites des approches mémoire courantes :

1. les constructions complexes peuvent coûter beaucoup pour des gains de performance marginaux ;
2. concaténer naïvement les souvenirs récupérés ne comble pas l’écart entre **retrieval recall** et **reasoning accuracy**.

### Cause / interprétation

Retrouver les bons fragments n’implique pas que l’agent sache les ordonner, les relier et les utiliser correctement pour inférer ou décider.

### SoiNesis est-il exposé ?

**OUI.**

P1/P2 et les futurs tests mémoire pourraient surévaluer un mécanisme si le rappel est excellent alors que l’intégration des souvenirs dans le raisonnement ou la décision est mauvaise.

### Garde-fous associés

- GF-011 ;
- quatre métriques séparées : conservation, récupération, interprétation/intégration, effet décisionnel ;
- mesurer le coût de construction d’une mémoire complexe ;
- comparer les architectures mémoire à une baseline simple recevant les mêmes informations.

### Test futur à prévoir

Construire des cas où tous les souvenirs nécessaires sont bien retrouvés mais doivent être reliés dans un ordre causal ou temporel précis pour obtenir la bonne décision.

**Priorité : HAUTE**

---

## EGF-013 — Web agents : un meilleur plan ne corrige pas une mauvaise exécution

**Étude :** *Why Do LLM-based Web Agents Fail? A Hierarchical Planning Perspective*  
**Auteurs :** Mohamed Aghzal, Gregory J. Stein, Ziyu Yao  
**Publication :** ACL 2026, long paper  
**Date :** juillet 2026  
**Source primaire :** https://aclanthology.org/2026.acl-long.1483/

### Limite observée

L’étude décompose les web agents en planification haut niveau, exécution bas niveau et replanification. Des plans structurés PDDL sont plus concis et orientés vers le but que les plans en langage naturel, mais **l’exécution bas niveau reste le principal goulot d’étranglement**.

### Cause / interprétation

Améliorer le raisonnement ou le plan global ne résout pas automatiquement les problèmes de grounding, de contrôle local et de récupération après erreur.

### SoiNesis est-il exposé ?

**OUI — pour les futurs objectifs, plans et actions incarnées.**

Un objectif persistant ou un plan cohérent pourrait être déclaré fonctionnel alors que la chaîne plan → action échoue.

### Garde-fous associés

- GF-012 ;
- ne pas utiliser uniquement le succès final comme diagnostic ;
- tracer chaque transition objectif → plan → action → observation → replanification ;
- ablater séparément planification, exécution et replanification lorsque possible.

### Test futur à prévoir

Créer des tâches où le même plan haut niveau est exécuté avec différents niveaux de difficulté perceptive ou motrice, puis mesurer séparément qualité du plan, erreurs locales, récupération et résultat final.

**Priorité : HAUTE**

---

# 5. Matrice de risque actuelle

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
| SelfModel calibré mais mal utilisé pour agir | Oui | HAUTE | GF-009 |
| Mémoire créant rigidité ou sous-exploration | Oui, future | HAUTE | GF-010 |
| Perte de causalité lors de consolidation/récupération | Oui | CRITIQUE | GF-011 |
| Bon rappel mais mauvaise utilisation du souvenir | Oui | HAUTE | GF-011 |
| Plan correct mais exécution défaillante | Oui, future | HAUTE | GF-012 |
| Modules présents mais non causaux | Oui | CRITIQUE | GF-001 + ablation |
| Hallucination dans l’expérimentation assistée par IA | Oui | CRITIQUE | GF-003 + GF-008 |

---

# 6. Relation avec les documents existants

Ce registre complète notamment :

- `docs/02-hypotheses.md` : hypothèses, variables, réfutation et ablations ;
- `docs/etat-de-l-art.md` : travaux existants et positionnement scientifique ;
- `docs/regles-contribution-scientifique.md` : niveaux de contribution et règles de nouveauté ;
- `docs/05-cycle-cognitif.md` : cycle causal et contrôle du rôle du LLM ;
- `docs/06-memoire-autobiographique.md` : provenance, consolidation, récupération et futurs tests d’inertie ;
- `docs/07-modele-de-soi.md` : SelfModel causal et versionné ;
- `docs/08-journal-evolution.md` : traçabilité ;
- `docs/09-securite-et-permissions.md` : contrôle des actions et de la persistance ;
- `docs/18-protocole-exp-001-p3.md` : séparation entre estimation des capacités, SelfModel et décision ;
- `docs/protocole-preenregistrement.md` : gel des critères ;
- `docs/politique-reproductibilite.md` : réplications et manifestes ;
- `docs/protocole-evaluation-independante.md` : séparation des rôles d’évaluation.

Le présent document ne remplace aucun de ces documents. Il traduit les erreurs observées ailleurs en contraintes de conception et de test pour SoiNesis.

---

# 7. Procédure pour ajouter un nouvel échec

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

# 8. Règle de maintenance

Lorsqu’une nouvelle publication, un post-mortem ou une réplication révèle une défaillance pertinente :

1. ajouter l’entrée ;
2. vérifier si SoiNesis est exposé ;
3. chercher si un garde-fou existe déjà ;
4. créer le garde-fou manquant uniquement s’il est justifié ;
5. définir un test ;
6. ne considérer le risque comme couvert qu’après validation du test correspondant.

Un garde-fou inutilement complexe ne doit pas être ajouté uniquement parce qu’un autre projet a échoué : la pertinence pour SoiNesis doit être explicitement démontrée.

---

# 9. Position actuelle

Le registre ne prétend pas être exhaustif.

Il couvre actuellement en priorité :

- développement d’architecture avec assistance IA ;
- validation causale ;
- qualité réelle des tests ;
- métacognition et contrôle de l’action ;
- mémoire persistante, provenance, causalité et récupération ;
- effets bénéfiques comme négatifs de la mémoire ;
- trajectoires longues et maintien d’état ;
- objectifs, planification, exécution et replanification ;
- expérimentation scientifique automatisée ;
- interprétation de la conscience.

La règle générale reste : **apprendre des échecs documentés avant d’avoir à les reproduire nous-mêmes.**