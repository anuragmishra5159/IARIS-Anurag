# IARIS — v1 Requirements

## v1 Requirements

### Process Monitoring
- [ ] **MON-01**: System can discover and list all running processes with PID, name, CPU%, memory%, I/O counters
- [ ] **MON-02**: System samples process metrics at 1-second intervals with <0.3% CPU overhead
- [ ] **MON-03**: System gracefully handles process termination mid-scan (NoSuchProcess, AccessDenied)
- [ ] **MON-04**: System works identically on Windows native and Linux/WSL

### Dummy Process Simulator
- [ ] **SIM-01**: User can spawn dummy processes that simulate CPU-hog behavior (sustained high CPU)
- [ ] **SIM-02**: User can spawn dummy processes that simulate latency-sensitive behavior (short bursts, fast response)
- [ ] **SIM-03**: User can spawn dummy processes that simulate bursty behavior (periodic spikes)
- [ ] **SIM-04**: User can spawn dummy processes that simulate blocking/I/O-wait behavior
- [ ] **SIM-05**: User can spawn dummy processes that simulate memory-heavy behavior
- [ ] **SIM-06**: Dummy processes can be started/stopped via CLI commands

### Behavior Classification
- [ ] **BHV-01**: System classifies processes into behavior types: cpu_hog, latency_sensitive, bursty, blocking, memory_heavy, idle
- [ ] **BHV-02**: Classification updates dynamically as process behavior changes over time
- [ ] **BHV-03**: System generates a behavior signature hash for each process (hash of name + usage pattern + behavior type)

### Scoring & Decision Engine
- [ ] **SCR-01**: System computes an allocation score for each process: allocationScore = f(behavior, systemState, signals)
- [ ] **SCR-02**: Scoring considers process behavior type, current system state, and workload membership
- [ ] **SCR-03**: System produces resource allocation decisions (throttle, boost, maintain, pause) based on scores

### Learning System
- [ ] **LRN-01**: System maintains EWMA-based behavior profiles: newScore = 0.3 × observation + 0.7 × oldScore
- [ ] **LRN-02**: Behavior profiles persist across sessions via SQLite knowledge base
- [ ] **LRN-03**: System recognizes returning processes by behavior signature and applies learned profiles
- [ ] **LRN-04**: Cold-start recipes (JSON files) provide initial behavior hints for known process types

### System State Machine
- [ ] **SYS-01**: System detects overall state: Stable (normal load), Pressure (elevated resource usage), Critical (near exhaustion)
- [ ] **SYS-02**: State transitions trigger behavioral changes: Balanced (stable) → Protective (pressure) → Aggressive (critical)
- [ ] **SYS-03**: State thresholds are configurable via JSON config

### Workload Coordination
- [ ] **WRK-01**: User can define workload groups (e.g., "web-service" = [api, database, cache]) via config
- [ ] **WRK-02**: System prioritizes workload-level goals over individual process goals
- [ ] **WRK-03**: System detects and resolves resource conflicts between workloads

### Reasoning Engine
- [ ] **RSN-01**: System generates natural language explanations for every allocation decision
- [ ] **RSN-02**: Explanations reference specific behavior data and system state that triggered the decision
- [ ] **RSN-03**: Reasoning log is accessible via API and displayed in both CLI and web dashboard

### API Layer
- [ ] **API-01**: FastAPI server exposes REST endpoints for system state, process list, workloads, decisions, reasoning
- [ ] **API-02**: WebSocket endpoint streams real-time updates (metrics, state changes, decisions) to connected clients
- [ ] **API-03**: API supports starting/stopping dummy processes
- [ ] **API-04**: API supports configuring workload groups and system thresholds

### CLI Dashboard
- [ ] **CLI-01**: Terminal dashboard shows real-time system state panel (CPU, memory, I/O, state indicator)
- [ ] **CLI-02**: Terminal dashboard shows process list with behavior classification and allocation scores
- [ ] **CLI-03**: Terminal dashboard shows workload groups and their status
- [ ] **CLI-04**: Terminal dashboard shows reasoning panel with latest decisions and explanations
- [ ] **CLI-05**: Terminal dashboard updates in real-time (1-second refresh)

