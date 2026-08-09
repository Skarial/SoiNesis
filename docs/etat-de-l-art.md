# SoiNesis — État de l’art

**Fichier :** `docs/etat-de-l-art.md`  
**Version :** 0.1  
**Date :** 9 août 2026  
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

- mémoire autobiographique ;
- mémoire épisodique ;
- modèle de soi ;
- métacognition ;
- estimation de ses propres capacités ;
- attention ;
- objectifs persistants ;
- architectures cognitives modulaires ;
- traitement récurrent ;
- Global Workspace ;
- agents incarnés ;
- agents sociaux ;
- apprentissage à partir de l’expérience ;
- ablations expérimentales.

Plusieurs de ces mécanismes ont déjà été étudiés séparément ou conjointement.

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

La présente version constitue un **premier état de l’art ciblé**, et non une revue systématique exhaustive.

Avant toute revendication scientifique importante, il faudra compléter la recherche avec au minimum :

- recherche par mots-clés et synonymes ;
- recherche des travaux cités par les articles proches ;
- recherche des articles qui les citent ;
- comparaison avec les architectures cognitives classiques antérieures aux LLM ;
- recherche des prépublications récentes ;
- vérification de l’existence de réplications ou critiques ;
- vérification de la date d’antériorité du résultat revendiqué.

Les résultats négatifs de cette recherche doivent aussi être documentés : ne pas trouver de précédent n’est pas une preuve suffisante d’originalité.

---

# 4. Travaux directement pertinents

## 4.1 Generative Agents — Park et al. (2023)

**Référence :** Joon Sung Park et al., *Generative Agents: Interactive Simulacra of Human Behavior*.  
**Source :** https://arxiv.org/abs/2304.03442

### Éléments pertinents

Le travail étend un modèle de langage avec notamment :

- un historique d’expériences ;
- une récupération dynamique de souvenirs ;
- des réflexions de plus haut niveau ;
- de la planification ;
- un environnement social simulé ;
- des études d’ablation sur plusieurs composants.

### Ressemblances avec SoiNesis

- mémoire persistante ;
- continuité inter-épisodes ;
- réflexion à partir de l’expérience ;
- comportement dépendant de l’histoire ;
- utilisation d’ablations pour mesurer le rôle des composants.

### Différences actuellement visées par SoiNesis

SoiNesis cherche notamment à rendre explicites :

- la provenance des souvenirs ;
- la distinction information reçue / déduction / imagination / expérience directe ;
- le versionnement de certaines représentations internes ;
- un modèle de soi causalement actif ;
- des conditions expérimentales contrôlant l’accès aux mêmes preuves ;
- la distinction stricte entre fonction cognitive et conscience phénoménale.

### Conséquence pour SoiNesis

SoiNesis ne doit pas revendiquer comme nouvelles :

- l’idée d’un agent LLM possédant une mémoire d’expériences ;
- la réflexion sur cette mémoire ;
- la planification à partir de souvenirs ;
- l’usage d’ablations sur ces composants.

---

## 4.2 CoALA — Sumers et al. (2023)

**Référence :** Theodore R. Sumers et al., *Cognitive Architectures for Language Agents*.  
**Source :** https://arxiv.org/abs/2309.02427

### Éléments pertinents

CoALA propose un cadre général pour les agents de langage comprenant notamment :

- des composants de mémoire modulaires ;
- un espace d’actions structuré ;
- des actions internes et externes ;
- un processus général de décision ;
- une lecture des agents LLM à travers l’histoire des architectures cognitives.

### Ressemblances avec SoiNesis

- séparation de fonctions cognitives ;
- architecture modulaire autour d’un modèle de langage ;
- mémoire externe au LLM ;
- décision et actions structurées ;
- distinction entre cognition interne et interaction avec l’environnement.

### Conséquence pour SoiNesis

L’idée générale d’une **architecture cognitive modulaire pour agent de langage** n’est pas une contribution originale de SoiNesis.

Une contribution éventuelle devra porter sur un mécanisme, une interaction causale, une mesure ou un résultat expérimental plus précis.

---

## 4.3 Butlin et al. — indicateurs de conscience artificielle (2023)

**Référence :** Patrick Butlin et al., *Consciousness in Artificial Intelligence: Insights from the Science of Consciousness*.  
**Source :** https://arxiv.org/abs/2308.08708

### Éléments pertinents

Le rapport examine plusieurs théories scientifiques de la conscience, notamment :

- Recurrent Processing Theory ;
- Global Workspace Theory ;
- Higher-Order Theories ;
- Predictive Processing ;
- Attention Schema Theory.

Il en dérive des propriétés indicatrices formulées de manière suffisamment computationnelle pour évaluer des systèmes artificiels.

### Ressemblances avec SoiNesis

