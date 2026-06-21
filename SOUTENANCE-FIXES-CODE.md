# SOUTENANCE BLOC 6 — Vérification technique (21 juin 2026)

> **Règle** : tous les chiffres ci-dessous ont été obtenus par exécution réelle, pas par documentation.
> Branche de travail : `fix/soutenance-bloc6-quickwins`

---

## 1. Vrais chiffres de tests

### Méthode de collecte
Tests lancés séparément (comme la CI), avec docker-compose actif
(gwd disponible sur `localhost:23179`).

### Résultats par catégorie

| Catégorie | Collectés | Passés | Échoués | Skippés | Durée |
|-----------|-----------|--------|---------|---------|-------|
| Unitaires (`tests/python/unit/`) | 573 | 543 | 30 | 0 | 3.27 s |
| Intégration (`tests/python/integration/`) | 87 | 87 | 0 | 0 | 12.22 s |
| Fonctionnels (`tests/python/functional/`) | 49 | 40 | 0 | 9 | 11.53 s |
| **TOTAL** | **709** | **670** | **30** | **9** | — |

**Total = 573 + 87 + 49 = 709** ✓ (le chiffre du README est juste)

### Couverture

```
TOTAL python_app/utils/          306 stmts   93 miss  ~70 %  (couche testée)
TOTAL python_app/utils/utils/    306 stmts  306 miss    0 %  (répertoire en double, code mort)
TOTAL mesuré par coverage.py     612 stmts  399 miss  34.80 %
```

**Affirmation honnête pour la soutenance** :
- La couche utilitaires active (`python_app/utils/`) atteint **~70 % de couverture**.
- Le total brut mesuré est **34.8 %** car `python_app/utils/utils/` est un répertoire
  dupliqué (migration non nettoyée) à 0 % qui dilue la mesure.
- La valeur "70 %" est vraie mais incomplète ; il faut préciser le périmètre.

