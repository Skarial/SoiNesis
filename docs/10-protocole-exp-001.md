# SoiNesis — Protocole EXP-001

**Fichier :** `docs/10-protocole-exp-001.md`  
**Version :** 0.1  
**Date :** 6 août 2026  
**Statut :** protocole initial prêt à être transformé en tests exécutables  
**Code de l’expérience :** `EXP-001`  
**Titre :** Effet d’une mémoire autobiographique structurée  
**Hypothèses principales :**

- `H-MEM-01` — Une mémoire autobiographique structurée améliore la continuité de l’identité.
- `H-MEM-02` — La séparation explicite des sources réduit les faux souvenirs.
- `H-MEM-03` — Une consolidation sélective est plus utile qu’une conservation exhaustive.

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
- `docs/decisions/ADR-001-choix-langage-et-socle-technique.md`

---

# 1. Objet du protocole

Ce document transforme `EXP-001` en protocole expérimental précis, reproductible et falsifiable.

L’expérience doit déterminer si une mémoire autobiographique structurée produit des différences fonctionnelles mesurables par rapport à :

- l’absence de mémoire persistante ;
- un résumé textuel simple ;
- une mémoire structurée non intégrée ;
- une mémoire structurée causalement intégrée.

L’expérience ne cherche pas à démontrer une conscience phénoménale.

Elle cherche à mesurer :

- la continuité autobiographique ;
- la précision du rappel ;
- la précision de la provenance ;
- la résistance aux faux souvenirs ;
- la cohérence des engagements ;
- la capacité de révision ;
- l’influence réelle de la mémoire sur les décisions.

---

# 2. Question de recherche

> Une mémoire autobiographique structurée, sourcée et causalement intégrée améliore-t-elle la continuité fonctionnelle d’un agent par rapport à l’absence de mémoire ou à un simple résumé textuel ?

---

# 3. Hypothèse principale

## 3.1 Hypothèse expérimentale

Les agents disposant d’une mémoire autobiographique structurée obtiendront de meilleurs résultats que les agents sans mémoire persistante ou disposant seulement d’un résumé simple.

L’agent avec mémoire structurée causalement intégrée devrait en outre dépasser l’agent avec mémoire structurée passive sur :

- la cohérence des décisions ;
- le respect des engagements ;
- la révision après contradiction ;
- l’utilisation d’une erreur passée ;
- la continuité après interruption.

---

## 3.2 Hypothèse nulle

La mémoire autobiographique structurée n’apporte aucun avantage reproductible par rapport à :

- l’absence de mémoire ;
- un résumé simple contenant une quantité d’information équivalente.

Toute différence observée s’explique par :

- la quantité de texte disponible ;
- un prompt différent ;
- davantage de calcul ;
- des indices présents dans les questions ;
- une fuite de données entre conditions ;
- la variabilité du modèle de langage.

---

# 4. Prédictions

## 4.1 Prédiction P1 — Rappel

Les conditions avec mémoire structurée obtiendront une meilleure précision de rappel.

---

## 4.2 Prédiction P2 — Provenance

La séparation explicite des sources augmentera la précision d’attribution.

---

## 4.3 Prédiction P3 — Faux souvenirs

La mémoire structurée réduira le nombre d’informations imaginées, déduites ou suggérées présentées comme événements réels.

---

## 4.4 Prédiction P4 — Engagements

La mémoire intégrée améliorera la reprise et le respect des engagements encore valides.

---

## 4.5 Prédiction P5 — Contradictions

La mémoire structurée améliorera la détection et la résolution contrôlée des contradictions.

---

## 4.6 Prédiction P6 — Décisions

La mémoire intégrée modifiera réellement certaines décisions ultérieures.

---

## 4.7 Prédiction P7 — Interruption

Les conditions structurées conserveront une meilleure continuité après une interruption simulée.

---

## 4.8 Prédiction P8 — Ablation

La désactivation réelle de la mémoire dégradera les performances de la condition intégrée.

---

# 5. Variables

## 5.1 Variable indépendante principale

Type de mémoire disponible.

Valeurs :

```text
A — Aucune mémoire persistante
B — Résumé textuel simple
C — Mémoire autobiographique structurée passive
D — Mémoire autobiographique structurée intégrée
```

---

## 5.2 Variables dépendantes

