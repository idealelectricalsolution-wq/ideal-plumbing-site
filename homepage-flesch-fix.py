#!/usr/bin/env python3
"""
Liverpool Emergency Plumber — Homepage Flesch + Semantic Gap Fix
================================================================
Drop in repo root and run: python3 homepage-flesch-fix.py

Applies 37 prose rewrites to src/pages/index.astro to:
  - Raise page-wide Flesch Reading Ease from 69.0 → 85.6 avg
  - Eliminate all paragraphs scoring below 70 (was 34 below)
  - Weave in 2 Semrush semantic gaps:
      * "plumbing issues"
      * "24/7 emergency plumbing"

What it does NOT touch:
  - Schema (LocalBusiness, Service, FAQPage)
  - 3 real Google reviews (James Alexander, John Manley, Elaine McHugh)
  - Phone, address, postcode list, prices, pricing tiers, brand names
  - HTML structure, links, styles, CSS classes
  - All h1/h2/h3 headings (kept as-is for SEO continuity)

Self-verifies after applying:
  - Flesch page average
  - Both semantic gaps present
  - All 10 AI-tell categories still zero
"""

import sys
import re
from pathlib import Path

PATH = Path("src/pages/index.astro")

# ---------------------------------------------------------------------------
# THE 37 REWRITES  (OLD → NEW, exact string match)
# ---------------------------------------------------------------------------

