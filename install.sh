#!/bin/bash
# ============================================================
# install.sh — Installation automatique de Security Toolbox
# Usage : sudo bash install.sh
# ============================================================

GREEN='\033[0;32m'; AMBER='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${AMBER}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; exit 1; }
step()  { echo -e "\n${AMBER}==== $1 ====${NC}"; }

echo -e "${GREEN}"
echo "  ___                      _ _           _____           _ _"
echo " / __|___ __ _  _ _ _ ___ (_) |_ _  _   |_   _|__  ___| | |__ _____ __"
echo " \__ / -_) _| || | '_/ -_)| |  _| || |    | |/ _ \/ _ \ | '_ / _ \ \ /"
echo " |___\___\__|\_,_|_| \___|_|_|\__|\_, |    |_|\___/\___/_|_.__\___/_\_/"
echo "                                  |__/"
echo -e "${NC}"
echo "  Security Toolbox — Installer"
echo "  Usage autorisé uniquement"
echo ""

# ── Vérifications système ──────────────────────────────────
step "1/4 — Vérification des prérequis"

OS=$(uname -s)
[ "$OS" != "Linux" ] && error "Ce script nécessite Linux."

if [ "$EUID" -ne 0 ]; then
    warn "Ce script devrait être lancé en root (sudo bash install.sh)"
fi

log "Vérification de Docker..."
if ! command -v docker &>/dev/null; then
    warn "Docker non trouvé — installation en cours..."
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
    log "Docker installé"
else
    log "Docker $(docker --version | cut -d' ' -f3 | tr -d ',') — OK"
fi

log "Vérification de Docker Compose..."
if ! command -v docker-compose &>/dev/null && ! docker compose version &>/dev/null 2>&1; then
    warn "Docker Compose non trouvé — installation en cours..."
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    log "Docker Compose installé"
else
    log "Docker Compose — OK"
fi

log "Vérification de Git..."
if ! command -v git &>/dev/null; then
    warn "Git non trouvé — installation..."
    apt install -y git 2>/dev/null || yum install -y git 2>/dev/null
fi

# ── Structure des dossiers ─────────────────────────────────
step "2/4 — Création de la structure"

INSTALL_DIR="${INSTALL_DIR:-/opt/security-toolbox}"

mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/output"/{recon,web,network,ad,reports}

log "Dossier d'installation : $INSTALL_DIR"
log "Dossier de résultats   : $INSTALL_DIR/output"

# Droits sur le dossier output
chmod -R 777 "$INSTALL_DIR/output"

# ── Copie des fichiers ─────────────────────────────────────
step "3/4 — Copie des fichiers"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    log "Fichiers copiés vers $INSTALL_DIR"
else
    error "Lancez ce script depuis le dossier racine du projet (où se trouve docker-compose.yml)"
fi

# Rendre tous les scripts exécutables
find "$INSTALL_DIR/modules" -name "*.sh" -exec chmod +x {} \;
chmod +x "$INSTALL_DIR/run.sh" 2>/dev/null

# ── Build des images Docker ────────────────────────────────
step "4/4 — Build des images Docker"

cd "$INSTALL_DIR" || error "Impossible d'accéder à $INSTALL_DIR"

log "Build de l'image web (dashboard)..."
docker-compose build web
log "Build de l'image recon..."
docker-compose build recon
log "Build de l'image web_audit..."
docker-compose build web_audit
log "Build de l'image network..."
docker-compose build network
log "Build de l'image ad_audit..."
docker-compose build ad_audit
log "Build de l'image reporting..."
docker-compose build reporting

# ── Lien symbolique pour run.sh ────────────────────────────
ln -sf "$INSTALL_DIR/run.sh" /usr/local/bin/toolbox 2>/dev/null
chmod +x /usr/local/bin/toolbox 2>/dev/null

# ── Résumé final ───────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Installation terminée avec succès !      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Démarrer le dashboard : ${AMBER}toolbox start${NC}"
echo -e "  Ou directement        : ${AMBER}cd $INSTALL_DIR && bash run.sh start${NC}"
echo -e "  Dashboard web         : ${AMBER}http://localhost:5000${NC}"
echo ""
echo -e "  ${RED}⚠ Usage autorisé uniquement${NC}"
echo ""
