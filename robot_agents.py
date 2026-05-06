from __future__ import annotations

import time
from typing import List
from colorama import Fore, Style
from config import SPEED_DELAY
from robot_model import Robot
from task_generator import Task

class RobotAgent:

    def __init__(self, robot: Robot) -> None:
        self.robot = robot

    # ── Task loading ──────────────────────────────────────────────────────────

    def load_tasks(self, tasks: List[Task]) -> None:

        self.robot.assigned_tasks = sorted(tasks, key=lambda t: t.priority_value)

    # ── Execution ─────────────────────────────────────────────────────────────

    def execute_tasks(self, *, simulate_delay: bool = True) -> None:

        if not self.robot.assigned_tasks:
            print(
                Fore.WHITE + f"  [{self.robot.robot_id}] {self.robot.name}: "
                + Style.DIM + "no tasks assigned."
                + Style.RESET_ALL
            )
            return

        delay = SPEED_DELAY.get(self.robot.speed, 1)

        for task in self.robot.assigned_tasks:
            colour = (
                Fore.RED    if task.priority == "high"   else
                Fore.YELLOW if task.priority == "medium" else
                Fore.GREEN
            )
            print(
                f"  [{self.robot.robot_id}] {self.robot.name} → "
                f"executing {colour}{task.task_id}{Style.RESET_ALL} "
                f"'{task.task_type}' [{task.priority}] at ({task.x},{task.y})  "
                f"[~{delay}s]"
            )
            if simulate_delay:
                time.sleep(delay * 0.1)   # 0.1× real time so demo is fast

            task.completed = True
            task.assigned_robot_id = self.robot.robot_id  # stamp the robot
            self.robot.completed_tasks.append(task)

        print(
            Fore.WHITE + f"  [{self.robot.robot_id}] {self.robot.name}: "
            + Fore.GREEN + f"{len(self.robot.completed_tasks)} task(s) completed."
            + Style.RESET_ALL
        )


def run_all_robots(robot_agents: List[RobotAgent], *, simulate_delay: bool = True) -> None:

    print(Fore.BLUE + "\n" + "=" * 60)
    print(Fore.BLUE + "  ROBOT EXECUTION PHASE")
    print(Fore.BLUE + "=" * 60)

    for agent in robot_agents:
        agent.execute_tasks(simulate_delay=simulate_delay)