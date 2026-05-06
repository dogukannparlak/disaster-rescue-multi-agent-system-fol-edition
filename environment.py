from __future__ import annotations

from typing import List
from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate
from robot_model import Robot
from task_generator import Task

colorama_init(autoreset=True)

class DisasterEnvironment:

    def __init__(self, grid_size: int, tasks: List[Task], robots: List[Robot]) -> None:
        self.grid_size = grid_size
        self.tasks = tasks
        self.robots = robots

    # ── Display helpers ───────────────────────────────────────────────────────

    def display_tasks(self) -> None:

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "  DISASTER ENVIRONMENT — TASK LIST")
        print(Fore.CYAN + "=" * 60)

        rows = []
        for t in self.tasks:
            colour = (
                Fore.RED    if t.priority == "high"   else
                Fore.YELLOW if t.priority == "medium" else
                Fore.GREEN
            )
            rows.append([
                colour + t.task_id + Style.RESET_ALL,
                t.task_type,
                colour + t.priority + Style.RESET_ALL,
                t.required_capability,
                f"({t.x}, {t.y})",
            ])

        print(tabulate(
            rows,
            headers=["ID", "Type", "Priority", "Required Capability", "Location"],
            tablefmt="rounded_outline",
        ))

    def display_robots(self) -> None:
        """Print the robot fleet as a table."""
        print(Fore.MAGENTA + "\n" + "=" * 60)
        print(Fore.MAGENTA + "  ROBOT FLEET")
        print(Fore.MAGENTA + "=" * 60)

        rows = [
            [r.robot_id, r.name, r.capability, r.speed]
            for r in self.robots
        ]
        print(tabulate(
            rows,
            headers=["ID", "Name", "Capability", "Speed"],
            tablefmt="rounded_outline",
        ))

    def display_assignments(self) -> None:
        """Print final task–robot assignments."""
        print(Fore.BLUE + "\n" + "=" * 60)
        print(Fore.BLUE + "  FINAL TASK ASSIGNMENTS")
        print(Fore.BLUE + "=" * 60)

        robot_map = {r.robot_id: r for r in self.robots}
        rows = []
        for t in sorted(self.tasks, key=lambda x: x.priority_value):
            robot_name = (
                robot_map[t.assigned_robot_id].name
                if t.assigned_robot_id in robot_map
                else Fore.RED + "UNASSIGNED" + Style.RESET_ALL
            )
            rows.append([t.task_id, t.task_type, t.priority, robot_name, f"({t.x},{t.y})"])

        print(tabulate(
            rows,
            headers=["Task ID", "Type", "Priority", "Assigned Robot", "Location"],
            tablefmt="rounded_outline",
        ))

    # ── Serialisation helper used by agents ──────────────────────────────────

    def tasks_as_text(self) -> str:
        lines = ["Tasks in the disaster environment:"]
        for t in self.tasks:
            lines.append(f"  {t}")
        return "\n".join(lines)

    def robots_as_text(self) -> str:
        lines = ["Available robots:"]
        for r in self.robots:
            lines.append(f"  {r}")
        return "\n".join(lines)

    def tasks_as_fol(self) -> str:
        lines = []
        for t in self.tasks:
            task_type = t.task_type.replace(" ", "_")
            capability = t.required_capability.replace(" ", "_")
            lines.append(
                f"Task({t.task_id}). "
                f"Type({t.task_id}, {task_type}). "
                f"Priority({t.task_id}, {t.priority}). "
                f"Location({t.task_id}, {t.x}, {t.y}).\n"
                f"Capability({t.task_id}, {capability})."
            )
        return "\n".join(lines)

    def robots_as_fol(self) -> str:
        lines = []
        for r in self.robots:
            capability = r.capability.replace(" ", "_")
            lines.append(
                f"Robot({r.robot_id}). "
                f"Capability({r.robot_id}, {capability}). "
                f"Speed({r.robot_id}, {r.speed})."
            )
        return "\n".join(lines)

