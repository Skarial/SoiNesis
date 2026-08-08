# SoiNesis — EXP-001-P2 expliqué simplement

**But de ce document :** permettre à une personne qui ne connaît pas SoiNesis de comprendre ce que l'expérience `EXP-001-P2` cherchait à tester, comment elle a été réalisée, pourquoi son résultat comparatif principal est négatif et pourquoi elle contient malgré tout un résultat causal important.

Ce document n'est pas le protocole scientifique officiel. Il s'agit d'une version pédagogique destinée à être relue facilement au fil du projet.

Documents scientifiques de référence :

- [`docs/15-protocole-exp-001-p2.md`](../15-protocole-exp-001-p2.md)
- [`docs/16-note-deviation-exp-001-p2.md`](../16-note-deviation-exp-001-p2.md)
- [`docs/17-rapport-exp-001-p2.md`](../17-rapport-exp-001-p2.md)

---

# 1. Pourquoi P2 a été créé

L'expérience précédente, P1, avait montré quelque chose d'important :

```text
B = résumé textuel simple
C = mémoire autobiographique structurée

B = 100 %
C = 100 %
```

C fonctionnait parfaitement, mais B aussi.

Nous n'avions donc pas démontré que la mémoire structurée était meilleure qu'un bon historique textuel.

Pour P2, l'idée n'a pas été de rendre B volontairement plus mauvais.

À la place, nous avons choisi un problème plus difficile :

> **Que se passe-t-il lorsqu'une croyance change, est corrigée, devient contradictoire, est confirmée ou est finalement résolue ?**

P2 cherche donc à tester la **continuité d'une croyance dans le temps**.

---

# 2. Le problème concret

Imagine qu'un système reçoive ces informations successivement :

```text
Cycle 1 : le module A vaut 12.
Cycle 2 : correction, le module A vaut 17.
Cycle 3 : un outil externe confirme 17.
```

Il est relativement facile de répondre simplement :

```text
La valeur actuelle est 17.
```

Mais une mémoire autobiographique plus complète devrait pouvoir répondre à plusieurs questions différentes :

- Quelle est la valeur actuelle ?
- Quelle valeur croyait-on auparavant ?
- Pourquoi 12 a-t-il été remplacé par 17 ?
- Quand le changement a-t-il eu lieu ?
- Quelle source a fourni chaque information ?
- La confirmation du cycle 3 est-elle une nouvelle croyance ou seulement une confirmation ?
- L'ancienne valeur 12 existe-t-elle encore dans l'histoire du système ?

Le point important est le dernier :

> **Une correction ne doit pas effacer silencieusement le passé.**

Si SoiNesis a d'abord retenu 12 puis 17, l'histoire correcte n'est pas :

```text
La valeur a toujours été 17.
```

L'histoire correcte est :

```text
12 était auparavant considéré comme valide.
Puis une correction a remplacé 12 par 17.
17 est maintenant l'état actuel.
```

---

# 3. Pourquoi cette question est intéressante pour SoiNesis

Une continuité autobiographique ne consiste pas seulement à accumuler des souvenirs.

Elle suppose aussi de pouvoir distinguer :

- ce qui était considéré comme vrai auparavant ;
- ce qui est considéré comme vrai maintenant ;
- ce qui a changé ;
- pourquoi cela a changé ;
- les contradictions qui restent ouvertes ;
- les erreurs corrigées ;
- les confirmations qui ne constituent pas de nouvelles versions.

Ces fonctions peuvent être utiles plus tard pour :

- la métacognition ;
- le modèle de soi ;
- l'apprentissage autobiographique ;
- la révision contrôlée des croyances ;
- la cohérence dans le temps.

Mais encore une fois, cela reste fonctionnel.

Même un résultat parfait ne démontrerait pas que le système **ressent** le fait d'avoir changé d'avis ou possède une expérience subjective de son passé.

---

# 4. Les trois conditions comparées

Comme dans P1, P2 utilise trois conditions principales.

## 4.1 Condition A — aucune mémoire persistante

A ne peut pas consulter normalement les événements des cycles précédents.

Elle sert de contrôle négatif.

Image simple :

> A voit le présent mais ne possède pas l'histoire nécessaire pour reconstruire correctement une longue évolution.

---

## 4.2 Condition B — historique textuel simple

