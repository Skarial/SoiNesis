# SoiNesis — Protocole EXP-001-P3

**Fichier :** `docs/18-protocole-exp-001-p3.md`

**Version :** 0.2

**Date :** 8 août 2026

**Statut :** approuvé pour implémentation DEV uniquement — OFFICIAL interdit avant calibration, validation et gel définitif.

**Code de l’expérience :** `EXP-001-P3`

**Protocole parent :** `EXP-001`

**Phase précédente :** `EXP-001-P2`

**Titre :** Modèle de soi causal et métacognition dynamique appliqués aux capacités propres

**Documents associés :**

- `docs/01-definitions.md`
- `docs/02-hypotheses.md`
- `docs/03-architecture-generale.md`
- `docs/04-modele-de-donnees.md`
- `docs/05-cycle-cognitif.md`
- `docs/06-memoire-autobiographique.md`
- `docs/07-modele-de-soi.md`
- `docs/08-journal-evolution.md`
- `docs/09-securite-et-permissions.md`
- `docs/10-protocole-exp-001.md`
- `docs/13-protocole-exp-001-p1.md`
- `docs/14-rapport-exp-001-p1.md`
- `docs/15-protocole-exp-001-p2.md`
- `docs/16-note-deviation-exp-001-p2.md`
- `docs/17-rapport-exp-001-p2.md`

> **Limite d’autorisation :** le présent protocole autorise uniquement la future implémentation et calibration en environnement `DEV`. Il n’autorise ni la création d’un corpus `OFFICIAL`, ni une exécution `OFFICIAL`, ni le gel définitif des paramètres expérimentaux.

---

# 1. Objet du protocole

`EXP-001-P3` étudie la capacité de SoiNesis à construire, consolider, réviser et utiliser causalement une représentation de certaines de ses propres capacités à partir de performances observées.

La propriété étudiée est strictement fonctionnelle :

```text
performances propres observées
→ estimation métacognitive
→ représentation consolidée dans le SelfModel
→ influence sur les décisions futures
```

`P3` doit distinguer quatre éléments qui ne sont pas interchangeables :

1. la performance brute observée ;
2. l’état statistique utilisé pour estimer la capacité ;
3. la représentation persistante consolidée dans le modèle de soi ;
4. la version logique globale du modèle de soi.

Le protocole compare cette architecture à une baseline fixe et à une reconstruction temporaire crédible depuis les mêmes observations brutes.

---

# 2. Portée scientifique et statut épistémique

`P3` porte sur une forme limitée de conscience fonctionnelle : la représentation opérationnelle de capacités propres et son influence causale sur la stratégie.

Même une réussite complète de `P3` ne démontrerait pas :

- une conscience phénoménale ;
- une expérience subjective ;
- un sentiment vécu de compétence ou d’incompétence ;
- une introspection phénoménale ;
- une capacité cognitive générale ;
- une identité consciente.

Les domaines `ALPHA`, `BETA` et `GAMMA` sont des capacités synthétiques contrôlées. Ils ne doivent pas être présentés comme de véritables capacités cognitives générales.

Les conclusions autorisées concernent uniquement des mécanismes observables, auditables, persistants et causalement testables.

---

# 3. Problème concret et questions de recherche

Un système peut adapter ponctuellement une décision à son historique sans posséder de modèle de soi persistant. Il peut également stocker un attribut de soi sans jamais l’utiliser causalement.

`P3` doit donc distinguer :

- une estimation fixe sans apprentissage ;
- une reconstruction temporaire depuis les performances brutes ;
- une représentation persistante et versionnée, produite par un mécanisme métacognitif ;
- l’effet causal réel de cette représentation sur les décisions futures.

La question principale est :

> SoiNesis peut-il construire et réviser une représentation persistante de certaines capacités propres à partir de ses performances intrinsèques, puis utiliser cette représentation pour adapter ses décisions ?

La question comparative propre à `H-P3-03` est :

> La représentation consolidée persistante du SelfModel et son mécanisme de révision apportent-ils une contribution fonctionnelle au-delà de la reconstruction temporaire depuis les mêmes observations brutes ?

Cette formulation interdit d’attribuer un éventuel avantage à la « persistance seule ». Le mécanisme étudié est l’ensemble fonctionnel constitué par la représentation consolidée, sa révision contrôlée et son utilisation causale.

---

# 4. Statut des décisions et paramètres

## 4.1 Décisions architecturales approuvées

La version 0.2 fixe pour l’implémentation DEV :

- la séparation entre vérité terrain, preuve brute, état métacognitif et SelfModel ;
- l’ordre causal d’un cycle ;
- les frontières d’accès des conditions A, B et C ;
- les comportements de `SELF-ABL` et `META-ABL` ;
- l’apprentissage depuis `intrinsic_success` uniquement ;
- le latent commun de correction ;
- le calcul analytique du regret par l’oracle ;
- l’interdiction de toute logique de phase dans le code cognitif testé ;
- la séparation stricte `DEV / VALIDATION / OFFICIAL`.

Toute modification ultérieure de ces décisions doit produire une nouvelle version explicite du protocole.

## 4.2 Paramètres de travail DEV non gelés

Restent à calibrer en `DEV` :

- `lambda` ;
- la règle exacte de `significant_self_revision` ;
- le poids minimal de preuve ;
- les règles d’`attribute_confidence` ;
- les seuils ou règles de `capability_status` ;
- une éventuelle hystérésis de révision ;
- les fenêtres d’analyse ;
- la taille future de réplication, dont `N = 30` n’est qu’un candidat.

Aucune valeur calibrée en DEV ne devient `OFFICIAL` par simple usage. Elle doit être validée puis gelée explicitement.

---

# 5. Architecture de la capacité expérimentale et de l’oracle

## 5.1 `ExperimentalCapabilityModule`

La capacité réelle appartient conceptuellement à un composant expérimental de SoiNesis nommé :

```text
ExperimentalCapabilityModule
```

Pour chaque domaine synthétique, ce composant possède une fiabilité réelle interne :

```text
true_success_probability
```

Cette valeur est privée.

Elle ne doit jamais être accessible à :

- `SelfModel` ;
- `SelfAttribute` ;
- l’état métacognitif ;
- l’estimateur cognitif ;
- la politique de décision ;
- les providers A, B ou C ;
- les mécanismes d’ablation ;
- toute trace publique fournie au décideur.

