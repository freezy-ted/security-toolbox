#!/usr/bin/env python3
"""
osint_report.py — Rapport HTML du module OSINT avancé
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

def extract_emails(text):
    if not text:
        return []
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return list(set(re.findall(pattern, text)))

def extract_ips(text):
    if not text:
        return []
    pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return list(set(re.findall(pattern, text)))

def file_section(title, path, icon="📄"):
    content = read_file(path)
    if not content:
        return f"<div class='section'><h2>{icon} {title}</h2><p class='empty'>Aucune donnée.</p></div>"
    escaped = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<div class='section'><h2>{icon} {title}</h2><pre>{escaped}</pre></div>"

def list_section(title, items, icon="📋", color="#185fa5"):
    if not items:
        return f"<div class='section'><h2>{icon} {title}</h2><p class='empty'>Aucun résultat.</p></div>"
    rows = "".join(
        f'<div class="list-item"><span style="color:{color}">→</span> {item}</div>'
        for item in items[:100]
    )
    more = f'<p class="empty" style="margin-top:8px">...et {len(items)-100} autres</p>' if len(items) > 100 else ""
    return f"<div class='section'><h2>{icon} {title} <span class='count'>({len(items)})</span></h2>{rows}{more}</div>"

def generate(output_dir, target, target_type):
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")

    # Collecte des données
    subdomains_all  = read_file(os.path.join(output_dir, "subdomains_all.txt")) or ""
    subdomains      = [s for s in subdomains_all.splitlines() if s.strip()]

    whois_txt = read_file(os.path.join(output_dir, "whois.txt")) or ""
    harvester_google = read_file(os.path.join(output_dir, "harvester_google.xml")) or \
                       read_file(os.path.join(output_dir, "harvester_google.html")) or ""
    shodan_host = read_file(os.path.join(output_dir, "shodan_host.txt")) or ""
    shodan_org  = read_file(os.path.join(output_dir, "shodan_org.txt")) or ""

    # Extraction automatique
    all_text = " ".join([whois_txt, harvester_google, shodan_host])
    emails   = extract_emails(all_text)
    ips      = extract_ips(shodan_org or whois_txt)

    sub_count   = len(subdomains)
    email_count = len(emails)
    ip_count    = len(ips)

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Rapport OSINT — {target}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f5f5f5;color:#1a1a1a;line-height:1.6}}
header{{background:#185fa5;color:white;padding:2rem 2rem}}
header h1{{font-size:1.5rem;font-weight:500;margin-bottom:4px}}
header p{{opacity:.85;font-size:.9rem}}
.header-meta{{display:flex;gap:1rem;margin-top:10px;flex-wrap:wrap}}
.hbadge{{font-size:11px;padding:4px 12px;border-radius:99px;background:rgba(255,255,255,.2)}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;padding:1.5rem 2rem;background:white;border-bottom:1px solid #e0e0e0}}
.stat{{background:#f9f9f9;border-radius:8px;padding:1rem;text-align:center}}
.stat-value{{font-size:2rem;font-weight:500;color:#185fa5}}
.stat-label{{font-size:.78rem;color:#666;margin-top:2px}}
.content{{max-width:1200px;margin:2rem auto;padding:0 1.5rem}}
.toc{{background:white;border-radius:10px;border:1px solid #e0e0e0;padding:1.25rem;margin-bottom:2rem}}
.toc h2{{font-size:.9rem;font-weight:500;margin-bottom:10px}}
.toc ul{{list-style:none;display:flex;flex-wrap:wrap;gap:8px}}
.toc a{{text-decoration:none;color:#185fa5;font-size:.82rem;padding:4px 12px;background:#e6f1fb;border-radius:99px}}
.section{{background:white;border-radius:10px;border:1px solid #e0e0e0;padding:1.5rem;margin-bottom:1rem;overflow:hidden}}
.section h2{{font-size:.95rem;font-weight:500;margin-bottom:1rem;padding-bottom:8px;border-bottom:1px solid #eee;display:flex;align-items:center;gap:8px}}
.count{{font-size:.8rem;color:#185fa5;background:#e6f1fb;padding:2px 8px;border-radius:99px;font-weight:400}}
pre{{background:#1a1a1a;color:#d4d4d4;padding:1rem;border-radius:6px;font-size:.75rem;line-height:1.6;overflow-x:auto;max-height:320px;overflow-y:auto;white-space:pre-wrap}}
.list-item{{padding:5px 0;border-bottom:1px solid #f0f0f0;font-size:.85rem;display:flex;align-items:center;gap:8px}}
.list-item:last-child{{border-bottom:none}}
.empty{{color:#999;font-style:italic;font-size:.88rem}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem}}
footer{{text-align:center;padding:2rem;color:#999;font-size:.78rem;border-top:1px solid #e0e0e0;margin-top:2rem}}
@media(max-width:600px){{.grid-2{{grid-template-columns:1fr}}}}
</style></head><body>

<header>
  <h1>Rapport OSINT</h1>
  <p>Cible : <strong>{target}</strong> &nbsp;·&nbsp; Type : {target_type} &nbsp;·&nbsp; {now}</p>
  <div class="header-meta">
    <span class="hbadge">Security Toolbox v1.0</span>
    <span class="hbadge">Sources publiques uniquement</span>
    <span class="hbadge">Usage autorisé uniquement</span>
  </div>
</header>

<div class="stats">
  <div class="stat"><div class="stat-value">{sub_count}</div><div class="stat-label">Sous-domaines</div></div>
  <div class="stat"><div class="stat-value">{email_count}</div><div class="stat-label">Emails trouvés</div></div>
  <div class="stat"><div class="stat-value">{ip_count}</div><div class="stat-label">IPs détectées</div></div>
  <div class="stat"><div class="stat-value">{now.split()[0]}</div><div class="stat-label">Date</div></div>
</div>

<div class="content">

  <div class="toc"><h2>Sommaire</h2><ul>
    <li><a href="#whois">Whois</a></li>
    <li><a href="#dns">DNS</a></li>
    <li><a href="#subdomains">Sous-domaines</a></li>
    <li><a href="#emails">Emails</a></li>
    <li><a href="#ips">IPs</a></li>
    <li><a href="#shodan">Shodan</a></li>
    <li><a href="#harvester">theHarvester</a></li>
  </ul></div>

  <div class="grid-2">
    <div id="whois">{file_section("Whois", os.path.join(output_dir,"whois.txt"), "🔎")}</div>
    <div id="dns">{file_section("Enregistrements DNS", os.path.join(output_dir,"dns_records.txt"), "📡")}</div>
  </div>

  <div id="subdomains">{list_section("Sous-domaines découverts", subdomains, "🌐", "#185fa5")}</div>
  <div id="emails">{list_section("Emails trouvés", emails, "✉️", "#0f6e56")}</div>
  <div id="ips">{list_section("Adresses IP détectées", ips, "🖥️", "#533ab7")}</div>

  <div id="shodan">
    <div class="grid-2">
      {file_section("Shodan — Host", os.path.join(output_dir,"shodan_host.txt"), "🛰️")}
      {file_section("Shodan — Organisation", os.path.join(output_dir,"shodan_org.txt"), "🏢")}
    </div>
  </div>

  <div id="harvester">
    {file_section("theHarvester — Google", os.path.join(output_dir,"harvester_google.html"), "🔍")}
    {file_section("theHarvester — LinkedIn", os.path.join(output_dir,"harvester_linkedin.html"), "💼")}
  </div>

  {file_section("Recon-ng", os.path.join(output_dir,"recon_ng.txt"), "⚙️")}
  {file_section("Transfert de zone DNS", os.path.join(output_dir,"zone_transfer.txt"), "⚠️")}

</div>
<footer>Security Toolbox — OSINT basé sur sources publiques uniquement — usage autorisé</footer>
</body></html>"""

    out = os.path.join(output_dir, "report.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"[+] Rapport OSINT → {out}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage : python3 osint_report.py <output_dir> <target> [type]")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "domain")
