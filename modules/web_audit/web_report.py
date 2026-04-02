#!/usr/bin/env python3
"""
web_report.py — Rapport HTML du module Audit Web
"""
import sys, os, json
from datetime import datetime

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read().strip()
    except:
        return None

def parse_ffuf(path):
    try:
        with open(path) as f:
            data = json.load(f)
        results = data.get("results", [])
        if not results:
            return "<p class='empty'>Aucun résultat FFUF.</p>"
        rows = "".join(
            f"<tr><td>{r['url']}</td><td>{r['status']}</td><td>{r['length']}</td></tr>"
            for r in results
        )
        return f"""<table><thead><tr><th>URL</th><th>Status</th><th>Taille</th></tr></thead>
        <tbody>{rows}</tbody></table>"""
    except:
        return "<p class='empty'>Fichier FFUF non disponible.</p>"

def file_section(title, path, icon="📄"):
    content = read_file(path)
    if not content:
        return f"<div class='section'><h2>{icon} {title}</h2><p class='empty'>Aucun résultat.</p></div>"
    escaped = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<div class='section'><h2>{icon} {title}</h2><pre>{escaped}</pre></div>"

def generate(output_dir, target):
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")
    nikto = read_file(os.path.join(output_dir, "nikto.txt")) or ""
    vuln_count = nikto.count("+ ")
    gobuster = read_file(os.path.join(output_dir, "gobuster.txt")) or ""
    dir_count = len([l for l in gobuster.splitlines() if l.startswith("/")])

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"/>
<title>Rapport Audit Web — {target}</title>
<style>
* {{ box-sizing: border-box; margin:0; padding:0; }}
body {{ font-family: -apple-system,sans-serif; background:#f5f5f5; color:#1a1a1a; line-height:1.6; }}
header {{ background:#185fa5; color:white; padding:2rem; }}
header h1 {{ font-size:1.5rem; font-weight:500; }}
header p {{ opacity:0.8; font-size:0.9rem; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px;
          padding:1.5rem 2rem; background:white; border-bottom:1px solid #e0e0e0; }}
.stat {{ background:#f9f9f9; border-radius:8px; padding:1rem; text-align:center; }}
.stat-value {{ font-size:2rem; font-weight:500; color:#185fa5; }}
.stat-label {{ font-size:0.8rem; color:#666; }}
.content {{ max-width:1100px; margin:2rem auto; padding:0 1.5rem; }}
.section {{ background:white; border-radius:10px; border:1px solid #e0e0e0;
            padding:1.5rem; margin-bottom:1.5rem; overflow:hidden; }}
.section h2 {{ font-size:1rem; font-weight:500; margin-bottom:1rem;
               padding-bottom:8px; border-bottom:1px solid #eee; }}
pre {{ background:#1a1a1a; color:#d4d4d4; padding:1rem; border-radius:6px;
       font-size:0.78rem; overflow-x:auto; max-height:400px; overflow-y:auto;
       white-space:pre-wrap; }}
table {{ width:100%; border-collapse:collapse; font-size:0.85rem; }}
th,td {{ padding:8px 12px; text-align:left; border-bottom:1px solid #eee; }}
th {{ background:#f0f4ff; font-weight:500; }}
.empty {{ color:#999; font-style:italic; font-size:0.9rem; }}
footer {{ text-align:center; padding:2rem; color:#999; font-size:0.8rem; }}
</style></head><body>
<header>
  <h1>Rapport Audit Web</h1>
  <p>Cible : <strong>{target}</strong> &nbsp;|&nbsp; {now}</p>
</header>
<div class="stats">
  <div class="stat"><div class="stat-value">{vuln_count}</div><div class="stat-label">Alertes Nikto</div></div>
  <div class="stat"><div class="stat-value">{dir_count}</div><div class="stat-label">Répertoires trouvés</div></div>
  <div class="stat"><div class="stat-value">{target}</div><div class="stat-label">Cible</div></div>
  <div class="stat"><div class="stat-value">{now.split()[0]}</div><div class="stat-label">Date</div></div>
</div>
<div class="content">
  {file_section("Nikto — Vulnérabilités web", os.path.join(output_dir,"nikto.txt"), "⚠️")}
  {file_section("Gobuster — Répertoires", os.path.join(output_dir,"gobuster.txt"), "📂")}
  <div class="section"><h2>🔀 FFUF — Fuzzing</h2>{parse_ffuf(os.path.join(output_dir,"ffuf.json"))}</div>
</div>
<footer>Security Toolbox — usage autorisé uniquement</footer>
</body></html>"""

    out = os.path.join(output_dir, "report.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"[+] Rapport → {out}")

if __name__ == "__main__":
    generate(sys.argv[1], sys.argv[2])
