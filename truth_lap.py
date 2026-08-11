#!/usr/bin/env python3
"""
truth_lap.py - Liverpool Emergency Plumber site-wide truth pass

Enforces one canonical fact set across every page.

CANONICAL FACTS (confirmed by Mike, 11 Aug 2026):
  Company name   : Liverpool Emergency Plumber
  Phone          : 0151 558 0334  (+441515580334)
  Google reviews : 26
  Public liability: £2 million
  Guarantee      : 12 months
  Emergency claims: "30 minute response" and "£80 fixed" are ACCURATE - left alone

REMOVED / CORRECTED:
  - "Ideal Plumbing Solutions"        -> Liverpool Emergency Plumber
  - 07399 676656 (electrical mobile)  -> 0151 558 0334
  - 250 / 280 review claims           -> 26
  - AggregateRating schema            -> deleted (banned)
  - Absolute no-subcontractor claims  -> softened to a verifiable claim

Usage:
    python3 truth_lap.py            # dry run, prints full report, writes nothing
    python3 truth_lap.py --apply    # backs up to .truth_lap_backup/ then writes
"""

import argparse
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

SRC = Path("src")
BACKUP = Path(".truth_lap_backup")

REAL_PHONE_DISPLAY = "0151 558 0334"
REAL_PHONE_INTL = "+441515580334"
REAL_NAME = "Liverpool Emergency Plumber"
REAL_REVIEWS = "26"

# ---------------------------------------------------------------------------
# Rules: (id, description, compiled pattern, replacement)
# Replacement may be a string or a callable taking the match object.
# ---------------------------------------------------------------------------

