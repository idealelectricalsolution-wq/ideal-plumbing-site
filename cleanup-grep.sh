#!/bin/bash
# Liverpool Emergency Plumber - false claims & AI tells cleanup scan
# Save in repo root, run with: bash cleanup-grep.sh
# Or save output to file: bash cleanup-grep.sh > cleanup-results.txt

set +e  # don't exit on grep no-match

SCOPE="src/"

# Colours (auto-disabled if piped to file)
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  BLUE='\033[0;34m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; BLUE=''; BOLD=''; DIM=''; NC=''
fi

search() {
  local pattern="$1"
  local label="$2"
  local severity="$3"  # HIGH, MED, LOW
  local results count
  
  results=$(grep -rniE --include="*.astro" --include="*.md" --include="*.mdx" --include="*.html" "$pattern" "$SCOPE" 2>/dev/null)
  
  if [ -z "$results" ]; then
    count=0
  else
    count=$(echo "$results" | wc -l | tr -d ' ')
  fi
  
  if [ "$count" -eq 0 ]; then
    printf "  ${GREEN}✓${NC} %-65s ${DIM}0${NC}\n" "$label"
  else
    case "$severity" in
      HIGH) printf "  ${RED}✗ %-65s %s${NC}\n" "$label" "$count" ;;
      MED)  printf "  ${YELLOW}! %-65s %s${NC}\n" "$label" "$count" ;;
      LOW)  printf "  ${YELLOW}? %-65s %s${NC}\n" "$label" "$count" ;;
    esac
    echo "$results" | sed 's/^/      /'
    echo ""
  fi
}

clear
echo -e "${BOLD}================================================================${NC}"
echo -e "${BOLD}  CLEANUP SCAN — Liverpool Emergency Plumber${NC}"
echo -e "${BOLD}================================================================${NC}"
echo ""
total_files=$(find "$SCOPE" -type f \( -name "*.astro" -o -name "*.md" -o -name "*.mdx" -o -name "*.html" \) 2>/dev/null | wc -l | tr -d ' ')
echo -e "${DIM}Scope: ${SCOPE} (.astro, .md, .mdx, .html) — $total_files files${NC}"
echo ""

echo -e "${BOLD}━━━ HIGH PRIORITY: FALSE CLAIMS (must fix immediately) ━━━${NC}"
echo ""

search 'Karen M[^a-z]|Paul R[^a-z]|Louise T[^a-z]|Kathleen R[^a-z]|Frank B[^a-z]|Norma T[^a-z]|Derek N[^a-z]|Patricia H[^a-z]|Veronica S[^a-z]|Tom K[^a-z]' \
  "Fictional reviewer names" HIGH

search '250 (Google|reviews|5-star|happy|customers|jobs|installations)' \
  "250 reviews/jobs claim" HIGH

search 'Ideal Plumbing|Ideal\+Plumbing' \
  "'Ideal Plumbing' wrong brand" HIGH

search 'since the 1990s|since 199[0-9]|established 19[0-9]{2}|founded in 19[0-9]{2}|founded 19[0-9]{2}' \
  "Pre-2000s founding claims" HIGH

search '[0-9]{2}\+ years (of experience|experience|in business|in the trade)|over [0-9]{2} years|three decades|two decades|decades of experience' \
  "Decade+ experience claims" HIGH

search 'NICEIC' \
  "NICEIC mentions (review - is this their cert or sister firm's?)" HIGH

echo ""
echo -e "${BOLD}━━━ MEDIUM PRIORITY: VOLUME CLAIMS (soften) ━━━${NC}"
echo ""

search 'every month|every week we (do|fit|install|service)' \
  "Volume frequency claims" MED

search 'most landlords|most homes|most homeowners|most customers' \
  "Most-customers claims" MED

search 'thousands of (customers|jobs|installations|homes|reviews)|hundreds of (customers|jobs|reviews)' \
  "Thousands/hundreds claims" MED

echo ""
echo -e "${BOLD}━━━ MEDIUM PRIORITY: AI TELLS (rewrite) ━━━${NC}"
echo ""