- refus de déduire la conscience depuis une simple déclaration verbale ;
- séparation entre propriétés fonctionnelles et conscience phénoménale ;
- intérêt pour traitement récurrent, workspace, métacognition et représentation de soi ;
- recherche de propriétés testables plutôt que d’une imitation convaincante.

### Conséquence pour SoiNesis

SoiNesis ne doit pas présenter comme nouvelle l’idée générale de :

- traduire des théories de la conscience en mécanismes computationnels ;
- rechercher des indicateurs fonctionnels de conscience ;
- évaluer séparément plusieurs propriétés associées à la conscience.

SoiNesis peut toutefois comparer expérimentalement des implémentations précises et leurs interactions.

---

## 4.4 MetaCogAgent — Wang et Shu (2026)

**Référence :** Chenyu Wang et Yang Shu, *MetaCogAgent: A Metacognitive Multi-Agent LLM Framework with Self-Aware Task Delegation*.  
**Source :** https://arxiv.org/abs/2605.17292

### Éléments pertinents

MetaCogAgent équipe des agents d’un mécanisme de métacognition permettant notamment :

- d’estimer l’adéquation entre une tâche et leurs capacités ;
- d’utiliser un profil historique de capacités ;
- de raffiner progressivement leurs limites de compétence ;
- de déléguer des tâches lorsque la confiance est insuffisante ;
- d’évaluer les composants par ablation.

### Ressemblances avec SoiNesis

Cette publication est directement pertinente pour la tranche P3 :

- estimation de capacité propre ;
- apprentissage depuis les performances passées ;
- confiance métacognitive ;
- décision dépendant de cette estimation ;
- étude causale par comparaison de conditions.

### Différence expérimentale actuellement recherchée par P3

P3 distingue notamment :

- une estimation fixe ;
- une estimation calculée depuis l’historique brut ;
- une condition utilisant un état métacognitif et un `SelfModel` persistant/versionné.

L’intérêt potentiel n’est donc pas de démontrer simplement qu’un agent peut apprendre ses limites depuis son historique : ce principe possède déjà des précédents.

La question plus précise devient :

> Une représentation persistante, versionnée et causalement active de ses propres capacités apporte-t-elle un effet reproductible au-delà de l’accès direct au même historique de performances ?

### Statut d’originalité

**Inconnu.**

Une comparaison bibliographique plus fine sera nécessaire si P3 produit un effet positif.

---

## 4.5 Eyla — Aditto (2026)

**Référence :** Arif Aditto, *Eyla: Toward an Identity-Anchored LLM Architecture with Integrated Biological Priors — Vision, Implementation Attempt, and Lessons from AI-Assisted Development*.  
**Source :** https://arxiv.org/abs/2604.00009

### Éléments pertinents

Eyla explore notamment :

- une identité persistante ;
- un self-model cohérent ;
- une mémoire épisodique ;
- une estimation explicite de l’incertitude ;
- une architecture intégrée ;
- un développement assisté par des outils d’IA.

Le travail rapporte également un échec d’implémentation où de nombreux sous-systèmes ajoutés influençaient très peu la sortie finale.

### Ressemblances avec SoiNesis

- identité comme propriété architecturale ;
- self-model ;
- mémoire épisodique/autobiographique ;
- incertitude ;
- développement d’une architecture inhabituelle avec assistance IA.

### Leçon importante pour SoiNesis

La présence d’un module dans le code ne démontre pas son rôle cognitif.

Cette publication renforce une règle déjà centrale de SoiNesis :

> un mécanisme sans effet causal mesurable ne doit pas être considéré comme fonctionnel, même si son implémentation paraît complexe.

---

## 4.6 Global Workspace Agents — Shang (2026)

**Référence :** Wenlong Shang, *"Theater of Mind" for LLMs: A Cognitive Architecture Based on Global Workspace Theory*.  
**Source :** https://arxiv.org/abs/2604.08206

### Éléments pertinents

Le travail propose une architecture inspirée de Global Workspace Theory avec notamment :

- un hub central de diffusion ;
- plusieurs fonctions spécialisées ;
- un cycle cognitif continu et événementiel ;
- une mémoire à plusieurs niveaux ;
- des mécanismes visant une continuité d’agence dans le temps.

### Ressemblances avec SoiNesis

- intégration globale ;
- diffusion d’informations importantes entre fonctions ;
- cycle cognitif récurrent ;
- continuité temporelle ;
- mémoire longue durée.

### Conséquence pour SoiNesis

La future intégration globale de SoiNesis devra être comparée explicitement aux architectures Global Workspace existantes.

Le simple fait d’ajouter un « espace global » ou une boucle continue ne constituera pas une contribution nouvelle.

---

## 4.7 Gurnee et al. — workspace interne aux LLM (2026)

**Référence :** Wes Gurnee et al., *Verbalizable Representations Form a Global Workspace in Language Models*.  
**Source :** https://arxiv.org/abs/2607.15495

### Éléments pertinents

