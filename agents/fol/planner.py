from __future__ import annotations

from colorama import Fore, Style
from agents.base import BasePlannerAgent
from environment import DisasterEnvironment

# Priority label → display string
_PRIORITY_LABEL = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}


class FOLPlannerAgent(BasePlannerAgent):
    """
    Rule-based planner using First-Order Logic constraints.

    FOL axioms applied:
      ∀t Task(t) → HasPriority(t, Priority(t))
      ∀t1,t2 Priority(t1) > Priority(t2) → ScheduledBefore(t1, t2)
      ∀t Task(t) → RequiresCapability(t, Capability(t))

    Deterministic symbolic reasoning — no external model required.
    """

    def run(self, env: DisasterEnvironment) -> str:
        print(Fore.CYAN + "\n[FOL Planner] Generating rule-based rescue plan...")

        sorted_tasks = sorted(env.tasks, key=lambda t: t.priority_value)

        lines = ["[FOL Planner] Rescue Plan:"]
        for idx, task in enumerate(sorted_tasks, start=1):
            priority_label = _PRIORITY_LABEL.get(task.priority, task.priority.upper())
            lines.append(
                f"{idx}. [{task.task_id}] {task.task_type} ({priority_label})"
                f" → requires {task.required_capability} robot"
                f" | location=({task.x},{task.y})"
            )

        plan_str = "\n".join(lines)

        print(Fore.CYAN + "[FOL Planner] Plan generated.")
        print(Fore.WHITE + "-" * 60)
        print(plan_str)
        print(Fore.WHITE + "-" * 60)

        return plan_str
