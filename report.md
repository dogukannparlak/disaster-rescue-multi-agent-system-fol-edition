# Disaster Rescue Multi-Agent System — Technical Report

> **FOL / Symbolic Reasoning Edition**
> A deterministic, fully self-contained multi-agent system for disaster rescue coordination powered by First-Order Logic agents.

---

## 1. Overview

Natural disasters create chaotic, time-critical environments where rescue operations must be coordinated rapidly across multiple simultaneous tasks. This project implements a multi-agent pipeline that coordinates three specialised rescue robots using **symbolic (First-Order Logic) reasoning** — no external model or server is required, and the system runs in under one second.

The pipeline was built as a deliberate study in **reliability vs. flexibility**: an earlier LLM-based version of the same pipeline ([v1 — LLM Edition](https://github.com/dogukannparlak/disaster-rescue-multi-agent)) demonstrated natural-language flexibility but introduced non-determinism — identical inputs sometimes produced different (and incorrect) outputs. This symbolic edition replaces the three reasoning agents with rule-based implementations that enforce explicit FOL axioms, making every decision fully traceable and bit-for-bit reproducible.

**Core design question:** *Can FOL-based symbolic agents match or exceed the reliability of LLM-based agents for disaster rescue coordination, while eliminating non-determinism and external dependencies?*

---

## 2. System Architecture

### 2.1 Pipeline Overview

```
DisasterEnvironment (tasks + robots)
           │
           ▼
   [1] FOL Planner Agent  ─────────►  Rescue Plan (priority-ordered list)
           │
           ▼
   [2] FOL Assignment Agent  ──────►  {task_id → robot_id} map
           │
           ▼
   [3] FOL Critic Agent  ──────────►  Critique text + Corrected Map
           │
           ▼
   [4] Robot Agents  ──────────────►  Task Execution (simulated)
           │
           ▼
   [5] Metrics Engine  ────────────►  Evaluation Scores (incl. cost ratio Actual/Optimal)
```

### 2.2 Component Table

| Component            | File                    | Role                                                              |
| -------------------- | ----------------------- | ----------------------------------------------------------------- |
| Base Interfaces      | `agents/base.py`        | Abstract base classes for all three agent types                   |
| FOL Agents           | `agents/fol/`           | Rule-based Planner, Assignment, and Critic                        |
| Disaster Environment | `environment.py`        | Task list + robot fleet container + FOL serialisation helpers     |
| Task Generator       | `task_generator.py`     | Produces randomised `Task` objects                                |
| Robot Model          | `robot_model.py`        | `Robot` dataclass + fixed three-robot fleet                       |
| Robot Agents         | `robot_agents.py`       | Simulates task execution with speed-based delays                  |
| Metrics Engine       | `metrics.py`            | Five performance scores + `compute_cost_efficiency()`             |
| Simulation           | `simulation.py`         | Orchestrates the full FOL pipeline; exports `results/` JSON       |
| Entry Point          | `main.py`               | CLI + interactive menu                                            |
| Config               | `config.py`             | Grid size, task count, robot definitions, `SPEED_VALUES`, depot `(ROBOT_START_X/Y)` |

### 2.3 FOL Constraints

The entire assignment strategy is encoded as four FOL axioms:

| Axiom | Formula |
|---|---|
| Unique assignment | `∀t (Task(t) → ∃!r Assigned(t,r))` |
| Capability match  | `∀t,r (Assigned(t,r) → Compatible(Type(t), Capability(r)))` |
| Priority ordering | `∀t1,t2 (Priority(t1) > Priority(t2) → ScheduledBefore(t1,t2))` |
| Cost formula      | `Cost(r,t) = Distance(r,t) / Speed(r)` |

Assignments minimise: **∑ Cost(r,t)** subject to the above constraints.

---

## 3. Agent Design

### 3.1 FOL Planner Agent (`agents/fol/planner.py`)

Sorts tasks by `priority_value` (high=1, medium=2, low=3) and produces a numbered, deterministic rescue plan. No external calls.

Output format:
```
[FOL Planner] Rescue Plan:
1. [T01] rescue victim (HIGH) → requires medical support robot | location=(0,8)
2. [T02] rescue victim (HIGH) → requires search and mapping robot | location=(7,4)
...
```

### 3.2 FOL Assignment Agent (`agents/fol/assignment.py`)

Iterates over priority-sorted tasks and assigns each to the robot with matching capability and minimum `Cost(r,t)`. Robot starting position is the depot defined in `config.py` (default `(0,0)`).

Speed values used in the cost formula:

| Speed  | Value |
|--------|-------|
| fast   | 2.0   |
| medium | 1.0   |
| slow   | 0.5   |

### 3.3 FOL Critic Agent (`agents/fol/critic.py`)

Performs three independent rule checks:

1. **Rule 1** — `∀t Task(t) → ∃!r Assigned(t,r)`: every task must be assigned.
2. **Rule 2** — `∀t,r Assigned(t,r) → Compatible(...)`: capability must match.
3. **Rule 3** — `∀t1,t2 ...ScheduledBefore(t1,t2)`: each robot's queue must be priority-ordered (enforced at execution by `RobotAgent.load_tasks()`).

Any violation is automatically corrected by re-assigning to the correct compatible robot.

### 3.4 Robot Agents (`robot_agents.py`)

Tasks are sorted by priority (high → medium → low) and executed sequentially.

| Speed  | Simulated Time per Task |
|--------|-------------------------|
| fast   | 1 second                |
| medium | 2 seconds               |
| slow   | 3 seconds               |

---

## 4. Disaster Environment

### 4.1 Grid

The disaster area is modelled as an **N × N integer grid** (default: 20 × 20). Each task is assigned a random `(x, y)` coordinate.

### 4.2 Task Catalogue

| Task Type        | Priority | Required Capability  |
|------------------|----------|----------------------|
| rescue victim    | high     | medical support      |
| rescue victim    | high     | search and mapping   |
| clear debris     | medium   | heavy debris removal |
| map building     | low      | search and mapping   |
| deliver medicine | medium   | medical support      |

### 4.3 Robot Fleet

| Robot ID | Name                       | Capability           | Speed  |
|----------|----------------------------|----------------------|--------|
| R1       | Search and Mapping Robot   | search and mapping   | fast   |
| R2       | Medical Support Robot      | medical support      | medium |
| R3       | Heavy Debris Removal Robot | heavy debris removal | slow   |

---

## 5. Evaluation Metrics

| Metric | Formula / Description | Best |
|--------|-----------------------|------|
| Capability Match Rate | Correctly assigned tasks / Total tasks | 100% |
| Priority Order Score | Correctly ordered consecutive pairs / Total pairs | 100% |
| Task Distribution Balance | `1 / (1 + CV)`, where CV = std/mean of tasks-per-robot | → 1.0 |
| Completion Rate | Completed tasks / Total tasks | 100% |
| Unassigned Task Count | Raw count of UNASSIGNED tasks | 0 |

### 5.1 Cost Efficiency

$$\text{Cost}(r,t) = \frac{\text{Distance}(r,t)}{\text{Speed}(r)}$$

$$\text{Efficiency} = \frac{\text{Actual Total Cost}}{\text{Optimal Total Cost}}$$

**Optimal Cost** — sum over tasks of the minimum $\text{Cost}(r,t)$ among robots compatible with that task.
**Actual Cost** — sum of $\text{Cost}(r,t)$ for the robot actually assigned to each task after execution.
**Interpretation:** **1.0** means actual equals the per-task greedy lower bound; **> 1.0** would indicate a worse-than-baseline assignment.

---

## 6. Results

### 6.1 Configuration A — `seed=10`, `grid=10×10`, `tasks=10`

**Generated tasks:**

| ID  | Type          | Priority | Required Capability  | Location |
|-----|---------------|----------|----------------------|----------|
| T01 | rescue victim | high     | medical support      | (6, 7)   |
| T02 | rescue victim | high     | search and mapping   | (3, 7)   |
| T04 | rescue victim | high     | medical support      | (8, 7)   |
| T07 | rescue victim | high     | search and mapping   | (9, 5)   |
| T03 | clear debris  | medium   | heavy debris removal | (4, 2)   |
| T05 | clear debris  | medium   | heavy debris removal | (1, 3)   |
| T06 | clear debris  | medium   | heavy debris removal | (0, 6)   |
| T09 | clear debris  | medium   | heavy debris removal | (7, 2)   |
| T10 | clear debris  | medium   | heavy debris removal | (5, 2)   |
| T08 | map building  | low      | search and mapping   | (6, 4)   |

**Final assignments (after Critic validation):**

| Task | Type          | Priority | Required Capability  | Assigned Robot                  | Match? |
|------|---------------|----------|----------------------|---------------------------------|--------|
| T01  | rescue victim | high     | medical support      | Medical Support Robot (R2)      | ✓      |
| T02  | rescue victim | high     | search and mapping   | Search and Mapping Robot (R1)   | ✓      |
| T04  | rescue victim | high     | medical support      | Medical Support Robot (R2)      | ✓      |
| T07  | rescue victim | high     | search and mapping   | Search and Mapping Robot (R1)   | ✓      |
| T03  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T05  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T06  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T09  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T10  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T08  | map building  | low      | search and mapping   | Search and Mapping Robot (R1)   | ✓      |

**Per-robot summary:**

| Robot                     | Tasks Assigned | Tasks Completed |
|---------------------------|----------------|-----------------|
| R1 — Search and Mapping   | 3              | 3               |
| R2 — Medical Support      | 2              | 2               |
| R3 — Heavy Debris Removal | 5              | 5               |

**Evaluation metrics (`seed=10`, `grid=10×10`):**

| Metric                      | Score       |
|-----------------------------|-------------|
| Capability Match Rate       | **100.0%**  |
| Priority Order Score        | **100.0%**  |
| Task Distribution Balance   | **68.6%**   |
| Completion Rate             | **100.0%**  |
| Unassigned Tasks            | **0**       |
| Actual Total Cost           | **85.0103** |
| Optimal Total Cost          | **85.0103** |
| Cost Ratio (Actual/Optimal) | **1.0000**  |

---

### 6.2 Configuration B — `seed=42`, `grid=20×20`, `tasks=10`

**Generated tasks:**

| ID  | Type             | Priority | Required Capability  | Location |
|-----|------------------|----------|----------------------|----------|
| T01 | rescue victim    | high     | medical support      | (0, 8)   |
| T02 | rescue victim    | high     | search and mapping   | (7, 4)   |
| T05 | rescue victim    | high     | medical support      | (2, 6)   |
| T06 | rescue victim    | high     | search and mapping   | (16, 19) |
| T07 | rescue victim    | high     | medical support      | (17, 6)  |
| T10 | rescue victim    | high     | medical support      | (5, 13)  |
| T03 | clear debris     | medium   | heavy debris removal | (17, 2)  |
| T04 | deliver medicine | medium   | medical support      | (13, 1)  |
| T08 | deliver medicine | medium   | medical support      | (13, 7)  |
| T09 | map building     | low      | search and mapping   | (18, 8)  |

**Final assignments (after Critic validation):**

| ID  | Type             | Priority | Required Capability  | Assigned Robot             | Match? |
|-----|------------------|----------|----------------------|----------------------------|--------|
| T01 | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T02 | rescue victim    | high     | search and mapping   | Search and Mapping Robot (R1) | ✓   |
| T05 | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T06 | rescue victim    | high     | search and mapping   | Search and Mapping Robot (R1) | ✓   |
| T07 | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T10 | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T03 | clear debris     | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓  |
| T04 | deliver medicine | medium   | medical support      | Medical Support Robot (R2) | ✓      |
| T08 | deliver medicine | medium   | medical support      | Medical Support Robot (R2) | ✓      |
| T09 | map building     | low      | search and mapping   | Search and Mapping Robot (R1) | ✓   |

**Per-robot summary:**

| Robot                     | Tasks Assigned | Tasks Completed |
|---------------------------|----------------|-----------------|
| R1 — Search and Mapping   | 3              | 3               |
| R2 — Medical Support      | 6              | 6               |
| R3 — Heavy Debris Removal | 1              | 1               |

**Evaluation metrics (`seed=42`, `grid=20×20`):**

| Metric                      | Score        |
|-----------------------------|--------------|
| Capability Match Rate       | **100.0%**   |
| Priority Order Score        | **100.0%**   |
| Task Distribution Balance   | **57.0%**    |
| Completion Rate             | **100.0%**   |
| Unassigned Tasks            | **0**        |
| Actual Total Cost           | **134.6181** |
| Optimal Total Cost          | **134.6181** |
| Cost Ratio (Actual/Optimal) | **1.0000**   |

---

## 7. Symbolic vs. LLM Approaches

This system was originally prototyped with an LLM backend (Ollama). The comparison below documents the architectural trade-offs observed between the two approaches.

### 7.1 Aggregate Comparison

| Aspect                         | LLM version (archived)                    | FOL version (this project)        |
|--------------------------------|-------------------------------------------|-----------------------------------|
| Capability match (range)       | 80% – 100%                                | **100%** (both configs)           |
| Completion (range)             | 80% – 100%                                | **100%** (both configs)           |
| Runs with constraint violations| **2 / 4** (stochastic failures)           | **0 / 2**                         |
| External dependency            | Ollama (`/api/chat`)                      | **None**                          |
| Typical wall-clock             | ~10–60 s per pipeline                     | **< 1 s**                         |
| Reproducibility                | Non-deterministic (same seed ≠ same JSON) | **Bit-for-bit reproducible**      |
| Cost ratio (Actual/Optimal)    | Not computed                              | **1.0** (see §5.1)                |

### 7.2 Analysis

**Reliability and variance:** The LLM version behaves like a probabilistic component — marginal distributions over outputs depend on hidden model state. This FOL version replaces that component with a total function from `(seed, grid, catalogue)` to assignments, collapsing variance to zero in the reasoning layer.

**Verification vs. generation:** The LLM Critic empirically failed to detect omissions and mis-assignments that are trivially checkable by symbolic rules. `FOLCriticAgent` implements explicit checks for uniqueness and capability compatibility with deterministic repair; priority ordering is enforced at execution via `RobotAgent.load_tasks()`.

**Cost model:** `Cost(r,t) = Distance(r,t) / Speed(r)` is minimised directly in `FOLAssignmentAgent` and the ratio is computed in `compute_cost_efficiency()`. With one robot per capability, greedy choice is forced and totals match → ratio **1.0** (see §5.1).

**Trade-off:** LLMs retain open-world flexibility (new verbs in prompts) at the price of formal guarantees. FOL sacrifices linguistic generality for auditability — every decision is traceable to an axiom instance.

---

## 8. Limitations & Future Work

| Limitation | Current Behaviour | Potential Improvement |
|---|---|---|
| Rigid capability model | One robot per capability type | Multi-capability robots; dynamic fleet scaling |
| Static robot positions | Assumed start at depot `(0,0)` | Track actual robot positions between tasks |
| Sequential execution | All runs | Parallel execution via `asyncio` |
| Fixed task catalogue | Same 5 task types | Dynamic catalogue; priority-weighted sampling |
| Single-robot per capability | Cost ratio is always 1.0 | Global optimiser or redundant robots to surface Actual > Optimal cases |

---

## 9. Conclusion

The FOL symbolic pipeline satisfies all four formal constraints — unique assignment, capability match, priority ordering, and cost minimisation — **in every reproduced configuration**, while running in under one second without any external dependencies. Every decision is traceable to an explicit axiom instance.

Qualitatively, the shift from generative to deductive reasoning trades prompt-level flexibility for mathematical traceability — a deliberate engineering choice aligned with safety-critical multi-agent system design.

Future directions include **hybrid neuro-symbolic** controllers (FOL for hard constraints, LLM for unstructured sensor fusion) and **fleet redundancy** to activate non-trivial cost optimisation scenarios.
