#!/bin/bash
# ============================================================
# Module : OSINT Avancé
# Collecte d'informations publiques uniquement
# Usage autorisé uniquement
# ============================================================

TARGET="$1"          # Domaine, IP ou nom d'organisation
TYPE="${2:-domain}"  # domain | ip | org | email
OUTPUT_BASE="/output/osint"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$OUTPUT_BASE/${TARGET}_${TIMESTAMP}"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${AMBER}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }
step()  { echo -e "\n${AMBER}==== $1 ====${NC}"; }

[ -z "$TARGET" ] && { error "Usage : $0 <cible> [domain|ip|org|email]"; exit 1; }

mkdir -p "$OUTPUT"
log "Cible     : $TARGET"
log "Type      : $TYPE"
log "Résultats : $OUTPUT"

# ============================================================
step "1/6 — Informations Whois & DNS"
# ============================================================
log "Whois domaine..."
whois "$TARGET" > "$OUTPUT/whois.txt" 2>/dev/null
log "Whois terminé → whois.txt"

log "Enregistrements DNS..."
dig ANY "$TARGET" +noall +answer > "$OUTPUT/dns_records.txt" 2>/dev/null
dig MX  "$TARGET" +noall +answer >> "$OUTPUT/dns_records.txt" 2>/dev/null
dig TXT "$TARGET" +noall +answer >> "$OUTPUT/dns_records.txt" 2>/dev/null
log "DNS terminé → dns_records.txt"

log "Tentative de transfert de zone..."
for ns in $(dig NS "$TARGET" +short 2>/dev/null); do
    dig AXFR "@$ns" "$TARGET" >> "$OUTPUT/zone_transfer.txt" 2>/dev/null
done
log "Zone transfer → zone_transfer.txt"

# ============================================================
step "2/6 — Sous-domaines (sources passives)"
# ============================================================
log "Subfinder (APIs passives)..."
if command -v subfinder &>/dev/null; then
    subfinder -d "$TARGET" -silent -all \
        -o "$OUTPUT/subdomains_subfinder.txt" 2>/dev/null
    log "Subfinder → $(wc -l < "$OUTPUT/subdomains_subfinder.txt" 2>/dev/null || echo 0) sous-domaines"
fi

log "Amass (énumération passive)..."
if command -v amass &>/dev/null; then
    amass enum -passive -d "$TARGET" \
        -o "$OUTPUT/subdomains_amass.txt" 2>/dev/null
    log "Amass → $(wc -l < "$OUTPUT/subdomains_amass.txt" 2>/dev/null || echo 0) sous-domaines"
fi

log "Consolidation des sous-domaines..."
cat "$OUTPUT"/subdomains_*.txt 2>/dev/null | sort -u > "$OUTPUT/subdomains_all.txt"
TOTAL=$(wc -l < "$OUTPUT/subdomains_all.txt" 2>/dev/null || echo 0)
log "Total unique : $TOTAL sous-domaines → subdomains_all.txt"

# ============================================================
step "3/6 — theHarvester (emails, IPs, employés)"
# ============================================================
if command -v theHarvester &>/dev/null; then
    log "Recherche Google..."
    theHarvester -d "$TARGET" -b google -l 200 \
        -f "$OUTPUT/harvester_google" 2>/dev/null

    log "Recherche Bing..."
    theHarvester -d "$TARGET" -b bing -l 200 \
        -f "$OUTPUT/harvester_bing" 2>/dev/null

    log "Recherche LinkedIn..."
    theHarvester -d "$TARGET" -b linkedin \
        -f "$OUTPUT/harvester_linkedin" 2>/dev/null

    log "theHarvester terminé → harvester_*.html"
else
    warn "theHarvester non disponible"
fi

# ============================================================
step "4/6 — Recon-ng (framework OSINT)"
# ============================================================
if command -v recon-ng &>/dev/null; then
    log "Recon-ng — modules whois et domaines..."
    recon-ng -r /toolbox/modules/osint/recon_ng_commands.rc \
        > "$OUTPUT/recon_ng.txt" 2>/dev/null
    log "Recon-ng terminé → recon_ng.txt"
else
    warn "recon-ng non disponible"
fi

# ============================================================
step "5/6 — Shodan (assets exposés sur internet)"
# ============================================================
if [ -n "$SHODAN_API_KEY" ] && command -v shodan &>/dev/null; then
    log "Shodan host lookup..."
    shodan host "$TARGET" > "$OUTPUT/shodan_host.txt" 2>/dev/null

    log "Shodan search org..."
    shodan search --fields ip_str,port,org,hostnames "org:\"$TARGET\"" \
        > "$OUTPUT/shodan_org.txt" 2>/dev/null

    log "Shodan terminé → shodan_*.txt"
else
    warn "SHODAN_API_KEY non définie — Shodan ignoré"
    warn "Définissez : export SHODAN_API_KEY=votre_clé"
fi

# ============================================================
step "6/6 — Rapport OSINT"
# ============================================================
python3 /toolbox/modules/osint/osint_report.py "$OUTPUT" "$TARGET" "$TYPE"
log "OSINT terminé → $OUTPUT/report.html"
