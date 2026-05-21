"""
Suite de tests pour l'API Agify.
Tests du contrat (réponse valide, champs, types, codes HTTP).
Tests de robustesse (latence, gestion d'erreurs).
"""
from typing import Dict, List, Tuple
from .client import APIClient

class APITest:
    """Représente un test avec son résultat."""

    def __init__(self, name: str, passed: bool, details: str = "", latency_ms: float = 0):
        self.name = name
        self.passed = passed
        self.details = details
        self.latency_ms = latency_ms

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "status": "PASS" if self.passed else "FAIL",
            "details": self.details,
            "latency_ms": round(self.latency_ms, 2)
        }


class AgifyTestSuite:
    """Suite de tests pour l'API Agify."""

    def __init__(self, client: APIClient):
        self.client = client
        self.tests: List[APITest] = []

    def test_valid_name_michael(self) -> APITest:
        """Test 1: Vérifier que Agify retourne une réponse valide pour un nom valide (michael)."""
        response, latency, status_code, error = self.client.get(params={"name": "michael"})

        passed = (
            status_code == 200 and
            "name" in response and
            "age" in response and
            "count" in response
        )

        details = f"Status: {status_code}" if passed else f"Error: {error}"
        return APITest(
            name="GET / with name=michael",
            passed=passed,
            details=details,
            latency_ms=latency
        )

    def test_valid_name_john(self) -> APITest:
        """Test 2: Vérifier avec un autre nom valide (john)."""
        response, latency, status_code, error = self.client.get(params={"name": "john"})

        passed = (
            status_code == 200 and
            "name" in response and
            response.get("name") == "john"
        )

        details = f"Name returned: {response.get('name')}" if passed else f"Error: {error}"
        return APITest(
            name="GET / with name=john",
            passed=passed,
            details=details,
            latency_ms=latency
        )

    def test_response_schema_types(self) -> APITest:
        """Test 3: Vérifier que les types de champs sont corrects."""
        response, latency, status_code, error = self.client.get(params={"name": "alice"})

        if status_code != 200:
            return APITest(
                name="Response schema types validation",
                passed=False,
                details=f"Status not 200: {status_code}",
                latency_ms=latency
            )

        # Vérifier les types
        name_is_string = isinstance(response.get("name"), str)
        age_is_int_or_null = isinstance(response.get("age"), (int, type(None)))
        count_is_int = isinstance(response.get("count"), int)

        passed = name_is_string and age_is_int_or_null and count_is_int

        details = (
            f"name is str: {name_is_string}, age is int/null: {age_is_int_or_null}, "
            f"count is int: {count_is_int}"
        )

        return APITest(
            name="Response schema types validation",
            passed=passed,
            details=details,
            latency_ms=latency
        )

    def test_count_field_positive(self) -> APITest:
        """Test 4: Vérifier que le champ 'count' est > 0."""
        response, latency, status_code, error = self.client.get(params={"name": "bob"})

        if status_code != 200:
            return APITest(
                name="Count field is positive",
                passed=False,
                details=f"Status not 200: {status_code}",
                latency_ms=latency
            )

        count = response.get("count", -1)
        passed = count > 0

        details = f"count = {count}"
        return APITest(
            name="Count field is positive",
            passed=passed,
            details=details,
            latency_ms=latency
        )

    def test_content_type_json(self) -> APITest:
        """Test 5: Vérifier que la réponse est du JSON valide."""
        response, latency, status_code, error = self.client.get(params={"name": "charlie"})

        # Si on a pu parser le JSON, c'est bon
        passed = status_code == 200 and isinstance(response, dict)

        details = "Response is valid JSON dict" if passed else f"Status: {status_code}, Error: {error}"
        return APITest(
            name="Content-Type JSON validation",
            passed=passed,
            details=details,
            latency_ms=latency
        )

    def test_latency_under_threshold(self) -> APITest:
        """Test 6: Vérifier que la latence est < 1000ms (seuil raisonnable)."""
        response, latency, status_code, error = self.client.get(params={"name": "david"})

        threshold_ms = 1000
        passed = latency < threshold_ms and status_code == 200

        details = f"Latency: {latency:.2f}ms (threshold: {threshold_ms}ms)"
        return APITest(
            name="Latency under 1000ms",
            passed=passed,
            details=details,
            latency_ms=latency
        )

    def test_empty_name_error_handling(self) -> APITest:
        """Test 7 (Bonus): Vérifier la gestion d'une requête avec nom vide."""
        response, latency, status_code, error = self.client.get(params={"name": ""})

        # Agify accepte les noms vides mais retourne une réponse avec age=None
        passed = status_code in [200, 400] and (response or error)

        details = f"Status: {status_code}, Response: {response if response else 'empty'}"
        return APITest(
            name="Empty name error handling",
            passed=passed,
            details=details,
            latency_ms=latency
        )

    def run_all(self) -> List[APITest]:
        """Exécuter tous les tests et retourner les résultats."""
        self.tests = [
            self.test_valid_name_michael(),
            self.test_valid_name_john(),
            self.test_response_schema_types(),
            self.test_count_field_positive(),
            self.test_content_type_json(),
            self.test_latency_under_threshold(),
            self.test_empty_name_error_handling(),
        ]
        return self.tests

    def get_results(self) -> List[Dict]:
        """Retourner les résultats des tests sous forme de dictionnaires."""
        return [test.to_dict() for test in self.tests]

