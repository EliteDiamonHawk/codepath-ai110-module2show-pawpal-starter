from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import List, Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "high", "medium", "low"
    due_date: Optional[date] = None
    scheduled_time: Optional[time] = None  # e.g. time(8, 30) for 8:30 AM
    reoccurring_weekly: bool = False
    reoccurring_daily: bool = False
    is_scheduled: bool = False
    is_complete: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_complete = True

    def next_occurrence(self) -> Task | None:
        """Return a fresh, incomplete copy of this task if it recurs; otherwise None."""
        if self.reoccurring_daily:
            delta = timedelta(days=1)
        elif self.reoccurring_weekly:
            delta = timedelta(weeks=1)
        else:
            return None
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_date=date.today() + delta,
            scheduled_time=self.scheduled_time,
            reoccurring_daily=self.reoccurring_daily,
            reoccurring_weekly=self.reoccurring_weekly,
        )

    def __lt__(self, other: Task) -> bool:
        """Compare tasks by priority order (high < medium < low)."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return priority_order.get(self.priority, 99) < priority_order.get(other.priority, 99)


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks_by_priority(self) -> List[Task]:
        """Return this pet's tasks sorted from highest to lowest priority."""
        return sorted(self.tasks)

    def complete_task(self, task: Task) -> Task | None:
        """Mark task complete and append the next occurrence if it recurs.

        Returns the new Task instance if one was created, otherwise None.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            self.tasks.append(next_task)
        return next_task

    def filter_tasks_by_completion(self, is_complete: bool) -> List[Task]:
        """Return tasks matching the given completion status."""
        return [t for t in self.tasks if t.is_complete == is_complete]


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_tasks_by_pet_name(self, name: str) -> List[Task]:
        """Return all tasks belonging to the pet with the given name, or [] if not found."""
        for pet in self.pets:
            if pet.name == name:
                return pet.tasks
        return []


@dataclass
class Schedule:
    scheduled_tasks: List[Task] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    total_duration: int = 0
    explanation: str = ""

    def summary(self) -> str:
        """Return a formatted string summarizing scheduled and skipped tasks."""
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
        """Return True if the task duration fits within the remaining time."""
        return task.duration_minutes <= remaining

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort by scheduled_time first (unscheduled last), then by priority within each group."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda t: (
                t.scheduled_time is None,
                t.scheduled_time,
                priority_order.get(t.priority, 99),
            ),
        )

    def sort_by_time(self) -> List[Task]:
        """Return the pet's tasks sorted by scheduled_time; unscheduled tasks go last."""
        return sorted(
            self.pet.tasks,
            key=lambda t: (t.scheduled_time is None, t.scheduled_time),
        )

    def sort_by_duration(self) -> List[Task]:
        """Return the pet's tasks sorted by duration_minutes, shortest first."""
        return sorted(self.pet.tasks, key=lambda t: t.duration_minutes)

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for any two tasks across all pets that share a scheduled_time."""
        # Collect (scheduled_time -> [(pet_name, task_title), ...]) across all pets
        time_map: dict = {}
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.scheduled_time is None:
                    continue
                time_map.setdefault(task.scheduled_time, []).append((pet.name, task.title))

        warnings = []
        for scheduled_time, entries in time_map.items():
            if len(entries) > 1:
                details = ", ".join(f"{pet}:{title}" for pet, title in entries)
                warnings.append(f"WARNING: Conflict at {scheduled_time} — {details}")
        return warnings

    def generate_plan(self) -> Schedule:
        """Build and return a Schedule by greedily fitting tasks into available time."""
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