### Web Dashboard
- [ ] **WEB-01**: React web dashboard shows system state panel with CPU/memory/I/O gauges
- [ ] **WEB-02**: Web dashboard shows time-series charts of resource usage (last 5 minutes)
- [ ] **WEB-03**: Web dashboard shows process list with behavior types and live scoring
- [ ] **WEB-04**: Web dashboard shows workload topology view
- [ ] **WEB-05**: Web dashboard shows reasoning timeline with decision explanations
- [ ] **WEB-06**: Web dashboard connects via WebSocket for real-time updates
- [ ] **WEB-07**: Web dashboard has controls to spawn/stop dummy processes

### Demo Flow
- [ ] **DEM-01**: User can run a scripted demo: baseline → add heavy workload → observe degradation → enable IARIS → show improvement
- [ ] **DEM-02**: Demo shows clear before/after metrics comparison
- [ ] **DEM-03**: Demo displays reasoning explanations for automated decisions

## v2 Requirements (Deferred)
- [ ] Real process control via nice/renice/cpulimit/kill on Linux
- [ ] Real process priority control via psutil on Windows
- [ ] Temporal pattern detection and predictive pre-allocation
- [ ] Multi-resource optimization (CPU + memory + I/O jointly)
- [ ] Distributed cross-node resource balancing
- [ ] Historical trend analysis and reporting

## Out of Scope
- **Kernel-level scheduling** — Too risky, not cross-platform
- **GPU management** — Different domain entirely
- **Network traffic shaping** — Too OS-specific
- **Container orchestration** — Out of scope for demo
- **Machine learning model training** — EWMA is sufficient for v1
- **Production security hardening** — Hackathon demo only

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| MON-01 | Phase 1 | Pending |
| MON-02 | Phase 1 | Pending |
| MON-03 | Phase 1 | Pending |
| MON-04 | Phase 1 | Pending |
| SIM-01 | Phase 2 | Pending |
| SIM-02 | Phase 2 | Pending |
| SIM-03 | Phase 2 | Pending |
| SIM-04 | Phase 2 | Pending |
| SIM-05 | Phase 2 | Pending |
| SIM-06 | Phase 2 | Pending |
| BHV-01 | Phase 3 | Pending |
| BHV-02 | Phase 3 | Pending |
| BHV-03 | Phase 3 | Pending |
| SCR-01 | Phase 3 | Pending |
| SCR-02 | Phase 3 | Pending |
| SCR-03 | Phase 3 | Pending |
| LRN-01 | Phase 3 | Pending |
| LRN-02 | Phase 3 | Pending |
| LRN-03 | Phase 3 | Pending |
| LRN-04 | Phase 3 | Pending |
| SYS-01 | Phase 3 | Pending |
| SYS-02 | Phase 3 | Pending |
| SYS-03 | Phase 3 | Pending |
| WRK-01 | Phase 4 | Pending |
| WRK-02 | Phase 4 | Pending |
| WRK-03 | Phase 4 | Pending |
| RSN-01 | Phase 4 | Pending |
| RSN-02 | Phase 4 | Pending |
| RSN-03 | Phase 4 | Pending |
| API-01 | Phase 5 | Pending |
| API-02 | Phase 5 | Pending |
| API-03 | Phase 5 | Pending |
| API-04 | Phase 5 | Pending |
| CLI-01 | Phase 6 | Pending |
| CLI-02 | Phase 6 | Pending |
| CLI-03 | Phase 6 | Pending |
| CLI-04 | Phase 6 | Pending |
| CLI-05 | Phase 6 | Pending |
| WEB-01 | Phase 7 | Pending |
| WEB-02 | Phase 7 | Pending |
| WEB-03 | Phase 7 | Pending |
| WEB-04 | Phase 7 | Pending |
| WEB-05 | Phase 7 | Pending |
| WEB-06 | Phase 7 | Pending |
| WEB-07 | Phase 7 | Pending |
| DEM-01 | Phase 7 | Pending |
| DEM-02 | Phase 7 | Pending |
| DEM-03 | Phase 7 | Pending |

**Coverage:**
- v1 requirements: 37 total
- Mapped to phases: 37
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-13*
*Last updated: 2026-04-13 after roadmap creation*
