"""PawPal+ core classes (skeleton generated from diagrams/uml.mmd, no logic yet)."""

from dataclasses import dataclass, field
from datetime import time


@dataclass
class Pet:
    """An animal the owner takes care of."""

    name: str
    species: str


@dataclass
class Task:
    """One pet care activity, e.g. a walk or feeding."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium" or "high"
    pet: Pet
    preferred_time: str | None = None  # "morning", "evening" or None

    def priority_score(self) -> int:
        """Return the priority as a number (high = 3, medium = 2, low = 1) for sorting."""
        pass


@dataclass
class Owner:
    """The pet owner, their pets and their care to-do list."""

    name: str
    available_minutes: int
    day_start: time = time(8, 0)
    pets: list[Pet] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def add_task(self, task: Task) -> None:
        """Add a care task to the to-do list."""
        pass

    def edit_task(self, title: str, changes: dict) -> None:
        """Find the task with this title and update the given fields."""
        pass


@dataclass
class DailyPlan:
    """The result of scheduling: what got scheduled, what got skipped, and why."""

    scheduled: list[tuple[Task, time, time, str]] = field(default_factory=list)  # (task, start, end, reason)
    skipped: list[tuple[Task, str]] = field(default_factory=list)  # (task, reason)

    def add_entry(self, task: Task, start: time, reason: str) -> None:
        """Schedule a task at the given start time (end time comes from its duration)."""
        pass

    def skip(self, task: Task, reason: str) -> None:
        """Record a task that didn't make it into the plan."""
        pass

    def total_minutes(self) -> int:
        """Return the total minutes of all scheduled tasks."""
        pass

    def explain(self) -> str:
        """Return a readable explanation of why the plan looks like this."""
        pass

    def to_table(self) -> list[dict]:
        """Return the plan as rows for st.table() in the Streamlit app."""
        pass


class Scheduler:
    """Builds a daily plan from the owner's tasks and available time."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks in the order they should be scheduled (priority first, then preferred time)."""
        pass

    def build_plan(self) -> DailyPlan:
        """Fit the owner's tasks into their available time and return the plan."""
        pass