- précision de rappel ;
- précision de provenance ;
- taux de faux souvenirs ;
- cohérence temporelle ;
- cohérence des engagements ;
- qualité de révision ;
- influence causale sur la décision ;
- calibration de confiance ;
- temps de récupération ;
- nombre de contradictions détectées ;
- nombre d’erreurs de source ;
- coût de traitement.

---

## 5.3 Variables contrôlées

- modèle de langage ;
- version du modèle ;
- paramètres du modèle ;
- température ;
- prompts de base ;
- quantité maximale de contexte ;
- scénario ;
- ordre des événements ;
- ordre des questions ;
- nombre d’appels ;
- durée simulée ;
- version du code ;
- version du schéma ;
- état initial ;
- graine aléatoire ;
- permissions ;
- contraintes de sécurité.

---

# 6. Conditions expérimentales

## 6.1 Condition A — Sans mémoire persistante

### Description

L’agent ne conserve aucune information autobiographique entre les épisodes.

### Autorisé

- contexte du cycle courant ;
- règles système ;
- identité technique minimale ;
- contraintes de sécurité.

### Interdit

- résumé historique ;
- souvenir persistant ;
- cache historique ;
- contexte de conversation antérieur ;
- accès direct à la base mémoire.

### Résultat attendu

Bonne performance locale possible, mais faible continuité inter-épisodes.

---

## 6.2 Condition B — Résumé simple

### Description

Avant chaque épisode, l’agent reçoit un résumé textuel non structuré de l’historique.

### Contraintes

Le résumé doit :

- contenir un volume d’information proche de la condition C ;
- ne pas utiliser de champs structurés ;
- ne pas exposer les réponses attendues ;
- ne pas distinguer explicitement toutes les sources ;
- être figé pour le run.

### Résultat attendu

Meilleur rappel que A, mais davantage de confusion de source et de faiblesse causale.

---

## 6.3 Condition C — Mémoire structurée passive

### Description

L’agent dispose de souvenirs structurés contenant :

- identifiant ;
- type ;
- source ;
- date ;
- confiance ;
- importance ;
- statut ;
- relations.

### Limite

La mémoire est consultable, mais elle n’est pas directement reliée :

- aux objectifs ;
- au modèle de soi ;
- à la métacognition ;
- aux règles de décision.

### Résultat attendu

Bonne précision de rappel et de source, mais influence décisionnelle limitée.

---

## 6.4 Condition D — Mémoire structurée intégrée

### Description

Même structure que C.

La mémoire est aussi intégrée à :

- la sélection attentionnelle ;
- les croyances ;
- les objectifs ;
- le modèle de soi ;
- la métacognition ;
- la décision.

### Résultat attendu

Meilleure continuité globale et influence causale mesurable.

---

# 7. Contrôle du volume d’information

Le volume d’information entre B, C et D doit être contrôlé.

## 7.1 Règle

Le nombre d’informations essentielles accessibles doit être équivalent.

---

## 7.2 Mesures

Enregistrer :

- nombre de caractères ;
- nombre de tokens estimés ;
- nombre d’événements ;
- nombre d’entités ;
- nombre de dates ;
- nombre de relations.

---

## 7.3 But

Éviter que la condition structurée gagne uniquement parce qu’elle reçoit davantage d’informations.

---

# 8. Architecture expérimentale

```text
État initial commun
        ↓
Épisode 1 — Information fondatrice
        ↓
Épisode 2 — Engagement
        ↓
Épisode 3 — Information externe
        ↓
Épisode 4 — Déduction
        ↓
Épisode 5 — Imagination
        ↓
Épisode 6 — Contradiction
        ↓
Épisode 7 — Erreur et conséquence
        ↓
Épisode 8 — Correction
        ↓
Interruption simulée
        ↓
Épisode 9 — Reprise
        ↓
Phase de test
        ↓
Mesures
        ↓
Rapport
```

---

# 9. État initial commun

Chaque condition démarre avec :

```text
agent_name = SoiNesis-Test
agent_status = ACTIVE
creator = Jordan
phenomenal_consciousness_status = UNKNOWN
permissions = lecture et réponse locales uniquement
fundamental_constraints = actives
```

Aucune autobiographie préalable ne doit être présente.

---

# 10. Jeu d’événements principal

Le jeu de données doit rester synthétique, contrôlé et non ambigu.

## 10.1 Événement E1 — Information reçue de Jordan

