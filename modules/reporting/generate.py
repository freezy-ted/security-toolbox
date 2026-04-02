#!/usr/bin/env python3
"""
generate.py — Rapport consolidé HTML + export PDF automatique
Usage : python3 generate.py --target <cible> --output <fichier.html> [--pdf]
"""

import os, sys, glob, argparse
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

def find_latest(base, pattern):
    dirs = sorted(glob.glob(os.path.join(base, pattern)), reverse=True)
    return dirs[0] if dirs else None

def pre(content):
    if not content:
        return "<p class='empty'>Aucune donnée disponible.</p>"
    escaped = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<pre>{escaped}</pre>"

def section(title, content, icon=""):
    return f"<div class='section'><h2>{icon} {title}</h2>{content}</div>"

def generate_html(target, output_path):
    now  = datetime.now().strftime("%d/%m/%Y à %H:%M")
    base = "/output"

    recon_dir   = find_latest(os.path.join(base,"recon"),   f"{target}_*") or find_latest(os.path.join(base,"recon"),   "*")
    web_dir     = find_latest(os.path.join(base,"web"),     f"{target}_*") or find_latest(os.path.join(base,"web"),     "*")
    network_dir = find_latest(os.path.join(base,"network"), "capture_*")
    ad_dir      = find_latest(os.path.join(base,"ad"),      f"{target}_*") or find_latest(os.path.join(base,"ad"),      "*")

    open_ports = 0; subdomains = 0; hosts = 0; web_vulns = 0; ad_users = 0

    if recon_dir:
        nmap = read_file(os.path.join(recon_dir, "nmap_fast.nmap")) or ""
        open_ports = nmap.count("/open/")
        subdomains = count_lines(os.path.join(recon_dir, "subdomains.txt"))
    if network_dir:
        hosts = count_lines(os.path.join(network_dir, "hosts.txt"))
    if web_dir:
        nikto = read_file(os.path.join(web_dir, "nikto.txt")) or ""
        web_vulns = nikto.count("+ ")
    if ad_dir:
        enum = read_file(os.path.join(ad_dir, "enum4linux.txt")) or ""
        ad_users = enum.count("user:")

    risk_score = 0
    if open_ports > 10: risk_score += 2
    if web_vulns > 5:   risk_score += 3
    if web_vulns > 0:   risk_score += 1
    risk_label = "Faible" if risk_score <= 1 else "Moyen" if risk_score <= 3 else "Eleve"
    risk_color = "#3b6d11" if risk_score <= 1 else "#854f0b" if risk_score <= 3 else "#a32d2d"

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"/>
<title>Rapport Consolide - {target}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,sans-serif;background:#f5f5f5;color:#1a1a1a;line-height:1.6}}
header{{background:#0f6e56;color:white;padding:2.5rem 2rem}}
header h1{{font-size:1.8rem;font-weight:500;margin-bottom:6px}}
header p{{opacity:.85;font-size:.9rem}}
.header-meta{{display:flex;gap:1rem;margin-top:12px;flex-wrap:wrap}}
.header-badge{{font-size:11px;padding:4px 12px;border-radius:99px;background:rgba(255,255,255,.2)}}
.risk-badge{{font-size:13px;padding:5px 16px;border-radius:99px;background:white;font-weight:500;color:{risk_color}}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;padding:1.5rem 2rem;background:white;border-bottom:1px solid #e0e0e0}}
.stat{{background:#f9f9f9;border-radius:10px;padding:1rem;text-align:center}}
.stat-value{{font-size:2rem;font-weight:500;color:#0f6e56}}
.stat-label{{font-size:.78rem;color:#666;margin-top:3px}}
.content{{max-width:1200px;margin:2rem auto;padding:0 1.5rem}}
.toc{{background:white;border-radius:10px;border:1px solid #e0e0e0;padding:1.25rem;margin-bottom:2rem}}
.toc h2{{font-size:.9rem;font-weight:500;margin-bottom:10px}}
.toc ul{{list-style:none;display:flex;flex-wrap:wrap;gap:8px}}
.toc a{{text-decoration:none;color:#185fa5;font-size:.82rem;padding:4px 12px;background:#e6f1fb;border-radius:99px}}
.module-title{{display:flex;align-items:center;gap:12px;margin:2rem 0 .75rem}}
.module-title h2{{font-size:1.05rem;font-weight:500}}
.mod-ok{{font-size:11px;padding:3px 10px;border-radius:99px;background:#e1f5ee;color:#0f6e56}}
.mod-off{{font-size:11px;padding:3px 10px;border-radius:99px;background:#f5f5f5;color:#999}}
.section{{background:white;border-radius:10px;border:1px solid #e0e0e0;padding:1.5rem;margin-bottom:.75rem;overflow:hidden}}
.section h2{{font-size:.9rem;font-weight:500;margin-bottom:.9rem;padding-bottom:8px;border-bottom:1px solid #eee}}
pre{{background:#1a1a1a;color:#d4d4d4;padding:1rem;border-radius:6px;font-size:.75rem;line-height:1.6;overflow-x:auto;max-height:320px;overflow-y:auto;white-space:pre-wrap}}
.empty{{color:#999;font-style:italic;font-size:.88rem}}
.summary-table{{width:100%;border-collapse:collapse;font-size:.88rem}}
.summary-table th{{background:#f0f4f0;padding:9px 12px;text-align:left;font-weight:500}}
.summary-table td{{padding:9px 12px;border-bottom:1px solid #eee}}
.risk-high{{color:#a32d2d;font-weight:500}}
.risk-med{{color:#854f0b;font-weight:500}}
footer{{text-align:center;padding:3rem 2rem;color:#999;font-size:.78rem;border-top:1px solid #e0e0e0;margin-top:2rem}}
@media print{{.toc{{display:none}}pre{{max-height:none;overflow:visible;font-size:8px}}.section{{page-break-inside:avoid}}}}
</style></head><body>
<header>
  <h1>Rapport de Securite Consolide</h1>
  <p>Cible : <strong>{target}</strong> &nbsp;·&nbsp; {now}</p>
  <div class="header-meta">
    <span class="header-badge">Security Toolbox v1.0</span>
    <span class="header-badge">Usage autorise uniquement</span>
    <span class="risk-badge">Risque : {risk_label}</span>
  </div>
</header>
<div class="stats">
  <div class="stat"><div class="stat-value">{open_ports}</div><div class="stat-label">Ports ouverts</div></div>
  <div class="stat"><div class="stat-value">{subdomains}</div><div class="stat-label">Sous-domaines</div></div>
  <div class="stat"><div class="stat-value">{hosts}</div><div class="stat-label">Hotes reseau</div></div>
  <div class="stat"><div class="stat-value">{web_vulns}</div><div class="stat-label">Alertes web</div></div>
  <div class="stat"><div class="stat-value">{ad_users}</div><div class="stat-label">Utilisateurs AD</div></div>
  <div class="stat"><div class="stat-value" style="color:{risk_color}">{risk_label}</div><div class="stat-label">Niveau risque</div></div>
</div>
<div class="content">
  <div class="toc"><h2>Sommaire</h2><ul>
    <li><a href="#summary">Resume executif</a></li>
    <li><a href="#recon">Reconnaissance</a></li>
    <li><a href="#web">Audit Web</a></li>
    <li><a href="#network">Reseau</a></li>
    <li><a href="#ad">Active Directory</a></li>
    <li><a href="#conclusion">Conclusion</a></li>
  </ul></div>

  <div id="summary" class="module-title"><h2>Resume executif</h2></div>
  <div class="section"><h2>Vue d'ensemble</h2>
    <table class="summary-table"><thead><tr><th>Module</th><th>Statut</th><th>Resultats cles</th></tr></thead><tbody>
      <tr><td>Reconnaissance</td><td>{"Executed" if recon_dir else "Non execute"}</td><td>{open_ports} ports · {subdomains} sous-domaines</td></tr>
      <tr><td>Audit Web</td><td>{"Execute" if web_dir else "Non execute"}</td><td class="{"risk-high" if web_vulns>5 else "risk-med" if web_vulns>0 else ""}">{web_vulns} alerte(s)</td></tr>
      <tr><td>Reseau passif</td><td>{"Execute" if network_dir else "Non execute"}</td><td>{hosts} hotes actifs</td></tr>
      <tr><td>Active Directory</td><td>{"Execute" if ad_dir else "Non execute"}</td><td>{ad_users} utilisateur(s)</td></tr>
    </tbody></table>
  </div>

  <div id="recon" class="module-title"><h2>Reconnaissance</h2><span class="{"mod-ok" if recon_dir else "mod-off"}">{"Donnees disponibles" if recon_dir else "Non execute"}</span></div>
  {(section("Whois", pre(read_file(os.path.join(recon_dir,"whois.txt")))) + section("Sous-domaines", pre(read_file(os.path.join(recon_dir,"subdomains.txt")))) + section("Nmap", pre(read_file(os.path.join(recon_dir,"nmap_fast.nmap"))))) if recon_dir else ""}

  <div id="web" class="module-title"><h2>Audit Web</h2><span class="{"mod-ok" if web_dir else "mod-off"}">{"Donnees disponibles" if web_dir else "Non execute"}</span></div>
  {(section("Nikto", pre(read_file(os.path.join(web_dir,"nikto.txt")))) + section("Gobuster", pre(read_file(os.path.join(web_dir,"gobuster.txt"))))) if web_dir else ""}

  <div id="network" class="module-title"><h2>Analyse Reseau</h2><span class="{"mod-ok" if network_dir else "mod-off"}">{"Donnees disponibles" if network_dir else "Non execute"}</span></div>
  {(section("Hotes actifs", pre(read_file(os.path.join(network_dir,"hosts.txt")))) + section("DNS", pre(read_file(os.path.join(network_dir,"dns_queries.txt"))))) if network_dir else ""}

  <div id="ad" class="module-title"><h2>Active Directory</h2><span class="{"mod-ok" if ad_dir else "mod-off"}">{"Donnees disponibles" if ad_dir else "Non execute"}</span></div>
  {section("Enumeration", pre(read_file(os.path.join(ad_dir,"enum4linux.txt")))) if ad_dir else ""}

  <div id="conclusion" class="module-title"><h2>Conclusion</h2></div>
  <div class="section"><h2>Recommandations</h2>
    <ul style="padding-left:1.5rem;line-height:2.2;font-size:.9rem">
      {"<li class='risk-high'>Reduire la surface d'exposition : <strong>" + str(open_ports) + " ports ouverts</strong></li>" if open_ports > 5 else ""}
      {"<li class='risk-high'>Corriger les <strong>" + str(web_vulns) + " vulnerabilites web</strong> (Nikto)</li>" if web_vulns > 0 else ""}
      {"<li>Verifier les <strong>" + str(subdomains) + " sous-domaines</strong> exposes</li>" if subdomains > 0 else ""}
      {"<li>Analyser les <strong>" + str(hosts) + " hotes reseau</strong> actifs</li>" if hosts > 0 else ""}
      <li>Completer par une revue manuelle approfondie</li>
      <li>Mettre a jour les systemes et services exposes</li>
    </ul>
    <br/><p style="font-size:.82rem;color:#666">Rapport genere le {now} par Security Toolbox.<br/>Ce rapport automatique doit etre complete par une analyse experte.</p>
  </div>
</div>
<footer>Security Toolbox v1.0 — Usage reserve aux audits contractuellement autorises</footer>
</body></html>"""

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
    print(f"[+] Rapport HTML → {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--pdf", action="store_true", help="Exporter aussi en PDF")
    args = parser.parse_args()

    html_path = generate_html(args.target, args.output)

    if args.pdf:
        try:
            from weasyprint import HTML, CSS
            pdf_path = html_path.replace(".html", ".pdf")
            print_css = CSS(string="@page{size:A4;margin:1.5cm} pre{font-size:8px;max-height:none} .section{page-break-inside:avoid}")
            HTML(filename=html_path).write_pdf(pdf_path, stylesheets=[print_css])
            print(f"[+] PDF → {pdf_path}")
        except ImportError:
            print("[!] weasyprint non installe : pip install weasyprint")
        except Exception as e:
            print(f"[!] Export PDF echoue : {e}")
