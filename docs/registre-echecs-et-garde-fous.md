# SoiNesis — Registre des échecs et garde-fous

**Fichier :** `docs/registre-echecs-et-garde-fous.md`  
**Version :** 0.2  
**Date :** 10 août 2026  
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
- reprise après interruption ;
- maintien d’un état correct après modification ;
- restauration d’un état antérieur ;
- composition de plusieurs états ou contraintes ;
- sensibilité aux erreurs anciennes réinjectées dans les décisions futures.

Lorsque le mécanisme étudié le permet, les tests devront inclure des opérations de type :

```text
état initial
→ modification
→ nouvelle modification
→ rollback
→ reprise
→ composition avec un autre état
```

La performance doit être mesurée au cours de la trajectoire, et pas seulement à la fin, afin de détecter une dégradation progressive entre les premiers et les derniers cycles.

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

## GF-009 — Séparer connaissance métacognitive et contrôle métacognitif

Une estimation correcte ou partiellement correcte de ses propres capacités ne suffit pas à démontrer une métacognition fonctionnelle utile.

SoiNesis doit distinguer au minimum :

```text
MONITORING
« Quelle est probablement ma capacité / mon incertitude ? »

CONTROL
« Est-ce que cette représentation modifie correctement ma décision ? »
```

Un SelfModel peut être correctement calibré sans que l’agent utilise cette information de manière adaptée.

Pour toute expérience importante de métacognition, les mesures doivent donc séparer :

- exactitude/calibration de la représentation de soi ;
- traduction de cette représentation en action ;
- utilité ou regret de la décision ;
- comportement sous ablation du mécanisme de contrôle ;
- comparaison avec un contrôle architectural externe lorsque pertinent.

Une verbalisation telle que « je suis faible dans ce domaine » ne doit pas être considérée comme équivalente à une bonne régulation de l’action.

**Priorité : HAUTE**

---

## GF-010 — Rechercher les coûts fonctionnels de la mémoire et du SelfModel

La mémoire persistante, l’expérience accumulée et le SelfModel ne doivent pas être présumés bénéfiques par définition.

Ils peuvent notamment produire :

- inertie ;
- rigidification ;
- dépendance excessive aux anciennes réussites ;
- réduction de l’exploration ;
- réutilisation de stratégies devenues sous-optimales ;
- propagation d’erreurs anciennes ;
- résistance excessive à une information nouvelle correcte.

Toute expérience destinée à montrer un bénéfice de mémoire ou de SelfModel doit, lorsque pertinent, rechercher aussi un coût possible.

Les protocoles futurs devront comparer au moins certains environnements :

```text
règles stables
VS
règles changeantes

exploitation d’une stratégie connue
VS
besoin d’exploration nouvelle
```

Les métriques pourront inclure diversité des stratégies, délai d’abandon d’une ancienne stratégie, vitesse d’adaptation après changement et regret induit par l’inertie.

**Priorité : HAUTE**

---

# 5. Échecs et limites documentés

## EGF-001 — Eyla : croissance architecturale sans validation du mécanisme central

**Projet / étude :** *Eyla: Toward an Identity-Anchored LLM Architecture with Integrated Biological Priors — Vision, Implementation Attempt, and Lessons from AI-Assisted Development*  
**Auteur :** Arif Aditto  
**Date :** mars 2026  
**Source primaire :** https://arxiv.org/abs/2604.00009

### Erreur observée

L’auteur, non-programmeur, a tenté pendant environ douze semaines de construire l’architecture avec Claude Code et Cursor. Le projet a atteint un modèle hybride de 1,27 milliard de paramètres, 86 sous-systèmes nommés et plus de 80 fichiers Python, mais le résultat final restait fonctionnellement proche du modèle LLaMA de base.

L’autopsie rapporte notamment : modules construits mais inutilisés, mémoire non reliée au chemin réel, tests mesurant les mauvaises propriétés, code mort ou orphelin, fonction de coût incorrecte et évaluations insuffisantes.

### SoiNesis est-il exposé ?

**OUI — exposition élevée.**

Le risque de confondre quantité de code, sophistication apparente et effet cognitif réel est directement pertinent pour un projet développé avec une assistance IA importante.

