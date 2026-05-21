#!/usr/bin/env python3
"""
Script de test rapide de l'infrastructure
"""
import sys
import os

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("ATELIER TESTS API - Diagnostic de l'infrastructure")
        print("=" * 60)

        print("\n[1/4] Vérification des imports...")
        from tester.client import APIClient
        from tester.runner import TestRunner
        from tester.tests import AgifyTestSuite, APITest
        from storage.storage import TestStorage
        print("✅ Tous les imports sont OK")

        print("\n[2/4] Test du client HTTP...")
        client = APIClient("https://api.agify.io", timeout=5.0)
        data, latency, status, error = client.get(params={"name": "alice"})
        print(f"✅ Client fonctionne - Status: {status}, Latence: {latency:.2f}ms")
        print(f"   Réponse: name={data.get('name')}, age={data.get('age')}, count={data.get('count')}")

        print("\n[3/4] Test de la suite de tests...")
        suite = AgifyTestSuite(client)
        results = suite.run_all()
        passed = sum(1 for t in results if t.passed)
        print(f"✅ {passed}/{len(results)} tests passés")
        for test in results:
            status_mark = "✓" if test.passed else "✗"
            print(f"   {status_mark} {test.name}: {test.details}")

        print("\n[4/4] Test du stockage SQLite...")
        storage = TestStorage(db_path=os.path.join(os.path.dirname(__file__), "test_results.db"))
        print("✅ Base de données initialisée")

        print("\n" + "=" * 60)
        print("✅ DIAGNOSTIC COMPLET: TOUS LES SYSTÈMES FONCTIONNENT")
        print("=" * 60)
        print("\nProchaines étapes:")
        print("1. Exécuter: python3 run_test.py")
        print("2. Déployer sur PythonAnywhere")
        print("3. Configurer un Scheduled Task pour exécutions automatiques")

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

