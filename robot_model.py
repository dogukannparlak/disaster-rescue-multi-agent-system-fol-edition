from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
from config import ROBOT_DEFINITIONS

if TYPE_CHECKING:
    from task_generator import Task

@dataclass
class Robot:

    robot_id: str
    name: str
    capability: str          # matches Task.required_capability
    speed: str               # "fast" | "medium" | "slow"
    assigned_tasks: List["Task"] = field(default_factory=list)
    completed_tasks: List["Task"] = field(default_factory=list)

    def can_handle(self, task: "Task") -> bool:

        return self.capability.lower() == task.required_capability.lower()

    def __str__(self) -> str:
        return f"[{self.robot_id}] {self.name} | capability={self.capability} | speed={self.speed}"

def build_robot_fleet() -> List[Robot]:

    return [
        Robot(robot_id=rid, name=name, capability=cap, speed=speed)
        for rid, name, cap, speed in ROBOT_DEFINITIONS
    ]

