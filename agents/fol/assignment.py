from __future__ import annotations

import math
from typing import Dict, List
from colorama import Fore, Style
from agents.base import BaseAssignmentAgent
from environment import DisasterEnvironment
from config import ROBOT_START_X, ROBOT_START_Y, SPEED_VALUES


def _euclidean(rx: int, ry: int, tx: int, ty: int) -> float:
    return math.sqrt((rx - tx) ** 2 + (ry - ty) ** 2)


def _cost(rx: int, ry: int, tx: int, ty: int, speed: str) -> float:
    """Cost(r,t) = Distance(r,t) / Speed(r)"""
    dist = _euclidean(rx, ry, tx, ty)
    spd = SPEED_VALUES.get(speed, 1.0)
    return dist / spd


class FOLAssignmentAgent(BaseAssignmentAgent):
    """
    Rule-based assignment using First-Order Logic constraints.

    FOL constraints enforced:
      ∀t ∃!r Assigned(t, r)
        — every task is assigned to exactly one robot
      ∀t,r Assigned(t,r) → Compatible(Type(t), Capability(r))
        — capability must match
      ∀t1,t2 Priority(t1) > Priority(t2) → ScheduledBefore(t1, t2)
        — tasks ordered by urgency within each robot's queue

    Optimisation (greedy):
      When multiple robots share a capability, pick the one with
      minimum Cost(r,t) = Distance(r,t) / Speed(r).

    Deterministic symbolic reasoning — no external model required.
    """

    def run(self, env: DisasterEnvironment, plan_str: str) -> Dict[str, str]:
        print(Fore.YELLOW + "\n[FOL Assignment Agent] Assigning tasks via FOL constraints...")

        # Build capability → list[Robot] index
        cap_to_robots: Dict[str, List] = {}
        for robot in env.robots:
            cap_to_robots.setdefault(robot.capability.lower(), []).append(robot)

        # Sort tasks by priority (high=1 first)
        sorted_tasks = sorted(env.tasks, key=lambda t: t.priority_value)

        assignment: Dict[str, str] = {}
        total_cost = 0.0

        for task in sorted_tasks:
            required = task.required_capability.lower()
            candidates = cap_to_robots.get(required, [])

            if not candidates:
                # FOL constraint violation — no compatible robot exists
                print(
                    Fore.RED
                    + f"[FOL Assignment Agent] WARNING: No robot for capability "
                    f"'{task.required_capability}' — {task.task_id} UNASSIGNED"
                )
                assignment[task.task_id] = "UNASSIGNED"
                continue

            # Optimisation: min Cost(r,t) among compatible candidates
            best_robot = min(
                candidates,
                key=lambda r: _cost(ROBOT_START_X, ROBOT_START_Y, task.x, task.y, r.speed),
            )
            task_cost = _cost(ROBOT_START_X, ROBOT_START_Y, task.x, task.y, best_robot.speed)
            total_cost += task_cost

            assignment[task.task_id] = best_robot.robot_id
            print(
                Fore.YELLOW
                + f"  Assigned {task.task_id} ({task.priority}) → {best_robot.robot_id}"
                f" [{best_robot.name}]  cost={task_cost:.3f}"
            )

        print(
            Fore.YELLOW
            + f"\n[FOL Assignment Agent] Total cost ∑Cost(r,t) = {total_cost:.3f}"
        )
        print(Fore.YELLOW + "[FOL Assignment Agent] Assignments complete.")
        return assignment
