from datetime import time
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

DATA_FILE = Path(__file__).with_name("data.json")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pets")

# Load saved pets and tasks once per browser session; start fresh if there's no file or it can't be read.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=120)
    if DATA_FILE.exists():
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
        except (ValueError, KeyError, TypeError) as error:
            st.session_state.load_error = f"Couldn't read {DATA_FILE.name}, so this starts empty ({error})."
owner = st.session_state.owner
if "load_error" in st.session_state:
    st.warning(st.session_state.load_error, icon="⚠️")

name = st.text_input("Owner name", value=owner.name)
if name != owner.name:
    owner.name = name
    owner.save_to_json(DATA_FILE)

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))
    owner.save_to_json(DATA_FILE)

if owner.pets:
    st.write("Pets: " + ", ".join(f"{pet.name} ({pet.species})" for pet in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Pick a pet and add a task for it.")

if owner.pets:
    # Select by index: st.selectbox returns a copy of object options, so add_task would miss the real pet.
    pet_index = st.selectbox("Pet", range(len(owner.pets)), format_func=lambda i: owner.pets[i].name)
    selected_pet = owner.pets[pet_index]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_time = st.time_input("Time", value=time(8, 0))
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        selected_pet.add_task(Task(task_title, task_time.strftime("%H:%M"), int(duration), priority))
        owner.save_to_json(DATA_FILE)

scheduler = Scheduler(owner)
pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
PRIORITY_LABELS = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def show_task_table(tasks: list[Task]) -> None:
    """Show tasks as a table, keeping the order they're given in."""
    st.table(
        [
            {
                "Time": task.time,
                "Task": task.description,
                "Pet": pet_names[id(task)],
                "Duration": f"{task.duration_minutes} min",
                "Priority": PRIORITY_LABELS[task.priority],
            }
            for task in tasks
        ],
        hide_index=True,
        border="horizontal",
    )


if owner.get_all_tasks():
    show_pet = st.selectbox("Show tasks for", ["All pets"] + [pet.name for pet in owner.pets])
    shown = scheduler.filter_tasks(pet_name=None if show_pet == "All pets" else show_pet)
    st.caption(f"{len(shown)} task(s), sorted by time")
    show_task_table(scheduler.sort_by_time(shown))

    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        st.warning(warning, icon="⚠️")
    if not conflicts:
        st.success("No overlapping tasks.", icon="✅")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(
    f"Picks today's pending tasks by priority until your {owner.available_minutes} minutes run out, "
    "then lists them in time order."
)

if st.button("Generate schedule"):
    plan = scheduler.build_plan()
    pending = scheduler.get_pending_tasks()
    if not pending:
        st.info("No pending tasks for today. Add one above.")
    else:
        if plan:
            used = sum(task.duration_minutes for task in plan)
            st.success(
                f"Scheduled {len(plan)} of {len(pending)} tasks, using {used} of {owner.available_minutes} minutes.",
                icon="✅",
            )
            show_task_table(plan)
        planned = {id(task) for task in plan}
        skipped = [task for task in pending if id(task) not in planned]
        if skipped:
            st.warning(
                ", ".join(f"{task.description} for {pet_names[id(task)]} ({task.duration_minutes} min)" for task in skipped),
                title="Didn't fit in the time left",
                icon="⏳",
            )
