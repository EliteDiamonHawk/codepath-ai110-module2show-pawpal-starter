import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
