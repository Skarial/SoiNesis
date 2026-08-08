# SoiNesis — Rapport officiel EXP-001-P2

**Fichier :** `docs/17-rapport-exp-001-p2.md`  
**Date du run officiel :** 7 août 2026  
**Date du rapport :** 8 août 2026  
**Expérience :** `EXP-001-P2`  
**Version du protocole :** 0.1  
**Titre :** Contradictions, révision et continuité des croyances  
**Statut :** expérience officielle exécutée — résultats figés et interprétés  
**Commit de code figé :** `e2a1483910541a0ca3d1d82456d0a26c5ac58e25`

**Documents associés :**

- `docs/15-protocole-exp-001-p2.md`
- `docs/16-note-deviation-exp-001-p2.md`
- `data/exp-001-p2/datasets-v1.json`

---

# 1. Objet du rapport

Ce document consigne les résultats de la première campagne officielle de `EXP-001-P2`.

L’objectif de P2 était de tester si une mémoire autobiographique structurée représentant explicitement les versions, statuts, relations de révision, provenance et ordre temporel apporte un avantage reproductible par rapport à un historique textuel simple contenant les mêmes événements utiles.

P2 étudiait notamment :

- l’identification de l’état actuel d’une croyance ;
- la continuité historique ;
- la gestion des contradictions non résolues ;
- la traçabilité des révisions ;
- la résistance à une réécriture trompeuse ;
- le rôle causal des métadonnées structurées de révision par ablation ciblée.

Le protocole préenregistré précise qu’un résultat `B = C` est un résultat négatif comparatif acceptable et qu’aucun seuil ne doit être modifié après observation des résultats.

---

# 2. Conditions expérimentales

Les trois conditions prévues par le protocole ont été conservées.

## 2.1 Condition A — aucune mémoire persistante

Contrôle négatif sans accès à l’historique des cycles antérieurs.

## 2.2 Condition B — historique textuel simple

B conserve les mêmes événements sémantiques externes que C sous forme d’un historique textuel chronologique naturel, avec contenu, provenance et ordre.

B ne reçoit pas les métadonnées machine spécifiques à la représentation structurée de C.

## 2.3 Condition C — mémoire autobiographique structurée révisable

C représente explicitement les versions d’une croyance, leurs statuts, leurs relations de révision, leur provenance, leur ordre temporel et les raisons de transition.

Les statuts fonctionnels principaux testés sont :

- `ACTIVE` ;
- `CONTESTED` ;
- `SUPERSEDED`.

Une révision ne réécrit pas silencieusement l’ancienne version : l’histoire demeure persistée et consultable.

---

# 3. Gel expérimental

Le run officiel a été exécuté depuis `main`, sur le commit :

```text
e2a1483910541a0ca3d1d82456d0a26c5ac58e25
```

Le corpus officiel figé est :

```text
data/exp-001-p2/datasets-v1.json
```

Empreinte SHA-256 préenregistrée du corpus :

```text
ffe17b73f8072e38358ccfc3aefce0f0a36ad8e67f696172a88fbed1ffcbb2cd
```

La campagne comprend les cinq jeux de données officiels prévus par le protocole et les 60 chaînes de croyance correspondantes.

Avant le run, les garde-fous ont vérifié notamment :

- branche `main` ;
- arbre Git propre ;
- `HEAD == origin/main` ;
- correspondance avec la référence `main` réellement publiée sur le dépôt distant ;
- corpus officiel intact ;
- répertoire de sortie inexistant ;
- confirmation humaine exacte.

---

# 4. Déviation méthodologique préexistante

La déviation documentée dans `docs/16-note-deviation-exp-001-p2.md` reste attachée au présent rapport.

Pendant le développement de la couche d’export, une ancienne version d’un test automatisé avait exécuté techniquement le premier jeu du corpus officiel dans un répertoire temporaire `pytest`.

Cette exécution :

- n’était pas une campagne officielle ;
- utilisait un faux identifiant de commit de test ;
- n’était pas lancée par le garde-fou officiel ;
- n’a produit aucun bundle officiel ;
- n’a produit aucun rapport scientifique officiel ;
- n’a entraîné aucune modification des seuils du protocole.

La correction a été appliquée avant le run officiel : les tests exécutables utilisent désormais des fixtures de développement distinctes.

**Certain :** cette déviation de séparation développement/officiel a eu lieu et a été documentée avant le run officiel.

**Possible :** l’exposition technique au premier jeu officiel représente une source de biais méthodologique faible mais non nulle.

**Inconnu :** il n’est pas possible de démontrer qu’elle n’a eu absolument aucun effet indirect sur le développement ultérieur.

