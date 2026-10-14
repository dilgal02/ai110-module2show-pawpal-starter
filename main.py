"""Temporary testing ground: build a small owner/pet setup and print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task

owner = Owner("Jordan", available_minutes=120)

mochi = Pet("Mochi", "dog")
luna = Pet("Luna", "cat")
owner.add_pet(mochi)
owner.add_pet(luna)

mochi.add_task(Task("Morning walk", "08:00", 30, "high"))
mochi.add_task(Task("Evening walk", "18:30", 30, "medium"))
luna.add_task(Task("Feeding", "07:30", 10, "high"))
luna.add_task(Task("Play time", "17:00", 15, "low"))

pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}

print("Today's Schedule")
print("================")
for task in Scheduler(owner).build_plan():
    print(f"{task.time} — {task.description} for {pet_names[id(task)]} ({task.duration_minutes} min) [priority: {task.priority}]")