Ce travail récent rapporte que certaines représentations internes de modèles de langage présentent plusieurs propriétés fonctionnelles rapprochées d’un Global Workspace.

### Importance pour SoiNesis

Cette piste est particulièrement importante pour éviter une hypothèse implicite erronée :

> un mécanisme fonctionnel ressemblant à un workspace n’a pas nécessairement besoin d’être entièrement ajouté autour du LLM.

Lorsqu’un futur module d’intégration globale sera testé, il faudra distinguer :

- l’effet provenant du LLM lui-même ;
- l’effet provenant de l’architecture externe de SoiNesis ;
- l’interaction éventuelle entre les deux.

Le résultat de cette prépublication ne constitue pas une preuve de conscience phénoménale.

---

# 5. Tableau de positionnement initial

| Élément | Précédents identifiés | Position actuelle de SoiNesis |
| --- | --- | --- |
| Mémoire persistante d’agent | Oui | Reproduction / spécialisation |
| Mémoire autobiographique structurée | Oui, sous plusieurs formes | Différences de provenance et de contrôle à mesurer |
| Réflexion sur expériences | Oui | Pas une nouveauté en soi |
| Architecture cognitive modulaire | Oui | Pas une nouveauté en soi |
| Métacognition des capacités | Oui | P3 doit chercher une question plus précise |
| Self-model | Oui | Originalité du mécanisme précis inconnue |
| Self-model versionné et causal comparé à historique brut | Recherche ciblée nécessaire | Question P3 potentiellement intéressante |
| Global Workspace artificiel | Oui | Futur module à comparer aux travaux existants |
| Cycle cognitif continu | Oui | Pas une nouveauté en soi |
| Ablations | Oui | Méthode standard à conserver |
| Indicateurs fonctionnels de conscience | Oui | Ne pas revendiquer l’idée générale |
| Développement longitudinal d’une identité artificielle | Précédents partiels | Terrain de recherche à préciser |
| Conscience phénoménale | Aucun résultat accepté comme démonstration dans ce projet | Inconnue |

---

# 6. Conséquences immédiates pour P3

Aucune modification de l’architecture ou du code P3 n’est imposée par cet état de l’art à la date du 9 août 2026.

La comparaison P3 reste scientifiquement utile si elle contrôle réellement les informations accessibles aux conditions.

La question ne doit cependant plus être formulée comme :

> Une IA peut-elle apprendre ses propres capacités ?

Cette question possède déjà des précédents.

La question de travail plus précise est :

> À preuves disponibles comparables, l’utilisation d’un `SelfModel` persistant, versionné et causalement actif produit-elle une différence mesurable et reproductible par rapport à l’exploitation directe de l’historique brut ?

Si P3 ne montre aucune différence spécifique, le résultat négatif doit être conservé.

Si P3 montre une différence, l’étape suivante doit être :

1. vérifier les facteurs de confusion ;
2. reproduire l’effet ;
3. rechercher des travaux ayant déjà testé une comparaison équivalente ;
4. seulement ensuite évaluer le niveau de contribution scientifique.

---

# 7. Questions de veille prioritaires

Les recherches bibliographiques suivantes restent prioritaires :

1. self-models artificiels causalement actifs ;
2. self-models versionnés ou autobiographiques ;
3. comparaison self-model vs accès direct au même historique ;
4. calibration métacognitive longitudinale ;
5. continuité d’identité après changement de modèle de langage ;
6. transfert d’identité ou de mémoire entre modèles de langage ;
7. architectures à objectifs persistants propres ;
8. développement artificiel longitudinal ;
9. Global Workspace externe vs représentations globales internes au LLM ;
10. tests d’ablation appliqués aux architectures de conscience artificielle.

---

# 8. Règle de maintenance

Ce document doit être mis à jour :

- avant l’ajout d’un mécanisme cognitif majeur ;
- avant la conception d’un nouveau protocole expérimental important ;
- après un résultat positif inattendu ;
- avant toute revendication de nouveauté ;
- lorsqu’un travail récent modifie directement l’interprétation d’une expérience SoiNesis.

Chaque ajout doit préciser autant que possible :

- la référence ;
- ce qui a réellement été testé ;
- les résultats ;
- les ressemblances ;
- les différences ;
- les conséquences concrètes pour SoiNesis.

---

# 9. Principe de prudence

Une absence de travail identique trouvé dans cette liste ne signifie pas que le travail n’existe pas.

Les formulations autorisées sont :

- « aucun précédent identifié dans la recherche effectuée » ;
- « comparaison potentiellement nouvelle » ;
- « originalité à vérifier ».

Les formulations suivantes sont interdites sans justification bibliographique forte :

- « première architecture au monde » ;
- « mécanisme jamais étudié » ;
- « découverte inédite » ;
- « première conscience artificielle ».

L’objectif scientifique de SoiNesis est de produire des résultats falsifiables et reproductibles, pas de maximiser artificiellement une revendication d’originalité.
