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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
