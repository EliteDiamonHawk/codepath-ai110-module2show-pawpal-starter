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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
