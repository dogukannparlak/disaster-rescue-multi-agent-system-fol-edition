from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from environment import DisasterEnvironment

class BasePlannerAgent(ABC):

    @abstractmethod
    def run(self, env: "DisasterEnvironment") -> str: ...

class BaseAssignmentAgent(ABC):

    @abstractmethod
    def run(self, env: "DisasterEnvironment", plan_str: str) -> Dict[str, str]: ...

class BaseCriticAgent(ABC):

    @abstractmethod
    def run(
        self,
        env: "DisasterEnvironment",
        assignment: Dict[str, str],
    ) -> Tuple[str, Dict[str, str]]: ...
