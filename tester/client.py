"""
HTTP Client wrapper avec timeout, mesure de latence et gestion des erreurs.
"""
import time
from typing import Dict, Tuple

try:
    import requests
    from requests.exceptions import Timeout, ConnectionError, RequestException
except ImportError:  # pragma: no cover - fallback utile si requests n'est pas installé
    requests = None
    Timeout = ConnectionError = RequestException = Exception


class APIClient:
    """Client HTTP pour l'API Agify avec mesure de latence et robustesse."""

    def __init__(self, base_url: str, timeout: float = 5.0, max_retries: int = 1):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session() if requests else None

    def get(self, endpoint: str = "", params: Dict = None, retry_count: int = 0) -> Tuple[Dict, float, int, str]:
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        if not self.session:
            latency_ms = (time.time() - start_time) * 1000
            return {}, latency_ms, -1, "requests is not installed"

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                headers={"User-Agent": "Atelier-API-Tests/1.0"},
            )
            latency_ms = (time.time() - start_time) * 1000

            if response.status_code >= 500 and retry_count < self.max_retries:
                time.sleep(0.5)
                return self.get(endpoint, params, retry_count + 1)

            if response.status_code == 429 and retry_count < self.max_retries:
                retry_after = response.headers.get("Retry-After", "1")
                time.sleep(float(retry_after))
                return self.get(endpoint, params, retry_count + 1)

            try:
                data = response.json()
            except Exception:
                data = {}

            error_msg = "" if response.status_code < 400 else f"HTTP {response.status_code}"
            return data, latency_ms, response.status_code, error_msg

        except Timeout:
            latency_ms = (time.time() - start_time) * 1000
            return {}, latency_ms, -1, f"Timeout after {self.timeout}s"
        except ConnectionError:
            latency_ms = (time.time() - start_time) * 1000
            return {}, latency_ms, -1, "Connection error"
        except RequestException as e:
            latency_ms = (time.time() - start_time) * 1000
            return {}, latency_ms, -1, f"Request error: {e}"
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return {}, latency_ms, -1, f"Unexpected error: {e}"

    def close(self):
        if self.session:
            self.session.close()

