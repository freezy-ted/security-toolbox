#!/usr/bin/env python3
# ============================================================
# app.py — Dashboard Flask de la Security Toolbox
# Avec authentification basique
# Usage autorisé uniquement
# ============================================================

# ── Imports ──────────────────────────────────────────────────
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
import subprocess, os, glob, threading, hashlib
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "changez_cette_cle_secrete"
OUTPUT_BASE = "/output"
COMPOSE_FILE = "/opt/security-toolbox/docker-compose.yml"
running_jobs = {}

# ── Comptes utilisateurs ──────────────────────────────────────
# admin    : accès complet
# tech1-4  : accès complet aux modules
USERS = {
    "admin":  hashlib.sha256("Admin2026!".encode()).hexdigest(),
    "Tech1":  hashlib.sha256("Tech1@2026".encode()).hexdigest(),
    "Tech2":  hashlib.sha256("Tech2@2026".encode()).hexdigest(),
    "Tech3":  hashlib.sha256("Tech3@2026".encode()).hexdigest(),
    "Tech4":  hashlib.sha256("Tech4@2026".encode()).hexdigest(),
}

# ── Vérification de session ───────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── Page de login ─────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if username in USERS and USERS[username] == hashed:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("index"))
        error = "Identifiants incorrects"
    return render_template("login.html", error=error)

# ── Déconnexion ───────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── Page principale ───────────────────────────────────────────
@app.route("/")
@login_required
def index():
    return render_template("dashboard_charts.html")

# ── Module Reconnaissance ─────────────────────────────────────
@app.route("/api/run/recon", methods=["POST"])
@login_required
def run_recon():
    target = request.json.get("target","").strip()
    if not target: return jsonify({"error": "Cible manquante"}), 400
    job_id = f"recon_{datetime.now().strftime('%H%M%S')}"
    cmd = f"docker compose -f {COMPOSE_FILE} run --remove-orphans recon {target}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

# ── Module Audit Web ──────────────────────────────────────────
@app.route("/api/run/web", methods=["POST"])
@login_required
def run_web():
    target = request.json.get("target","").strip()
    if not target: return jsonify({"error": "Cible manquante"}), 400
    job_id = f"web_{datetime.now().strftime('%H%M%S')}"
    cmd = f"docker compose -f {COMPOSE_FILE} run --remove-orphans web_audit {target}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

# ── Module Vulnérabilités ─────────────────────────────────────
@app.route("/api/run/vuln", methods=["POST"])
@login_required
def run_vuln():
    target = request.json.get("target","").strip()
    if not target: return jsonify({"error": "Cible manquante"}), 400
    job_id = f"vuln_{datetime.now().strftime('%H%M%S')}"
    cmd = f"docker compose -f {COMPOSE_FILE} run --remove-orphans vuln {target}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

# ── Module OSINT ──────────────────────────────────────────────
@app.route("/api/run/osint", methods=["POST"])
@login_required
def run_osint():
    target = request.json.get("target","").strip()
    type_ = request.json.get("type","domain")
    if not target: return jsonify({"error": "Cible manquante"}), 400
    job_id = f"osint_{datetime.now().strftime('%H%M%S')}"
    cmd = f"docker compose -f {COMPOSE_FILE} run --remove-orphans osint {target} {type_}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

# ── Module Réseau passif ──────────────────────────────────────
@app.route("/api/run/network", methods=["POST"])
@login_required
def run_network():
    iface = request.json.get("interface","eth0")
    duration = request.json.get("duration", 300)
    job_id = f"network_{datetime.now().strftime('%H%M%S')}"
    cmd = f"docker compose -f {COMPOSE_FILE} run --remove-orphans network {iface} {duration}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

# ── Module Active Directory ───────────────────────────────────
@app.route("/api/run/ad", methods=["POST"])
@login_required
def run_ad():
    data = request.json
    dc   = data.get("dc_ip","").strip()
    dom  = data.get("domain","").strip()
    user = data.get("user","").strip()
    pwd  = data.get("password","").strip()
    if not all([dc, dom, user, pwd]):
        return jsonify({"error": "Paramètres incomplets"}), 400
    job_id = f"ad_{datetime.now().strftime('%H%M%S')}"
    cmd = f"docker compose -f {COMPOSE_FILE} run --remove-orphans ad_audit {dc} {dom} {user} {pwd}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

# ── Module Rapport consolidé ──────────────────────────────────
@app.route("/api/run/report", methods=["POST"])
@login_required
def run_report():
    target = request.json.get("target","").strip()
    if not target: return jsonify({"error": "Cible manquante"}), 400
    out = f"/output/reports/report_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    job_id = f"report_{datetime.now().strftime('%H%M%S')}"
    cmd = f"docker compose -f {COMPOSE_FILE} run --remove-orphans reporting --target {target} --output {out}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id, "output_file": out})

# ── Lancement d'un job en arrière-plan ────────────────────────
def run_job(job_id, cmd):
    running_jobs[job_id] = {
        "status": "running",
        "output": [],
        "started": datetime.now().isoformat()
    }
    try:
        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in proc.stdout:
            running_jobs[job_id]["output"].append(line.strip())
        proc.wait()
        running_jobs[job_id]["status"] = "done" if proc.returncode == 0 else "error"
    except Exception as e:
        running_jobs[job_id]["status"] = "error"
        running_jobs[job_id]["output"].append(str(e))

# ── Statut d'un job en cours ──────────────────────────────────
@app.route("/api/job/<job_id>")
@login_required
def job_status(job_id):
    job = running_jobs.get(job_id)
    if not job: return jsonify({"error": "Job inconnu"}), 404
    return jsonify(job)

# ── Liste des rapports disponibles ───────────────────────────
@app.route("/api/reports")
@login_required
def list_reports():
    reports = []
    for f in sorted(glob.glob(f"{OUTPUT_BASE}/**/*.html", recursive=True), reverse=True)[:20]:
        reports.append({
            "path": f,
            "name": os.path.basename(f),
            "size": os.path.getsize(f),
            "date": datetime.fromtimestamp(os.path.getmtime(f)).strftime("%d/%m/%Y %H:%M")
        })
    return jsonify(reports)

# ── Accès aux rapports HTML ───────────────────────────────────
@app.route("/reports/<path:filename>")
@login_required
def serve_report(filename):
    return send_from_directory(OUTPUT_BASE, filename)

# ── Démarrage du serveur ──────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
