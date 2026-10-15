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

My scheduler looks at four things:

- **Available time.** This is the hard limit. `build_plan()` never schedules more minutes than the owner has (120 in the app).
- **Priority.** High tasks get picked first, then medium, then low. If two tasks have the same priority, the earlier one goes first.
- **Start time and duration.** Every task has a real start time, so the plan is shown in time order and the conflict check can tell when two tasks overlap.
- **Due date and status.** Only tasks that aren't done and are due today or earlier go into today's plan, so tomorrow's copy of a daily walk doesn't show up today.

Time had to be the hard limit, because you can't make more minutes in a day. After that, priority decides what gets dropped, because missing meds or feeding is way worse than missing play time. The morning/evening preferences from my first design didn't make it into the final version, since every task now has an actual start time instead. Conflicts are the one thing I didn't make a hard rule. I specifically asked for a "lightweight" check that only warns instead of blocking or crashing, because sometimes an owner can do two quick things at once, and they know their day better than the app does.

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

I used Claude Code in VS Code as a tool that I directed one assignment step at a time, not as something that builds the whole app for me. Every step followed the same routine: I pasted the exact step from the assignment, it made that one change, and the result had to pass `main.py` and the tests before I committed it. I used it in a few different roles. At the start it was a brainstorming partner for the three core actions, the classes and the first UML. Then it was a reviewer: I gave it my skeleton and my diagram and asked it to find problems. After that it drafted the code and tests one feature at a time, and near the end I used it as a checker for edge cases and for whether the UML still matched the code. The big decisions stayed with me: what's in scope, how the design looks, and what to keep or throw out.

The most helpful prompts were the specific ones that asked it to look for problems instead of just building stuff. For example "review the diagram, make sure the relationships make sense and there's no unnecessary complexity", or giving it `pawpal_system.py` and asking if it noticed any missing relationships or logic bottlenecks. Those gave me concrete issues with actual examples. One was that two pets could both have a "Feeding" task, so editing by title would change the wrong one. The least helpful prompts were the open ones like "flesh out the implementation", because the AI took that as permission to do way more than I asked (more on that below). What worked better was pasting the exact requirements from the assignment so it had something specific to stick to.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The biggest one was when I asked it to implement the four classes. It did that, but it also added a lot I never asked for. It kept a fifth `DailyPlan` class with explanations for every task, added overlap checking between tasks, made recurring tasks automatically create their next copy when completed, and added due dates. It also rewrote my UML and added a paragraph to this reflection on its own. Some of it was actually kind of smart, but this is a graded assignment, and I need code that matches the requirements and that I can explain myself. So I told it to keep only what the assignment asks for. It removed the extra class and features and reverted the UML and reflection changes. That left the four required classes, with the `Scheduler` reading tasks through `Owner.get_all_tasks()` like the assignment says.

Another thing I noticed is that the AI changed its mind about the design. At first it put the tasks on `Pet`, then during the UML review it moved them to `Owner`, and then the assignment said they should be on `Pet` after all. So its suggestions can sound reasonable and still not be what the assignment needs, and I had to check them against the actual instructions every time. In the skeleton review I also skipped two of its suggestions (a separate `PlanEntry` class and an Enum for priority) because they added more code than they were worth.