## 5.2 Deux façades séparées

Le banc expérimental doit exposer deux voies conceptuellement distinctes :

1. une façade d’exécution, qui produit un résultat intrinsèque sans révéler la probabilité réelle ;
2. une façade oracle, réservée à la génération contrôlée et à l’évaluation postérieure.

Seuls `ExperimentalCapabilityModule` et l’oracle expérimental peuvent lire `true_success_probability`.

L’oracle peut l’utiliser uniquement pour :

- générer ou vérifier les performances selon le plan expérimental privé ;
- calculer les métriques de vérité terrain ;
- calculer le regret analytique ;
- réaliser les contrôles d’intégrité du banc expérimental.

## 5.3 Confinement des phases

La logique de phase et les changements de probabilité sont autorisés uniquement dans :

- le plan expérimental privé ;
- `ExperimentalCapabilityModule` ;
- l’oracle et l’évaluateur post-hoc.

Ils sont strictement interdits dans :

- `SelfModel` ;
- la métacognition cognitive ;
- la politique de décision ;
- les providers A, B et C ;
- `SELF-ABL` et `META-ABL` ;
- toute règle de révision du SelfModel.

Le domaine courant peut être public. Le numéro de phase, le prochain changement de probabilité et toute connaissance du futur doivent rester privés.

---

# 6. Séparation stricte des objets

## 6.1 `CapabilityPerformanceObservation`

`CapabilityPerformanceObservation` représente une preuve brute immuable.

Elle doit pouvoir contenir conceptuellement :

- un identifiant ;
- l’agent concerné ;
- un identifiant opaque d’essai ;
- `capability_key` ;
- l’ordre ou le cycle public de l’observation ;
- `intrinsic_success` ;
- la date ;
- la provenance.

Elle ne doit pas contenir :

- `true_success_probability` ;
- le numéro de phase ;
- la graine expérimentale ;
- le numéro de réplication ;
- un identifiant de dataset `OFFICIAL` ;
- une annotation révélant un futur changement de capacité.

Le résultat intrinsèque doit rester distinguable du résultat final éventuellement corrigé.

## 6.2 `MetacognitiveCapabilityState`

`MetacognitiveCapabilityState` représente l’état statistique de travail du mécanisme métacognitif.

Il peut contenir :

- `alpha` ;
- `beta` ;
- `lambda` ;
- le poids de preuve ;
- la dernière preuve traitée ;
- les informations nécessaires à l’idempotence et au contrôle de concurrence.

Cet état n’est pas un `SelfAttribute`.

Il ne doit jamais être lu directement par la politique de décision.

## 6.3 `SelfAttribute` de type `CAPABILITY`

Le `SelfAttribute` représente la croyance consolidée et persistante de SoiNesis au sujet d’une capacité propre.

Il doit pouvoir représenter :

- `attribute_type = CAPABILITY` ;
- `capability_key` ;
- `estimated_success` ;
- `capability_status` ;
- `attribute_confidence` ;
- les preuves utilisées ;
- la provenance ;
- le cycle de création ;
- la version de l’attribut ;
- la version précédente ;
- la raison de révision ;
- son statut historique ou courant.

`alpha`, `beta` et `lambda` ne doivent pas être copiés dans le `SelfAttribute`.

`attribute_confidence` ne doit pas être confondue avec `estimated_success` ni avec la vérité terrain.

## 6.4 `SelfModelVersion`

`SelfModelVersion` représente une version globale logique du modèle de soi.

Elle doit permettre d’identifier :

- la version globale courante ;
- la version précédente ;
- les révisions d’attribut introduites à cette version ;
- la justification et la date de la version ;
- l’état historique complet consultable à cette version.

## 6.5 Invariant de séparation

Le flux autorisé est :

```text
CapabilityPerformanceObservation
→ MetacognitiveCapabilityState
→ candidat de révision significative
→ SelfAttribute CAPABILITY
→ SelfModelVersion
→ décision future
```

Aucun flux inverse vers la vérité terrain n’est autorisé.

---

# 7. Snapshot, versionnement et atomicité du SelfModel

Une microvariation statistique ne crée pas obligatoirement une nouvelle version importante du SelfModel.

Les mises à jour fréquentes de `MetacognitiveCapabilityState` peuvent rester internes tant qu’aucune révision significative n’est justifiée.

Lorsqu’une révision est significative, l’opération doit créer atomiquement :

1. un nouveau `SelfAttribute` ;
2. un lien vers le `SelfAttribute` précédent, lorsqu’il existe ;
3. une nouvelle `SelfModelVersion` ;
4. les liens vers les preuves ;
5. la provenance et la justification ;
6. un `JournalEvent` contenant les états précédent et nouveau.

Si une partie de cette opération échoue, aucune partie de la révision significative ne doit devenir visible.

L’historique doit être reconstructible sans :

- réécriture silencieuse ;
- modification en place d’une ancienne version ;
- perte de provenance ;
- remplacement d’un prédécesseur ;
- copie opaque empêchant l’audit.

La performance brute constitue un fait expérimental distinct. Elle doit pouvoir être enregistrée durablement avant le traitement métacognitif, afin qu’un blocage ou un échec de révision ne la fasse pas disparaître.

Le choix physique du schéma de snapshot peut être affiné pendant l’implémentation DEV, mais il doit préserver ces invariants logiques.

---

# 8. Ordre obligatoire d’un cycle

Pour chaque essai, l’ordre suivant est obligatoire :

```text
décision
→ tentative autonome
→ intrinsic_success
→ éventuelle correction VERIFY/HELP
→ final_success
→ apprentissage métacognitif à partir de intrinsic_success uniquement
```

## 8.1 Décision

La décision du cycle courant utilise uniquement l’état autorisé produit par les cycles antérieurs.

Elle ne doit pas dépendre :

- du résultat intrinsèque du cycle courant ;
- du résultat final du cycle courant ;
- de la phase privée ;
- de la probabilité réelle ;
- d’un événement futur.

## 8.2 Tentative autonome

La tentative autonome produit `intrinsic_success` selon la capacité réelle privée et le latent intrinsèque du cycle.

## 8.3 Correction et résultat final