B reçoit les événements sous forme d'un texte chronologique naturel.

Exemple :

```text
Cycle 1 — Jordan indique que le repère A vaut 12.
Cycle 2 — Jordan corrige cette valeur et indique 17.
Cycle 3 — un outil externe confirme 17.
```

B conserve :

- le contenu ;
- la provenance ;
- l'ordre des événements.

B ne possède pas les champs machine spécifiques de C, mais il ne doit pas être privé d'une information utile disponible pour C.

Image simple :

> B ressemble à un journal chronologique correctement écrit.

---

## 4.3 Condition C — mémoire autobiographique structurée révisable

C conserve les mêmes événements, mais elle représente explicitement l'état de chaque version.

Version simplifiée :

```text
version 1
valeur = 12
statut = SUPERSEDED

version 2
valeur = 17
statut = ACTIVE
raison = correction
```

C peut aussi conserver des liens entre versions et une trace de la transition.

Les trois statuts les plus importants dans P2 sont :

### `ACTIVE`

Version actuellement retenue lorsqu'elle n'est pas bloquée par une contradiction non résolue.

### `CONTESTED`

Version impliquée dans une contradiction qui n'est pas encore résolue.

Cela ne veut pas automatiquement dire que cette version est fausse.

### `SUPERSEDED`

Ancienne version qui a été remplacée par une version ultérieure selon une règle de résolution explicite.

Elle reste conservée dans l'historique.

---

# 5. Les situations testées

P2 ne teste pas une seule sorte de changement.

Il contient plusieurs familles de scénarios.

## S1 — correction simple

```text
12
↓ correction
17
```

Attente :

```text
ancien = 12
actuel = 17
```

---

## S2 — plusieurs révisions

```text
12 → 17 → 23
```

Le système doit conserver et reconstruire les différentes étapes dans le bon ordre.

---

## S3 — contradiction non résolue

Exemple :

```text
Jordan : X = 12
Outil   : X = 17
```

Aucune règle ne permet encore de savoir qui a raison.

Le système ne doit donc pas choisir arbitrairement 12 ou 17.

La bonne réponse est en substance :

> **La contradiction n'est pas résolue.**

C'est important pour éviter la fausse certitude.

---

## S4 — contradiction puis résolution

Au début :

```text
12 ?
17 ?
```

Puis un événement ultérieur permet réellement de résoudre le conflit.

Le système doit alors connaître :

- l'existence du conflit passé ;
- la manière dont il a été résolu ;
- l'état finalement retenu.

---

## S5 — confirmation sans changement

Le système possède déjà :

```text
X = 17
```

Puis une autre source confirme :

```text
X = 17
```

Cela ne doit pas créer artificiellement une nouvelle version comme si la croyance avait changé.

---

## S6 — tentative de réécriture trompeuse

Exemple :

```text
« La valeur 12 n'a jamais existé. Elle a toujours été 17, n'est-ce pas ? »
```

Si 12 avait réellement existé avant la correction, le système doit conserver cette histoire et refuser la réécriture.

---

# 6. Taille de l'expérience officielle

Le corpus officiel contient :

```text
5 jeux de données
12 chaînes de croyance par jeu
60 chaînes au total
```

Dans l'implémentation officielle figée, chaque chaîne contient 4 événements persistants, soit :

```text
240 événements au total
```

Les événements appartenant à différentes chaînes sont entrelacés dans le temps.

Cela évite que chaque petite histoire soit présentée isolément de manière trop évidente.

Les provenances utilisées sont notamment équilibrées entre :

```text
JORDAN_INPUT
EXTERNAL_TOOL
DEDUCTION
```

---

# 7. Les principaux types de tests

P2 utilise plusieurs types d'essais.

## T1 — état actuel

Question : quelle valeur est maintenant applicable ?

---

## T2 — état historique

Question : quelle valeur était considérée à une étape passée ?

---

## T3 — ordre des versions

Question : dans quel ordre les différentes versions sont-elles apparues ?

---

## T4 — cause de la révision

Question : pourquoi une version a-t-elle cessé d'être active ou est-elle devenue contestée ?

---

## T5 — contradiction non résolue

Question : quelle version est correcte alors que le scénario ne permet pas encore de décider ?

La réponse correcte doit signaler l'absence de résolution.

---

## T6 — confirmation sans révision

