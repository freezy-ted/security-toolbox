#!/bin/bash
# ============================================================
# run.sh — Lancement et gestion de Security Toolbox
# Usage : bash run.sh [commande] [options]
# ============================================================

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${AMBER}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }
info()  { echo -e "${BLUE}[i]${NC} $1"; }

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$INSTALL_DIR/output"
COMPOSE="docker-compose"
command -v docker-compose &>/dev/null || COMPOSE="docker compose"

# ── Bannière ───────────────────────────────────────────────
banner(){
echo -e "${GREEN}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║        Security Toolbox v1.0          ║"
echo "  ║     Usage autorisé uniquement         ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"
}

# ── Aide ───────────────────────────────────────────────────
usage(){
    banner
    echo -e "  ${AMBER}Commandes disponibles :${NC}"
    echo ""
    echo -e "  ${GREEN}start${NC}                   Démarrer le dashboard web"
    echo -e "  ${GREEN}stop${NC}                    Arrêter tous les services"
    echo -e "  ${GREEN}status${NC}                  Voir l'état des conteneurs"
    echo -e "  ${GREEN}logs${NC}                    Voir les logs du dashboard"
    echo ""
    echo -e "  ${GREEN}recon${NC}    <cible>         Lancer la reconnaissance"
    echo -e "  ${GREEN}web${NC}      <url>           Lancer l'audit web"
    echo -e "  ${GREEN}network${NC}  [iface] [durée] Lancer la capture réseau"
    echo -e "  ${GREEN}ad${NC}       <dc> <dom> <u> <p>  Lancer l'audit AD"
    echo -e "  ${GREEN}report${NC}   <cible>         Générer le rapport consolidé"
    echo ""
    echo -e "  ${GREEN}results${NC}                 Lister les résultats disponibles"
    echo -e "  ${GREEN}clean${NC}                   Supprimer tous les résultats"
    echo -e "  ${GREEN}update${NC}                  Reconstruire toutes les images"
    echo -e "  ${GREEN}menu${NC}                    Menu interactif"
    echo ""
    echo -e "  ${AMBER}Exemples :${NC}"
    echo -e "  bash run.sh start"
    echo -e "  bash run.sh recon example.com"
    echo -e "  bash run.sh web http://192.168.1.10"
    echo -e "  bash run.sh network eth0 300"
    echo -e "  bash run.sh ad 192.168.1.10 corp.local admin P@ssw0rd"
    echo ""
}

# ── Start dashboard ────────────────────────────────────────
cmd_start(){
    log "Démarrage du dashboard..."
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE up -d web
    sleep 2
    if $COMPOSE ps web | grep -q "Up"; then
        log "Dashboard démarré → http://localhost:5000"
    else
        error "Échec du démarrage. Vérifiez les logs : bash run.sh logs"
    fi
}

# ── Stop ──────────────────────────────────────────────────
cmd_stop(){
    log "Arrêt de tous les services..."
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE down
    log "Services arrêtés."
}

# ── Status ────────────────────────────────────────────────
cmd_status(){
    cd "$INSTALL_DIR" || exit 1
    echo ""
    $COMPOSE ps
    echo ""
    info "Dashboard : http://localhost:5000"
    info "Résultats : $OUTPUT_DIR"
}

# ── Logs ─────────────────────────────────────────────────
cmd_logs(){
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE logs -f web
}

# ── Recon ─────────────────────────────────────────────────
cmd_recon(){
    local target="$1"
    [ -z "$target" ] && { error "Usage : bash run.sh recon <cible>"; exit 1; }
    log "Lancement de la reconnaissance sur : $target"
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE run --rm \
        -v "$OUTPUT_DIR:/output" \
        recon "$target"
}

# ── Web audit ─────────────────────────────────────────────
cmd_web(){
    local target="$1"
    [ -z "$target" ] && { error "Usage : bash run.sh web <url>"; exit 1; }
    log "Lancement de l'audit web sur : $target"
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE run --rm \
        -v "$OUTPUT_DIR:/output" \
        web_audit "$target"
}

# ── Network ───────────────────────────────────────────────
cmd_network(){
    local iface="${1:-eth0}"
    local duration="${2:-300}"
    log "Capture réseau sur $iface pendant ${duration}s..."
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE run --rm \
        --privileged \
        --network host \
        -v "$OUTPUT_DIR:/output" \
        network "$iface" "$duration"
}

# ── AD audit ──────────────────────────────────────────────
cmd_ad(){
    local dc="$1" domain="$2" user="$3" pass="$4"
    if [ -z "$dc" ] || [ -z "$domain" ] || [ -z "$user" ] || [ -z "$pass" ]; then
        error "Usage : bash run.sh ad <dc_ip> <domaine> <utilisateur> <mot_de_passe>"
        exit 1
    fi
    log "Audit Active Directory → $domain ($dc)"
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE run --rm \
        -v "$OUTPUT_DIR:/output" \
        ad_audit "$dc" "$domain" "$user" "$pass"
}