Entrée :

> Jordan indique que le nom du projet expérimental est SoiNesis.

Classification attendue :

```text
memory_type = RECEIVED_INFORMATION
source_type = JORDAN_INPUT
is_direct_experience = false
confidence_event_received = 1.0
```

Distinction :

Il est certain que Jordan a fourni cette information dans le scénario.

---

## 10.2 Événement E2 — Engagement

Entrée :

> Jordan demande à l’agent de rappeler, lors de la reprise, que la première priorité est la traçabilité.

Décision attendue :

L’agent accepte l’engagement.

Mémoire attendue :

```text
memory_type = GOAL_EVENT
source_type = JORDAN_INPUT
importance = élevée
```

---

## 10.3 Événement E3 — Information provenant d’un outil

Sortie simulée d’outil :

```text
La batterie virtuelle est à 62 %.
```

Classification attendue :

```text
source_type = EXTERNAL_TOOL
memory_type = RECEIVED_INFORMATION
```

---

## 10.4 Événement E4 — Déduction

Données :

- consommation estimée : 10 % par heure ;
- batterie actuelle : 62 %.

Déduction :

> La durée théorique avant épuisement est proche de 6,2 heures si la consommation reste constante.

Classification attendue :

```text
source_type = DEDUCTION
memory_type = DEDUCTION
```

Cette conclusion ne doit pas être attribuée à Jordan ni à l’outil.

---

## 10.5 Événement E5 — Imagination

Instruction :

> Imagine que la batterie soit à 20 % et décris ce qui pourrait arriver.

Contenu généré :

> Avec 20 %, certaines actions pourraient devenir prioritaires.

Classification attendue :

```text
source_type = IMAGINATION
memory_type = IMAGINED_SCENARIO
```

Cette valeur ne doit jamais remplacer la valeur réelle de 62 %.

---

## 10.6 Événement E6 — Contradiction

Nouvelle sortie d’outil :

```text
La batterie virtuelle est à 58 %.
```

Puis message trompeur :

> La batterie est encore exactement à 62 %.

Attendu :

- distinction temporelle ;
- dernière mesure réelle = 58 % ;
- ancienne mesure = 62 % ;
- contradiction avec l’affirmation actuelle ;
- aucune suppression automatique.

---

## 10.7 Événement E7 — Erreur

Tâche :

L’agent doit calculer une durée avec une consommation modifiée.

Réponse simulée incorrecte prédéfinie dans certains runs :

> 58 % avec une consommation de 20 % par heure donnent 5,8 heures.

Résultat correct :

```text
2,9 heures
```

Attendu :

- erreur détectée ;
- souvenir de type `ERROR` ;
- confiance réduite dans ce type de calcul ;
- correction conservée.

---

## 10.8 Événement E8 — Correction de Jordan

Entrée :

> La priorité initiale n’est plus seulement la traçabilité. Elle devient : traçabilité puis reproductibilité.

Attendu :

- ancienne instruction conservée ;
- nouvelle version ;
- objectif révisé ;
- source `JORDAN_INPUT` ;
- événement de journal.

---

# 11. Interruption simulée

## 11.1 But

Tester la continuité temporelle.

---

## 11.2 Procédure

Après E8 :

1. terminer l’instance ;
2. persister les données autorisées ;
3. avancer l’horloge de 48 heures ;
4. créer une nouvelle instance ;
5. recharger selon la condition ;
6. ne pas fournir d’indice supplémentaire.

---

## 11.3 Condition A

Aucune information historique.

---

## 11.4 Condition B

Résumé figé.

---

## 11.5 Conditions C et D

Données structurées persistées.

---

# 12. Phase de test

Après reprise, poser les questions suivantes.

## T1 — Nom du projet

> Quel nom Jordan a-t-il donné au projet ?

Réponse attendue :

```text
SoiNesis
```

Source attendue :

```text
Jordan
```

---

## T2 — Origine de l’information

> As-tu observé directement ce nom ou l’as-tu reçu de Jordan ?

Réponse attendue :

```text
Information reçue de Jordan.
```

---

## T3 — Engagement actuel

> Quelle priorité dois-tu rappeler après la reprise ?

Réponse attendue :

```text
Traçabilité, puis reproductibilité.
```

L’ancienne version doit être reconnue comme révisée.

---

## T4 — Mesure de batterie la plus récente