RULES = [
    # --- Wrong phone number (Ideal Electrical's mobile) --------------------
    ("phone-display", "07399 676656 -> 0151 558 0334",
     re.compile(r"07399\s*676656"), REAL_PHONE_DISPLAY),

    ("phone-intl", "+447399676656 -> +441515580334",
     re.compile(r"\+?447399\s*676656"), REAL_PHONE_INTL),

    ("phone-tel-href", "tel: link with wrong number",
     re.compile(r'(tel:)\s*0?7399\s*676656'), r"\g<1>" + REAL_PHONE_DISPLAY),

    # --- Wrong company name -------------------------------------------------
    ("name-ideal-plumbing", "Ideal Plumbing Solutions -> Liverpool Emergency Plumber",
     re.compile(r"Ideal\s+Plumbing\s+Solutions"), REAL_NAME),

    ("name-ideal-plumbing-ltd", "Ideal Plumbing Ltd -> Liverpool Emergency Plumber",
     re.compile(r"Ideal\s+Plumbing(?:\s+Ltd\.?)?(?!\s+Solutions)\b"), REAL_NAME),

    # --- Inflated review counts --------------------------------------------
    # Label form first: it is followed by a stray "Google" that the prose
    # rule would otherwise leave stranded ("26 Google reviews Google").
    ("reviews-label", "'250 Five-Star Reviews Google' label -> 26 Google Reviews",
     re.compile(r"2[58]0\s+Five[- ]Star\s+Reviews(\s+Google)?", re.I),
     f"{REAL_REVIEWS} Google Reviews"),

    ("reviews-prose", "'over 250/280 five-star reviews' -> 26 Google reviews",
     re.compile(r"(?:[Oo]ver\s+)?2[58]0\s+(?:five[- ]star|5[- ]star)\s+(?:Google\s+)?reviews?",
                re.I),
     f"{REAL_REVIEWS} Google reviews"),

    ("reviews-count-schema", '"reviewCount": "250" -> "26"',
     re.compile(r'("reviewCount"\s*:\s*")\d+(")'),
     r"\g<1>" + REAL_REVIEWS + r"\g<2>"),

    ("reviews-bare", "'250 reviews' / '250 Google reviews' -> 26",
     re.compile(r"\b2[58]0\s+(Google\s+)?reviews\b", re.I),
     REAL_REVIEWS + r" \g<1>reviews".replace("  ", " ")),

    ("staff-6", "'Our Own Engineers' card heading plus subtext, as one unit",
     re.compile(r"Our\s+Own\s+Engineers\s+No\s+sub-?contractors\.\s*Ever\.", re.I),
     "Gas Safe Registered Engineers Verify at gassaferegister.co.uk"),

    # --- Absolute no-subcontractor claims -----------------------------------
    # Longest form first. These sentences appear adjacently on the emergency
    # pages, so matching them separately produces duplicated replacement text.
    ("subs-0", "'Every engineer is our own staff. No sub-contractors. No agency workers.'",
     re.compile(r"Every\s+engineer\s+is\s+our\s+own\s+staff\.\s*"
                r"No\s+sub-?contractors\.\s*No\s+agency\s+workers\.", re.I),
     "Every engineer is Gas Safe registered."),

    ("subs-1", "'No sub-contractors. No agency workers.' -> verifiable claim",
     re.compile(r"No\s+sub-?contractors\.\s*No\s+agency\s+workers\.", re.I),
     "Gas Safe registered engineers."),

    ("subs-2", "'We never use sub-contractors.' -> verifiable claim",
     re.compile(r"We\s+never\s+use\s+sub-?contractors\.", re.I),
     "All gas work is carried out by Gas Safe registered engineers."),

    ("subs-3", "'No sub-contractors. Ever.' -> verifiable claim",
     re.compile(r"No\s+sub-?contractors\.\s*Ever\.", re.I),
     "Gas Safe registered."),

    ("subs-4", "'Every engineer is our own staff.' -> verifiable claim",
     re.compile(r"Every\s+engineer\s+is\s+our\s+own\s+staff\.", re.I),
     "Every engineer is Gas Safe registered."),

    ("subs-5", "standalone 'No sub-contractors' -> verifiable claim",
     re.compile(r"\bNo\s+sub-?contractors\b\.?", re.I),
     "Gas Safe registered"),

    ("subs-6", "'No agency workers.' -> removed",
     re.compile(r"\s*No\s+agency\s+workers\.", re.I),
     ""),

    # --- Employment-status wording (all engineers are self-employed) --------
    ("staff-1", "'our own directly employed X engineers' -> Gas Safe registered",
     re.compile(r"our\s+own\s+directly\s+employed\s+(?:Gas\s+Safe\s+registered\s+)?engineers",
                re.I),
     "Gas Safe registered engineers"),

    ("staff-2", "'our own employed engineers/plumbers/team' -> Gas Safe registered",
     re.compile(r"our\s+own\s+employed\s+(engineers?|plumbers?|team|staff)", re.I),
     r"Gas Safe registered \g<1>"),

    ("staff-2b", "'our own employed tiler' -> customer arranges tiling",
     re.compile(r"(?:by\s+)?our\s+own\s+employed\s+tiler", re.I),
     "by a tiler you arrange"),

    ("staff-3", "'Our Own Engineers' heading -> Gas Safe Registered Engineers",
     re.compile(r"Our\s+Own\s+Engineers"),
     "Gas Safe Registered Engineers"),

    ("staff-4", "'our own Gas Safe engineers/team' -> our Gas Safe engineers/team",
     re.compile(r"our\s+own\s+(Gas\s+Safe\s+(?:registered\s+)?(?:engineers|team|staff))", re.I),
     r"our \g<1>"),

    ("staff-5", "'our own staff' -> our engineers",
     re.compile(r"our\s+own\s+staff", re.I),
     "our engineers"),


    # --- Attacks on competitors for using subcontractors --------------------
    # We are a group of self-employed engineers, so this line cuts both ways.
    ("hypocrite-1", "competitor attack: 'national chains using sub-contractors'",
     re.compile(r"\s*(?:typically\s+|usually\s+)?come\s+from\s+national\s+chains\s+"
                r"using\s+sub-?contractors\.", re.I),
     " typically come from national chains."),
]

# AggregateRating blocks are removed structurally, not by the rule table,
# because they span multiple lines inside JSON-LD.
AGG_RATING = re.compile(
    r'\s*"aggregateRating"\s*:\s*\{[^{}]*\}\s*,?',
    re.S,
)

