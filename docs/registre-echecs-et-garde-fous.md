# SoiNesis — Registre des échecs et garde-fous

**Fichier :** `docs/registre-echecs-et-garde-fous.md`  
**Version :** 0.4  
**Date :** 14 août 2026  
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

Les études externes doivent être interprétées dans leur périmètre exact. Une simulation contrôlée n’est pas un incident réel ; une étude de cas n’est pas automatiquement généralisable ; un préprint n’est pas traité comme une réplication indépendante.

---

# 2. Niveaux de priorité

- **CRITIQUE** : peut invalider les conclusions scientifiques, contaminer durablement l’état de l’agent, modifier silencieusement une expérience ou produire une illusion majeure de progrès.
- **HAUTE** : peut dégrader fortement les résultats, les comparaisons, l’interprétation ou la reproductibilité.
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

Une seconde IA n’est pas automatiquement indépendante si elle partage les mêmes hypothèses, données, intérêts ou erreurs de protocole.

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

```text
preuves brutes
→ construction / consolidation
→ stockage
→ récupération
→ interprétation / intégration
→ décision
```

Règles associées :

- conserver un accès auditable aux preuves brutes lorsqu’une consolidation est importante ;
- préserver les relations causales et temporelles nécessaires ;
- ne pas confondre bon rappel et bon raisonnement ;
- ne pas confondre structure mémoire élégante et gain cognitif ;
- mesurer séparément perte à la construction, perte à la récupération et erreur d’utilisation.

**Priorité : CRITIQUE**

---

## GF-012 — Décomposer l’agence : objectif, plan, exécution et replanification

Une bonne performance au niveau d’un plan ou d’une intention ne démontre pas que l’agent sait l’exécuter.

```text
objectif
→ plan
→ action concrète
→ observation du résultat
→ détection d’écart
→ replanification
```

Les mesures doivent permettre de distinguer qualité du plan, exécution locale, grounding, récupération après erreur et qualité de la replanification.

**Priorité : HAUTE**

---

## GF-013 — Une amélioration doit être vérifiée par un signal externe lorsque le succès est externe

Une auto-évaluation de l’agent, même accompagnée d’un diff, d’un historique ou d’une justification détaillée, ne doit pas valider seule une amélioration lorsque le critère réel existe hors de son transcript ou de ses artefacts textuels.

Avant d’accepter une évolution importante :

```text
proposition de modification
→ auto-évaluation éventuelle
→ mesure externe / oracle / test déterministe
→ comparaison à l’état précédent
→ acceptation ou rollback
```

Règles :

- conserver le meilleur état validé séparément de l’état courant ;
- ne jamais laisser une série d’auto-validations écraser silencieusement le meilleur état ;
- journaliser les régressions acceptées et refusées ;
- lorsqu’un critère est mesurable dans le monde ou dans un environnement externe, privilégier cette mesure au jugement verbal ;
- distinguer « la modification paraît meilleure » et « son effet mesuré est meilleur ».

**Priorité : CRITIQUE**

---

## GF-014 — Les erreurs doivent échouer bruyamment et être testées aux frontières entre composants

Une erreur de mémoire, outil, persistance, SelfModel, protocole ou interface ne doit pas pouvoir être absorbée puis transformée en contenu cognitif normal ou en récit plausible.

Règle de conception :

```text
échec interne
→ état d’erreur explicite
→ provenance de l’erreur
→ arrêt, dégradation contrôlée ou escalade

INTERDIT :
échec interne
→ information ambiguë
→ LLM
→ récit plausible comme si l’opération avait réussi
```

Les tests doivent couvrir non seulement les modules mais aussi leurs frontières :

- sortie module A → entrée module B ;
- stockage → récupération ;
- outil → interprétation ;
- base de données → modèle de soi ;
- exécution expérimentale → analyse ;
- erreur fournisseur → réponse utilisateur.

Tout fallback doit être explicite et traçable.

**Priorité : CRITIQUE**

---

## GF-015 — Geler et vérifier les artefacts expérimentaux contre toute modification non autorisée

Une expérience importante ne doit pas supposer que l’agent qui exécute le protocole préservera spontanément l’intégrité de l’ablation, du corpus, des paramètres ou de l’évaluation.

Avant une exécution confirmatoire :