# ── Report ────────────────────────────────────────────────
cmd_report(){
    local target="$1"
    [ -z "$target" ] && { error "Usage : bash run.sh report <cible>"; exit 1; }
    local out="/output/report_${target}_$(date +%Y%m%d_%H%M%S).html"
    log "Génération du rapport consolidé pour : $target"
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE run --rm \
        -v "$OUTPUT_DIR:/output" \
        reporting --target "$target" --output "$out"
    log "Rapport disponible : $OUTPUT_DIR/$(basename $out)"
}

# ── Results ───────────────────────────────────────────────
cmd_results(){
    echo ""
    info "Résultats disponibles dans $OUTPUT_DIR :"
    echo ""
    for dir in recon web network ad; do
        count=$(find "$OUTPUT_DIR/$dir" -name "report.html" 2>/dev/null | wc -l)
        echo -e "  ${AMBER}$dir${NC} → $count rapport(s)"
        find "$OUTPUT_DIR/$dir" -name "report.html" 2>/dev/null | while read f; do
            echo -e "    ${GREEN}→${NC} $f"
        done
    done
    echo ""
    reports=$(find "$OUTPUT_DIR" -maxdepth 1 -name "report_*.html" 2>/dev/null | wc -l)
    echo -e "  ${AMBER}Rapports consolidés${NC} → $reports fichier(s)"
    find "$OUTPUT_DIR" -maxdepth 1 -name "report_*.html" 2>/dev/null | while read f; do
        echo -e "    ${GREEN}→${NC} $f"
    done
    echo ""
}

# ── Clean ─────────────────────────────────────────────────
cmd_clean(){
    warn "Cette action supprimera TOUS les résultats dans $OUTPUT_DIR"
    read -rp "Confirmer ? (oui/non) : " confirm
    if [ "$confirm" = "oui" ]; then
        rm -rf "${OUTPUT_DIR:?}"/*
        mkdir -p "$OUTPUT_DIR"/{recon,web,network,ad,reports}
        log "Résultats supprimés."
    else
        info "Annulé."
    fi
}

# ── Update ────────────────────────────────────────────────
cmd_update(){
    log "Reconstruction de toutes les images Docker..."
    cd "$INSTALL_DIR" || exit 1
    $COMPOSE build --no-cache
    log "Images reconstruites."
}

# ── Menu interactif ───────────────────────────────────────
cmd_menu(){
    while true; do
        clear
        banner
        echo -e "  ${AMBER}Que voulez-vous faire ?${NC}"
        echo ""
        echo "  1) Démarrer le dashboard web"
        echo "  2) Lancer une reconnaissance"
        echo "  3) Lancer un audit web"
        echo "  4) Lancer une capture réseau"
        echo "  5) Lancer un audit Active Directory"
        echo "  6) Générer un rapport consolidé"
        echo "  7) Voir les résultats"
        echo "  8) Statut des services"
        echo "  9) Arrêter les services"
        echo "  0) Quitter"
        echo ""
        read -rp "  Choix : " choice
        echo ""

        case $choice in
            1) cmd_start ;;
            2) read -rp "  Cible (IP ou domaine) : " t; cmd_recon "$t" ;;
            3) read -rp "  URL cible : " t; cmd_web "$t" ;;
            4)
                read -rp "  Interface (défaut: eth0) : " i
                read -rp "  Durée en secondes (défaut: 300) : " d
                cmd_network "${i:-eth0}" "${d:-300}"
                ;;
            5)
                read -rp "  IP du DC : " dc
                read -rp "  Domaine : " dom
                read -rp "  Utilisateur : " usr
                read -rsp "  Mot de passe : " pwd; echo ""
                cmd_ad "$dc" "$dom" "$usr" "$pwd"
                ;;
            6) read -rp "  Cible : " t; cmd_report "$t" ;;
            7) cmd_results ;;
            8) cmd_status ;;
            9) cmd_stop ;;
            0) log "Au revoir."; exit 0 ;;
            *) warn "Choix invalide." ;;
        esac

        echo ""
        read -rp "  Appuyez sur Entrée pour continuer..."
    done
}

# ── Router ────────────────────────────────────────────────
case "${1:-menu}" in
    start)   cmd_start ;;
    stop)    cmd_stop ;;
    status)  cmd_status ;;
    logs)    cmd_logs ;;
    recon)   cmd_recon "$2" ;;
    web)     cmd_web "$2" ;;
    network) cmd_network "$2" "$3" ;;
    ad)      cmd_ad "$2" "$3" "$4" "$5" ;;
    report)  cmd_report "$2" ;;
    results) cmd_results ;;
    clean)   cmd_clean ;;
    update)  cmd_update ;;
    menu)    cmd_menu ;;
    help|-h|--help) usage ;;
    *)
        error "Commande inconnue : $1"
        usage
        exit 1
        ;;
esac