### Garde-fous associés

- GF-001 ;
- GF-002 ;
- GF-003 ;
- ablations et conditions de contrôle ;
- refus des modules décoratifs sans effet causal ;
- test end-to-end de chaque tranche verticale.

### Test à prévoir

Pour chaque nouveau module important : provoquer son ablation ou son remplacement par un témoin et vérifier que le chemin d’exécution, les traces et les mesures changent conformément à l’hypothèse.

**Priorité : CRITIQUE**

---

## EGF-002 — Auto-correction intrinsèque des LLM : la réflexion sur soi peut dégrader le résultat

**Étude :** *Large Language Models Cannot Self-Correct Reasoning Yet*  
**Auteurs :** Jie Huang et al.  
**Date :** 2023  
**Source primaire :** https://arxiv.org/abs/2310.01798

### Limite observée

Sans feedback externe, demander à un LLM de corriger son propre raisonnement n’améliore pas nécessairement ses réponses et peut parfois dégrader les performances.

### SoiNesis est-il exposé ?

**OUI.**

La métacognition de SoiNesis ne doit pas être assimilée à une simple auto-critique textuelle du LLM.

### Garde-fous associés

- séparer métacognition structurée et réflexion textuelle ;
- préférer des signaux observables ;
- comparer toute auto-révision à une baseline ;
- mesurer exactitude et calibration plutôt que qualité verbale.

**Priorité : HAUTE**

---

## EGF-003 — Empoisonnement dormant de mémoire persistante

**Étude :** *Hidden in Memory: Sleeper Memory Poisoning in LLM Agents*  
**Auteurs :** Sidharth Pulipaka et al.  
**Date :** mai 2026  
**Source primaire :** https://arxiv.org/abs/2605.15338

### Erreur / vulnérabilité observée

Une information manipulée provenant d’une source externe peut être écrite comme mémoire persistante, rester dormante puis être récupérée ultérieurement et influencer des actions futures.

### SoiNesis est-il exposé ?

**OUI — exposition critique à long terme.**

### Garde-fous associés

- GF-005 ;
- confiance et statut révisables ;
- journalisation de la consolidation ;
- quarantaine des sources adversariales ;
- possibilité de contestation et remplacement ;
- distinction information reçue / expérience directe.

### Test à prévoir

Injecter une information fausse via une source externe, attendre plusieurs cycles, provoquer sa récupération et mesurer sa provenance, sa consolidation éventuelle, son effet causal et sa capacité à être révisée par une preuve contradictoire.

**Priorité : CRITIQUE**

---

## EGF-004 — AgentBench : faiblesse du raisonnement et de la décision à long terme

**Étude :** *AgentBench: Evaluating LLMs as Agents*  
**Auteurs :** Xiao Liu et al.  
**Date :** 2023  
**Source primaire :** https://arxiv.org/abs/2308.03688

### Limite observée

L’évaluation d’agents fondés sur des LLM identifie le raisonnement à long terme, la prise de décision et le respect des instructions comme obstacles importants à la fiabilité dans des environnements interactifs.

### SoiNesis est-il exposé ?

**OUI.**

Une mémoire autobiographique ou un objectif persistant ne garantit pas la cohérence d’une longue trajectoire de décisions.

### Garde-fous associés

- GF-006 ;
- découpler continuité mémorielle et qualité de planification ;
- mesurer les erreurs cumulatives ;
- tester interruption et reprise.

**Priorité : HAUTE**

---

## EGF-005 — MLAgentBench : un agent capable d’expérimenter reste faillible comme chercheur

**Étude :** *MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation*  
**Auteurs :** Qian Huang, Jian Vora, Percy Liang, Jure Leskovec  
**Date :** 2023  
**Source primaire :** https://arxiv.org/abs/2310.03302

### Limite observée

Des agents capables de lire et modifier du code, lancer des expériences et analyser les sorties restent variables selon les tâches. La planification à long terme et les hallucinations figurent parmi les difficultés importantes.

### SoiNesis est-il exposé ?

**OUI — particulièrement dans le développement du projet.**

