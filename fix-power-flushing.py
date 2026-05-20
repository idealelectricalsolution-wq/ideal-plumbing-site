#!/usr/bin/env python3
"""
Patch power-flushing-liverpool.astro with 6 surgical edits:
  1. Add LocalBusiness/Plumber schema with aggregateRating (Semrush flag)
  2. Hero sub: lead with direct factual answer for AI extraction
  3. Process step 1: fix 5x "We" sentence-start staccato
  4. Process step 3: smooth fragmented sentences  
  5. Reviews header: "Liverpool Customers" -> "Our Customers" (truthful framing)
  6. Add 4 new visible FAQ entries (aligns visible 12 to schema 12)

Run from repo root:
  python3 fix-power-flushing.py
"""
import re
from pathlib import Path

FILE = Path("src/pages/power-flushing-liverpool.astro")
if not FILE.exists():
    raise SystemExit(f"File not found: {FILE.resolve()}")

text = FILE.read_text()
original_len = len(text)
misses = []

# ====================================================================
# EDIT 1: Add LocalBusiness/Plumber schema before Service schema
# ====================================================================
old_service_open = '  <script type="application/ld+json" slot="head">\n  {\n    "@context": "https://schema.org",\n    "@type": "Service",\n    "name": "Power Flush Radiator Liverpool",'

LOCAL_BUSINESS_SCHEMA = '''  <script type="application/ld+json" slot="head">
  {
    "@context": "https://schema.org",
    "@type": ["LocalBusiness", "Plumber"],
    "@id": "https://liverpoolemergencyplumber.co.uk/#business",
    "name": "Liverpool Emergency Plumber",
    "image": "https://liverpoolemergencyplumber.co.uk/ideal-plumbing-logo.png",
    "url": "https://liverpoolemergencyplumber.co.uk/power-flushing-liverpool",
    "telephone": "+441515580334",
    "email": "emergencyplumberliverpool@gmail.com",
    "priceRange": "££",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "29 Park Road",
      "addressLocality": "Kirkby",
      "addressRegion": "Merseyside",
      "postalCode": "L32 2AL",
      "addressCountry": "GB"
    },
    "openingHoursSpecification": {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
      "opens": "00:00",
      "closes": "23:59"
    },
    "areaServed": [
      { "@type": "City", "name": "Liverpool" },
      { "@type": "City", "name": "Wirral" },
      { "@type": "City", "name": "St Helens" },
      { "@type": "City", "name": "Formby" }
    ],
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "5.0",
      "reviewCount": "3",
      "bestRating": "5"
    }
  }
  </script>

  <script type="application/ld+json" slot="head">
  {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "Power Flush Radiator Liverpool",'''

if old_service_open in text:
    text = text.replace(old_service_open, LOCAL_BUSINESS_SCHEMA, 1)
    print("✓ Edit 1: LocalBusiness/Plumber schema with aggregateRating added")
else:
    misses.append("Edit 1: Service schema opener not found")

# ====================================================================
# EDIT 2: Hero sub -> AI-extraction-friendly opener
# ====================================================================
old_hero = '<p class="page-hero-sub">Power flush radiator Liverpool from £350 fixed price. Cold spots, noisy boilers and sludge fixed by Gas Safe engineers in a single day. All chemicals and inhibitor included. Written report provided.</p>'
new_hero = '<p class="page-hero-sub">A power flush in Liverpool costs from £350 fixed price and clears cold radiators, noisy boilers and sludge in a single day. Done by Gas Safe engineers with all chemicals, inhibitor and a written report included.</p>'

if old_hero in text:
    text = text.replace(old_hero, new_hero, 1)
    print("✓ Edit 2: Hero sub rewritten for AI extraction")
else:
    misses.append("Edit 2: Hero sub paragraph not found")

# ====================================================================
# EDIT 3: Process Step 1 - kill 5x "We" staccato
# ====================================================================
old_step1 = '<strong>First check, 20 to 30 minutes</strong><p>We inspect the system. We check the boiler. We find the radiators with the worst blockages. We test a water sample to gauge the sludge level. We talk through any concerns with you before we start.</p>'
new_step1 = '<strong>First check, 20 to 30 minutes</strong><p>Our engineer inspects the system, checks the boiler and finds the radiators with the worst blockages. A water sample is tested to gauge the sludge level. We talk through any concerns with you before starting work.</p>'

