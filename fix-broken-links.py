#!/usr/bin/env python3
"""
Fix broken external links flagged by Semrush.
- Replaces 9 verified-broken URLs with their working replacements
- Strips <a> wrapper from 24 unverifiable URLs (keeps visible text)
Run from repo root: python3 fix-broken-links.py
"""
import re
from pathlib import Path

# Verified replacements (broken -> working, confirmed via web search)
REPLACEMENTS = {
    "https://cadentgas.com/gas-escapes":
        "https://cadentgas.com/emergencies",
    "https://www.unitedutilities.com/help-and-support/emergencies/":
        "https://www.unitedutilities.com/emergencies/",
    "https://www.checkatrade.com/blog/cost-guides/emergency-plumber-cost/":
        "https://www.checkatrade.com/blog/cost-guides/plumber-call-out-fee/",
    "https://www.nrla.org.uk/resources/gas-safety":
        "https://www.nrla.org.uk/resources/looking-after-your-property/landlords-gas-safety-responsibilities",
    "https://liverpool.gov.uk/housing/landlords/hmo/":
        "https://liverpool.gov.uk/housing/private-rented-accommodation/multiple-occupancy-homes/",
    "https://www.gov.uk/check-energy-performance-certificate":
        "https://www.gov.uk/find-energy-certificate",
    "https://www.gov.uk/apply-home-insulation-grant":
        "https://www.gov.uk/apply-great-british-insulation-scheme",
    "https://www.hse.gov.uk/gas/domestic/co-poisoning.htm":
        "https://www.hse.gov.uk/gas/domestic/co.htm",
}

# Unverifiable broken URLs — strip the <a> wrapper, keep visible text
# (Boiler Plus withdrawn by gov.uk; rest are low-count/contextual)
STRIP_URLS = [
    "https://www.gov.uk/guidance/boiler-plus",
    "https://www.ofgem.gov.uk/information-for-household-consumers/energy-efficiency",
    "https://www.vaillant.co.uk/homeowners/support-and-spares/warranty/",
    "https://www.worcester-bosch.co.uk/support/warranty-and-guarantee",
    "https://liverpool.gov.uk/parks/sefton-park/",
    "https://liverpool.gov.uk/housing/landlords/selective-licensing/",
    "https://liverpool.gov.uk/business/licensing/private-rented-housing/",
    "https://www.dwi.gov.uk/consumers/learn-about-your-drinking-water/lead-pipes/",
    "https://liverpool.gov.uk/housing/landlords/",
    "https://www.nationwide.co.uk/about/house-price-index/house-price-index/",
    "https://www.gov.uk/guidance/smoke-and-carbon-monoxide-alarms-explanatory-booklet-for-landlords",
    "https://www.gov.uk/drinking-water-inspectorate",
    "https://www.abi.org.uk/products-and-issues/choosing-and-buying/home-insurance/",
    "https://www.citizensadvice.org.uk/consumer/insurance/making-a-home-insurance-claim/",
    "https://www.ofgem.gov.uk/information-for-household-consumers/energy-saving-and-efficiency",
    "https://www.worcester-bosch.co.uk/professionals/support/technical-support",
    "https://www.aintree.thejockeyclub.co.uk/",
    "https://www.water.org.uk/consumers/top-tips-to-save-water/hard-water/",
    "https://www.hse.gov.uk/gas/commercial/",
    "https://www.sefton.gov.uk/leisure-culture/parks-and-open-spaces/crosby-beach/",
    "https://liverpool.gov.uk/parks/croxteth-hall/",
    "https://liverpool.gov.uk/planning-and-building-control/conservation-and-heritage/",
    "https://www.wirral.gov.uk/housing/private-housing/hmo-licensing",
    "https://www.gov.uk/guidance/building-regulations-part-g-sanitation-hot-water-safety-and-water-efficiency",
    "https://www.citizensadvice.org.uk/consumer/buying-and-owning/buying-and-owning-your-home/getting-work-done-on-your-home/",
]

EXTENSIONS = {".astro", ".md", ".mdx", ".html", ".jsx", ".tsx"}
SCAN_DIRS = ["src", "public", "content"]  # adjust if needed

def fix_file(path):
    """Returns (replacements, strips) counts for one file."""
    text = path.read_text(encoding="utf-8")
    original = text
    n_replace = 0
    n_strip = 0

    # 1. URL replacements (literal string swap inside href)
    for old, new in REPLACEMENTS.items():
        if old in text:
            count = text.count(old)
            text = text.replace(old, new)
            n_replace += count

    # 2. Strip <a> wrapper around unverifiable URLs
    # Pattern: <a ... href="BROKEN_URL" ...>TEXT</a>  ->  TEXT
    for url in STRIP_URLS:
        escaped = re.escape(url)
        # Match <a> with any attribute order, capture inner text
        pattern = re.compile(
            r'<a\s+[^>]*href=["\']' + escaped + r'["\'][^>]*>(.*?)</a>',
            re.DOTALL | re.IGNORECASE
        )
        new_text, count = pattern.subn(r'\1', text)
        if count:
            n_strip += count
            text = new_text

    if text != original:
        path.write_text(text, encoding="utf-8")

    return n_replace, n_strip


def main():
    root = Path(".").resolve()
    total_files = 0
    total_replace = 0
    total_strip = 0
    changed_files = []

    for d in SCAN_DIRS:
        base = root / d
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in EXTENSIONS:
                total_files += 1
                r, s = fix_file(path)
                if r or s:
                    changed_files.append((path, r, s))
                    total_replace += r
                    total_strip += s

    print(f"Scanned: {total_files} files")
    print(f"Modified: {len(changed_files)} files")
    print(f"URL replacements: {total_replace}")
    print(f"Link wrappers stripped: {total_strip}")
    print()
    if changed_files:
        print("Changed files:")
        for path, r, s in sorted(changed_files):
            rel = path.relative_to(root)
            print(f"  {rel}  (replaced: {r}, stripped: {s})")


if __name__ == "__main__":
    main()
