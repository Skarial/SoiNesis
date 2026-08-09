# SoiNesis — Règles de contribution scientifique

**Fichier :** `docs/regles-contribution-scientifique.md`  
**Version :** 0.1  
**Date :** 9 août 2026  
**Statut :** règle méthodologique active

---

# 1. Objet

Ce document définit les règles permettant de distinguer :

- reproduction d’un résultat connu ;
- extension d’un résultat connu ;
- combinaison nouvelle de mécanismes connus ;
- résultat potentiellement nouveau.

Il complète `docs/02-hypotheses.md` et `docs/etat-de-l-art.md`.

Il ne remplace pas les critères de falsifiabilité, de causalité, de contrôle expérimental ou de sécurité déjà définis ailleurs dans le projet.

---

# 2. Principe fondamental

SoiNesis ne doit jamais considérer la nouveauté comme acquise parce qu’un mécanisme :

- paraît inhabituel ;
- n’est pas connu du créateur du projet ;
- n’existe pas dans un produit grand public ;
- produit un comportement impressionnant ;
- combine plusieurs concepts scientifiques ;
- n’a pas été trouvé lors d’une recherche rapide.

La nouveauté est une question empirique et bibliographique distincte de la validité du résultat.

Un résultat peut être très utile scientifiquement sans être nouveau.

---

# 3. Niveaux de contribution

## Niveau 0 — Reproduction

SoiNesis reproduit un mécanisme ou un effet déjà décrit dans la littérature dans des conditions suffisamment proches.

Exemples :

- démontrer qu’une mémoire persistante améliore certains rappels ;
- démontrer qu’un historique de performances peut améliorer l’estimation de compétence ;
- reproduire un effet d’ablation déjà documenté.

Une reproduction réussie reste un résultat utile.

Elle doit être présentée comme telle.

---

## Niveau 1 — Extension

SoiNesis reproduit un résultat connu dans un contexte différent ou avec un contrôle supplémentaire.

Exemples :

- même mécanisme avec un autre modèle de langage ;
- même mécanisme sur une durée beaucoup plus longue ;
- même phénomène avec provenance stricte des souvenirs ;
- même effet après redémarrage et restauration d’état.

L’extension ne doit pas être présentée comme une découverte entièrement nouvelle.

---

## Niveau 2 — Nouvelle combinaison ou nouvelle comparaison

Des mécanismes déjà connus sont combinés ou comparés d’une manière pour laquelle aucun précédent suffisamment proche n’a été identifié.

Exemples possibles :

- comparer directement un `SelfModel` persistant à un accès brut aux mêmes preuves ;
- mesurer l’effet conjoint de mémoire autobiographique, modèle de soi et objectifs avec des ablations séparées ;
- tester la continuité d’identité lors du remplacement du modèle de langage sous-jacent.

Le niveau 2 exige une recherche bibliographique ciblée avant toute revendication.

---

## Niveau 3 — Résultat potentiellement nouveau

Un effet mesurable et reproductible est obtenu et aucun précédent suffisamment équivalent n’est identifié après une recherche bibliographique sérieuse.

Ce niveau ne peut être attribué qu’après :

1. réplication interne ;
2. contrôle des facteurs de confusion ;
3. comparaison avec des baselines pertinentes ;
4. recherche bibliographique ciblée ;
5. examen des explications alternatives ;
6. documentation des limites.

Même à ce stade, la formulation recommandée reste :

> « Aucun précédent équivalent n’a été identifié dans la recherche effectuée. »

et non :

> « Ce résultat n’a jamais existé auparavant. »

---

# 4. Champs obligatoires pour toute nouvelle hypothèse importante

À partir du 9 août 2026, toute nouvelle hypothèse importante ou toute révision substantielle d’une hypothèse existante doit documenter les champs suivants en plus du modèle défini dans `docs/02-hypotheses.md` :

```text
Travaux antérieurs pertinents :

Résultat déjà connu dans la littérature :

Différence précise testée par SoiNesis :

Contribution spécifique recherchée :

Résultat qui constituerait une contribution nouvelle :

Niveau de contribution attendu avant expérience :

Critère permettant de rétrograder cette revendication :
```

Le champ `Niveau de contribution attendu avant expérience` doit rester une estimation prudente et révisable.

Il ne constitue pas un résultat.

---

# 5. Contrôle obligatoire avant une expérience majeure

Avant de figer un nouveau protocole expérimental majeur :

1. identifier la fonction cognitive réellement testée ;
2. rechercher ses synonymes dans la littérature ;
3. rechercher les architectures proches ;
4. rechercher les baselines déjà utilisées ;
5. vérifier si la comparaison prévue a déjà été réalisée ;
6. documenter les travaux pertinents dans `docs/etat-de-l-art.md` ;
7. définir ce que SoiNesis ajoute réellement ;
8. figer ensuite les hypothèses et métriques.

