"""Display helpers shared by the CLI demo (main.py) and the Streamlit app (app.py)."""

from pawpal_system import Task

PRIORITY_LABELS = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
STATUS_LABELS = {True: "✅ Done", False: "⏳ Pending"}
# Checked in order, so "Vet meds" gets the vet emoji before the meds one.
TASK_EMOJIS = [
    (("walk",), "🦮"),
    (("feed", "breakfast", "dinner", "meal", "food"), "🍖"),
    (("vet",), "🏥"),
    (("med", "pill"), "💊"),
    (("brush", "groom", "bath"), "🧼"),
    (("play", "toy", "fetch"), "🎾"),
    (("water",), "💧"),
]
DEFAULT_EMOJI = "🐾"


def task_emoji(task: Task) -> str:
    """Pick an emoji from keywords in the task's description, e.g. "Morning walk" -> 🦮, or 🐾 if nothing matches."""
    description = task.description.lower()
    for keywords, emoji in TASK_EMOJIS:
        if any(keyword in description for keyword in keywords):
            return emoji
    return DEFAULT_EMOJI


def task_row(task: Task, pet_name: str) -> dict:
    """Return one task as a table row with readable column names and color-coded priority and status."""
    return {
        "Time": task.time,
        "Task": f"{task_emoji(task)} {task.description}",
        "Pet": pet_name,
        "Duration": f"{task.duration_minutes} min",
        "Priority": PRIORITY_LABELS[task.priority],
        "Status": STATUS_LABELS[task.completed],
    }