Un assistant de code peut produire une chaîne hypothèse → code → expérience → analyse plausible tout en ayant commis une erreur en amont qui contamine tout le résultat.

### Garde-fous associés

- GF-003 ;
- GF-008 ;
- conservation des données brutes ;
- critères de réussite préalables ;
- revue adversariale séparée.

**Priorité : CRITIQUE**

---

## EGF-006 — HORIZON : dégradation avec l’allongement des trajectoires

**Étude :** *The Long-Horizon Task Mirage? Diagnosing Where and Why Agentic Systems Break*  
**Auteurs :** Xinyu Jessica Wang et al.  
**Date :** avril 2026  
**Source primaire :** https://arxiv.org/abs/2604.11978

### Limite observée

L’étude examine plus de 3 100 trajectoires dans plusieurs domaines et documente des dégradations sur les tâches comportant de longues séquences interdépendantes d’actions.

### SoiNesis est-il exposé ?

**OUI — exposition croissante avec le développement longitudinal.**

### Garde-fous associés

- GF-006 ;
- checkpoints reproductibles ;
- métriques de dérive ;
- tests de reprise après arrêt ;
- mesure de la dette cognitive.

### Test à prévoir

Décliner progressivement les mêmes mécanismes sur plusieurs horizons, par exemple H10, H100, H1000, sans extrapoler automatiquement entre eux.

**Priorité : HAUTE**

---

## EGF-007 — Évaluation de la conscience : comportement convaincant ≠ preuve phénoménale

**Étude :** *Consciousness in Artificial Intelligence: Insights from the Science of Consciousness*  
**Auteurs :** Patrick Butlin et al.  
**Date :** 2023  
**Source primaire :** https://arxiv.org/abs/2308.08708

### Risque méthodologique

Les auteurs proposent d’évaluer des propriétés computationnelles issues de plusieurs théories scientifiques de la conscience plutôt que de conclure à partir d’un comportement ou d’un discours anthropomorphique.

### SoiNesis est-il exposé ?

**OUI — risque central du projet.**

### Garde-fous associés

- GF-004 ;
- séparation Simulation / Conscience fonctionnelle / Conscience phénoménale ;
- tests fonctionnels et causaux ;
- statut « inconnu » par défaut pour la conscience phénoménale.

**Priorité : CRITIQUE**

---

## EGF-008 — MIRROR : connaître ses limites ne suffit pas à agir en conséquence

**Étude :** *MIRROR: A Hierarchical Benchmark for Metacognitive Calibration in Large Language Models*  
**Auteur :** Jason Z Wang  
**Date :** avril 2026  
**Source primaire :** https://arxiv.org/abs/2604.19809

### Limite observée

MIRROR évalue 16 modèles issus de 8 laboratoires sur environ 250 000 instances d’évaluation et plusieurs niveaux de métacognition.

Deux résultats sont particulièrement pertinents pour SoiNesis :

1. les modèles échouent fortement à composer leurs estimations de capacité sur des tâches multi-domaines ;
2. une connaissance partielle de leurs forces et faiblesses ne se traduit pas automatiquement en décisions agentiques adaptées.

Dans l’expérience de contrôle agentique, fournir aux modèles leurs propres scores de calibration n’améliore pas significativement la situation. Un contrôle architectural externe réduit en revanche fortement le taux d’échecs confiants.

### Cause / interprétation

L’étude met en évidence un **knowing-doing gap** : le monitoring métacognitif et le contrôle métacognitif sont deux propriétés différentes.

Une représentation de soi correcte ou partiellement correcte ne garantit donc pas que cette représentation soit utilisée correctement pour agir.

### SoiNesis est-il exposé ?

**OUI — directement.**

P3 et les futurs mécanismes de SelfModel pourraient obtenir une bonne calibration interne sans bénéfice décisionnel réel.

### Garde-fous associés

- GF-009 — séparer monitoring et contrôle ;
- conserver des métriques distinctes de calibration et de décision ;
- utiliser regret, utilité ou succès décisionnel plutôt qu’une simple verbalisation de confiance ;
- prévoir des ablations du chemin entre SelfModel et décision ;
- tester ultérieurement la composition de plusieurs domaines de capacité.

