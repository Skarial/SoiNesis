# SoiNesis — État de l’art

**Fichier :** `docs/etat-de-l-art.md`  
**Version :** 0.2  
**Date :** 12 août 2026  
**Statut :** document vivant, incomplet par définition

---

# 1. Objet du document

Ce document maintient le positionnement de SoiNesis par rapport aux travaux scientifiques et techniques pertinents.

Il sert à distinguer :

- ce qui est déjà connu dans la littérature ;
- ce que SoiNesis reproduit ;
- ce que SoiNesis étend ;
- ce que SoiNesis combine différemment ;
- ce qui pourrait éventuellement constituer un résultat nouveau.

Ce document ne doit jamais être utilisé pour affirmer que SoiNesis est inédit dans son ensemble.

L’originalité d’une architecture, d’un mécanisme ou d’un résultat doit rester **inconnue** tant qu’une recherche bibliographique suffisamment ciblée n’a pas été réalisée.

---

# 2. Position scientifique

SoiNesis n’est pas fondé sur l’hypothèse que les briques suivantes sont nouvelles :

- mémoire autobiographique ou épisodique ;
- mémoire persistante d’agent ;
- modèle de soi ;
- métacognition ;
- estimation de ses propres capacités ;
- attention ;
- objectifs persistants ;
- architectures cognitives modulaires ;
- traitement récurrent ;
- Global Workspace ;
- agents incarnés ou sociaux ;
- apprentissage à partir de l’expérience ;
- planification et replanification ;
- ablations expérimentales.

La contribution éventuelle de SoiNesis doit donc être recherchée dans :

1. une comparaison expérimentale encore non réalisée ;
2. une combinaison de mécanismes produisant un effet non expliqué par les composants isolés ;
3. un mécanisme causal plus précisément défini ou mieux contrôlé ;
4. une méthode de mesure ou de falsification nouvelle ;
5. un phénomène longitudinal ou développemental encore insuffisamment étudié ;
6. un résultat reproductible qui résiste aux explications alternatives connues.

Aucune de ces possibilités ne doit être présumée à l’avance.

---

# 3. Méthode de veille

La présente version constitue un état de l’art ciblé et vivant, pas une revue systématique exhaustive.

Avant toute revendication scientifique importante, il faut compléter la recherche avec :

- mots-clés et synonymes ;
- travaux cités par les articles proches ;
- articles qui les citent ;
- architectures cognitives classiques antérieures aux LLM ;
- prépublications récentes ;
- réplications, critiques et résultats négatifs ;
- vérification des dates d’antériorité.

Ne pas trouver de précédent n’est jamais une preuve suffisante d’originalité.

---

# 4. Travaux directement pertinents

## 4.1 Generative Agents — Park et al. (2023)

**Référence :** Joon Sung Park et al., *Generative Agents: Interactive Simulacra of Human Behavior*.  
**Source :** https://arxiv.org/abs/2304.03442

### Éléments pertinents

- historique d’expériences ;
- récupération dynamique de souvenirs ;
- réflexions de plus haut niveau ;
- planification ;
- environnement social simulé ;
- études d’ablation.

### Conséquence pour SoiNesis

La mémoire d’expériences, la réflexion sur cette mémoire, la planification depuis des souvenirs et l’usage d’ablations ne sont pas nouveaux en eux-mêmes.

Les différences de SoiNesis doivent être recherchées dans la provenance, le versionnement, les comparaisons contrôlées, les effets causaux et les phénomènes longitudinaux.

---

## 4.2 CoALA — Sumers et al. (2023)

**Référence :** Theodore R. Sumers et al., *Cognitive Architectures for Language Agents*.  
**Source :** https://arxiv.org/abs/2309.02427

### Éléments pertinents

CoALA formalise une architecture cognitive pour agents de langage comprenant mémoire, actions internes/externes et processus de décision.

### Conséquence pour SoiNesis

L’idée générale d’une architecture cognitive modulaire autour d’un LLM n’est pas une contribution originale de SoiNesis.

---

## 4.3 Butlin et al. — indicateurs de conscience artificielle (2023)

**Référence :** Patrick Butlin et al., *Consciousness in Artificial Intelligence: Insights from the Science of Consciousness*.  
**Source :** https://arxiv.org/abs/2308.08708

### Éléments pertinents

Le travail dérive des propriétés indicatrices à partir de plusieurs théories de la conscience : traitement récurrent, Global Workspace, Higher-Order, predictive processing, attention schema, etc.

### Conséquence pour SoiNesis

SoiNesis ne doit pas présenter comme nouvelle l’idée générale de traduire des théories de la conscience en propriétés computationnelles testables. Une auto-déclaration n’est pas une preuve phénoménale.

---

## 4.4 MetaCogAgent — Wang et Shu (2026)