REWRITES = [
    # HERO — weave in "24/7 emergency plumbing"
    ("Burst pipes. Boiler breakdowns. Blocked drains. Gas leaks. We will be there in 30 minutes. Gas Safe registered. Our own Gas Safe engineers. Fixed rates from £80. Full emergency plumbing services across L1 to L40.",
     "Burst pipes. Boiler breakdowns. Blocked drains. Gas leaks. We will be there in 30 minutes. Gas Safe registered. Our own engineers. Fixed rates from £80. 24/7 emergency plumbing across L1 to L40."),

    # PRICING — alert paragraph
    ("Burst pipe: £120 to £350 · Boiler breakdown: £150 to £500 · Blocked drain: £80 to £250 · Gas leak safety visit: FREE · Major leak: £80 to £200. For independent price benchmarks see ",
     "Burst pipe: £120 to £350. Boiler down: £150 to £500. Blocked drain: £80 to £250. Gas leak safety visit: FREE. Major leak: £80 to £200. For market price checks see "),

    # COMMON JOBS section
    ("The plumbing faults we attend most often across Liverpool L1 to L40.",
     "The plumbing issues we see most days. From L1 to L40."),

    ("Water pouring from pipes, ceiling or walls. We stop the leak, repair or replace the pipe section and check for hidden damage. Common in winter in Liverpool's Victorian properties with external pipes.",
     "Water pours from pipes, ceiling or walls. We stop the leak. We swap the pipe section if needed. We check for hidden damage. Common in winter in old Liverpool homes with outside pipes."),

    ("Heating not working. Some radiators cold. Boiler fires but no heat. We check pump, motorised valves, thermostats and pipework. Priority response in winter for vulnerable people.",
     "Heating off. Some rads cold. Boiler fires but no heat. We check the pump. We check the valves. We check the thermostat. Priority response in winter for older people."),

    # OTHER SERVICES intro
    ("Not an emergency? We cover the full range of plumbing and heating work across Liverpool and Merseyside.",
     "Not an emergency? We fix every kind of plumbing issue. Big jobs and small. Across all of Liverpool."),

    # HOW IT WORKS
    ("Fast, pro emergency response every time.",
     "Fast help. Every time. The same team."),

    ("A real person answers 24/7. No voicemail. No automated system. We give you safety advice while sending an engineer to your Liverpool property.",
     "A real person picks up at any hour. No voicemail. No bots. We give you safety tips on the phone. The engineer is on the way."),

    # WHY CHOOSE — section sub
    ("Gas Safe registered. Our own engineers. All Liverpool L1 to L40 postcodes covered 24/7.",
     "Gas Safe. Our own team. We cover all Liverpool postcodes from L1 to L40. Day or night."),

    ("We aim to be with you within 30 minutes across Liverpool L1 to L40. We know emergencies cannot wait.",
     "We aim to be there in 30 mins. We cover all of Liverpool from L1 to L40. We know you cannot wait."),

    ("All engineers Gas Safe registered. Verify at <a href=\"https://www.gassaferegister.co.uk\" target=\"_blank\" rel=\"noopener\">gassaferegister.co.uk</a>. Required by law for all boiler and gas work. Certificates given for all gas work.",
     "All our team are Gas Safe. Check us at <a href=\"https://www.gassaferegister.co.uk\" target=\"_blank\" rel=\"noopener\">gassaferegister.co.uk</a>. Gas Safe is the law for all gas and boiler work. We give you a cert for every gas job."),

    # BLOCKED DRAINS section
    ("Blocked toilet, blocked sink, shower backing up or drain overflowing. We clear all types of drain blockage across Liverpool same day. Our emergency plumbing services cover every postcode.",
     "Blocked toilet. Blocked sink. Shower backed up. Drain spilling over. We clear the lot the same day. 24/7 emergency plumbing across all of Liverpool."),

    ("Stop flushing and call us at once. More flushing will overflow sewage onto your floor. We attend blocked toilet emergencies 24/7 across Liverpool. Most fixed on the same visit using pro clearing gear.",
     "Stop flushing. Call us right now. More flushing means sewage on your floor. We come out for blocked toilets 24/7. Most jobs are fixed on the first visit."),

    ("Liverpool's Victorian sewer system is one of the oldest in England. Tree roots growing into clay sewer pipes are very common across Aigburth, Sefton Park, Woolton and areas with mature trees.",
     "Liverpool has one of the oldest sewer systems in England. Tree roots get into the old clay pipes. We see this a lot in Aigburth, Sefton Park and Woolton."),

    ("Sewage backing up into the toilet or bath is a health emergency. Call us 24/7 on 0151 558 0334. We attend sewage overflow as a priority.",
     "Sewage in the toilet or bath is a health risk. Call us 24/7 on 0151 558 0334. We treat it as a top priority."),

    # FROZEN PIPES section
    ("Liverpool winters cause many frozen pipe emergencies every year. Many can be stopped before they happen.",
     "Cold snaps freeze a lot of Liverpool pipes each winter. Most can be stopped before they burst."),

    ("Liverpool's Victorian and Edwardian terraces often have external or loft pipes that were never lagged to modern standards. Properties with pipes running through unheated spaces are most at risk in cold snaps.",
     "Old Liverpool homes often have pipes in the loft or outside. They were never lagged to today's standards. Homes with pipes in cold spaces are most at risk."),

    ("Lag all exposed pipes in lofts, garages and cellar entries before winter. Keep your heating on a low background temperature even when away. Know where your stopcock is before an emergency hits.",
     "Lag any open pipes in lofts, garages and cellars before winter. Keep the heating on low even when away. Know where your stopcock is. Before an emergency hits."),

    # WATER DAMAGE section
    ("A plumbing emergency can cause serious water damage. Here is what to do to protect your property and your insurance claim.",
     "Plumbing issues can cause real water damage. Here is how to keep your home safe and your insurance claim sound."),

    # COVERAGE section
    ("Searching for a plumber near me in Liverpool? We cover all Liverpool postcodes L1 to L40 and the wider Merseyside area. Any time of day or night. 365 days a year.",
     "Need a plumber near you in Liverpool? We cover all postcodes from L1 to L40. Plus the rest of Merseyside. Day or night. 365 days a year."),

    # COMMERCIAL section
    ("Plumbing emergencies in Liverpool commercial premises cannot wait. We provide 24/7 commercial emergency cover across all Liverpool L1 to L40 postcodes at the same fixed rates as our residential service. No commercial premium.",
     "Shop, hotel or office burst pipe? It will not wait. We do 24/7 emergency plumbing for all Liverpool businesses. Same fixed rates as homes. No business top-up."),

    # LANDLORDS section
    ("Liverpool has one of the largest private rental sectors in the North West. Here is what Merseyside landlords need to stay compliant.",
     "Liverpool has one of the biggest rental markets in the North West. Here is what landlords need to keep on the right side of the law."),

    ("Burst pipe. Boiler failure. Blocked drain. Your tenants call us directly. We attend, fix and document everything. You get a full report. Works with all letting agents across Merseyside.",
     "Burst pipe. Boiler dead. Blocked drain. Your tenants call us. We come out. We fix. We send you the full report. Works with any letting agent across Merseyside."),

    ("HMO licensing requires up-to-date gas safety certificates and a plumbing system in good repair. We provide all the docs required by <a href=\"https://liverpool.gov.uk/housing/private-rented-accommodation/multiple-occupancy-homes/\" target=\"_blank\" rel=\"noopener\" style=\"color:var(--navy);font-weight:700;\">Liverpool City Council HMO licensing</a>.",
     "HMO rules mean your gas cert must be up to date. The plumbing must be sound too. We sort all the docs <a href=\"https://liverpool.gov.uk/housing/private-rented-accommodation/multiple-occupancy-homes/\" target=\"_blank\" rel=\"noopener\" style=\"color:var(--navy);font-weight:700;\">Liverpool City Council</a> asks for."),

    ("Managing multiple Liverpool properties? We offer priority response, joined-up invoicing and yearly compliance schedules for portfolio landlords across Merseyside. One call handles everything.",
     "Got more than one Liverpool rental? We give you fast response. One invoice. One yearly plan. One call sorts the lot."),

    # FAQ subhead
    ("Straight answers to what Liverpool homeowners ask most.",
     "Straight answers to the questions Liverpool folk ask most."),

    # FAQ — Gas Safe
    ("Yes. All our engineers are Gas Safe registered. It is illegal to work on gas appliances without this. Verify our registration at <a href=\"https://www.gassaferegister.co.uk\" target=\"_blank\" rel=\"noopener\">gassaferegister.co.uk</a>. We give gas safety certificates for all gas work done.",
     "Yes. All our team are Gas Safe. Working on gas without it is against the law. Check us at <a href=\"https://www.gassaferegister.co.uk\" target=\"_blank\" rel=\"noopener\">gassaferegister.co.uk</a>. We give a gas cert for every gas job."),

    # FAQ — sub-contractors
    ("No. Every engineer we send to your Liverpool property is our own employed staff. We never use sub-contractors or agency workers. You get the same trained, vetted, insured pro every time.",
     "No. Every engineer we send is on our own staff. We never use subbies. We never use agency workers. You get the same trained, vetted, insured team each time."),

    # FAQ — response time
    ("We aim for a 30 minute response across Liverpool L1 to L40. City centre, Anfield and Wavertree typically under 20 minutes. Outlying areas like Formby, Kirkby and Maghull around 35 minutes.",
     "We aim to be there in 30 minutes. We cover all of Liverpool L1 to L40. Inner Liverpool is often under 20 mins. The outer ring takes about 35."),

    # FAQ — postcodes (long list killed Flesch; shortened in visible, comprehensive list stays in schema)
    ("We cover all Liverpool postcodes from L1 to L40. This includes the city centre, Anfield, Aigburth, Wavertree, West Derby, Woolton, Old Swan, Childwall, Allerton, Garston, Bootle, Crosby, Maghull, Kirkby, Huyton, Norris Green, Fazakerley, Aintree, Formby and Southport.",
     "We cover all 40 Liverpool postcodes. That is L1 right through to L40. See the area links above to find your postcode."),

    # FAQ — commercial
    ("Yes. We cover commercial emergencies 24/7 across Liverpool. Shops, restaurants, offices, hotels and warehouses. Same fixed rates as residential. No commercial premium. We can invoice on 30-day payment terms for set-up businesses.",
     "Yes. We do 24/7 emergency plumbing for Liverpool businesses. Shops, cafes, offices, hotels, warehouses. Same fixed rates as homes. No business top-up. We can invoice on 30-day terms for set-up firms."),

    # FAQ — landlords
    ("Yes. We work with single landlords and letting agents across Liverpool, Wirral and St Helens. We provide annual gas safety certificates (CP12) from £80. We handle tenant emergency call-outs. We offer monthly cover plans for portfolio landlords. See <a href=\"https://www.nrla.org.uk/resources/looking-after-your-property/landlords-gas-safety-responsibilities\" target=\"_blank\" rel=\"noopener\">NRLA landlord gas safety guidance</a> for your legal duties.",
     "Yes. We work with landlords and letting agents in Liverpool, Wirral and St Helens. CP12 gas certs from £80. We handle tenant call-outs. We offer cover plans for landlords with a few rentals. See <a href=\"https://www.nrla.org.uk/resources/looking-after-your-property/landlords-gas-safety-responsibilities\" target=\"_blank\" rel=\"noopener\">NRLA landlord gas safety guidance</a> for the legal duties."),

    # QUALIFICATIONS section sub
    ("Every engineer we send to your Liverpool property holds these qualifications. All gas work is registered with <a href=\"https://www.gassaferegister.co.uk\" target=\"_blank\" rel=\"noopener\">Gas Safe Register</a>.",
     "Every engineer who comes to your home holds these certs. All gas work goes on the <a href=\"https://www.gassaferegister.co.uk\" target=\"_blank\" rel=\"noopener\">Gas Safe Register</a>."),

    # SEO COPY — find a reliable plumber
    ("Always check Gas Safe registration. Verify reviews on Google or Trustpilot. Ask for a clear price before anyone attends. Our fixed rates and 1 hour minimum are stated clearly. Our Gas Safe registration can be verified at <a href=\"https://www.gassaferegister.co.uk\" target=\"_blank\" rel=\"noopener\">gassaferegister.co.uk</a>.",
     "Always check the Gas Safe number. Read the Google reviews. Ask for a price before they show up. Our rates are fixed and on this page. Check our Gas Safe number at <a href=\"https://www.gassaferegister.co.uk\" target=\"_blank\" rel=\"noopener\">gassaferegister.co.uk</a>."),

    # SEO COPY — Victorian homes
    ("Liverpool has one of the highest concentrations of Victorian and Edwardian housing in England. Lead pipes. Gravity-fed systems. Back boilers. External pipework at risk of freezing. All common in Liverpool's older stock. The <a href=\"https://www.hse.gov.uk/gas/domestic/\" target=\"_blank\" rel=\"noopener\">HSE gas safety guidance</a> is clear that all gas work must be done by a Gas Safe registered engineer.",
     "Liverpool has lots of Victorian and Edwardian homes. More than most cities in England. Lead pipes. Gravity-fed systems. Back boilers. Outside pipes that freeze. All common in older Liverpool homes. <a href=\"https://www.hse.gov.uk/gas/domestic/\" target=\"_blank\" rel=\"noopener\">HSE rules</a> say all gas work must be done by a Gas Safe engineer."),

    # SEO COPY — Liverpool City Council
    ("Yes. <a href=\"https://liverpool.gov.uk\" target=\"_blank\" rel=\"noopener\">Liverpool City Council</a> enforces housing standards. This includes plumbing and gas safety in rental homes. Landlords found in breach face fines and enforcement action. We work with Liverpool landlords on full compliance across all property types.",
     "Yes. <a href=\"https://liverpool.gov.uk\" target=\"_blank\" rel=\"noopener\">Liverpool City Council</a> sets housing rules. The rules cover gas and plumbing in rental homes. Landlords who break the rules get fined. We help Liverpool landlords stay on the right side of it."),

    # FINAL CTA
    ("30 minute response. Fixed rates from £80. Gas Safe registered. Our own engineers. Full emergency plumbing services across Liverpool, Sefton, Knowsley, Wirral and St Helens.",
     "30 minute response. Fixed rates from £80. Gas Safe. Our own team. We cover Liverpool, Sefton, Knowsley, Wirral and St Helens."),
]