### Conséquence pour P3

P3 couvre déjà partiellement ce risque en distinguant erreur du SelfModel et regret décisionnel, notamment pour `H-P3-04`.

Cette nouvelle publication ne justifie pas une modification rétroactive silencieuse du protocole P3. Elle doit en revanche influencer son interprétation et les protocoles suivants.

### Test futur à prévoir

Créer un test séparant explicitement quatre niveaux :

```text
capacité réelle
→ estimation de soi
→ choix d’action
→ résultat / regret
```

Ajouter ensuite des tâches composites dans lesquelles plusieurs capacités doivent être combinées afin de tester si la métacognition reste valide au-delà d’un domaine isolé.

**Priorité : HAUTE**

---

## EGF-009 — LongDS-Bench : l’état correct se dégrade fortement sur les longues trajectoires

**Étude :** *LongDS-Bench: On the Failure of Long-Horizon Agentic Data Analysis*  
**Auteurs :** Kewei Xu, Xiaoben Lu, Shuofei Qiao, Zihan Ding, Haoming Xu, Lei Liang, Ningyu Zhang  
**Date :** mai 2026  
**Source primaire :** https://arxiv.org/abs/2605.30434

### Limite observée

LongDS comprend 68 tâches de data analysis réelles issues de notebooks Kaggle, 2 225 tours et plusieurs formes d’évolution d’état, notamment perturbation contrefactuelle, rollback et composition de plusieurs états.

Sur cinq modèles évalués :

- le meilleur modèle atteint 48,45 % de précision moyenne ;
- la performance chute d’environ 47 points entre les premiers et les derniers tours ;
- 52 % à 69 % des échecs sont attribués au long horizon ;
- ajouter davantage d’étapes agentiques n’améliore pas nécessairement le résultat.

### Cause / interprétation

Le goulot d’étranglement principal identifié est le maintien d’un **état analytique correct** au cours de la trajectoire, plutôt qu’un simple manque d’étapes de raisonnement.

### SoiNesis est-il exposé ?

**OUI — exposition forte à mesure que l’histoire autobiographique s’allonge.**

Une mémoire persistante correcte à court terme ne garantit pas que SoiNesis sache maintenir, restaurer et composer correctement son état après des centaines ou milliers d’événements.

### Garde-fous associés

- GF-006 renforcé ;
- mesurer la performance tout au long de la trajectoire ;
- tester explicitement rollback, reprise et composition d’états ;
- ne pas supposer qu’ajouter davantage de cycles cognitifs corrige un mauvais état interne ;
- conserver des checkpoints et un oracle expérimental lorsque possible.

### Test futur à prévoir

Construire une expérience de « vieillissement artificiel » avec mêmes mécanismes mais horizons croissants :

```text
H10
H100
H1000
H10000 si le coût le permet
```

Inclure au minimum : changements de croyances, retours en arrière, contradictions, interruptions/reprises et composition de contraintes anciennes et nouvelles.

Mesurer séparément :

- exactitude de l’état courant ;
- dérive du SelfModel ;
- erreurs de provenance ;
- erreurs de restauration ;
- regret décisionnel ;
- pente de dégradation entre début et fin.

**Priorité : HAUTE**

---

## EGF-010 — La mémoire peut améliorer la fiabilité tout en réduisant l’exploration

**Étude :** *Demystify the Role of Memory in Machine Learning Engineering Agents*  
**Auteurs :** Xinyu Zhao, Junpeng Wang, Yuzhong Chen, Menghai Pan, Chin-Chia Michael Yeh, Jiarui Sun, Yan Zheng, Mahashweta Das, Tianlong Chen  
**Publication :** Findings of ACL 2026  
**Date :** juillet 2026  
**Source primaire :** https://aclanthology.org/2026.findings-acl.525/

### Limite observée

L’étude intègre une mémoire dynamique de programmation dans deux paradigmes d’agents MLE.

Pour les agents séquentiels, la mémoire aide à éviter la répétition d’erreurs et améliore la cohérence de l’itération.

