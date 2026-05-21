#!/usr/bin/env python3
"""
Script autonome pour exécuter les tests et sauvegarder les résultats.
Peut être appelé depuis une tâche planifiée (cron, Windows Task Scheduler, PythonAnywhere Scheduled Task).
"""
import sys
import os
import json
from datetime import datetime

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    from tester.runner import TestRunner
    from storage.storage import TestStorage

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Démarrage de l'exécution des tests...")

    try:
        # Créer le runner
        runner = TestRunner(api_url="https://api.agify.io", timeout=5.0)

        # Exécuter les tests
        print("[...] Exécution des tests en cours...")
        result = runner.run()

        # Sauvegarder le résultat
        db_path = os.path.join(os.path.dirname(__file__), "test_results.db")
        storage = TestStorage(db_path=db_path)
        run_id = storage.save_run(result)

        # Nettoyer les anciens résultats
        storage.clear_old_runs(keep_count=100)

        # Afficher le résumé
        print(f"\n✅ Tests exécutés avec succès (Run ID: {run_id})")
        print(f"   API: {result.get('api')}")
        print(f"   Status: {result.get('status')}")
        summary = result.get('summary', {})
        print(f"   Résultats: {summary.get('passed', 0)}/{summary.get('total_tests', 0)} PASS")
        print(f"   Taux de succès: {summary.get('success_rate', 0):.1f}%")
        print(f"   Latence moyenne: {summary.get('latency_ms', {}).get('avg', 0):.2f}ms")

        return 0

    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

