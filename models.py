from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Todo:
    id: int
    description: str
    done: bool = False

    def __str__(self):
        status = "✅" if self.done else "⏳"
        return f"{status} [{self.id}] {self.description}"