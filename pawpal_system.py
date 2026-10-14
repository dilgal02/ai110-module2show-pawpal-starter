"""PawPal+ core classes: Task, Pet, Owner and Scheduler."""

from dataclasses import dataclass, field, replace
from datetime import datetime

PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """One pet care activity at a set time of day, e.g. a walk at 08:00."""

    description: str
    time: str  # start time as "HH:MM"
    duration_minutes: int
    priority: str = "medium"  # "low", "medium" or "high"
    frequency: str = "daily"  # "once", "daily" or "weekly"
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate the fields and normalize time to zero-padded "HH:MM" so times sort correctly."""
        if self.priority not in PRIORITY_SCORES:
            raise ValueError(f"priority must be one of {list(PRIORITY_SCORES)}, got {self.priority!r}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}, got {self.frequency!r}")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be more than 0")
        self.time = datetime.strptime(self.time, "%H:%M").strftime("%H:%M")

    def priority_score(self) -> int:
        """Return the priority as a number (high = 3, medium = 2, low = 1) for sorting."""
        return PRIORITY_SCORES[self.priority]

    def mark_complete(self) -> None:
        """Mark the task as done."""
        self.completed = True


@dataclass
class Pet:
    """An animal the owner takes care of, plus its care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def edit_task(self, task: Task, changes: dict) -> Task:
        """Replace the task with an updated, re-validated copy and return the new task."""
        index = self.tasks.index(task)
        updated = replace(task, **changes)
        self.tasks[index] = updated
        return updated


@dataclass
class Owner:
    """The pet owner, how much time they have today, and their pets."""

    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every pet's tasks together in one list."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The "brain": pulls every pet's tasks from the owner, then organizes them into a plan."""

    def __init__(self, owner: Owner):
        """Store the owner whose pets' tasks this scheduler will plan."""
        self.owner = owner

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks across all of the owner's pets that aren't completed yet."""
        return [task for task in self.owner.get_all_tasks() if not task.completed]

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return a new list with the highest priority first, ties broken by earlier time."""
        return sorted(tasks, key=lambda task: (-task.priority_score(), task.time))

    def build_plan(self) -> list[Task]:
        """Pick pending tasks by priority until the owner's time runs out, and return them in time order."""
        plan = []
        minutes_left = self.owner.available_minutes
        for task in self.sort_tasks(self.get_pending_tasks()):
            if task.duration_minutes <= minutes_left:
                plan.append(task)
                minutes_left -= task.duration_minutes
        return sorted(plan, key=lambda task: task.time)