**Référence :** Chenyu Wang et Yang Shu, *MetaCogAgent: A Metacognitive Multi-Agent LLM Framework with Self-Aware Task Delegation*.  
**Source :** https://arxiv.org/abs/2605.17292

### Éléments pertinents

- estimation de capacité propre ;
- apprentissage depuis les performances passées ;
- confiance métacognitive ;
- décision et délégation dépendant de cette estimation ;
- ablations.

### Conséquence pour P3

La question « une IA peut-elle apprendre ses propres limites depuis son historique ? » possède déjà des précédents.

La question plus spécifique de P3 reste :

> À preuves comparables, un `SelfModel` persistant, versionné et causalement actif produit-il une différence mesurable par rapport à une reconstruction directe depuis le même historique ?

**Statut d’originalité : inconnu.**

---

## 4.5 Eyla — Aditto (2026)

**Référence :** Arif Aditto, *Eyla: Toward an Identity-Anchored LLM Architecture with Integrated Biological Priors — Vision, Implementation Attempt, and Lessons from AI-Assisted Development*.  
**Source :** https://arxiv.org/abs/2604.00009

### Éléments pertinents

Identité persistante, self-model, mémoire épisodique, incertitude et développement assisté par IA.

### Leçon pour SoiNesis

Un module présent dans le code ne démontre pas une fonction cognitive. La causalité doit être mesurée avant d’étendre l’architecture.

---

## 4.6 Global Workspace Agents — Shang (2026)

**Référence :** Wenlong Shang, *"Theater of Mind" for LLMs: A Cognitive Architecture Based on Global Workspace Theory*.  
**Source :** https://arxiv.org/abs/2604.08206

### Éléments pertinents

Hub de diffusion, fonctions spécialisées, cycle cognitif continu, mémoire multi-niveaux et continuité d’agence.

### Conséquence pour SoiNesis

Un futur mécanisme d’intégration globale devra être comparé aux architectures Global Workspace existantes. Ajouter un « espace global » n’est pas nouveau en soi.

---

## 4.7 Gurnee et al. — workspace interne aux LLM (2026)

**Référence :** Wes Gurnee et al., *Verbalizable Representations Form a Global Workspace in Language Models*.  
**Source :** https://arxiv.org/abs/2607.15495

### Importance

Certaines propriétés fonctionnelles rapprochées d’un Global Workspace pourraient déjà émerger dans les représentations internes du LLM.

Les futures expériences doivent donc distinguer :

- effet du LLM lui-même ;
- effet de l’architecture externe SoiNesis ;
- interaction entre les deux.

Ce résultat ne constitue pas une preuve de conscience phénoménale.

---

## 4.8 AMA-Bench — mémoire agentique et causalité (2026)

**Référence :** Yujie Zhao et al., *AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications*.  
**Source :** https://arxiv.org/abs/2602.22769

### Éléments pertinents

AMA-Bench évalue des systèmes mémoire sur de vraies trajectoires agentiques et des trajectoires synthétiques extensibles à de longs horizons.

Les auteurs rapportent que les systèmes existants sont notamment limités par :

- perte d’information causale ;
- perte d’information objective ;
- caractère lossy des récupérations par similarité.

Leur propre système ajoute notamment un graphe de causalité et une récupération outillée.

### Conséquence pour SoiNesis

Une mémoire autobiographique ne doit pas être évaluée seulement sur le rappel du contenu.

SoiNesis doit préserver et tester :

- pourquoi un état existe ;
- quelle preuve ou action l’a causé ;
- l’ordre temporel ;
- la provenance ;
- la capacité à revenir aux preuves brutes.

Cela renforce le garde-fou `GF-011` dans `docs/registre-echecs-et-garde-fous.md`.

---

## 4.9 Chain-of-Memory — construction légère et utilisation de la mémoire (2026)

**Référence :** Xiucheng Xu et al., *Chain-of-Memory: Lightweight Memory Construction with Dynamic Evolution for LLM Agents*.  
**Source :** https://arxiv.org/abs/2601.14287

### Éléments pertinents

Les auteurs identifient deux limites importantes :

- les architectures de construction mémoire complexes peuvent coûter beaucoup pour des gains faibles ;
- un bon rappel des fragments pertinents ne garantit pas une bonne précision de raisonnement.

Leur approche cherche à mieux organiser les souvenirs récupérés en chemins d’inférence.

### Conséquence pour SoiNesis

Les futures évaluations mémoire doivent distinguer au minimum :

```text
conservation
→ récupération
→ intégration / interprétation
→ effet sur la décision
```

P1/P2 ne doivent pas être généralisés comme preuve qu’un bon rappel équivaut à une mémoire fonctionnellement supérieure.

---

## 4.10 Aghzal et al. — échecs des web agents par niveau (ACL 2026)

**Référence :** Mohamed Aghzal, Gregory J. Stein, Ziyu Yao, *Why Do LLM-based Web Agents Fail? A Hierarchical Planning Perspective*.  
**Source :** https://aclanthology.org/2026.acl-long.1483/