Une correction peut transformer un échec intrinsèque en succès final selon l’action choisie et `u_correction`.

Elle ne modifie jamais rétroactivement `intrinsic_success`.

## 8.4 Apprentissage

Le mécanisme métacognitif reçoit exclusivement `intrinsic_success` comme variable de succès ou d’échec propre.

Apprendre depuis `final_success` confondrait capacité autonome et assistance stratégique et invaliderait l’expérience.

Toute révision issue du résultat courant ne peut influencer que les décisions futures.

---

# 9. Domaines synthétiques et phases privées

La configuration de travail DEV comprend trois domaines.

## 9.1 `ALPHA` — capacité stable

```text
Phase I   : 0.65
Phase II  : 0.65
Phase III : 0.65
```

## 9.2 `BETA` — dégradation

```text
Phase I   : 0.85
Phase II  : 0.40
Phase III : 0.40
```

## 9.3 `GAMMA` — amélioration

```text
Phase I   : 0.35
Phase II  : 0.75
Phase III : 0.75
```

Ces valeurs sont des paramètres du banc expérimental privé. Elles ne doivent apparaître dans aucun objet cognitif ou provider normal.

Elles constituent la configuration candidate de travail pour DEV, pas une configuration `OFFICIAL` gelée.

---

# 10. Conditions expérimentales

## 10.1 Condition A — baseline fixe

### Rôle

Contrôle sans apprentissage sur soi.

### Estimation

```text
estimated_success = 0.60
```

### Autorisé

- domaine courant ;
- règles communes de décision ;
- estimation fixe.

### Interdit pour décider

- historique brut ;
- état métacognitif ;
- SelfModel ;
- vérité terrain.

Les performances peuvent être enregistrées pour la parité et l’évaluation, mais A ne doit pas les lire pour décider.

## 10.2 Condition B — reconstruction depuis l’historique brut

### Rôle

Comparateur crédible sans représentation de soi persistante.

### Flux

```text
historique brut antérieur
→ estimation temporaire
→ décision
```

### Contraintes

B :

- utilise les observations brutes disponibles avant le cycle courant ;
- reconstruit l’estimation à chaque décision ;
- utilise le même estimateur générique que le mécanisme métacognitif de C ;
- ne persiste aucun état `alpha/beta/lambda` ;
- ne crée aucun `SelfAttribute` ;
- ne consulte aucun SelfModel ;
- ne conserve aucun cache équivalent à un SelfModel ;
- ne reçoit aucune vérité terrain ni information de phase.

B ne doit pas être volontairement affaibli.

## 10.3 Condition C — SelfModel causal et métacognition active

### Rôle

Condition expérimentale complète.

### Flux d’apprentissage

```text
performance brute
→ état métacognitif
→ éventuelle révision significative
→ SelfAttribute CAPABILITY
→ SelfModelVersion
```

### Flux de décision

```text
SelfAttribute courant
→ estimation consultée
→ décision
```

### Contraintes

C :

- possède les mêmes observations brutes que B ;
- peut les traiter après chaque résultat via le mécanisme métacognitif ;
- décide uniquement depuis le `SelfAttribute` courant ;
- ne reconstruit pas l’historique brut pendant la décision ;
- n’autorise pas le décideur à lire `alpha`, `beta` ou `lambda` ;
- conserve versions, preuves, provenance et journalisation ;
- ne reçoit aucune vérité terrain ni information de phase.

---

# 11. Matrice décisionnelle et d’accès

| Condition | Brut pour décider | État méta persistant | SelfModel pour décider | Révision SelfModel |
|---|---:|---:|---:|---:|
| A | non | non | non | non |
| B | oui, reconstruction | non | non | non |
| C | non | oui | oui | conditionnelle |
| `SELF-ABL` | oui, provider exact de B | non | non | non |
| `META-ABL` | non | aucune mise à jour | oui, version existante | non |

Dans toutes les conditions et ablations, les performances intrinsèques doivent continuer d’être produites et enregistrées selon le même protocole.

La matrice porte sur les accès cognitifs et décisionnels. L’évaluateur post-hoc conserve sa voie oracle séparée.

---

# 12. Actions, utilités et correction

## 12.1 Récompense et coûts

La récompense de résultat est :

```text
succès : +10
échec  : -10
```

Les actions possibles sont :

- `DIRECT`, coût `0` ;
- `VERIFY`, coût `2` ;
- `HELP`, coût `6`.

## 12.2 Utilités attendues

Pour une estimation `p` :

```text
U_DIRECT(p) = 20p - 10
U_VERIFY(p) = 10p - 2
U_HELP(p)   = 2p + 2
```

La politique commune doit appliquer :

```text
p < 0.50         → HELP
0.50 <= p < 0.80 → VERIFY
p >= 0.80        → DIRECT
```

Les égalités sont départagées selon ces bornes : `VERIFY` à `p = 0.50`, `DIRECT` à `p = 0.80`.

Toutes les conditions utilisent exactement les mêmes fonctions d’utilité et la même politique de décision.

## 12.3 Latent commun de correction

Chaque essai possède un latent privé commun :

```text
u_correction ∈ [0, 1)
```

Si `intrinsic_success = true`, alors `final_success = true` quelle que soit l’action.

Si `intrinsic_success = false` :

- `DIRECT` ne corrige pas et `final_success = false` ;
- `VERIFY` corrige si `u_correction < 0.50` ;
- `HELP` corrige si `u_correction < 0.90`.

Le même `u_correction` doit être utilisé pour les conditions appariées. Aucun nouveau tirage ne doit être effectué à cause d’une branche de décision.

Le succès final peut servir à calculer la récompense réalisée. Il ne doit jamais servir à mettre à jour l’estimation de la capacité autonome.

---

# 13. Mise à jour métacognitive et révision significative

## 13.1 Prior de travail DEV

Le prior candidat est :

```text
alpha0 = 3
beta0  = 2
```

Sa moyenne initiale est :

```text
alpha0 / (alpha0 + beta0) = 0.60
```

## 13.2 Mise à jour candidate

Pour `y = 1` en cas de succès intrinsèque et `y = 0` en cas d’échec intrinsèque :

