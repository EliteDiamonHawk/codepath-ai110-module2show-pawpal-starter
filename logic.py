from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "high", "medium", "low"
    reoccurring_weekly: bool = False
    reoccurring_daily: bool = False
    is_scheduled: bool = False

    def __lt__(self, other: Task) -> bool:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return priority_order.get(self.priority, 99) < priority_order.get(other.priority, 99)


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_tasks_by_priority(self) -> List[Task]:
        return sorted(self.tasks)


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)


@dataclass
class Schedule:
    scheduled_tasks: List[Task] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    total_duration: int = 0
    explanation: str = ""

    def summary(self) -> str:
        lines = []
        if self.scheduled_tasks:
            lines.append("Scheduled tasks:")
            for task in self.scheduled_tasks:
                lines.append(f"  - {task.title} ({task.duration_minutes} min) [{task.priority}]")
        if self.skipped_tasks:
            lines.append("Skipped tasks (not enough time):")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.title} ({task.duration_minutes} min) [{task.priority}]")
        lines.append(f"Total scheduled time: {self.total_duration} min")
        if self.explanation:
            lines.append(f"\n{self.explanation}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet

    def _fits_in_time(self, task: Task, remaining: int) -> bool:
        return task.duration_minutes <= remaining

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        return sorted(tasks)

    def generate_plan(self) -> Schedule:
        sorted_tasks = self._sort_tasks(self.pet.tasks)
        remaining = self.owner.available_minutes
        schedule = Schedule()

        for task in sorted_tasks:
            if self._fits_in_time(task, remaining):
                task.is_scheduled = True
                schedule.scheduled_tasks.append(task)
                schedule.total_duration += task.duration_minutes
                remaining -= task.duration_minutes
            else:
                schedule.skipped_tasks.append(task)

        schedule.explanation = (
            f"Scheduled {len(schedule.scheduled_tasks)} task(s) for {self.pet.name} "
            f"using {schedule.total_duration} of {self.owner.available_minutes} available minutes. "
            f"{len(schedule.skipped_tasks)} task(s) skipped due to time constraints."
        )
        return schedule
