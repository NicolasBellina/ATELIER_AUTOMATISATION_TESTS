"""
Runner de tests : orchestration, calcul de métriques et logging.
"""
from datetime import datetime, timezone
from typing import Dict, Any
import statistics
from .client import APIClient
from .tests import AgifyTestSuite


class TestRunner:
    """Orchestrateur de tests avec calcul de métriques."""

    def __init__(self, api_url: str = "https://api.agify.io", timeout: float = 5.0):
        """
        Initialiser le runner.

        Args:
            api_url: URL de base de l'API
            timeout: Délai d'attente en secondes
        """
        self.api_url = api_url
        self.timeout = timeout
        self.client = APIClient(api_url, timeout=timeout)

    @staticmethod
    def _p95(values):
        if not values:
            return 0
        ordered = sorted(values)
        index = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * 0.95))))
        return ordered[index]

    def run(self) -> Dict[str, Any]:
        """
        Exécuter la suite de tests et calculer les métriques.

        Returns:
            Dict contenant les résultats et métriques
        """
        # Timestamp ISO 8601 avec fuseau horaire
        timestamp = datetime.now(timezone.utc).isoformat()

        # Exécuter les tests
        test_suite = AgifyTestSuite(self.client)
        test_suite.run_all()
        tests_results = test_suite.get_results()

        # Calculer les métriques
        passed_count = sum(1 for test in tests_results if test["passed"])
        failed_count = len(tests_results) - passed_count
        latencies = [test["latency_ms"] for test in tests_results]

        # Compiler le résultat
        result = {
            "api": "Agify",
            "timestamp": timestamp,
            "url": self.api_url,
            "summary": {
                "total_tests": len(tests_results),
                "passed": passed_count,
                "failed": failed_count,
                "success_rate": round((passed_count / len(tests_results) * 100) if tests_results else 0, 2),
                "error_rate": round((failed_count / len(tests_results) * 100) if tests_results else 0, 2),
                "latency_ms": {
                    "avg": round(statistics.mean(latencies), 2) if latencies else 0,
                    "min": round(min(latencies), 2) if latencies else 0,
                    "max": round(max(latencies), 2) if latencies else 0,
                    "p95": round(self._p95(latencies), 2),
                },
            },
            "tests": tests_results,
            "status": "OK" if failed_count == 0 else "PARTIAL_FAILURE" if failed_count < len(tests_results) else "FAILURE",
        }

        self.client.close()
        return result

    def run_multiple_iterations(self, iterations: int = 3) -> Dict[str, Any]:
        """
        Exécuter plusieurs itérations de tests pour une meilleure statistique.

        Args:
            iterations: Nombre d'itérations

        Returns:
            Dict contenant l'agrégation des résultats
        """
        all_results = []
        all_latencies = []
        total_passed = 0
        total_failed = 0

        for _ in range(iterations):
            runner = TestRunner(self.api_url, self.timeout)
            result = runner.run()
            all_results.append(result)
            total_passed += result["summary"]["passed"]
            total_failed += result["summary"]["failed"]
            all_latencies.extend([test["latency_ms"] for test in result["tests"]])

        total = total_passed + total_failed
        return {
            "api": "Agify",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "iterations": iterations,
            "summary": {
                "total_tests": total,
                "passed": total_passed,
                "failed": total_failed,
                "success_rate": round((total_passed / total * 100) if total else 0, 2),
                "error_rate": round((total_failed / total * 100) if total else 0, 2),
                "latency_ms": {
                    "avg": round(statistics.mean(all_latencies), 2) if all_latencies else 0,
                    "min": round(min(all_latencies), 2) if all_latencies else 0,
                    "max": round(max(all_latencies), 2) if all_latencies else 0,
                    "p95": round(self._p95(all_latencies), 2),
                },
            },
            "runs": all_results,
            "status": "OK" if total_failed == 0 else "PARTIAL_FAILURE" if total_failed < total else "FAILURE",
        }

