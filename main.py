"""Temporary testing ground: build a small owner/pet setup and print today's schedule."""

from dataclasses import replace

from tabulate import tabulate

from formatting import task_row
from pawpal_system import Owner, Pet, Scheduler, Task

owner = Owner("Jordan", available_minutes=120)

mochi = Pet("Mochi", "dog")
luna = Pet("Luna", "cat")
owner.add_pet(mochi)
owner.add_pet(luna)

# Added out of time order on purpose (and "8:00" without the leading zero) so the sorting has work to do.
breakfast = Task("Breakfast", "07:00", 10, "high")
mochi.add_task(Task("Evening walk", "18:30", 30, "medium"))
luna.add_task(Task("Play time", "17:00", 15, "low"))
mochi.add_task(Task("Morning walk", "8:00", 30, "high"))
luna.add_task(Task("Brushing", "12:15", 10, "low"))
mochi.add_task(breakfast)
luna.add_task(Task("Feeding", "07:30", 10, "high"))
# Same start time as Mochi's morning walk, so the conflict check has something to catch.
luna.add_task(Task("Medication", "08:00", 5, "high"))
breakfast.mark_complete()

pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
scheduler = Scheduler(owner)


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print a heading, then the tasks as a table."""
    print(f"\n{title}")
    print(tabulate([task_row(task, pet_names[id(task)]) for task in tasks], headers="keys", tablefmt="rounded_outline"))


print_tasks("All tasks, in the order they were added", owner.get_all_tasks())
print_tasks("All tasks, sorted by time", scheduler.sort_by_time(owner.get_all_tasks()))
print_tasks("Luna's tasks", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")))
print_tasks("Completed tasks", scheduler.filter_tasks(completed=True))
print_tasks("Mochi's pending tasks", scheduler.sort_by_time(scheduler.filter_tasks(completed=False, pet_name="mochi")))
print_tasks("Today's Schedule", scheduler.build_plan())

# Priority scheduling: the order build_plan() picks tasks in, then the same tasks with less time available.
print_tasks("Pending tasks by priority, then time", scheduler.sort_tasks(scheduler.get_pending_tasks()))
short_scheduler = Scheduler(replace(owner, available_minutes=60))
short_plan = short_scheduler.build_plan()
planned = {id(task) for task in short_plan}
print_tasks("Today's Schedule with only 60 minutes", short_plan)
print_tasks("Didn't fit in 60 minutes", [task for task in short_scheduler.sort_tasks(short_scheduler.get_pending_tasks()) if id(task) not in planned])

print("\nConflict check")
warnings = scheduler.detect_conflicts()
for warning in warnings:
    print(f"⚠️  {warning}")
if not warnings:
    print("✅ No conflicts found.")
