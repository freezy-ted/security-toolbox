#!/usr/bin/env python3
"""
app.py — Dashboard Flask de la Security Toolbox
Accès : http://localhost:5000
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess, os, glob, threading, json
from datetime import datetime

app = Flask(__name__)
OUTPUT_BASE = "/output"
MODULES_BASE = "/toolbox/modules"

# ── Lancement d'un module en arrière-plan ──────────────────
running_jobs = {}

def run_job(job_id, cmd, cwd=None):
    running_jobs[job_id] = {"status": "running", "output": [], "started": datetime.now().isoformat()}
    try:
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, cwd=cwd
        )
        for line in proc.stdout:
            running_jobs[job_id]["output"].append(line.strip())
        proc.wait()
        running_jobs[job_id]["status"] = "done" if proc.returncode == 0 else "error"
        running_jobs[job_id]["returncode"] = proc.returncode
    except Exception as e:
        running_jobs[job_id]["status"] = "error"
        running_jobs[job_id]["output"].append(str(e))

# ── Routes ─────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/run/recon", methods=["POST"])
def run_recon():
    target = request.json.get("target", "").strip()
    if not target:
        return jsonify({"error": "Cible manquante"}), 400
    job_id = f"recon_{datetime.now().strftime('%H%M%S')}"
    cmd = f"bash /toolbox/modules/recon/recon.sh {target}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

@app.route("/api/run/web", methods=["POST"])
def run_web():
    target = request.json.get("target", "").strip()
    if not target:
        return jsonify({"error": "Cible manquante"}), 400
    job_id = f"web_{datetime.now().strftime('%H%M%S')}"
    cmd = f"bash /toolbox/modules/web_audit/web_audit.sh {target}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

@app.route("/api/run/network", methods=["POST"])
def run_network():
    iface    = request.json.get("interface", "eth0")
    duration = request.json.get("duration", 300)
    job_id = f"network_{datetime.now().strftime('%H%M%S')}"
    cmd = f"bash /toolbox/modules/network/network.sh {iface} {duration}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

@app.route("/api/run/ad", methods=["POST"])
def run_ad():
    data = request.json
    dc   = data.get("dc_ip","").strip()
    dom  = data.get("domain","").strip()
    user = data.get("user","").strip()
    pwd  = data.get("password","").strip()
    if not all([dc, dom, user, pwd]):
        return jsonify({"error": "Paramètres AD incomplets"}), 400
    job_id = f"ad_{datetime.now().strftime('%H%M%S')}"
    cmd = f"bash /toolbox/modules/ad_audit/ad_audit.sh {dc} {dom} {user} {pwd}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id})

@app.route("/api/run/report", methods=["POST"])
def run_report():
    target = request.json.get("target","").strip()
    if not target:
        return jsonify({"error": "Cible manquante"}), 400
    out = f"/output/report_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    job_id = f"report_{datetime.now().strftime('%H%M%S')}"
    cmd = f"python3 /toolbox/modules/reporting/generate.py --target {target} --output {out}"
    threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
    return jsonify({"job_id": job_id, "output_file": out})

@app.route("/api/job/<job_id>")
def job_status(job_id):
    job = running_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job inconnu"}), 404
    return jsonify(job)

@app.route("/api/reports")
def list_reports():
    reports = []
    for f in sorted(glob.glob(f"{OUTPUT_BASE}/**/*.html", recursive=True), reverse=True)[:20]:
        reports.append({"path": f, "name": os.path.basename(f),
                         "size": os.path.getsize(f),
                         "date": datetime.fromtimestamp(os.path.getmtime(f)).strftime("%d/%m/%Y %H:%M")})
    return jsonify(reports)

@app.route("/reports/<path:filename>")
def serve_report(filename):
    return send_from_directory(OUTPUT_BASE, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
