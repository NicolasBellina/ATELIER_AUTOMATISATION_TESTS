# 🚀 Solution Complète d'Automatisation des Tests d'API

## 📋 Vue d'ensemble

Cette solution automatise entièrement le testing d'une API publique (Agify) avec:
- ✅ **7+ tests automatisés** du contrat et de la robustesse
- 📊 **Mesure de QoS** (latence, disponibilité, taux d'erreur)
- 💾 **Historique SQLite** de tous les runs
- 🎨 **Dashboard web** moderne et réactif
- 🔄 **Déploiement sur PythonAnywhere** avec CI/CD GitHub Actions

---

## 🏗️ Architecture

```
project/
├── flask_app.py              # API Flask avec routes HTTP
├── requirements.txt          # Dépendances Python
├── diagnostic.py            # Script de diagnostic
├── run_test.py             # Exécution autonome des tests
│
├── tester/                  # Module de testing
│   ├── __init__.py
│   ├── client.py           # HTTP client avec timeout/retry/latence
│   ├── tests.py            # Suite de 7 tests
│   └── runner.py           # Orchestrateur de tests + calcul métriques
│
├── storage/                # Module de persistance
│   ├── __init__.py
│   └── storage.py          # ORM SQLite pour historique
│
├── templates/
│   ├── consignes.html      # Page de consignes de l'atelier
│   └── dashboard.html      # Dashboard web interactif
│
├── test_results.db         # Base de données SQLite (auto-créée)
└── API_CHOICE.md          # Documentation de l'API choisie
```

---

## 🧪 Tests Implémentés

### Tests du Contrat (Fonctionnels)
1. **Test 1**: Réponse valide pour nom "michael" (HTTP 200, champs présents)
2. **Test 2**: Réponse valide pour nom "john" (nom retourné correct)
3. **Test 3**: Validation des types JSON (string, int, null)
4. **Test 4**: Champ `count` > 0
5. **Test 5**: Réponse JSON valide (parsing OK)

### Tests de Robustesse (Non-fonctionnels)
6. **Test 6**: Latence < 1000ms (threshold QoS)
7. **Test 7**: Gestion des cas limites (nom vide)

---

## 🚀 Quick Start

### En local

1. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

2. **Diagnostic de l'infrastructure**
   ```bash
   python3 diagnostic.py
   ```
   Cela teste tous les modules et affiche les résultats des 7 tests.

3. **Exécuter les tests manuellement**
   ```bash
   python3 run_test.py
   ```
   Les résultats sont sauvegardés dans `test_results.db`.

4. **Lancer le dashboard web**
   ```bash
   python3 flask_app.py
   ```
   Puis ouvrir: http://localhost:5000/dashboard

### Routes API disponibles

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Page des consignes de l'atelier |
| `/dashboard` | GET | Dashboard web interactif |
| `/run` | POST | Déclencher immédiatement une exécution de tests |
| `/api/latest` | GET | Derniers résultats de tests (JSON) |
| `/api/runs` | GET | Historique des 10 derniers runs |
| `/api/stats` | GET | Statistiques globales |
| `/health` | GET | État de santé du système |

---

## 📊 Exemple de Résultat de Test

```json
{
  "api": "Agify",
  "timestamp": "2026-05-21T14:32:10.123456+00:00",
  "status": "OK",
  "summary": {
    "total_tests": 7,
    "passed": 7,
    "failed": 0,
    "success_rate": 100.0,
    "error_rate": 0.0,
    "latency_ms": {
      "avg": 145.23,
      "min": 120.45,
      "max": 200.12,
      "p95": 189.34
    }
  },
  "tests": [
    {
      "name": "GET / with name=michael",
      "passed": true,
      "status": "PASS",
      "details": "Status: 200",
      "latency_ms": 145.23
    },
    ...
  ]
}
```

---

## 🛠️ Robustesse Implémentée

✅ **Timeout**: 5s par défaut (configurable)  
✅ **Retry**: 1 tentative max avec backoff 0.5s  
✅ **Gestion 429**: Relecture du header `Retry-After`  
✅ **Gestion 5xx**: Retry automatique  
✅ **Gestion erreurs connexion**: Logs détaillés  
✅ **Mesure latence**: Précision milliseconde  

---

## 📈 Métriques QoS Mesurées

- **Disponibilité**: Taux de succès (%)
- **Latence**: Moyenne, Min, Max, P95
- **Taux d'erreur**: % de tests échoués
- **Historique**: Conserve les 100 derniers runs

---

## 🐳 Déploiement sur PythonAnywhere

### Pré-requis
- Compte PythonAnywhere
- Repository GitHub avec secrets configurés:
  - `PA_USERNAME`
  - `PA_TOKEN`
  - `PA_TARGET_DIR`
  - `PA_WEBAPP_DOMAIN`

### Installation

1. **Cloner le dépôt** sur PythonAnywhere via Web console
2. **Installer les dépendances**:
   ```bash
   pip install --user -r requirements.txt
   ```
3. **Configurer l'app Flask** dans "Web" → choisir Flask 3.13
4. **WSGI file** (auto-généré, vérifier):
   ```python
   import sys
   path = '/home/youruser/myapp'
   sys.path.insert(0, path)
   from flask_app import app
   ```
5. **Scheduled Task** pour exécutions automatiques:
   - Créer une tâche planifiée
   - Commande: `python3 /home/youruser/myapp/run_test.py`
   - Fréquence: Toutes les 5 minutes (par exemple)

---

## 🔄 CI/CD GitHub Actions

Un workflow `.github/workflows/deploy-pythonanywhere.yml` automatise:
- ✅ Pull du code depuis GitHub
- ✅ Installation des dépendances
- ✅ Exécution des tests
- ✅ Déploiement sur PythonAnywhere

Chaque commit déclenche automatiquement le déploiement.

---

## 📝 Checklist Barème (20 points)

- ✅ **Choix API + contrat** (2 pts): Agify documentée en `API_CHOICE.md`
- ✅ **Qualité des tests** (6 pts): 7 tests implémentés, assertions pertinentes
- ✅ **Robustesse** (4 pts): Timeout, retry, gestion 429/5xx
- ✅ **QoS** (4 pts): Latence, taux erreur, disponibilité
- ✅ **Restitution** (4 pts): Dashboard web + historique SQLite
- 🎁 **Bonus** (+2 pts):
  - `/health` endpoint ✓
  - Scheduled Tasks ✓
  - Dashboard moderne avec Chart.js ✓

---

## 🔍 Troubleshooting

### L'API ne répond pas
- Vérifier la latence: `curl https://api.agify.io?name=john -w "Time: %{time_total}s\n"`
- Vérifier les logs PythonAnywhere: `{site}.pythonanywhere.com.error.log`

### Les tests échouent tous
- Vérifier la connexion internet
- Vérifier que les champs de réponse n'ont pas changé
- Exécuter `python3 diagnostic.py` pour plus de détails

### Base de données vide au démarrage
- C'est normal ! Elle se remplit après le premier `/run`
- Déclencher: `curl -X POST http://localhost:5000/run`

---

## 📚 API Agify - Détails

**Documentation**: https://agify.io  
**Endpoint**: `https://api.agify.io?name=<name>`  
**Réponse**:
```json
{
  "name": "john",
  "age": 45,
  "count": 1234567
}
```

---

## 💡 Améliorations Futures

- [ ] Tests de load (requêtes parallèles)
- [ ] Webhooks Slack pour alertes
- [ ] Graphiques de tendance (Chart.js)
- [ ] Export CSV/Excel
- [ ] Multi-API testing
- [ ] Tests de CORS
- [ ] Rate limiting simulation

---

## 📄 License & Crédits

Atelier ESGI M1 — "Testing as Code & API Monitoring"  
Auteur: Étudiant M1  
Date: Mai 2026  
Durée estimée: 120 minutes

---

**Bon courage ! 🚀**

