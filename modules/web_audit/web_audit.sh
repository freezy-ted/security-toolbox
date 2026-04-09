#!/bin/bash

# ============================================================

# Module : Audit Web

# Toolbox de sécurité — usage autorisé uniquement

# ============================================================

TARGET="$1"
OUTPUT_BASE="/output/web"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CLEAN_TARGET=$(echo "$TARGET" | sed 's|https\?://||g' | sed 's|/|_|g')
OUTPUT="$OUTPUT_BASE/${CLEAN_TARGET}_${TIMESTAMP}"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${AMBER}[!]${NC} $1"; }
step()  { echo -e "\n${AMBER}==== $1 ====${NC}"; }

[ -z "$TARGET" ] && { echo "Usage : $0 <URL>"; exit 1; }
[[ "$TARGET" != http* ]] && URL="http://$TARGET" || URL="$TARGET"

mkdir -p "$OUTPUT"
log "Cible : $URL"
log "Résultats : $OUTPUT"

step "1/4 — Nikto"
nikto -h "$URL" -output "$OUTPUT/nikto.txt" -Format txt 2>/dev/null
log "Nikto terminé → nikto.txt"

step "2/4 — Gobuster"
WORDLIST="/usr/share/wordlists/dirb/common.txt"
[ ! -f "$WORDLIST" ] && WORDLIST="/usr/share/dirb/wordlists/common.txt"
if [ -f "$WORDLIST" ]; then
    gobuster dir -u "$URL" -w "$WORDLIST" -o "$OUTPUT/gobuster.txt" -t 30 --no-error 2>/dev/null
    log "Gobuster terminé → gobuster.txt"
else
    warn "Wordlist non trouvée"
fi

step "3/4 — FFUF"
if command -v ffuf &>/dev/null && [ -f "$WORDLIST" ]; then
    ffuf -u "$URL/FUZZ" -w "$WORDLIST" -o "$OUTPUT/ffuf.json" -of json -mc 200,201,301,302,403 -t 30 -s 2>/dev/null
    log "FFUF terminé → ffuf.json"
fi

step "4/4 — Rapport"
python3 /toolbox/modules/web_audit/web_report.py "$OUTPUT" "$CLEAN_TARGET"
log "Audit Web terminé → $OUTPUT/report.html"
