#!/usr/bin/env python3
"""
Fix schema errors on the 3 un-overhauled area pages flagged by Semrush.

Changes applied to each file:
  1. Adds the missing `address` block to LocalBusiness schema (Semrush fix)
  2. Changes aggregateRating reviewCount from "250" -> "3" (real count per handover)
  3. Changes visible "Google · 250 reviews" -> "Google · 3 reviews"
  4. Inserts a TODO comment before the visible reviews section flagging that
     the review CARDS still contain fabricated reviewer names - replace with
     real reviewers (James Alexander, John Manley, Elaine McHugh) per playbook.

Run from repo root: python3 fix-schema.py
"""
import sys
from pathlib import Path

FILES = [
    "src/pages/emergency-plumber-formby.astro",
    "src/pages/emergency-plumber-st-helens.astro",
    "src/pages/emergency-plumber-wirral.astro",
]

# --- 1. Add address block to LocalBusiness ---
# Insert immediately after `"priceRange": "££",` in the LocalBusiness schema.
ADDRESS_OLD = '''    "priceRange": "££",
    "openingHoursSpecification"'''

ADDRESS_NEW = '''    "priceRange": "££",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "29 Park Road",
      "addressLocality": "Kirkby",
      "addressRegion": "Merseyside",
      "postalCode": "L32 2AL",
      "addressCountry": "GB"
    },
    "openingHoursSpecification"'''

# --- 2. Fix fabricated review count in schema ---
REVIEW_COUNT_OLD = '"reviewCount": "250"'
REVIEW_COUNT_NEW = '"reviewCount": "3"'

# --- 3. Fix visible review count ---
VISIBLE_COUNT_OLD = "Google · 250 reviews"
VISIBLE_COUNT_NEW = "Google · 3 reviews"

# --- 4. TODO marker before reviews section ---
TODO_ANCHOR = "  <!-- REVIEWS -->"
TODO_REPLACEMENT = """  <!-- TODO: Review cards below still contain fabricated reviewer names.
       Per playbook ("Real reviews only - 3 we have, never fabricate"), replace
       with real Google reviews: James Alexander (burst pipe response 30 min),
       John Manley (new shower fitted in 2 hours), Elaine McHugh ("Excellent service"). -->
  <!-- REVIEWS -->"""


def fix_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    original = text
    results = {}

    # 1. Address
    if ADDRESS_OLD in text:
        text = text.replace(ADDRESS_OLD, ADDRESS_NEW, 1)
        results["address"] = "added"
    else:
        results["address"] = "ANCHOR NOT FOUND - manual check needed"

    # 2. Review count in schema
    schema_count = text.count(REVIEW_COUNT_OLD)
    if schema_count:
        text = text.replace(REVIEW_COUNT_OLD, REVIEW_COUNT_NEW)
        results["reviewCount_schema"] = f"replaced {schema_count}x"
    else:
        results["reviewCount_schema"] = "not found"

    # 3. Visible review count
    visible_count = text.count(VISIBLE_COUNT_OLD)
    if visible_count:
        text = text.replace(VISIBLE_COUNT_OLD, VISIBLE_COUNT_NEW)
        results["reviewCount_visible"] = f"replaced {visible_count}x"
    else:
        results["reviewCount_visible"] = "not found"

    # 4. TODO marker
    if "TODO: Review cards below" not in text and TODO_ANCHOR in text:
        text = text.replace(TODO_ANCHOR, TODO_REPLACEMENT, 1)
        results["todo_marker"] = "inserted"
    elif "TODO: Review cards below" in text:
        results["todo_marker"] = "already present"
    else:
        results["todo_marker"] = "anchor not found"

    if text != original:
        path.write_text(text, encoding="utf-8")
        results["status"] = "MODIFIED"
    else:
        results["status"] = "unchanged"

    return results


def main():
    root = Path(".").resolve()
    if not (root / "src" / "pages").exists():
        print("ERROR: Run this from the repo root (the directory containing src/).")
        sys.exit(1)

    print(f"Working in: {root}\n")

    for rel in FILES:
        path = root / rel
        if not path.exists():
            print(f"SKIPPED (not found): {rel}")
            continue
        results = fix_file(path)
        print(f"{rel}")
        for k, v in results.items():
            print(f"  {k}: {v}")
        print()


if __name__ == "__main__":
    main()
