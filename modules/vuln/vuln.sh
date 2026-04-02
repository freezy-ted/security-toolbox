#!/bin/bash
# ============================================================
# Module : Scan de vulnérabilités
# Nuclei + OpenVAS — usage autorisé uniquement
# ============================================================

TARGET="$1"
OUTPUT_BASE="/output/vuln"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$OUTPUT_BASE/${TARGET}_${TIMESTAMP}"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${AMBER}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }
step()  { echo -e "\n${AMBER}==== $1 ====${NC}"; }

[ -z "$TARGET" ] && { error "Usage : $0 <IP ou domaine>"; exit 1; }

mkdir -p "$OUTPUT"
log "Cible     : $TARGET"
log "Résultats : $OUTPUT"

# ============================================================
step "1/4 — Nuclei (CVE et vulnérabilités connues)"
# ============================================================
if command -v nuclei &>/dev/null; then
    log "Mise à jour des templates Nuclei..."
    nuclei -update-templates -silent 2>/dev/null

    log "Scan CVE critique et élevé..."
    nuclei -u "$TARGET" \
        -severity critical,high,medium \
        -t cves/ \
        -o "$OUTPUT/nuclei_cves.txt" \
        -silent 2>/dev/null
    log "Scan CVE terminé → nuclei_cves.txt"

    log "Scan de mauvaises configurations..."
    nuclei -u "$TARGET" \
        -t misconfiguration/ \
        -o "$OUTPUT/nuclei_misconfig.txt" \
        -silent 2>/dev/null
    log "Scan misconfig terminé → nuclei_misconfig.txt"

    log "Scan d'expositions de données..."
    nuclei -u "$TARGET" \
        -t exposures/ \
        -o "$OUTPUT/nuclei_exposures.txt" \
        -silent 2>/dev/null
    log "Scan exposures terminé → nuclei_exposures.txt"

    log "Scan des technologies détectées..."
    nuclei -u "$TARGET" \
        -t technologies/ \
        -o "$OUTPUT/nuclei_tech.txt" \
        -silent 2>/dev/null
    log "Détection technos terminée → nuclei_tech.txt"
else
    warn "nuclei non disponible — étape ignorée"
fi

# ============================================================
step "2/4 — Nmap NSE (scripts de détection de vulnérabilités)"
# ============================================================
log "Scan Nmap vulnérabilités (scripts vuln)..."
nmap -sV --script vuln \
    -oN "$OUTPUT/nmap_vuln.txt" \
    "$TARGET" 2>/dev/null
log "Nmap vuln terminé → nmap_vuln.txt"

# ============================================================
step "3/4 — Nmap NSE (scripts safe + default)"
# ============================================================
log "Scan Nmap scripts safe..."
nmap -sV --script safe \
    -oN "$OUTPUT/nmap_safe.txt" \
    "$TARGET" 2>/dev/null
log "Nmap safe terminé → nmap_safe.txt"

# ============================================================
step "4/4 — Rapport"
# ============================================================
python3 /toolbox/modules/vuln/vuln_report.py "$OUTPUT" "$TARGET"
log "Scan de vulnérabilités terminé → $OUTPUT/report.html"