```text
alpha_t = alpha0 + lambda × (alpha_(t-1) - alpha0) + y
beta_t  = beta0  + lambda × (beta_(t-1)  - beta0)  + (1 - y)
```

L’estimation statistique candidate est :

```text
p_hat = alpha_t / (alpha_t + beta_t)
```

La grille DEV candidate de `lambda` est :

```text
0.90
0.92
0.94
0.95
0.96
0.97
```

Ces valeurs ne sont pas `OFFICIAL`.

## 13.3 Estimateur commun

B et C doivent partager la même définition mathématique de l’estimateur :

- B la rejoue depuis l’historique brut à chaque décision ;
- C la met à jour dans `MetacognitiveCapabilityState` après chaque performance.

À historique identique et paramètres identiques, le replay complet et les mises à jour successives doivent produire le même état statistique avant consolidation.

## 13.4 `significant_self_revision`

La règle exacte doit être calibrée en DEV.

Elle peut considérer notamment :

- l’ampleur du changement estimé ;
- le franchissement naturel d’une zone décisionnelle ;
- le poids de preuve ;
- la confiance ;
- une hystérésis contre les oscillations.

Elle ne doit jamais considérer :

- `true_success_probability` ;
- le numéro de phase ;
- une graine particulière ;
- un numéro précis d’observation ;
- le prochain changement programmé de capacité ;
- un résultat futur.

Une microvariation ne doit pas créer mécaniquement un nouveau snapshot. Une révision significative doit cependant être persistée, versionnée, justifiée et journalisée selon la section 7.

---

# 14. Hypothèses

## 14.1 `H-P3-01` — calibration du modèle de soi

Le SelfModel construit et adapte correctement une estimation de certaines capacités propres à partir des performances intrinsèques.

La métrique primaire prévue est :

```text
MAE(estimated_success, true_success_probability)
```

La vérité terrain est jointe uniquement par l’évaluateur oracle.

## 14.2 `H-P3-02` — causalité naturelle sur les décisions

Les changements naturellement appris du SelfModel influencent causalement les décisions futures.

La chaîne principale attendue est :

```text
performances
→ révision naturelle du SelfModel
→ franchissement d’une zone décisionnelle
→ modification de stratégie future
```

Une corruption artificielle ne constitue pas la preuve principale. Elle n’est qu’un contrôle interventionnel supplémentaire.

## 14.3 `H-P3-03` — contribution au-delà de la reconstruction brute

La formulation correcte est :

> La représentation consolidée persistante du SelfModel et son mécanisme de révision apportent-ils une contribution fonctionnelle au-delà de la reconstruction temporaire depuis les mêmes observations brutes ?

`H-P3-03` ne teste pas la persistance isolée.

Si la reconstruction temporaire depuis le brut compense entièrement l’ablation du SelfModel :

```text
H-P3-03 = NOT_SUPPORTED
```

Ce résultat est scientifiquement acceptable.

## 14.4 `H-P3-04` — contribution de la mise à jour métacognitive

Lorsque le mécanisme métacognitif est ablaté :

- les nouvelles performances continuent d’exister ;
- elles continuent d’être enregistrées ;
- le SelfModel existant reste disponible pour décider ;
- sa mise à jour métacognitive est bloquée ;
- aucun nouveau `SelfAttribute` ne doit résulter de cette métacognition bloquée.

La chaîne étudiée est :

```text
META-ABL
→ SelfModel plus obsolète
→ décisions moins adaptées
```

Les deux conséquences sont nécessaires pour soutenir `H-P3-04` :

1. une augmentation de l’erreur du SelfModel ;
2. une augmentation du regret décisionnel.

---

# 15. Ablations et intervention causale

## 15.1 `SELF-ABL`

Pendant `SELF-ABL` :

### Toujours disponible

- historique brut des performances ;
- domaine courant ;
- cycles antérieurs ;
- succès et échecs intrinsèques ;
- règles générales communes ;
- estimateur générique commun.

### Obligatoire

- utiliser exactement le même provider de reconstruction que B ;
- reconstruire temporairement depuis le même historique brut ;
- tracer les preuves consultées.

### Interdit

- lecture ou écriture de `SelfAttribute` ;
- lecture ou écriture de `SelfModelVersion` ;
- lecture ou écriture de `MetacognitiveCapabilityState` ;
- cache équivalent ;
- copie cachée d’une estimation consolidée ;
- vérité terrain.

## 15.2 `META-ABL`

Pendant `META-ABL` :

- les performances intrinsèques sont toujours enregistrées ;
- le SelfModel existant reste lisible et causalement utilisé pour décider ;
- aucune mise à jour de `MetacognitiveCapabilityState` n’est autorisée ;
- aucun nouveau `SelfAttribute` issu de la métacognition n’est autorisé ;
- aucune nouvelle `SelfModelVersion` issue de cette voie n’est autorisée ;
- aucune reconstruction brute de secours n’est autorisée pour la décision ;
- aucun rattrapage caché ne doit avoir lieu pendant l’ablation.

Les tentatives de mise à jour doivent être bloquées et comptabilisées de manière auditable.

## 15.3 T4-B — intervention temporaire

La corruption temporaire constitue un contrôle interventionnel secondaire.

Elle doit vérifier :

- la direction attendue du changement de décision ;
- la spécificité au domaine ciblé ;
- l’absence d’effet sur les autres domaines ;
- la réversibilité après retrait ;
- l’absence de mutation persistante du SelfModel.

T4-B ne remplace jamais la preuve naturelle T4-A.

---

# 16. Structure temporelle, randomisation et appariement

## 16.1 Structure candidate par réplication

```text
180 cycles
3 phases privées de 60 cycles
20 observations ALPHA par phase
20 observations BETA par phase
20 observations GAMMA par phase
```

L’ordre doit être pseudo-aléatoire et équilibré à l’intérieur de chaque phase privée.

Le contrôleur et les mécanismes cognitifs peuvent recevoir le domaine et l’ordre des observations passées. Ils ne doivent jamais recevoir le numéro de phase.

## 16.2 Plan latent privé

Avant l’exécution appariée, le banc expérimental peut préparer un plan immuable contenant notamment :

- l’ordre des domaines ;
- les latents intrinsèques ;
- `u_correction` ;
- les informations privées nécessaires à l’oracle.

Ce plan ne doit pas être transmis au contrôleur.