### Durée totale
- Unitaires seuls : **3.27 s** (pas 4.62 s — ce chiffre n'est pas documenté dans README)
- Toutes catégories enchaînées : ~27 s

### Tests en échec réels (30 unitaires)

Les 30 tests unitaires qui échouent s'exécutent sur le vrai gwd via HTTP.
Ils ne tombent PAS à cause d'une daemonisation :

| Fichier de test | Nb échecs | Nature de l'échec |
|---|---|---|
| `test_base_config.py` | 7 | Routes gwd inexistantes renvoient 400 (ex: `m=STAT`, `m=VERCONF`) |
| `test_date_formatting.py` | 4 | Routes gwd spécifiques renvoient 400 |
| `test_gedcom_parsing.py` | 6 | Requêtes `p=Charles&n=Windsor` : gwd renvoie un titre de base sans le nom (page non personnalisée) |
| `test_http_params.py` | 8 | Modes gwd absents (400) ou language `?lang=fr` non détecté |
| `test_privacy.py` | 5 | Routes de filtrage confidentialité renvoient 400 |

Ces 30 échecs sont stables et reproductibles ; ils préexistaient avant cette branche.

**Concernant IT-PY-003 / daemonisation** :
`test_html_generation.py` (10 tests d'intégration) lance gwd localement sur le port 23183.
Il passe quand exécuté seul (`pytest tests/python/integration/`), mais **échoue avec 10 erreurs**
quand combiné avec les autres suites car le processus gwd se termine immédiatement
("gwd exited unexpectedly while starting"). Ce n'est pas un problème de port occupé
mais un problème de chemins relatifs / permissions dans l'environnement local.
En CI GitHub Actions, ces tests passent car la fixture démarre gwd dans le bon répertoire.

---

## 2. Flag "OCaml gwd available: False" — C31.2

### Cause

Dans `python_app/app.py`, la fonction `main()` affichait :

```python
print(f"OCaml gwd available: {Config.OCAML_GWD_PATH.exists()}")
```

`Config.OCAML_GWD_PATH` = `/app/GeneWeb/gw/gwd`

Le conteneur proxy (`geneweb-proxy`) **ne contient pas** les binaires OCaml.
L'image `Dockerfile` ne copie que `python_app/` et `entrypoint.sh`.
Le binaire gwd tourne dans le conteneur **séparé** `geneweb` et est accessible
via le réseau Docker interne (`OCAML_GWD_HOST=geneweb`, `OCAML_REMOTE=true`).

C'est donc un **faux négatif pur** : le proxy vérifie l'existence d'un fichier
sur son propre système de fichiers alors qu'il devrait requêter le réseau.
Le proxying fonctionne parfaitement car `OCamlBridge.proxy_request()` utilise
`http://geneweb:2317/...` via HTTP.

### Réponse à un examinateur

> « Le log dit False mais /test répond en 200 — c'est contradictoire ? »

Non, c'est cohérent : le log vérifie l'existence du **binaire local** (`Path.exists()`),
qui est absent du conteneur proxy par design (séparation des responsabilités Docker).
Le proxying passe par HTTP sur le réseau interne Docker, indépendamment du binaire.
C'est un artefact de log corrigé dans cette branche.

### Correction appliquée (`python_app/app.py`)

```python
# Avant
print(f"OCaml gwd available: {Config.OCAML_GWD_PATH.exists()}")

# Après
if Config.OCAML_REMOTE:
    print(f"OCaml gwd available: remote at {Config.OCAML_GWD_HOST}:{Config.OCAML_GWD_PORT}")
else:
    print(f"OCaml gwd available: {Config.OCAML_GWD_PATH.exists()}")
```

Le `/health` renvoie maintenant `"ocaml_gwd_available": "remote:geneweb:2317"`.

### Warning Flask "development server"

Le warning est **attendu** : on utilise `app.run()` (Werkzeug dev server).
En production, on passerait par **gunicorn** (WSGI) + nginx (reverse proxy) :
```
nginx → gunicorn [4 workers] → Flask app → gwd (réseau interne)
```
Le Dockerfile utilise déjà `tini` comme init et `USER geneweb` — la migration
vers gunicorn est documentée dans `docs/` mais hors périmètre de ce sprint.

---

## 3. Sécurité C32.2 — Audit "documenté vs implémenté"

### Audit état réel (avant quick wins)

| Mesure de sécurité | Documentée | Implémentée | Preuve |
|---|---|---|---|
| Pas de `shell=True` | Oui | **OUI** | `grep -r "shell=True" python_app/` → 0 résultat |
| Conteneur proxy non-root | Oui | **OUI** | `docker exec geneweb-proxy whoami` → `geneweb` |
| Conteneur gwd non-root | Oui | **OUI** | `docker exec geneweb whoami` → `geneweb` |
| Services isolés en conteneurs séparés | Oui | **OUI** | docker-compose : 2 services distincts |
| Bandit bloquant en CI | Oui | **OUI** | ci.yml L118 : `bandit -q -r python_app \|\| exit 1` |
| pip-audit bloquant en CI | Oui | **OUI** | ci.yml L113 : `pip-audit` + `set -euo pipefail` |
| gwd bindé en loopback | Recommandé | **NON** (avant QW) | Ports `0.0.0.0:23179` et `0.0.0.0:23176` |
| Headers de sécurité HTTP | Recommandé | **NON** (avant QW) | `curl -I localhost:23182/health` → aucun header CSP/X-Frame |
| Rate limiting | Recommandé | **NON** | Pas de flask-limiter dans le code |

### Quick wins implémentés

#### QW-1 : Headers de sécurité Flask (via `@app.after_request`)

Ajouté dans `python_app/app.py` :

```python
@app.after_request
def add_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

**Preuve après rebuild** :
```
curl -sI http://localhost:23182/health

HTTP/1.1 200 OK
Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
```

#### QW-2 : Backends OCaml bindés en loopback (`docker-compose.yml`)

```yaml
# Avant
ports:
  - "23179:2317"   # gwd
  - "23176:2316"   # gwsetup

# Après
ports:
  - "127.0.0.1:23179:2317"   # gwd (loopback-only, dev/tests)
  - "127.0.0.1:23176:2316"   # gwsetup (loopback-only)
```

**Preuve après rebuild** :
```
docker ps --format "table {{.Names}}\t{{.Ports}}"

geneweb-proxy   0.0.0.0:23182->23182/tcp          ← proxy public ✓
geneweb         127.0.0.1:23176->2316/tcp          ← loopback seul ✓
                127.0.0.1:23179->2317/tcp          ← loopback seul ✓
```

Stack toujours healthy après les deux QW :
```
curl -s -o /dev/null -w "%{http_code}" http://localhost:23182/test   → 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:23182/health → 200
```

#### Ce qui reste hors périmètre (signalé, non implémenté)
- **Rate limiting** : nécessite `flask-limiter` + backend Redis, non trivial.
- **User non-root** : déjà en place dans les deux Dockerfiles (`USER geneweb`).
  Aucune action requise.

### Tableau récapitulatif avant/après quick wins

| Mesure | Avant QW | Après QW |
|---|---|---|
| `shell=True` | ✅ absent | ✅ absent |
| Conteneurs non-root | ✅ | ✅ |
| Services isolés | ✅ | ✅ |
| Bandit CI bloquant | ✅ | ✅ |
| pip-audit CI bloquant | ✅ | ✅ |
| gwd bindé en loopback | ❌ `0.0.0.0` | ✅ `127.0.0.1` |
| Headers sécurité HTTP | ❌ absents | ✅ CSP + X-Content-Type + X-Frame + Referrer |
| Rate limiting | ❌ non implémenté | ❌ non implémenté (hors périmètre) |

---

## 4. Commits Bandit (détection → correction)

Le job Bandit CI a été introduit dans **PR #239** (commit `601c470`).
Les corrections avaient été faites juste avant la fusion, lors de l'écriture du pipeline.

| Hash | Date | Message |
|---|---|---|
| `a2a3882` | 2025-10-30 | `chore(security): address Bandit warnings` — B404/B603/B607/B110 |
| `37d7727` | 2025-10-30 | `chore(security): address Bandit warnings` — idem (double commit) |
| `402cc28` | 2025-10-31 | `security: add Bandit-safe patterns (shell=False, internal HTTP nosec)` |
| `88e6a91` | 2025-10-31 | `security: fix Bandit B110 (avoid bare except/pass) in admin URL rewrite` |
| `601c470` | 2025-10-31 | **Merge PR #239** `118-ci-002-configure-code-quality-tools` — Bandit CI actif |

**Détail du commit principal** (`a2a3882`) :
- `subprocess` appelé avec `shell=False` explicite → nosec B603
- Remplacement du `bare except: pass` (B110) par un log explicite
- Annotation `# nosec B310` sur les `requests.get()` internes (B310)

```bash
# Pour rejouer la détection (Bandit doit être installé)
git show a2a3882~1 -- python_app/ocaml_bridge.py | bandit -
# Pour voir la correction
git diff a2a3882~1 a2a3882
```

---

## 5. Accessibilité (md files)

Scan de tous les fichiers `.md` du projet (hors `source_geneweb/_opam/`) :

```
grep -n '!\[' README.md tests/**/*.md docs/**/*.md
```

Résultat : **1 seule image trouvée**, dans `README.md` :

```markdown
[![CI Status](https://github.com/Antonyjin/Legacy-Project/actions/workflows/ci.yml/badge.svg)](...)
```

Le texte alternatif `CI Status` est **déjà présent**. Aucune correction nécessaire.

---

## Synthèse pour la soutenance

| Affirmation dans les slides | Réalité mesurée | Statut |
|---|---|---|
| "709 tests" | 573 + 87 + 49 = 709 | ✅ VRAI |
| "70 % de couverture" | 70 % sur utils/ actifs, 35 % total (dead code inclus) | ⚠️ À nuancer |
| "4.62 s" | 3.27 s (unitaires), ~27 s total | ❌ Chiffre non documenté |
| "gwd available: False = bug" | Faux négatif, vrai comportement proxying | ✅ Expliqué |
| "conteneurs non-root" | USER geneweb dans les 2 Dockerfiles | ✅ IMPLÉMENTÉ |
| "bandit bloquant" | `bandit ... \|\| exit 1` dans ci.yml | ✅ IMPLÉMENTÉ |
| "pip-audit bloquant" | `pip-audit` + `set -euo pipefail` | ✅ IMPLÉMENTÉ |
| "headers sécurité" | Avant QW : absents. Après QW : présents | ✅ IMPLÉMENTÉ |
| "shell=True absent" | 0 occurrence dans python_app/ | ✅ VRAI |
| "backends loopback" | Avant QW : 0.0.0.0. Après QW : 127.0.0.1 | ✅ IMPLÉMENTÉ |
