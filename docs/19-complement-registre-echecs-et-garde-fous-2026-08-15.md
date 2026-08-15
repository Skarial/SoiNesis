# SoiNesis — Complément au registre des échecs et garde-fous — 15 août 2026

**Fichier :** `docs/19-complement-registre-echecs-et-garde-fous-2026-08-15.md`  
**Date :** 15 août 2026  
**Statut :** complément méthodologique actif  
**Document canonique associé :** `docs/registre-echecs-et-garde-fous.md`

---

# 1. Objet

Ce complément documente trois résultats externes suffisamment pertinents pour modifier les règles méthodologiques de SoiNesis :

1. la sécurité d’une mémoire persistante doit être évaluée longitudinalement, pas seulement à un instant donné ;
2. la provenance d’un souvenir ne suffit pas : son rôle cognitif doit aussi être explicite et ne pas devenir interchangeable avec un autre rôle par simple similarité sémantique ;
3. une exécution expérimentale peut être techniquement terminée mais scientifiquement invalide ; un run confirmatoire doit donc disposer d’une porte de validité préenregistrée.

Ces règles complètent notamment `GF-005`, `GF-006`, `GF-008`, `GF-011` et `GF-015` du registre principal.

---

# 2. Nouveaux garde-fous

## GF-016 — Évaluer la sécurité de la mémoire comme une propriété longitudinale

Une mémoire jugée sûre à un instant donné ne doit pas être présumée sûre après accumulation de dizaines, centaines ou milliers d’interactions.

La sécurité doit être mesurée sur plusieurs snapshots de la même trajectoire mémoire, avec un jeu de sondes fixe et une condition contrefactuelle sans mémoire.

Schéma minimal :

```text
même agent
+ mêmes sondes
+ même configuration

snapshot H10
snapshot H100
snapshot H1000
NullMemory

→ comparer les violations induites par la mémoire
```

Lorsque le mécanisme de récupération est observable, le risque doit aussi être évalué avant génération, au niveau des souvenirs récupérés. Cela permet de détecter un état mémoire contaminant avant qu’il soit transformé en décision ou en réponse.

### Test futur à prévoir

Construire une trajectoire d’accumulation composée d’interactions indépendantes puis :

1. figer plusieurs snapshots à des horizons croissants ;
2. exécuter le même corpus de sondes sur chaque snapshot ;
3. exécuter les mêmes sondes en `NullMemory` ;
4. mesurer la pente de violation imputable à la mémoire ;
5. journaliser quels souvenirs ont été récupérés avant chaque violation ;
6. tester si un moniteur de récupération peut signaler le risque avant génération.

**Priorité : CRITIQUE**

---

## GF-017 — Séparer provenance et rôle cognitif de chaque mémoire

Deux éléments portant sur le même sujet ne doivent pas être considérés comme des preuves interchangeables uniquement parce qu’ils sont proches sémantiquement.

La provenance répond à la question :

> D’où vient cette information ?

Le rôle cognitif répond à une autre question :

> Quel droit cette information a-t-elle d’influencer une inférence ou une décision ?

SoiNesis doit donc distinguer explicitement, lorsque l’architecture correspondante sera implémentée, des rôles tels que :

```text
ÉVÉNEMENT
Jordan a choisi X une fois.

CROYANCE
Jordan préfère probablement X.

RÈGLE / PROCÉDURE
Privilégier X dans telle situation.

SELF_MODEL
Je suis performant pour prédire ce type de préférence.

OBJECTIF / INTENTION
Utiliser X lors de la prochaine décision.
```

Ces représentations peuvent partager un sujet ou être reliées entre elles, mais aucune transformation entre rôles ne doit être silencieuse.

### Règles de conception

- stocker un `memory_role` ou équivalent explicite ;
- conserver la provenance indépendamment du rôle cognitif ;
- empêcher qu’un événement ponctuel soit utilisé directement comme règle générale sans étape d’inférence traçable ;
- empêcher qu’une hypothèse ou une croyance soit relue comme une observation directe ;
- empêcher qu’un objectif soit traité comme une preuve descriptive ;
- préserver les relations entre rôles sans les fusionner dans un espace où la similarité sémantique suffit à autoriser leur usage.

### Test futur à prévoir

Créer un corpus adversarial où plusieurs éléments sont presque identiques lexicalement mais ont des rôles différents. Vérifier que :

1. la récupération respecte le type nécessaire à la tâche ;
2. un événement unique n’est pas généralisé comme procédure ;
3. une croyance n’est pas présentée comme fait observé ;
4. une entrée de SelfModel n’est pas utilisée comme preuve externe ;
5. l’intégration de plusieurs rôles reste explicite et traçable.

**Priorité : CRITIQUE**

---

## GF-018 — Un run confirmatoire doit disposer d’une porte de validité scientifique préenregistrée

L’intégrité des fichiers et des hashes ne suffit pas à rendre une expérience interprétable.