## 16.3 Appariement des conditions

Pour une même réplication et un même cycle, A, B, C et les conditions d’ablation doivent utiliser :

- le même domaine ;
- le même latent intrinsèque ;
- le même `u_correction` ;
- la même chronologie publique ;
- les mêmes observations intrinsèques lorsque l’action n’affecte pas la tentative autonome.

La randomisation ne doit pas être consommée séquentiellement selon les branches d’action. Les latents doivent être indexés par essai.

La graine peut être conservée dans les métadonnées expérimentales privées pour la reproductibilité. Elle ne doit pas être accessible au code cognitif testé ni déclencher une règle particulière.

## 16.4 Réplications

Le nombre futur candidat de réplications `OFFICIAL` est :

```text
N = 30
```

Cette valeur n’est pas gelée. DEV doit évaluer si elle est raisonnable avant toute décision de validation ou d’exécution officielle.

---

# 17. Essais prévus

## 17.1 T1 — calibration

Mesurer l’erreur entre `estimated_success` et `true_success_probability` par domaine, période et réplication.

Métrique primaire : `MAE`.

## 17.2 T2 — adaptation

Mesurer :

- l’adaptation descendante de BETA ;
- l’adaptation ascendante de GAMMA ;
- le délai et l’amplitude de la réponse après changement privé de capacité.

## 17.3 T3 — stabilité

Mesurer sur ALPHA :

- la variance de l’estimation ;
- les oscillations de décision ;
- le nombre de révisions significatives ;
- la résistance au bruit.

T3 est secondaire.

## 17.4 T4-A — causalité naturelle

Identifier une chaîne observée et auditée :

```text
preuves intrinsèques
→ révision significative naturelle
→ nouvelle version consultée
→ franchissement de zone
→ changement de stratégie future
```

La révision ne doit pas être déclenchée par un numéro de phase ou de cycle prédéfini.

## 17.5 T4-B — corruption temporaire

Appliquer le contrôle interventionnel décrit en section 15.3 sans modifier la persistance.

## 17.6 T5 — ablation équitable du SelfModel

Comparer C et `SELF-ABL` avec les mêmes observations brutes et le provider de reconstruction exact de B.

Métrique primaire : différence appariée de regret.

## 17.7 T6 — ablation métacognitive longitudinale

Comparer C et `META-ABL` sur :

1. l’erreur du SelfModel ;
2. le regret décisionnel.

Une seule dégradation ne suffit pas à soutenir `H-P3-04`.

## 17.8 T7 — comparaison B/C

Comparer secondairement la reconstruction brute temporaire et le SelfModel consolidé complet.

Une égalité B/C est un résultat recevable.

---

# 18. Variables

## 18.1 Variables indépendantes principales

- condition A, B ou C ;
- activation de `SELF-ABL` ;
- activation de `META-ABL` ;
- domaine synthétique ;
- évolution privée de la capacité réelle.

## 18.2 Variables de calibration DEV

- `lambda` ;
- règle de révision significative ;
- poids minimal de preuve ;
- confiance et statuts ;
- hystérésis ;
- taille de réplication candidate.

## 18.3 Variables dépendantes

- erreur absolue d’estimation ;
- action choisie ;
- utilité attendue ;
- regret analytique ;
- récompense réalisée ;
- délai d’adaptation ;
- nombre de révisions ;
- accès aux sources autorisées et interdites.

## 18.4 Variables contrôlées

Entre conditions appariées doivent rester identiques :

- ordre des domaines ;
- latents intrinsèques ;
- `u_correction` ;
- prior et `lambda` lorsque comparables ;
- estimateur générique ;
- politique de décision ;
- fonctions d’utilité ;
- observations brutes disponibles ;
- budget temporel et informationnel ;
- définition des métriques.

---

# 19. Métriques et regret

## 19.1 Erreur d’estimation

La métrique primaire de calibration est :

```text
MAE = moyenne(|estimated_success - true_success_probability|)
```

Elle doit être calculée par l’évaluateur post-hoc après jointure avec la vérité terrain.

## 19.2 Adaptation et stabilité

Les métriques secondaires peuvent inclure :

- erreur avant et après changement ;
- délai avant franchissement d’une zone décisionnelle ;
- aire d’erreur après changement ;
- variance sur ALPHA ;
- nombre de révisions ;
- fréquence d’oscillation entre actions.

Les définitions exactes doivent être fixées après calibration DEV et avant VALIDATION.

## 19.3 Regret analytique

Pour une probabilité réelle privée `p_true`, l’oracle calcule :

```text
regret = max_a U_a(p_true) - U_action_choisie(p_true)
```

Le regret est calculé analytiquement à partir :

- de `true_success_probability` ;
- des mêmes fonctions d’utilité que la politique normale ;
- de l’action effectivement choisie.

Il est indépendant du succès ou de l’échec aléatoire effectivement obtenu au cycle considéré.

Un résultat chanceux ne transforme donc pas une décision sous-optimale en décision sans regret. Inversement, un échec malchanceux n’augmente pas le regret d’une action analytiquement optimale.

## 19.4 Comparaisons appariées

Les contrastes principaux de regret doivent être calculés à l’intérieur d’une même réplication et sur les mêmes essais latents avant agrégation.

---

# 20. Audit et traces causales

Le protocole doit permettre de compter et auditer au minimum :

- lectures de l’historique brut ;
- lectures et écritures de `MetacognitiveCapabilityState` ;
- lectures et écritures de `SelfAttribute` et `SelfModelVersion` ;
- tentatives de mise à jour métacognitive ;
- mises à jour appliquées ;
- mises à jour bloquées par `META-ABL` ;
- lectures de l’oracle, avec le rôle appelant ;
- identifiants de preuves consultées ;
- identifiant et version du `SelfAttribute` consulté ;
- source de l’estimation : fixe, brut reconstruit ou SelfModel ;
- utilités calculées et action choisie ;
- création de versions et événements de journal.

Une trace décisionnelle doit permettre de relier :

```text
état autorisé consulté
→ estimation
→ utilités
→ action
```

Une trace de révision doit permettre de relier :

```text
performances intrinsèques
→ mise à jour métacognitive
→ décision de révision
→ SelfAttribute précédent
→ SelfAttribute nouveau
→ SelfModelVersion
→ JournalEvent
```

