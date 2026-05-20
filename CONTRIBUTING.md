# Contributing to Disaster Rescue Multi-Agent System

Thank you for your interest in contributing! This document covers everything you need to get started.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Commit Convention](#commit-convention)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Areas Open for Contribution](#areas-open-for-contribution)

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/disaster-rescue-multi-agent-system-fol-edition.git
   cd disaster-rescue-multi-agent-system-fol-edition
   ```
3. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Verify** the baseline works before making any changes:
   ```bash
   python main.py --no-delay
   ```

---

## Project Structure

```
agents/fol/          # FOL symbolic agent implementations
  planner.py         # Priority-ordered rescue plan
  assignment.py      # Min-cost, capability-constrained assignment
  critic.py          # FOL axiom verifier + auto-corrector

agents/base.py       # Abstract base classes — extend these for new backends

config.py            # All constants (grid, robots, catalogue, speeds)
environment.py       # DisasterEnvironment + FOL serialisation
task_generator.py    # Randomised task generation
robot_model.py       # Robot dataclass + fleet builder
robot_agents.py      # Task execution engine
metrics.py           # Evaluation metrics + cost efficiency
simulation.py        # Full pipeline orchestrator
main.py              # CLI entry point
report/              # Static HTML dashboard
```

Key design principle: **agents are interchangeable**. `BasePlannerAgent`, `BaseAssignmentAgent`, and `BaseCriticAgent` in `agents/base.py` define the interface. A new backend (e.g. `agents/llm/`) only needs to implement those three classes.

---

## Development Setup

### Linting

The project targets clean, readable Python. Before submitting a PR, please ensure your code passes:

```bash
# Ruff (fast linter + formatter — recommended)
pip install ruff
ruff check .
ruff format .

# Or with flake8 + black
pip install flake8 black
flake8 .
black .
```

### Running the Simulation

```bash
python main.py --no-delay                          # quick smoke test
python main.py --tasks 20 --seed 123 --no-delay    # larger scenario
python main.py --interactive                        # interactive mode
```

---

## Making Changes

### Branch Naming

| Type | Pattern | Example |
|---|---|---|
| New feature | `feature/<short-description>` | `feature/parallel-execution` |
| Bug fix | `fix/<short-description>` | `fix/critic-false-negative` |
| Refactor | `refactor/<short-description>` | `refactor/metrics-module` |
| Documentation | `docs/<short-description>` | `docs/update-architecture` |
| Tests | `test/<short-description>` | `test/assignment-axioms` |

Always branch off `main`:
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

---

## Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org):

```
<type>(<scope>): <short summary>
```

| Type | When to use |
|---|---|
| `feat` | New capability or agent |
| `fix` | Bug fix |
| `refactor` | Code restructure without behaviour change |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Build scripts, CI, tooling |
| `perf` | Performance improvement |

**Examples:**

```
feat(agents): add LLM-based planner agent backend
fix(critic): repair false negative on unassigned task detection
refactor(metrics): extract cost helpers into separate module
docs(readme): add architecture diagram
test(assignment): add FOL axiom violation coverage
```

Keep the summary under 72 characters. Add a body paragraph if the change needs more context.

---

## Pull Request Guidelines

1. **One concern per PR** — keep changes focused and reviewable.
2. **Update `CHANGELOG.md`** — add an entry under `[Unreleased]`.
3. **Describe what and why** in the PR description, not just what changed.
4. **All existing behaviour must still work** — run `python main.py --no-delay` and confirm clean output before opening the PR.
5. **If you add a new feature**, update the relevant section in `README.md` and `report.md`.

---

## Areas Open for Contribution

Below are ideas ranging from small to large. Pick what interests you.

### Small
- Add `pytest` unit tests for `FOLCriticAgent`, `FOLAssignmentAgent`, and `metrics.py`
- Add a `Makefile` with `make run`, `make test`, `make lint` shortcuts
- Improve error messages in `robot_agents.py` for edge cases

### Medium
- `requirements-dev.txt` with `pytest`, `ruff`, `mypy`
- GitHub Actions CI workflow that runs lint + tests on every push
- Export simulation results to CSV in addition to JSON
- Add a `--format` CLI flag (`json` / `csv` / `text`)

### Large
- Implement a second agent backend under `agents/llm/` using Ollama or OpenAI
- Add multi-capability robots to the fleet and update the cost optimiser
- Track actual robot positions between tasks (real travelling cost)
- Parallel task execution with `asyncio` in `robot_agents.py`
- Interactive grid visualisation in the HTML dashboard

---

## Code Style Notes

- **No unnecessary comments** — code should be self-explanatory; comments explain *why*, not *what*.
- **Type hints** on all function signatures.
- **Dataclasses** for data-holding objects (see `Task`, `Robot`).
- **Colorama** for all terminal output — keep colour conventions consistent (cyan=info, yellow=assignment, green=success, red=error, magenta=metrics).

---

## Questions?

Open a [GitHub Issue](../../issues) with the `question` label. Happy to help.
