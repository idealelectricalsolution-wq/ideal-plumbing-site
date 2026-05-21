#!/bin/bash
# cleanup-fix.sh - Batch fix false claims across the repo
# Run from: ~/Documents/GitHub/ideal-plumbing-site
# Usage: bash cleanup-fix.sh

set -e

# Sanity check
if [ ! -d "src/pages" ]; then
  echo "ERROR: src/pages directory not found. Run this from the repo root."
  exit 1
fi

# Colours
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  BLUE='\033[0;34m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; BLUE=''; BOLD=''; DIM=''; NC=''
fi

echo -e "${BOLD}================================================================${NC}"
echo -e "${BOLD}  BULK CLEANUP: Liverpool Emergency Plumber${NC}"
echo -e "${BOLD}================================================================${NC}"
echo ""

# Show git status
if [ -n "$(git status --porcelain)" ]; then
  echo -e "${YELLOW}You have uncommitted changes:${NC}"
  git status --short
  echo ""
  read -p "Proceed anyway? Your changes will be mixed with the cleanup. (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted. Commit or stash your changes first."
    exit 0
  fi
fi

echo -e "${YELLOW}This will modify multiple files in src/pages/.${NC}"
read -p "Proceed with bulk fixes? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

# Helper: count matches for a pattern
count_hits() {
  grep -rEc "$1" src/pages 2>/dev/null | awk -F: '{s+=$2} END {print s+0}'
}

echo ""
echo -e "${BOLD}━━━ FIX 1: '250 Google Reviews' → '3 Google Reviews' ━━━${NC}"
BEFORE=$(count_hits "5\.0 · 250 Google Reviews")
find src/pages -name "*.astro" -type f -exec sed -i '' 's|5\.0 · 250 Google Reviews|5.0 · 3 Google Reviews|g' {} +
AFTER=$(count_hits "5\.0 · 250 Google Reviews")
printf "  ${GREEN}Fixed: $((BEFORE - AFTER)) of $BEFORE${NC}\n"
echo ""

echo -e "${BOLD}━━━ FIX 2: Wrong Google search URL ━━━${NC}"
BEFORE=$(count_hits "Ideal\+Plumbing\+Solutions\+Liverpool\+reviews")
find src/pages -name "*.astro" -type f -exec sed -i '' 's|Ideal+Plumbing+Solutions+Liverpool+reviews|Liverpool+Emergency+Plumber+reviews|g' {} +
AFTER=$(count_hits "Ideal\+Plumbing\+Solutions\+Liverpool\+reviews")
printf "  ${GREEN}Fixed: $((BEFORE - AFTER)) of $BEFORE${NC}\n"
echo ""

echo -e "${BOLD}━━━ FIX 3: 'Choose Ideal Plumbing' H2 headings → 'Choose Us' ━━━${NC}"
BEFORE=$(count_hits "Choose Ideal Plumbing")
find src/pages -name "*.astro" -type f -exec sed -i '' 's|Choose Ideal Plumbing|Choose Us|g' {} +
AFTER=$(count_hits "Choose Ideal Plumbing")
printf "  ${GREEN}Fixed: $((BEFORE - AFTER)) of $BEFORE${NC}\n"
echo ""

echo -e "${BOLD}━━━ FIX 4: 'Quote from Ideal Plumbing' (blog link) ━━━${NC}"
BEFORE=$(count_hits "Quote from Ideal Plumbing")
find src/pages -name "*.astro" -type f -exec sed -i '' 's|Quote from Ideal Plumbing|Quote|g' {} +
AFTER=$(count_hits "Quote from Ideal Plumbing")
printf "  ${GREEN}Fixed: $((BEFORE - AFTER)) of $BEFORE${NC}\n"
echo ""

echo -e "${BOLD}================================================================${NC}"
echo -e "${BOLD}  VERIFICATION${NC}"
echo -e "${BOLD}================================================================${NC}"
echo ""

# Post-state checks
echo -e "${BOLD}Remaining 'Ideal Plumbing' hits (should be fake review bodies only):${NC}"
REMAIN=$(grep -rEn "Ideal Plumbing" src/pages 2>/dev/null)
if [ -z "$REMAIN" ]; then
  echo -e "  ${GREEN}✓ Zero hits remaining${NC}"
else
  echo "$REMAIN" | sed 's/^/  /'
fi
echo ""

echo -e "${BOLD}Remaining '250 Google' hits:${NC}"
REMAIN=$(grep -rEn "250 Google" src/pages 2>/dev/null)
if [ -z "$REMAIN" ]; then
  echo -e "  ${GREEN}✓ Zero hits remaining${NC}"
else
  echo "$REMAIN" | sed 's/^/  /'
fi
echo ""

echo -e "${BOLD}━━━ FILES WITH FICTIONAL REVIEWER NAMES (needs manual fix) ━━━${NC}"
echo -e "${DIM}Original list + new names found in output (Debbie H, Susan P, Neil A, Gary L)${NC}"
echo ""
FAKE_FILES=$(grep -rlE '\b(Louise T|Debbie H|Susan P|Neil A|Gary L|Karen M|Paul R|Tom K|Kathleen R|Frank B|Norma T|Derek N|Patricia H|Veronica S)\b' src/pages 2>/dev/null)
if [ -z "$FAKE_FILES" ]; then
  echo -e "  ${GREEN}✓ No files contain fictional reviewer names${NC}"
else
  echo "$FAKE_FILES" | sed 's/^/  /'
fi
echo ""

echo -e "${BOLD}━━━ GIT DIFF SUMMARY ━━━${NC}"
echo ""
git diff --stat src/pages/

echo ""
echo -e "${BOLD}================================================================${NC}"
echo -e "${BOLD}  NEXT STEPS${NC}"
echo -e "${BOLD}================================================================${NC}"
echo ""
echo "  1. Review the diff if you want:"
echo -e "     ${DIM}git diff src/pages/ | less${NC}"
echo ""
echo "  2. Send the fictional-reviewer-name files (listed above) to Claude,"
echo "     one at a time — needs targeted str_replace for each fake review."
echo ""
echo "  3. After fictional reviews are cleaned, commit and push:"
echo -e "     ${DIM}git add . && git commit -m 'Site-wide cleanup: 250 reviews fix + Ideal Plumbing brand swap' && git push${NC}"
echo ""
