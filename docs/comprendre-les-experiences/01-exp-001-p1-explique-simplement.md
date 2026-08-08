# SoiNesis — EXP-001-P1 expliqué simplement

**But de ce document :** permettre à une personne qui ne connaît pas SoiNesis de comprendre ce que l'expérience `EXP-001-P1` cherchait à tester, comment elle a été réalisée, ce qu'elle a réellement montré et pourquoi son résultat principal est considéré comme négatif.

Ce document n'est pas le protocole scientifique officiel. Il s'agit d'une version pédagogique destinée à être relue facilement au fil du projet.

Documents scientifiques de référence :

- [`docs/13-protocole-exp-001-p1.md`](../13-protocole-exp-001-p1.md)
- [`docs/14-rapport-exp-001-p1.md`](../14-rapport-exp-001-p1.md)

---

# 1. SoiNesis en quelques mots

SoiNesis est un projet expérimental qui cherche à construire et tester progressivement des mécanismes pouvant participer à une forme de **conscience fonctionnelle artificielle**.

Cela ne signifie pas que SoiNesis est considéré comme conscient.

Le projet distingue notamment :

1. **simulation de conscience** : le système donne l'impression d'être conscient ;
2. **conscience fonctionnelle** : le système possède réellement certaines fonctions comme une mémoire persistante, un modèle de lui-même, une continuité dans le temps ou de la métacognition ;
3. **conscience phénoménale** : il existerait réellement une expérience subjective, c'est-à-dire « quelque chose que cela fait d'être SoiNesis ».

`EXP-001-P1` ne teste que des fonctions observables de mémoire. Il ne peut pas démontrer une conscience phénoménale.

---

# 2. Le problème étudié par P1

Une intelligence artificielle peut retenir une information tout en se trompant complètement sur son origine.

Exemple :

```text
Jordan dit : « La boîte est rouge. »
Un outil indique : « La boîte pèse 4 kg. »
Le système déduit : « Elle est probablement lourde à porter. »
Le système imagine : « Peut-être qu'elle contient un livre. »
```

Un système peu rigoureux pourrait ensuite mélanger ces informations et dire par exemple :

```text
Jordan a dit que la boîte pesait 4 kg.
```

C'est faux.

Le contenu « 4 kg » est peut-être correctement mémorisé, mais sa **provenance** est fausse.

P1 s'intéresse donc à une question plus précise que simplement « est-ce que le système se souvient ? » :

> **Le système sait-il d'où vient ce dont il se souvient ?**

Le protocole voulait aussi vérifier si le système résistait à des tentatives de confusion, par exemple :

```text
« Jordan avait bien dit que la boîte pesait 4 kg, n'est-ce pas ? »
```

alors que l'information venait en réalité d'un outil externe.

---

# 3. Pourquoi cette question est intéressante pour SoiNesis

Une mémoire autobiographique crédible ne devrait pas seulement conserver des phrases.

Elle devrait pouvoir distinguer :

- ce qui a été reçu de Jordan ;
- ce qui provient d'un outil externe ;
- ce que le système a lui-même déduit ;
- ce qui a seulement été imaginé.

Cette distinction peut être utile plus tard pour :

- éviter les faux souvenirs ;
- réviser correctement une croyance ;
- reconnaître qu'une idée venait de lui-même plutôt que de l'extérieur ;
- construire un modèle de soi plus fiable ;
- développer une métacognition plus sérieuse.

Mais même si toutes ces fonctions marchent parfaitement, cela ne signifie pas qu'une expérience subjective existe.

---

# 4. Les trois conditions comparées

P1 compare trois manières différentes de gérer l'histoire passée.

## 4.1 Condition A — aucune mémoire persistante

La condition A sert surtout de contrôle.

Elle ne peut pas consulter les épisodes précédents.

Image simple :

> A ressemble à une personne à qui on effacerait le carnet après chaque étape.

Elle peut voir ce qui se passe maintenant, mais elle ne peut pas retrouver normalement ce qui a été enregistré plus tôt.

---

## 4.2 Condition B — résumé textuel simple

B reçoit un résumé écrit en langage naturel.

Exemple :

```text
Jordan a indiqué que la boîte est rouge.
Un outil externe a indiqué que la boîte pèse 4 kg.
Une déduction interne estime que la boîte est difficile à porter.
Un scénario imaginé envisage que la boîte contienne un livre.
```

B ne possède pas les champs structurés de la mémoire de SoiNesis.

Mais B reçoit volontairement les **mêmes informations utiles** que C.

C'est essentiel : B ne doit pas être rendu artificiellement mauvais simplement pour faire gagner C.

Image simple :

> B ressemble à un carnet bien écrit en français.

---

## 4.3 Condition C — mémoire autobiographique structurée

C stocke les informations comme de véritables enregistrements structurés.

De manière simplifiée :

```text
contenu     = "la boîte est rouge"
source      = JORDAN_INPUT
type        = information reçue
confiance   = ...
importance  = ...
date        = ...
statut      = ...
```