if old_step1 in text:
    text = text.replace(old_step1, new_step1, 1)
    print("✓ Edit 3: Process step 1 staccato fixed")
else:
    misses.append("Edit 3: Process step 1 not found")

# ====================================================================
# EDIT 4: Process Step 3 - smooth fragments
# ====================================================================
old_step3 = '<strong>Flush machine hooked up</strong><p>We hook up the flush machine. The link point is at the boiler pump or a radiator tail. Which one depends on the system layout.</p>'
new_step3 = '<strong>Flush machine hooked up</strong><p>We hook up the flush machine to either the boiler pump or a radiator tail, depending on the system layout.</p>'

if old_step3 in text:
    text = text.replace(old_step3, new_step3, 1)
    print("✓ Edit 4: Process step 3 smoothed")
else:
    misses.append("Edit 4: Process step 3 not found")

# ====================================================================
# EDIT 5: Reviews header - "Liverpool Customers" -> "Our Customers"
# ====================================================================
old_reviews = '<h2 style="margin-bottom:0.1rem;">What Liverpool Customers Say</h2>\n        <p class="pf-sub" style="margin:0 0 0.75rem;">Real Google reviews from Liverpool customers</p>'
new_reviews = '<h2 style="margin-bottom:0.1rem;">What Our Customers Say</h2>\n        <p class="pf-sub" style="margin:0 0 0.75rem;">Real Google reviews from across our coverage area</p>'

if old_reviews in text:
    text = text.replace(old_reviews, new_reviews, 1)
    print("✓ Edit 5: Reviews header truthful framing")
else:
    misses.append("Edit 5: Reviews header not found")

# ====================================================================
# EDIT 6: Add 4 new visible FAQs at start of FAQ list
# (Currently visible=8, schema=12; this brings visible to 12)
# ====================================================================
NEW_FAQS = '<details class="pf-faq-item" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:0.5rem;padding:0;"><summary style="cursor:pointer;padding:1rem 1.25rem;font-weight:700;color:#1a3a5c;display:flex;align-items:center;gap:0.5rem;"><span class="pf-faq-tag pf-tag-navy">DEFINE</span>&nbsp; What is power flushing?</summary><div class="pf-faq-body" style="padding:0 1.25rem 1.25rem;border-top:1px solid #f1f5f9;"><p>A power flush is a professional cleaning process. High-velocity water mixed with cleaning chemicals is pumped through your central heating system at low pressure around 2 bar. The flow dislodges sludge, magnetite, rust and debris from radiators, pipework and the boiler heat exchanger. The dirty water is filtered out and the system refilled with clean water and corrosion inhibitor. A typical power flush in Liverpool takes 4 to 8 hours and is completed in a single visit.</p></div></details>\n        <details class="pf-faq-item" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:0.5rem;padding:0;"><summary style="cursor:pointer;padding:1rem 1.25rem;font-weight:700;color:#1a3a5c;display:flex;align-items:center;gap:0.5rem;"><span class="pf-faq-tag pf-tag-navy">TIME</span>&nbsp; How long does a power flush take?</summary><div class="pf-faq-body" style="padding:0 1.25rem 1.25rem;border-top:1px solid #f1f5f9;"><p>A power flush takes between 4 and 8 hours depending on system size and contamination level. A typical 3-bed Liverpool property takes around 6 hours. Small systems with up to 6 radiators take 3 to 4 hours. Larger or heavily clogged systems can take a full day. We always complete in a single visit. A morning start at 8am to 9am is recommended to give the full day if needed.</p></div></details>\n        <details class="pf-faq-item" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:0.5rem;padding:0;"><summary style="cursor:pointer;padding:1rem 1.25rem;font-weight:700;color:#1a3a5c;display:flex;align-items:center;gap:0.5rem;"><span class="pf-faq-tag pf-tag-green">FREQUENCY</span>&nbsp; How often should I power flush my central heating?</summary><div class="pf-faq-body" style="padding:0 1.25rem 1.25rem;border-top:1px solid #f1f5f9;"><p>The <a href="https://www.ciphe.org.uk" target="_blank" rel="noopener">Chartered Institute of Plumbing and Heating Engineering</a> and the <a href="https://www.powerflushassociation.com/faq.html" target="_blank" rel="noopener">Power Flush Association</a> both recommend power flushing every 5 to 7 years for a well-maintained system. Annual boiler servicing should include an inhibitor level check between flushes. If inhibitor drops too low, corrosion accelerates and systems may need flushing sooner. Fitting a magnetic filter helps extend the gap between flushes.</p></div></details>\n        <details class="pf-faq-item" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:0.5rem;padding:0;"><summary style="cursor:pointer;padding:1rem 1.25rem;font-weight:700;color:#1a3a5c;display:flex;align-items:center;gap:0.5rem;"><span class="pf-faq-tag pf-tag-orange">SIGNS</span>&nbsp; How do I know if my Liverpool home needs a power flush?</summary><div class="pf-faq-body" style="padding:0 1.25rem 1.25rem;border-top:1px solid #f1f5f9;"><p>The main signs are cold spots at the bottom of radiators, boiler making banging or kettling noises, system taking much longer to warm up than it used to, black water when bleeding radiators and some radiators not heating at all. If you recognise two or more of these signs, your central heating likely needs a power flush. Call Liverpool Emergency Plumber on 0151 558 0334 for a free no-obligation assessment.</p></div></details>\n        '