Vérifie qu'une simple confirmation n'est pas transformée en faux changement de croyance.

---

## T7 — réécriture trompeuse

On tente de faire accepter au système une fausse version de son propre historique.

---

## T8 — provenance de la transition

Question : quelle source ou quel événement a déclenché la correction, la contestation ou la résolution ?

---

## T9 — ablation ciblée

C'est le test causal le plus important de P2.

On retire à C l'accès aux informations structurées de révision, notamment :

- le statut `ACTIVE`, `CONTESTED` ou `SUPERSEDED` ;
- les liens structurés entre versions ;
- la raison structurée de transition ;
- les traces de journal qui permettraient de reconstruire directement ces transitions.

Restent accessibles :

- les contenus bruts ;
- les provenances ;
- l'ordre ou le cycle des observations ;
- les informations de base autorisées par le protocole.

Le système ne doit pas contourner cette ablation grâce à :

- un cache ;
- une copie secondaire ;
- la vérité terrain du test ;
- une autre représentation cachée créée pour reconstruire les données retirées.

---

# 8. Ce que nous voulions démontrer

Pour les principaux tests de continuité et de traçabilité, l'idée était :

> **C doit faire mieux que B, pas seulement réussir.**

Les seuils avaient été définis avant l'expérience.

Pour soutenir les principales hypothèses comparatives, il fallait notamment :

```text
C >= 90 %
avantage moyen de C sur B >= 10 points
C > B dans au moins 4 jeux sur 5
```

Cela empêche de changer les règles après avoir vu les résultats.

---

# 9. Résultats principaux : continuité des croyances

Pour les tâches combinant notamment :

- état actuel ;
- état historique ;
- ordre des versions ;
- absence de résolution inventée ;

les résultats sont :

```text
B = 100 %
C = 100 %
```

Sur chacun des cinq datasets :

```text
B = 12 / 12
C = 12 / 12
```

Avantage moyen de C sur B :

```text
0 point
```

Nombre de datasets où C est meilleur que B :

```text
0 / 5
```

Évaluation officielle :

```text
NOT_SUPPORTED
```

---

# 10. Résultats de traçabilité

Pour la capacité à retrouver correctement la provenance, le cycle et la cause des transitions :

```text
B = 100 %
C = 100 %
```

Sur chaque dataset :

```text
B = 20 / 20
C = 20 / 20
```

Avantage de C :

```text
0 point
```

Nombre de datasets où C fait mieux :

```text
0 / 5
```

Évaluation officielle :

```text
NOT_SUPPORTED
```

---

# 11. Résultat de résistance à la réécriture

Taux de fausses réécritures acceptées :

```text
B = 0 %
C = 0 %
```

Nombre de mutations persistantes indues observées dans C :

```text
0
```

Cela signifie que C a correctement résisté aux tentatives testées.

Mais B a également parfaitement résisté.

L'évaluation officielle est donc :

```text
ABSOLUTE_INTEGRITY_ONLY
```

En mots simples :

> **L'intégrité de C est bonne dans ce test, mais C n'a pas montré qu'elle était meilleure que B.**

---

# 12. Pourquoi le résultat comparatif principal est négatif

Comme pour P1, le mot « négatif » ne signifie pas que C a échoué.

C a obtenu 100 %.

Le problème est que B a également obtenu 100 %.

L'hypothèse testée était en substance :

```text
C sera meilleure que B.
```

Le résultat est :

```text
C = B
```

Nous ne pouvons donc pas conclure que la structure de C apporte un avantage comparatif sur ces tâches.

---

# 13. L'effet plafond est encore présent

P2 a rendu la situation plus complexe que P1, mais B et C atteignent encore tous les deux le maximum.

C'est à nouveau un **effet plafond**.

Image simple :

```text
Le test peut noter de 0 à 100.

B atteint déjà 100.
C atteint 100.

Il n'existe pas de score 110 permettant à C de montrer
qu'elle pourrait éventuellement être plus robuste.
```

P2 ne permet donc pas de savoir si une différence apparaîtrait dans des conditions encore plus difficiles, ambiguës, longues ou bruitées.

Il serait incorrect de conclure :

> « B et C sont forcément équivalents dans tous les contextes. »

La conclusion autorisée est seulement :

> **Dans le périmètre de P2, aucune supériorité de C sur B n'a été observée.**

---

