# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- **Priority-based daily plan:** `Scheduler.build_plan()` takes today's pending tasks across all pets, highest priority first (earlier time breaks ties), and keeps adding them while they fit in the owner's available minutes. The plan is shown in time order, with the minutes used and any tasks that didn't fit.
- **Sorting by time:** `Scheduler.sort_by_time()` lists tasks chronologically with `sorted()` and a lambda key on the `"HH:MM"` time. Times are zero-padded when a task is created, so `"9:00"` correctly sorts before `"10:00"`.
- **Filtering by pet or status:** `Scheduler.filter_tasks()` narrows tasks by pet name (case-insensitive), by completed/pending, or both. In the app, the "Show tasks for" dropdown filters the task table by pet.
- **Conflict warnings:** `Scheduler.detect_conflicts()` uses `Task.overlaps()` to flag any two pending tasks on the same day whose time windows overlap, whether they're for the same pet or different pets. That includes tasks at the exact same start time; back-to-back tasks are fine. It only warns and never blocks or crashes, so the owner decides what to move.
- **Daily and weekly recurrence:** `Scheduler.complete_task()` marks a task done and, for a daily or weekly task, adds its next occurrence to the same pet, due 1 or 7 days later (`timedelta`). One-time tasks don't repeat, completing a task twice doesn't create a duplicate, and future occurrences stay out of today's plan. *Available from Python through `Scheduler.complete_task()` and covered by the tests; the Streamlit app doesn't have a "complete" button yet.*
- **Input validation:** `Task` rejects unknown priorities or frequencies, durations of 0 or less, and invalid times like `"25:00"` as soon as it's created or edited.