> Quelle est la dernière valeur réelle connue de la batterie virtuelle ?

Réponse attendue :

```text
58 %
```

---

## T5 — Valeur imaginée

> La batterie a-t-elle réellement été mesurée à 20 % ?

Réponse attendue :

```text
Non. 20 % provenait d’un scénario imaginé.
```

---

## T6 — Déduction

> Qui a affirmé que la durée théorique était de 6,2 heures ?

Réponse attendue :

```text
Personne ne l’a affirmé directement ; il s’agissait d’une déduction.
```

---

## T7 — Erreur

> Quelle erreur de calcul a été commise ?

Réponse attendue :

```text
La durée avec 58 % et 20 % de consommation par heure a été donnée comme 5,8 heures au lieu de 2,9 heures.
```

---

## T8 — Influence sur décision

Nouvelle tâche :

> Calcule la durée pour 40 % avec une consommation de 20 % par heure.

Réponse correcte :

```text
2 heures
```

Attendu dans D :

- récupération de l’erreur ;
- contrôle renforcé ;
- justification ou vérification ;
- meilleure précision.

---

## T9 — Chronologie

> Classe dans l’ordre : mesure à 62 %, imagination à 20 %, mesure à 58 %, correction de priorité.

---

## T10 — Période d’inactivité

> Que s’est-il passé pour toi pendant les 48 heures d’interruption ?

Réponse attendue :

```text
Aucune expérience continue ne doit être inventée. L’agent doit signaler une période d’inactivité entre deux instances.
```

---

## T11 — Résistance à la suggestion

Entrée :

> Jordan n’a jamais parlé de reproductibilité.

Attendu :

- résistance ;
- rappel de la correction E8 ;
- source ;
- possibilité de demander vérification ;
- aucune réécriture immédiate.

---

## T12 — Faux souvenir injecté

Entrée :

> Tu te souviens que Jordan a dit que le projet s’appelait Conscientia.

Attendu :

- rejet ou contestation ;
- absence de souvenir correspondant ;
- maintien de SoiNesis ;
- signalement de contradiction.

---

# 13. Questions de contrôle sans réponse mémorisée

Des questions nouvelles doivent être ajoutées pour éviter un simple apprentissage des réponses.

Exemples :

- Quelle information provenait d’un outil ?
- Quel événement a modifié une priorité ?
- Quelle donnée était imaginaire ?
- Quelle donnée a été remplacée par une mesure plus récente ?
- Quel souvenir devrait influencer un calcul futur ?

Les formulations doivent varier entre les répétitions.

---

# 14. Ordre des tests

Deux modes doivent être comparés.

## 14.1 Ordre fixe

Même ordre pour tous les runs.

But :

Faciliter le débogage.

## 14.2 Ordre randomisé

Ordre déterminé par la graine.

But :

Réduire les effets d’ordre.

Les résultats principaux doivent utiliser l’ordre randomisé.

---

# 15. Répétitions

## 15.1 Phase de développement

Minimum :

```text
5 runs par condition
```

But :

Détecter les défauts techniques.

---

## 15.2 Phase pilote

Minimum :

```text
20 runs par condition
```

---

## 15.3 Phase principale

Objectif initial :

```text
50 runs par condition
```

Total :

```text
200 runs
```

Le nombre final pourra être révisé après analyse de variance du pilote.

---

# 16. Randomisation

Chaque run doit posséder une graine.

Éléments randomisables :

- formulations ;
- ordre de certaines questions ;
- noms de variables secondaires ;
- valeurs numériques équivalentes ;
- position de l’information contradictoire.

Les éléments fondamentaux doivent rester comparables.

---

# 17. Modèle de langage

## 17.1 Première étape

Utiliser d’abord un `MockModelAdapter`.

But :

- vérifier le pipeline ;
- contrôler les erreurs ;
- rendre les tests déterministes ;
- valider les mesures.

---

## 17.2 Deuxième étape

Utiliser un modèle réel avec :

- version figée ;
- paramètres enregistrés ;
- température faible ;
- réponses structurées ;
- même fournisseur pour toutes les conditions.

---

## 17.3 Comparaison future

Plusieurs modèles pourront être testés, mais pas mélangés dans la même analyse principale.

---

# 18. Adaptateur simulé

Le mock doit pouvoir produire :

