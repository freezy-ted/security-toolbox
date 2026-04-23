#!/bin/bash
# ============================================================
# rgpd_purge.sh — Suppression des rapports et données
# Conformité RGPD — usage autorisé uniquement
# ============================================================

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${AMBER}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }
step()  { echo -e "\n${AMBER}==== $1 ====${NC}"; }

OUTPUT_DIR="/opt/security-toolbox/output"
LOG_FILE="/opt/security-toolbox/rgpd_purge.log"

# ── Journalisation de la suppression ─────────────────────────
log_action(){
    echo "[$(date '+%d/%m/%Y %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ── Affiche les stats avant suppression ──────────────────────
show_stats(){
    echo ""
    echo -e "${AMBER}Données présentes dans /output :${NC}"
    echo ""
    for dir in recon web network ad vuln osint reports; do
        count=$(find "$OUTPUT_DIR/$dir" -type f 2>/dev/null | wc -l)
        size=$(du -sh "$OUTPUT_DIR/$dir" 2>/dev/null | cut -f1)
        echo -e "  ${GREEN}$dir${NC} → $count fichier(s) — $size"
    done
    echo ""
    total=$(du -sh "$OUTPUT_DIR" 2>/dev/null | cut -f1)
    echo -e "  Total : ${RED}$total${NC}"
    echo ""
}

# ── Suppression d'un module spécifique ───────────────────────
purge_module(){
    local module="$1"
    local path="$OUTPUT_DIR/$module"
    if [ -d "$path" ]; then
        local count=$(find "$path" -type f | wc -l)
        rm -rf "${path:?}"/*
        mkdir -p "$path"
        log_action "Suppression module $module — $count fichier(s)"
        log "Module $module purgé — $count fichier(s) supprimés"
    else
        warn "Module $module introuvable"
    fi
}

# ── Suppression par ancienneté ────────────────────────────────
purge_older_than(){
    local days="$1"
    local count=$(find "$OUTPUT_DIR" -type f -mtime +"$days" | wc -l)
    find "$OUTPUT_DIR" -type f -mtime +"$days" -delete
    log_action "Suppression fichiers > $days jours — $count fichier(s)"
    log "$count fichier(s) de plus de $days jours supprimés"
}

# ── Suppression complète ──────────────────────────────────────
purge_all(){
    local total=$(find "$OUTPUT_DIR" -type f | wc -l)
    for dir in recon web network ad vuln osint reports; do
        rm -rf "${OUTPUT_DIR:?}/$dir"/*
        mkdir -p "$OUTPUT_DIR/$dir"
    done
    log_action "PURGE TOTALE — $total fichier(s) supprimés"
    log "Purge totale effectuée — $total fichier(s) supprimés"
}

# ── Menu principal ────────────────────────────────────────────
show_menu(){
    clear
    echo -e "${GREEN}"
    echo "  ╔══════════════════════════════════════════╗"
    echo "  ║     Security Toolbox — Purge RGPD        ║"
    echo "  ║     Suppression des données personnelles  ║"
    echo "  ╚══════════════════════════════════════════╝"
    echo -e "${NC}"

    show_stats

    echo -e "  ${AMBER}Options disponibles :${NC}"
    echo ""
    echo "  1) Purger un module spécifique"
    echo "  2) Purger les fichiers de plus de 30 jours"
    echo "  3) Purger les fichiers de plus de 7 jours"
    echo "  4) Purge totale (tous les rapports)"
    echo "  5) Voir le journal de purge"
    echo "  0) Quitter"
    echo ""
    read -rp "  Choix : " choice

    case $choice in
        1)
            echo ""
            echo -e "  Modules disponibles : ${AMBER}recon web network ad vuln osint reports${NC}"
            read -rp "  Module à purger : " mod
            warn "Vous allez supprimer tous les rapports du module : $mod"
            read -rp "  Confirmer ? (oui/non) : " confirm
            [ "$confirm" = "oui" ] && purge_module "$mod" || log "Annulé"
            ;;
        2)
            warn "Suppression des fichiers de plus de 30 jours"
            read -rp "  Confirmer ? (oui/non) : " confirm
            [ "$confirm" = "oui" ] && purge_older_than 30 || log "Annulé"
            ;;
        3)
            warn "Suppression des fichiers de plus de 7 jours"
            read -rp "  Confirmer ? (oui/non) : " confirm
            [ "$confirm" = "oui" ] && purge_older_than 7 || log "Annulé"
            ;;
        4)
            error "ATTENTION — Cette action supprimera TOUS les rapports !"
            read -rp "  Tapez CONFIRMER pour valider : " confirm
            [ "$confirm" = "CONFIRMER" ] && purge_all || log "Annulé"
            ;;
        5)
            echo ""
            if [ -f "$LOG_FILE" ]; then
                cat "$LOG_FILE"
            else
                warn "Aucun journal de purge disponible"
            fi
            ;;
        0)
            log "Au revoir"
            exit 0
            ;;
        *)
            warn "Choix invalide"
            ;;
    esac

    echo ""
    read -rp "  Appuyez sur Entrée pour continuer..."
    show_menu
}

# ── Lancement ─────────────────────────────────────────────────
case "${1:-menu}" in
    menu)    show_menu ;;
    all)     purge_all ;;
    module)  purge_module "$2" ;;
    days)    purge_older_than "$2" ;;
    *)       show_menu ;;
esac
