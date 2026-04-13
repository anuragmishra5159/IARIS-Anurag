<!-- GSD:project-start source:PROJECT.md -->
## Project

**IARIS — Intent-Aware Adaptive Resource Intelligence System**

IARIS is a behavior-driven, learning-based framework for intelligent resource allocation across computing systems. It replaces static priority scheduling with dynamic intent inference — observing process behavior, learning patterns over time, and allocating CPU, memory, I/O, and network resources based on context and impact rather than fixed rules. It targets both Windows (native) and Linux (WSL) environments, with a CLI dashboard and web-based visual interface.

**Core Value:** Allocate resources based on observed behavior, context, and system-wide impact — not fixed rules — and explain every decision transparently.

### Constraints

- **Timeline**: 1 week — must be demo-ready by end of week
- **Platform**: Must work on Windows natively and on Linux/WSL
- **Overhead**: Engine must consume <0.3% CPU with 1-second sampling
- **Dependencies**: Python ecosystem only (psutil, FastAPI, SQLite) — no heavy frameworks
- **Process control**: v1 uses dummy processes only; real process control deferred
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack (2025)
### Core Engine
| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| Language | Python | 3.11+ | ★★★★★ | Best psutil support, rapid prototyping, cross-platform |
| Process Monitoring | psutil | 5.9+ | ★★★★★ | Industry standard, cross-platform (Win+Linux), mature API |
| Async Runtime | asyncio | stdlib | ★★★★★ | Native to Python, required by Textual and FastAPI |
### Learning & Storage
| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| Knowledge Base | SQLite | stdlib | ★★★★★ | Zero-config, file-based, perfect for hackathon |
| In-Memory Cache | dict + dataclasses | stdlib | ★★★★★ | Hot data path, no external dependency |
| Serialization | JSON | stdlib | ★★★★★ | Human-readable recipes, config files |
### CLI Dashboard
| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| TUI Framework | Rich + Textual | 0.50+ | ★★★★☆ | Best Python TUI framework, async-native, beautiful output |
| CLI Args | typer | 0.9+ | ★★★★☆ | Clean CLI interface, built on Click |
### Web Dashboard
| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| Backend API | FastAPI | 0.100+ | ★★★★★ | Async, WebSocket support, auto-docs, Python-native |
| Real-time Comm | WebSocket | native | ★★★★★ | Bidirectional, low-latency updates |
| Frontend | React 18 | 18.2+ | ★★★★★ | Rich ecosystem, good for real-time data viz |
| Charts | Recharts | 2.x | ★★★★☆ | React-native charting, great for time-series |
| Build Tool | Vite | 5.x | ★★★★★ | Fast dev server, modern bundling |
### What NOT to Use
- **Django** — Too heavy for a real-time monitoring system
- **Flask** — No native async/WebSocket support
- **Kubernetes/Docker** — Adds complexity without value for v1 dummy processes
- **Prometheus/Grafana** — Overkill; we need custom behavior analysis, not generic metrics
- **curses** — Low-level; Rich/Textual provides much better abstractions
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