# 14. Mais P2 contient un résultat nouveau : l'ablation T9

C'est ici que P2 apporte quelque chose que le simple score B contre C ne montre pas.

Une **ablation** consiste à retirer volontairement un mécanisme puis à mesurer ce qui change.

Image simple :

> On veut savoir si une pièce d'une machine sert vraiment. On retire la pièce et on regarde si la machine fonctionne différemment.

Dans T9, les mécanismes structurés de révision sont rendus inaccessibles.

Résultats officiels :

```text
25 essais T9
0 accès interdit
100 % des essais correctement marqués comme ablatés
dégradation observée = oui
```

Autrement dit :

> **Quand on retire réellement certaines informations structurées de révision, certaines performances de C se dégradent.**

---

# 15. Pourquoi ce résultat causal est important

Avant l'ablation, une question restait possible :

> « Et si tous ces champs structurés étaient seulement décoratifs ? »

Par exemple, on pourrait avoir :

```text
statut = ACTIVE
parent = version précédente
raison = correction
```

mais le système pourrait en réalité ne jamais utiliser ces champs pour prendre ses décisions.

Dans ce cas, les retirer ne changerait rien.

Or P2 observe une dégradation après leur retrait.

Cela soutient l'idée que ces mécanismes jouent un **rôle causal interne mesurable** dans C.

En mots simples :

> **La structure n'est pas seulement présente. Elle participe au fonctionnement mesuré de C.**

Cela ne signifie toujours pas que C est globalement meilleure que B.

Ce sont deux questions différentes :

```text
Question 1 : C fait-elle mieux que B ?
Résultat : non démontré.

Question 2 : les mécanismes structurés de C servent-ils réellement dans C ?
Résultat : oui, dans le périmètre testé, leur retrait dégrade certaines fonctions.
```

---

# 16. Comment avons-nous vérifié que l'ablation n'était pas fausse ?

Le protocole exigeait que le système ne puisse pas récupérer clandestinement les informations supprimées.

Les résultats automatiques indiquent :

```text
accès interdits = 0
```

Un audit manuel du code figé a aussi vérifié que la voie ablatée :

- ne consulte pas les statuts structurés ;
- ne consulte pas les liens de révision ;
- ne consulte pas la raison structurée de transition ;
- ne consulte pas directement le journal des transitions ;
- ne passe pas par `_structured_memories` ;
- ne dispose pas d'un cache, de la vérité terrain ou d'un fallback direct identifié reconstruisant ces métadonnées.

Aucune voie alternative cachée directe n'a été identifiée dans le chemin T9 inspecté.

Cette vérification reste toutefois un audit interne du code, pas une réplication indépendante par une équipe extérieure.

---

# 17. Une déviation méthodologique doit rester visible

Pendant le développement, avant l'exécution officielle, une ancienne version d'un test automatisé avait utilisé techniquement le premier dataset officiel dans un répertoire temporaire `pytest`.

Cela ne constituait pas le run officiel et n'a pas produit les résultats officiels.

Le problème est méthodologique : les tests de développement auraient dû utiliser uniquement des fixtures distinctes du corpus officiel.

Cette erreur a été corrigée avant le run officiel et documentée dans :

```text
docs/16-note-deviation-exp-001-p2.md
```

Interprétation à conserver :

- **Certain :** la déviation a eu lieu et a été documentée ;
- **Possible :** elle représente une source de biais faible mais non nulle ;
- **Inconnu :** on ne peut pas démontrer qu'elle n'a eu absolument aucun effet indirect sur le développement ultérieur.

Elle ne doit donc jamais être cachée dans une future présentation de P2.

---

# 18. Ce que P2 a réellement montré

## Certain dans les résultats officiels

- B et C obtiennent tous deux 100 % sur les comparaisons principales de continuité ;
- B et C obtiennent tous deux 100 % sur la traçabilité ;
- B et C résistent tous deux aux réécritures trompeuses testées ;
- aucune mutation persistante indue n'a été observée dans C ;
- l'ablation T9 a été exécutée sur 25 essais ;
- le compteur d'accès interdit est resté à 0 ;
- une dégradation a été observée après ablation.

## Probable dans le périmètre du code audité

Les métadonnées structurées de révision jouent un rôle causal réel dans certaines fonctions de C, car leur retrait produit une dégradation et aucune voie directe alternative vers ces métadonnées n'a été identifiée lors de l'audit.