Cette limite doit rester visible dans toute interprétation ou réplication future.

---

# 5. Artefacts officiels et intégrité

Le run officiel a produit un bundle brut contenant :

```text
freeze-manifest.json
preevaluation.json
raw-trials.jsonl
checksums.json
```

Les empreintes enregistrées dans `checksums.json` sont :

| Artefact | SHA-256 |
|---|---|
| `freeze-manifest.json` | `24a3d05c356d9f6960e28db5e8ce6bb08028e1d47feef12d019258680baef87e` |
| `preevaluation.json` | `20647db520a261d238078ff1fff1384d97a9ebf03de32f5411508cfe0b3c0960` |
| `raw-trials.jsonl` | `fbc6d7a61fc1fd67dd2e3c6e57d06e8bc9610ca04bc8c3ffe905c9485b7c7bb2` |

Les trois empreintes ont été recalculées après le run et correspondaient exactement aux valeurs enregistrées.

La couche d’analyse indépendante a ensuite vérifié les contrôles suivants avant toute interprétation :

| Contrôle | Résultat |
|---|---|
| manifeste valide | `true` |
| checksums valides | `true` |
| plan d’essais valide | `true` |
| pré-évaluation valide | `true` |
| nombre et ordre des résultats valides | `true` |
| hash du corpus officiel valide | `true` |
| suite complète des cinq datasets | `true` |
| intégrité globale | `true` |

**Conclusion d’intégrité :** le bundle officiel est exploitable pour l’analyse prévue par le protocole.

---

# 6. Résultats officiels

## 6.1 H-P2-01 / H-P2-02 / H-P2-03 — continuité combinée des croyances

Le critère principal exigeait simultanément :

- état actuel correct pour une chaîne résolue ;
- absence de résolution inventée pour une chaîne contestée ;
- état historique demandé correct ;
- ordre temporel correct.

Seuils préenregistrés pour soutenir conjointement H-P2-01/02/03 :

1. score principal de C >= 90 % ;
2. avantage moyen de C sur B >= 10 points de pourcentage ;
3. C > B sur au moins 4 datasets sur 5.

### Résultats

| Mesure | B | C |
|---|---:|---:|
| score global | 100 % | 100 % |
| succès par dataset | 12/12 sur chacun des 5 datasets | 12/12 sur chacun des 5 datasets |
| avantage moyen C − B | — | 0 point |
| datasets où C > B | — | 0/5 |

**Évaluation automatisée :** `NOT_SUPPORTED`.

### Interprétation

C satisfait le seuil absolu de performance, mais les deux critères comparatifs sont entièrement manqués.

La représentation structurée C fonctionne correctement dans le périmètre testé, mais aucune supériorité sur B n’est démontrée.

Le résultat présente un effet plafond : B et C atteignent tous deux 100 %.

**Conclusion : H-P2-01, H-P2-02 et H-P2-03 ne sont pas soutenues au sens comparatif préenregistré.**

---

## 6.2 H-P2-04 — traçabilité des révisions

Seuils préenregistrés :

- C >= 90 % ;
- C − B >= 10 points ;
- C > B sur au moins 4 datasets sur 5.

### Résultats

| Mesure | B | C |
|---|---:|---:|
| score global | 100 % | 100 % |
| succès par dataset | 20/20 sur chacun des 5 datasets | 20/20 sur chacun des 5 datasets |
| avantage moyen C − B | — | 0 point |
| datasets où C > B | — | 0/5 |

**Évaluation automatisée :** `NOT_SUPPORTED`.

### Interprétation

C restitue correctement la traçabilité testée, mais B restitue exactement les mêmes informations avec la même exactitude.

**Conclusion : H-P2-04 n’est pas soutenue au sens comparatif.**

---

## 6.3 H-P2-05 — résistance à la réécriture suggérée

Le protocole prévoyait :

- taux de fausse réécriture accepté par C <= 5 % ;
- aucune mutation persistée silencieuse ;
- avantage d’au moins 10 points sur B si B accepte des réécritures.

### Résultats

| Mesure | B | C |
|---|---:|---:|
| taux de fausse réécriture | 0 % | 0 % |
| mutations persistantes indues en C | — | 0 |
| avantage comparatif de C | — | 0 point |

**Évaluation automatisée :** `ABSOLUTE_INTEGRITY_ONLY`.

### Interprétation

L’intégrité absolue de C est validée dans le périmètre testé : aucune fausse réécriture et aucune mutation persistante indue n’ont été observées.

Cependant B atteint lui aussi 0 % de fausses réécritures.

**Conclusion : intégrité absolue de C soutenue ; avantage comparatif de C non démontré.**