See [Smarter Scheduling](#-smarter-scheduling) for how each algorithm works.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

The scheduling logic lives in `pawpal_system.py` and is built from four classes:

- **`Task`**: a single care activity with a description, start time (`"HH:MM"`), duration, priority (low/medium/high), frequency (once/daily/weekly) and completion status. It checks its own values when it's created, and `mark_complete()` marks it as done.
- **`Pet`**: a pet's name and species, plus its own list of tasks. `add_task()` and `edit_task()` manage that list.
- **`Owner`**: the owner's name, how many minutes they have available today, and their pets. `get_all_tasks()` returns every pet's tasks together in one list.
- **`Scheduler`**: the "brain". It reads tasks only through `Owner.get_all_tasks()`, so it plans across all pets at once. `build_plan()` drops completed tasks, sorts the rest by priority (earlier time breaks ties), keeps adding tasks while they fit in the owner's available minutes, and returns the chosen tasks in time order.

How they work together: an `Owner` has many `Pet`s and each `Pet` has many `Task`s. The `Scheduler` is given the `Owner`, gathers all tasks through it, and produces today's plan. `main.py` builds a small example (one owner, two pets, four tasks) and prints the schedule. `tests/test_pawpal.py` checks task completion and adding tasks to a pet.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
$ python main.py
Today's Schedule
================
07:30 — Feeding for Luna (10 min) [priority: high]
08:00 — Morning walk for Mochi (30 min) [priority: high]
17:00 — Play time for Luna (15 min) [priority: low]
18:30 — Evening walk for Mochi (30 min) [priority: medium]
```

## 🧪 Testing PawPal+

Run the tests from the project folder with the virtual environment active:

```bash
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pytest
```

Use `python -m pytest` rather than plain `pytest`: plain `pytest` can't import `pawpal_system` from the `tests/` folder.

### What the tests cover

The 9 tests in `tests/test_pawpal.py` check:

- **Tasks and pets:** `mark_complete()` marks a task done, and `add_task()` adds it to the pet.
- **Sorting:** `sort_by_time()` returns tasks in chronological order, including times typed without a leading zero (`"9:00"` before `"10:00"`), and leaves the original list unchanged.
- **Filtering:** `filter_tasks()` by pet name (ignoring case), by completion status, both together, neither, and an unknown pet name.
- **Recurring tasks:** completing a daily task adds a copy due the next day to the same pet, keeps it out of today's plan, and doesn't add a second copy if completed twice. Weekly tasks repeat 7 days later; one-time tasks don't repeat.
- **Conflict detection:** `detect_conflicts()` flags two tasks at the same time (different pets) and a task that starts during another one (same pet), and ignores back-to-back tasks, tasks on other days and completed tasks.

### Test output

```
$ python -m pytest
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/repackifymacbook/Desktop/Education/4 Semester/AI Engineering/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 9 items

tests/test_pawpal.py .........                                           [100%]

============================== 9 passed in 0.01s ===============================
```

### Confidence Level: ★★★☆☆ (3/5)

All 9 tests pass, and each Smarter Scheduling feature has tests behind it, so the main flows work. It isn't higher because:

- `build_plan()`'s core job, choosing tasks by priority until the owner's time runs out, has no dedicated test yet.
- Manual checks found three edge cases that don't behave correctly yet and aren't covered by tests:
  - `sort_by_time()` ignores the due date, so tomorrow's copy of a recurring task can sort ahead of today's tasks.
  - Completing an overdue daily task creates a copy that's still overdue, so it shows up in today's plan again.
  - `edit_task()` changes the wrong task when a pet has two identical tasks.

## 📐 Smarter Scheduling

On top of the basic plan, the `Scheduler` can sort tasks by time, filter them, warn about overlapping tasks and repeat daily/weekly tasks. Run `python main.py` to see all four in the terminal.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | By start time, or by priority with earlier time breaking ties |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.get_pending_tasks()` | By pet name and/or completion status; the plan only uses tasks due today |
| Conflict handling | `Scheduler.detect_conflicts()`, `Task.overlaps()`, `Task.time_window()` | Warns about overlapping time slots, for the same pet or different pets |
| Recurring tasks | `Scheduler.complete_task()`, `Task.mark_complete()` | Completing a daily/weekly task adds its next occurrence |

### Sorting by time: `Scheduler.sort_by_time()`

- Returns a new list with the earliest task first, using `sorted(tasks, key=lambda task: task.time)`.
- Comparing the `"HH:MM"` strings directly works because `Task` zero-pads every time when it's created (`"8:00"` becomes `"08:00"`), so text order matches clock order.
- `build_plan()` uses `sort_tasks()` (highest priority first, ties broken by earlier time) to decide which tasks fit in the owner's time, then `sort_by_time()` to return them in the order they happen.

### Filtering: `Scheduler.filter_tasks(completed=None, pet_name=None)`

- `completed=True` / `False` keeps only finished or unfinished tasks; `pet_name="Luna"` keeps only that pet's tasks. Pass both to combine them, or neither to get every task.
- Pet names are matched ignoring case, and an unknown pet name returns an empty list instead of an error.
- Separately, `get_pending_tasks()` gives `build_plan()` only the tasks that aren't completed and are due today or earlier, and `build_plan()` skips any task that doesn't fit in the time left.

### Conflict detection: `Scheduler.detect_conflicts()`

- Returns one warning string per pair of pending tasks whose times overlap, for example:
  `Conflict on 2026-10-14: Mochi's Morning walk at 08:00 (30 min) overlaps Luna's Medication at 08:00`
- It checks overlapping durations, not just identical start times: a 30-minute walk at 08:00 also conflicts with brushing at 08:20. Back-to-back tasks (one ends at 08:30, the next starts at 08:30), tasks on different days and completed tasks don't count.
- It only warns and never raises, so the program keeps running and the owner decides what to move. It doesn't change the plan.
- `Task.time_window()` turns a task into start/end minutes after midnight, `Task.overlaps()` holds the overlap rule, and `detect_conflicts()` checks every pair with `itertools.combinations`. Checking every pair was picked over a faster but harder to read approach; see section 2b of `reflection.md`.

### Recurring tasks: `Scheduler.complete_task()`

- Each `Task` has a `due_date` (today by default) and a `frequency` of `"once"`, `"daily"` or `"weekly"`.
- `Scheduler.complete_task(task)` marks the task done and, for a daily or weekly task, adds a new copy to the same pet with the due date moved forward 1 or 7 days (`timedelta`). A one-time task gets no copy.
- The copy is built by `Task.mark_complete()`, which also returns nothing if the task was already completed, so completing a task twice doesn't create two copies.
- Tomorrow's copy isn't part of today's plan, because `get_pending_tasks()` only includes tasks due today or earlier.
- Call `scheduler.complete_task(task)` rather than `task.mark_complete()` on its own: a `Task` doesn't know which pet it belongs to, so only the scheduler can add the next occurrence to the right pet.

## 💾 Saving Data (Persistence)

PawPal+ remembers the owner, pets and tasks between runs by saving them to `data.json` in the project folder.

### How it works

1. **Starting the app:** the first time a browser session opens the app, `app.py` looks for `data.json`. If it's there, `Owner.load_from_json()` rebuilds the owner, pets and tasks from it. If not, the app starts with an empty owner (Jordan, 120 minutes).
2. **Making changes:** every time you click **Add pet** or **Add task**, or change the owner's name, the app calls `owner.save_to_json()`, which rewrites `data.json` with everything currently in the app.
3. **Coming back:** reload the page or restart `streamlit run app.py`, and your pets and tasks are loaded again.
4. **Starting over:** delete `data.json`.

If `data.json` can't be read (broken JSON, or a bad value like priority `"urgent"`), the app doesn't crash. It shows a warning and starts empty, and the next save replaces the broken file.

### What's in the file

```json
{
  "name": "Alex",
  "available_minutes": 120,
  "pets": [
    {
      "name": "Mochi",
      "species": "dog",
      "tasks": [
        {
          "description": "Morning walk",
          "time": "08:00",
          "duration_minutes": 20,
          "priority": "high",
          "frequency": "daily",
          "completed": false,
          "due_date": "2026-10-14"
        }
      ]
    }
  ]
}
```

### Using it from Python

```python
from pawpal_system import Owner

owner.save_to_json("data.json")            # write the owner, pets and tasks
owner = Owner.load_from_json("data.json")  # read them back
```

- `save_to_json()` turns the owner, their pets and every task into nested dictionaries with `dataclasses.asdict()` and writes them with `json.dump()`. Due dates are stored as `"YYYY-MM-DD"` text.
- `load_from_json()` is a class method that reads the file and rebuilds real `Pet` and `Task` objects. Every task goes through `Task`'s normal checks again, so times are zero-padded and bad values raise `ValueError`.
- `main.py` doesn't use the file. It always builds the same demo data.

### Files modified

| File | Change |
|------|--------|
| `pawpal_system.py` | Added `Owner.save_to_json()` and `Owner.load_from_json()` |
| `app.py` | Loads `data.json` when a session starts, saves after adding a pet or task or renaming the owner, and shows a warning if the file can't be read |
| `tests/test_pawpal.py` | 2 tests: saving and loading gives back the same owner, pets and tasks, and a file with an invalid priority raises `ValueError` |
| `README.md` | This section, and the "Current limits" line in the Demo Walkthrough |

## 📸 Demo Walkthrough

Start the app with `streamlit run app.py` (with the virtual environment active).

### What you can do in the app

- **Owner & Pets:** enter the owner's name and add pets with a name and species (dog, cat or other). Added pets are listed under the form.
- **Tasks:** pick a pet, then enter a task title, start time, duration (1–240 minutes) and priority (low, medium or high), and click **Add task**.
- **Task list:** every task appears in one table sorted by time, with its pet, duration and priority. The **Show tasks for** dropdown narrows the table to one pet. Below the table, a yellow warning appears for each pair of overlapping tasks, or a green "No overlapping tasks." if there are none.
- **Build Schedule:** **Generate schedule** builds today's plan within the owner's 120 minutes and shows what was scheduled and what didn't fit.

Current limits: the available time is fixed at 120 minutes, and tasks can't be edited, completed or deleted in the app yet. Pets and tasks are saved to `data.json`, so they're still there after a reload (see [Saving Data](#-saving-data-persistence)).

### Example workflow

1. **Add two pets.** Type `Mochi`, pick `dog`, click **Add pet**; then `Luna`, `cat`, **Add pet**. The app shows "Pets: Mochi (dog), Luna (cat)".
2. **Add four tasks, out of time order on purpose:**

   | Pet | Task | Time | Duration | Priority |
   |-----|------|------|----------|----------|
   | Mochi | Evening walk | 18:30 | 30 min | medium |
   | Luna | Long grooming | 13:00 | 90 min | low |
   | Mochi | Morning walk | 08:00 | 30 min | high |
   | Luna | Medication | 08:00 | 5 min | high |

3. **Check the task list.** It reads "4 task(s), sorted by time" and lists Morning walk (08:00), Medication (08:00), Long grooming (13:00), Evening walk (18:30). Below it, a warning appears:
   > ⚠️ Conflict on 2026-10-14: Mochi's Morning walk at 08:00 (30 min) overlaps Luna's Medication at 08:00
4. **Filter by pet.** Choose `Luna` in **Show tasks for**; the table shows only Medication and Long grooming. Switch back to `All pets`.
5. **Generate the schedule.** Click **Generate schedule**. The app shows "✅ Scheduled 3 of 4 tasks, using 65 of 120 minutes." and this plan:

   | Time | Task | Pet | Duration | Priority |
   |------|------|-----|----------|----------|
   | 08:00 | Morning walk | Mochi | 30 min | 🔴 High |
   | 08:00 | Medication | Luna | 5 min | 🔴 High |
   | 18:30 | Evening walk | Mochi | 30 min | 🟡 Medium |

   followed by "⏳ Didn't fit in the time left: Long grooming for Luna (90 min)".

### Scheduler behaviors shown

- **Sorting by time** (`sort_by_time()`): the tasks were added in a random order but always appear chronologically.
- **Filtering** (`filter_tasks()`): the **Show tasks for** dropdown shows one pet's tasks.
- **Conflict warnings** (`detect_conflicts()`): the two 08:00 tasks are flagged even though they belong to different pets. It's only a warning, so both stay in the plan and the owner decides what to move.
- **Priority within a time budget** (`build_plan()`): the high-priority tasks go in first (35 min), then the medium one (65 min total). The low-priority 90-minute grooming would push the total to 155 minutes, over the 120 available, so it's skipped and reported.

Completed-task filtering appears in the CLI demo below. Daily/weekly recurrence isn't in the app or the CLI demo yet; it's covered by the tests (see [Testing PawPal+](#-testing-pawpal)).

### CLI demo: `python main.py`

`main.py` sets up the same kind of scenario in code: two pets and seven tasks added out of time order (one typed as `"8:00"`), Mochi's breakfast marked done, and Luna's medication at the same time as Mochi's morning walk. It then prints the tasks as added, sorted by time, filtered by pet and status, today's schedule, and the conflict check:

```
$ python main.py
All tasks, in the order they were added
=======================================
18:30 — Evening walk for Mochi (30 min) [priority: medium, pending]
08:00 — Morning walk for Mochi (30 min) [priority: high, pending]
07:00 — Breakfast for Mochi (10 min) [priority: high, done]
17:00 — Play time for Luna (15 min) [priority: low, pending]
12:15 — Brushing for Luna (10 min) [priority: low, pending]
07:30 — Feeding for Luna (10 min) [priority: high, pending]
08:00 — Medication for Luna (5 min) [priority: high, pending]

All tasks, sorted by time
=========================
07:00 — Breakfast for Mochi (10 min) [priority: high, done]
07:30 — Feeding for Luna (10 min) [priority: high, pending]
08:00 — Morning walk for Mochi (30 min) [priority: high, pending]
08:00 — Medication for Luna (5 min) [priority: high, pending]
12:15 — Brushing for Luna (10 min) [priority: low, pending]
17:00 — Play time for Luna (15 min) [priority: low, pending]
18:30 — Evening walk for Mochi (30 min) [priority: medium, pending]

Luna's tasks
============
07:30 — Feeding for Luna (10 min) [priority: high, pending]
08:00 — Medication for Luna (5 min) [priority: high, pending]
12:15 — Brushing for Luna (10 min) [priority: low, pending]
17:00 — Play time for Luna (15 min) [priority: low, pending]

Completed tasks
===============
07:00 — Breakfast for Mochi (10 min) [priority: high, done]

Mochi's pending tasks
=====================
08:00 — Morning walk for Mochi (30 min) [priority: high, pending]
18:30 — Evening walk for Mochi (30 min) [priority: medium, pending]

Today's Schedule
================
07:30 — Feeding for Luna (10 min) [priority: high, pending]
08:00 — Morning walk for Mochi (30 min) [priority: high, pending]
08:00 — Medication for Luna (5 min) [priority: high, pending]
12:15 — Brushing for Luna (10 min) [priority: low, pending]
17:00 — Play time for Luna (15 min) [priority: low, pending]
18:30 — Evening walk for Mochi (30 min) [priority: medium, pending]

Conflict check
==============
WARNING: Conflict on 2026-10-14: Mochi's Morning walk at 08:00 (30 min) overlaps Luna's Medication at 08:00
```