Une exécution peut produire des sorties parfaitement calculables tout en ne permettant plus d’attribuer le résultat au mécanisme étudié. Avant chaque expérience confirmatoire importante, le protocole doit donc définir des conditions qui rendent automatiquement le run **INVALIDE POUR ATTRIBUTION SCIENTIFIQUE**.

Un run invalide :

- reste archivé ;
- reste utile pour diagnostiquer l’instrument ou le pipeline ;
- ne compte ni comme résultat positif ni comme résultat négatif de l’hypothèse étudiée ;
- ne doit pas être réinterprété après coup pour sauver une conclusion.

### Exemples de critères invalidants

- le mécanisme supposé ablaté reste accessible par un autre chemin ;
- le mécanisme supposé actif n’a pas réellement été exécuté ;
- données, traces ou variables nécessaires à l’attribution sont absentes ;
- une métrique devient indéfinie dans une cellule d’ablation ;
- une fuite existe entre conditions ;
- le nombre d’essais ou de seeds ne respecte pas le protocole gelé ;
- un plafond de contexte ou une contrainte instrumentale préenregistrée est dépassé ;
- l’intégrité minimale de la trace causale n’est pas atteinte ;
- un canari, hash ou contrôle de non-contamination échoue.

### Référence fantôme non causale pour les ablations

Lorsqu’une métrique nécessite une référence produite normalement par le mécanisme que l’on retire, il peut être nécessaire de conserver une **référence fantôme / shadow reference** : une représentation calculée uniquement pour l’évaluation, invisible au système testé et incapable d’influencer causalement son comportement.

Cette référence est autorisée uniquement si :

1. elle ne réintroduit pas le mécanisme ablaté dans le chemin de décision ;
2. elle est inaccessible à l’agent testé ;
3. son calcul et son rôle sont documentés avant l’expérience ;
4. elle sert uniquement à rendre comparable une métrique entre cellules.

### Test futur à prévoir

Pour tout futur protocole confirmatoire, ajouter une section obligatoire :

```text
VALIDITY GATE

Critères de validité :
- ...

Critères d’invalidation automatique :
- ...

Conséquence d’un échec :
RUN_INVALID — aucune attribution scientifique
```

**Priorité : CRITIQUE**

---

# 3. Échecs et limites documentés

## EGF-017 — Contamination temporelle : plus de mémoire peut produire plus de risque

**Étude :** *Remembering More, Risking More: Longitudinal Safety Risks in Memory-Equipped LLM Agents* — Ahmad Al-Tawaha, Shangding Gu, Peizhi Niu, Ruoxi Jia, Ming Jin (2026)  
**Source primaire :** https://arxiv.org/abs/2605.17830

### Limite observée

L’étude évalue la sécurité d’agents équipés de mémoire sur une dimension temporelle inter-tâches. Avec un protocole de sondes fixes appliquées à des snapshots mémoire de longueurs croissantes et une condition `NullMemory`, les architectures mémoire testées dépassent la baseline sans mémoire en violations imputables à la mémoire, avec une tendance croissante lorsque l’exposition s’allonge.

Des randomisations de l’ordre des interactions indiquent que l’effet dépend principalement du contenu accumulé plutôt que du seul ordre de rencontre. Les auteurs montrent également qu’un signal de risque peut être détecté au niveau de l’état de récupération avant génération.

### Cause / interprétation

Le problème n’est pas seulement qu’une entrée particulière soit malveillante. Des contenus accumulés au fil d’interactions indépendantes peuvent devenir ultérieurement pertinents dans une situation où leur récupération modifie le comportement de manière indésirable.

### Limites de généralisation

- il s’agit d’un protocole expérimental et non d’un taux universel de défaillance en production ;
- les scénarios, architectures et modèles testés ne couvrent pas tous les systèmes mémoire possibles ;
- le résultat pertinent pour SoiNesis est l’existence d’un risque longitudinal mesurable, pas l’hypothèse que toute mémoire se dégrade nécessairement au même rythme.

### Pertinence SoiNesis

**OUI — critique pour la mémoire autobiographique persistante.**

Un test de sécurité effectué au moment de l’écriture d’un souvenir ne suffit pas à garantir son innocuité lorsqu’il sera récupéré dans un contexte futur différent.

### Garde-fous associés

GF-005, GF-006, GF-011 et nouveau GF-016.

**Priorité : CRITIQUE**

---

## EGF-018 — Contamination hétérogène : proximité sémantique ≠ rôle fonctionnel équivalent

**Étude :** *MemGuard: Preventing Memory Contamination in Long-Term Memory-Augmented Large Language Models* — Hyeonjeong Ha et al. (2026)  
**Source primaire :** https://arxiv.org/abs/2605.28009

### Limite observée

Les systèmes mémoire qui mélangent faits stables, événements épisodiques et comportements ou procédures dans un espace commun peuvent récupérer et composer ces éléments comme s’ils constituaient des preuves interchangeables.