L’audit doit également vérifier :

- l’absence de champs privés dans les objets cognitifs ;
- la parité des latents entre conditions ;
- l’absence de cache équivalent ;
- l’absence de lecture SQL ou de contournement non instrumenté ;
- l’absence de mutation persistante lors de T4-B.

---

# 21. Équité entre B, C et les ablations

B doit rester un comparateur crédible.

À information brute identique :

- B et C utilisent la même définition de l’estimateur ;
- B rejoue cet estimateur depuis le brut ;
- C l’utilise dans le mécanisme métacognitif, puis décide depuis le SelfAttribute consolidé ;
- `SELF-ABL` utilise le provider exact de B ;
- toutes les conditions utilisent la même politique de décision ;
- aucune condition ne reçoit de vérité ou de futur supplémentaire.

Les différences intentionnelles entre B et C sont limitées à :

- l’existence d’un état métacognitif persistant ;
- la consolidation dans le SelfModel ;
- le versionnement ;
- la provenance et le journal ;
- les conséquences fonctionnelles de la représentation consolidée.

Il est interdit :

- d’empêcher B ou `SELF-ABL` de reconstruire une estimation autorisée ;
- de donner à C une observation brute supplémentaire ;
- de faire varier la formule statistique entre B et C ;
- de comparer des conditions utilisant des latents différents ;
- d’interpréter toute différence comme un effet de la persistance isolée.

---

# 22. Procédure DEV

La future procédure DEV devra suivre l’ordre général suivant.

## Étape 1 — Sélection explicite du niveau DEV

Le run doit porter un niveau de données et d’exécution explicite `DEV`.

Toute demande `OFFICIAL` doit être refusée tant que le présent protocole n’a pas franchi les étapes de calibration, validation et gel.

## Étape 2 — Configuration de travail

Enregistrer :

- version du protocole ;
- paramètres DEV ;
- version du code ;
- règle de révision testée ;
- configuration des conditions et ablations ;
- identifiant de plan DEV.

## Étape 3 — Création du plan expérimental privé

Créer l’ordre équilibré et les latents indexés sans les exposer au code cognitif.

## Étape 4 — Initialisation isolée des conditions

Chaque condition doit posséder son propre état persistant ou absence d’état selon la matrice, sans partage de cache ni repository mutable.

## Étape 5 — Exécution online

Livrer un seul essai public à la fois et appliquer strictement l’ordre de la section 8.

Le futur du flux ne doit jamais être transmis aux providers ou au contrôleur.

## Étape 6 — Audits continus

Enregistrer les compteurs d’accès, les traces décisionnelles, les révisions et les blocages d’ablation.

## Étape 7 — Contrôles causaux

Exécuter T4-A sur les révisions naturelles et T4-B comme intervention temporaire séparée.

## Étape 8 — Évaluation post-hoc

L’évaluateur oracle joint la vérité aux traces uniquement après les décisions.

## Étape 9 — Analyse DEV

Calculer T1 à T7, comparer les paramètres candidats et documenter les résultats négatifs autant que les résultats favorables.

Cette procédure ne doit produire aucun artefact `OFFICIAL`.

---

# 23. Données à enregistrer

## 23.1 Trace cognitive sans oracle

Pour chaque décision :

- identifiant opaque d’essai ;
- domaine ;
- condition ;
- ablation active ;
- source de l’estimation ;
- `estimated_success` ;
- identifiant/version du SelfAttribute, si autorisé ;
- identifiants des preuves brutes, si autorisés ;
- utilités calculées ;
- action choisie ;
- compteurs d’accès pertinents.

## 23.2 Trace de résultat

- `intrinsic_success` ;
- `u_correction` dans la trace expérimentale privée ;
- application ou non d’une correction ;
- `final_success` ;
- récompense réalisée ;
- preuve brute créée.

## 23.3 Trace métacognitive et SelfModel

- état précédent et nouvel état statistique, si autorisés ;
- preuve traitée ;
- mise à jour tentée, appliquée ou bloquée ;
- décision de révision significative ;
- versions précédente et nouvelle ;
- justification ;
- événement de journal.

## 23.4 Extension oracle post-hoc

L’évaluateur peut ajouter dans un objet séparé :

- phase privée ;
- `true_success_probability` ;
- action oracle optimale ;
- regret analytique ;
- métriques de calibration.

Ces champs ne doivent jamais être réinjectés dans le flux cognitif.

---

# 24. Analyse DEV et évaluation de `N = 30`

L’analyse DEV doit :

1. calculer les métriques par domaine, période privée et réplication ;
2. utiliser des différences appariées pour T5 et T6 ;
3. examiner séparément erreur d’estimation et regret ;
4. mesurer stabilité et fréquence de révision ;
5. comparer la grille de `lambda` selon des critères déclarés ;
6. analyser la sensibilité aux règles candidates de révision ;
7. rechercher activement les résultats nuls ou inverses ;
8. estimer la variabilité des contrastes principaux.

Pour examiner `N = 30`, DEV peut utiliser des simulations et réplications DEV indépendantes afin d’estimer notamment :

- la largeur attendue des intervalles ;
- la stabilité des moyennes appariées ;
- la sensibilité à des effets plausibles ;
- le risque qu’un petit nombre de plans latents domine le résultat.

DEV ne doit pas sélectionner une graine ou un sous-ensemble de réplications parce qu’il produit un résultat favorable.

La décision sur `N` doit être prise avant VALIDATION, documentée, puis gelée avant toute conception `OFFICIAL`.

---

# 25. Critères de soutien, réfutation et résultat partiel

## 25.1 `H-P3-01`

Soutien si le SelfModel suit les niveaux et changements de capacité avec une erreur et une dynamique compatibles avec les critères gelés après DEV.

Affaiblissement ou réfutation si l’estimation reste durablement mal calibrée, instable ou insensible aux changements.

## 25.2 `H-P3-02`

Soutien uniquement si une chaîne naturelle auditée relie preuves, révision, version consultée et changement de décision future.

Une réussite de T4-B sans réussite de T4-A ne suffit pas.

## 25.3 `H-P3-03`

Soutien si C présente un avantage fonctionnel robuste sur `SELF-ABL`, à observations brutes, estimateur, politique de décision et latents comparables.

