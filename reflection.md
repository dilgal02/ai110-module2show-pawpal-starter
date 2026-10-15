# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Before drawing any UML I reread the scenario in the README and tried to figure out what a user actually needs to *do* in the app. Basically it's a busy pet owner who keeps forgetting stuff, so the app should help them stay on track. I ended up with three core actions:

1. **Add an owner and their pet.** The user puts in some basic info about themselves (name, how much free time they have today, maybe some preferences like "I prefer walks in the morning") and about their pet (name, species/breed). This has to come first, because the scheduler can't plan anything if it doesn't know how much time the owner has or who the tasks are even for.

2. **Add or edit a care task.** The user can create tasks like "morning walk", "feeding", "give meds" or "brushing". Each task needs at least a duration in minutes and a priority (low / medium / high). They should also be able to edit a task later, for example if the walk takes longer than they thought or the meds become more important. These tasks are basically the input for the whole scheduling part.

3. **Generate and view today's plan.** The user clicks a button and gets a daily schedule. The app tries to fit the tasks into the time the owner has, high priority stuff goes first, and if something doesn't fit it gets skipped. The plan should also explain *why* it looks like that (e.g. "meds were scheduled first because they're high priority, grooming was skipped because there was no time left"), because the README says the app should explain its reasoning and not just spit out a list.

From these actions I came up with five classes (the diagram is in `diagrams/uml.mmd`):

- **`Owner`**: the person using the app. It stores their name, how many minutes they have today (`available_minutes`), when their day starts (`day_start`), their list of pets and their list of tasks. It's responsible for adding pets and adding/editing tasks. I put the tasks on the owner and not on each pet because it's basically the owner's to-do list, and the scheduler needs all the tasks in one list anyway.
- **`Pet`**: super simple, just the pet's name and species. It doesn't really *do* anything, it's mostly there so each task knows which animal it's for (so the plan can say "Walk (Mochi)" and not just "Walk" if you have two dogs).
- **`Task`**: one care activity. It has a title, a duration in minutes, a priority, the pet it's for, and an optional preferred time (morning/evening), which is how I handle owner preferences. Its only method is `priority_score()`, which turns high/medium/low into 3/2/1 so tasks are easy to sort.
- **`Scheduler`**: the "brain" of the app. It takes the owner, sorts the tasks (priority first, then preferred time) and fits them into the available time one after another. Anything that doesn't fit gets skipped. All the actual decision making happens here, so this is the main thing I'll write tests for.
- **`DailyPlan`**: the result the scheduler gives back. It keeps a list of scheduled tasks (with start time, end time and a reason) and a list of skipped tasks (with the reason why). It can add up the total minutes, write an explanation of the plan, and turn itself into a table for the Streamlit UI.

For the relationships: an owner has many pets and many tasks, every task is for exactly one pet, the scheduler uses the owner to build a `DailyPlan`, and the plan lists the tasks it scheduled or skipped.

I made `Pet`, `Task`, `Owner` and `DailyPlan` dataclasses because they mostly just hold data, and kept `Scheduler` a normal class since it's all behavior. I also kept the design pretty small on purpose. Stuff like recurring tasks or conflict checking isn't in there yet, I'll add it if I get to the "smarter scheduling" part. I'll probably change some of this once I start coding, but this is my starting point.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, it changed a bit even before I wrote any real logic. After I generated the skeleton in `pawpal_system.py`, I gave the file to the AI and asked if it noticed any missing relationships or potential logic bottlenecks. Some of the stuff it found I honestly wouldn't have caught until much later. These are the changes I made:

1. **Added an `add_minutes()` helper.** I was planning to calculate start/end times with `time + timedelta`, but it turns out Python doesn't allow that for `datetime.time` (I tested it and got a `TypeError`). So now there's one small helper for that. I also decided the plan is never allowed to go past midnight, otherwise a task could end up going from 23:50 to 00:20, which makes no sense.

2. **`edit_task` now takes the pet name too.** Before it was `edit_task(title, changes)`. If two pets both have a task called "Feeding" it would just edit whichever one it found first. Now it's `edit_task(pet_name, title, changes)`. Also it uses `dataclasses.replace()`, so if I make a typo like `"priorty"` it throws an error instead of silently doing nothing.

3. **`add_task` checks that the task's pet actually belongs to the owner.** Otherwise you could add a task for a pet the owner doesn't even have. I also made `add_pet` reject duplicate pet names, because the edit lookup now depends on the pet name.

4. **Validation in `Task`.** Priority was just a string, so something like `"High"` instead of `"high"` would break the sorting later. Now `Task` has a `__post_init__` that checks the priority, the preferred time and that the duration is more than 0.