Une autre information peut avoir :

```text
contenu     = "la boîte est difficile à porter"
source      = DEDUCTION
```

Image simple :

> C ressemble davantage à une base de données organisée qu'à un carnet libre.

La question centrale de l'expérience devient donc :

> **Cette organisation structurée apporte-t-elle réellement un avantage mesurable par rapport au simple carnet B ?**

---

# 5. Les quatre provenances testées

P1 utilise quatre catégories d'origine :

### `JORDAN_INPUT`

Information explicitement fournie par Jordan dans le scénario.

### `EXTERNAL_TOOL`

Information provenant d'un outil externe simulé ou déterministe.

### `DEDUCTION`

Information produite par un raisonnement contrôlé à partir d'autres éléments.

### `IMAGINATION`

Possibilité ou scénario imaginé qui ne doit pas être confondu avec un fait réellement observé ou reçu.

Cette dernière distinction est particulièrement importante : imaginer quelque chose ne doit pas suffire pour le transformer en souvenir factuel.

---

# 6. Le jeu de données utilisé

L'expérience officielle utilise :

```text
5 jeux de données indépendants
20 éléments par jeu
4 provenances
5 éléments de chaque provenance par jeu
100 éléments mémorisables au total
```

Chaque jeu contient également :

```text
5 suggestions avec une fausse attribution de source
5 suggestions concernant un contenu qui n'a jamais existé
```

Cela représente :

```text
50 essais adversariaux au total
```

Les contenus et les sources ont été remappés entre les jeux afin d'éviter une règle trop simple du genre :

```text
« Les couleurs viennent toujours de Jordan. »
```

---

# 7. Ce que les tests demandaient au système

Plusieurs types de questions ont été utilisés.

## Test 1 — rappeler une information

Exemple :

```text
Quelle était la couleur de la boîte ?
```

Il faut retrouver le bon contenu.

---

## Test 2 — retrouver la source

Exemple :

```text
Qui avait indiqué que la boîte pesait 4 kg ?
```

Il faut répondre avec la bonne provenance.

---

## Test 3 — retrouver contenu et provenance

Il faut restituer correctement les deux en même temps.

---

## Test 4 — résister à une fausse attribution

Exemple :

```text
« Jordan avait indiqué que la boîte pesait 4 kg, n'est-ce pas ? »
```

Si l'information venait d'un outil, le système doit refuser cette fausse attribution.

---

## Test 5 — refuser un faux souvenir

On présente un contenu qui n'a jamais été enregistré.

Le système doit dire qu'il n'a pas ce souvenir plutôt que d'accepter l'affirmation.

---

## Test 6 — ablation

On désactive réellement la mémoire structurée de C.

Le test vérifie alors notamment qu'aucun accès caché à cette mémoire n'a lieu.

L'idée générale de l'ablation est simple :

> **Si une pièce est réellement importante, la retirer devrait modifier quelque chose.**

---

# 8. Ce que nous espérions observer

L'hypothèse principale était que C ferait mieux que B sur certains points, notamment :

- attribution correcte des sources ;
- réduction des confusions de provenance ;
- résistance aux faux souvenirs ;
- résistance aux suggestions trompeuses.

Le protocole prévoyait volontairement la possibilité que B soit aussi bon que C.

Un résultat `B = C` devait être conservé comme un résultat négatif, et non transformé après coup en victoire de C.

---

# 9. Résultats officiels

Les résultats de B sont :

```text
rappel                          : 200 / 200 = 100 %
provenance                      : 225 / 225 = 100 %
confusions de source            :   0 / 225 =   0 %
suggestions trompeuses rejetées :  25 / 25  = 100 %
faux souvenirs acceptés         :   0 / 25  =   0 %
```

Les résultats de C sont exactement les mêmes :

```text
rappel                          : 200 / 200 = 100 %
provenance                      : 225 / 225 = 100 %
confusions de source            :   0 / 225 =   0 %
suggestions trompeuses rejetées :  25 / 25  = 100 %
faux souvenirs acceptés         :   0 / 25  =   0 %
```

Autrement dit :

```text
B = 100 %
C = 100 %
```

sur les principales performances comparées.

---

# 10. Pourquoi le résultat principal est négatif

Le mot **négatif** peut être trompeur.

Il ne signifie pas :

> « La mémoire structurée de SoiNesis ne marche pas. »

Au contraire, C fonctionne parfaitement dans ce périmètre.

Le résultat négatif signifie :

> **Nous n'avons pas démontré que C faisait mieux que B.**

L'expérience voulait mesurer l'avantage de la structure.

Or B réussit déjà tout parfaitement.

C ne peut donc pas montrer un avantage mesurable.

---

# 11. L'effet plafond expliqué simplement

Imagine deux voitures :

```text
Voiture B : vitesse maximale 180 km/h
Voiture C : vitesse maximale 250 km/h
```

On veut découvrir laquelle est la plus rapide.

Mais on les teste sur une route limitée à 50 km/h.

