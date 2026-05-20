# Disaster Rescue Multi-Agent System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
![Backend](https://img.shields.io/badge/Backend-Symbolic%20FOL-orange)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
[![Contributing](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

> A multi-agent system for disaster rescue coordination powered by **First-Order Logic (FOL) symbolic agents**.
> Fully deterministic, zero external dependencies, runs in under one second.

---

## Overview

This project implements a multi-agent rescue coordination pipeline where three specialised robots are autonomously assigned to disaster tasks using symbolic reasoning. Every agent decision is governed by explicit **FOL axioms** — uniqueness, capability matching, priority ordering, and cost minimisation — making the system fully auditable and reproducible.

The system was designed as a study in reliability over flexibility. An earlier LLM-based version of the same pipeline demonstrated natural-language adaptability but suffered from non-determinism. This symbolic edition eliminates stochastic failures entirely while running orders of magnitude faster.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the simulation

```bash
python main.py
```

No environment configuration needed. The symbolic agents operate without any external AI backend.

---

## CLI Flags

```
--tasks        N            Generate N tasks (default: 10)
--seed         N            Random seed for reproducibility (default: 42)
--grid         N            Grid size NxN (default: 20)
--no-delay                  Skip simulated execution delays (faster demo)
--out          PATH         Output JSON path (default: auto under results/)
--interactive, -i           Run in interactive mode with parameter menu
```

**Examples:**

```bash
python main.py --tasks 15 --seed 7 --no-delay
python main.py --grid 30 --seed 99
python main.py --interactive
```

---

## Interactive Mode

```bash
python main.py --interactive
```

- **Live parameter adjustment** — change tasks, seed, grid size, delay, and output path without restarting
- **Random seed generator** — quickly test different scenarios with `[R]`
- **Auto-incrementing output** — `results/latest.json` always stays current; each run also saves a traceable file
- **Re-run simulation instantly** — experiment with different configurations

---

## Configuration

All constants live in `config.py`. No `.env` file or environment variables are required.

| Constant | Default | Description |
|---|---|---|
| `GRID_SIZE` | 20 | NxN disaster grid |
| `NUM_TASKS` | 10 | Tasks to generate per run |
| `RANDOM_SEED` | 42 | Reproducibility seed |
| `SPEED_VALUES` | fast=2.0, medium=1.0, slow=0.5 | Used in `Cost(r,t) = Distance(r,t) / Speed(r)` |
| `SPEED_DELAY` | fast=1s, medium=2s, slow=3s | Simulated execution time per task |

---

## Project Structure

```
disaster-rescue-multi-agent-system/
│
├── agents/
│   ├── base.py                    # BasePlannerAgent, BaseAssignmentAgent, BaseCriticAgent
│   │
│   └── fol/                       # Symbolic (FOL) implementations
│       ├── planner.py             # FOLPlannerAgent
│       ├── assignment.py          # FOLAssignmentAgent
│       └── critic.py              # FOLCriticAgent
│
├── report/
│   ├── index.html                 # Dashboard home page
│   ├── css/
│   │   └── styles.css             # Dashboard styles
│   ├── js/
│   │   └── app.js                 # Dashboard JavaScript
│   └── pages/
│       ├── tasks.html             # Detailed tasks view
│       ├── robots.html            # Detailed robots view
│       ├── metrics.html           # Detailed metrics view
│       ├── architecture.html      # System architecture docs
│       └── guide.html             # User guide
│
├── config.py                      # All constants & settings
├── environment.py                 # DisasterEnvironment class + FOL serialisation helpers
├── task_generator.py              # Task dataclass + generate_tasks()
├── robot_model.py                 # Robot dataclass + build_robot_fleet()
├── robot_agents.py                # RobotAgent execution engine
├── metrics.py                     # Evaluation metrics (incl. cost efficiency)
├── simulation.py                  # Full pipeline orchestration
├── results/                       # Output runs (auto-created)
│   ├── latest.json                # Dashboard data (latest run)
│   └── t*_g*_s*_*.json           # Individual traceable runs
├── main.py                        # CLI entry point
├── requirements.txt
├── report.md                      # Technical documentation
└── README.md
```

---

## Architecture

```
┌───────────────────────────────┐
│        BaseAgent ABCs         │  (agents/base.py)
│                               │
│  - BasePlannerAgent           │
│  - BaseAssignmentAgent        │
│  - BaseCriticAgent            │
└───────────────┬───────────────┘
                │ implements
                ▼
        agents/fol/
┌───────────────────────────────┐
│     Symbolic (FOL) Agents     │
│                               │
│  - FOLPlannerAgent            │
│  - FOLAssignmentAgent         │
│  - FOLCriticAgent             │
└───────────────┬───────────────┘
                │ used by
                ▼
┌───────────────────────────────┐
│        simulation.py          │
└───────────────────────────────┘
```

### FOL Constraints

| Axiom | Formula |
|---|---|
| Unique assignment | `∀t (Task(t) → ∃!r Assigned(t,r))` |
| Capability match | `∀t,r (Assigned(t,r) → Compatible(Type(t), Capability(r)))` |
| Priority order | `∀t1,t2 (Priority(t1) > Priority(t2) → ScheduledBefore(t1,t2))` |
| Cost formula | `Cost(r,t) = Distance(r,t) / Speed(r)` |

### Pipeline

```
1. generate_tasks()       →  randomised tasks with priorities & locations
2. FOLPlannerAgent        →  prioritised rescue plan (rule-based, deterministic)
3. FOLAssignmentAgent     →  task_id → robot_id mapping (min-cost, FOL-constrained)
4. FOLCriticAgent         →  validates & auto-corrects assignments
5. RobotAgent.execute()   →  simulates task completion
6. metrics.evaluate()     →  capability match, priority order, balance,
                              completion rate, cost efficiency
```

---

## HTML Dashboard

**1. Run the simulation** (JSON is generated automatically):

```bash
python main.py --no-delay
```

**2. Open the dashboard** in your browser:

```
report/index.html
```

### Dashboard Pages

| Page | Description |
|---|---|
| **Dashboard** (index.html) | Overview with all key data |
| **Tasks** | Detailed task list and catalogue info |
| **Robots** | Robot fleet details and statistics |
| **Metrics** | Performance scores with explanations |
| **Architecture** | System design and agent pipeline |
| **User Guide** | Setup instructions and troubleshooting |

### How it Works

```
python main.py  →  results/latest.json  →  Dashboard (HTML/JS)
      ↑                   ↑                        ↑
  Run simulation    Auto-generated           Reads JSON data
```

The dashboard is **semi-dynamic**: HTML/CSS/JS files are static, but data is loaded from `results/latest.json` at runtime. Run the simulation again and refresh the browser to see updated results.

To view a specific past run:

```
report/index.html?json=results/t10_g20_s42_20260505-1629_8ab42d.json
```

---

## Technical Report

See [`report.md`](report.md) for full technical documentation including agent design, evaluation metrics, results tables, and a comparison between symbolic and LLM-based approaches.

---

## Contributing

Contributions are welcome — bug fixes, new agent backends, tests, and documentation improvements. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branch naming, commit conventions, and PR guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
