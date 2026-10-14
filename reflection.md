# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Before drawing any UML I reread the scenario in the README and tried to figure out what a user actually needs to *do* in the app. Basically it's a busy pet owner who keeps forgetting stuff, so the app should help them stay on track. I ended up with three core actions:

1. **Add an owner and their pet.** The user puts in some basic info about themselves (name, how much free time they have today, maybe some preferences like "I prefer walks in the morning") and about their pet (name, species/breed). This has to come first, because the scheduler can't plan anything if it doesn't know how much time the owner has or who the tasks are even for.

2. **Add or edit a care task.** The user can create tasks like "morning walk", "feeding", "give meds" or "brushing". Each task needs at least a duration in minutes and a priority (low / medium / high). They should also be able to edit a task later, for example if the walk takes longer than they thought or the meds become more important. These tasks are basically the input for the whole scheduling part.

3. **Generate and view today's plan.** The user clicks a button and gets a daily schedule. The app tries to fit the tasks into the time the owner has, high priority stuff goes first, and if something doesn't fit it gets skipped. The plan should also explain *why* it looks like that (e.g. "meds were scheduled first because they're high priority, grooming was skipped because there was no time left"), because the README says the app should explain its reasoning and not just spit out a list.

Based on these actions I figured my first classes would roughly be `Owner`, `Pet`, `Task` and `Scheduler` (which builds some kind of daily plan). `Owner` and `Pet` store the profile info, `Task` holds the info about each care task, and `Scheduler` does the actual sorting/filtering and keeps track of the reasoning. I'll probably change some of this once I start coding, but this is my starting point.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