To verify things, I didn't just trust that the code was right:
- I ran `main.py` and checked the schedule by hand. The tasks came out in time order (07:30, 08:00, 17:00, 18:30), and 85 minutes in total fit in the 120 available, so nothing should have been dropped.
- I also asked for a second check with only 60 minutes available, to see what happens when time runs out. The 40-minute low-priority brushing got left out like it should, and a task disappeared from the plan after I marked it complete.
- For the AI's claims during the skeleton review, I made it actually test them instead of just believing it. For example, `time + timedelta` really does throw a `TypeError` in Python, and `dataclasses.replace()` really does catch a typo like `"priorty"`.
- The two pytest tests pass (`mark_complete()` changes the status, and `add_task()` increases the pet's task count). That's also how I found out pytest only works from the `.venv` with `python -m pytest`, because plain `pytest` couldn't find `pawpal_system`.

**c. AI strategy**

- Which AI coding assistant features were most effective for building your scheduler?
- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
- How did using separate chat sessions for different phases help you stay organized?
- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.

**Most effective features.** The most useful thing was that Claude Code can actually run code, not just write it. After every change it ran `python -m pytest` and `main.py`, and when I asked about edge cases it wrote small throwaway scripts to try them, so I got real output instead of "this should work". It even checked the Streamlit app without a browser (with Streamlit's `AppTest`) and rendered my Mermaid diagram to make sure the syntax was valid. Second was being able to send a message while it was still working. In the middle of the conflict detection I added "do a lightweight strategy that returns a warning instead of crashing", and in the middle of the app changes I asked for `st.success` / `st.warning` / `st.table`, and it adjusted right away instead of me having to redo things afterwards. Third was memory. After the first session, where it did way more than I asked, a "do only what's asked, offer extras in one line" rule got saved, and in the later session it stuck to it. It would say something like "I can also update the README if you want", and I decided when.

**A suggestion I rejected.** When I asked for ideas to improve the scheduler, one of the AI's suggestions was to find the next free time slot and offer to move a task when two tasks clash. Later it also offered to make the schedule skip or move clashing tasks automatically. I didn't take either. I asked for a check that only warns, because moving tasks around on its own would mean the scheduler makes decisions the owner should make, and it would add a lot of logic that's hard to test. Same idea with the conflict code itself: the AI's simplified version was one big list comprehension, and I asked it to judge that on readability and not just on how "Pythonic" it is, so it ended up as a normal `for` loop (more on that in 2b).

**Separate chat sessions.** I did the design, UML, skeleton and core classes in earlier sessions and then started a new one for the "smarter scheduling" part. Each phase ended with a commit, so the new session started from clean, working code, and the AI worked from what was actually in the files instead of from old chat history. That helped, because in the first session it had changed its mind about the design a few times (tasks on `Pet`, then on `Owner`, then back on `Pet`), and none of that back-and-forth followed me into the new session. The one thing I did want to carry over, the "don't do more than I ask" rule, was saved in its memory, so I didn't have to repeat it. I didn't split everything perfectly though: the algorithms, tests, UI and docs all ended up in one long session, and next time I'd start a fresh one for the docs part too.

**Being the "lead architect".** The AI is fast and sounds just as confident when it's wrong as when it's right, so my job was making the decisions and checking the results, not typing the code. I set the scope (the strict-scope rule, and pasting the exact assignment step), I made the design calls (warnings instead of moving tasks, a readable loop over a clever one-liner), and I didn't accept "it works" without seeing tests or output. The prompts that helped most were questions, not orders: "list 3–5 core behaviors to verify", "what are the most important edge cases", "does the UML still match my code", "how could this be simplified". Those questions found three real bugs and an outdated diagram, which a plain "write the tests" wouldn't have. The AI even caught one of its own mistakes: it had written in the README that recurrence is shown in `main.py`, which wasn't true, and it fixed that while writing the demo section. That's exactly why I don't treat anything it writes as final until it's checked.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

There are 9 tests in `tests/test_pawpal.py`. They cover marking a task complete and adding tasks to a pet, sorting by time (including times typed without a leading zero), filtering by pet and status, recurring tasks (daily, weekly, one-time, and completing the same task twice), and conflict detection (same time, partial overlap, and the cases that shouldn't count: back-to-back tasks, other days and completed tasks).

Before adding more tests I asked the AI to list the core behaviors worth verifying, and later what the most important edge cases are, instead of just saying "write tests". That gave me a list I could check against the code first. These behaviors matter because the whole plan depends on them. If sorting is off, the schedule reads wrong. If recurrence breaks, a daily feeding either disappears or shows up twice. And the conflict check has easy off-by-one mistakes: a walk that ends at 08:30 and a feeding that starts at 08:30 shouldn't be a conflict.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

About 3 out of 5, the same as in the README. All 9 tests pass and every feature has tests, but when I asked which behaviors and edge cases still needed checking, three things turned up that really don't work right. I didn't take that on faith either. Each one was shown with real output from a small script:

- `sort_by_time()` ignores the date, so tomorrow's 07:00 breakfast sorted ahead of today's 08:00 walk.
- Completing an overdue daily task creates a copy that's still overdue, so the task shows up in today's plan again.
- `edit_task()` changes the wrong task when a pet has two identical tasks (the durations came out `[20, 10]` instead of `[10, 20]`).

Next I'd write tests for those three, plus direct tests for `build_plan()` (priority order, a task that exactly fills the minutes left, 0 available minutes) and for two tasks at the same time always keeping the same order. I kept the 3/5 in the README with the bugs listed, because that's more honest than 5 stars.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the conflict detection. It catches overlapping tasks across different pets, not only identical start times, it ignores back-to-back tasks and other days, and in the app it shows up as a clear yellow warning instead of crashing anything. I also like that the `Scheduler` stayed the one "brain": `main.py` and the Streamlit app both just call its methods (sort, filter, conflicts, plan) and display the results, so the CLI demo and the app always agree.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

First I'd fix the three bugs from 4b. Then I'd let a `Task` know which pet it belongs to, or at least give it an id. Right now it doesn't, and that caused workarounds all over the place: `complete_task()` has to search every pet to find where to add the next copy, and both `main.py` and `app.py` build a little `id(task) -> pet name` dictionary just to print the pet's name. The `edit_task()` bug comes from the same problem. In the app I'd add a field for the available minutes (it's stuck at 120), buttons to complete, edit and delete tasks so recurrence can actually be used there, and a short "why" for each scheduled task, which was in my first design but got lost along the way.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Small decisions in the data model spread everywhere. Putting tasks on `Pet` without a link back to the pet looked harmless in the UML, but it ended up shaping `complete_task()`, the display code in two files, and one of the bugs. Next time I'd think harder about "who needs to know what" before writing the skeleton, because changing a diagram is a lot cheaper than changing code that already has tests and a UI built on top of it.
