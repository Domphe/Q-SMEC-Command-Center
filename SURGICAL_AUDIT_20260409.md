# Q-SMEC Command Center — Surgical Audit
**Date:** 2026-04-09  
**Auditor:** Claude Code (claude-sonnet-4-6)  
**Branch:** claude/pedantic-hodgkin  
**Repo root:** E:\data1\Q-SMEC-Command-Center  
**Overall Grade: C+**

---

## Executive Summary

The backend architecture is structurally sound: the service layer is respected, imports are clean, no circular dependencies, no hardcoded API keys, and f-string compliance is perfect. However, a critical async/blocking bug in `ai_service.py` can freeze the entire FastAPI event loop on every AI call; two of five expected APScheduler jobs are completely missing; email send dates are never parsed from Gmail (always overwritten with the sync time); note export and email sync logic are each duplicated in two places; and there are zero tests.

**3 P0 bugs must be fixed before this app is reliable. 10 total P0/P1 issues.**

---

## CHECK 1 — CODE QUALITY

### APScheduler Jobs (backend/main.py)

**Registered jobs (3 of 5 expected):**

| Job | Interval | Status |
|-----|----------|--------|
| `run_email_sync` | 15 min | Registered ✅ |
| `run_repo_health_check` | 1 hr | Registered ✅ |
| `run_note_export` | 5 min | Registered ✅ |
| `agent_digest` | 30 min | **MISSING** — no job file, not registered ❌ |
| `morning_brief` | 7:00 AM daily | **MISSING** — no job file, not registered ❌ |

**main.py other issues:**
- Generic `except Exception` at scheduler startup loses context about the failure
- `wait=False` on scheduler shutdown may interrupt in-flight jobs
- No telemetry if scheduler silently fails to start

**Grade: B+**

---

### backend/jobs/email_sync.py (2.8K) — Grade: B-