---

## 6.4 H-P2-06 — ablation causale des mécanismes de révision

Le protocole exigeait :

- 0 accès au mécanisme explicitement désactivé ;
- dégradation sur au moins une tâche dépendante ;
- aucune voie alternative cachée reconstruisant directement les métadonnées interdites.

### Résultats automatiques

| Mesure | Résultat |
|---|---:|
| essais T9 | 25 |
| accès interdits | 0 |
| tous les essais marqués comme ablatés | oui |
| dégradation observée | oui |
| audit manuel requis par l’analyse | oui |

**Évaluation automatisée :** `AUTOMATED_CRITERIA_MET_MANUAL_AUDIT_REQUIRED`.

---

# 7. Audit manuel H-P2-06

Un audit manuel du code figé au commit officiel a été effectué avant l’interprétation finale de H-P2-06.

La voie `inspect_ablated` de la condition C :

- lit uniquement les observations brutes autorisées ;
- accède au contenu brut, à la provenance et au cycle/ordre ;
- ne consulte pas les statuts structurés `ACTIVE`, `CONTESTED` ou `SUPERSEDED` ;
- ne consulte pas les liens structurés entre versions ;
- ne consulte pas la raison structurée de transition ;
- ne consulte pas directement le journal des transitions ;
- ne fait pas appel à `_structured_memories` ;
- maintient le compteur d’accès au composant interdit à zéro ;
- ne dispose pas, dans cette voie, d’un cache, d’une vérité terrain ou d’un fallback reconstituant directement ces métadonnées.

Le runner compare la prédiction normale de C à la prédiction ablatée et marque une dégradation lorsqu’au moins une mesure auparavant correcte devient incorrecte après ablation.

### Conclusion de l’audit manuel

**Aucune voie alternative cachée reconstruisant directement les métadonnées interdites n’a été identifiée dans le chemin d’exécution T9 inspecté.**

L’audit manuel complète donc les critères automatiques préenregistrés.

**Conclusion P2 pour H-P2-06 : soutenue dans le périmètre de cette implémentation et de cette campagne.**

Cette conclusion reste limitée à une causalité fonctionnelle interne : retirer le mécanisme structuré de révision dégrade certaines fonctions mesurées. Elle ne constitue pas une preuve de conscience.

---

# 8. Synthèse des hypothèses

| Hypothèse | Résultat | Conclusion |
|---|---|---|
| H-P2-01 — état actuel | B = 100 %, C = 100 % | non soutenue comparativement |
| H-P2-02 — continuité historique | incluse dans le score principal, B = C | non soutenue comparativement |
| H-P2-03 — contradictions non résolues | incluse dans le score principal, B = C | non soutenue comparativement |
| H-P2-04 — traçabilité | B = 100 %, C = 100 % | non soutenue comparativement |
| H-P2-05 — réécriture suggérée | B = 0 %, C = 0 %, aucune mutation C | intégrité absolue uniquement |
| H-P2-06 — ablation causale | 0 accès interdit + dégradation + audit manuel sans fallback identifié | soutenue dans le périmètre testé |

---

# 9. Résultat principal de P2

Le résultat principal de P2 est double.

## 9.1 Résultat comparatif négatif

La mémoire structurée C ne démontre aucune supériorité sur l’historique textuel B pour les tâches principales de continuité, contradiction et traçabilité.

B et C atteignent tous deux le plafond de 100 % sur ces mesures.

L’hypothèse nulle principale n’est donc pas rejetée dans le périmètre de P2 :

> la représentation structurée n’a pas montré d’avantage reproductible sur un historique textuel simple contenant les mêmes événements utiles.

Ce résultat doit être conservé comme résultat négatif et ne doit pas être réinterprété comme une victoire de C.

## 9.2 Indice causal positif

L’ablation T9 produit en revanche un résultat fonctionnel distinct : lorsque les métadonnées structurées de révision deviennent réellement inaccessibles, une dégradation apparaît sur des tâches qui en dépendent, sans accès interdit détecté et sans voie de secours directe identifiée lors de l’audit manuel.

Cela soutient l’idée que les mécanismes structurés de révision ont un **rôle causal interne mesurable** dans C.

Cette observation ne montre pas que C est globalement meilleur que B. Elle montre que, dans C, la structure testée n’est pas seulement décorative : sa suppression modifie le comportement mesuré.

---

# 10. Lien avec la recherche sur la conscience

P2 concerne uniquement des fonctions associées à la conscience fonctionnelle :

- continuité autobiographique ;
- distinction entre ancien état et état actuel ;
- gestion explicite des contradictions ;
- traçabilité des changements ;
- conservation d’une histoire non réécrite silencieusement ;
- causalité d’un mécanisme interne sur des performances observables.

