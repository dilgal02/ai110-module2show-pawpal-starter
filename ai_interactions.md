# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code (agent mode in VS Code) for Challenge 1. I gave it the challenge as written: add a third algorithmic capability that goes beyond the basic requirements (the examples were "next available slot" or weighted prioritization), then document the workflow here. I didn't tell it which one to pick. It chose **next available slot**, because it fixes the problem the conflict warnings point out: once the app says two tasks clash, the owner needs to know where else the task could go.

**What did the agent do?**

1. Read `pawpal_system.py`, `tests/test_pawpal.py` and this file to see the existing scheduler methods and test style.
2. Added `Scheduler.next_available_slot(duration_minutes, earliest="00:00", day=None)` to `pawpal_system.py`. It returns the earliest `"HH:MM"` start, at or after `earliest`, where a task of that length doesn't overlap anything, or `None` if it can't finish before midnight.
   - Only pending tasks on that day take up time. Completed tasks and tasks on other days are ignored, which matches how `detect_conflicts()` works.
   - The algorithm sorts the busy time windows by start, then walks through them once. If the new task fits before the next busy window, that's the answer. Otherwise it jumps to the end of that window. That's O(n log n) for the sort plus one pass.
   - Back-to-back is allowed (a task can start exactly when another ends), and a duration of 0 or less raises a `ValueError`, the same rule `Task` uses.
3. Added two tests to `tests/test_pawpal.py`:
   - `test_next_available_slot_finds_first_gap_that_fits`: free time before the first task, a gap that fits exactly, a gap that's too short, and a start time in the middle of a task. It also checks that a task placed in the suggested slot gives no conflict warnings.
   - `test_next_available_slot_ignores_done_and_other_days_and_gives_up_at_midnight`: completed tasks and tomorrow's tasks don't block today, the `day` argument works, and it returns `None` when the task would run past midnight.
4. Ran `python -m pytest`: 11 passed (the 9 existing tests plus the 2 new ones) on the first run.
5. Filled in this section.

**Files modified**

| File | Change |
|------|--------|
| `pawpal_system.py` | New method `Scheduler.next_available_slot()` (20 lines) |
| `tests/test_pawpal.py` | 2 new tests (35 lines) |
| `ai_interactions.md` | This Agent Workflow section |

It didn't touch `app.py`, `main.py` or the README. It offered to update them instead of doing it, which is the rule I set after the first session.

**What did you have to verify or fix manually?**

No code fixes were needed: both new tests passed on the first run, and the existing 9 still pass. What needed a human decision instead were the choices the agent made on its own:

- **The day ends at midnight.** A task has to finish by 24:00. The scheduler has no "day end" setting, so a slot like 23:30 is still allowed even though nobody walks a dog then.
- **It ignores the owner's available minutes.** It only looks for free time on the clock. Whether the task still fits in today's time budget is still `build_plan()`'s job.
- **It isn't used in the app or `main.py` yet.** For now it's only available in Python and the tests.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
