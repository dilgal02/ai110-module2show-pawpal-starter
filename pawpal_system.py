"""PawPal+ core classes: Task, Pet, Owner and Scheduler."""

import json
from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime, timedelta
from itertools import combinations
from pathlib import Path

PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
FREQUENCIES = ("once", "daily", "weekly")
RECURRENCE_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """One pet care activity at a set time of day, e.g. a walk at 08:00."""

    description: str
    time: str  # start time as "HH:MM"
    duration_minutes: int
    priority: str = "medium"  # "low", "medium" or "high"
    frequency: str = "daily"  # "once", "daily" or "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

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

    def time_window(self) -> tuple[int, int]:
        """Return when the task starts and ends as minutes after midnight, e.g. 08:00 for 30 min -> (480, 510)."""
        hours, minutes = map(int, self.time.split(":"))
        start = hours * 60 + minutes
        return start, start + self.duration_minutes

    def overlaps(self, other: "Task") -> bool:
        """Return True if both tasks are on the same day and their times overlap (back-to-back doesn't count)."""
        start, end = self.time_window()
        other_start, other_end = other.time_window()
        return self.due_date == other.due_date and start < other_end and other_start < end

    def mark_complete(self) -> "Task | None":
        """Mark the task as done and return a copy for its next due date, or None if it doesn't repeat.

        Completing a task that's already done returns None, so it can't create the next occurrence twice.
        """
        if self.completed:
            return None
        self.completed = True
        if self.frequency == "once":
            return None
        return replace(self, completed=False, due_date=self.due_date + RECURRENCE_INTERVALS[self.frequency])


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

    def save_to_json(self, path: str | Path = "data.json") -> None:
        """Write the owner, their pets and every pet's tasks to a JSON file, replacing what was there."""
        with open(path, "w", encoding="utf-8") as file:
            json.dump(asdict(self), file, indent=2, default=str)  # default=str turns due_date into "YYYY-MM-DD"

    @classmethod
    def load_from_json(cls, path: str | Path = "data.json") -> "Owner":
        """Rebuild an owner, their pets and tasks from a file written by save_to_json().

        Each task goes through Task's normal checks again, so a file with bad values raises ValueError.
        """
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        pets = [
            Pet(
                pet["name"],
                pet["species"],
                [Task(**{**task, "due_date": date.fromisoformat(task["due_date"])}) for task in pet["tasks"]],
            )
            for pet in data["pets"]
        ]
        return cls(data["name"], data["available_minutes"], pets)


class Scheduler:
    """The "brain": pulls every pet's tasks from the owner, then organizes them into a plan."""

    def __init__(self, owner: Owner):
        """Store the owner whose pets' tasks this scheduler will plan."""
        self.owner = owner

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks across all of the owner's pets that aren't completed and are due today or earlier."""
        today = date.today()
        return [task for task in self.owner.get_all_tasks() if not task.completed and task.due_date <= today]

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task done; for a daily or weekly task, add its next occurrence to the same pet and return it."""
        for pet in self.owner.pets:
            if any(pet_task is task for pet_task in pet.tasks):
                next_task = task.mark_complete()
                if next_task is not None:
                    pet.add_task(next_task)
                return next_task
        raise ValueError(f"{task.description!r} doesn't belong to any of {self.owner.name}'s pets")

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> list[Task]:
        """Return the tasks that match every filter given; a filter left as None matches everything.

        Pet names are compared ignoring case, so "luna" finds Luna's tasks.
        """
        return [
            task
            for pet in self.owner.pets
            if pet_name is None or pet.name.lower() == pet_name.lower()
            for task in pet.tasks
            if completed is None or task.completed == completed
        ]

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return a new list with the highest priority first, ties broken by earlier time."""
        return sorted(tasks, key=lambda task: (-task.priority_score(), task.time))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return a new list with the earliest start time first.

        Comparing the "HH:MM" strings works because Task zero-pads them, so text order matches clock order.
        """
        return sorted(tasks, key=lambda task: task.time)

    def build_plan(self) -> list[Task]:
        """Pick pending tasks by priority until the owner's time runs out, and return them in time order."""
        plan = []
        minutes_left = self.owner.available_minutes
        for task in self.sort_tasks(self.get_pending_tasks()):
            if task.duration_minutes <= minutes_left:
                plan.append(task)
                minutes_left -= task.duration_minutes
        return self.sort_by_time(plan)

    def detect_conflicts(self) -> list[str]:
        """Return a warning for each pair of pending tasks that overlap; empty if none do.

        Only warns, never raises, since the owner may be fine with two quick tasks overlapping.
        Checks every pair, which is plenty fast for the handful of tasks one owner has in a day.
        """
        pending = [(pet, task) for pet in self.owner.pets for task in pet.tasks if not task.completed]
        pending.sort(key=lambda pair: (pair[1].due_date, pair[1].time))  # only so each warning names the earlier task first
        warnings = []
        for (pet, task), (other_pet, other) in combinations(pending, 2):
            if task.overlaps(other):
                warnings.append(
                    f"Conflict on {task.due_date}: {pet.name}'s {task.description} at {task.time} "
                    f"({task.duration_minutes} min) overlaps {other_pet.name}'s {other.description} at {other.time}"
                )
        return warnings

    def next_available_slot(self, duration_minutes: int, earliest: str = "00:00", day: date | None = None) -> str | None:
        """Return the earliest "HH:MM" start, at or after `earliest`, where a task this long overlaps nothing.

        Only pending tasks on `day` (today by default) take up time, and back-to-back is fine. Busy times are
        walked in start order, jumping past each one the new task would overlap. Returns None if it can't finish by midnight.
        """
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be more than 0")
        day = day or date.today()
        earliest_time = datetime.strptime(earliest, "%H:%M")
        start = earliest_time.hour * 60 + earliest_time.minute
        busy = sorted(task.time_window() for task in self.owner.get_all_tasks() if not task.completed and task.due_date == day)
        for busy_start, busy_end in busy:
            if start + duration_minutes <= busy_start:
                break
            start = max(start, busy_end)
        if start + duration_minutes > 24 * 60:
            return None
        return f"{start // 60:02d}:{start % 60:02d}"
