from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List
from config import GRID_SIZE, PRIORITY_ORDER, RANDOM_SEED, TASK_CATALOGUE

@dataclass
class Task:

    task_id: str
    task_type: str
    priority: str                  # "high" | "medium" | "low"
    required_capability: str       # must match a robot capability
    x: int                         # grid column
    y: int                         # grid row
    assigned_robot_id: str = ""    # filled during assignment phase
    completed: bool = False

    # numeric priority for easy sorting (lower = more urgent)
    @property
    def priority_value(self) -> int:
        return PRIORITY_ORDER.get(self.priority, 99)

    def __str__(self) -> str:
        return (
            f"[{self.task_id}] {self.task_type} | priority={self.priority} "
            f"| capability={self.required_capability} | location=({self.x},{self.y})"
        )

def generate_tasks(
    n: int,
    seed: int | None = RANDOM_SEED,
    grid_size: int = GRID_SIZE,
) -> List[Task]:

    rng = random.Random(seed)
    tasks: List[Task] = []

    # Build a map: capability → list of catalogue entries
    cap_to_entries: dict[str, list] = {}
    for entry in TASK_CATALOGUE:
        cap = entry[2]  # required_capability
        cap_to_entries.setdefault(cap, []).append(entry)

    unique_caps = list(cap_to_entries.keys())
    task_idx = 0

    # Phase 1: guarantee at least one task per capability
    for cap in unique_caps:
        if task_idx >= n:
            break
        entry = rng.choice(cap_to_entries[cap])
        task_type, priority, capability = entry
        task = Task(
            task_id=f"T{task_idx + 1:02d}",
            task_type=task_type,
            priority=priority,
            required_capability=capability,
            x=rng.randint(0, grid_size - 1),
            y=rng.randint(0, grid_size - 1),
        )
        tasks.append(task)
        task_idx += 1

    # Phase 2: fill remaining slots with random catalogue entries
    while task_idx < n:
        task_type, priority, capability = rng.choice(TASK_CATALOGUE)
        task = Task(
            task_id=f"T{task_idx + 1:02d}",
            task_type=task_type,
            priority=priority,
            required_capability=capability,
            x=rng.randint(0, grid_size - 1),
            y=rng.randint(0, grid_size - 1),
        )
        tasks.append(task)
        task_idx += 1

    # Sort by urgency so the planner already receives an ordered list
    tasks.sort(key=lambda t: t.priority_value)
    return tasks


