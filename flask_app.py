from flask import Flask, render_template, jsonify, request
import os

try:
    from tester.runner import TestRunner
except Exception:
    TestRunner = None

try:
    from storage.storage import TestStorage
except Exception:
    TestStorage = None

app = Flask(__name__)

storage = TestStorage(db_path=os.path.join(os.path.dirname(__file__), "test_results.db")) if TestStorage else None

@app.get("/")
def index():
    """Page d'accueil avec les consignes de l'atelier."""
    return render_template('consignes.html')

@app.get("/dashboard")
def dashboard():
    """Page du dashboard de monitoring."""
    return render_template('dashboard.html')

@app.post("/run")
def run_tests():
    """
    Déclencher un run de tests immédiatement.
    Sauvegarde les résultats en base et retourne le JSON.
    """
    try:
        if not TestRunner or not storage:
            return jsonify({"error": "Dependencies not available"}), 500
        runner = TestRunner(api_url="https://api.agify.io", timeout=5.0)
        result = runner.run()

        # Sauvegarder le run
        run_id = storage.save_run(result)
        result["run_id"] = run_id

        # Nettoyer les anciens runs (garder les 100 derniers)
        storage.clear_old_runs(keep_count=100)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/latest")
def api_latest():
    """
    Récupérer le dernier run de tests.
    """
    latest = storage.get_latest_run() if storage else None
    return (jsonify(latest), 200) if latest else (jsonify({"error": "No test run found"}), 404)

@app.get("/api/runs")
def api_runs():
    """
    Récupérer les N derniers runs (pour l'historique).
    """
    limit = request.args.get('limit', 10, type=int)
    runs = storage.get_runs(limit=limit) if storage else []
    return jsonify(runs), 200

@app.get("/api/stats")
def api_stats():
    """
    Récupérer les statistiques globales.
    """
    stats = storage.get_statistics() if storage else {}
    return jsonify(stats), 200

@app.get("/health")
def health():
    """
    Endpoint de santé pour vérifier que l'API répond.
    """
    latest = storage.get_latest_run() if storage else None
    if latest:
        status = latest.get("status", "UNKNOWN")
        return jsonify({
            "status": "OK" if status == "OK" else "DEGRADED",
            "api": "Agify",
            "last_run": latest.get("timestamp"),
            "success_rate": latest.get("summary", {}).get("success_rate", 0)
        }), 200
    return jsonify({"status": "NO_DATA", "message": "No test run available", "api": "Agify"}), 200

if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
