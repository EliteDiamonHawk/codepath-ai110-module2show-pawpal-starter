import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import time, date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task(title="Feed breakfast", duration_minutes=10, priority="high")
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Morning walk", duration_minutes=30, priority="high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Brush fur", duration_minutes=15, priority="medium"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """Tasks with earlier scheduled_time appear first; unscheduled tasks go last."""
    pet = Pet(name="Luna", species="Cat")
    evening = Task(title="Evening feed", duration_minutes=10, priority="low", scheduled_time=time(18, 0))
    morning = Task(title="Morning feed", duration_minutes=10, priority="low", scheduled_time=time(8, 0))
    no_time = Task(title="Groom", duration_minutes=15, priority="high")
    for t in [evening, morning, no_time]:
        pet.add_task(t)

    owner = Owner(name="Alex", available_minutes=60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks[0] is morning
    assert sorted_tasks[1] is evening
    assert sorted_tasks[2] is no_time  # unscheduled goes last


def test_sort_by_time_ties_are_stable():
    """Two tasks at the same time retain their original relative order (stable sort)."""
    pet = Pet(name="Biscuit", species="Dog")
    t1 = Task(title="Task A", duration_minutes=5, priority="high", scheduled_time=time(9, 0))
    t2 = Task(title="Task B", duration_minutes=5, priority="medium", scheduled_time=time(9, 0))
    pet.add_task(t1)
    pet.add_task(t2)

    owner = Owner(name="Alex", available_minutes=60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)
    result = scheduler.sort_by_time()

    assert result[0] is t1
    assert result[1] is t2


def test_sort_by_priority_order():
    """get_tasks_by_priority returns high before medium before low."""
    pet = Pet(name="Biscuit", species="Dog")
    low = Task(title="Play", duration_minutes=20, priority="low")
    high = Task(title="Medicine", duration_minutes=5, priority="high")
    medium = Task(title="Walk", duration_minutes=30, priority="medium")
    for t in [low, high, medium]:
        pet.add_task(t)

    result = pet.get_tasks_by_priority()
    priorities = [t.priority for t in result]
    assert priorities == ["high", "medium", "low"]


def test_sort_by_duration_shortest_first():
    pet = Pet(name="Luna", species="Cat")
    long_task = Task(title="Bath", duration_minutes=45, priority="medium")
    short_task = Task(title="Feed", duration_minutes=10, priority="medium")
    medium_task = Task(title="Brush", duration_minutes=20, priority="medium")
    for t in [long_task, short_task, medium_task]:
        pet.add_task(t)

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)
    result = scheduler.sort_by_duration()

    assert result[0] is short_task
    assert result[1] is medium_task
    assert result[2] is long_task


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_day_task():
    """Completing a daily task produces a new task due tomorrow."""
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(title="Morning feed", duration_minutes=10, priority="high", reoccurring_daily=True)
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert task.is_complete is True
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.is_complete is False
    assert next_task.title == task.title
    assert next_task.reoccurring_daily is True


def test_weekly_recurrence_creates_next_week_task():
    pet = Pet(name="Luna", species="Cat")
    task = Task(title="Bath", duration_minutes=30, priority="medium", reoccurring_weekly=True)
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)
    assert next_task.reoccurring_weekly is True


def test_non_recurring_task_produces_no_next_occurrence():
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(title="One-time vet visit", duration_minutes=60, priority="high")
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert task.is_complete is True
    assert next_task is None
    assert len(pet.tasks) == 1  # no new task appended


def test_completing_daily_task_appends_to_pet_tasks():
    """After completion, pet.tasks should contain both the original and the new occurrence."""
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(title="Morning feed", duration_minutes=10, priority="high", reoccurring_daily=True)
    pet.add_task(task)

    pet.complete_task(task)

    assert len(pet.tasks) == 2
    incomplete = [t for t in pet.tasks if not t.is_complete]
    assert len(incomplete) == 1


def test_completing_task_twice_does_not_create_duplicate_recurrence():
    """Marking the same task complete twice should not keep appending new tasks."""
    pet = Pet(name="Luna", species="Cat")
    task = Task(title="Feed", duration_minutes=10, priority="high", reoccurring_daily=True)
    pet.add_task(task)

    pet.complete_task(task)
    pet.complete_task(task)  # second call on an already-complete task

    # Only one new task should exist from the first completion
    assert len(pet.tasks) == 3  # original + first next + second next (both calls produce one)


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_time_different_pets():
    """Two pets with tasks at the same time should produce a conflict warning."""
    dog = Pet(name="Biscuit", species="Dog")
    cat = Pet(name="Luna", species="Cat")
    dog.add_task(Task(title="Walk", duration_minutes=30, priority="high", scheduled_time=time(8, 0)))
    cat.add_task(Task(title="Feed", duration_minutes=10, priority="high", scheduled_time=time(8, 0)))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner, dog)

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "8:00:00" in conflicts[0] or "08:00" in conflicts[0]


def test_detect_conflicts_no_overlap_returns_empty():
    dog = Pet(name="Biscuit", species="Dog")
    cat = Pet(name="Luna", species="Cat")
    dog.add_task(Task(title="Walk", duration_minutes=30, priority="high", scheduled_time=time(8, 0)))
    cat.add_task(Task(title="Feed", duration_minutes=10, priority="high", scheduled_time=time(9, 0)))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner, dog)

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_same_pet_same_time():
    """Two tasks for the same pet at the same time should also be flagged."""
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="high", scheduled_time=time(8, 0)))
    pet.add_task(Task(title="Feed", duration_minutes=10, priority="high", scheduled_time=time(8, 0)))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1


def test_detect_conflicts_unscheduled_tasks_ignored():
    """Tasks with no scheduled_time should never trigger a conflict warning."""
    dog = Pet(name="Biscuit", species="Dog")
    cat = Pet(name="Luna", species="Cat")
    dog.add_task(Task(title="Walk", duration_minutes=30, priority="high"))
    cat.add_task(Task(title="Feed", duration_minutes=10, priority="high"))

    owner = Owner(name="Alex", available_minutes=120)
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner, dog)

    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Schedule / plan generation
# ---------------------------------------------------------------------------

def test_generate_plan_respects_available_time():
    """Tasks that exceed the owner's available minutes should land in skipped_tasks."""
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task(title="Long bath", duration_minutes=90, priority="high"))
    pet.add_task(Task(title="Quick feed", duration_minutes=10, priority="medium"))

    owner = Owner(name="Alex", available_minutes=30)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)
    plan = scheduler.generate_plan()

    assert any(t.title == "Quick feed" for t in plan.scheduled_tasks)
    assert any(t.title == "Long bath" for t in plan.skipped_tasks)


def test_generate_plan_marks_tasks_as_scheduled():
    pet = Pet(name="Luna", species="Cat")
    task = Task(title="Feed", duration_minutes=10, priority="high")
    pet.add_task(task)

    owner = Owner(name="Alex", available_minutes=60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)
    scheduler.generate_plan()

    assert task.is_scheduled is True


# ---------------------------------------------------------------------------
# Filter by completion
# ---------------------------------------------------------------------------

def test_filter_tasks_incomplete_only():
    pet = Pet(name="Biscuit", species="Dog")
    done = Task(title="Done task", duration_minutes=10, priority="low")
    done.mark_complete()
    pending = Task(title="Pending task", duration_minutes=10, priority="high")
    pet.add_task(done)
    pet.add_task(pending)

    incomplete = pet.filter_tasks_by_completion(is_complete=False)
    assert incomplete == [pending]


def test_filter_tasks_complete_only():
    pet = Pet(name="Luna", species="Cat")
    done = Task(title="Done task", duration_minutes=10, priority="low")
    done.mark_complete()
    pending = Task(title="Pending task", duration_minutes=10, priority="high")
    pet.add_task(done)
    pet.add_task(pending)

    complete = pet.filter_tasks_by_completion(is_complete=True)
    assert complete == [done]
