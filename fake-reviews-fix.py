#!/usr/bin/env python3
# fake-reviews-fix.py
# Fixes the 5 known fake reviewer entries across the repo.
# Run from: ~/Documents/GitHub/ideal-plumbing-site
# Usage: python3 fake-reviews-fix.py

import os
import sys
from pathlib import Path

# ANSI colours
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BOLD = '\033[1m'
DIM = '\033[2m'
NC = '\033[0m'

# Sanity check
if not Path('src/pages').exists():
    print(f"{RED}ERROR: src/pages not found. Run from repo root.{NC}")
    sys.exit(1)

# Real review block - John Manley (the most substantial of the 3 verified reviews)
JOHN_MANLEY_REVIEW = '<div class="pf-review"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;"><div class="pf-review-quote">"</div><span style="font-size:0.68rem;font-weight:700;background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;border-radius:999px;padding:0.15rem 0.5rem;">Verified Google Review</span></div><p>Fantastic service, less than two hours after phoning up to order a new shower the job was done. The young man who fitted it was a credit to himself. I would highly recommend this company.</p><div class="pf-review-footer"><div class="pf-review-avatar">J</div><div><div class="pf-review-name">John Manley</div><div class="pf-review-loc">Shower Installation</div></div><div class="pf-review-stars">★★★★★</div></div></div>'

# Real trust-bar quote (shortened version used in trust bars)
JOHN_MANLEY_TRUST_BAR_QUOTE = '<div style="color:rgba(255,255,255,0.85);font-size:0.84rem;font-style:italic;max-width:520px;">"Fantastic service. The job was done in two hours. Highly recommend this firm." John Manley, Google Review</div>'

# 5 known fake reviews to fix
fixes = [
    {
        'name': 'Louise T (boiler-installation-formby)',
        'file': 'src/pages/boiler-installation-formby.astro',
        'old': '<div class="pf-review"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;"><div class="pf-review-quote">"</div><span style="font-size:0.68rem;font-weight:700;background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;border-radius:999px;padding:0.15rem 0.5rem;">Verified Google Review</span></div><p>New Worcester Bosch system boiler fitted in our Formby detached. The engineer surveyed on Thursday, explained exactly why we needed a system boiler rather than the combi another company had quoted for, and had everything installed by the following Wednesday. Perfect hot water throughout and the house heats more evenly than it ever has. All documentation arrived by email that afternoon.</p><div class="pf-review-footer"><div class="pf-review-avatar">L</div><div><div class="pf-review-name">Louise T</div><div class="pf-review-loc">Formby · System Boiler</div></div><div class="pf-review-stars">★★★★★</div></div></div>',
        'new': JOHN_MANLEY_REVIEW,
    },
    {
        'name': 'Debbie H (hot-water-cylinders-wirral)',
        'file': 'src/pages/hot-water-cylinders-wirral.astro',
        'old': '<div class="pf-review"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;"><div class="pf-review-quote">"</div><span style="font-size:0.68rem;font-weight:700;background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;border-radius:999px;padding:0.15rem 0.5rem;">Verified Google Review</span></div><p>Old vented cylinder in our Birkenhead terrace finally gave out   over 25 years old. Ideal came out the same day, confirmed it needed replacing, and fitted a new cylinder the following morning. Fixed price quoted on the phone, stuck to on the invoice. No drama, no mess. Highly recommended for any Wirral cylinder work.</p><div class="pf-review-footer"><div class="pf-review-avatar">D</div><div><div class="pf-review-name">Debbie H</div><div class="pf-review-loc">Birkenhead · Vented Cylinder Replacement</div></div><div class="pf-review-stars">★★★★★</div></div></div>',
        'new': JOHN_MANLEY_REVIEW,
    },
    {
        'name': 'Neil A (gas-safety-certificate-wirral)',
        'file': 'src/pages/gas-safety-certificate-wirral.astro',
        'old': '<div class="pf-review"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;"><div class="pf-review-quote">"</div><span style="font-size:0.68rem;font-width:700;background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;border-radius:999px;padding:0.15rem 0.5rem;">Verified Google Review</span></div><p>Combined CP12 and boiler service for my Bebington HMO. One visit, two documents, both by email same afternoon. Letting agent accepted the certificate the next morning. The annual reminder means it never slips through the net. Ideal Plumbing are the only people I trust with my compliance paperwork.</p><div class="pf-review-footer"><div class="pf-review-avatar">N</div><div><div class="pf-review-name">Neil A</div><div class="pf-review-loc">Bebington · HMO Landlord</div></div><div class="pf-review-stars">★★★★★</div></div></div>',
        'new': JOHN_MANLEY_REVIEW,
    },
    {
        'name': 'Gary L (central-heating-installation-st-helens)',
        'file': 'src/pages/central-heating-installation-st-helens.astro',
        'old': '<div class="pf-review"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;"><div class="pf-review-quote">"</div><span style="font-size:0.68rem;font-weight:700;background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;border-radius:999px;padding:0.15rem 0.5rem;">Verified Google Review</span></div><p>Rental property in WA10 with a back boiler that was on its last legs. Ideal surveyed it, assessed ECO4 eligibility and confirmed we qualified. New combi, all new radiators, the lot. Done to a fixed price in five days. The letting agent was delighted, the tenant was delighted and the property now has a much better EPC rating. Ideal Plumbing are the real deal.</p><div class="pf-review-footer"><div class="pf-review-avatar">G</div><div><div class="pf-review-name">Gary L</div><div class="pf-review-loc">St Helens · Landlord, Back Boiler Property</div></div><div class="pf-review-stars">★★★★★</div></div></div>',
        'new': JOHN_MANLEY_REVIEW,
    },
    {
        'name': 'Susan P trust bar quote (hot-water-cylinders-st-helens)',
        'file': 'src/pages/hot-water-cylinders-st-helens.astro',
        'old': '<div style="color:rgba(255,255,255,0.85);font-size:0.84rem;font-style:italic;max-width:520px;">"Old copper cylinder in our WA10 terrace was well over 20 years old and had failed overnight. Ideal came out the same morning, confirmed it needed replacing, and fitted a new cylinder by the afternoon. No mess, fixed price, exactly what they said." Susan P, St Helens</div>',
        'new': JOHN_MANLEY_TRUST_BAR_QUOTE,
    },
]

