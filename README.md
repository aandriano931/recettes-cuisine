# recettes-cuisine

Source de vérité des recettes familiales. Chaque recette est **un fichier markdown** versionné dans ce repo. Le projet [Maison](https://github.com/aandriano931/home-ia) importe ce repo dans sa base SQLite pour que l'assistant Signal puisse s'en servir — mais les fichiers ici restent le référentiel pérenne, indépendamment de tout outil.

## Pourquoi ce repo existe

- **Pérennité** : du texte plat versionné en git survit à n'importe quel outil. Si le projet Maison disparaît, les recettes restent.
- **Édition naturelle** : on tape la recette dans un éditeur (VS Code, Obsidian, nano…), pas dans l'app.
- **Portabilité** : un fichier markdown est importable dans tous les outils de recettes modernes (Paprika, Mealie, etc.) ou un générateur de site statique.
- **Historique git** : chaque correction, ajustement de quantités, variante → un commit qui raconte l'histoire de la recette.

## Structure

```
recettes-cuisine/
├── README.md              # ce fichier
├── CONVENTIONS.md         # règles d'écriture et schéma des ingrédients (source de vérité)
├── .gitignore
├── drafts/                # brouillons générés par l'agent (non importés)
└── recipes/
    ├── _template.md       # squelette à copier pour une nouvelle recette
    ├── tajine-maison.md
    ├── pates-carbonara.md
    └── ...
```

Une recette = **un fichier dans `recipes/`**. Pas de sous-dossiers par catégorie — les tags dans le frontmatter servent à ça.

## Ajouter une nouvelle recette

1. Copier le template :
   ```bash
   cp recipes/_template.md recipes/nom-de-ma-recette.md
   ```
2. Le nom du fichier est **l'identifiant stable** de la recette. Règle : minuscules, tirets, sans accents. Exemples : `tajine-maison.md`, `pates-carbonara.md`, `gateau-chocolat-fondant.md`.
3. Éditer le fichier (voir **Format** ci-dessous).
4. Commit + push :
   ```bash
   git add recipes/nom-de-ma-recette.md
   git commit -m "feat: add recipe 'Nom de ma recette'"
   git push
   ```
5. Importer dans la base du projet Maison (depuis le repo Maison) :
   ```bash
   cd ~/workspace/projectx/agent
   PYTHONPATH=. .venv/bin/python scripts/admin/import_recipes.py --path ~/workspace/recettes-cuisine/recipes/ --apply
   ```

## Peupler le repo depuis la base Maison

Si tu as déjà des recettes en base Maison (imports Cookmate, recettes ajoutées par Alfred via `add_recipe`…) et que tu veux les matérialiser ici, le script `scripts/admin/export_recipes.py` côté projet Maison fait le travail.

**Le pas-à-pas complet (snapshot prod via SSH → scp en local → export filtré → commit ici → cleanup) est documenté dans le runbook du projet Maison** : section [_Exporter des recettes vers le repo markdown_](https://github.com/aandriano931/home-ia/blob/main/docs/runbook.md#exporter-des-recettes-vers-le-repo-markdown).

⚠ **Round-trip cassé pour les recettes Cookmate et Alfred** : leur `source_id` en base n'est pas slug-conforme (UUID Cookmate ou `NULL` pour Alfred). Le `.md` exporté a donc un slug ≠ ID DB → le ré-importer créerait un **doublon**. Le runbook décrit le "bootstrap dance" (delete en base + re-import) pour rendre une recette éditable depuis ce repo.

Tant que tu fais juste un export pour archiver, aucune danse n'est nécessaire — le `.md` reste une copie statique.

## Format

Chaque recette est un fichier `.md` avec deux zones :

- **Frontmatter** (entre deux lignes `---`) : métadonnées structurées, lues par le script d'import.
- **Corps markdown** : titre, ingrédients, préparation, notes — lisible par un humain sans rendu.

### Frontmatter

```yaml
---
title: Tajine maison
servings: 4
duration_minutes: 90
source: manual
source_url: null
tags: [famille, hiver, maghreb]
role: main
ingredients:
  - name: poulet
    qty: 800
    unit: g
    note: cuisses désossées
  - name: oignon
    qty: 2
  - name: ras el hanout
    qty: 1
    unit: cs
  - name: sel
---
```

| Champ | Obligatoire | Type | Description |
|---|---|---|---|
| `title` | oui | string | Titre de la recette. Peut avoir accents et espaces. |
| `servings` | oui | int | Nombre de portions. |
| `duration_minutes` | oui | int | Temps total (prépa + cuisson) en minutes. |
| `source` | oui | enum | `manual` (recette écrite par toi), `url` (recette trouvée sur le web), `cookmate` (importée depuis un export Cookmate), `agent_draft` (brouillon généré par l'agent). |
| `source_url` | non | string ou `null` | URL d'origine si `source: url`. Sinon `null`. |
| `tags` | non | list[string] | Liste plate `[tag1, tag2]`. Libre, minuscules conseillées. |
| `role` | non | enum | `main` (défaut), `dessert`, `preparation`. Catégorisation de la recette. |
| `ingredients` | oui | list | Liste structurée d'ingrédients. Voir **Schéma ingredients** ci-dessous et `CONVENTIONS.md` pour les règles d'arbitrage détaillées. |

### Schéma `ingredients`

Chaque entrée de la liste :

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `name` | string | oui | Nom canonique en minuscules, sans article partitif, singulier sauf si invariable. |
| `qty` | number | non | Quantité numérique (entier ou décimal). |
| `unit` | string | non | Vocabulaire fermé — voir ci-dessous. |
| `note` | string | non | Texte descriptif libre (`émincé`, `pour la cuisson`). Pas utilisé pour la liste de courses. |
| `optional` | bool | non | `true` exclut l'ingrédient de la liste de courses. |

**Vocabulaire fermé d'unités** (25 unités — toute autre valeur est rejetée par le linter) :

- **Poids** : `mg`, `g`, `kg`
- **Volume** : `ml`, `cl`, `dl`, `l`
- **Cuisine** : `cs`, `cc`, `tasse`, `verre`
- **Pack** : `sachet`, `boite`, `pot`, `canette`, `bouteille`
- **Bouquet** : `bouquet`, `botte`, `branche`, `brin`, `tige`, `feuille`
- **Discret** : `pincee`, `gousse`, `tranche`

Voir `CONVENTIONS.md` pour les règles d'arbitrage (fourchettes, fractions, achat vs usage, etc.).

### Corps — sections obligatoires

````markdown
# Tajine maison

## Ingrédients

(Auto-généré depuis le YAML — ne pas éditer à la main.)

## Préparation

1. Faire revenir les oignons émincés dans l'huile d'olive
2. Ajouter le poulet, saisir 5 min de chaque côté
3. ...
````

- **Titre H1** : reprend `title` du frontmatter (redondance volontaire — garde-fou si l'un des deux est modifié sans l'autre).
- **`## Ingrédients`** : rendu lisible généré automatiquement depuis la clé `ingredients:` du frontmatter. **Ne pas éditer cette section à la main** — les modifications seraient écrasées au prochain passage du script. Pour changer un ingrédient, éditer le YAML dans le frontmatter.
- **`## Préparation`** : texte libre. Liste numérotée conseillée, mais pas obligatoire.

### Corps — sections optionnelles

Toutes les autres sections sont libres et **ignorées par le script d'import** — elles existent pour le lecteur humain.

```markdown
## Notes

Peut se préparer la veille, encore meilleur réchauffé.

## Variantes

- Version agneau : remplacer le poulet par 1 kg d'épaule d'agneau, mijoter 2h.

## Origine

Recette transmise par Mamie Hawa, ajustée au fil des années.
```

### Recettes complexes (composants multiples)

Pour une recette avec marinade + plat + sauce, tous les ingrédients restent dans la liste `ingredients:` du frontmatter. Utiliser le champ `note` pour préciser le composant :

```yaml
ingredients:
  - name: huile d'olive
    qty: 2
    unit: cs
    note: pour la marinade
  - name: citron
    qty: 1
    note: pour la marinade
  - name: poulet
    qty: 800
    unit: g
    note: pour le plat
  - name: oignon
    qty: 2
    note: pour le plat
```

Le script d'import regroupe tous les ingrédients sous la recette parente.

## Règles de nommage

- **Slug de fichier** : minuscules, tirets, pas d'accents, pas d'espaces, pas d'underscore.
  - ✅ `tajine-maison.md`, `gateau-chocolat-fondant.md`
  - ❌ `Tajine Maison.md`, `tajine_maison.md`, `tartiflette-à-la-Savoyarde.md`
- **Pas de suffixe numéroté** (`tajine-1.md`, `tajine-2.md`) → préférer des noms distinctifs (`tajine-poulet.md`, `tajine-agneau.md`).

## Bonnes pratiques d'édition

- **Un commit = un changement logique**. Ajout d'une recette, correction d'une faute, ajustement de quantités — chacun son commit avec un message clair.
- **Messages de commit** :
  - `feat: add recipe 'Tajine maison'`
  - `fix: correct tajine quantities (was 500g, should be 800g)`
  - `docs: add variante agneau in tajine-maison`
- **Pas de rush** : rien n'est en production tant que tu ne lances pas `import_recipes.py` côté Maison.

## Pièges courants

- **Oublier les `---`** en début/fin de frontmatter → parseur échoue. Un fichier non parseable est skippé avec un warning, jamais silencieux.
- **Indentation dans `tags`** : rester en syntaxe inline `tags: [famille, hiver]`. Éviter la forme imbriquée (piège YAML).
- **Guillemets dans le titre** : si le titre contient `:` (ex. `Pâtes : sauce tomate`), mettre entre guillemets : `title: "Pâtes : sauce tomate"`.
- **Renommer un fichier** = créer une nouvelle recette côté base (le slug change). Si tu dois renommer, prévois un `import --apply` pour nettoyer l'ancienne entrée.

## Outils conseillés

- **VS Code** ou **Obsidian** : rendu markdown live, coloration frontmatter.
- **Obsidian** : particulièrement adapté — ouvre ce repo comme un vault, graphe des tags, recherche plein-texte.
- Tout éditeur texte fait l'affaire (nano, vim, TextEdit, Notepad).

## Licence

Contenu privé. Ne pas publier, ne pas diffuser. Certaines recettes peuvent être adaptées de sources tierces (sites web, livres) et ne sont pas redistribuables.
