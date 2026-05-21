#!/usr/bin/env python3
"""
Liverpool Emergency Plumber — Homepage Flesch Patch 2
=====================================================
Run after homepage-flesch-fix.py to push page avg from 82.7 → ~86.

Applies 5 micro-text/CTA fixes that the diagnostic flagged:
  - 1 caption above a CTA button
  - 1 subhead in the reviews section
  - 1 commercial sidebar card
  - 1 mid-page orange CTA banner
  - 1 insurance section CTA bar

Does NOT touch James Alexander's real review (score 65.7 is the
actual customer's words and is left alone).
"""
import re
import sys
from pathlib import Path

PATH = Path("src/pages/index.astro")

PATCHES = [
    # 1. Caption above Why Choose CTA (-8.7 → 99)
    ("Plumbing emergency in Liverpool?",
     "Burst pipe? Boiler down?"),

    # 2. Reviews subhead (32.6 → 74)
    ("Real reviews from Liverpool homeowners",
     "Real reviews from real Liverpool jobs."),

    # 3. Commercial sidebar card text (35.1 → 86)
    ("No commercial premium. 24/7 cover. 30 minute response. Gas Safe registered engineers.",
     "No business top-up. 24/7 cover. 30 min response. Gas Safe team."),

    # 4. Mid-page orange CTA banner (51.5 → 105)
    ("24 hour plumber Liverpool. Fixed rates from £80. 30 minute response. Gas Safe registered. Full emergency plumbing services.",
     "24 hour plumber. From £80. Gas Safe team. We come in 30 mins. 24/7 cover."),

    # 5. Insurance section CTA bar (66.5 → 106)
    ("Need documentation for an insurance claim? Call us on <a href=\"tel:0151 558 0334\" style=\"color:var(--orange);font-weight:700;\">0151 558 0334</a> and we will sort everything you need.",
     "Need docs for an insurance claim? Call us on <a href=\"tel:0151 558 0334\" style=\"color:var(--orange);font-weight:700;\">0151 558 0334</a>. We will sort all of it."),
]


def count_syllables(word):
    word = word.lower()
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', word)
    word = re.sub(r'^y', '', word)
    return max(1, len(re.findall(r'[aeiouy]+', word)))

def flesch(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return None
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    if not sentences or not words:
        return None
    syllables = sum(count_syllables(w) for w in words)
    return round(206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words)), 1)


def main():
    if not PATH.exists():
        print(f"ERROR: {PATH} not found. Run from repo root.")
        sys.exit(1)

    content = PATH.read_text(encoding='utf-8')
    original = content

    print(f"=== Applying {len(PATCHES)} micro-text patches to {PATH} ===\n")
    applied, skipped = 0, []
    for i, (old, new) in enumerate(PATCHES, 1):
        if old in content:
            content = content.replace(old, new, 1)
            applied += 1
        else:
            skipped.append((i, old[:70]))

    if content == original:
        print("No changes applied. Already run or text drift.")
        sys.exit(1)

    PATH.write_text(content, encoding='utf-8')
    print(f"✓ Applied: {applied} / {len(PATCHES)}")
    if skipped:
        print(f"\n⚠ Skipped {len(skipped)}:")
        for i, preview in skipped:
            print(f"   #{i}: {preview!r}...")

    # Verification
    new_content = PATH.read_text(encoding='utf-8')

    print("\n=== POST-APPLY VERIFICATION ===\n")

    # Semantic gaps
    print("Semantic gaps still present:")
    for gap in ["plumbing issues", "24/7 emergency plumbing"]:
        c = new_content.lower().count(gap.lower())
        print(f"  {'✓' if c else '✗'} '{gap}': {c}")

    # James's review is preserved
    print("\nReal reviews preserved (we did NOT touch these):")
    for name in ["James Alexander", "John Manley", "Elaine McHugh"]:
        print(f"  {'✓' if name in new_content else '✗ MISSING'} {name}")
    real_review_text = "Great company, came within 30 mins for emergency burst pipe"
    print(f"  {'✓' if real_review_text in new_content else '✗ MISSING'} James's review text verbatim")

    # Page Flesch
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', new_content, flags=re.DOTALL)
    cleaned = []
    for p in paragraphs:
        t = re.sub(r'<[^>]+>', '', p).strip()
        t = re.sub(r'\s+', ' ', t)
        if len(t) > 20:
            cleaned.append(t)
    scores = [flesch(p) for p in cleaned if flesch(p) is not None]
    if scores:
        avg = sum(scores) / len(scores)
        avg80 = [s for s, p in zip(scores, cleaned) if len(p) >= 80]
        print(f"\nPage Flesch:")
        print(f"  Paragraphs: {len(scores)}")
        print(f"  Average:    {avg:.1f}")
        print(f"  Min:        {min(scores)}")
        print(f"  Below 60:   {sum(1 for s in scores if s < 60)}")
        print(f"  Below 70:   {sum(1 for s in scores if s < 70)}")
        if avg80:
            print(f"  Avg ≥80 chars: {sum(avg80)/len(avg80):.1f}  (excludes micro-text)")

    print("\n=== DONE ===")
    print("Next: git diff src/pages/index.astro, then commit + push.")


if __name__ == "__main__":
    main()
