from dataclasses import dataclass, field, asdict


class Tally:
    def __init__(self, start: int = 0) -> None:
        self._count = 0

    def increment(self) -> None:
        self._count += 1

    @property
    def count(self) -> int:
        return self._count

    def __repr__(self) -> str:
        return f"Tally(count={self._count})"


@dataclass
class Task:
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)


c = Tally()
c.increment()
print(c, c.count)


t = Task("write code")
q = Task("write code", tags=["idk"])
print(t, t == Task("write code"), asdict(t))