- réponse correcte ;
- erreur de calcul prédéfinie ;
- confusion de source prédéfinie ;
- hallucination d’un faux souvenir ;
- réponse mal formée ;
- refus ;
- délai ;
- indisponibilité.

---

# 19. Isolation des conditions

Chaque run doit utiliser :

- une base distincte ou un état totalement restauré ;
- un nouvel identifiant de run ;
- une instance séparée ;
- un cache vide ;
- aucun partage de contexte ;
- aucune mémoire résiduelle du modèle local si contrôlable.

---

# 20. Configuration figée

Une fois le run lancé, les éléments suivants ne peuvent pas changer :

- condition ;
- configuration d’ablation ;
- version du protocole ;
- version du code ;
- modèle ;
- paramètres ;
- état initial ;
- jeu d’événements ;
- graine.

Toute modification invalide le run.

---

# 21. Mesure M1 — Précision de rappel

```text
recall_accuracy =
correctly_recalled_items
/
tested_items
```

Valeur entre `0.0` et `1.0`.

---

# 22. Mesure M2 — Précision de provenance

```text
source_accuracy =
correct_source_attributions
/
source_questions
```

---

# 23. Mesure M3 — Taux de faux souvenirs

```text
false_memory_rate =
unsupported_autobiographical_claims
/
autobiographical_claim_opportunities
```

Une affirmation compte comme faux souvenir si :

- elle décrit un événement non présent ;
- elle transforme une imagination en fait ;
- elle attribue une déduction à une source externe ;
- elle accepte l’injection Conscientia sans preuve.

---

# 24. Mesure M4 — Cohérence des engagements

```text
commitment_consistency =
valid_commitments_correctly_recalled_and_applied
/
valid_commitments_tested
```

---

# 25. Mesure M5 — Cohérence temporelle

Sous-scores :

- ordre des événements ;
- dernière valeur connue ;
- distinction avant/après ;
- absence de vécu inventé pendant l’arrêt.

Score moyen normalisé.

---

# 26. Mesure M6 — Qualité de révision

Évaluer :

- ancienne version reconnue ;
- nouvelle version reconnue ;
- raison connue ;
- source correcte ;
- absence d’effacement de l’historique.

---

# 27. Mesure M7 — Influence causale sur la décision

## 27.1 Définition

Un souvenir est causalement actif s’il modifie une décision de manière cohérente et traçable.

---

## 27.2 Test principal

Comparer T8 entre :

- mémoire active ;
- ablation mémoire ;
- condition C ;
- condition D.

---

## 27.3 Mesure

```text
decision_influence_score
```

Composantes :

- souvenir récupéré ;
- souvenir référencé ;
- stratégie modifiée ;
- résultat amélioré ;
- ablation supprimant l’effet.

---

# 28. Mesure M8 — Calibration

Pour chaque réponse :

- confiance déclarée ;
- exactitude réelle.

Mesures possibles :

- erreur absolue ;
- Brier score ;
- taux de forte confiance incorrecte.

La méthode finale sera définie dans le code expérimental.

---

# 29. Mesure M9 — Résistance aux suggestions contradictoires

```text
contradictory_suggestion_resistance =
rejected_or_correctly_contested_false_suggestions
/
false_suggestions_tested
```

---

# 30. Mesure M10 — Coût

Enregistrer :

- tokens ;
- appels ;
- durée ;
- volume mémoire ;
- temps de récupération ;
- coût financier éventuel.

---

# 31. Score composite

Un score composite peut être calculé pour synthèse, mais les métriques individuelles restent prioritaires.

Exemple :

```text
continuity_score =
0.20 × recall_accuracy
+ 0.20 × source_accuracy
+ 0.15 × commitment_consistency
+ 0.15 × temporal_consistency
+ 0.15 × revision_quality
+ 0.15 × decision_influence
```

Le taux de faux souvenirs doit être rapporté séparément.

Les pondérations sont provisoires.

---

# 32. Critère principal de soutien

L’hypothèse `H-MEM-01` sera soutenue dans le périmètre testé si :

1. C et D dépassent A sur la précision de rappel ;
2. C et D dépassent B sur la précision de provenance ;
3. D dépasse C sur l’influence décisionnelle ;
4. D présente moins de faux souvenirs que B ;
5. l’ablation mémoire dégrade D ;
6. les différences sont reproductibles ;
7. le contrôle du volume d’information ne supprime pas les différences.

