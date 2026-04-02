#!/bin/bash
# ============================================================
# Module : Active Directory
# Énumération et cartographie — usage autorisé uniquement
# ============================================================

DC_IP="$1"       # IP du contrôleur de domaine
DOMAIN="$2"      # ex: corp.local
USER="$3"        # compte de domaine (lecture seule suffit)
PASS="$4"        # mot de passe

OUTPUT_BASE="/output/ad"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$OUTPUT_BASE/${DOMAIN}_${TIMESTAMP}"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${AMBER}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }
step()  { echo -e "\n${AMBER}==== $1 ====${NC}"; }

if [ -z "$DC_IP" ] || [ -z "$DOMAIN" ] || [ -z "$USER" ] || [ -z "$PASS" ]; then
    error "Usage : $0 <DC_IP> <domaine> <utilisateur> <mot_de_passe>"
    exit 1
fi

mkdir -p "$OUTPUT"
log "DC        : $DC_IP"
log "Domaine   : $DOMAIN"
log "Résultats : $OUTPUT"

# ============================================================
step "1/4 — Dump LDAP (ldapdomaindump)"
# ============================================================
ldapdomaindump \
    -u "$DOMAIN\\$USER" \
    -p "$PASS" \
    "$DC_IP" \
    -o "$OUTPUT/ldap" \
    2>/dev/null
log "LDAP dump terminé → $OUTPUT/ldap/"

# ============================================================
step "2/4 — Énumération (enum4linux-ng)"
# ============================================================
if command -v enum4linux-ng &>/dev/null; then
    enum4linux-ng -A \
        -u "$USER" -p "$PASS" \
        "$DC_IP" > "$OUTPUT/enum4linux.txt" 2>/dev/null
    log "enum4linux-ng terminé → enum4linux.txt"
else
    warn "enum4linux-ng non disponible"
fi

# ============================================================
step "3/4 — BloodHound (collecte)"
# ============================================================
if command -v bloodhound-python &>/dev/null; then
    bloodhound-python \
        -d "$DOMAIN" \
        -u "$USER" \
        -p "$PASS" \
        -ns "$DC_IP" \
        -c All \
        --zip \
        -o "$OUTPUT/bloodhound" \
        2>/dev/null
    log "BloodHound terminé → $OUTPUT/bloodhound/"
    log "Importe le .zip dans l'interface BloodHound pour visualiser"
else
    warn "bloodhound-python non disponible"
fi

# ============================================================
step "4/4 — Rapport"
# ============================================================
python3 /toolbox/modules/ad_audit/ad_report.py "$OUTPUT" "$DOMAIN" "$DC_IP"
log "Audit AD terminé → $OUTPUT/report.html"
