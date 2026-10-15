"""Temporary testing ground: build a small owner/pet setup and print today's schedule."""

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
    """Print a heading, then one line per task."""
    print(f"\n{title}")
    print("=" * len(title))
    for task in tasks:
        status = "done" if task.completed else "pending"
        print(f"{task.time} — {task.description} for {pet_names[id(task)]} ({task.duration_minutes} min) [priority: {task.priority}, {status}]")


print_tasks("All tasks, in the order they were added", owner.get_all_tasks())
print_tasks("All tasks, sorted by time", scheduler.sort_by_time(owner.get_all_tasks()))
print_tasks("Luna's tasks", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")))
print_tasks("Completed tasks", scheduler.filter_tasks(completed=True))
print_tasks("Mochi's pending tasks", scheduler.sort_by_time(scheduler.filter_tasks(completed=False, pet_name="mochi")))
print_tasks("Today's Schedule", scheduler.build_plan())

print("\nConflict check")
print("==============")
warnings = scheduler.detect_conflicts()
for warning in warnings:
    print(f"WARNING: {warning}")
if not warnings:
    print("No conflicts found.")