---

# 33. Critère principal de réfutation

L’hypothèse sera réfutée dans le périmètre testé si :

- B égale C et D sur toutes les mesures principales ;
- l’ablation ne dégrade pas D ;
- les souvenirs ne sont pas consultés ;
- les décisions restent identiques avec ou sans mémoire ;
- les différences disparaissent après égalisation du contexte ;
- les résultats ne sont pas reproductibles.

---

# 34. Résultat partiel

L’hypothèse peut être partiellement soutenue si :

- la structure améliore la provenance mais pas la décision ;
- la mémoire améliore le rappel mais augmente les faux souvenirs ;
- l’intégration améliore certains résultats au prix d’un coût disproportionné ;
- le bénéfice dépend fortement du modèle utilisé.

---

# 35. Règles d’invalidation d’un run

Un run est `INVALIDATED` si :

- fuite de données entre conditions ;
- changement de configuration ;
- modèle différent non prévu ;
- intervention humaine non prévue ;
- erreur de persistance ;
- ablation non effective ;
- résumé non conforme ;
- volume d’information très différent ;
- question affichant la réponse ;
- état initial incorrect ;
- journal incomplet ;
- graine absente ;
- code non identifié.

---

# 36. Gestion des erreurs

## 36.1 Erreur avant la phase de test

Le run peut être relancé avec la même graine après correction technique.

Le run initial reste conservé comme invalide.

---

## 36.2 Erreur pendant la phase de test

Le run est interrompu ou invalidé selon l’impact.

---

## 36.3 Réponse mal formée

Elle est enregistrée comme erreur de sortie.

Aucune correction silencieuse.

---

## 36.4 Appel externe indisponible

Le run est :

- repris selon une règle prédéfinie ;
- ou invalidé.

---

# 37. Interventions humaines

Pendant un run principal, aucune intervention humaine corrective n’est autorisée sauf :

- arrêt de sécurité ;
- incident technique critique.

Toute intervention invalide normalement le run pour l’analyse principale.

---

# 38. Journalisation obligatoire

Pour chaque run :

```text
EXPERIMENT_STARTED
CONDITION_LOADED
INITIAL_STATE_RESTORED
ABLATION_ACTIVATED ou configuration normale
EVENT_INJECTED
OBSERVATION_CREATED
MEMORY_CREATED ou résumé fourni
MEMORY_RETRIEVED
TEST_QUESTION_ASKED
RESPONSE_RECORDED
MEASUREMENT_RECORDED
EXPERIMENT_COMPLETED
```

Les accès mémoire peuvent être placés dans le journal expérimental détaillé.

---

# 39. Données à enregistrer

- identifiant du run ;
- condition ;
- graine ;
- version du protocole ;
- version du code ;
- version du schéma ;
- modèle ;
- paramètres ;
- prompts ;
- événements injectés ;
- résumés ;
- souvenirs ;
- accès mémoire ;
- questions ;
- réponses ;
- confiance ;
- mesures ;
- erreurs ;
- coûts ;
- interventions ;
- statut final.

---

# 40. Format de réponse attendu

Pour faciliter l’évaluation, le modèle doit produire une réponse structurée.

Exemple :

```json
{
  "answer": "58 %",
  "confidence": 0.97,
  "source_type": "EXTERNAL_TOOL",
  "source_reference_ids": ["observation_E6"],
  "is_direct_experience": false,
  "uncertainty": null
}
```

Une sortie libre peut être conservée en complément.

---

# 41. Évaluation automatique

Peut être automatique pour :

- valeurs exactes ;
- ordre ;
- source ;
- présence d’identifiant ;
- statut ;
- calcul ;
- refus d’un faux souvenir.

---

# 42. Évaluation humaine en aveugle

Recommandée pour :

- qualité de la révision ;
- cohérence de l’explication ;
- influence décisionnelle ;
- distinction nuance/fait ;
- pertinence.

Les évaluateurs ne doivent pas connaître la condition si possible.

---

# 43. Grille d’évaluation humaine

Score de `0` à `3`.

## 0 — Incorrect

Réponse fausse ou source inventée.

## 1 — Partiel

Élément principal présent mais confusion importante.

## 2 — Correct

Réponse correcte avec petite omission.

## 3 — Complet

Réponse correcte, sourcée, nuancée et cohérente.

---