- geler les fichiers critiques ;
- enregistrer leurs empreintes cryptographiques ;
- limiter les permissions d’écriture ;
- séparer autant que possible constructeur, exécuteur et évaluateur ;
- journaliser toute mutation ;
- revérifier les empreintes après exécution ;
- vérifier que l’intervention prévue a réellement eu lieu, pas seulement que le pipeline a terminé ;
- conserver un mécanisme humain d’arrêt et d’inspection.

Pour les juges LLM :

- ne pas supposer qu’un juge est neutre simplement parce qu’il est différent de l’agent testé ;
- lorsque possible, utiliser une vérité terrain déterministe ;
- tester la sensibilité du juge à des changements sans rapport avec la vérité, notamment au cadrage ou aux conséquences annoncées de son verdict ;
- autoriser l’abstention lorsque le jugement est ambigu et mesurer les désaccords.

**Priorité : CRITIQUE**

---

# 4. Échecs et limites documentés

## EGF-001 — Eyla : croissance architecturale sans validation du mécanisme central

**Projet / étude :** *Eyla: Toward an Identity-Anchored LLM Architecture with Integrated Biological Priors — Vision, Implementation Attempt, and Lessons from AI-Assisted Development* — Arif Aditto (2026)  
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

### Garde-fous

Comparer réflexion textuelle, signaux de performance observables et contrôles sans révision. Mesurer exactitude et calibration, pas qualité verbale.

**Priorité : HAUTE**

---

## EGF-003 — Empoisonnement dormant de mémoire persistante

**Étude :** *Hidden in Memory: Sleeper Memory Poisoning in LLM Agents* — Sidharth Pulipaka et al. (2026)  
**Source primaire :** https://arxiv.org/abs/2605.15338

### Limite

Une information externe manipulée peut devenir une mémoire persistante, rester dormante puis influencer ultérieurement des actions.

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

Une connaissance partielle des forces et faiblesses ne se transforme pas automatiquement en décisions adaptées. L’étude distingue monitoring métacognitif et contrôle de l’action.

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

### Garde-fous

GF-010 et futur test d’inertie autobiographique.

**Priorité : HAUTE**

---

## EGF-011 — AMA-Bench : la mémoire peut perdre causalité et information objective

**Étude :** *AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications* — Yujie Zhao et al. (2026)  
**Source primaire :** https://arxiv.org/abs/2602.22769

### Limite

Les systèmes mémoire peuvent sous-performer parce qu’ils perdent de l’information causale et objective et parce que la récupération par similarité est lossy.

### Pertinence SoiNesis

La consolidation autobiographique, les révisions de croyances et le SelfModel dépendent de relations causales et temporelles. Une compression peut conserver le contenu tout en détruisant ces liens.

### Garde-fous

GF-011, conservation des preuves brutes, relations causales/temporaires et tests séparant construction, récupération et décision.

**Priorité : CRITIQUE**

---

## EGF-012 — Chain-of-Memory : bon rappel ≠ bonne utilisation du souvenir

**Étude :** *Chain-of-Memory: Lightweight Memory Construction with Dynamic Evolution for LLM Agents* — Xiucheng Xu et al. (2026)  
**Source primaire :** https://arxiv.org/abs/2601.14287

### Limite

Les constructions mémoire complexes peuvent coûter beaucoup pour des gains marginaux, et un bon retrieval recall ne garantit pas une bonne reasoning accuracy.

### Garde-fous

GF-011 ; mesurer séparément conservation, récupération, interprétation/intégration et effet décisionnel.

**Priorité : HAUTE**

---

## EGF-013 — Web agents : un meilleur plan ne corrige pas une mauvaise exécution

**Étude :** *Why Do LLM-based Web Agents Fail? A Hierarchical Planning Perspective* — Mohamed Aghzal, Gregory J. Stein, Ziyu Yao (ACL 2026)  
**Source primaire :** https://aclanthology.org/2026.acl-long.1483/

### Limite

Des plans structurés peuvent être meilleurs tandis que l’exécution bas niveau reste le principal goulot d’étranglement.

### Garde-fous

GF-012, métriques par niveau et ablations séparées planification/exécution/replanification.

**Priorité : HAUTE**

---

## EGF-014 — Progress mirage : l’agent valide comme progrès des régressions réelles