old_faq_marker = '<div class="pf-faq" style="display:flex;flex-direction:column;gap:0.5rem;">\n        <details class="pf-faq-item" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:0.5rem;padding:0;"><summary style="cursor:pointer;padding:1rem 1.25rem;font-weight:700;color:#1a3a5c;display:flex;align-items:center;gap:0.5rem;"><span class="pf-faq-tag pf-tag-orange">COST</span>&nbsp; How much does power flushing cost in Liverpool?'

new_faq_marker = '<div class="pf-faq" style="display:flex;flex-direction:column;gap:0.5rem;">\n        ' + NEW_FAQS + '<details class="pf-faq-item" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:0.5rem;padding:0;"><summary style="cursor:pointer;padding:1rem 1.25rem;font-weight:700;color:#1a3a5c;display:flex;align-items:center;gap:0.5rem;"><span class="pf-faq-tag pf-tag-orange">COST</span>&nbsp; How much does power flushing cost in Liverpool?'

if old_faq_marker in text:
    text = text.replace(old_faq_marker, new_faq_marker, 1)
    print("✓ Edit 6: 4 new visible FAQs added (aligned with schema)")
else:
    misses.append("Edit 6: FAQ container opening not found")

# ====================================================================
# Write and report
# ====================================================================
FILE.write_text(text)
new_len = len(text)
delta = new_len - original_len

print(f"\n{'='*60}")
print(f"File: {FILE}")
print(f"Size: {original_len:,} -> {new_len:,} bytes (+{delta:,})")
print(f"{'='*60}")

if misses:
    print(f"⚠  {len(misses)} edits FAILED:")
    for m in misses:
        print(f"   ✗ {m}")
    print("\nThe file has been written with the edits that DID match.")
    print("Run `git diff` to see what changed, then ping Claude for the failing patterns.")
else:
    print("✓ All 6 edits applied cleanly. Ready to verify and commit.")

# Quick post-run validation counts
print(f"\n--- Post-run validation ---")
print(f"LocalBusiness/Plumber schema:    {'✓' if 'LocalBusiness' in text and 'Plumber' in text else '✗'}")
print(f"aggregateRating:                 {'✓' if 'aggregateRating' in text else '✗'}")
faq_schema = len(re.findall(r'"@type": "Question"', text))
faq_visible = len(re.findall(r'class="pf-faq-item"', text))
print(f"FAQ schema questions:            {faq_schema}")
print(f"FAQ visible items:               {faq_visible}")
print(f"FAQ count match:                 {'✓' if faq_schema == faq_visible else '✗'}")
print(f"'30 years' false claims:         {len(re.findall(r'(?<!1)30[- ]?year', text, re.IGNORECASE))} (should be 0)")
print(f"'250 reviews' false claims:      {len(re.findall(r'250[- ]?(five|review)', text, re.IGNORECASE))} (should be 0)")
