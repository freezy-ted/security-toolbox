#!/usr/bin/env python3
"""
recon_report.py — Génère un rapport HTML à partir des résultats de recon.sh
Usage : python3 recon_report.py <output_dir> <target>
"""

import sys
import os
import glob
from datetime import datetime

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def file_section(title, path, icon="📄"):
    content = read_file(path)
    if not content:
        return f"""
        <div class="section">
            <h2>{icon} {title}</h2>
            <p class="empty">Aucun résultat trouvé ou outil non disponible.</p>
        </div>"""
    escaped = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"""
    <div class="section">
        <h2>{icon} {title}</h2>
        <pre>{escaped}</pre>
    </div>"""

def count_lines(path):
    content = read_file(path)
    if not content:
        return 0
    return len([l for l in content.splitlines() if l.strip()])

def generate(output_dir, target):
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")

    # Stats
    subdomains = count_lines(os.path.join(output_dir, "subdomains.txt"))
    nmap_fast  = read_file(os.path.join(output_dir, "nmap_fast.nmap"))
    open_ports = 0
    if nmap_fast:
        open_ports = nmap_fast.count("/open/")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Rapport Recon — {target}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #f5f5f5; color: #1a1a1a; line-height: 1.6; }}
  header {{ background: #0f6e56; color: white; padding: 2rem; }}
  header h1 {{ font-size: 1.5rem; font-weight: 500; margin-bottom: 4px; }}
  header p  {{ opacity: 0.8; font-size: 0.9rem; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px; padding: 1.5rem 2rem; background: white;
            border-bottom: 1px solid #e0e0e0; }}
  .stat {{ background: #f9f9f9; border-radius: 8px; padding: 1rem; text-align: center; }}
  .stat-value {{ font-size: 2rem; font-weight: 500; color: #0f6e56; }}
  .stat-label {{ font-size: 0.8rem; color: #666; margin-top: 2px; }}
  .content {{ max-width: 1100px; margin: 2rem auto; padding: 0 1.5rem; }}
  .section {{ background: white; border-radius: 10px; border: 1px solid #e0e0e0;
              padding: 1.5rem; margin-bottom: 1.5rem; overflow: hidden; }}
  .section h2 {{ font-size: 1rem; font-weight: 500; margin-bottom: 1rem;
                 padding-bottom: 8px; border-bottom: 1px solid #eee; }}
  pre {{ background: #1a1a1a; color: #d4d4d4; padding: 1rem; border-radius: 6px;
         font-size: 0.78rem; overflow-x: auto; line-height: 1.6;
         max-height: 400px; overflow-y: auto; white-space: pre-wrap; }}
  .empty {{ color: #999; font-size: 0.9rem; font-style: italic; }}
  footer {{ text-align: center; padding: 2rem; color: #999; font-size: 0.8rem; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 99px;
            font-size: 0.75rem; background: #e1f5ee; color: #0f6e56; margin-left: 8px; }}
</style>
</head>
<body>
<header>
  <h1>Rapport de Reconnaissance</h1>
  <p>Cible : <strong>{target}</strong> &nbsp;|&nbsp; Généré le {now}</p>
  <p style="margin-top:8px;font-size:0.8rem;opacity:0.6;">
    Usage autorisé uniquement — Security Toolbox
  </p>
</header>

<div class="stats">
  <div class="stat">
    <div class="stat-value">{open_ports}</div>
    <div class="stat-label">Ports ouverts</div>
  </div>
  <div class="stat">
    <div class="stat-value">{subdomains}</div>
    <div class="stat-label">Sous-domaines</div>
  </div>
  <div class="stat">
    <div class="stat-value">{now.split(" ")[0]}</div>
    <div class="stat-label">Date du scan</div>
  </div>
  <div class="stat">
    <div class="stat-value">{target}</div>
    <div class="stat-label">Cible</div>
  </div>
</div>

<div class="content">
  {file_section("Whois", os.path.join(output_dir, "whois.txt"), "🔎")}
  {file_section("Sous-domaines (subfinder)", os.path.join(output_dir, "subdomains.txt"), "🌐")}
  {file_section("DNS — Enregistrements standard", os.path.join(output_dir, "dns_std.txt"), "📡")}
  {file_section("DNS — Tentative de transfert de zone", os.path.join(output_dir, "dns_axfr.txt"), "⚠️")}
  {file_section("Nmap — Scan rapide", os.path.join(output_dir, "nmap_fast.nmap"), "🔍")}
  {file_section("Nmap — Scan complet", os.path.join(output_dir, "nmap_full.nmap"), "🔍")}
  {file_section("Shodan", os.path.join(output_dir, "shodan.txt"), "🛰️")}
</div>

<footer>Security Toolbox — rapport généré automatiquement — usage autorisé uniquement</footer>
</body>
</html>"""

    out_path = os.path.join(output_dir, "report.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"[+] Rapport généré → {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage : python3 recon_report.py <output_dir> <target>")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
