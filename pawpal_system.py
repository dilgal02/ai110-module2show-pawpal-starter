"""PawPal+ core classes (skeleton generated from diagrams/uml.mmd, no logic yet)."""

from dataclasses import dataclass, field
from datetime import time

PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
TIME_OF_DAY_ORDER = {"morning": 0, None: 1, "evening": 2}  # order used when placing chosen tasks


def add_minutes(start: time, minutes: int) -> time:
    """Return the time `minutes` after `start` (datetime.time doesn't support + timedelta)."""
    pass


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

    def __post_init__(self) -> None:
        """Raise ValueError if priority or preferred_time isn't an allowed value, or duration isn't positive."""
        pass

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
        """Add a pet to this owner. Raise ValueError if a pet with that name already exists."""
        pass

    def add_task(self, task: Task) -> None:
        """Add a care task to the to-do list. Raise ValueError if task.pet isn't one of this owner's pets."""
        pass

    def edit_task(self, pet_name: str, title: str, changes: dict) -> None:
        """Replace the task matching pet_name + title with an updated copy.

        Uses dataclasses.replace(), so unknown field names raise TypeError and
        bad values get caught by Task.__post_init__.
        """
        pass


@dataclass
class DailyPlan:
    """The result of scheduling: what got scheduled, what got skipped, and why."""

    day_start: time
    available_minutes: int
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
        """Return a readable explanation of the plan, e.g. minutes used out of available and why tasks were skipped."""
        pass

    def to_table(self) -> list[dict]:
        """Return the plan as rows for st.table() in the Streamlit app."""
        pass


class Scheduler:
    """Builds a daily plan from the owner's tasks and available time."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return a new list sorted by priority, highest first (doesn't reorder owner.tasks)."""
        pass

    def order_by_preferred_time(self, tasks: list[Task]) -> list[Task]:
        """Return a new list ordered morning -> no preference -> evening."""
        pass

    def build_plan(self) -> DailyPlan:
        """Choose tasks by priority until time runs out, order them by preferred time, then assign start times.

        The time budget is capped so the plan never runs past midnight.
        """
        pass