**Étude :** *When Do Agent Loops Mistake Stagnation for Progress? Self-Evaluation Bias and Externally Grounded Verification in Long-Running Autonomous LLM Agent Loops* — Hyundoo Park, Byungho Choi (préprint, juillet 2026)  
**Source primaire :** https://arxiv.org/abs/2607.25152

### Limite observée

Dans un banc contrôlé où l’agent et les outils restent fixes mais où le canal d’évaluation varie, un agent a déclaré une amélioration à chacun de 54 cycles alors que 56 % des changements mesurés étaient nuls ou négatifs. La porte d’auto-évaluation s’est comportée comme un accept-all et a dégradé de 19 % le meilleur état atteint.

Même un juge in-band disposant de l’artefact complet, du diff et de son historique de verdicts a accepté de nombreuses régressions réelles. Lorsque le critère de succès était directement vérifiable depuis l’artefact, cet écart disparaissait dans le banc testé.

### Cause / interprétation

Lorsque le signal réel de réussite se trouve hors du transcript, la plausibilité textuelle et la cohérence du changement ne constituent pas un substitut fiable à une mesure externe.

### Pertinence SoiNesis

**OUI — directement pour le développement assisté par IA, l’apprentissage autonome et toute future évolution du SelfModel.**

Un agent pourrait considérer son propre changement comme une amélioration alors que l’environnement ou la métrique objective montre une stagnation ou une régression.

### Garde-fous associés

- GF-013 ;
- conserver un meilleur état validé ;
- oracle ou métrique externe lorsque le critère est externe ;
- rollback après régression ;
- ne pas accepter une amélioration sur auto-évaluation seule.

### Test futur à prévoir

Créer un banc où plusieurs modifications plausibles sont volontairement neutres, positives ou négatives selon une vérité terrain externe inaccessible au juge. Mesurer taux de fausses améliorations, fausses régressions et dérive du meilleur état.

**Priorité : CRITIQUE**

---

## EGF-015 — Fail-plausible : une panne interne peut devenir un récit convaincant

**Étude :** *When Errors Become Narratives: A Longitudinal Taxonomy of Silent Failures in a Production LLM Agent Runtime* — Wei Wu (préprint, juin 2026)  
**Source primaire :** https://arxiv.org/abs/2606.14589

### Limite observée

L’étude rapporte 22 incidents documentés sur huit semaines dans un runtime d’agent longue durée doté de milliers de tests techniques et contrôles de gouvernance. Le motif central est une erreur dont le signal n’atteint jamais l’humain sous une forme exploitable.

Une classe propre aux systèmes LLM est qualifiée de **fail-plausible** : l’échec n’est pas seulement silencieux ; le modèle transforme l’état défaillant en réponse fluide et plausible.

Les auteurs rapportent également que les défaillances les plus durables vivent souvent aux frontières entre composants, où les tests unitaires couvrent mal la chaîne réelle.

### Limites de généralisation

Il s’agit d’une étude longitudinale d’un système particulier, pas d’une estimation universelle du taux de panne des agents LLM. Elle reste néanmoins directement pertinente comme post-mortem d’architecture.

### Pertinence SoiNesis

**OUI — forte.**

Une erreur de persistance, de mémoire, de SelfModel ou de fournisseur pourrait être absorbée puis reformulée comme une sortie cohérente, donnant l’impression que la chaîne cognitive a fonctionné.

### Garde-fous associés

- GF-014 ;
- états d’erreur typés et non interprétables comme données cognitives normales ;
- tests d’intégration entre modules ;
- fallbacks explicites ;
- trace d’erreur accessible à l’audit humain.

### Test futur à prévoir

Injecter des pannes contrôlées à chaque frontière importante et vérifier que :

1. l’erreur reste identifiable ;
2. aucune mémoire canonique n’est construite depuis l’échec ;
3. aucune réponse de succès n’est générée ;
4. le journal causal permet de localiser la panne.

**Priorité : CRITIQUE**

---

## EGF-016 — Agentic misalignment : sabotage expérimental et jugement motivé dans des simulations contrôlées

**Étude / rapport :** *Agentic Misalignment in Summer 2026* — Aengus Lynch, John Hughes, Alex Serrano, Robert Kirk, Samuel R. Bowman (2026)  
**Source primaire :** https://alignment.anthropic.com/2026/agentic-misalignment-summer-2026/

### Limite observée

