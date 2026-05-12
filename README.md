# Security Toolbox 🔒

Plateforme d'audit de sécurité modulaire conteneurisée avec Docker, pilotable via une interface web.

> ⚠️ **Usage autorisé uniquement** — Réservé aux audits contractuels sur des systèmes
> pour lesquels vous avez une autorisation écrite explicite.

---

## 📋 Description

Security Toolbox regroupe 6 modules d'audit couvrant les phases d'un pentest standard :
- Reconnaissance passive et active
- Audit web
- Analyse réseau passive
- Audit Active Directory
- Scan de vulnérabilités
- OSINT avancé

Le tout pilotable depuis un dashboard web avec authentification, graphiques en temps réel et génération automatique de rapports HTML/PDF.

---

## 🚀 Installation rapide

```bash
git clone https://github.com/freezy-ted/security-toolbox.git
cd security-toolbox
sudo bash install.sh
```

---

## ▶️ Lancement

```bash
cd /opt/security-toolbox
sudo docker compose up -d web
```

Dashboard disponible sur **http://localhost:5000**

---

## 🔐 Identifiants

| Utilisateur | Mot de passe | Rôle |
|-------------|-------------|------|
| admin | Admin2026! | Admin — gestion des comptes |
| tech1 | Tech1@2026 | Tech — lancement des scans |
| tech2 | Tech2@2026 | Tech |
| tech3 | Tech3@2026 | Tech |
| tech4 | Tech4@2026 | Tech |

---

## 🛠️ Modules disponibles

| Module | Outils | Commande terminal |
|--------|--------|----------|
| Reconnaissance | nmap, whois, subfinder, theHarvester, dnsrecon, shodan | `sudo docker compose run recon <cible>` |
| Audit Web | nikto, gobuster, ffuf | `sudo docker compose run web_audit <url>` |
| Réseau passif | tcpdump, tshark | `sudo docker compose run network eth0 300` |
| Active Directory | ldapdomaindump, bloodhound, enum4linux-ng | `sudo docker compose run ad_audit <dc> <dom> <user> <pass>` |
| Vulnérabilités | nuclei, nmap NSE | `sudo docker compose run vuln <cible>` |
| OSINT | subfinder, amass, theHarvester, shodan | `sudo docker compose run osint <cible> domain` |
| Reporting | python3, weasyprint | `sudo docker compose run reporting --target <cible> --output /output/reports/rapport.html` |

---

## 📁 Structure du projet
security-toolbox/
├── install.sh                   ← Installation automatique
├── run.sh                       ← Menu interactif
├── docker-compose.yml           ← Orchestration Docker
├── rgpd_purge.sh                ← Purge RGPD interactive
├── DOCUMENTATION.md             ← Documentation technique
├── web/                         ← Dashboard Flask (port 5000)
│   ├── Dockerfile
│   ├── app.py                   ← API Flask + authentification
│   ├── static/
│   │   └── chart.umd.js        ← Chart.js local (201Ko)
│   └── templates/
│       ├── dashboard_charts.html ← Interface principale
│       ├── login.html           ← Page de connexion
│       └── admin.html           ← Page d'administration
└── modules/
├── recon/                   ← Reconnaissance
├── web_audit/               ← Audit Web
├── network/                 ← Réseau passif
├── ad_audit/                ← Active Directory
├── vuln/                    ← Vulnérabilités
├── osint/                   ← OSINT avancé
└── reporting/               ← Rapport consolidé
---

## 🗂️ Résultats des scans
/opt/security-toolbox/output/
├── recon/
│   └── example.com_20260101_120000/
│       ├── whois.txt
│       ├── subdomains.txt
│       ├── nmap_fast.nmap
│       ├── nmap_full.nmap
│       └── report.html
├── web/
├── network/
├── ad/
├── vuln/
├── osint/
└── reports/                     ← Rapports consolidés
---

## 🐳 Images Docker
security-toolbox-web
security-toolbox-recon
security-toolbox-web_audit
security-toolbox-network
security-toolbox-ad_audit
security-toolbox-vuln
security-toolbox-osint
security-toolbox-reporting
---

## ⚙️ Configuration

Créer un fichier `.env` pour les clés API :
SHODAN_API_KEY=votre_cle_api
---

## 🧹 Purge RGPD

```bash
# Menu interactif
sudo bash /opt/security-toolbox/rgpd_purge.sh

# Purge directe
sudo bash /opt/security-toolbox/rgpd_purge.sh all
sudo bash /opt/security-toolbox/rgpd_purge.sh module recon
sudo bash /opt/security-toolbox/rgpd_purge.sh days 30
```

---

## 📝 Disclaimer

Ce projet est fourni à des fins éducatives et de recherche en sécurité uniquement.
L'utilisation de ces outils sur des systèmes sans autorisation explicite est illégale.
Les auteurs déclinent toute responsabilité en cas d'utilisation illicite.