search '—' \
  "Em dashes (some in CSS - review carefully)" MED

search '[Ww]hether you|[Ww]hether it|[Ww]hether they|[Ww]hether your' \
  "Whether constructs" MED

search "not just|It's not just|It is not just" \
  "Not just constructs" MED

search 'delve|dive into|unpack' \
  "Dive/delve/unpack" MED

search 'robust|comprehensive|intricate' \
  "Robust/comprehensive/intricate" MED

search '\b(moreover|furthermore|additionally)\b' \
  "Moreover/furthermore/additionally" MED

search 'seamless|streamlin|tailored' \
  "Seamless/streamlined/tailored" MED

search 'leverag|cutting.edge|state.of.the.art' \
  "Leverage/cutting-edge/state-of-the-art" MED

search '\bin conclusion\b' \
  "In conclusion" MED

echo ""
echo -e "${BOLD}━━━ LOW PRIORITY: SPECIALIST CLAIMS (context-dependent) ━━━${NC}"
echo -e "${DIM}  Acceptable: 'radiator installation specialists', 'shower specialists'${NC}"
echo -e "${DIM}  Soften: 'microbore specialists', 'open-vented specialists', etc.${NC}"
echo ""

search 'specialists?\b' \
  "Specialist mentions (review by context)" LOW

echo ""
echo -e "${BOLD}━━━ LOW PRIORITY: PUFFERY (review by context) ━━━${NC}"
echo ""

search 'highest contamination|highest sludge|worst contamination|highest in (Merseyside|Liverpool)' \
  "Worst/highest puffery" LOW

search 'most experienced|most trusted|leading (provider|firm|company)|premier|number one' \
  "Superlative puffery" LOW

search 'unbeatable|unrivalled|unparalleled|second to none|best in (Liverpool|the area|Merseyside)' \
  "Strong superlative claims" LOW

echo ""
echo -e "${BOLD}━━━ FILES WITH MOST HIGH-PRIORITY ISSUES ━━━${NC}"
echo ""

# Aggregate just the HIGH severity hits per file
echo "Files ranked by HIGH-priority hit count:"
echo ""
{
  grep -rliE --include="*.astro" --include="*.md" 'Karen M[^a-z]|Paul R[^a-z]|Louise T[^a-z]|Kathleen R[^a-z]|Frank B[^a-z]|Norma T[^a-z]|Derek N[^a-z]|Patricia H[^a-z]|Veronica S[^a-z]|Tom K[^a-z]' "$SCOPE" 2>/dev/null
  grep -rliE --include="*.astro" --include="*.md" '250 (Google|reviews|5-star|happy|customers)' "$SCOPE" 2>/dev/null
  grep -rliE --include="*.astro" --include="*.md" 'Ideal Plumbing|Ideal\+Plumbing' "$SCOPE" 2>/dev/null
  grep -rliE --include="*.astro" --include="*.md" 'since the 1990s|since 199[0-9]|established 19[0-9]{2}|founded in 19[0-9]{2}' "$SCOPE" 2>/dev/null
  grep -rliE --include="*.astro" --include="*.md" '[0-9]{2}\+ years (of experience|experience|in business)|over [0-9]{2} years|decades of experience' "$SCOPE" 2>/dev/null
} | sort | uniq -c | sort -rn | head -20

echo ""
echo -e "${BOLD}================================================================${NC}"
echo -e "${BOLD}  SCAN COMPLETE${NC}"
echo -e "${BOLD}================================================================${NC}"
echo ""
echo -e "${BOLD}What to do next:${NC}"
echo "  1. Fix all HIGH (red ✗) — non-negotiable false claims"
echo "  2. Review MED (yellow !) case by case — soften or rewrite"
echo "  3. Spot-check LOW (yellow ?) — context dependent"
echo ""
echo -e "${DIM}Tip: save the output for reference:${NC}"
echo -e "${DIM}  bash cleanup-grep.sh > cleanup-results.txt${NC}"
echo ""
