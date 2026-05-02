# Conventions — recettes-cuisine

Règles d'écriture des fichiers `recipes/*.md`. Source de vérité pour le format ;
le linter (`projectx:agent/scripts/admin/lint_recipes.py`) les enforce avant
chaque import en DB.

## Structure d'un fichier

Chaque recette est un `.md` avec :

- **frontmatter YAML** — métadonnées + `ingredients:` (liste structurée)
- **`## Ingrédients`** — bullets générés depuis le YAML, ne pas éditer à la main
- **`## Préparation`** — étapes numérotées, en français
- **`## Notes`** (optionnel) — texte libre

## Schéma `ingredients`

Chaque entrée a les champs :

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `name` | string | oui | Nom canonique en minuscules, sans article partitif (du/de la/des/de l'), singulier sauf si invariable, ≤ 80 chars. Pas de chiffre, pas d'unité dans le nom. |
| `qty` | number | non | Numérique (entier ou décimal). Fractions Unicode → décimaux (`0.5`, `1.5`). |
| `unit` | string | non | Vocabulaire fermé (voir `_template.md`). |
| `note` | string | non | Texte libre descriptif (`émincé`, `jaune coupé en dés`, `pour la cuisson`), ≤ 100 chars. **Pas utilisé pour la liste de courses** — purement informatif. |
| `optional` | bool | non | `true` exclut l'ingrédient de la liste de courses. |

## Vocabulaire fermé d'unités

Toute unité hors de cette liste est rejetée par le linter (25 unités) :

- **Poids** : `mg`, `g`, `kg`
- **Volume** : `ml`, `cl`, `dl`, `l`
- **Cuisine** : `cs`, `cc`, `tasse`, `verre`
- **Pack** : `sachet`, `boite`, `pot`, `canette`, `bouteille`
- **Bouquet** : `bouquet`, `botte`, `branche`, `brin`, `tige`, `feuille`
- **Discret** : `pincee`, `gousse`, `tranche`

Quand le source utilise une unité absente (`tbsp`, `cup`, `cuillerée à soupe`) :
remplacer par l'équivalent canonique (`cs`, `tasse`, `cs`).

## Règles d'arbitrage

Quand le texte source est ambigu, suivre ces règles :

### 1. Encoder ce qu'on achète, pas la prose

Source : `Une très belle queue de lotte parée et nettoyée (compter en moyenne 200 g brut ou 150 g minimum net par personne)`

YAML :
```yaml
- name: queue de lotte
  qty: 200
  unit: g
  note: parée et nettoyée, par personne
```

### 2. Prendre la borne haute des fourchettes

Source : `2 à 3 cl d'huile d'olive ou d'arachide`

YAML :
```yaml
- name: huile d'olive
  qty: 3
  unit: cl
  note: ou huile d'arachide
```

Mieux d'avoir un peu trop que pas assez.

### 3. Encoder l'achat entier, pas l'usage partiel

Source : `le zeste d'un demi citron vert`

YAML :
```yaml
- name: citron vert
  qty: 0.5
  note: zeste seulement
```

On achète 1 citron, on en utilise la moitié — encoder ce qu'on doit acheter.

### 4. Inclure les épices comptées

`sel`, `poivre`, `thym`, `cumin` (déjà sur l'étagère) → entrées sans `qty`,
juste `name`.

`pincée de safran` (à acheter spécifiquement) → `qty: 1, unit: pincee`.

### 5. Cas dérivés

- `1 ½ tasse` → `qty: 1.5, unit: tasse` (fractions Unicode → décimaux)
- `une pincée` → `qty: 1, unit: pincee` (mots-quantité → numériques)
- `1 canne de 400 ml de lait de coco` → `qty: 400, unit: ml, name: lait de coco`
  (encoder la quantité utile, pas l'emballage)

### 6. Ingrédients composés

Quand un produit est connu par sa marque ou un nom long :

- Préférer le nom canonique de la course (`tomate concassée`, pas `boîte de tomates italiennes pelées`).
- La précision (marque, AOP, etc.) part en `note`.

## Validation

Avant tout commit, depuis `~/workspace/projectx/agent` :

```bash
PYTHONPATH=. .venv/bin/python scripts/admin/lint_recipes.py
```

Doit retourner `Summary: N OK / 0 warnings / 0 errors` et exit 0.

Pour CI strict (recommandé) :

```bash
PYTHONPATH=. .venv/bin/python scripts/admin/lint_recipes.py --strict
```