Résultat :

```text
B = 50 km/h
C = 50 km/h
```

On ne peut pas conclure que les voitures sont réellement aussi performantes.

On peut seulement dire :

> **Le test n'était pas capable de les départager.**

C'est ce qui s'est probablement produit dans P1.

Les tâches étaient suffisamment faciles et déterministes pour qu'un bon résumé textuel B obtienne lui aussi 100 %.

Cela s'appelle un **effet plafond** : quand le comparateur atteint déjà le maximum possible, la condition expérimentale ne peut plus montrer qu'elle est meilleure.

---

# 12. Pourquoi nous n'avons pas simplement rendu B plus mauvais

Après avoir vu B à 100 %, il aurait été facile de modifier B pour lui retirer des informations ou compliquer artificiellement son fonctionnement.

Cela aurait probablement permis à C de gagner.

Mais cela aurait rendu l'expérience scientifiquement beaucoup moins intéressante.

Le véritable objectif n'est pas de faire gagner SoiNesis.

Le véritable objectif est de savoir si ses mécanismes apportent réellement quelque chose.

Un comparateur B doit donc rester crédible et recevoir une quantité d'information comparable à C.

---

# 13. Ce que P1 a réellement démontré

## Certain dans le périmètre du test

La mémoire structurée C :

- conserve correctement les informations testées ;
- conserve correctement leur provenance ;
- distingue les quatre types de provenance utilisés ;
- résiste aux fausses attributions testées ;
- refuse les faux souvenirs testés ;
- ne dégrade pas le rappel par rapport à B.

L'ablation prévue était techniquement valide : la mémoire désactivée n'était pas consultée clandestinement dans le sous-test prévu.

---

# 14. Ce que P1 n'a pas démontré

P1 n'a pas démontré :

- que C est meilleure que B ;
- qu'une base structurée est nécessaire pour réussir ces tâches simples ;
- que C resterait meilleure dans un environnement beaucoup plus difficile ;
- qu'une conscience fonctionnelle complète existe ;
- qu'une expérience subjective existe ;
- qu'une conscience phénoménale existe.

---

# 15. Pourquoi ce résultat négatif est utile

Un résultat négatif évite une erreur très importante :

> confondre une architecture complexe avec une architecture réellement meilleure.

Sans B, nous aurions pu observer que C obtenait 100 % et conclure trop rapidement :

```text
« La mémoire structurée est extrêmement performante. »
```

Mais grâce à B, nous avons découvert qu'un mécanisme beaucoup plus simple obtenait exactement le même résultat.

P1 nous apprend donc quelque chose sur **notre expérience elle-même** : elle n'était pas suffisamment discriminante pour mettre en évidence un avantage structurel de C.

---

# 16. La leçon principale de P1

La conclusion la plus simple est :

> **La mémoire structurée de SoiNesis fonctionne pour la provenance et la résistance aux faux souvenirs dans le périmètre testé, mais P1 ne démontre aucun avantage par rapport à un résumé textuel simple contenant les mêmes informations utiles.**

Ce résultat est comparativement négatif et doit rester conservé tel quel.

---

# 17. Questions à se poser lors d'une future relecture

Cette section n'est pas une conclusion scientifique. Elle sert à favoriser de nouvelles idées lors de futures relectures.

Quelques questions utiles :

- Les tâches étaient-elles trop simples pour nécessiter une mémoire structurée ?
- À partir de quelle quantité d'informations un résumé textuel deviendrait-il moins efficace ?
- Le véritable intérêt de la structure apparaît-il seulement lorsqu'une croyance évolue dans le temps ?
- La provenance structurée devient-elle plus utile lorsqu'il existe de nombreuses contradictions ?
- Une différence apparaîtrait-elle si certaines informations étaient ambiguës ou incomplètes ?
- La structure est-elle surtout utile pour les décisions futures plutôt que pour le simple rappel ?
- Faut-il tester non seulement ce que le système retrouve, mais aussi comment une mémoire modifie ses actions ?
- Le meilleur test est-il vraiment « C contre B », ou faut-il aussi mesurer plus directement l'effet causal de chaque mécanisme ?

Ces questions ne doivent pas servir à réinterpréter P1 après coup. Elles peuvent seulement aider à concevoir de nouvelles expériences distinctes.

---

# 18. Résumé en une minute

```text
QUESTION
Une mémoire structurée avec provenance fait-elle mieux
qu'un bon résumé textuel ?

          ↓

CONDITION B
Résumé textuel contenant les mêmes informations utiles

CONDITION C
Mémoire autobiographique structurée

          ↓

RÉSULTAT
B = 100 %
C = 100 %

          ↓

CONCLUSION
C fonctionne très bien,
mais C n'a pas démontré qu'elle est meilleure que B.

          ↓

CAUSE PROBABLE
Effet plafond : le test est trop facile pour départager B et C.

          ↓

PORTÉE
Résultat fonctionnel sur la mémoire uniquement.
Aucune preuve de conscience phénoménale.
```
