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
