# Roadmap: IARIS v1.0

**Created:** 2026-04-13
**Milestone:** v1.0 — Hackathon Demo
**Phases:** 7
**Requirements:** 37 mapped

## Phase Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Core Monitor & Project Setup | Process monitoring foundation with cross-platform support | MON-01..04 | 4 |
| 2 | Dummy Process Simulator | Synthetic workloads for testing and demo | SIM-01..06 | 4 |
| 3 | Behavior & Intelligence Engine | Classification, scoring, EWMA learning, state machine | BHV-01..03, SCR-01..03, LRN-01..04, SYS-01..03 | 5 |
| 4 | Workload & Reasoning | Workload coordination and explainable decisions | WRK-01..03, RSN-01..03 | 4 |
| 5 | API Layer | FastAPI REST + WebSocket server | API-01..04 | 3 |
| 6 | CLI Dashboard | Rich terminal UI with Textual | CLI-01..05 | 4 |
| 7 | Web Dashboard & Demo | React web dashboard with demo flow | WEB-01..07, DEM-01..03 | 5 |

## Phase Details

### Phase 1: Core Monitor & Project Setup
**Goal:** Build the process monitoring foundation that everything depends on. Set up the Python project structure with cross-platform psutil monitoring.

**Requirements:** MON-01, MON-02, MON-03, MON-04

**UI hint**: no

**Success criteria:**
1. Python project initializes with proper package structure and dependencies
2. Process monitor discovers all running processes with PID, name, CPU%, memory%, I/O
3. Monitor samples at 1-second intervals with measured overhead <0.3%
4. Same code runs identically on Windows native and Linux/WSL

---

### Phase 2: Dummy Process Simulator
**Goal:** Create synthetic processes that exhibit distinct resource usage patterns for testing and demo purposes.

**Requirements:** SIM-01, SIM-02, SIM-03, SIM-04, SIM-05, SIM-06

**UI hint**: no

**Success criteria:**
1. Can spawn CPU-hog, latency-sensitive, bursty, and blocking dummy processes
2. Each dummy process generates measurably different resource patterns
3. Dummy processes can be started and stopped via CLI commands
4. Monitor correctly detects and tracks dummy processes

---

### Phase 3: Behavior & Intelligence Engine
**Goal:** Build the core intelligence — behavior classification, allocation scoring, EWMA learning, and system state detection.

**Requirements:** BHV-01, BHV-02, BHV-03, SCR-01, SCR-02, SCR-03, LRN-01, LRN-02, LRN-03, LRN-04, SYS-01, SYS-02, SYS-03

**UI hint**: no

**Success criteria:**
1. Processes are classified into behavior types (cpu_hog, latency_sensitive, bursty, blocking, memory_heavy, idle)
2. Allocation scores are computed using behavior + system state + signals
3. EWMA profiles update correctly and persist across sessions in SQLite
4. System state transitions (Stable → Pressure → Critical) trigger behavioral changes
5. Cold-start recipes load from JSON and provide initial behavior hints

---

### Phase 4: Workload & Reasoning
**Goal:** Add workload abstraction (group processes) and natural language reasoning that explains every decision.

**Requirements:** WRK-01, WRK-02, WRK-03, RSN-01, RSN-02, RSN-03

**UI hint**: no

**Success criteria:**
1. Workload groups can be defined via config and processes are correctly assigned
2. Workload-level goals override individual process priorities during conflicts
3. Every allocation decision generates a natural language explanation
4. Explanations reference specific metrics and state that triggered the decision

---

### Phase 5: API Layer
**Goal:** Expose the IARIS engine via FastAPI with REST endpoints and WebSocket streaming.

**Requirements:** API-01, API-02, API-03, API-04

**UI hint**: no

**Success criteria:**
1. REST endpoints return system state, process list, workloads, decisions, reasoning
2. WebSocket endpoint streams real-time updates at 1-second intervals
3. API supports starting/stopping dummy processes and configuring thresholds

---

### Phase 6: CLI Dashboard
**Goal:** Build a rich terminal dashboard using Textual that displays real-time system monitoring.

**Requirements:** CLI-01, CLI-02, CLI-03, CLI-04, CLI-05

**UI hint**: yes

**Success criteria:**
1. Terminal dashboard shows system state panel with live CPU/memory/I/O and state indicator
2. Process list displays with behavior classification and allocation scores
3. Workload groups and reasoning panel display correctly
4. Dashboard updates in real-time at 1-second intervals

---

### Phase 7: Web Dashboard & Demo
**Goal:** Build the React web dashboard with charts, workload visualization, and the complete demo flow.

**Requirements:** WEB-01, WEB-02, WEB-03, WEB-04, WEB-05, WEB-06, WEB-07, DEM-01, DEM-02, DEM-03

**UI hint**: yes

**Success criteria:**
1. Web dashboard shows system gauges, time-series charts, and process list
2. Workload topology and reasoning timeline display correctly
3. WebSocket connection provides real-time updates
4. Demo flow runs end-to-end: baseline → load → degrade → IARIS → improve → explain
5. Before/after comparison is visually clear and compelling
