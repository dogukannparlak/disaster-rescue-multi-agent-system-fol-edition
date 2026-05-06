# CSE419 — Artificial Intelligence

## CSE419 Homework 01 : LLM-Based Disaster Rescue Multi-Agent System

**Student Name:** Doğukan
**Student ID:** 221805040
**Date:** March 2026
**University:** Aydın Adnan Menderes University

---

## 1. Introduction

Natural disasters create chaotic, time-critical environments where rescue operations must be coordinated rapidly across multiple simultaneous tasks: locating and rescuing victims, clearing debris, delivering medical supplies, and mapping affected areas. Human operators are easily overwhelmed; autonomous multi-agent systems (MAS) offer a promising complement to human decision-making in such scenarios.

This project implements a **fully LLM-based multi-agent disaster rescue system** in Python. Three reasoning agents—a **Planner**, an **Assignment Agent**, and a **Critic**—collaborate in a sequential pipeline before handing a validated rescue plan to a fleet of robot agents that execute tasks in simulation.

**Core question:** *Can LLM-based agents (Ollama) coordinate a heterogeneous robot fleet to correctly and efficiently execute prioritised rescue tasks in a simulated disaster environment?*

---

## 2. System Architecture

### 2.1 Pipeline Overview

```
DisasterEnvironment (tasks + robots)
           │
           ▼
   [1] Planner Agent  ──────────────►  Rescue Plan (plain text)
           │
           ▼
   [2] Assignment Agent  ───────────►  {task_id → robot_id} map (JSON)
           │
           ▼
   [3] Critic Agent  ───────────────►  Critique (text) + Corrected Map (JSON)
           │
           ▼
   [4] Robot Agents  ───────────────►  Task Execution (simulated)
           │
           ▼
   [5] Metrics Engine  ─────────────►  Evaluation Scores
```

### 2.2 Component Table


| Component            | File                   | Role                                                       |
| -------------------- | ---------------------- | ---------------------------------------------------------- |
| Base Interfaces      | `agents/base.py`       | Abstract base classes for all three agent types            |
| LLM Agents           | `agents/llm/`          | Ollama-powered Planner, Assignment, and Critic             |
| LLM Client           | `agents/llm/client.py` | Thin HTTP wrapper for the Ollama `/api/chat` endpoint      |
| Disaster Environment | `environment.py`       | Task list + robot fleet container                          |
| Task Generator       | `task_generator.py`    | Produces randomised `Task` objects                         |
| Robot Model          | `robot_model.py`       | `Robot` dataclass + fixed three-robot fleet                |
| Robot Agents         | `robot_agents.py`      | Simulates task execution with speed-based delays           |
| Metrics Engine       | `metrics.py`           | Computes five quantitative performance scores              |
| Simulation           | `simulation.py`        | Orchestrates the full pipeline; exports `results/` JSON    |
| Entry Point          | `main.py`              | CLI + interactive menu                                     |
| Config               | `config.py`            | Grid size, task count, robot definitions, priority weights |


### 2.3 Agent Descriptions

#### Planner Agent (`agents/llm/planner.py`)

Receives the disaster grid, full task list, and robot fleet. Produces a numbered, urgency-justified plain-text rescue plan. This narrative provides context to the downstream Assignment Agent.

#### Assignment Agent (`agents/llm/assignment.py`)

Receives the Planner's narrative together with structured task and robot data. Returns a strict JSON object:

```json
{"assignments": [{"task_id": "T01", "robot_id": "R2"}, "..."]}
```

If the model returns malformed JSON or omits tasks, the agent retries automatically with a stricter prompt. If both attempts fail a `RuntimeError` is raised.

#### Critic Agent (`agents/llm/critic.py`)

Receives the provisional assignment map, the task list, and the robot fleet. Checks for:

