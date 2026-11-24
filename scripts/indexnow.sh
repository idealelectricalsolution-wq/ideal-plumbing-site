#!/bin/sh
# Tell Bing/IndexNow which pages changed. Usage: sh scripts/indexnow.sh /page-one /page-two
KEY=$(cat "$(dirname "$0")/../.indexnow-key")
HOST=liverpoolemergencyplumber.co.uk
URLS=""
for p in "$@"; do URLS="$URLS\"https://$HOST$p\","; done
URLS="[${URLS%,}]"
curl -s -o /dev/null -w "IndexNow: %{http_code}\n" -X POST https://api.indexnow.org/indexnow \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY.txt\",\"urlList\":$URLS}"