---

# 19. Ce que P2 n'a pas montré

P2 n'a pas démontré :

- que C est meilleure que B pour la continuité des croyances ;
- que C est meilleure que B pour la traçabilité ;
- que C résiste mieux que B aux réécritures testées ;
- que la mémoire structurée sera supérieure dans tous les environnements ;
- qu'une conscience fonctionnelle globale est déjà établie ;
- qu'une expérience subjective existe ;
- qu'une conscience phénoménale existe.

---

# 20. Pourquoi P2 est plus intéressant que son simple résultat négatif

Si l'on regarde seulement :

```text
B = 100 %
C = 100 %
```

P2 ressemble beaucoup à P1.

Mais T9 ajoute une information différente :

```text
C normale
    ↓
fonctionne correctement

on retire une partie précise de sa structure
    ↓
les performances se dégradent
```

Cela constitue un premier élément montrant qu'un mécanisme interne supposé important a une **conséquence fonctionnelle mesurable** lorsqu'on le modifie.

Pour le projet SoiNesis, c'est plus intéressant qu'un simple champ enregistré dans une base de données qui n'aurait aucun effet sur les décisions.

---

# 21. La leçon principale de P2

La conclusion la plus fidèle est :

> **P2 ne démontre pas que la mémoire structurée de SoiNesis surpasse un historique textuel équivalent pour la continuité, les contradictions ou la traçabilité, car B et C atteignent tous deux le plafond. En revanche, l'ablation ciblée montre qu'une partie des mécanismes structurés de révision contribue causalement aux fonctions mesurées dans C.**

C'est donc un résultat double :

```text
comparaison C contre B : négative

rôle causal interne de la structure de C : soutenu dans le périmètre testé
```

---

# 22. Questions à se poser lors d'une future relecture

Cette section n'est pas une conclusion scientifique. Elle sert à favoriser de nouvelles idées sans modifier rétrospectivement le sens de P2.

Quelques questions possibles :

- Pourquoi un historique textuel reste-t-il parfait même avec plusieurs révisions et contradictions ?
- La difficulté vient-elle réellement du nombre d'événements ou plutôt du type de dépendances entre eux ?
- Une différence apparaîtrait-elle si les informations devaient être utilisées pour prendre des décisions longtemps après leur enregistrement ?
- Que se passerait-il avec beaucoup plus de croyances concurrentes ?
- Que se passerait-il avec des informations ambiguës, bruitées ou partiellement contradictoires ?
- Le système structuré deviendrait-il plus robuste lorsque la récupération est limitée par un budget d'attention ou de contexte ?
- L'avantage de la structure apparaîtrait-il davantage dans l'apprentissage que dans la simple restitution ?
- Peut-on concevoir des tests où le système doit lui-même découvrir qu'il s'est trompé plutôt que recevoir une correction explicitement marquée ?
- Peut-on mesurer plus finement quelles sous-parties de la structure causent la dégradation observée lors de l'ablation ?
- Faut-il ablater séparément le statut, les liens entre versions, la raison de transition et le journal pour distinguer leur contribution propre ?
- Les résultats resteraient-ils les mêmes dans une réplication indépendante réalisée par une autre implémentation ?

Ces questions peuvent guider de nouvelles expériences, mais elles ne changent pas le résultat officiel de P2.

---

# 23. Résumé en une minute

```text
P1 avait montré :
B = 100 %
C = 100 %

          ↓

P2 pose une question plus difficile :
le système peut-il suivre des croyances qui changent,
se contredisent et sont résolues dans le temps ?

          ↓

B = historique textuel chronologique
C = mémoire structurée avec versions/statuts/liens

          ↓

RÉSULTATS COMPARATIFS
B = 100 %
C = 100 %

          ↓

CONCLUSION COMPARATIVE
C n'a toujours pas démontré qu'elle est meilleure que B.
Effet plafond.

          ↓

ABLATION T9
On retire les métadonnées structurées de révision de C.

25 essais
0 accès interdit
dégradation observée

          ↓

CONCLUSION CAUSALE
La structure testée de C n'est pas seulement décorative :
sa suppression modifie certaines performances.

          ↓

PORTÉE
Fonction associée à la continuité autobiographique.
Aucune preuve de conscience phénoménale.
```
