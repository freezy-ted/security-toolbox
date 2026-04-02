#!/usr/bin/env python3
"""
vuln_report.py — Rapport HTML du module scan de vulnérabilités
"""
import sys, os, re
from datetime import datetime

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read().strip()
    except:
        return None

def count_lines(path):
    c = read_file(path)
    return len([l for l in c.splitlines() if l.strip()]) if c else 0

def parse_nuclei(path):
    """Parse les résultats Nuclei et les classe par sévérité"""
    content = read_file(path)
    if not content:
        return [], {}

    findings = []
    severity_count = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        # Format Nuclei : [timestamp] [template-id] [severity] url
        sev = "info"
        if "[critical]" in line.lower(): sev = "critical"
        elif "[high]"     in line.lower(): sev = "high"
        elif "[medium]"   in line.lower(): sev = "medium"
        elif "[low]"      in line.lower(): sev = "low"

        severity_count[sev] = severity_count.get(sev, 0) + 1
        findings.append({"line": line, "severity": sev})

    return findings, severity_count

def severity_badge(sev):
    colors = {
        "critical": ("#a32d2d", "#fcebeb"),
        "high":     ("#854f0b", "#faeeda"),
        "medium":   ("#533ab7", "#eeedfe"),
        "low":      ("#185fa5", "#e6f1fb"),
        "info":     ("#3b6d11", "#eaf3de"),
    }
    fg, bg = colors.get(sev, ("#666", "#f5f5f5"))
    return f'<span style="font-size:10px;padding:2px 8px;border-radius:99px;background:{bg};color:{fg};font-weight:500">{sev.upper()}</span>'

def findings_table(findings):
    if not findings:
        return "<p class='empty'>Aucune vulnérabilité trouvée.</p>"
    rows = ""
    for f in findings:
        escaped = f["line"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        rows += f"<tr><td>{severity_badge(f['severity'])}</td><td style='font-family:monospace;font-size:12px'>{escaped}</td></tr>"
    return f"""<table><thead><tr><th style='width:90px'>Sévérité</th><th>Détail</th></tr></thead>
    <tbody>{rows}</tbody></table>"""

def file_section(title, path, icon="📄"):
    content = read_file(path)
    if not content:
        return f"<div class='section'><h2>{icon} {title}</h2><p class='empty'>Aucun résultat.</p></div>"
    escaped = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<div class='section'><h2>{icon} {title}</h2><pre>{escaped}</pre></div>"

def generate(output_dir, target):
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")

    # Parse tous les fichiers Nuclei
    all_findings = []
    total_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    for fname in ["nuclei_cves.txt", "nuclei_misconfig.txt", "nuclei_exposures.txt", "nuclei_tech.txt"]:
        f, s = parse_nuclei(os.path.join(output_dir, fname))
        all_findings.extend(f)
        for k in total_severity:
            total_severity[k] += s.get(k, 0)

    total_vulns = sum(total_severity.values())

    # Niveau de risque
    if total_severity["critical"] > 0:
        risk_label, risk_color = "Critique", "#a32d2d"
    elif total_severity["high"] > 0:
        risk_label, risk_color = "Élevé", "#854f0b"
    elif total_severity["medium"] > 0:
        risk_label, risk_color = "Moyen", "#533ab7"
    else:
        risk_label, risk_color = "Faible", "#3b6d11"

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"/>
<title>Rapport Vulnérabilités — {target}</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:-apple-system,sans-serif; background:#f5f5f5; color:#1a1a1a; line-height:1.6; }}
header {{ background:#533ab7; color:white; padding:2rem; }}
header h1 {{ font-size:1.5rem; font-weight:500; margin-bottom:4px; }}
header p {{ opacity:.85; font-size:.9rem; }}
.risk-badge {{ display:inline-block; margin-top:10px; font-size:13px; padding:5px 16px;
               border-radius:99px; background:white; font-weight:500; color:{risk_color}; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(110px,1fr));
          gap:10px; padding:1.5rem 2rem; background:white; border-bottom:1px solid #e0e0e0; }}
.stat {{ background:#f9f9f9; border-radius:8px; padding:.9rem; text-align:center; }}
.stat-value {{ font-size:1.8rem; font-weight:500; }}
.stat-label {{ font-size:.75rem; color:#666; margin-top:2px; }}
.stat.critical .stat-value {{ color:#a32d2d; }}
.stat.high     .stat-value {{ color:#854f0b; }}
.stat.medium   .stat-value {{ color:#533ab7; }}
.stat.low      .stat-value {{ color:#185fa5; }}
.stat.info     .stat-value {{ color:#3b6d11; }}
.stat.total    .stat-value {{ color:#1a1a1a; }}
.content {{ max-width:1200px; margin:2rem auto; padding:0 1.5rem; }}
.section {{ background:white; border-radius:10px; border:1px solid #e0e0e0;
            padding:1.5rem; margin-bottom:1rem; overflow:hidden; }}
.section h2 {{ font-size:.95rem; font-weight:500; margin-bottom:1rem;
               padding-bottom:8px; border-bottom:1px solid #eee; }}
pre {{ background:#1a1a1a; color:#d4d4d4; padding:1rem; border-radius:6px;
       font-size:.75rem; line-height:1.6; overflow-x:auto;
       max-height:350px; overflow-y:auto; white-space:pre-wrap; }}
table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
th,td {{ padding:9px 12px; text-align:left; border-bottom:1px solid #eee; }}
th {{ background:#f5f0ff; font-weight:500; }}
.empty {{ color:#999; font-style:italic; font-size:.88rem; }}
footer {{ text-align:center; padding:2rem; color:#999; font-size:.78rem;
          border-top:1px solid #e0e0e0; margin-top:2rem; }}
</style></head><body>
<header>
  <h1>Rapport Scan de Vulnérabilités</h1>
  <p>Cible : <strong>{target}</strong> &nbsp;·&nbsp; {now}</p>
  <span class="risk-badge">Risque global : {risk_label}</span>
</header>

<div class="stats">
  <div class="stat total"><div class="stat-value">{total_vulns}</div><div class="stat-label">Total</div></div>
  <div class="stat critical"><div class="stat-value">{total_severity["critical"]}</div><div class="stat-label">Critique</div></div>
  <div class="stat high"><div class="stat-value">{total_severity["high"]}</div><div class="stat-label">Élevé</div></div>
  <div class="stat medium"><div class="stat-value">{total_severity["medium"]}</div><div class="stat-label">Moyen</div></div>
  <div class="stat low"><div class="stat-value">{total_severity["low"]}</div><div class="stat-label">Faible</div></div>
  <div class="stat info"><div class="stat-value">{total_severity["info"]}</div><div class="stat-label">Info</div></div>
</div>

<div class="content">
  <div class="section">
    <h2>⚠️ Résultats Nuclei — Toutes catégories</h2>
    {findings_table(all_findings)}
  </div>
  {file_section("Nmap — Scripts de vulnérabilités", os.path.join(output_dir,"nmap_vuln.txt"), "🔍")}
  {file_section("Nmap — Scripts safe", os.path.join(output_dir,"nmap_safe.txt"), "🔒")}
</div>
<footer>Security Toolbox — usage autorisé uniquement</footer>
</body></html>"""

    out = os.path.join(output_dir, "report.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"[+] Rapport → {out}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage : python3 vuln_report.py <output_dir> <target>")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
