# SoiNesis — Initialisation technique

**Fichier :** `docs/11-initialisation-technique.md`  
**Version :** 0.1  
**Date :** 6 août 2026  
**Statut :** procédure opérationnelle initiale

---

## 1. Objectif

Initialiser le socle Python de SoiNesis sans commencer prématurément les mécanismes cognitifs.

Le socle comprend :

- Python 3.14 ;
- une organisation sous `src/` ;
- Pydantic 2 ;
- pytest ;
- Ruff ;
- Pyright ;
- un point d’entrée en ligne de commande ;
- les dossiers des futurs tests ;
- un dossier local pour SQLite.

---

## 2. Prérequis

Vérifier que Python 3.14 est disponible :

```powershell
py -3.14 --version
```

Résultat attendu :

```text
Python 3.14.x
```

---

## 3. Créer l’environnement virtuel

Depuis la racine du dépôt :

```powershell
py -3.14 -m venv .venv
```

Activer l’environnement :

```powershell
.\\.venv\\Scripts\\Activate.ps1
```

Vérifier :

```powershell
python --version
```

---

## 4. Installer le projet

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

L’installation en mode éditable permet d’utiliser directement le code présent dans `src/`.

---

## 5. Vérifier le point d’entrée

```powershell
python -m soinesis
```

ou :

```powershell
soinesis
```

La commande doit afficher l’aide de la ligne de commande.

Vérifier la version :

```powershell
python -m soinesis --version
```

Résultat attendu :

```text
soinesis 0.1.0
```

---

## 6. Exécuter les tests

```powershell
python -m pytest
```

Les deux premiers tests doivent réussir.

---

## 7. Vérifier la qualité

Lint :

```powershell
python -m ruff check .
```

Formatage :

```powershell
python -m ruff format --check .
```

Typage :

```powershell
python -m pyright
```

---

## 8. Arborescence initiale

```text
SoiNesis/
├── pyproject.toml
├── .python-version
├── .gitignore
├── data/
│   └── .gitkeep
├── src/
│   └── soinesis/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── py.typed
│       ├── application/
│       ├── domain/
│       ├── experiments/
│       ├── infrastructure/
│       └── ports/
└── tests/
    ├── unit/
    ├── integration/
    └── experiments/
```

---

## 9. Règles initiales

- Ne pas versionner `.venv`.
- Ne pas versionner la base SQLite réelle.
- Ne pas ajouter FastAPI, PyTorch ou Docker à ce stade.
- Ne pas créer tous les modules cognitifs sous forme de fichiers vides.
- Chaque nouveau composant doit être utilisé par une tranche verticale ou un test.
- Le domaine ne doit pas dépendre de SQLite ou d’un fournisseur de modèle.
- Les tests doivent fonctionner sans accès réseau.

---

## 10. Contrôle avant le premier commit technique

Les commandes suivantes doivent réussir :

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m pyright
python -m soinesis --version
```

Commit recommandé :

```text
Initialiser le socle Python de SoiNesis
```

---

## 11. Étape suivante

Après validation du squelette, implémenter uniquement la première tranche :

```text
Observation
→ Souvenir autobiographique
→ SQLite
→ Récupération
→ Décision simple
→ Journal
→ Ablation
```