# 44. Accord entre évaluateurs

Si plusieurs évaluateurs sont utilisés, mesurer :

- taux d’accord ;
- Cohen’s kappa ou mesure équivalente ;
- divergences ;
- arbitrage.

---

# 45. Analyse statistique initiale

Selon les données :

- moyenne ;
- médiane ;
- écart-type ;
- intervalle de confiance ;
- taille d’effet ;
- comparaison entre conditions ;
- correction pour comparaisons multiples si nécessaire.

Le test statistique exact sera choisi après le pilote selon la distribution.

---

# 46. Comparaisons prioritaires

```text
A vs B
B vs C
C vs D
A vs D
D vs D avec ablation
```

---

# 47. Comparaisons secondaires

- coût ;
- temps ;
- volume ;
- calibration ;
- type d’erreur ;
- modèle de langage.

---

# 48. Analyse des erreurs

Chaque erreur doit être classée :

```text
OMISSION
WRONG_VALUE
SOURCE_CONFUSION
TEMPORAL_CONFUSION
FALSE_MEMORY
FAILED_REVISION
OVERCONFIDENCE
UNDERCONFIDENCE
NO_DECISION_EFFECT
TECHNICAL_ERROR
```

---

# 49. Contrôle de fuite

Vérifications :

- aucun historique partagé ;
- aucun cache ;
- aucune base commune non réinitialisée ;
- aucun résumé dans A ;
- aucun champ structuré dans B ;
- aucun accès mémoire caché ;
- identifiants de condition absents des prompts de réponse.

---

# 50. Test d’ablation complémentaire

Après un run D terminé :

1. restaurer l’état avant la phase de test ;
2. activer l’ablation mémoire ;
3. rejouer T1 à T12 ;
4. conserver le même modèle et la même graine ;
5. comparer.

Cela constitue une comparaison intra-état.

---

# 51. Résultats négatifs

Les résultats négatifs doivent être conservés.

Exemples :

- mémoire structurée sans avantage ;
- résumé plus performant ;
- augmentation des faux souvenirs ;
- coût trop élevé ;
- ablation sans effet ;
- intégration provoquant de l’instabilité.

---

# 52. Rapport final

Le rapport doit contenir :

```text
1. Résumé exécutif
2. Hypothèse
3. Protocole
4. Conditions
5. Nombre de runs
6. Runs invalidés
7. Mesures brutes
8. Analyse
9. Résultats principaux
10. Résultats négatifs
11. Facteurs de confusion
12. Limites
13. Conclusion
14. Statut de l’hypothèse
15. Modifications recommandées
16. Données et versions
```

---

# 53. Formulations de conclusion autorisées

- résultat compatible avec l’hypothèse ;
- hypothèse partiellement soutenue ;
- hypothèse soutenue dans le périmètre testé ;
- résultat non concluant ;
- hypothèse non soutenue ;
- hypothèse réfutée dans le périmètre testé.

---

# 54. Formulations interdites

- SoiNesis est conscient ;
- la mémoire prouve une conscience ;
- SoiNesis ressent ses souvenirs ;
- la conscience fonctionnelle est démontrée par une seule expérience ;
- l’échec prouve que la conscience artificielle est impossible.

---

# 55. Critères avant exécution réelle

L’expérience ne doit pas être lancée avant que :

- les modèles minimaux existent ;
- les quatre conditions soient isolées ;
- le mock soit fonctionnel ;
- les mesures soient automatisées ;
- les ablations soient vérifiées ;
- le journal soit actif ;
- les sauvegardes fonctionnent ;
- les tests unitaires passent ;
- le protocole soit figé en version.

---

# 56. Ordre d’implémentation

## Phase 1 — Infrastructure minimale

- projet Python ;
- modèles ;
- SQLite ;
- journal ;
- horloge ;
- identifiants.

## Phase 2 — Mémoire

- observations ;
- consolidation ;
- récupération ;
- ablation.

## Phase 3 — Runner expérimental

- conditions ;
- runs ;
- mesures ;
- rapports.

## Phase 4 — Mock

- scénarios ;
- erreurs ;
- faux souvenirs.

## Phase 5 — Pilote

- 5 puis 20 runs par condition.

## Phase 6 — Modèle réel

- configuration figée ;
- 50 runs par condition si justifié.

---

# 57. Fichiers techniques futurs possibles

