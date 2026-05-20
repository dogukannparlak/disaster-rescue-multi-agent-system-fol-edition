from __future__ import annotations

from typing import Dict, List, Tuple
from colorama import Fore, Style
from agents.base import BaseCriticAgent
from environment import DisasterEnvironment


class FOLCriticAgent(BaseCriticAgent):
    """
    Rule-based critic that verifies and repairs assignments using FOL axioms.

    Rule 1  ∀t Task(t) → ∃!r Assigned(t, r)
              Every task must be assigned; no UNASSIGNED entries allowed.

    Rule 2  ∀t,r Assigned(t,r) → Compatible(Type(t), Capability(r))
              The assigned robot's capability must match the task's requirement.

    Rule 3  ∀t1,t2(Priority(t1)>Priority(t2)→ScheduledBefore(t1,t2))
              Enforced at execution: RobotAgent.load_tasks() sorts by priority_value
              before running; the assignment dict does not encode execution order.

    Detected violations are described in English, then automatically corrected.
    Deterministic symbolic reasoning — no external model required.
    """

    def run(
        self,
        env: DisasterEnvironment,
        assignment: Dict[str, str],
    ) -> Tuple[str, Dict[str, str]]:
        print(Fore.GREEN + "\n[FOL Critic Agent] Evaluating assignment plan...")

        task_map  = {t.task_id: t for t in env.tasks}
        robot_map = {r.robot_id: r for r in env.robots}
        # capability → robot_id (first match; adequate for current fleet size)
        cap_to_robot = {r.capability.lower(): r.robot_id for r in env.robots}

        issues: List[str] = []
        corrected: Dict[str, str] = dict(assignment)

        # ── Rule 1: ∀t Task(t) → ∃!r Assigned(t,r) ─────────────────────────
        for task in env.tasks:
            tid = task.task_id
            rid = corrected.get(tid, "UNASSIGNED")

            if rid == "UNASSIGNED" or rid not in robot_map:
                issue = (
                    f"Rule 1 violation: Task {tid} is UNASSIGNED. "
                    f"Requires capability '{task.required_capability}'."
                )
                issues.append(issue)
                print(Fore.RED + f"  [!] {issue}")

                # Correction: find a compatible robot
                fix_rid = cap_to_robot.get(task.required_capability.lower())
                if fix_rid:
                    corrected[tid] = fix_rid
                    print(Fore.GREEN + f"      → Corrected: {tid} → {fix_rid}")
                else:
                    corrected[tid] = "UNASSIGNED"
                    print(Fore.RED + f"      → No compatible robot found; left UNASSIGNED")

        # ── Rule 2: ∀t,r Assigned(t,r) → Compatible(Type(t),Capability(r)) ─
        for tid, rid in list(corrected.items()):
            task  = task_map.get(tid)
            robot = robot_map.get(rid)

            if task is None or robot is None or rid == "UNASSIGNED":
                continue

            if robot.capability.lower() != task.required_capability.lower():
                issue = (
                    f"Rule 2 violation: {tid} assigned to {rid} "
                    f"(capability='{robot.capability}') but requires "
                    f"'{task.required_capability}'."
                )
                issues.append(issue)
                print(Fore.RED + f"  [!] {issue}")

                # Correction: re-assign to a compatible robot
                fix_rid = cap_to_robot.get(task.required_capability.lower())
                if fix_rid:
                    corrected[tid] = fix_rid
                    print(Fore.GREEN + f"      → Corrected: {tid} → {fix_rid}")
                else:
                    corrected[tid] = "UNASSIGNED"
                    print(Fore.RED + f"      → No compatible robot found; left UNASSIGNED")

        # ── Rule 3: priority order (ScheduledBefore) ───────────────────────────
        # The assignment map is task→robot only; execution order is not encoded in
        # dict key order. RobotAgent.load_tasks() sorts by priority_value before
        # execution, so the FOL priority constraint is enforced in simulation.py /
        # robot_agents.py — no dict-order check here (avoids false positives).

        # ── Summary ──────────────────────────────────────────────────────────
        if issues:
            critique_text = "Issues found:\n" + "\n".join(f"  - {i}" for i in issues)
        else:
            critique_text = "No issues found. All FOL constraints satisfied."

        print(Fore.GREEN + "\n[FOL Critic Agent] Critique complete.")
        print(Fore.WHITE + "-" * 60)
        print(f"CRITIQUE:\n{critique_text}")
        print(Fore.WHITE + "-" * 60)

        return critique_text, corrected
