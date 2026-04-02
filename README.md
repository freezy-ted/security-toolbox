# Security Toolbox

Toolbox d'audit de sécurité modulaire avec interface web.

> ⚠️ **Usage autorisé uniquement** — Réservé aux audits contractuels sur des systèmes
> pour lesquels vous avez une autorisation écrite explicite.

---

## Structure du projet

```
toolbox/
├── docker-compose.yml
├── web/                        # Dashboard Flask (port 5000)
│   ├── Dockerfile
│   ├── app.py
│   └── templates/index.html
├── modules/
│   ├── recon/                  # Reconnaissance
│   │   ├── Dockerfile
│   │   ├── recon.sh
│   │   └── recon_report.py
│   ├── web_audit/              # Audit Web
│   │   ├── web_audit.sh
│   │   └── web_report.py
│   ├── network/                # Réseau passif
│   │   ├── network.sh
│   │   └── network_report.py
│   ├── ad_audit/               # Active Directory
│   │   ├── ad_audit.sh
│   │   └── ad_report.py
│   └── reporting/              # Rapport consolidé
│       └── generate.py
└── output/                     # Résultats (créé automatiquement)
```

---

## Démarrage rapide

### 1. Prérequis
- Docker + Docker Compose installés
- Linux recommandé (Kali, Ubuntu, Debian)

### 2. Build et lancement du dashboard

```bash
git clone <ton-repo> toolbox
cd toolbox
docker-compose up --build web
```

Accède ensuite à : **http://localhost:5000**

---

## Utilisation des modules

### Via l'interface web (recommandé)
Ouvre http://localhost:5000, entre ta cible et clique sur le module.

### Via Docker directement

#### Reconnaissance
```bash
docker-compose run recon example.com
# ou avec une IP :
docker-compose run recon 192.168.1.1
```

#### Audit Web
```bash
docker-compose run web_audit http://example.com
```

#### Réseau passif
```bash
# Capture sur eth0 pendant 5 minutes (300s)
docker-compose run --privileged network eth0 300
```

#### Active Directory
```bash
docker-compose run ad_audit 192.168.1.10 corp.local jdupont MonMotDePasse
```

#### Rapport consolidé
```bash
docker-compose run reporting --target example.com --output /output/rapport_final.html
```

---

## Outils inclus par module

| Module | Outils |
|--------|--------|
| Reconnaissance | nmap, whois, dnsrecon, theHarvester, subfinder, shodan |
| Audit Web | nikto, gobuster, ffuf |
| Réseau | tcpdump, tshark |
| Active Directory | ldapdomaindump, bloodhound-python, enum4linux-ng |
| Reporting | Python (génération HTML/PDF) |

---

## Variables d'environnement optionnelles

```bash
# Shodan (module recon)
export SHODAN_API_KEY=ton_api_key
```

---

## Résultats

Tous les résultats sont dans le dossier `output/` :
```
output/
├── recon/
│   └── example.com_20240101_120000/
│       ├── whois.txt
│       ├── subdomains.txt
│       ├── nmap_fast.nmap
│       └── report.html          ← rapport du module
├── web/
├── network/
├── ad/
└── rapport_final.html            ← rapport consolidé
```

---

## Disclaimer

Ce projet est fourni à des fins éducatives uniquement.
L'utilisation sur des systèmes sans autorisation explicite est illégale.