5. **Split the sorting into two steps.** This was the biggest logic problem. Since tasks are placed back to back from the start of the day, an "evening" task could easily land at 8:10 in the morning, and then the explanation would kind of be lying. Now the scheduler first picks tasks by priority until time runs out (`sort_tasks`), and then puts the picked ones in morning → no preference → evening order (`order_by_preferred_time`) before giving them times.

6. **`DailyPlan` now stores `day_start` and `available_minutes`.** Without them `explain()` couldn't say something like "you used 75 of your 90 minutes".

I didn't take every suggestion though. The AI also mentioned replacing the tuples in `DailyPlan` with a separate `PlanEntry` class, and using an Enum for priority. I skipped both because they add more code than they're worth for a project this size (the AI itself said they were optional), and the validation already covers the priority problem. I updated `diagrams/uml.mmd` so it matches the new skeleton.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My conflict check (`detect_conflicts()`) compares every pair of pending tasks to see if their times overlap, which isn't the fastest way to do it. The first version sorted the tasks by start time and stopped checking as soon as the next task started after the current one ended, so it skipped most of the pairs. When I asked the AI how to simplify it, it suggested just checking every pair with `itertools.combinations` and moving the overlap rule into its own `Task.overlaps()` method. So the tradeoff is readability over speed: the number of comparisons grows with the square of the number of tasks.

I think that's reasonable here because one owner just doesn't have that many tasks in a day. Even a really busy day with 20 tasks is only 190 pairs, which is instant. The old version also only worked because the list was sorted first, so if you didn't know that, the early `break` looked like a bug. And it copied the rest of the list on every loop anyway, so it wasn't even as fast as it looked. The new version is easier to read, and the "do these two tasks overlap?" rule is now in one place where I can test it. The AI wrote the whole loop as one list comprehension, which was more "Pythonic" but honestly harder to read, so I kept the idea but wrote it as a normal `for` loop. If the app ever had to handle thousands of tasks, I'd go back to the sorted version.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude Code inside VS Code pretty much the whole way through, one assignment step at a time. First I had it read the scenario and pick out the three core actions. Then I had it brainstorm the classes with their attributes and methods, turn that into a Mermaid UML diagram, and generate the class skeleton with dataclasses. After that it helped me implement the logic, write `main.py` as a testing ground, write the first pytest tests, and add docstrings and the summary to the README.

The most helpful prompts were the specific ones that asked it to look for problems instead of just building stuff. For example "review the diagram, make sure the relationships make sense and there's no unnecessary complexity", or giving it `pawpal_system.py` and asking if it noticed any missing relationships or logic bottlenecks. Those gave me concrete issues with actual examples. One was that two pets could both have a "Feeding" task, so editing by title would change the wrong one. The least helpful prompts were the open ones like "flesh out the implementation", because the AI took that as permission to do way more than I asked (more on that below). What worked better was pasting the exact requirements from the assignment so it had something specific to stick to.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The biggest one was when I asked it to implement the four classes. It did that, but it also added a lot I never asked for. It kept a fifth `DailyPlan` class with explanations for every task, added overlap checking between tasks, made recurring tasks automatically create their next copy when completed, and added due dates. It also rewrote my UML and added a paragraph to this reflection on its own. Some of it was actually kind of smart, but this is a graded assignment, and I need code that matches the requirements and that I can explain myself. So I told it to keep only what the assignment asks for. It removed the extra class and features and reverted the UML and reflection changes. That left the four required classes, with the `Scheduler` reading tasks through `Owner.get_all_tasks()` like the assignment says.

Another thing I noticed is that the AI changed its mind about the design. At first it put the tasks on `Pet`, then during the UML review it moved them to `Owner`, and then the assignment said they should be on `Pet` after all. So its suggestions can sound reasonable and still not be what the assignment needs, and I had to check them against the actual instructions every time. In the skeleton review I also skipped two of its suggestions (a separate `PlanEntry` class and an Enum for priority) because they added more code than they were worth.

To verify things, I didn't just trust that the code was right:
- I ran `main.py` and checked the schedule by hand. The tasks came out in time order (07:30, 08:00, 17:00, 18:30), and 85 minutes in total fit in the 120 available, so nothing should have been dropped.
- I also had it run a quick check with only 60 minutes available. The 40-minute low-priority brushing got left out like it should, and a task disappeared from the plan after I marked it complete.
- For the AI's claims during the skeleton review, I made it actually test them instead of just believing it. For example, `time + timedelta` really does throw a `TypeError` in Python, and `dataclasses.replace()` really does catch a typo like `"priorty"`.
- The two pytest tests pass (`mark_complete()` changes the status, and `add_task()` increases the pet's task count). That's also how I found out pytest only works from the `.venv` with `python -m pytest`, because plain `pytest` couldn't find `pawpal_system`.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