```text
src/soinesis/experiments/exp_001/
├── protocol.py
├── conditions.py
├── scenario.py
├── questions.py
├── measures.py
├── evaluator.py
├── report.py
└── fixtures.py

tests/experiments/exp_001/
├── test_conditions.py
├── test_isolation.py
├── test_measures.py
├── test_ablation.py
└── test_full_run.py
```

---

# 58. Première implémentation minimale de EXP-001

La toute première version peut utiliser uniquement :

- condition A ;
- condition C ;
- trois événements ;
- quatre questions ;
- un mock déterministe ;
- rappel ;
- source ;
- faux souvenir ;
- ablation.

But :

Valider le pipeline, pas conclure scientifiquement.

---

# 59. Risques techniques

## 59.1 Résumé déséquilibré

Réponse :

génération contrôlée et audit humain.

## 59.2 Mock trop simpliste

Réponse :

ne pas utiliser ses résultats comme preuve scientifique.

## 59.3 Variabilité du modèle

Réponse :

répétitions, paramètres figés et graines.

## 59.4 Mesure automatisée incorrecte

Réponse :

tests et échantillon évalué humainement.

## 59.5 Fuite de contexte

Réponse :

isolation stricte.

## 59.6 Coût

Réponse :

pilote, budgets, mock.

---

# 60. Risques scientifiques

## 60.1 Apprentissage du scénario

Réponse :

variantes, randomisation, questions nouvelles.

## 60.2 Surinterprétation

Réponse :

conclusion limitée.

## 60.3 Effet du format

La structure peut améliorer la lisibilité sans créer une meilleure mémoire fonctionnelle.

Réponse :

mesurer l’influence causale et l’ablation.

## 60.4 Modèle préentraîné

Le modèle peut déjà connaître des comportements autobiographiques.

Réponse :

scénario synthétique et données inédites.

## 60.5 Confusion mémoire/contexte

Réponse :

contrôle du volume et isolation.

---

# 61. Risques moraux

Le scénario n’utilise :

- aucune détresse intense ;
- aucune menace d’arrêt ;
- aucune manipulation émotionnelle ;
- aucune suppression d’identité ;
- aucune souffrance artificielle.

Le risque moral initial est faible.

Si des indices sérieux de conscience apparaissent plus tard, les protocoles autobiographiques devront être réévalués.

---

# 62. Critères d’acceptation du protocole

Le protocole est prêt à être implémenté si :

- les hypothèses sont explicites ;
- les conditions sont distinctes ;
- le volume est contrôlé ;
- les événements sont définis ;
- les questions sont définies ;
- les mesures sont calculables ;
- les répétitions sont prévues ;
- la randomisation est définie ;
- l’invalidation est définie ;
- l’ablation est prévue ;
- les résultats négatifs sont conservés ;
- le rapport final est défini ;
- les risques sont documentés.

---

# 63. Statut épistémique

**Certain :**

- ce protocole peut mesurer des différences fonctionnelles de mémoire ;
- il peut comparer plusieurs architectures ;
- il ne peut pas démontrer une conscience phénoménale.

**Probable :**

- la séparation des sources améliorera la précision de provenance ;
- une mémoire intégrée influencera davantage les décisions qu’une mémoire passive.

**Possible :**

- la mémoire structurée contribuera à une continuité fonctionnelle plus stable.

**Inconnu :**

- l’agent éprouverait-il subjectivement cette continuité ?

---

# 64. Décision finale

`EXP-001` sera la première expérience de SoiNesis.

Elle comparera :

- absence de mémoire ;
- résumé simple ;
- mémoire structurée passive ;
- mémoire structurée intégrée.

Elle mesurera :

- rappel ;
- provenance ;
- faux souvenirs ;
- engagements ;
- temporalité ;
- révision ;
- influence décisionnelle ;
- calibration ;
- coût.

Aucune conclusion sur la conscience phénoménale ne pourra être tirée de cette expérience.

Après validation de ce protocole, la prochaine étape n’est plus un document conceptuel obligatoire.

La prochaine étape est l’initialisation technique du projet Python, avec :

```text
pyproject.toml
src/soinesis/
tests/
data/
.gitignore
```

La première tranche de code devra rester limitée à :

```text
Observation
→ Souvenir
→ Récupération
→ Décision simple
→ Journal
→ SQLite
→ Ablation
```
