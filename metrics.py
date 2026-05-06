from __future__ import annotations

import math
import statistics
from typing import Any, Dict, List
from colorama import Fore
from tabulate import tabulate
from config import ROBOT_START_X, ROBOT_START_Y
from robot_model import Robot
from task_generator import Task


def compute_cost_efficiency(
    tasks: List[Task],
    robots: List[Robot],
    speed_values: Dict[str, float],
) -> Dict[str, Any]:
    """
    PDF (Term Project #2): Cost(r,t) = Distance(r,t) / Speed(r)
    Efficiency = Actual Cost / Optimal Cost (CSE419 PDF; 1.0 = optimal).

    Optimal Cost — each task assigned to the lowest-cost compatible robot.
    Actual Cost  — based on the current assigned_robot_id on each task.
    Robot start position from config (ROBOT_START_X/Y); distance is Euclidean.
    """
    robot_map = {r.robot_id: r for r in robots}

    def dist(tx: int, ty: int) -> float:
        return math.sqrt((ROBOT_START_X - tx) ** 2 + (ROBOT_START_Y - ty) ** 2)

    def cost(robot: Robot, task: Task) -> float:
        spd = speed_values.get(robot.speed, 1.0)
        return dist(task.x, task.y) / spd if spd > 0 else float("inf")

    actual_cost = 0.0
    optimal_cost = 0.0

    for task in tasks:
        # Compatible robots for this task
        compatible = [r for r in robots if r.capability.lower() == task.required_capability.lower()]

        # Optimal: minimum cost among compatible robots
        if compatible:
            optimal_cost += min(cost(r, task) for r in compatible)

        # Actual: cost with the assigned robot
        assigned = robot_map.get(task.assigned_robot_id)
        if assigned:
            actual_cost += cost(assigned, task)
        # Unassigned tasks contribute 0 actual cost but inflate the gap

    # PDF (CSE419 TP#2): Efficiency = Actual Cost / Optimal Cost
    # 1.0 = optimal; >1.0 means actual cost exceeds per-task greedy lower bound.
    if optimal_cost > 0:
        efficiency: float | None = actual_cost / optimal_cost
    elif actual_cost == 0.0:
        efficiency = 1.0
    else:
        efficiency = None  # degenerate: no positive optimal baseline

    return {
        "actual_cost":     round(actual_cost,  4),
        "optimal_cost":    round(optimal_cost, 4),
        "cost_efficiency": round(efficiency, 4) if efficiency is not None else None,
    }

def evaluate(tasks: List[Task], robots: List[Robot]) -> Dict[str, Any]:

    # ── 1. Capability match rate ──────────────────────────────────────────────
    robot_map = {r.robot_id: r for r in robots}

    total = len(tasks)
    correct_cap = 0
    for t in tasks:
        if t.assigned_robot_id and t.assigned_robot_id != "UNASSIGNED":
            robot = robot_map.get(t.assigned_robot_id)
            if robot and robot.can_handle(t):
                correct_cap += 1

    capability_match_rate = correct_cap / total if total > 0 else 0.0

    # ── 2. Priority order score ───────────────────────────────────────────────
    pairs_total = 0
    pairs_correct = 0
    for robot in robots:
        tasks_sorted_assigned = sorted(
            robot.completed_tasks, key=lambda t: t.priority_value
        )
        # Compare the actual completion order vs the ideal priority order
        actual_order = [t.task_id for t in robot.completed_tasks]
        ideal_order  = [t.task_id for t in tasks_sorted_assigned]

        for i in range(len(actual_order) - 1):
            pairs_total += 1
            if (
                ideal_order.index(actual_order[i])
                <= ideal_order.index(actual_order[i + 1])
            ):
                pairs_correct += 1

    priority_order_score = pairs_correct / pairs_total if pairs_total > 0 else 1.0

    # ── 3. Task distribution balance ─────────────────────────────────────────
    counts = [len(r.completed_tasks) for r in robots]
    if len(counts) > 1 and statistics.mean(counts) > 0:
        cv = statistics.stdev(counts) / statistics.mean(counts)
    else:
        cv = 0.0
    task_distribution_balance = 1.0 / (1.0 + cv)

    # ── 4. Completion rate ────────────────────────────────────────────────────
    completed = sum(1 for t in tasks if t.completed)
    completion_rate = completed / total if total > 0 else 0.0

    # ── 5. Unassigned task count ────────────────────────────────────────────────
    unassigned_count = sum(
        1 for t in tasks if t.assigned_robot_id in ("", "UNASSIGNED")
    )

    metrics = {
        "capability_match_rate":      round(capability_match_rate,      4),
        "priority_order_score":       round(priority_order_score,       4),
        "task_distribution_balance":  round(task_distribution_balance,  4),
        "completion_rate":            round(completion_rate,            4),
        "unassigned_count":           unassigned_count,
    }
    return metrics


def display_metrics(metrics: Dict[str, Any], robots: List[Robot]) -> None:

    print(Fore.MAGENTA + "\n" + "=" * 60)
    print(Fore.MAGENTA + "  EVALUATION METRICS")
    print(Fore.MAGENTA + "=" * 60)

    ce = metrics.get("cost_efficiency")
    if ce is None:
        ce_str = "n/a"
    else:
        ce_str = f"{ce:.4f} (1.0 = optimal)"

    rows = [
        ["Capability Match Rate",        f"{metrics['capability_match_rate'] * 100:.1f}%"],
        ["Priority Order Score",         f"{metrics['priority_order_score'] * 100:.1f}%"],
        ["Task Distribution Balance",    f"{metrics['task_distribution_balance'] * 100:.1f}%"],
        ["Completion Rate",              f"{metrics['completion_rate'] * 100:.1f}%"],
        ["Unassigned Tasks",             f"{metrics['unassigned_count']}"],
        ["Actual Total Cost",            f"{metrics.get('actual_cost', 0.0):.2f}"],
        ["Optimal Total Cost",           f"{metrics.get('optimal_cost', 0.0):.2f}"],
        ["Cost Ratio (Actual/Optimal)",  ce_str],
    ]
    print(tabulate(rows, headers=["Metric", "Score"], tablefmt="rounded_outline"))

    # Per-robot summary
    print(Fore.MAGENTA + "\n  PER-ROBOT SUMMARY")
    robot_rows = [
        [r.robot_id, r.name, len(r.assigned_tasks), len(r.completed_tasks)]
        for r in robots
    ]
    print(tabulate(
        robot_rows,
        headers=["ID", "Robot", "Assigned", "Completed"],
        tablefmt="rounded_outline",
    ))