- **BUG (P0-02):** Line 46 writes `date=datetime.utcnow()` — overwrites the Gmail RFC 2822 send date with the current time. All emails appear to arrive at sync time. Chronological display is broken.
- Silent error swallowing on sync failure — logs, returns, no retry, no downstream alert
- No success-completion log
- `== True` SQLAlchemy comparison (noqa'd, not a real bug)

---

### backend/jobs/note_export.py (1.6K) — Grade: A-

- Clean, defensive `os.makedirs(exist_ok=True)` pattern
- **DRY violation (P1-02):** 28 lines duplicated exactly in `backend/routers/notes.py:91-119`
- No try/except around `json.dump()` — file I/O failure is unhandled crash

---

### backend/jobs/repo_health.py (1.7K) — Grade: B

- Module-level mutable `_last_health` dict — not thread-safe, would corrupt with multiple scheduler instances
- `get_cached_health()` exported function depends on global state — untestable
- No logging of which specific repos failed
- No cache invalidation strategy

---

### backend/services/ai_service.py (2.8K) — Grade: C+ — CRITICAL

**CRITICAL BUG (P0-01):** Both `call_claude()` and `call_gemini()` are declared `async def` but call **synchronous blocking** SDK methods:

```python
# Line 28 — blocks the FastAPI event loop:
response = client.messages.create(...)

# Line 64 — blocks the FastAPI event loop:
response = client.models.generate_content(...)
```

Every AI call freezes the entire FastAPI server for its duration (100ms–30s). Under any concurrent load, all other requests queue behind the AI call.

**Required fix:** `await asyncio.to_thread(client.messages.create, ...)` or remove `async`.

**Other issues:**
- Placeholder check `"sk-ant-REPLACE"` is too loose — real keys also start with `"sk-ant-"`, so this check is semantically broken
- Exception handler logs `str(e)` but discards traceback — debugging is harder than necessary

**Confirmed:** Real Anthropic Claude and Google Gemini API calls are made — these are not stubs.

---

### backend/services/gmail_service.py (6.8K) — Grade: A-

**Well designed:** singleton pattern, lazy Google imports, credential auto-detection (OAuth2 + service account).

**Bugs:**
- **Line 167:** From-header parsing via `split("<")` — will fail on addresses like `"Name <with angle>" <email@domain.com>`; should use `email.headerparser`
- **Line 202:** Silent `continue` on email parse failure — no logging of skipped message IDs; data is silently lost
- No exponential backoff on Gmail API rate limits
- Pagination loop can theoretically spin forever on inconsistent `nextPageToken`

**Confirmed:** Real Gmail API calls are made.

---

### backend/services/github_service.py (3.7K) — Grade: A

**BUG (P0-03):** `list_org_repos()` line 98 calls `gh.get_user()` instead of `gh.get_organization()`. This function has never worked correctly.

**Other issues:**
- `list(repo.get_commits()[:1])` — materializes a generator slice unnecessarily; use `next(repo.get_commits(), None)`
- Health rating uses string matching on `"month"` in commit age string — brittle if format changes
- `get_repo_info()` returns `{"health": "error", ...}` on exception, but caller `repo_health.py:38` does not check for the `"error"` key

**Confirmed:** Real GitHub API calls are made.

---

### backend/services/email_triage.py (4.1K) — Grade: A

- Rule engine is sound; patterns correctly map to categories
- Confidence scoring uses static weights (not learned, but functional)
- No AI fallback when confidence is below threshold

---

### backend/services/file_bridge.py (1.5K) — Grade: A

- Clean, minimal — no issues
- `export_state()` is defined here but **never called anywhere** (see Data Flow section)

---

### backend/services/model_router.py (2.9K) — Grade: B+

- Complexity scoring weights are arbitrary magic numbers (`task > 500 chars = +15`, `"physics" = +20`)
- Silent `max(0, min(100, score))` clamp — no warning when score exceeds bounds
- Logic is sound, weights should be configurable

---

### backend/routers/ai_router.py (3.9K) — Grade: B

- **CRITICAL (inherited):** Awaits `call_claude()` and `call_gemini()` — both block the event loop (P0-01)
- No timeout on task execution — a hanging Claude API call blocks the server indefinitely
- No streaming response, no cancellation mechanism
- Hardcoded model-name string matching — should use constants or enum
- Task `session.commit()` + `session.refresh()` lacks rollback on downstream failure

---

### backend/routers/emails.py (5.0K) — Grade: B+

- **BUG (P0-02 same root):** Line 75 writes `date=datetime.utcnow()` — same date-loss bug as email_sync.py
- `session.add()` is not rolled back if a downstream exception occurs
- POST `/api/emails/sync` returns 200 synchronously — should return 202 Accepted (it is an async operation)
- **DRY violation (P1-03):** 46-line email sync block copied from `jobs/email_sync.py`
- Full exception string returned to client at line 101 (see Security section)

---

### backend/routers/notes.py (3.7K) — Grade: B

- **DRY violation (P1-02):** `_export_pending_notes()` lines 91-119 is an exact copy of `jobs/note_export.py:17-50`
- Hard-delete with no soft-delete option and no confirmation
- `setattr()` for updates with no field validation

---

### backend/routers/repos.py (5.4K) — Grade: B

- Three separate `subprocess.check_output()` calls per repo — should batch into fewer calls
- `CalledProcessError` is not caught (only `subprocess.SubprocessError` and `OSError` are in the except clause)
- Health rating uses string matching (same brittle pattern as github_service.py)
- `folder` path not explicitly validated against REPO_REGISTRY before `os.path.join()`

---

### Remaining Files — All Grade A or A-

| File | Grade | Note |
|------|-------|------|
| routers/clients.py | A- | `setattr()` no validation |
| routers/pipeline.py | A | Clean |
| routers/overview.py | A | `== True` noqa (SQLAlchemy quirk) |
| backend/config.py | A | Clean |
| backend/database.py | A | Clean |
| backend/models/* | A | All clean |

---

### F-String Compliance (CLAUDE.md Rule)

**PASS** — Zero f-strings found in any backend Python file. All interpolation uses `.format()`.

---

### API-in-Router Compliance (CLAUDE.md Rule)

**PASS** — All external API calls go through the services layer:
- Gmail: via `services/gmail_service.py`
- GitHub: via `services/github_service.py`
- Claude/Gemini: via `services/ai_service.py`

---

## CHECK 2 — DATA FLOW

### Email Sync → SQLite → Digest → Bridge

```
Gmail API
  → gmail_service.sync_recent_emails()      # fetches raw email dicts
  → email_triage.categorize_email()          # rule-based classification
  → EmailCache table (SQLite)               # persisted record
  → emails.py router: GET /api/emails        # reads by category/search
  → overview.py: KPI aggregation             # action_required counts
  → file_bridge.export_email_digest()        # top 20 → bridge/email_digest.json
```

### EmailCache Schema

```
id (str, PK)         thread_id (str)       from_addr (str)
from_name (str)      to_addr (str)         subject (str)
snippet (str)        date (datetime)        category (str)
uc (str)             client (str)           has_attachment (bool)
is_unread (bool)     action_required (bool) raw_labels (JSON list)
categorized_by (str) synced_at (datetime)
```

**Schema consistency:** PASS — routers and jobs write identical fields.

### Data-Flow Bugs

**Bug DF-01 (P0-02):** `date` field. Both `jobs/email_sync.py:46` and `routers/emails.py:75` write `date=datetime.utcnow()` instead of parsing the Gmail RFC 2822 date string from `raw["date"]`. All stored emails carry the sync timestamp, not the send timestamp. Chronological queries are broken. The fix path is in the raw dict: `raw["date"]` contains the correct RFC 2822 string that `email.utils.parsedate_to_datetime()` can parse.

**Bug DF-02 (P1-04):** `export_state()` in `file_bridge.py` is defined but never called from any router, job, or startup hook. `bridge/command_center_state.json` is never written. The KPI snapshot intended for other Claude tools does not exist.

**Bug DF-03 (P1-03):** 46-line email sync block copied between `jobs/email_sync.py:17-60` and `routers/emails.py:43-89`. Only difference: `max_results` (50 vs 500). Should be extracted to `services/email_sync_service.py`.

### Bridge Directory State

| File | Source | Status |
|------|--------|--------|
| `bridge/email_digest.json` | `jobs/email_sync.run_email_sync()` | Not present (jobs not run) |
| `bridge/pending_notes.json` | `jobs/note_export.run_note_export()` | Not present (jobs not run) |
| `bridge/command_center_state.json` | `file_bridge.export_state()` | **Never written — function not called** |

### seed.py (227 lines, ~14KB)

- Inserts 13 clients, 23 UC pipeline records, 8 seed emails on first startup
- All data hardcoded in function bodies — no external JSON data file
- Email seed encodes category/uc assignments that duplicate `email_triage.py` rule logic
- No update mechanism — silently skips if any record exists
- DRY violation: mixes data definitions and DB session logic in same functions

### Import Graph — No Circular Dependencies

Full import chain: `config.py → database.py → models/ → seed.py → main.py → routers/ → services/ → jobs/`

All lazy imports (anthropic, google libs, github) are safe — startup does not fail if optional dependencies are absent.

---

## CHECK 3 — TEST COVERAGE

### Grade: F

**Zero test files exist.** No `tests/`, no `test_*.py`, no `*.test.ts`, no pytest config in `pyproject.toml`.

### CI Pipeline (.github/workflows/ci.yml)

| Step | Runs? | Passes failures? |
|------|-------|-----------------|
| Ruff lint + format | Yes | Fails build |
| Import sort | Yes | Fails build |
| deptry dependency check | Yes | Fails build |
| pip-audit vulnerability scan | Yes | **Silently ignored (`\|\| true`)** |
| Gitleaks secret scan | Yes | Fails build |
| Unit tests | **No** | N/A |
| Integration tests | **No** | N/A |

`pip-audit || true` means known CVEs are logged but do not block merge.

### Error Handling When APIs Are Unreachable

| API | Behavior on failure |
|-----|---------------------|
| Gmail | `sync_recent_emails()` catches `Exception`, logs, returns empty list. Dashboard shows stale data. No retry. |
| GitHub | `get_repo_info()` catches `Exception`, returns `{"health": "error"}`. Caller does not check for error key. |
| Anthropic/Gemini | `call_claude/call_gemini` catch `Exception`, return `{"error": str(e)}`. Task recorded as failed. |

No circuit breaker, no exponential backoff, no retry logic anywhere.

---

## CHECK 4 — ARCHITECTURE

### File Sizes

| File | Lines | Concern |
|------|-------|---------|
| backend/seed.py | 227 | Data + DB logic mixed; hardcoded business rules |
| backend/services/gmail_service.py | 204 | Large but appropriate for scope |
| backend/routers/emails.py | 146 | Contains 46-line email sync duplicate |
| backend/routers/repos.py | 125 | Subprocess heavy |
| backend/routers/ai_router.py | 120 | Blocking async calls |
| backend/routers/notes.py | 119 | Contains 28-line note export duplicate |
| backend/services/email_triage.py | 117 | Appropriate |
| **Total backend Python** | **~2,131** | |

### Duplicate Code

| Logic | Location A | Location B | Lines |
|-------|-----------|-----------|-------|
| Email sync | `jobs/email_sync.py:17-60` | `routers/emails.py:43-89` | 46 |
| Note export | `jobs/note_export.py:17-50` | `routers/notes.py:91-119` | 28 |

**Recommendation:** Extract each to a service function. The job and the manual endpoint both call the service.

### seed.py Doing Too Much

At 14KB, `seed.py` hardcodes 356 field assignments that mix data, formatting, and DB logic. It also encodes category labels that duplicate `email_triage.py` rules. Should be split: `seed_data.json` (data only) + thin `seed.py` loader.

---

## CHECK 5 — DIRECTORY STRUCTURE

```
Q-SMEC-Command-Center/
├── .env.example                   # tracked — contains real email (see Security)
├── .github/
│   └── workflows/ci.yml           # lint + security only, no tests
├── .gitignore                     # correct
├── .pre-commit-config.yaml        # ruff, deptry hooks
├── backend/
│   ├── config.py                  # env var loader
│   ├── database.py                # SQLModel engine
│   ├── main.py                    # FastAPI app, CORS, scheduler
│   ├── seed.py                    # startup seed (14KB, too large)
│   ├── jobs/
│   │   ├── email_sync.py          # 15-min background job
│   │   ├── note_export.py         # 5-min background job
│   │   └── repo_health.py         # 1-hr background job
│   │   # MISSING: agent_digest.py, morning_brief.py
│   ├── models/
│   │   ├── email_cache.py, note.py, client.py, pipeline.py, task.py
│   ├── routers/
│   │   ├── ai_router.py, clients.py, emails.py, notes.py
│   │   ├── overview.py, pipeline.py, repos.py
│   ├── services/
│   │   ├── ai_service.py          # CRITICAL blocking async bug
│   │   ├── email_triage.py, file_bridge.py
│   │   ├── github_service.py, gmail_service.py, model_router.py
│   └── static/                    # .gitkeep only — frontend not built
├── bridge/
│   └── README.md                  # Only file present — no JSON exports yet
├── frontend/
│   ├── src/
│   │   ├── pages/                 # 7 page components
│   │   └── components/            # 5 UI components
│   └── dist/                      # NOT PRESENT — frontend not built
├── scripts/
│   ├── deploy.sh                  # MODIFIED (unreviewed git change)
│   ├── dev.sh                     # MODIFIED (unreviewed git change)
│   └── setup.sh                   # MODIFIED (unreviewed git change)
├── pyproject.toml, uv.lock, CLAUDE.md
```

**Observations:**
- No root clutter — clean
- `backend/static/` empty — frontend must be built before serving
- `bridge/` empty of runtime files — expected on fresh worktree
- All three `scripts/*.sh` show unreviewed modifications in git status

---

## CHECK 6 — SECURITY

### Tracked Secrets

| Item | Status |
|------|--------|
| `.env` | NOT tracked ✅ |
| `client_secret.json` | NOT tracked ✅ |
| `token.json` | NOT tracked ✅ |
| Hardcoded API keys in Python | None found ✅ |
| Hardcoded API keys in JS | None found ✅ |
| `.env.example` line 13: `GMAIL_USER=s.dely@niketllc.com` | LOW — real email exposed ⚠️ |

### CORS Configuration (backend/main.py:102-108)

```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:8000",
    "http://niket-hv-01:8000",
]
allow_methods=["*"]
allow_headers=["*"]
```

| Check | Status |
|-------|--------|
| Not wildcard (`*`) | ✅ |
| Scoped to known internal origins | ✅ |
| Hardcoded hostnames (not env-configurable) | ⚠️ |
| All methods allowed | ⚠️ |
| All headers allowed | ⚠️ |
| No production domain | ⚠️ |

### Authentication

**No API authentication exists.** All 7 routers, all endpoints are fully open.

- Acceptable for LAN-only internal deployment
- **Not safe for internet-facing deployment**
- No Bearer token, no OAuth2, no session management

### FastAPI Auto-Docs

`/docs` (Swagger UI) and `/redoc` are enabled by default. No authentication gate. Anyone with network access can enumerate all API endpoints and schemas.

**Fix:** `FastAPI(docs_url=None, redoc_url=None)` in production, or gated behind auth middleware.

### Subprocess Safety (repos.py)

- Uses list form — **safe from shell injection** ✅
- `timeout=5` set ✅
- Does not validate `folder` against REPO_REGISTRY before `os.path.join()` ⚠️

### Error Exposure (emails.py:101)

```python
return {"synced": 0, "new": 0, "error": str(e)}
```

Full exception message returned to client. Internal paths, API structure, or key names could leak.

**Fix:** Log full exception server-side; return `{"error": "sync failed"}` to client.

### DEBUG Mode

`.env.example` ships with `DEBUG=true`. If this is copied to production `.env`, SQLAlchemy logs every SQL query (table names, query structure) to stdout/logs.

### pip-audit in CI

```yaml
- run: uv run pip-audit || true   # vulnerabilities silently ignored
```

Known CVEs pass CI. Should be `uv run pip-audit` with no `|| true`.

---

## Priority Fix List

### P0 — Must fix (data-correctness / stability)

| ID | File | Line(s) | Issue | Fix |
|----|------|---------|-------|-----|
| P0-01 | `backend/services/ai_service.py` | 17, 53 | `async def` wraps blocking `client.messages.create()` and `client.models.generate_content()` — freezes FastAPI event loop | `await asyncio.to_thread(client.messages.create, ...)` |
| P0-02 | `backend/jobs/email_sync.py` / `backend/routers/emails.py` | 46 / 75 | `date=datetime.utcnow()` overwrites Gmail send date — all emails show sync time | Parse `raw["date"]` with `email.utils.parsedate_to_datetime()` |
| P0-03 | `backend/services/github_service.py` | 98 | `gh.get_user()` should be `gh.get_organization()` — `list_org_repos()` never works | Replace with `gh.get_organization(org_name)` |

### P1 — Should fix (architecture / reliability)

| ID | File | Issue | Fix |
|----|------|-------|-----|
| P1-01 | `backend/jobs/` | `agent_digest` (30 min) and `morning_brief` (7 AM) jobs entirely missing | Create job files; register in `main.py` |
| P1-02 | `jobs/note_export.py` + `routers/notes.py:91-119` | 28-line duplicate | Extract to `services/note_export_service.py` |
| P1-03 | `jobs/email_sync.py` + `routers/emails.py:43-89` | 46-line duplicate | Extract to `services/email_sync_service.py` |
| P1-04 | `services/file_bridge.py:export_state()` | Defined, never called — `bridge/command_center_state.json` never written | Call from overview router or lifespan startup |
| P1-05 | All datetime usage | `datetime.utcnow()` (naive) used throughout | Replace with `datetime.now(timezone.utc)` |

### P2 — Security / quality

| ID | File | Issue | Fix |
|----|------|-------|-----|
| P2-01 | `backend/main.py:102-108` | CORS origins hardcoded; `allow_methods=["*"]` | Move origins to env var; restrict methods/headers |
| P2-02 | `backend/routers/emails.py:101` | Exception string returned to client | Log server-side; return generic message |
| P2-03 | `backend/services/gmail_service.py:202` | Silent `continue` on email parse failure | Log message ID and error before continuing |
| P2-04 | `backend/services/gmail_service.py:167` | From-header split on `<` is fragile | Use `email.headerparser.HeaderParser` |
| P2-05 | `.env.example:13` | Real email address exposed | Redact to `your.email@example.com` |
| P2-06 | `backend/main.py` | FastAPI auto-docs open without auth | Disable in production or gate behind middleware |
| P2-07 | `.github/workflows/ci.yml` | `pip-audit \|\| true` ignores CVEs | Remove `\|\| true` |

### P3 — Nice-to-have

| ID | Issue | Fix |
|----|-------|-----|
| P3-01 | `seed.py` 14KB hardcoded data | Extract to `seed_data.json` + thin loader |
| P3-02 | `repo_health.py` mutable global cache | Replace with DB row or module-level `threading.Lock` |
| P3-03 | `github_service.py:46` generator materialized unnecessarily | `next(repo.get_commits(), None)` |
| P3-04 | No retry logic on any external API | Add `tenacity` with exponential backoff |
| P3-05 | Zero tests | Create `tests/` with pytest; target happy + unreachable-API paths per router |
| P3-06 | No API auth | Add Bearer token middleware for production deployment |

---

## Grade Summary

| Component | Grade |
|-----------|-------|
| backend/main.py | B+ |
| jobs/email_sync.py | B- |
| jobs/note_export.py | A- |
| jobs/repo_health.py | B |
| services/ai_service.py | **C+** |
| services/gmail_service.py | A- |
| services/github_service.py | A |
| services/email_triage.py | A |
| services/file_bridge.py | A |
| services/model_router.py | B+ |
| routers/ai_router.py | B |
| routers/emails.py | B+ |
| routers/notes.py | B |
| routers/repos.py | B |
| routers/clients.py | A- |
| routers/pipeline.py | A |
| routers/overview.py | A |
| config.py / database.py / models/ | A |
| Test coverage | **F** |
| Security (internal deployment) | B+ |
| **OVERALL** | **C+** |

---

## Verification Checklist (post-fix)

1. `cd backend && uvicorn main:app --reload` — confirm all 5 jobs appear in scheduler startup log
2. `POST /api/emails/sync` — verify returned emails carry Gmail send dates, not sync time
3. `POST /api/ai/execute` — confirm no event-loop blocking under concurrent load
4. Wait 15 min — verify `bridge/email_digest.json` and `bridge/pending_notes.json` written
5. `GET /api/overview` — verify `bridge/command_center_state.json` written (after wiring `export_state()`)
6. `pytest tests/ -v` — target 0 failures
7. `uv run pip-audit` — 0 known CVEs (without `|| true`)
8. `deptry .` — 0 violations