### Éléments pertinents

L’étude décompose les agents en :

- planification haut niveau ;
- exécution bas niveau ;
- replanification.

Des plans PDDL structurés deviennent plus concis et orientés vers le but que des plans en langage naturel, mais l’exécution bas niveau reste le principal goulot d’étranglement.

### Conséquence pour SoiNesis

Un objectif persistant ou un plan cohérent ne doit pas être confondu avec une capacité d’action réussie.

Les futurs tests d’agence devront mesurer séparément :

```text
objectif
→ plan
→ action
→ observation
→ détection d’erreur
→ replanification
```

Cela renforce `GF-012`.

---

# 5. Tableau de positionnement actuel

| Élément | Précédents identifiés | Position actuelle de SoiNesis |
| --- | --- | --- |
| Mémoire persistante d’agent | Oui | Reproduction / spécialisation |
| Mémoire autobiographique structurée | Oui, sous plusieurs formes | Provenance, causalité et contrôle à mesurer |
| Récupération par similarité | Oui | Ne pas supposer qu’elle suffit aux relations causales |
| Bon rappel → bon raisonnement | Non garanti | Mesurer séparément récupération et utilisation |
| Réflexion sur expériences | Oui | Pas une nouveauté en soi |
| Architecture cognitive modulaire | Oui | Pas une nouveauté en soi |
| Métacognition des capacités | Oui | P3 doit poser une question plus précise |
| Self-model | Oui | Originalité du mécanisme précis inconnue |
| Self-model versionné causal vs historique brut | Recherche ciblée nécessaire | Question P3 potentiellement intéressante |
| Planification hiérarchique agentique | Oui | Plan ≠ exécution ; mesurer chaque couche |
| Global Workspace artificiel | Oui | Futur module à comparer aux travaux existants |
| Ablations | Oui | Méthode standard à conserver |
| Indicateurs fonctionnels de conscience | Oui | Ne pas revendiquer l’idée générale |
| Développement longitudinal d’une identité artificielle | Précédents partiels | Terrain à préciser |
| Conscience phénoménale | Aucun résultat accepté comme démonstration dans ce projet | Inconnue |

---

# 6. Conséquences immédiates pour P3

Aucune modification rétroactive du protocole P3 n’est imposée par ces ajouts.

P3 doit continuer à répondre à sa question gelée. Les nouveaux travaux influencent surtout :

- l’interprétation du résultat ;
- les futurs protocoles mémoire ;
- les futurs tests de long horizon ;
- les futurs objectifs et actions incarnées.

Si P3 ne montre aucune différence spécifique entre B et C, le résultat négatif doit être conservé.

Si P3 montre une différence :

1. vérifier les facteurs de confusion ;
2. reproduire l’effet ;
3. rechercher une comparaison équivalente dans la littérature ;
4. seulement ensuite évaluer le niveau de contribution.

---

# 7. Questions de veille prioritaires

1. self-models artificiels causalement actifs ;
2. self-models versionnés ou autobiographiques ;
3. comparaison self-model vs accès direct au même historique ;
4. calibration métacognitive longitudinale ;
5. continuité d’identité après changement de modèle de langage ;
6. transfert d’identité ou de mémoire entre modèles ;
7. consolidation mémoire préservant causalité et provenance ;
8. récupération causale vs récupération par similarité ;
9. coût cognitif des mémoires structurées complexes ;
10. objectifs persistants et mémoire prospective ;
11. développement artificiel longitudinal ;
12. Global Workspace externe vs représentations globales internes au LLM ;
13. ablations appliquées aux architectures de conscience artificielle ;
14. séparation planification / exécution / replanification dans les agents incarnés.

---

# 8. Règle de maintenance

Ce document doit être mis à jour :

- avant l’ajout d’un mécanisme cognitif majeur ;
- avant la conception d’un nouveau protocole expérimental important ;
- après un résultat positif inattendu ;
- avant toute revendication de nouveauté ;
- lorsqu’un travail récent modifie directement l’interprétation d’une expérience SoiNesis.

Chaque ajout doit préciser autant que possible : référence, test réel, résultats, ressemblances, différences et conséquences concrètes pour SoiNesis.

---

# 9. Principe de prudence

Une absence de travail identique trouvé dans cette liste ne signifie pas que le travail n’existe pas.

Formulations autorisées :

- « aucun précédent identifié dans la recherche effectuée » ;
- « comparaison potentiellement nouvelle » ;
- « originalité à vérifier ».

Formulations interdites sans justification bibliographique forte :

- « première architecture au monde » ;
- « mécanisme jamais étudié » ;
- « découverte inédite » ;
- « première conscience artificielle ».

L’objectif scientifique de SoiNesis est de produire des résultats falsifiables et reproductibles, pas de maximiser artificiellement une revendication d’originalité.