# ---------------------------------------------------------------------------
# Flesch utility (no external deps)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not PATH.exists():
        print(f"ERROR: {PATH} not found.")
        print("Run from repo root (ideal-plumbing-site).")
        sys.exit(1)

    content = PATH.read_text(encoding='utf-8')
    original = content

    print(f"=== Applying {len(REWRITES)} rewrites to {PATH} ===\n")
    applied, skipped = 0, []
    for i, (old, new) in enumerate(REWRITES, 1):
        if old in content:
            content = content.replace(old, new, 1)
            applied += 1
        else:
            skipped.append((i, old[:80]))

    if content == original:
        print("No changes applied. Either already run, or page text has drifted.")
        sys.exit(1)

    PATH.write_text(content, encoding='utf-8')
    print(f"✓ Applied: {applied} / {len(REWRITES)}")

    if skipped:
        print(f"\n⚠ Skipped {len(skipped)} (string not found — already applied?):")
        for i, preview in skipped:
            print(f"   #{i}: {preview!r}...")

    # -----------------------------------------------------------------------
    # Verification
    # -----------------------------------------------------------------------
    print("\n=== POST-APPLY VERIFICATION ===\n")
    new_content = PATH.read_text(encoding='utf-8')

    # 1. Semantic gaps
    print("Semantic gaps:")
    for gap in ["plumbing issues", "24/7 emergency plumbing"]:
        count = new_content.lower().count(gap.lower())
        mark = "✓" if count > 0 else "✗"
        print(f"  {mark} '{gap}': {count} occurrences")

    # 2. AI-tell scan (banned phrase categories)
    print("\nAI-tell scan (zero target on each):")
    ai_tells = [
        ("em dash (—)",              r"—"),
        ("whether you/it/they/your", r"[Ww]hether (you|it|they|your)"),
        ("not just",                 r"\bnot just\b"),
        ("delve / dive into",        r"\b(delve|dive into|unpack)\b"),
        ("robust / comprehensive",   r"\b(robust|comprehensive|intricate)\b"),
        ("moreover / furthermore",   r"\b(moreover|furthermore|additionally)\b"),
        ("seamless / streamlined",   r"\b(seamless|streamlin\w*|tailored)\b"),
        ("leverage / cutting-edge",  r"\b(leverag\w*|cutting.edge|state.of.the.art)\b"),
        ("in conclusion",            r"\bin conclusion\b"),
        ("from X to Y (cap names)",  r"\b[Ff]rom [A-Z][a-z]+ to [A-Z][a-z]+\b"),
    ]
    # Strip script and style blocks for the scan (avoid false positives)
    body_only = re.sub(r'<script[^>]*>.*?</script>', '', new_content, flags=re.DOTALL)
    body_only = re.sub(r'<style[^>]*>.*?</style>', '', body_only, flags=re.DOTALL)
    for label, pattern in ai_tells:
        hits = re.findall(pattern, body_only)
        mark = "✓" if not hits else "✗"
        print(f"  {mark} {label}: {len(hits)}" + (f"  hits: {hits[:3]}" if hits else ""))

    # 3. Page-level Flesch
    print("\nPage-level Flesch (visible prose <p> blocks):")
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', new_content, flags=re.DOTALL)
    # Strip any inner HTML, ignore empty / very short fragments
    cleaned = []
    for p in paragraphs:
        text = re.sub(r'<[^>]+>', '', p).strip()
        if len(text) > 20:
            cleaned.append(text)
    scores = [flesch(p) for p in cleaned if flesch(p) is not None]
    if scores:
        avg = sum(scores) / len(scores)
        print(f"  Paragraphs: {len(scores)}")
        print(f"  Average:    {avg:.1f}")
        print(f"  Min:        {min(scores)}")
        print(f"  Below 60:   {sum(1 for s in scores if s < 60)}")
        print(f"  Below 70:   {sum(1 for s in scores if s < 70)}")

    # 4. Sanity preservation checks
    print("\nSanity preservation checks:")
    must_have = [
        ("0151 558 0334",                         "Phone number"),
        ("L32 2AL",                               "Postcode"),
        ("29 Park Road",                          "Address"),
        ("James Alexander",                       "Real review #1"),
        ("John Manley",                           "Real review #2"),
        ("Elaine McHugh",                         "Real review #3"),
        ('"reviewCount": "3"',                    "Schema review count = 3"),
        ('"ratingValue": "5.0"',                  "Schema aggregateRating = 5.0"),
        ('"@type": "FAQPage"',                    "FAQ schema present"),
        ('"@type": ["LocalBusiness", "Plumber"]', "LocalBusiness/Plumber schema"),
    ]
    for needle, label in must_have:
        mark = "✓" if needle in new_content else "✗ MISSING"
        print(f"  {mark} {label}")

    print("\n=== DONE ===")
    print("Next: review src/pages/index.astro visually, then commit + push.")


if __name__ == "__main__":
    main()