1. Capability mismatches (wrong robot type)
2. Priority ordering violations (low before high within a robot's queue)
3. Unassigned tasks

Returns a JSON object with a `critique` string and an optional `corrected_assignments` list.

#### Robot Agents (`robot_agents.py`)

Each `RobotAgent` wraps a `Robot` dataclass. Tasks are sorted by priority (high → medium → low) and executed sequentially. Execution time is simulated per robot speed:


| Speed  | Simulated Time per Task |
| ------ | ----------------------- |
| fast   | 1 second                |
| medium | 2 seconds               |
| slow   | 3 seconds               |


---

## 3. Disaster Environment

### 3.1 Grid

The disaster area is modelled as an **N × N integer grid** (default: 20 × 20). Each task is assigned a random `(x, y)` coordinate within the grid at generation time.

### 3.2 Task Catalogue

Tasks are sampled uniformly at random from the following catalogue:


| Task Type        | Priority | Required Capability  |
| ---------------- | -------- | -------------------- |
| rescue victim    | high     | medical support      |
| rescue victim    | high     | search and mapping   |
| clear debris     | medium   | heavy debris removal |
| map building     | low      | search and mapping   |
| deliver medicine | medium   | medical support      |


### 3.3 Task Attributes

Each task carries the following fields:


| Field                 | Description                             |
| --------------------- | --------------------------------------- |
| `task_id`             | Unique identifier (e.g., `T01`)         |
| `task_type`           | Human-readable name from the catalogue  |
| `priority`            | `"high"`, `"medium"`, or `"low"`        |
| `required_capability` | Must match a robot's `capability` field |
| `x`, `y`              | Random grid coordinates                 |


### 3.4 Generation Guarantee

`generate_tasks()` guarantees **at least one task per unique capability** so that every robot in the fleet receives at least one task. Remaining slots are filled randomly from the full catalogue and then sorted by priority before being handed to the Planner Agent.

---

## 4. Robot Fleet


| Robot ID | Name                       | Capability           | Speed  |
| -------- | -------------------------- | -------------------- | ------ |
| R1       | Search and Mapping Robot   | search and mapping   | fast   |
| R2       | Medical Support Robot      | medical support      | medium |
| R3       | Heavy Debris Removal Robot | heavy debris removal | slow   |


Each task's `required_capability` must exactly match a robot's `capability`. The Assignment Agent is instructed to enforce this constraint; the Critic Agent validates it independently.

---

## 5. Task Assignment Strategy

### 5.1 LLM-Driven Assignment

The `LLMAssignmentAgent` sends the Planner's plan together with the structured task and robot lists to a local Ollama model. The system prompt instructs the model to:

- Assign every task to exactly one robot.
- Respect capability constraints.
- Order each robot's tasks with high-priority tasks first.

The model returns a JSON array; the agent parses it and validates completeness. If parsing fails, a single automatic retry is issued with a stricter JSON-only instruction.

### 5.2 Critic Correction Loop

After initial assignment, the `LLMCriticAgent` performs a single-pass review. Any corrected assignments returned by the Critic replace the original map before robot execution begins. In practice, the Critic either confirms the plan ("No issues found.") or reorders a small number of tasks.

---

## 6. Evaluation Metrics

All five metrics are computed in `metrics.py` after the Critic phase completes.

### 6.1 Capability Match Rate

$$\text{Capability Match Rate} = \frac{\text{tasks assigned to a capability-matching robot}}{\text{total tasks}}$$

A score of **1.0 (100%)** means every task was given to the correct robot type.

### 6.2 Priority Order Score

For each robot, consecutive task pairs in execution order are compared. A pair is "correct" if the earlier task has equal or higher urgency than the later one.

$$\text{Priority Order Score} = \frac{\text{correctly ordered consecutive pairs}}{\text{total consecutive pairs}}$$

### 6.3 Task Distribution Balance

The Coefficient of Variation (CV) of tasks-per-robot measures load imbalance; a lower CV is better. The score is transformed so higher is better:

$$\text{Balance Score} = \frac{1}{1 + CV}$$

A score close to **1.0** indicates even distribution. The natural capability constraint means robots with more catalogue entries will always receive more tasks; the balance score captures this effect.

### 6.4 Completion Rate

$$\text{Completion Rate} = \frac{\text{completed tasks}}{\text{total tasks}}$$

Because all assigned tasks are always executed in simulation, this metric primarily catches unassigned tasks (capability mismatches that resulted in `"UNASSIGNED"`).

### 6.5 Unassigned Task Count

A raw count of tasks left without a valid robot assignment.

---

## 7. Results

Four simulation runs were conducted across two distinct configurations. Each run is stored as a traceable JSON file under `results/`. The table below summarises all results at a glance.


| Run | Result File                               | seed | grid  | Cap. Match | Priority | Balance | Completion | Unassigned |
| --- | ----------------------------------------- | ---- | ----- | ---------- | -------- | ------- | ---------- | ---------- |
| A   | `t10_g10_s10_20260317-174851_5f8d5b.json` | 10   | 10×10 | **80%**    | 100%     | 63.4%   | **90%**    | 1          |
| B   | `t10_g10_s10_20260317-175004_6d895e.json` | 10   | 10×10 | **100%**   | 100%     | 68.6%   | **100%**   | 0          |
| C   | `t10_g20_s42_20260317-180555_a5d85e.json` | 42   | 20×20 | **90%**    | 100%     | 48.0%   | **80%**    | 1          |
| D   | `t10_g20_s42_20260317-180716_0b3c92.json` | 42   | 20×20 | **100%**   | 100%     | 57.0%   | **100%**   | 0          |


> Runs A & B share the same seed (10) and identical task set. Runs C & D share the same seed (42). The differing outcomes between same-seed pairs demonstrate LLM non-determinism.

---

### 7.1 Configuration 1 — `seed=10, grid=10×10`

**Generated Tasks** (identical for both Runs A and B):


| ID  | Type          | Priority | Required Capability  | Location |
| --- | ------------- | -------- | -------------------- | -------- |
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


#### Run A — `t10_g10_s10_20260317-174851_5f8d5b.json`


| Task | Type          | Priority | Required Capability  | Assigned Robot                  | Match? |
| ---- | ------------- | -------- | -------------------- | ------------------------------- | ------ |
| T01  | rescue victim | high     | medical support      | Medical Support Robot (R2)      | ✓      |
| T02  | rescue victim | high     | search and mapping   | Search and Mapping Robot (R1)   | ✓      |
| T04  | rescue victim | high     | medical support      | Medical Support Robot (R2)      | ✓      |
| T07  | rescue victim | high     | search and mapping   | Search and Mapping Robot (R1)   | ✓      |
| T03  | clear debris  | medium   | heavy debris removal | **UNASSIGNED**                  | ✗      |
| T05  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T06  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T08  | map building  | low      | search and mapping   | **Heavy Debris Removal (R3)**   | ✗      |
| T09  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T10  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |


> T03 was left unassigned; T08 (map building) was wrongly assigned to R3 (heavy debris removal).

**Per-Robot Summary:**


| Robot                     | Tasks Assigned | Tasks Completed |
| ------------------------- | -------------- | --------------- |
| R1 — Search and Mapping   | 2              | 2               |
| R2 — Medical Support      | 2              | 2               |
| R3 — Heavy Debris Removal | 5              | 5               |


**Evaluation Metrics:**


| Metric                    | Score                                           |
| ------------------------- | ----------------------------------------------- |
| Capability Match Rate     | **80.0%** (8/10 — T08 mismatch, T03 unassigned) |
| Priority Order Score      | **100.0%**                                      |
| Task Distribution Balance | **63.4%**                                       |
| Completion Rate           | **90.0%** (9/10)                                |
| Unassigned Tasks          | 1                                               |


---

#### Run B — `t10_g10_s10_20260317-175004_6d895e.json`


| Task | Type          | Priority | Required Capability  | Assigned Robot                  | Match? |
| ---- | ------------- | -------- | -------------------- | ------------------------------- | ------ |
| T01  | rescue victim | high     | medical support      | Medical Support Robot (R2)      | ✓      |
| T02  | rescue victim | high     | search and mapping   | Search and Mapping Robot (R1)   | ✓      |
| T03  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T04  | rescue victim | high     | medical support      | Medical Support Robot (R2)      | ✓      |
| T05  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T06  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T07  | rescue victim | high     | search and mapping   | Search and Mapping Robot (R1)   | ✓      |
| T08  | map building  | low      | search and mapping   | Search and Mapping Robot (R1)   | ✓      |
| T09  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |
| T10  | clear debris  | medium   | heavy debris removal | Heavy Debris Removal Robot (R3) | ✓      |


> No issues — perfect assignment on all 10 tasks.

**Per-Robot Summary:**


| Robot                     | Tasks Assigned | Tasks Completed |
| ------------------------- | -------------- | --------------- |
| R1 — Search and Mapping   | 3              | 3               |
| R2 — Medical Support      | 2              | 2               |
| R3 — Heavy Debris Removal | 5              | 5               |


**Evaluation Metrics:**


| Metric                    | Score      |
| ------------------------- | ---------- |
| Capability Match Rate     | **100.0%** |
| Priority Order Score      | **100.0%** |
| Task Distribution Balance | **68.6%**  |
| Completion Rate           | **100.0%** |
| Unassigned Tasks          | 0          |


---

### 7.2 Configuration 2 — `seed=42, grid=20×20`

**Generated Tasks** (identical for both Runs C and D):


| ID  | Type             | Priority | Required Capability  | Location |
| --- | ---------------- | -------- | -------------------- | -------- |
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


#### Run C — `t10_g20_s42_20260317-180555_a5d85e.json`


| Task | Type             | Priority | Required Capability  | Assigned Robot             | Match? |
| ---- | ---------------- | -------- | -------------------- | -------------------------- | ------ |
| T01  | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T02  | rescue victim    | high     | search and mapping   | **Not in assignments**     | ✗      |
| T03  | clear debris     | medium   | heavy debris removal | Heavy Debris Removal (R3)  | ✓      |
| T04  | deliver medicine | medium   | medical support      | Medical Support Robot (R2) | ✓      |
| T05  | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T06  | rescue victim    | high     | search and mapping   | Search and Mapping (R1)    | ✓      |
| T07  | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T08  | deliver medicine | medium   | medical support      | Medical Support Robot (R2) | ✓      |
| T09  | map building     | low      | search and mapping   | **UNASSIGNED**             | ✗      |
| T10  | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |


> T02 was omitted from the assignments list entirely; T09 was explicitly marked UNASSIGNED.

**Per-Robot Summary:**


| Robot                     | Tasks Assigned | Tasks Completed |
| ------------------------- | -------------- | --------------- |
| R1 — Search and Mapping   | 1              | 1               |
| R2 — Medical Support      | 6              | 6               |
| R3 — Heavy Debris Removal | 1              | 1               |


**Evaluation Metrics:**


| Metric                    | Score                          |
| ------------------------- | ------------------------------ |
| Capability Match Rate     | **90.0%** (9/10 — T02 omitted) |
| Priority Order Score      | **100.0%**                     |
| Task Distribution Balance | **48.0%**                      |
| Completion Rate           | **80.0%** (8/10)               |
| Unassigned Tasks          | 1                              |


---

#### Run D — `t10_g20_s42_20260317-180716_0b3c92.json`


| Task | Type             | Priority | Required Capability  | Assigned Robot             | Match? |
| ---- | ---------------- | -------- | -------------------- | -------------------------- | ------ |
| T01  | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T02  | rescue victim    | high     | search and mapping   | Search and Mapping (R1)    | ✓      |
| T03  | clear debris     | medium   | heavy debris removal | Heavy Debris Removal (R3)  | ✓      |
| T04  | deliver medicine | medium   | medical support      | Medical Support Robot (R2) | ✓      |
| T05  | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T06  | rescue victim    | high     | search and mapping   | Search and Mapping (R1)    | ✓      |
| T07  | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |
| T08  | deliver medicine | medium   | medical support      | Medical Support Robot (R2) | ✓      |
| T09  | map building     | low      | search and mapping   | Search and Mapping (R1)    | ✓      |
| T10  | rescue victim    | high     | medical support      | Medical Support Robot (R2) | ✓      |


> No issues — perfect assignment on all 10 tasks.

**Per-Robot Summary:**


| Robot                     | Tasks Assigned | Tasks Completed |
| ------------------------- | -------------- | --------------- |
| R1 — Search and Mapping   | 3              | 3               |
| R2 — Medical Support      | 6              | 6               |
| R3 — Heavy Debris Removal | 1              | 1               |


**Evaluation Metrics:**


| Metric                    | Score      |
| ------------------------- | ---------- |
| Capability Match Rate     | **100.0%** |
| Priority Order Score      | **100.0%** |
| Task Distribution Balance | **57.0%**  |
| Completion Rate           | **100.0%** |
| Unassigned Tasks          | 0          |


---

### 7.3 Analysis

#### Task Completion Efficiency

Across all four runs, **two achieved 100% capability match and completion** (Runs B and D). Runs A and C each had failures: in Run A, T03 was left unassigned and T08 was misassigned to R3; in Run C, T02 was omitted from the assignment list and T09 was explicitly marked UNASSIGNED. In both failing runs the **Critic Agent did not catch the errors**, returning "No issues found." This confirms that the single-pass Critic is the system's main reliability bottleneck.

Task distribution balance ranged from 48.0% (Run C) to 68.6% (Run B). In Configuration 2 (seed 42), R2 received 6 of 10 tasks because the seed generated 6 medical-support-capable tasks. This is catalogue-driven imbalance, not a planning error.

#### Priority Handling

**All four runs achieved 100% Priority Order Score.** In every case, the Assignment Agent ordered each robot's task queue with high-priority tasks first, followed by medium and then low. The Planner Agent's urgency-ranked narrative proved a reliable context signal across both seeds and both grid sizes.

#### LLM Non-Determinism

Runs A and B use **identical inputs** (seed 10, grid 10×10) yet produce different results:

- Run A: 80% capability match, 1 unassigned task
- Run B: 100% capability match, 0 unassigned tasks

The same pattern appears in Runs C and D (seed 42):

- Run C: 90% capability match, 2 tasks missed
- Run D: 100% capability match, complete success

This confirms that LLM output is probabilistic. Re-running the same configuration can resolve failures—a strong argument for automatic retry or majority-voting logic.

---

### 7.4 Observations

1. **Priority ordering is the most reliable metric.** It scored 100% in all four runs regardless of capability match failures or missing assignments.
2. **Capability matching is the primary failure mode.** Every error across the four runs involved wrong robot assignments or omitted tasks—never priority violations.
3. **The Critic does not reliably catch all errors.** Both Run A and Run C ended with failures that the single-pass Critic did not correct. A stricter Critic prompt or a multi-pass loop is required for consistent results.
4. **Load imbalance is catalogue-driven.** With 6 medical-support tasks in Configuration 2, R2 is structurally overloaded in both Runs C and D. Expanding task variety or adding dynamic fleet scaling would improve balance scores.

---

### 7.5 Limitations and Future Work


| Limitation                               | Evidence from Runs        | Potential Improvement                          |
| ---------------------------------------- | ------------------------- | ---------------------------------------------- |
| Single-pass Critic misses errors         | Runs A, C                 | Multi-iteration feedback loop                  |
| LLM non-determinism causes failures      | A vs B, C vs D            | Automatic retry; majority-vote over N calls    |
| Sequential robot execution               | All runs                  | Parallel threads / asyncio                     |
| No travel distance modelling             | All runs                  | Distance-weighted cost function                |
| Fixed fleet, single capability per robot | All runs                  | Multi-capability robots; dynamic fleet scaling |
| Catalogue imbalance → load imbalance     | Run C: R2 gets 6/10 tasks | Balanced catalogue; priority-weighted sampling |


---

## 8. Conclusion

This project demonstrated that a fully LLM-based three-agent pipeline (Planner → Assignment → Critic) can coordinate a heterogeneous robot fleet in a simulated disaster environment. Across four real simulation runs, the system achieved **100% priority order compliance in all cases** and **100% task completion in two of four runs**. The two imperfect runs (A and C) revealed a consistent failure pattern: the LLM Assignment Agent occasionally omits or misassigns a task, and the single-pass Critic Agent does not always correct it.

The most significant finding is the **non-determinism of LLM outputs**: identical inputs (same seed, same task set) produced both perfect and imperfect results across repeated runs. This motivates future work on retry logic, multi-pass critiquing, and output validation before robot execution begins.

The modular architecture makes it straightforward to extend: additional task types, larger robot fleets, more capable Ollama models, or richer evaluation metrics can be integrated without restructuring the pipeline. The `results/`-based JSON storage and interactive CLI enable rapid experimentation and reproducible cross-run comparisons.

---