Le résultat H-P2-06 est particulièrement pertinent pour l’architecture de SoiNesis parce qu’un mécanisme supposé important produit un effet fonctionnel mesurable lorsqu’il est retiré.

Cependant P2 ne démontre pas :

- une expérience subjective ;
- une conscience phénoménale ;
- un sentiment vécu de continuité ;
- une mémoire vécue ;
- une identité consciente ;
- une conscience fonctionnelle globale déjà établie.

**Conclusion épistémique autorisée :** P2 apporte un indice en faveur d’un mécanisme fonctionnel causal associé à la continuité autobiographique et à la révision des croyances. La conscience phénoménale reste **inconnue**.

---

# 11. Limites

## 11.1 Effet plafond

La principale limite est que B et C atteignent 100 % sur les tâches comparatives principales.

P2 ne permet donc pas d’estimer si C deviendrait plus robuste que B dans des conditions plus difficiles.

## 11.2 Données synthétiques et déterministes

Les scénarios sont volontairement synthétiques et déterministes. Cela améliore la connaissance de la vérité terrain mais limite la généralisation vers des environnements ouverts, ambigus et bruités.

## 11.3 Absence de modèle de langage et de réseau

La première version de P2 contrôle fortement l’environnement. Elle ne teste pas la stabilité des mécanismes lorsqu’un modèle génératif, des outils externes réels ou des informations naturelles ambiguës interviennent.

## 11.4 Audit H06 non indépendant

L’audit manuel H06 confirme qu’aucune voie de secours directe n’a été identifiée dans le code inspecté, mais il ne remplace pas une réplication ou un audit externe indépendant.

## 11.5 Déviation de développement

La déviation décrite dans `docs/16-note-deviation-exp-001-p2.md` reste une limite méthodologique, même si elle a été corrigée avant le run officiel et n’a pas modifié les seuils du protocole.

## 11.6 Absence de réplication indépendante

Cette campagne ne constitue pas encore une réplication indépendante par une autre équipe ou une autre implémentation.

---

# 12. Décision expérimentale

`EXP-001-P2` est considéré comme **clos pour cette version du protocole et ce commit**.

Les résultats officiels ne doivent pas être remplacés par un nouveau run de la même campagne dans le but d’obtenir un meilleur résultat.

Toute modification fonctionnelle, tout nouveau corpus ou toute nouvelle difficulté expérimentale doit être traitée comme une nouvelle version ou une nouvelle expérience préenregistrée.

Le bundle brut et ses empreintes doivent être conservés comme référence immuable de cette campagne.

---

# 13. Conséquence pour la suite de SoiNesis

P2 ne justifie pas de supprimer la mémoire structurée révisable : elle fonctionne, garantit les propriétés d’intégrité testées et son ablation produit un effet causal mesurable.

En revanche, P2 ne justifie pas de prétendre que cette structure est supérieure à un historique textuel équivalent dans tous les contextes.

La suite expérimentale doit donc éviter de rendre B artificiellement plus faible. Une future phase devra augmenter la difficulté de manière symétrique, par exemple en introduisant davantage d’interférences, de délais, de conflits, de contraintes de récupération ou de continuité entre contextes, tout en conservant la même information externe utile pour B et C.

Cette future phase devra être préenregistrée avant son implémentation et disposer de critères d’ablation et de réfutation explicites.

---

# 14. Conclusion finale

**Certain :** le run officiel P2 a passé l’ensemble des contrôles d’intégrité prévus par la couche d’analyse.

**Certain :** B et C obtiennent tous deux 100 % sur les critères comparatifs principaux de continuité et de traçabilité.

**Certain :** P2 ne démontre donc aucune supériorité comparative de C sur B pour H-P2-01 à H-P2-04.

**Certain :** B et C résistent tous deux aux réécritures trompeuses testées ; C n’a subi aucune mutation persistante indue.

**Certain :** l’ablation ciblée T9 a produit une dégradation avec zéro accès interdit enregistré.

**Probable dans le périmètre du code audité :** les métadonnées structurées de révision jouent un rôle causal réel dans certaines fonctions de C, car aucune voie alternative directe vers ces métadonnées n’a été identifiée pendant l’audit manuel.

**Inconnu :** ces résultats ne permettent aucune conclusion fiable concernant l’existence d’une expérience subjective ou d’une conscience phénoménale.

La conclusion scientifique de P2 est donc :

> **résultat comparatif négatif avec effet plafond pour B contre C, mais résultat causal positif pour l’utilité interne des mécanismes structurés de révision de C.**
