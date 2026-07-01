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

## Features

- **Greedy daily plan generation** (`Scheduler.generate_plan`) — walks tasks in sorted order and packs each one into the owner's remaining time budget if it fits; tasks whose `scheduled_time` falls outside the owner's day window, or that no longer fit the remaining budget, land in `skipped_tasks` instead. Produces a plain-language explanation of the outcome (window, minutes used, tasks skipped).
- **Multi-key task sorting** — `Scheduler._sort_tasks` orders tasks by `scheduled_time` first (unscheduled tasks last), then breaks ties by priority (high → medium → low). Standalone `sort_by_time` and `sort_by_duration` helpers provide chronological and shortest-duration-first views. `Task.__lt__` defines a priority ordering used by `Pet.get_tasks_by_priority`.
- **Time-window validation** — `Scheduler._in_window` checks a task's `scheduled_time` against the owner's `day_start`/`day_end` before it's eligible for scheduling.
- **Cross-pet conflict detection** (`Scheduler.detect_conflicts`) — buckets every scheduled task across all of an owner's pets by `scheduled_time` and flags any time slot shared by two or more tasks (whether from the same pet or different pets).
- **Recurring task generation** (`Task.next_occurrence`) — given a completed daily or weekly task, produces a fresh, incomplete copy due one day or one week later; non-recurring tasks return `None`. `Pet.complete_task` ties this together by marking a task complete and auto-appending its next occurrence.
- **Completion filtering** (`Pet.filter_tasks_by_completion`) — returns the subset of a pet's tasks matching a given completion state.
- **Lookup by pet name** (`Owner.get_tasks_by_pet_name`) — returns a named pet's task list, or an empty list if the pet doesn't exist.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
========================================
        TODAY'S SCHEDULE
========================================

[ Biscuit the Dog ]
Scheduled tasks:
  - Morning walk (30 min) [high]
  - Feed breakfast (10 min) [high]
  - Brush fur (15 min) [medium]
Total scheduled time: 55 min

Scheduled 3 task(s) for Biscuit using 55 of 90 available minutes. 0 task(s) skipped due to time constraints.

[ Luna the Cat ]
Scheduled tasks:
  - Clean litter box (10 min) [high]
  - Playtime (20 min) [medium]
  - Vet checkup (60 min) [low]
Total scheduled time: 90 min

Scheduled 3 task(s) for Luna using 90 of 90 available minutes. 0 task(s) skipped due to time constraints.
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest tests/test_pawpal.py -v
```

**What the tests cover (19 tests across 6 areas):**

- **Sorting** — chronological order by `scheduled_time`, stable tie-breaking, priority order (high → medium → low), and shortest-duration-first ordering
- **Recurrence** — daily tasks produce a next-day copy, weekly tasks produce a next-week copy, non-recurring tasks produce nothing, and completed recurring tasks are appended to the pet's task list
- **Conflict detection** — flags two pets sharing a time slot, flags two tasks on the same pet at the same time, ignores unscheduled tasks, and returns empty when there are no overlaps
- **Plan generation** — over-budget tasks land in `skipped_tasks`, and scheduled tasks are marked `is_scheduled = True`
- **Filtering** — `filter_tasks_by_completion` correctly isolates complete and incomplete tasks
- **Task state** — `mark_complete` flips `is_complete`, `add_task` grows the pet's task list

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.0.3, pluggy-1.6.0
collecting ... collected 19 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  5%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 10%]
tests/test_pawpal.py::test_sort_by_time_chronological_order PASSED       [ 15%]
tests/test_pawpal.py::test_sort_by_time_ties_are_stable PASSED           [ 21%]
tests/test_pawpal.py::test_sort_by_priority_order PASSED                 [ 26%]
tests/test_pawpal.py::test_sort_by_duration_shortest_first PASSED        [ 31%]
tests/test_pawpal.py::test_daily_recurrence_creates_next_day_task PASSED [ 36%]
tests/test_pawpal.py::test_weekly_recurrence_creates_next_week_task PASSED [ 42%]
tests/test_pawpal.py::test_non_recurring_task_produces_no_next_occurrence PASSED [ 47%]
tests/test_pawpal.py::test_completing_daily_task_appends_to_pet_tasks PASSED [ 52%]
tests/test_pawpal.py::test_completing_task_twice_does_not_create_duplicate_recurrence PASSED [ 57%]
tests/test_pawpal.py::test_detect_conflicts_same_time_different_pets PASSED [ 63%]
tests/test_pawpal.py::test_detect_conflicts_no_overlap_returns_empty PASSED [ 68%]
tests/test_pawpal.py::test_detect_conflicts_same_pet_same_time PASSED    [ 73%]
tests/test_pawpal.py::test_detect_conflicts_unscheduled_tasks_ignored PASSED [ 78%]
tests/test_pawpal.py::test_generate_plan_respects_available_time PASSED  [ 84%]
tests/test_pawpal.py::test_generate_plan_marks_tasks_as_scheduled PASSED [ 89%]
tests/test_pawpal.py::test_filter_tasks_incomplete_only PASSED           [ 94%]
tests/test_pawpal.py::test_filter_tasks_complete_only PASSED             [100%]

============================= 19 passed in 0.08s ==============================
```

**Confidence Level: ★★★★☆ (4/5)**


## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by scheduled time | `Scheduler.sort_by_time()` | Returns the pet's tasks ordered by `Task.scheduled_time`; tasks with no scheduled time sort to the end |
| Sort by duration | `Scheduler.sort_by_duration()` | Returns the pet's tasks ordered shortest to longest by `Task.duration_minutes` |
| Filter by completion status | `Pet.filter_tasks_by_completion(is_complete)` | Pass `True` for completed tasks, `False` for incomplete |
| Filter by pet name | `Owner.get_tasks_by_pet_name(name)` | Returns all tasks belonging to the named pet; returns `[]` if no pet matches |
| Conflict detection | `Scheduler.detect_conflicts()` | Scans all pets under the owner and returns a warning string for every `scheduled_time` shared by two or more tasks; returns an empty list when there are no conflicts |
| Recurring task scheduling | `Task.next_occurrence()` | Returns a fresh, incomplete copy of the task with a `due_date` of today + 1 day (daily) or today + 7 days (weekly); returns `None` for one-off tasks |
| Complete and reschedule | `Pet.complete_task(task)` | Marks the task complete and automatically appends the next occurrence to the pet's task list if the task recurs |

## 📸 Demo Walkthrough

### UI features

The Streamlit app (`app.py`) is organized into four sections:

- **Owner Profile** — create, switch between, or delete owner profiles. Each profile stores a name, an available-minutes budget, and a `day_start`/`day_end`.
- **My Pets** — add or remove pets (name + species) under the active profile.
- **Tasks** — for the selected pet, add a task (title, duration, priority, and an optional scheduled time), clear all of a pet's tasks, and view them in a table sorted by either priority or duration.
- **Generate Schedule** — build a plan across *all* pets under the active profile at once: shows any conflict warnings, a table of scheduled tasks (tagged by pet), an expandable list of skipped tasks, and the remaining minutes left in the day.

### Example workflow

1. Under **Owner Profile**, enter a name (e.g. "Alex"), set a day window (08:00–20:00), and an available-minutes budget (e.g. 90), then click **Save profile**.
2. Under **My Pets**, add a pet (e.g. "Biscuit", species "dog").
3. Under **Tasks**, add a few tasks for Biscuit — e.g. "Morning walk" (30 min, high priority, time 08:00), "Feed breakfast" (10 min, high priority), "Brush fur" (15 min, medium priority). The task table updates live and can be re-sorted by priority or duration.
4. Repeat steps 2–3 for a second pet (e.g. "Luna" the cat) to see multi-pet behavior.
5. Click **Generate schedule for all pets** under **Generate Schedule** to view today's combined plan.

### Key Scheduler behaviors shown

- **Sorting** — the task table under **Tasks** re-orders instantly when switching the "Sort tasks by" radio between Priority and Duration, backed by `Pet.get_tasks_by_priority()` and `Scheduler.sort_by_duration()`.
- **Conflict warnings** — if two tasks (on the same pet or different pets) share the same `scheduled_time`, `Scheduler.detect_conflicts()` surfaces a `st.warning` banner above the schedule before the plan is generated.
- **Greedy plan generation** — `Scheduler.generate_plan()` fills the available-minutes budget in sorted order, skipping any task that no longer fits or falls outside the day window, then reports scheduled vs. skipped tasks and remaining minutes.

### Sample CLI output (`python main.py`)

```
========================================
        TODAY'S SCHEDULE
========================================

[ Biscuit the Dog ]
Scheduled tasks:
  - Morning walk (30 min) [high]
  - Feed breakfast (10 min) [high]
  - Brush fur (15 min) [medium]
Total scheduled time: 55 min

Day window: 08:00–20:00 (90 min). Scheduled 3 task(s) using 55 min. 0 task(s) skipped.

[ Luna the Cat ]
Scheduled tasks:
  - Clean litter box (10 min) [high]
  - Playtime (20 min) [medium]
  - Vet checkup (60 min) [low]
Total scheduled time: 90 min

Day window: 08:00–20:00 (90 min). Scheduled 3 task(s) using 90 min. 0 task(s) skipped.

========================================
     SORT BY DURATION (shortest first)
========================================

[ Biscuit ]
  15 min  -  Brush fur
  30 min  -  Morning walk
  10 min  -  Feed breakfast

[ Luna ]
  60 min  -  Vet checkup
  20 min  -  Playtime
  10 min  -  Clean litter box

========================================
       FILTER BY COMPLETION STATUS
========================================

[ Biscuit ]
  Completed (1):
    + Brush fur
  Incomplete (2):
    - Morning walk
    - Feed breakfast

[ Luna ]
  Completed (1):
    + Clean litter box
  Incomplete (2):
    - Vet checkup
    - Playtime

========================================
      FILTER TASKS BY PET NAME
========================================

  Biscuit: ['Brush fur', 'Morning walk', 'Feed breakfast']

  Luna: ['Vet checkup', 'Playtime', 'Clean litter box']

  Unknown: no pet found

========================================

========================================
       DAY WINDOW DEMOS
========================================

day_minutes() for 08:00-20:00: 720 min  (expected 720)

Task at 09:00 (window 08-20) -> scheduled: ['Morning walk']
  skipped: []

Task at 22:00 (window 08-20) -> scheduled: []
  skipped: ['Late snack']

avail=30 min (window 720 min), tasks 30+20 min:
  scheduled: ['Walk']  total=30 min
  skipped:   ['Feed']

Mixed tasks (in-window timed + out-of-window timed + untimed):
  scheduled: ['Morning walk', 'Brush']
  skipped:   ['Late snack']
  Day window: 08:00–20:00 (720 min). Scheduled 2 task(s) using 35 min. 1 task(s) skipped.

========================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
