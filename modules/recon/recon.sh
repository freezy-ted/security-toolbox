#!/bin/bash
# ============================================================
# Module : Reconnaissance
# Toolbox de sécurité — usage autorisé uniquement
# ============================================================

TARGET="$1"
OUTPUT_BASE="/output/recon"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$OUTPUT_BASE/${TARGET}_${TIMESTAMP}"

# ---- Couleurs terminal ----
GREEN='\033[0;32m'
AMBER='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${AMBER}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }
step()  { echo -e "\n${AMBER}==== $1 ====${NC}"; }

# ---- Vérifications ----
if [ -z "$TARGET" ]; then
    error "Usage : $0 <IP ou domaine>"
    exit 1
fi

mkdir -p "$OUTPUT"
log "Cible       : $TARGET"
log "Résultats   : $OUTPUT"

# ============================================================
# ÉTAPE 1 — OSINT PASSIF
# ============================================================
step "1/5 — OSINT passif"

log "Whois..."
whois "$TARGET" > "$OUTPUT/whois.txt" 2>/dev/null
log "Whois terminé → whois.txt"

if command -v theHarvester &>/dev/null; then
    log "theHarvester (emails, sous-domaines, IPs)..."
    theHarvester -d "$TARGET" -b all -f "$OUTPUT/harvester" 2>/dev/null
    log "theHarvester terminé → harvester.html"
else
    warn "theHarvester non installé, étape ignorée"
fi

if command -v subfinder &>/dev/null; then
    log "Subfinder (sous-domaines passifs)..."
    subfinder -d "$TARGET" -silent -o "$OUTPUT/subdomains.txt" 2>/dev/null
    SUBDOMAIN_COUNT=$(wc -l < "$OUTPUT/subdomains.txt" 2>/dev/null || echo 0)
    log "Subfinder terminé → $SUBDOMAIN_COUNT sous-domaines trouvés"
else
    warn "subfinder non installé, étape ignorée"
fi

# ============================================================
# ÉTAPE 2 — DNS
# ============================================================
step "2/5 — Énumération DNS"

log "DNSrecon (enregistrements standard)..."
dnsrecon -d "$TARGET" -t std > "$OUTPUT/dns_std.txt" 2>/dev/null

log "Tentative de transfert de zone..."
dnsrecon -d "$TARGET" -t axfr > "$OUTPUT/dns_axfr.txt" 2>/dev/null

log "DNS terminé → dns_std.txt / dns_axfr.txt"

# ============================================================
# ÉTAPE 3 — SCAN DE PORTS
# ============================================================
step "3/5 — Scan Nmap"

log "Scan rapide (top 1000 ports)..."
nmap -sV -sC --open -T4 \
    -oA "$OUTPUT/nmap_fast" \
    "$TARGET" 2>/dev/null

log "Scan complet (tous les ports)..."
nmap -sV -p- --open -T4 \
    -oA "$OUTPUT/nmap_full" \
    "$TARGET" 2>/dev/null

log "Nmap terminé → nmap_fast.* / nmap_full.*"

# ============================================================
# ÉTAPE 4 — SHODAN (optionnel, nécessite une API key)
# ============================================================
step "4/5 — Shodan"

if [ -n "$SHODAN_API_KEY" ] && command -v shodan &>/dev/null; then
    log "Configuration Shodan..."
    shodan init "$SHODAN_API_KEY" 2>/dev/null
    log "Recherche Shodan pour $TARGET..."
    shodan host "$TARGET" > "$OUTPUT/shodan.txt" 2>/dev/null
    log "Shodan terminé → shodan.txt"
else
    warn "SHODAN_API_KEY non définie — Shodan ignoré"
fi

# ============================================================
# ÉTAPE 5 — RAPPORT
# ============================================================
step "5/5 — Génération du rapport"

python3 /toolbox/modules/recon/recon_report.py "$OUTPUT" "$TARGET"

log "Reconnaissance terminée !"
log "Rapport HTML → $OUTPUT/report.html"
