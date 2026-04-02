#!/usr/bin/env python3
"""
ad_report.py — Rapport HTML du module Active Directory
"""
import sys, os, glob
from datetime import datetime

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read().strip()
    except:
        return None

def file_section(title, path, icon="📄"):
    content = read_file(path)
    if not content:
        return f"<div class='section'><h2>{icon} {title}</h2><p class='empty'>Aucune donnée.</p></div>"
    escaped = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<div class='section'><h2>{icon} {title}</h2><pre>{escaped}</pre></div>"

def generate(output_dir, domain, dc_ip):
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")

    # Comptage des fichiers LDAP générés
    ldap_files = glob.glob(os.path.join(output_dir, "ldap", "*.json"))
    ldap_count = len(ldap_files)
    bh_files   = glob.glob(os.path.join(output_dir, "bloodhound", "*.zip"))

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"/>
<title>Rapport AD — {domain}</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:-apple-system,sans-serif; background:#f5f5f5; color:#1a1a1a; line-height:1.6; }}
header {{ background:#533ab7; color:white; padding:2rem; }}
header h1 {{ font-size:1.5rem; font-weight:500; }}
header p {{ opacity:0.8; font-size:0.9rem; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px;
          padding:1.5rem 2rem; background:white; border-bottom:1px solid #e0e0e0; }}
.stat {{ background:#f9f9f9; border-radius:8px; padding:1rem; text-align:center; }}
.stat-value {{ font-size:1.6rem; font-weight:500; color:#533ab7; word-break:break-all; }}
.stat-label {{ font-size:0.8rem; color:#666; }}
.content {{ max-width:1100px; margin:2rem auto; padding:0 1.5rem; }}
.section {{ background:white; border-radius:10px; border:1px solid #e0e0e0;
            padding:1.5rem; margin-bottom:1.5rem; overflow:hidden; }}
.section h2 {{ font-size:1rem; font-weight:500; margin-bottom:1rem;
               padding-bottom:8px; border-bottom:1px solid #eee; }}
pre {{ background:#1a1a1a; color:#d4d4d4; padding:1rem; border-radius:6px;
       font-size:0.78rem; overflow-x:auto; max-height:400px; overflow-y:auto;
       white-space:pre-wrap; }}
.info-box {{ background:#f0eeff; border-left:3px solid #533ab7; padding:1rem;
             border-radius:0 8px 8px 0; font-size:0.9rem; margin-bottom:1rem; }}
.empty {{ color:#999; font-style:italic; font-size:0.9rem; }}
footer {{ text-align:center; padding:2rem; color:#999; font-size:0.8rem; }}
</style></head><body>
<header>
  <h1>Rapport Audit Active Directory</h1>
  <p>Domaine : <strong>{domain}</strong> &nbsp;|&nbsp; DC : {dc_ip} &nbsp;|&nbsp; {now}</p>
</header>
<div class="stats">
  <div class="stat"><div class="stat-value">{domain}</div><div class="stat-label">Domaine</div></div>
  <div class="stat"><div class="stat-value">{dc_ip}</div><div class="stat-label">DC ciblé</div></div>
  <div class="stat"><div class="stat-value">{ldap_count}</div><div class="stat-label">Fichiers LDAP</div></div>
  <div class="stat"><div class="stat-value">{"✓" if bh_files else "✗"}</div><div class="stat-label">BloodHound</div></div>
</div>
<div class="content">
  {"<div class='section'><h2>🩸 BloodHound</h2><div class='info-box'>Fichier ZIP généré dans <code>bloodhound/</code>.<br/>Importe-le dans l'interface BloodHound Neo4j pour visualiser les chemins d'attaque.</div></div>" if bh_files else ""}
  {file_section("Énumération (enum4linux-ng)", os.path.join(output_dir,"enum4linux.txt"), "🔍")}
</div>
<footer>Security Toolbox — usage autorisé uniquement</footer>
</body></html>"""

    out = os.path.join(output_dir, "report.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"[+] Rapport → {out}")

if __name__ == "__main__":
    generate(sys.argv[1], sys.argv[2], sys.argv[3])