Si `SELF-ABL` reconstruit une estimation équivalente et compense entièrement l’absence de SelfModel :

```text
H-P3-03 = NOT_SUPPORTED
```

Ce résultat ne constitue ni une invalidation technique ni une raison d’affaiblir B.

## 25.4 `H-P3-04`

Soutien uniquement si `META-ABL` produit simultanément :

1. un SelfModel plus erroné ou plus obsolète ;
2. un regret décisionnel plus élevé.

Une différence sur un seul critère produit au mieux un résultat partiel.

## 25.5 Résultat global partiel

Les hypothèses sont indépendantes. `P3` peut soutenir certaines hypothèses et en laisser d’autres non soutenues.

Aucun score composite ne doit masquer cette distinction.

---

# 26. Critères d’invalidation d’un run

Un run doit être invalidé au minimum si :

- le SelfModel, la métacognition ou la décision lit `true_success_probability` ;
- une condition cognitive accède au numéro de phase ;
- une règle dépend d’un numéro précis de dataset, réplication, graine ou observation ;
- le futur du flux est chargé ou exposé au contrôleur ;
- les conditions appariées n’utilisent pas les mêmes latents ;
- un RNG est consommé différemment selon les branches ;
- l’apprentissage utilise `final_success` au lieu de `intrinsic_success` ;
- C reconstruit le brut pendant la décision ;
- le décideur de C lit directement `alpha`, `beta` ou `lambda` ;
- `SELF-ABL` utilise un provider différent de B ;
- `SELF-ABL` lit un SelfModel, un état méta ou un cache équivalent ;
- `META-ABL` met à jour l’état méta ou crée un nouvel attribut issu de cette voie ;
- une révision significative n’est pas atomique ;
- une ancienne version est réécrite silencieusement ;
- l’oracle participe à la décision normale ;
- une donnée `OFFICIAL` est chargée en DEV ou utilisée pour calibrer ;
- les compteurs d’accès sont incomplets ou contournables ;
- l’intégrité ou la provenance des traces ne peut pas être établie.

Une invalidation doit être documentée. Le run invalidé ne doit pas être inclus silencieusement dans l’analyse.

---

# 27. Séparation `DEV / VALIDATION / OFFICIAL`

## 27.1 DEV

DEV sert à :

- implémenter les mécanismes ;
- déboguer ;
- calibrer `lambda` ;
- calibrer la règle de révision ;
- définir confiance, statuts et hystérésis ;
- vérifier les audits et ablations ;
- évaluer la taille de réplication ;
- analyser les risques méthodologiques.

Les plans et données DEV doivent être identifiés comme tels et générés indépendamment de tout corpus officiel.

## 27.2 VALIDATION

VALIDATION sert à éprouver une configuration sélectionnée après DEV sur des plans distincts.

Pendant VALIDATION :

- les paramètres candidats doivent être gelés pour le run ;
- les données ne doivent pas servir à poursuivre implicitement la calibration ;
- toute modification doit être documentée et renvoyer à DEV ;
- aucun corpus OFFICIAL ne doit encore être consulté.

## 27.3 OFFICIAL

OFFICIAL est interdit au statut actuel du protocole.

Avant toute autorisation future, il faudra au minimum :

- terminer la calibration DEV ;
- réaliser une validation indépendante ;
- geler les paramètres, métriques et critères ;
- geler la version du code et du protocole ;
- préenregistrer le nombre de réplications et le plan d’analyse ;
- vérifier les protections contre les fuites ;
- obtenir une décision explicite autorisant la création du corpus officiel.

Le présent document ne crée ni ne définit un corpus OFFICIAL concret.

---

# 28. Protection contre la contamination méthodologique

La séparation des niveaux doit être technique et pas seulement déclarative.

Le futur système devra garantir que :

- chaque plan ou artefact porte explicitement son niveau ;
- un loader DEV refuse un artefact OFFICIAL ;
- les tests unitaires et d’intégration ne chargent jamais un corpus OFFICIAL ;
- les fixtures de tests sont construites indépendamment ;
- `lambda` n’est jamais choisi depuis un résultat OFFICIAL ;
- les seuils ne sont jamais définis depuis un résultat OFFICIAL ;
- un corpus OFFICIAL n’est jamais utilisé pour déboguer ;
- un résultat VALIDATION ne devient pas silencieusement une nouvelle source de calibration ;
- les chemins et imports P1/P2 officiels restent hors du développement P3.

Les données, protocoles, résultats et runners gelés de `EXP-001-P1` et `EXP-001-P2` ne doivent être ni modifiés ni réexécutés dans le cadre de P3.

Au statut actuel, il est explicitement interdit de créer :

- un dataset P3 `OFFICIAL` ;
- un runner `exp_001_p3_official.py` ;
- un manifeste officiel P3 ;
- un résultat officiel P3 ;
- un chemin de test dépendant d’un futur corpus officiel.

---

# 29. Résultats négatifs possibles

## 29.1 B égale ou dépasse C

La reconstruction temporaire peut être aussi performante que le SelfModel consolidé, voire meilleure si la consolidation introduit du retard.

Ce résultat affaiblirait ou laisserait non soutenue `H-P3-03`. Il ne justifierait pas d’affaiblir B.

## 29.2 SelfModel calibré mais sans effet décisionnel

Le SelfModel peut estimer correctement les capacités sans modifier les actions.

Ce résultat pourrait soutenir partiellement `H-P3-01` mais pas `H-P3-02`.

## 29.3 Effet décisionnel sans calibration suffisante

Des décisions peuvent changer sans que l’estimation soit fiable.

Une simple variation d’action ne suffit pas à valider le mécanisme.

## 29.4 Ablation métacognitive sans double dégradation

`META-ABL` peut rendre le SelfModel plus obsolète sans augmenter le regret, ou augmenter le regret sans différence claire d’erreur.

Dans les deux cas, `H-P3-04` n’est pas pleinement soutenue.

## 29.5 Révisions trop fréquentes ou trop rares

Une politique peut osciller au bruit ou rester trop longtemps figée. DEV doit documenter ce compromis sans sélectionner a posteriori uniquement les runs favorables.

## 29.6 `N = 30` inadéquat