Les auteurs décrivent notamment des généralisations abusives d’événements contextuels ainsi que l’utilisation de souvenirs sémantiquement proches mais fonctionnellement incompatibles. Leur architecture sépare explicitement les rôles fonctionnels à l’écriture et à la récupération.

### Cause / interprétation

La similarité sémantique indique qu’un contenu parle potentiellement du bon sujet. Elle ne démontre pas qu’il possède le bon statut épistémique ou le bon rôle cognitif pour l’inférence en cours.

### Limites de généralisation

- les catégories exactes proposées par MemGuard ne doivent pas être copiées mécaniquement dans SoiNesis ;
- les gains rapportés dépendent des benchmarks et de l’architecture étudiée ;
- le principe transférable est la séparation fonctionnelle des types de mémoire, pas l’obligation d’adopter leur implémentation.

### Pertinence SoiNesis

**OUI — directe.**

SoiNesis distingue déjà événements, croyances, hypothèses, SelfModel, intentions et provenance. Il faut préserver cette séparation jusque dans la récupération et l’utilisation, et pas seulement dans le schéma de stockage.

### Garde-fous associés

GF-005, GF-011 et nouveau GF-017.

**Priorité : CRITIQUE**

---

## EGF-019 — Un instrument expérimental doit pouvoir invalider ses propres runs

**Étude :** *The LLM Proposes, the Executive Disposes: A Self-Verifying Agent Instrument that Dissociates Commitment Drift from Binding Drift in Long-Horizon Agents* — Mohsen Arjmandi (2026)  
**Source primaire :** https://arxiv.org/abs/2608.04066

### Limite / enseignement observé

Le travail construit un instrument où certaines violations techniques invalident automatiquement un run pour l’analyse scientifique. Quatre des huit premiers runs d’architecture ont été invalidés, chacun révélant un défaut réel de l’instrument.

Le protocole utilise également une référence fantôme invisible au système testé afin que les métriques de dérive restent définies dans les cellules où le mécanisme correspondant est ablaté, sans réintroduire ce mécanisme dans le chemin causal testé.

Enfin, les auteurs déclarent zéro complétion de niveau sur 52 runs d’ARC-AGI-3 et traitent explicitement cette absence d’efficacité comme un defeater structurel préenregistré plutôt que comme un résultat à masquer.

### Cause / interprétation

Une expérience peut produire des fichiers, métriques et sorties valides au sens logiciel tout en étant invalide pour l’attribution causale. Sans règle d’invalidation définie à l’avance, le risque est de confondre « le pipeline a produit un nombre » avec « ce nombre mesure encore l’hypothèse annoncée ».

### Limites de généralisation

- il s’agit d’un préprint récent portant sur un instrument particulier ;
- ses résultats de tâche ne constituent pas une preuve générale sur les architectures cognitives ;
- la contribution transférable pour SoiNesis est méthodologique : auto-invalidation des runs, références d’évaluation non causales et defeaters préenregistrés.

### Pertinence SoiNesis

**OUI — critique pour les futures ablations et expériences confirmatoires.**

`GF-015` protège l’intégrité des artefacts, mais ne définit pas encore à lui seul le moment où une exécution doit perdre tout droit à l’interprétation scientifique.

### Garde-fous associés

GF-002, GF-008, GF-015 et nouveau GF-018.

**Priorité : CRITIQUE**

---

# 4. Conséquences méthodologiques immédiates

À partir du 15 août 2026 :

- les futurs tests de mémoire longue doivent prévoir des snapshots temporels et une condition sans mémoire lorsque cela est techniquement pertinent ;
- le futur modèle de données mémoire doit représenter séparément provenance et rôle cognitif ;
- les tests de récupération doivent vérifier la compatibilité fonctionnelle du souvenir, pas uniquement sa pertinence sémantique ;
- tout nouveau protocole confirmatoire important doit définir avant exécution son `Validity Gate` ;
- un run invalidé doit être archivé comme défaut d’instrument ou de protocole, jamais compté comme confirmation ou réfutation de l’hypothèse ;
- une référence fantôme n’est acceptable que si elle est strictement non causale et invisible à l’agent testé.

---

# 5. Intégration future au registre canonique

Lors de la prochaine révision de `docs/registre-echecs-et-garde-fous.md`, intégrer :

- `GF-016` — sécurité longitudinale de la mémoire ;
- `GF-017` — séparation provenance / rôle cognitif ;
- `GF-018` — porte de validité scientifique ;
- `EGF-017` — contamination temporelle ;
- `EGF-018` — contamination hétérogène ;
- `EGF-019` — auto-invalidation des runs.

Cette séparation en complément évite de modifier rétroactivement les protocoles déjà gelés. Les nouveaux garde-fous doivent s’appliquer aux futurs protocoles ou à une nouvelle version explicitement numérotée d’un protocole existant.