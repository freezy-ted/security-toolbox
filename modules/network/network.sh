#!/bin/bash
# ============================================================
# Module : Réseau passif
# Capture et analyse de trafic — usage autorisé uniquement
# ============================================================

INTERFACE="${1:-eth0}"
DURATION="${2:-300}"   # durée en secondes (défaut 5 min)
OUTPUT_BASE="/output/network"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$OUTPUT_BASE/capture_$TIMESTAMP"

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${AMBER}[!]${NC} $1"; }
step() { echo -e "\n${AMBER}==== $1 ====${NC}"; }

mkdir -p "$OUTPUT"
PCAP="$OUTPUT/capture.pcap"

log "Interface  : $INTERFACE"
log "Durée      : ${DURATION}s"
log "Résultats  : $OUTPUT"

# ============================================================
step "1/4 — Capture trafic (${DURATION}s)"
# ============================================================
log "Capture en cours... (Ctrl+C pour arrêter)"
tcpdump -i "$INTERFACE" -w "$PCAP" -G "$DURATION" -W 1 2>/dev/null
log "Capture terminée → capture.pcap"

# ============================================================
step "2/4 — Analyse tshark"
# ============================================================
log "Conversations TCP..."
tshark -r "$PCAP" -q -z conv,tcp > "$OUTPUT/conv_tcp.txt" 2>/dev/null

log "Requêtes DNS..."
tshark -r "$PCAP" -Y "dns" -T fields \
    -e frame.time -e ip.src -e dns.qry.name \
    > "$OUTPUT/dns_queries.txt" 2>/dev/null

log "Requêtes HTTP..."
tshark -r "$PCAP" -Y "http.request" -T fields \
    -e ip.src -e http.host -e http.request.method -e http.request.uri \
    > "$OUTPUT/http_requests.txt" 2>/dev/null

log "Statistiques générales..."
tshark -r "$PCAP" -q -z io,stat,60 > "$OUTPUT/stats.txt" 2>/dev/null

# ============================================================
step "3/4 — Découverte d'hôtes"
# ============================================================
log "Extraction des IPs actives..."
tshark -r "$PCAP" -T fields -e ip.src -e ip.dst 2>/dev/null \
    | tr '\t' '\n' | sort -u | grep -v '^$' > "$OUTPUT/hosts.txt"
HOST_COUNT=$(wc -l < "$OUTPUT/hosts.txt")
log "$HOST_COUNT hôtes uniques détectés → hosts.txt"

# ============================================================
step "4/4 — Rapport"
# ============================================================
python3 /toolbox/modules/network/network_report.py "$OUTPUT"
log "Analyse réseau terminée → $OUTPUT/report.html"
