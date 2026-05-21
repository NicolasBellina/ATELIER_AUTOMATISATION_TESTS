"""
Module de stockage : persistance des résultats de tests dans SQLite.
"""
import sqlite3
import json
from typing import List, Dict, Any


class TestStorage:
    """Gestionnaire SQLite pour l'historique des tests."""

    def __init__(self, db_path: str = "test_results.db"):
        """
        Initialiser la base de données.

        Args:
            db_path: Chemin vers la base de données SQLite
        """
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Créer les tables si elles n'existent pas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table des runs (exécutions de tests)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api_name TEXT NOT NULL,
                total_tests INTEGER,
                passed_count INTEGER,
                failed_count INTEGER,
                success_rate REAL,
                error_rate REAL,
                latency_avg_ms REAL,
                latency_min_ms REAL,
                latency_max_ms REAL,
                latency_p95_ms REAL,
                status TEXT,
                full_result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des tests individuels
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                test_name TEXT NOT NULL,
                passed BOOLEAN,
                details TEXT,
                latency_ms REAL,
                FOREIGN KEY (run_id) REFERENCES test_runs(id)
            )
        """)

        conn.commit()
        conn.close()

    def save_run(self, result: Dict[str, Any]) -> int:
        """
        Sauvegarder un run de tests complet.

        Args:
            result: Dict contenant le résultat du run (sortie de TestRunner.run())

        Returns:
            ID du run inséré
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        summary = result.get("summary", {})
        latency = summary.get("latency_ms", {})

        # Insérer le run principal
        cursor.execute("""
            INSERT INTO test_runs (
                timestamp, api_name, total_tests, passed_count, failed_count,
                success_rate, error_rate, latency_avg_ms, latency_min_ms,
                latency_max_ms, latency_p95_ms, status, full_result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.get("timestamp"),
            result.get("api", "Unknown"),
            summary.get("total_tests", 0),
            summary.get("passed", 0),
            summary.get("failed", 0),
            summary.get("success_rate", 0),
            summary.get("error_rate", 0),
            latency.get("avg", 0),
            latency.get("min", 0),
            latency.get("max", 0),
            latency.get("p95", 0),
            result.get("status", "UNKNOWN"),
            json.dumps(result),
        ))

        run_id = cursor.lastrowid

        # Insérer les détails des tests
        for test in result.get("tests", []):
            details = test.get("details")
            if isinstance(details, (dict, list)):
                details = json.dumps(details, ensure_ascii=True)
            elif details is None:
                details = ""
            else:
                details = str(details)

            passed_value = test.get("passed", False)
            if not isinstance(passed_value, bool):
                passed_value = bool(passed_value)

            cursor.execute("""
                INSERT INTO test_details (
                    run_id, test_name, passed, details, latency_ms
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                run_id,
                test.get("name"),
                passed_value,
                details,
                test.get("latency_ms", 0),
            ))

        conn.commit()
        conn.close()
        return run_id

    def get_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupérer les runs récents.

        Args:
            limit: Nombre maximum de runs à retourner

        Returns:
            Liste des runs (sans les données JSON complètes pour performance)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, timestamp, api_name, total_tests, passed_count, failed_count,
                success_rate, error_rate, latency_avg_ms, status, created_at
            FROM test_runs
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_run(self, run_id: int) -> Dict[str, Any]:
        """
        Récupérer un run spécifique avec tous ses détails.

        Args:
            run_id: ID du run

        Returns:
            Dict contenant le run complet ou None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT full_result FROM test_runs WHERE id = ?", (run_id,))
        row = cursor.fetchone()
        conn.close()
        return json.loads(row["full_result"]) if row else None

    def get_latest_run(self) -> Dict[str, Any]:
        """
        Récupérer le dernier run.

        Returns:
            Dict du dernier run ou None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT full_result FROM test_runs
            ORDER BY created_at DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return json.loads(row["full_result"]) if row else None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Récupérer les statistiques globales sur tous les runs.

        Returns:
            Dict contenant des statistiques d'agrégation
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) as total_runs,
                AVG(success_rate) as avg_success_rate,
                AVG(error_rate) as avg_error_rate,
                AVG(latency_avg_ms) as avg_latency,
                MIN(latency_min_ms) as min_latency,
                MAX(latency_max_ms) as max_latency,
                SUM(CASE WHEN status = 'OK' THEN 1 ELSE 0 END) as healthy_runs
            FROM test_runs
        """)
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {}

        return {
            "total_runs": row[0] or 0,
            "avg_success_rate": round(row[1], 2) if row[1] is not None else 0,
            "avg_error_rate": round(row[2], 2) if row[2] is not None else 0,
            "avg_latency_ms": round(row[3], 2) if row[3] is not None else 0,
            "min_latency_ms": round(row[4], 2) if row[4] is not None else 0,
            "max_latency_ms": round(row[5], 2) if row[5] is not None else 0,
            "healthy_runs_count": row[6] or 0,
        }

    def clear_old_runs(self, keep_count: int = 100):
        """
        Supprimer les anciens runs, en conservant les N plus récents.

        Args:
            keep_count: Nombre de runs à conserver
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM test_runs
            ORDER BY created_at DESC, id DESC
            LIMIT -1 OFFSET ?
        """, (keep_count,))
        ids_to_delete = [row[0] for row in cursor.fetchall()]

        for run_id in ids_to_delete:
            cursor.execute("DELETE FROM test_details WHERE run_id = ?", (run_id,))
            cursor.execute("DELETE FROM test_runs WHERE id = ?", (run_id,))

        conn.commit()
        conn.close()