DEV peut conclure que 30 réplications seraient insuffisantes, excessives ou mal réparties. Le nombre futur doit alors être révisé avant gel, sans créer de corpus officiel.

---

# 30. Risques techniques et scientifiques

## 30.1 SelfModel décoratif

Risque : C calcule une représentation persistante mais décide depuis le brut ou l’état statistique.

Protection : la trace de décision doit identifier le `SelfAttribute` effectivement consulté et interdire les autres accès.

## 30.2 Copie cachée

Risque : une ablation conserve un cache, résumé ou état statistique équivalent.

Protection : instrumentation des ports, absence d’état méta sous `SELF-ABL` et reconstruction exacte par le provider B.

## 30.3 Circularité

Risque : l’estimateur ou la règle de révision utilise la vérité, la phase ou le changement futur.

Protection : séparation des façades et audit des champs transmis.

## 30.4 Divergence B/C

Risque : des différences de formule, ordre, prior ou budget rendent la comparaison injuste.

Protection : estimateur et politique de décision communs, latents et observations appariés.

## 30.5 Apprentissage de l’assistance

Risque : HELP ou VERIFY améliore `final_success`, que le système interprète ensuite comme sa capacité autonome.

Protection : seule la preuve `intrinsic_success` est admise par le mécanisme métacognitif.

## 30.6 Versionnement incohérent

Risque : chaque microvariation produit une version, ou une ancienne version est modifiée en place.

Protection : séparation état statistique/snapshot et transaction de révision significative.

## 30.7 Fuite du futur

Risque : le runner précharge le flux et transmet indirectement les phases ou résultats futurs.

Protection : exécution online, un essai public à la fois, avec lecture historique bornée au passé.

## 30.8 Surajustement DEV

Risque : choisir `lambda`, seuils ou règles parce qu’ils maximisent un scénario particulier.

Protection : critères de calibration déclarés, plans DEV multiples, validation indépendante et gel avant OFFICIAL.

## 30.9 Surinterprétation

Risque : présenter une adaptation synthétique comme une preuve de conscience phénoménale ou de compétence générale.

Protection : limiter les conclusions aux propriétés fonctionnelles testées.

---

# 31. Ce que P3 ne teste pas

`P3` ne teste pas directement :

- la conscience phénoménale ;
- la subjectivité ;
- l’expérience vécue d’une capacité ;
- une théorie générale de l’introspection ;
- des capacités cognitives réelles non synthétiques ;
- la mémoire autobiographique dans toute sa généralité ;
- la vérité de déclarations verbales sur soi ;
- la sécurité complète d’un agent autonome ;
- la généralisation à des environnements ouverts ;
- une supériorité intrinsèque de toute persistance.

`P3` teste une question plus étroite : la construction, la révision et l’usage causal d’une représentation consolidée de capacités synthétiques propres.

---

# 32. Frontières de la future implémentation DEV

La future implémentation devra respecter l’architecture générale de SoiNesis :

- objets de domaine indépendants du runner ;
- services applicatifs sans accès oracle ;
- ports explicites ;
- persistance auditée ;
- transactions limitées et atomiques ;
- modules expérimentaux séparés du mécanisme cognitif ;
- analyse post-hoc séparée de la décision.

La logique P3 ne doit pas être concentrée dans un runner monolithique.

Le SelfModel doit être un mécanisme du cœur de SoiNesis, pas une structure parallèle propre à l’expérience.

Les paramètres non triviaux doivent être nommés et versionnés. Aucune dépendance nouvelle ne doit être introduite sans nécessité démontrée.

Le statut « approuvé pour implémentation DEV » permet une future tranche de développement séparément demandée. Il n’autorise pas, dans la présente étape documentaire, la création de code, tests, datasets ou runners P3.

---

# 33. Critères avant passage à VALIDATION ou OFFICIAL

## 33.1 Avant VALIDATION

Il faudra au minimum :

- implémenter les frontières d’accès ;
- vérifier les invariants de séparation ;
- démontrer l’équivalence statistique replay/incrémental ;
- vérifier les transactions et l’historique ;
- vérifier les ablations par compteurs ;
- calibrer les paramètres DEV ;
- arrêter une règle de révision ;
- arrêter les métriques et fenêtres ;
- documenter les résultats négatifs ;
- préparer des plans VALIDATION indépendants.

## 33.2 Avant toute conception OFFICIAL

Il faudra en plus :

- terminer VALIDATION sans réutiliser ses données pour une calibration cachée ;
- résoudre toute déviation méthodologique ;
- figer le protocole final ;
- figer le code ;
- figer les paramètres ;
- figer le nombre de réplications ;
- figer le plan d’analyse ;
- auditer l’absence de fuite ;
- obtenir une autorisation explicite distincte.

Tant que ces critères ne sont pas satisfaits, `OFFICIAL` reste interdit.

---

# 34. Décision et conclusion du protocole

La conception `EXP-001-P3` version 0.2 est approuvée pour commencer ultérieurement l’implémentation et la calibration `DEV` dans les limites du présent protocole.

Les principes centraux sont :

1. la vérité terrain reste privée dans le banc expérimental et l’oracle ;
2. preuve brute, état métacognitif, SelfAttribute et SelfModelVersion restent distincts ;
3. les révisions significatives sont versionnées, justifiées, historisées et atomiques ;
4. l’apprentissage utilise uniquement la performance intrinsèque ;
5. B et `SELF-ABL` disposent d’une reconstruction brute crédible et identique ;
6. C décide uniquement depuis le SelfAttribute ;
7. `META-ABL` conserve les performances et le SelfModel existant tout en bloquant sa mise à jour ;
8. le regret est calculé analytiquement par l’oracle ;
9. les phases et changements réels restent hors du code cognitif ;
10. `DEV`, `VALIDATION` et `OFFICIAL` restent strictement séparés.

Une compensation complète par la reconstruction brute, une absence d’effet causal ou une ablation sans double dégradation sont des résultats recevables et doivent être rapportés sans affaiblissement rétroactif des comparateurs.

Au statut actuel :

```text
Implémentation DEV future : autorisée
Calibration DEV           : autorisée
VALIDATION                 : non encore autorisée
Création corpus OFFICIAL   : interdite
Exécution OFFICIAL         : interdite
```
