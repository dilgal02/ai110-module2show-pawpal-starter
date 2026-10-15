"""Tests for the PawPal+ classes in pawpal_system.py."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", "08:00", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", "07:30", 10, "high"))

    assert len(pet.tasks) == 1


def test_sort_by_time_orders_tasks_earliest_first():
    owner = Owner("Jordan", available_minutes=120)
    tasks = [
        Task("Evening walk", "18:30", 30),
        Task("Feeding", "7:30", 10),
        Task("Vet meds", "10:00", 5),
        Task("Morning walk", "9:00", 30),
    ]

    sorted_tasks = Scheduler(owner).sort_by_time(tasks)

    assert [task.time for task in sorted_tasks] == ["07:30", "09:00", "10:00", "18:30"]
    assert tasks[0].description == "Evening walk"  # the original list is left unchanged


def test_filter_tasks_by_status_and_pet_name():
    owner = Owner("Jordan", available_minutes=120)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    walk = Task("Morning walk", "08:00", 30)
    feeding = Task("Feeding", "07:30", 10)
    play = Task("Play time", "17:00", 15)
    mochi.add_task(walk)
    luna.add_task(feeding)
    luna.add_task(play)
    feeding.mark_complete()
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(completed=True) == [feeding]
    assert scheduler.filter_tasks(completed=False) == [walk, play]
    assert scheduler.filter_tasks(pet_name="luna") == [feeding, play]
    assert scheduler.filter_tasks(completed=False, pet_name="Luna") == [play]
    assert scheduler.filter_tasks() == [walk, feeding, play]
    assert scheduler.filter_tasks(pet_name="Rex") == []


def test_completing_daily_task_adds_next_day_occurrence():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    walk = Task("Morning walk", "08:00", 30, "high", "daily")
    pet.add_task(walk)
    scheduler = Scheduler(owner)

    next_walk = scheduler.complete_task(walk)

    assert walk.completed is True
    assert next_walk.completed is False
    assert next_walk.due_date == walk.due_date + timedelta(days=1)
    assert (next_walk.description, next_walk.time, next_walk.frequency) == ("Morning walk", "08:00", "daily")
    assert pet.tasks == [walk, next_walk]
    assert scheduler.build_plan() == []  # tomorrow's walk isn't part of today's plan
    assert scheduler.complete_task(walk) is None  # completing it again doesn't add a duplicate
    assert len(pet.tasks) == 2


def test_completing_weekly_task_adds_occurrence_one_week_later():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Luna", "cat")
    owner.add_pet(pet)
    brushing = Task("Brushing", "12:15", 10, "low", "weekly", due_date=date(2026, 10, 14))
    pet.add_task(brushing)

    next_brushing = Scheduler(owner).complete_task(brushing)

    assert next_brushing.due_date == date(2026, 10, 21)


def test_completing_one_time_task_adds_nothing():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Luna", "cat")
    owner.add_pet(pet)
    vet_visit = Task("Vet visit", "15:00", 60, "high", "once")
    pet.add_task(vet_visit)

    assert Scheduler(owner).complete_task(vet_visit) is None
    assert vet_visit.completed is True
    assert pet.tasks == [vet_visit]


def test_detect_conflicts_warns_about_same_time_and_overlapping_tasks():
    owner = Owner("Jordan", available_minutes=120)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Morning walk", "08:00", 30))
    luna.add_task(Task("Feeding", "08:00", 10))  # same start time, different pet
    mochi.add_task(Task("Brushing", "08:20", 10))  # starts during the walk, same pet

    warnings = Scheduler(owner).detect_conflicts()

    assert warnings == [
        "Conflict on " + str(date.today()) + ": Mochi's Morning walk at 08:00 (30 min) overlaps Luna's Feeding at 08:00",
        "Conflict on " + str(date.today()) + ": Mochi's Morning walk at 08:00 (30 min) overlaps Mochi's Brushing at 08:20",
    ]


def test_detect_conflicts_ignores_back_to_back_other_days_and_completed_tasks():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    done = Task("Breakfast", "08:00", 10)
    done.mark_complete()
    pet.add_task(Task("Morning walk", "08:00", 30))
    pet.add_task(Task("Feeding", "08:30", 10))  # starts right as the walk ends
    pet.add_task(Task("Morning walk", "08:00", 30, due_date=date.today() + timedelta(days=1)))
    pet.add_task(done)

    assert Scheduler(owner).detect_conflicts() == []


def test_next_available_slot_finds_first_gap_that_fits():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Morning walk", "08:00", 30))  # busy 08:00-08:30
    pet.add_task(Task("Feeding", "08:30", 10))  # busy 08:30-08:40
    pet.add_task(Task("Meds", "09:00", 5))  # busy 09:00-09:05
    scheduler = Scheduler(owner)

    assert scheduler.next_available_slot(10, earliest="07:00") == "07:00"  # free before the first task
    assert scheduler.next_available_slot(20, earliest="08:00") == "08:40"  # exactly fills the gap before meds
    assert scheduler.next_available_slot(25, earliest="08:00") == "09:05"  # too long for that gap
    assert scheduler.next_available_slot(10, earliest="08:15") == "08:40"  # starting mid-walk jumps past it

    pet.add_task(Task("Brushing", scheduler.next_available_slot(20, earliest="08:00"), 20))
    assert scheduler.detect_conflicts() == []  # a task placed in the slot doesn't clash


def test_next_available_slot_ignores_done_and_other_days_and_gives_up_at_midnight():
    owner = Owner("Jordan", available_minutes=120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    tomorrow = date.today() + timedelta(days=1)
    breakfast = Task("Breakfast", "08:00", 30)
    breakfast.mark_complete()
    pet.add_task(breakfast)
    pet.add_task(Task("Walk", "08:00", 30, due_date=tomorrow))
    pet.add_task(Task("Late walk", "23:00", 30))
    scheduler = Scheduler(owner)

    assert scheduler.next_available_slot(30, earliest="08:00") == "08:00"
    assert scheduler.next_available_slot(30, earliest="08:00", day=tomorrow) == "08:30"
    assert scheduler.next_available_slot(45, earliest="23:00") is None
