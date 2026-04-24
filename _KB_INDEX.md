# Q-SMEC-Command-Center — Compute-at-Ingestion KB Index

**Protocol:** Karpathy compute-at-ingestion — canonical at `Q-SMEC-Claude/shared-memory/protocol_karpathy_compute_at_ingestion.md`
**Global roll-up:** `Q-SMEC-Claude/shared-memory/_GLOBAL_KB_INDEX.md`
**This file:** per-repo KB index for `Q-SMEC-Command-Center/`
**Scope:** Dashboard metric snapshots + SLA findings
**Created:** 2026-04-23 (skeleton)

---

## Scope

Command Center operational dashboard. Metric snapshots, SLA burns, alerting patterns, live frontend state.

Every new artifact landing in this repo (research return, script output, config change, data ingestion, vendor datasheet, pattern decision) is distilled into a Finding row here at ingestion — NOT left as raw text for future compute-at-query.

---

## Finding index (progressive — populate at each ingestion)

| # | Claim / finding | Topic / scope | Source | Confidence | Status |
|:-:|:----------------|:--------------|:-------|:----------:|:------:|

*(populate as ingestion events fire in this repo)*

---

## Cross-reference table

| Topic | Files / catalogs in this repo | Cross-repo KB pointers |
|:------|:------------------------------|:-----------------------|

*(populate as findings are cross-referenced)*

---

## Contradiction log

*(populate when new findings reframe prior ones — always include date + source)*

---

## Quick-reference cheat sheet

*(populate as recurring questions about this repo land)*

---

## How to extend

When a new artifact lands in this repo:

1. **Distill** atomic claims into Finding rows (claim · topic · source · confidence · status)
2. **Cross-reference** to adjacent artifacts (other files in this repo + other repos' KBs)
3. **Flag** contradictions with date + source
4. **Update** quick-reference cheat sheet if a 30-second answer to a recurring question changed
5. **Register** in `Q-SMEC-Claude/shared-memory/_GLOBAL_KB_INDEX.md` if cross-repo
6. **Commit** raw artifact + KB update together
7. **Propagate** to trackers (PROJECT_TRACKER, Ops Tracker, README) per `memory/feedback_meeting_critical_auto_propagate.md` if meeting-critical

<!-- KB-AUTOINGEST:BEGIN -->
### Auto-distilled findings — last update 2026-04-24T01:24:10+00:00

| # | claim | topic | source | confidence | gap |
|:-:|:------|:------|:-------|:----------:|:----|
| 1 | Emails total: 549, with 136 requiring action (24.8% action-required rate) | Email Workload | command_center_state.json `kpis.emails` | High | No target or SLA threshold defined for action-required rate | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/bridge/command_center_state.json -->
| 2 | Active clients: 7 of 14 total (50% activation rate) | Client Engagement | command_center_state.json `kpis.clients` | High | No target activation rate or trend direction specified | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/bridge/command_center_state.json -->
| 3 | Notes total: 0, pending: 0 — no notes recorded in system | Notes Capture | command_center_state.json `kpis.notes` | High | Gap: zero notes may indicate unused feature or data not yet populated | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/bridge/command_center_state.json -->
| 4 | Pipeline contains 23 use cases with average progress of 29.1% | Pipeline Progress | command_center_state.json `kpis.pipeline` | High | No target avg_progress or completion SLA defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/bridge/command_center_state.json -->
| 5 | Pipeline phase distribution: 22 UCs in Phase 0, 1 UC in Phase 1 — 95.7% still in earliest phase | Pipeline Phase Concentration | command_center_state.json `pipeline_summary` | High | No phase advancement targets or SLA timelines provided | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/bridge/command_center_state.json -->
| 6 | Repository count: 18; tracked elements: 32 | Asset Inventory | command_center_state.json `kpis.repos` / `kpis.elements` | High | No target repo count, element coverage ratio, or SLA status available | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/bridge/command_center_state.json -->
| 7 | api-key-expiry agent ran 1/1 times OK in 24 h; checked=3 keys, invalid=0 | API Key Health | agent-state.json › api-key-expiry | High | No expiry dates or days-to-expiry surfaced | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 8 | backup-verifier ran 1/1 times OK; checked=26 backups, corrupt=0 | Backup Integrity | agent-state.json › backup-verifier | High | No backup age or restore-test latency reported | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 9 | business-activity agent: 19 projects tracked, 0 active, 19 stale, 774 overdue commits | Project Health | agent-state.json › business-activity | High | All 19 projects stale; no SLA or escalation threshold defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 10 | ci-watchdog-agent ran 142 times in 24 h with 0 OK / 0 failed; currently RUNNING | CI Pipeline Monitoring | agent-state.json › ci-watchdog-agent | Medium | No OK completions recorded; unclear if runs are succeeding silently or stuck | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 11 | confidence-tag-auditor: 4/4 runs PARTIAL; repos=9, violations=1 | Metadata Quality | agent-state.json › confidence-tag-auditor | High | Specific repo and tag causing violation not identified | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 12 | config-drift agent: 4/4 runs PARTIAL; drifts=2 detected | Configuration Drift | agent-state.json › config-drift | High | Which services drifted and remediation status not specified | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 13 | container-health-agent: 138 runs, COMPLETED_WITH_ERRORS; 12 containers probed, 9 errors | Container Health | agent-state.json › container-health-agent | High | 75% container error rate; no container names or error types surfaced | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 14 | dashboard-writer: 40 runs, 39 OK, currently RUNNING; 1 run unaccounted | Dashboard Reliability | agent-state.json › dashboard-writer | Medium | 1 run not classified as OK or failed | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 15 | database-health: 141/141 runs PARTIAL; probes=4, fails=1 (25% probe failure rate) | Database Reliability | agent-state.json › database-health | High | Failing probe identity and duration of degradation unknown | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 16 | dependabot-triage: scanned=18 of 283 total deps; crit=8, high=79, low=20 vulnerabilities | Dependency Security | agent-state.json › dependabot-triage | High | Only 18/283 deps scanned; 87 crit+high vulns unpatched | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 17 | email-triage: 118 runs in 24 h, only 25 OK; currently RUNNING | Email Processing | agent-state.json › email-triage | Medium | 93 runs not OK; no volume or error breakdown provided | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 18 | git-hygiene: 23 runs, 22 OK, 1 PARTIAL; hardened=17/17 repos | Git Security | agent-state.json › git-hygiene | High | 1 PARTIAL run not explained; no detail on what hardening entails | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 19 | handoff-integrity: 1/1 OK; ucs=23 checked, mismatches=0, missing=0 | Handoff Quality | agent-state.json › handoff-integrity | High | No definition of UCS or what constitutes a mismatch | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 20 | kb-index-updater: 3 runs in 24 h, 0 OK, currently RUNNING; no summary available | Knowledge Base Indexing | agent-state.json › kb-index-updater | Low | No completed run with output; possible stall | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 21 | literature-sentinel: new=31 papers ingested, dup=469 filtered; sources=5, topics=28 | Research Monitoring | agent-state.json › literature-sentinel | High | No relevance scoring or downstream routing of new papers noted | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 22 | Total emails in system: 3,904 with 3,458 triaged (88.6% triage rate) and 76 unclassified | Email Triage Coverage | email-state.json · generated_at 2026-04-23 | High | Target triage rate and SLA threshold not defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 23 | Largest triage category is "action" with 1,036 emails (30.0% of triaged), followed by "noise" at 1,017 (29.4%) | Email Category Distribution | email-state.json · by_triage_category | High | No age/staleness data per category; unclear how many actions are resolved | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 24 | 99 emails classified as "critical" urgency and 1,100 as "high" urgency out of 3,904 total (30.7% high+critical) | Urgency Distribution | email-state.json · by_urgency | High | No SLA defined for critical/high email response time | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 25 | 6,047 open commits tracked system-wide with 2,000 overdue (33.1% overdue rate) | Commit Backlog Health | email-state.json · open_commits / overdue_commits | High | No target overdue rate or resolution velocity defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 26 | Largest commit kind is "deliverable" at 2,255 followed by "meeting" at 2,007; payment commits at 126 | Commit Type Breakdown | email-state.json · commits_by_kind | High | No per-kind overdue breakdown provided | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 27 | Oldest overdue commit dates to 2023-01-20 (CII JMTC Weekly Zoom Meeting, owner: Alex Dely) — over 3 years past due | Overdue Commit Age / Staleness | email-state.json · overdue_list | High | System appears to retain resolved/cancelled items as still-overdue; data quality risk | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 28 | 15 overdue items listed all belong to 2023 due dates, spanning PROJ-CII-JMTC-WEEKLY-OPS and DEMO-JMTC-DOW-WHITE-PAPERS primarily | Overdue Commit Project Concentration | email-state.json · overdue_list | High | No indication whether these are acknowledged, stale artifacts, or genuinely unresolved | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 29 | Top project by email volume is PROJ-TEP-ENERGY-VERTICAL at 364 emails, but emails_7d = 0 for all top 15 projects | Project Activity (7-Day) | email-state.json · top_projects | High | Zero 7-day activity across all top projects suggests ingestion pipeline may be stalled or snapshot is stale | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 30 | Claude triage engine processed 3,375 emails vs Ollama at 83 (97.6% Claude share) | Triage Engine Distribution | email-state.json · by_triage_engine | High | No fallback SLA or cost-per-email benchmark defined for engine selection | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 31 | Daily AI triage cost is $27.86 across 24 runs (~$1.16 per run) | Operational Cost | email-state.json · cost_today | High | No budget ceiling or cost-per-email target defined; monthly run rate implied ~$835/month | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 32 | NIKET entity tag holds 1,619 emails (41.5%), CII 1,234 (31.6%), Joint 603 (15.4%) of triaged corpus | Entity Tag Distribution | email-state.json · by_entity_tag | High | 446 emails (11.4%) carry no entity tag; routing coverage incomplete | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 33 | "risk" category contains 168 emails with no visibility into how many are open, acknowledged, or escalated | Risk Email Backlog | email-state.json · by_triage_category | Medium | No risk-resolution workflow or SLA tracked in this snapshot | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 34 | Recent triage stream (last ~3 minutes) shows heavy concentration on "TIME-SENSITIVE: FCD Symposium / Quantum Sensing Brief" with multiple critical/high urgency re-triages of same subject | Duplicate / Re-triage Pattern | email-state.json · recent_triage | High | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 35 | ci-watchdog-agent ran 142 times in 24 h with 0 OK, 0 partial, 0 failed — all runs logged as RUNNING, never completing | Agent Health | agent-state.json / ci-watchdog-agent | High | No terminal status recorded; unclear if agent is stuck or intentionally long-running | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 36 | container-health-agent reports 9 errors out of 12 containers (75% error rate) on last probe | Infrastructure Health | agent-state.json / container-health-agent | High | No container names or error types surfaced; severity of errors unknown | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 37 | database-health agent recorded PARTIAL status on all 141 runs in 24 h with probes=4 fails=1 (25% probe failure rate) | Database Health | agent-state.json / database-health | High | Which database probe is failing and since when is not specified | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 38 | confidence-tag-auditor shows PARTIAL on all 4 runs with 1 violation across 9 repos | Code Quality | agent-state.json / confidence-tag-auditor | High | Identity of the violating repo and nature of violation not specified | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 39 | config-drift agent shows PARTIAL on all 4 runs with drifts=2 detected | Configuration Management | agent-state.json / config-drift | High | Which services or configs are drifted and drift severity not identified | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 40 | business-activity agent reports 19 stale projects, 0 active, and 774 overdue commits | Project Management | agent-state.json / business-activity | High | No breakdown of which projects are stale or commit age distribution | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 41 | dependabot-triage finds 8 critical and 79 high vulnerabilities across 18 scanned repos (total=283 advisories) | Security | agent-state.json / dependabot-triage | High | Critical vuln identities and affected repos not surfaced | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 42 | secret-scan-sentinel reports 113 total secret findings across 18 repos with 0 new in latest scan | Security | agent-state.json / secret-scan-sentinel | High | Whether existing 113 findings are remediated or accepted-risk is not stated | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 43 | obsidian-sync reports 528 broken links out of 537 notes (98.3% broken link rate) despite OK status | Knowledge Base Integrity | agent-state.json / obsidian-sync | High | Root cause of mass broken links and whether this is a known migration artifact is unstated | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 44 | message bus carries 4,295 CRIT messages vs 352 WARN and 162 INFO — CRIT outnumbers INFO by 26:1 | System-Wide Alerting | agent-state.json / messages | High | No mapping of CRIT messages to specific agents or incidents provided | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 45 | master-orchestrator identifies 7 silent agents out of 27 tracked in latest run | Agent Health | agent-state.json / master-orchestrator | High | Identities of the 7 silent agents not listed in this file | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 46 | workspace-hygiene consistently OK across all 48 runs but reports 15 Python orphans and 2 git locks persisting | Workspace Cleanliness | agent-state.json / workspace-hygiene | Medium | Whether orphans and locks are growing or stable over time is not tracked here | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 47 | email-triage processed only 55 OK out of 147 runs (37.4% OK rate) with remaining runs having no recorded terminal status | Automation Reliability | agent-state.json / email-triage | Medium | Status of the 92 non-OK runs is not classified as partial or failed | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 48 | session-log-autowriter reports 20 unresolved items across 462 agent runs and 34 commits at last run | Project Tracking | agent-state.json / session-log-autowriter | Medium | Nature and age of unresolved items not specified | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 49 | kb-index-updater shows 0 OK out of 4 runs in 24 h with status perpetually RUNNING and no summary output | Agent Health | agent-state.json / kb-index-updater | Medium | Whether indexing is genuinely in progress or hung cannot be determined from this file | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 50 | Total emails in system: 3,904 with 3,903 triaged (99.97% triage rate) | Email Triage Coverage | email-state.json | High | 1 unclassified email remains outstanding | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 51 | Largest triage category is "noise" at 1,162 emails (29.8% of total) | Email Signal-to-Noise Ratio | email-state.json | High | No target set for noise reduction | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 52 | "Action" emails total 1,123 (28.8%); "risk" emails total 180 (4.6%); "deal" emails total 203 (5.2%) | Email Category Distribution | email-state.json | High | No SLA defined for action/risk/deal response times | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 53 | Critical-urgency emails: 104; High-urgency: 1,118; combined critical+high = 1,222 (31.3% of total) | Email Urgency Distribution | email-state.json | High | No response SLA targets defined for critical or high urgency | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 54 | NIKET entity owns 1,816 emails (46.5%); CII owns 1,388 (35.6%); Joint owns 697 (17.9%) | Email Load by Entity | email-state.json | High | No load-balancing targets or entity-level SLAs defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 55 | Claude engine processed 3,809 of 3,903 triaged emails (97.6%); Ollama processed 94 (2.4%) | Triage Engine Distribution | email-state.json | High | No failover threshold or engine-mix target defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 56 | Top project PROJ-TEP-ENERGY-VERTICAL holds 410 emails; emails_7d = 0 across ALL top 15 projects | Project Email Activity (7-day) | email-state.json | High | Zero recent activity across all tracked projects — pipeline stall risk | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 57 | Open commits: 6,754; Overdue commits: 2,247 (33.3% overdue rate) | Commit Backlog & Overdue Rate | email-state.json | High | No target overdue rate defined; 33% overdue is a critical operational gap | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 58 | Largest commit kinds: deliverable 2,503; meeting 2,263; review 698; research 620 | Commit Type Distribution | email-state.json | High | No per-kind completion rate or aging targets defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 59 | Earliest overdue commit dates back to 2023-01-20 — over 3 years overdue (CII JMTC Weekly Zoom) | Commit Age / Staleness | email-state.json | High | No archival or escalation policy for commits aged >90 days | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 60 | 15 sampled overdue commits span 2023-01-20 to 2023-11-05; all are meetings or presentations | Overdue Commit Category Skew | email-state.json | High | Meeting-type commits dominate overdue list with no remediation workflow | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 61 | Supabase Project "Niket 2026" pause warning appears twice in recent triage as high-urgency risk | Repeated High-Risk Alert (Supabase) | email-state.json | High | Duplicate risk signals suggest no deduplication in triage pipeline | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 62 | AI triage cost today: $1.475 USD across 26 runs (~$0.057 per run) | Daily AI Triage Cost | email-state.json | High | No daily cost budget ceiling or per-run cost target defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 63 | Most recent triage batch (last 20 items) is 85% noise or FYI; only 2 action + 2 risk items | Recent Triage Signal Quality | email-state.json | High | High noise throughput consuming AI budget with low actionable yield | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 64 | CI watchdog agent ran 142 times in 24 h with 0 OK runs; last status COMPLETED_WITH_UNKNOWNS with 10 unclassified items | CI pipeline observability | agent-state.json › ci-watchdog-agent | High | Unknown classification rate (10/24 classified) needs root-cause; no SLA pass in 24 h | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 65 | Container health agent ran 138 times with 0 OK runs; last probe found 9 errors across 12 containers | Container reliability | agent-state.json › container-health-agent | High | 75 % container error rate persists; no remediation evidence in state | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 66 | Database health agent ran 141 times with all 141 runs PARTIAL; last probe shows 1 failure in 4 probes | Database availability | agent-state.json › database-health | High | 100 % partial-run rate over 24 h indicates chronic probe failure; specific failing probe unidentified | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 67 | Config-drift agent ran 4 times with all 4 PARTIAL; 2 active drifts detected | Infrastructure config integrity | agent-state.json › config-drift | High | Drifts unresolved across all 4 runs; no OK state achieved in 24 h | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 68 | Confidence-tag-auditor ran 4 times all PARTIAL; 1 violation across 9 repos | Code metadata quality | agent-state.json › confidence-tag-auditor | Medium | Persistent PARTIAL status suggests auditor itself may be misconfigured, not just the violation | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 69 | Dependabot triage reports 8 critical and 79 high CVEs across 18 scanned repos (283 total) | Dependency vulnerability exposure | agent-state.json › dependabot-triage | High | Critical CVE remediation timeline and ownership not visible in this state | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 70 | LLM cost sentinel reports $499.07 spend in one day; claude_in=347 636 tokens, claude_out=463 035 tokens | AI operational cost | agent-state.json › llm-cost-sentinel | High | Daily run rate of ~$499 projects to ~$15 000/month; no budget ceiling or alert threshold visible | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 71 | Secret-scan-sentinel found 113 cumulative findings across 18 repos; 0 new in last run | Secrets exposure | agent-state.json › secret-scan-sentinel | High | 113 existing findings remain unresolved; remediation backlog age unknown | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 72 | Business-activity agent shows 19 projects tracked, 0 active, 19 stale, 774 overdue commits | Project delivery health | agent-state.json › business-activity | High | 100 % project staleness and 774 overdue commits indicates systemic delivery blockage | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 73 | Obsidian-sync reports 528 broken links out of 537 notes (98.3 % broken-link rate) | Knowledge base integrity | agent-state.json › obsidian-sync | High | Near-total link graph corruption makes KB navigation unreliable; not flagged as non-OK | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 74 | Message bus holds 4 346 CRIT messages, 358 WARN, and 165 INFO outstanding | System alert backlog | agent-state.json › messages | High | 4 346 unprocessed CRIT messages implies alert fatigue or consumer lag; no drain rate provided | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 75 | Master orchestrator reports 7 silent agents out of 27 tracked despite 0 failing | Agent fleet coverage | agent-state.json › master-orchestrator | Medium | Silent agents may represent blind spots; identities of 7 silent agents not enumerated in state | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 76 | Workspace-hygiene detects 15 Python orphan files and 1 git lock file persisting | Workspace cleanliness | agent-state.json › workspace-hygiene | Medium | Git lock file could block concurrent git operations; orphan accumulation trend unknown | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 77 | Email-triage ran 148 times but only 60 OK; last run classified 0 emails with $0.00 LLM cost | Email automation effectiveness | agent-state.json › email-triage | Medium | 88 non-OK runs unexplained; zero classification | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/agent-state.json -->
| 78 | Total emails triaged: 3,904 of 3,904 (100% triage rate, 0 unclassified) | Email Triage Coverage | email-state.json › email.total / email.triaged | High | No target defined for triage SLA or cycle time | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 79 | Largest triage category is noise: 1,162 emails (29.8% of total) | Email Signal Quality | email-state.json › email.by_triage_category[noise] | High | No noise-reduction target or threshold defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 80 | Action-required emails: 1,124 (28.8% of total) | Actionable Email Volume | email-state.json › email.by_triage_category[action] | High | No SLA defined for action item response time | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 81 | Critical-urgency emails: 104 (2.7% of total); high-urgency: 1,119 (28.7%) | Email Urgency Distribution | email-state.json › email.by_urgency | High | No escalation SLA or owner-assignment rule defined for critical items | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 82 | Open commits: 6,754; overdue commits: 2,247 (33.3% overdue rate) | Commit Backlog Health | email-state.json › email.open_commits / email.overdue_commits | High | No target overdue rate defined; no velocity trend data present | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 83 | Oldest overdue commit dates to 2023-01-20 — over 3 years past due | Commit Age / Staleness | email-state.json › email.overdue_list[0].due | High | No automated aging or escalation policy visible | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 84 | Deliverable commits: 2,503 (largest kind); meeting commits: 2,263 | Commit Type Distribution | email-state.json › email.commits_by_kind | High | No per-kind completion rate or SLA target defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 85 | NIKET entity owns 1,817 emails (46.5%); CII owns 1,388 (35.6%); Joint 697 (17.9%) | Entity Email Load Distribution | email-state.json › email.by_entity_tag | High | No entity-level workload balance target defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 86 | Top project PROJ-TEP-ENERGY-VERTICAL: 410 total emails, 0 emails in last 7 days | Project Activity — Energy Vertical | email-state.json › email.top_projects[0] | High | emails_7d = 0 across all 15 listed projects — possible ingestion gap or pipeline stall | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 87 | All 15 top projects report emails_7d = 0 — no recent email activity on any project | Email Ingestion Freshness | email-state.json › email.top_projects[*].emails_7d | High | Data generated 2026-04-24; zero recent activity across all projects is anomalous and unresolved | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 88 | Claude engine processed 3,810 of 3,904 emails (97.6%); Ollama handled 94 (2.4%) | Triage Engine Distribution | email-state.json › email.by_triage_engine | High | No fallback policy or engine-failure SLA defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 89 | AI triage cost today: $1.475 USD across 30 runs (~$0.049/run average) | Triage AI Cost Efficiency | email-state.json › cost_today | High | No daily cost budget or per-run cost target defined | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 90 | Risk-category emails: 180 total; 2 recent high-urgency risk items involve Supabase project pause | Active Risk Signal — Infrastructure | email-state.json › email.by_triage_category[risk] + recent_triage | High | No risk-to-owner assignment or resolution tracking visible | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
| 91 | Opportunity emails: 542 (13.9% of total); deal emails: 203 (5.2%) | Pipeline Signal Volume | email-state.json › email.by_triage_category[opportunity/deal] | High | No conversion or follow-up rate tracked against opportunity/deal emails | <!-- src: /mnt/e/Data1/Q-SMEC-Command-Center/frontend/live/email-state.json -->
<!-- KB-AUTOINGEST:END -->