print(f"{BOLD}========================================================{NC}")
print(f"{BOLD}  FAKE REVIEWS CLEANUP{NC}")
print(f"{BOLD}========================================================{NC}\n")

fixed = 0
skipped = 0

for fix in fixes:
    name = fix['name']
    path = Path(fix['file'])

    if not path.exists():
        print(f"  {YELLOW}? {name}{NC}")
        print(f"    {DIM}File not found: {fix['file']}{NC}")
        skipped += 1
        continue

    content = path.read_text(encoding='utf-8')

    if fix['old'] not in content:
        print(f"  {YELLOW}? {name}{NC}")
        print(f"    {DIM}Pattern not found in file (already fixed?){NC}")
        skipped += 1
        continue

    new_content = content.replace(fix['old'], fix['new'])
    path.write_text(new_content, encoding='utf-8')
    print(f"  {GREEN}✓ {name}{NC}")
    fixed += 1

print()
print(f"{BOLD}Result:{NC} {GREEN}{fixed} fixed{NC}, {YELLOW}{skipped} skipped{NC}")
print()

# Verify
print(f"{BOLD}Verification — checking for known fictional names...{NC}\n")
import subprocess
fictional_names = ['Louise T', 'Debbie H', 'Susan P', 'Neil A', 'Gary L',
                   'Karen M', 'Paul R', 'Tom K', 'Kathleen R', 'Frank B',
                   'Norma T', 'Derek N', 'Patricia H', 'Veronica S']

for name in fictional_names:
    result = subprocess.run(
        ['grep', '-rln', f'\\b{name}\\b', 'src/pages'],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print(f"  {RED}✗ {name} still appears in:{NC}")
        for f in result.stdout.strip().split('\n'):
            print(f"    {f}")
    else:
        print(f"  {GREEN}✓ {name}: clean{NC}")

print()
print(f"{BOLD}Check 'Ideal Plumbing' remaining hits:{NC}")
result = subprocess.run(
    ['grep', '-rn', 'Ideal Plumbing', 'src/pages'],
    capture_output=True, text=True
)
if result.stdout.strip():
    for line in result.stdout.strip().split('\n')[:10]:
        print(f"  {line}")
else:
    print(f"  {GREEN}✓ Zero hits remaining{NC}")

print()
print(f"{BOLD}Next:{NC} git diff to review, then commit.")
print(f"  {DIM}git diff --stat src/pages/{NC}")
print(f"  {DIM}git add . && git commit -m 'Site-wide cleanup: fake reviews + Ideal Plumbing brand swap'{NC}")
print()
