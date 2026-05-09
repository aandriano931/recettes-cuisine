#!/usr/bin/env python3
"""One-shot migration : `source: cookmate` → `source: url`.

Le frontmatter de 22 recettes héritées de l'import Cookmate XML porte
encore `source: cookmate`. Le validator côté agent (projectx) n'accepte
que `manual | url`, donc ces recettes sont silencieusement skippées par
`scripts/admin/import_recipes.py`. Toutes ont déjà `source_url:` rempli
(héritage de Cookmate qui scrapait depuis le web), donc la valeur sémantique
correcte est `url`.

Dry-run par défaut. `--apply` pour réécrire. Idempotent.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = REPO_ROOT / "recipes"

SOURCE_LINE = re.compile(r"^source:\s*cookmate\s*$", re.MULTILINE)
SOURCE_URL_LINE = re.compile(r"^source_url:\s*\S", re.MULTILINE)


def migrate_one(path: Path, *, apply: bool) -> str | None:
    """Return a status string ('changed' | 'no-source-url' | None) for path."""
    text = path.read_text(encoding="utf-8")
    if not SOURCE_LINE.search(text):
        return None  # nothing to do
    if not SOURCE_URL_LINE.search(text):
        return "no-source-url"  # safety: refuse to convert without a URL
    new_text = SOURCE_LINE.sub("source: url", text, count=1)
    if apply:
        path.write_text(new_text, encoding="utf-8")
    return "changed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="actually rewrite the files"
    )
    parser.add_argument("--path", type=Path, default=RECIPES_DIR)
    args = parser.parse_args()

    files = sorted(p for p in args.path.glob("*.md"))
    if not files:
        print(f"no .md files under {args.path}", file=sys.stderr)
        return 1

    n_changed = 0
    flagged: list[str] = []
    for f in files:
        status = migrate_one(f, apply=args.apply)
        if status == "changed":
            n_changed += 1
            marker = "✏️ " if args.apply else "🔍"
            print(f"{marker} {f.name}: source: cookmate → url")
        elif status == "no-source-url":
            flagged.append(f.name)

    print()
    print("══ SUMMARY ══")
    print(f"  Recettes modifiées : {n_changed}")
    if flagged:
        print(f"  ⚠️  Recettes sans source_url ({len(flagged)}) :")
        for f in flagged:
            print(f"      {f}")
        print("    → laisser à `cookmate`, traiter manuellement (passer en `manual` ?)")
        return 2
    if not args.apply:
        print("  → relance avec --apply pour écrire les fichiers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