# Patterns we only REPORT on. These need a human decision, not a substitution.
FLAG_ONLY = [
    ("flag-subs-other", "other subcontractor wording - needs manual review",
     re.compile(r"sub-?contract", re.I)),
    ("flag-aggregate", "AggregateRating still present after removal pass",
     re.compile(r"AggregateRating")),
    ("flag-review-num", "other 3-digit review-ish number - check by hand",
     re.compile(r"\b(1\d\d|2\d\d|3\d\d)\s+(?:five[- ]star\s+)?reviews?\b", re.I)),
    ("flag-own", "residual 'our own' employment wording - check by hand",
     re.compile(r"our\s+own\s+(?:staff|team|engineers|employed|plumbers|fitters)", re.I)),
    ("flag-inhouse", "'in-house' / 'in house' claim - check it is still true",
     re.compile(r"in[- ]house", re.I)),
    ("flag-payroll", "'employed by us' / 'on our payroll' - REWRITE BY HAND",
     re.compile(r"\b(?:directly\s+)?employed\s+by\s+us\b|\bon\s+our\s+payroll\b"
                r"|\bdirectly\s+employed\b|\bemployed\s+engineers?\b", re.I)),
    ("flag-json", "JSON-LD block failed to parse after edits - INSPECT",
     re.compile(r"(?!)")),
]


def iter_files():
    if not SRC.is_dir():
        sys.exit("ERROR: no src/ directory. Run this from the repo root.")
    yield from sorted(SRC.rglob("*.astro"))


def process(text):
    """Return (new_text, {rule_id: count})."""
    counts = defaultdict(int)

    # Structural removal first, so the flag pass can catch leftovers.
    new, n = AGG_RATING.subn("", text)
    if n:
        counts["aggregate-rating-removed"] = n
        text = new

    for rule_id, _desc, pattern, repl in RULES:
        text, n = pattern.subn(repl, text)
        if n:
            counts[rule_id] = n

    # Tidy any comma damage left by the AggregateRating removal.
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\{\s*,", "{", text)
    text = re.sub(r",\s*\}", "\n  }", text)

    return text, counts


JSON_LD = re.compile(
    r'<script type="application/ld\+json"[^>]*>\s*(\{.*?\})\s*</script>', re.S
)


def flags(text):
    out = []
    for flag_id, desc, pattern in FLAG_ONLY:
        if flag_id == "flag-json":
            continue
        hits = pattern.findall(text)
        if hits:
            out.append((flag_id, desc, len(hits)))

    # Structural check: every JSON-LD block must still parse after edits.
    import json
    broken = 0
    for block in JSON_LD.findall(text):
        try:
            json.loads(block)
        except Exception:
            broken += 1
    if broken:
        out.append(("flag-json", "JSON-LD block failed to parse - INSPECT", broken))

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write changes (default is dry run)")
    args = ap.parse_args()

    totals = defaultdict(int)
    changed_files = []
    flagged = []

    files = list(iter_files())
    if not files:
        sys.exit("ERROR: no .astro files found under src/")

    for path in files:
        original = path.read_text(encoding="utf-8")
        updated, counts = process(original)

        if counts:
            changed_files.append((path, dict(counts)))
            for k, v in counts.items():
                totals[k] += v

        f = flags(updated)
        if f:
            flagged.append((path, f))

        if args.apply and updated != original:
            dest = BACKUP / path.relative_to(".")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            path.write_text(updated, encoding="utf-8")

    # ----------------------------- report ---------------------------------
    mode = "APPLIED" if args.apply else "DRY RUN - nothing written"
    print("=" * 68)
    print(f"  TRUTH LAP  |  {mode}")
    print(f"  {len(files)} files scanned  |  {len(changed_files)} would change")
    print("=" * 68)

    if totals:
        print("\nCHANGES BY RULE\n")
        desc = {r[0]: r[1] for r in RULES}
        desc["aggregate-rating-removed"] = "AggregateRating schema block removed"
        for rule_id, count in sorted(totals.items(), key=lambda x: -x[1]):
            print(f"  {count:5}  {desc.get(rule_id, rule_id)}")
    else:
        print("\n  No changes needed. Site already consistent.")

    if changed_files:
        print("\nPER FILE\n")
        for path, counts in changed_files:
            summary = ", ".join(f"{k}x{v}" for k, v in sorted(counts.items()))
            print(f"  {path}")
            print(f"      {summary}")

    if flagged:
        print("\n" + "-" * 68)
        print("  MANUAL REVIEW NEEDED - not auto-changed")
        print("-" * 68 + "\n")
        for path, f in flagged:
            print(f"  {path}")
            for flag_id, desc, n in f:
                print(f"      {n:3}x  {desc}")

    if args.apply:
        print(f"\n  Backups written to {BACKUP}/")
        print("  Roll back with:  cp -r .truth_lap_backup/src/ src/")
    else:
        print("\n  Re-run with --apply to write changes.")


if __name__ == "__main__":
    main()
