from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.get("/")
def index():
    return send_from_directory(PROJECT_ROOT, "index.html")


@app.get("/<path:filename>")
def frontend_file(filename: str):
    return send_from_directory(PROJECT_ROOT, filename)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "sudarshan-flask-demo"})


@app.post("/api/evidence")
def create_evidence():
    uploaded_file = request.files.get("file")
    case_id = request.form.get("caseId", "").strip()
    domain = request.form.get("domain", "Other").strip() or "Other"

    if not case_id:
        return jsonify({"error": "caseId is required"}), 400
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "A PDF file is required"}), 400
    if Path(uploaded_file.filename).suffix.lower() != ".pdf":
        return jsonify({"error": "Only PDF files are accepted"}), 415

    data = uploaded_file.read()
    if not data:
        return jsonify({"error": "The uploaded file is empty"}), 400

    return jsonify({
        "caseId": case_id,
        "domain": domain,
        "file": uploaded_file.filename,
        "hash": sha256(data).hexdigest(),
        "status": "Verified & Sealed",
        "timestamp": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
    }), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, load_dotenv=False)
