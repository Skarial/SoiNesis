# SoiNesis — Note de déviation pré-run EXP-001-P2

**Date :** 7 août 2026  
**Expérience :** `EXP-001-P2`  
**Statut :** déviation de développement documentée avant toute exécution officielle  
**Gravité :** `WARNING` — intégrité méthodologique, sans résultat officiel produit

---

# 1. Fait observé

Pendant le développement de la couche d’export P2, une première version du test `tests/experiments/test_exp_001_p2_export.py` chargeait le premier jeu du corpus figé officiel `data/exp-001-p2/datasets-v1.json` puis appelait le runner expérimental dans un répertoire temporaire de `pytest`.

Cette exécution était une validation technique automatisée et non une exécution officielle.

Elle utilisait un faux identifiant de commit de test (`"1" * 40`), n’était pas lancée depuis le garde-fou officiel, n’était pas exportée comme bundle officiel et ne constituait pas une campagne P2 enregistrée.

---

# 2. Règle du protocole concernée

La section 16.1 de `docs/15-protocole-exp-001-p2.md` impose que les essais techniques nécessaires au développement utilisent des fixtures distinctes des résultats officiels.

Le comportement initial du test d’export ne respectait donc pas strictement cette séparation, même s’il ne produisait pas de résultat officiel.

---

# 3. Ce qui a été exposé

Le runner a traité transitoirement le premier jeu officiel dans le cadre des tests automatisés.

Aucune métrique comparative officielle n’a été présentée comme résultat P2, aucun rapport scientifique n’a été généré et aucun seuil du protocole n’a été modifié après cette exécution technique.

Les sorties temporaires de `pytest` n’ont pas été intégrées au dépôt comme résultats officiels.

---

# 4. Risque méthodologique

Le risque principal n’est pas une altération du corpus : son SHA-256 préenregistré est resté inchangé.

Le risque est une rupture de la séparation stricte entre données de développement et données destinées à la première exécution officielle.

Cette déviation peut théoriquement augmenter le risque d’ajustement involontaire du code à un jeu officiel. Dans le cas présent, aucun ajustement des seuils ou du protocole n’a été effectué à partir de performances observées, mais la déviation doit rester explicitement visible dans l’historique scientifique.

---

# 5. Correction appliquée

Le test d’export a été modifié avant toute exécution officielle :

- le corpus officiel reste utilisé uniquement pour vérifier son empreinte SHA-256 préenregistrée ;
- les tests qui exécutent le runner construisent désormais un corpus de développement distinct ;
- les identifiants, espaces de noms, sujets et valeurs de ce corpus de développement sont transformés et marqués `dev-*` ;
- aucun résultat de ces fixtures ne doit être interprété comme une mesure scientifique de P2.

Cette correction a été validée par les tests ciblés de la couche d’export.

---

# 6. Conséquence pour l’exécution officielle

La première exécution officielle P2 reste à venir.

Elle devra obligatoirement utiliser :

- le corpus officiel dont le SHA-256 correspond au gel préenregistré ;
- les cinq jeux complets ;
- le code fusionné et figé sur `main` ;
- un dépôt Git propre et synchronisé avec `origin/main` ;
- le garde-fou d’exécution officielle ;
- un répertoire de sortie inexistant avant le run ;
- l’export brut et ses empreintes avant toute analyse.

Cette note doit rester associée au rapport final P2 afin qu’une lecture indépendante puisse tenir compte de la déviation de développement.

---

# 7. Interprétation autorisée

**Certain :** une déviation de séparation développement/officiel a eu lieu pendant les tests techniques et a été corrigée avant le run officiel.

**Certain :** aucun résultat officiel P2 n’a été déclaré à partir de cette exécution technique.

**Possible :** l’exposition technique au premier jeu officiel peut constituer une source de biais méthodologique faible mais non nulle.

**Inconnu :** il n’est pas possible de démontrer qu’une telle exposition n’a eu absolument aucun effet indirect sur le développement ultérieur.

La déviation ne doit donc ni être cachée ni dramatisée ; elle doit être conservée comme limite méthodologique documentée.