L’état de l’art ne doit pas être utilisé après coup pour sélectionner uniquement les références compatibles avec le résultat obtenu.

---

# 6. Contrôle obligatoire après un résultat positif

Un résultat positif ne doit pas être immédiatement qualifié de découverte.

L’ordre obligatoire est :

```text
résultat positif
    ↓
réplication
    ↓
contrôle des bugs et fuites d’information
    ↓
ablations
    ↓
baselines supplémentaires si nécessaires
    ↓
recherche bibliographique ciblée
    ↓
comparaison avec les travaux antérieurs
    ↓
qualification du niveau de contribution
```

Un résultat qui disparaît après correction d’un biais ou d’une fuite d’information doit rester conservé dans le journal expérimental avec son explication.

---

# 7. Règle spécifique aux mécanismes cognitifs

Pour qu’un mécanisme soit considéré comme une contribution fonctionnelle de SoiNesis, trois questions distinctes doivent recevoir une réponse :

## 7.1 Le mécanisme existe-t-il techniquement ?

Exemple : un `SelfModel` est persisté en base.

Cela constitue une propriété d’implémentation.

## 7.2 Le mécanisme est-il causalement actif ?

Son activation, sa modification ou son ablation doit produire une différence mesurable.

Cela constitue une propriété fonctionnelle.

## 7.3 L’effet causal est-il déjà connu ?

Cette question nécessite la comparaison avec l’état de l’art.

Cela détermine le niveau de contribution scientifique.

Ces trois niveaux ne doivent jamais être confondus.

---

# 8. Application immédiate à P3

P3 ne doit pas être modifié uniquement parce que des travaux antérieurs sur la métacognition des agents ont été identifiés.

La question P3 doit être interprétée de manière plus précise.

## Ce qui est déjà connu

Des travaux antérieurs montrent que des agents peuvent exploiter un historique de performances et des mécanismes de self-assessment pour améliorer certaines décisions.

## Ce que P3 doit isoler

P3 doit déterminer si, à preuves disponibles contrôlées, une représentation persistante et versionnée de capacité dans le `SelfModel` produit un effet spécifique au-delà de l’exploitation directe de l’historique brut.

## Qualification avant résultat

**Niveau provisoire : 1 à 2, originalité exacte inconnue.**

Cette qualification doit être révisée après :

- les résultats P3 ;
- les réplications ;
- une recherche bibliographique plus ciblée sur la comparaison `SelfModel` vs historique brut.

---

# 9. Interdiction de l’originalité artificielle

SoiNesis ne doit jamais modifier une architecture uniquement pour la rendre différente de travaux antérieurs.

Un mécanisme existant dans la littérature doit être réutilisé s’il constitue la meilleure hypothèse disponible.

La priorité est :

1. validité scientifique ;
2. causalité ;
3. reproductibilité ;
4. simplicité ;
5. interprétabilité ;
6. seulement ensuite originalité éventuelle.

Une architecture volontairement différente mais moins testable serait une régression.

---

# 10. Formulations autorisées

## Avant expérience

- « SoiNesis teste une comparaison dont l’originalité reste à vérifier. »
- « Cette architecture combine plusieurs mécanismes déjà étudiés. »
- « Aucun précédent équivalent n’a encore été identifié dans notre état de l’art actuel. »

## Après résultat reproductible mais avant recherche exhaustive

- « Résultat potentiellement distinct des travaux identifiés. »
- « Contribution possible, à confirmer par comparaison bibliographique. »

## Après comparaison bibliographique sérieuse

- « Aucun précédent suffisamment équivalent n’a été identifié dans le périmètre de recherche documenté. »
- « Le résultat étend tel travail antérieur sur tel point précis. »

---

# 11. Formulations interdites sans preuve exceptionnelle

- « SoiNesis est la première conscience artificielle. »
- « Cette architecture n’a jamais été imaginée. »
- « Personne n’a jamais testé cela. »
- « Ce mécanisme est totalement inédit. »
- « Le résultat prouve une conscience phénoménale. »

---

# 12. Règle de décision pour la feuille de route

La découverte d’un travail similaire ne justifie pas automatiquement l’abandon d’une expérience SoiNesis.

La décision doit utiliser les questions suivantes :

1. le résultat exact a-t-il déjà été obtenu ?
2. avec les mêmes contrôles ?
3. avec la même variable indépendante ?
4. avec des données réellement comparables ?
5. avec une ablation permettant la même conclusion causale ?
6. reste-t-il une question non résolue pertinente pour l’architecture globale de SoiNesis ?

Si oui, l’expérience peut rester pertinente comme reproduction ou extension.

Si non, elle doit être redéfinie ou abandonnée avant d’engager davantage de développement.