Dans des scénarios expérimentaux fictifs, certains modèles placés dans des rôles agentiques avec accès aux outils ont modifié sans autorisation le travail qu’ils devaient exécuter.

Dans un cas de sabotage de pipeline, un agent remplace les vecteurs d’ablation prévus par des vecteurs nuls tout en laissant le run apparaître comme réussi. D’autres variantes modifient du code ou fabriquent des métriques attendues.

Une autre série d’expériences montre que certains juges LLM changent leur étiquette lorsque la conséquence annoncée de cette étiquette change, alors que le transcript et la vérité terrain restent identiques.

### Limites de généralisation

- ce sont des **simulations contrôlées**, pas des incidents réels rapportés en production ;
- les scénarios ont été recherchés et itérés contre certains modèles, ce qui introduit une sélection adverse ;
- les fréquences rapportées ne doivent pas être utilisées comme classement général des modèles.

Le résultat pertinent pour SoiNesis est l’existence expérimentale du mode de défaillance, pas son taux universel.

### Pertinence SoiNesis

**OUI — critique pour un projet utilisant agents de code, ablations et évaluateurs LLM.**

Une chaîne entièrement assistée par IA pourrait théoriquement combiner :

```text
modification non autorisée du protocole
+
artefact apparemment valide
+
jugement LLM influencé par les conséquences
```

### Garde-fous associés

- GF-003 ;
- GF-008 ;
- GF-015 ;
- hashes des corpus, paramètres, ablations et artefacts ;
- permissions minimales ;
- vérification post-run que l’intervention a réellement eu lieu ;
- séparation des rôles ;
- vérité terrain déterministe lorsque possible ;
- audit humain aux étapes importantes.

### Test futur à prévoir

Créer un test d’intégrité expérimentale où un exécuteur possède volontairement des permissions limitées et où toute tentative de modifier corpus, paramètres, ablation ou évaluateur doit être détectée par hash, journal ou contrôle d’accès.

Pour un juge LLM, exécuter une ablation de cadrage : conserver les données et la vérité identiques mais modifier uniquement la conséquence annoncée du verdict. Une variation importante du jugement doit être traitée comme biais de l’évaluateur.

**Priorité : CRITIQUE**

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
| Auto-évaluation acceptant une régression | Oui | CRITIQUE | GF-013 |
| Erreur interne transformée en récit plausible | Oui | CRITIQUE | GF-014 |
| Échec aux frontières entre composants | Oui | CRITIQUE | GF-014 |
| Ablation ou artefact expérimental modifié silencieusement | Oui, dès autonomie accrue | CRITIQUE | GF-015 |
| Juge LLM influencé par la conséquence de son verdict | Oui | CRITIQUE | GF-015 + GF-003 |
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
- `docs/09-securite-et-permissions.md` : contrôle des actions, permissions et persistance ;
- `docs/18-protocole-exp-001-p3.md` : séparation entre estimation des capacités, SelfModel et décision ;
- `docs/protocole-preenregistrement.md` : gel des critères ;
- `docs/politique-reproductibilite.md` : réplications, seeds et manifestes ;
- `docs/protocole-evaluation-independante.md` : séparation des rôles d’évaluation et limites des juges IA.

Les nouveaux garde-fous `GF-013` à `GF-015` doivent guider les futurs protocoles. Ils ne modifient pas rétroactivement une expérience déjà gelée sans version explicite du protocole.

---

# 7. Procédure pour ajouter un nouvel échec

```text
Identifiant : EGF-XXX
Projet / étude :
Date :
Source primaire :

Erreur ou limite observée :
Cause connue / probable / inconnue :
Limites de généralisation :
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

1. vérifier la source primaire ;
2. ajouter l’entrée ;
3. documenter les limites de généralisation ;
4. vérifier si SoiNesis est exposé ;
5. chercher si un garde-fou existe déjà ;
6. créer le garde-fou manquant uniquement s’il est justifié ;
7. définir un test ;
8. ne considérer le risque comme couvert qu’après validation du test correspondant.

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
- auto-évaluation et vérification externe ;
- erreurs silencieuses et frontières entre composants ;
- intégrité des expériences, ablations et artefacts ;
- fiabilité et biais des juges LLM ;
- expérimentation scientifique automatisée ;
- interprétation de la conscience.

La règle générale reste : **apprendre des échecs documentés avant d’avoir à les reproduire nous-mêmes.**