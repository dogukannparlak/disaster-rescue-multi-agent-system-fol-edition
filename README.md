# Disaster Rescue Multi-Agent System — HW2

> A multi-agent system for disaster rescue coordination powered by **FOL-based (First-Order Logic / Symbolic Reasoning) agents**.
> No external model or server required — fully deterministic, runs instantly.

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

No `.env` configuration needed. The FOL agents operate without any LLM backend.

---

## All CLI Flags

```
--tasks        N            Generate N tasks (default: 10)
--seed         N            Random seed for reproducibility (default: 42)
--grid         N            Grid size NxN (default: 20)
--no-delay                  Skip simulated execution delays (faster demo)
--out          PATH         Output JSON path (default: auto under results/)
--interactive, -i           Run in interactive mode with parameter menu
```

Example:

```bash
python main.py --tasks 12 --seed 7 --no-delay
```

---

## Interactive Mode

```bash
python main.py --interactive
# or
python main.py -i
```

### Features

- **Live parameter adjustment** — change tasks, seed, grid size, delay, and output path without restarting
- **Random seed generator** — quickly test different scenarios with `[R]`
- **Auto-incrementing output** — `results/latest.json` always stays current; each run also saves a traceable file
- **Re-run simulation instantly** — experiment with different configurations

---

## Configuration

All constants live in `config.py`. No `.env` file or environment variables are required.

Key settings:

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
cse419_hw02_221805040/
│
├── agents/
│   ├── base.py                    # BasePlannerAgent, BaseAssignmentAgent, BaseCriticAgent
│   │
│   ├── fol/                       # FOL / Symbolic implementations (HW2 — active)
│   │   ├── __init__.py
│   │   ├── planner.py             # FOLPlannerAgent
│   │   ├── assignment.py          # FOLAssignmentAgent
│   │   └── critic.py              # FOLCriticAgent
│
├── report/
│   ├── index.html                 # Dashboard home page
│   ├── report.html                # Redirects to index.html (backwards compat)
│   ├── report.md                  # Written project report
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
├── simulation.py                  # Full FOL pipeline orchestration
├── results/                       # Output runs (auto-created)
│   ├── latest.json                # Dashboard data (latest run)
│   └── t*_g*_s*_*.json           # Individual traceable runs
├── main.py                        # CLI entry point
├── requirements.txt
├── .env.example
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
                │
                │ implements
                ▼
        agents/fol/
┌───────────────────────────────┐
│     FOL / Symbolic Agents     │
│                               │
│  - FOLPlannerAgent            │
│  - FOLAssignmentAgent         │
│  - FOLCriticAgent             │
└───────────────┬───────────────┘
                │
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

## Visual Report (HTML Dashboard)

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