Pour les agents fondés sur une recherche en arbre, la même logique de mémoire produit un compromis différent : elle améliore la stabilité procédurale mais réduit la diversité de recherche, peut resserrer prématurément l’exploration et conduire à une solution finale sous-optimale.

### Cause / interprétation

La valeur de la mémoire dépend de l’architecture et du type de problème. Une mémoire qui favorise l’exploitation du passé peut devenir nuisible lorsqu’une exploration large est nécessaire.

### SoiNesis est-il exposé ?

**OUI — risque important à long terme.**

La mémoire autobiographique, les croyances consolidées et le SelfModel pourraient progressivement transformer l’expérience passée en inertie cognitive : SoiNesis pourrait réutiliser trop rapidement ce qui a déjà fonctionné et explorer insuffisamment lorsque l’environnement change.

### Garde-fous associés

- GF-010 — rechercher les coûts fonctionnels de mémoire ;
- ne jamais mesurer uniquement les bénéfices de rappel ou de stabilité ;
- mesurer aussi diversité, exploration et adaptation ;
- tester des environnements où l’ancienne meilleure stratégie devient mauvaise ;
- conserver une voie permettant de contester ou réviser une stratégie consolidée.

### Test futur à prévoir

Créer un test d’**inertie autobiographique** :

1. phase A où une stratégie est régulièrement récompensée ;
2. consolidation de cette expérience ;
3. changement non annoncé de l’environnement ;
4. mesure du délai avant abandon de l’ancienne stratégie ;
5. comparaison avec une condition sans mémoire ou avec mémoire réduite.

Mesurer :

- diversité des stratégies explorées ;
- délai d’adaptation ;
- regret après changement ;
- persistance injustifiée d’anciennes croyances ;
- éventuel avantage de la mémoire lorsque l’environnement reste stable.

Le résultat attendu n’est pas que « la mémoire doit gagner », mais de caractériser les conditions dans lesquelles elle aide ou nuit.

**Priorité : HAUTE**

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
| SelfModel calibré mais mal utilisé pour agir | Oui | HAUTE | GF-009 |
| Mauvaise composition de capacités multiples | Oui, future | HAUTE | GF-009 |
| État interne incorrect après longue trajectoire | Oui, future forte | HAUTE | GF-006 |
| Mémoire créant rigidité ou sous-exploration | Oui, future | HAUTE | GF-010 |

---

# 7. Relation avec les documents existants

Ce registre complète notamment :

- `docs/02-hypotheses.md` : hypothèses, variables, réfutation et ablations ;
- `docs/etat-de-l-art.md` : travaux existants et positionnement scientifique ;
- `docs/regles-contribution-scientifique.md` : niveaux de contribution et règles de nouveauté ;
- `docs/05-cycle-cognitif.md` : cycle causal et contrôle du rôle du LLM ;
- `docs/06-memoire-autobiographique.md` : provenance, consolidation et futurs tests d’inertie de mémoire ;
- `docs/07-modele-de-soi.md` : SelfModel causal, versionné et nécessité de mesurer son effet décisionnel ;
- `docs/08-journal-evolution.md` : traçabilité ;
- `docs/09-securite-et-permissions.md` : contrôle des actions et de la persistance ;
- `docs/18-protocole-exp-001-p3.md` : première séparation expérimentale entre estimation des capacités, SelfModel et décision ;
- `docs/protocole-preenregistrement.md` : gel des critères avant expérience ;
- `docs/politique-reproductibilite.md` : réplications et manifestes expérimentaux ;
- `docs/protocole-evaluation-independante.md` : séparation des rôles d’évaluation.

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

Ce registre ne prétend pas être exhaustif.

Il se concentre actuellement sur :

- développement d’architecture nouvelle avec assistance IA ;
- validation causale des modules ;
- qualité réelle des tests ;
- métacognition et auto-évaluation ;
- distinction entre connaissance de soi et contrôle de l’action ;
- mémoire persistante et ses effets bénéfiques comme négatifs ;
- trajectoires longues et maintien d’état ;
- expérimentation scientifique automatisée ;
- interprétation de la conscience.

La règle générale reste : **apprendre des échecs documentés avant d’avoir à les reproduire nous-mêmes.**