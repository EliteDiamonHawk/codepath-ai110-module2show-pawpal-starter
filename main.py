from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name="Alex", available_minutes=90)

dog = Pet(name="Biscuit", species="Dog")
cat = Pet(name="Luna", species="Cat")

# Tasks added out of order (long before short, low before high)
dog.add_task(Task(title="Brush fur", duration_minutes=15, priority="medium", reoccurring_weekly=True))
dog.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", reoccurring_daily=True))
dog.add_task(Task(title="Feed breakfast", duration_minutes=10, priority="high", reoccurring_daily=True))

cat.add_task(Task(title="Vet checkup", duration_minutes=60, priority="low"))
cat.add_task(Task(title="Playtime", duration_minutes=20, priority="medium"))
cat.add_task(Task(title="Clean litter box", duration_minutes=10, priority="high", reoccurring_daily=True))

owner.add_pet(dog)
owner.add_pet(cat)

# Mark a couple tasks complete so filtering has something to show
dog.tasks[0].mark_complete()  # Brush fur
cat.tasks[2].mark_complete()  # Clean litter box

print("=" * 40)
print("        TODAY'S SCHEDULE")
print("=" * 40)

for pet in owner.pets:
    scheduler = Scheduler(owner=owner, pet=pet)
    schedule = scheduler.generate_plan()
    print(f"\n[ {pet.name} the {pet.species} ]")
    print(schedule.summary())

print("\n" + "=" * 40)
print("     SORT BY DURATION (shortest first)")
print("=" * 40)

for pet in owner.pets:
    scheduler = Scheduler(owner=owner, pet=pet)
    sorted_tasks = scheduler.sort_by_time()
    print(f"\n[ {pet.name} ]")
    for task in sorted_tasks:
        print(f"  {task.duration_minutes} min  -  {task.title}")

print("\n" + "=" * 40)
print("       FILTER BY COMPLETION STATUS")
print("=" * 40)

for pet in owner.pets:
    completed = pet.filter_tasks_by_completion(True)
    incomplete = pet.filter_tasks_by_completion(False)
    print(f"\n[ {pet.name} ]")
    print(f"  Completed ({len(completed)}):")
    for t in completed:
        print(f"    + {t.title}")
    print(f"  Incomplete ({len(incomplete)}):")
    for t in incomplete:
        print(f"    - {t.title}")

print("\n" + "=" * 40)
print("      FILTER TASKS BY PET NAME")
print("=" * 40)

for name in ["Biscuit", "Luna", "Unknown"]:
    tasks = owner.get_tasks_by_pet_name(name)
    print(f"\n  {name}: {[t.title for t in tasks] if tasks else 'no pet found'}")

print("\n" + "=" * 40)

# ---------------------------------------------------------------------------
# Day window demos
# ---------------------------------------------------------------------------
from datetime import time

print("\n" + "=" * 40)
print("       DAY WINDOW DEMOS")
print("=" * 40)

# 1. day_minutes() matches window
windowed_owner = Owner(name="Alex", available_minutes=720, day_start=time(8, 0), day_end=time(20, 0))
demo_pet = Pet(name="Demo", species="Dog")
sched = Scheduler(owner=windowed_owner, pet=demo_pet)
print(f"\nday_minutes() for 08:00-20:00: {sched.day_minutes()} min  (expected 720)")

# 2. Task inside window -> scheduled
demo_pet2 = Pet(name="Pip", species="Dog")
demo_pet2.add_task(Task(title="Morning walk", duration_minutes=20, priority="high", scheduled_time=time(9, 0)))
owner2 = Owner(name="Alex", available_minutes=720, day_start=time(8, 0), day_end=time(20, 0))
plan2 = Scheduler(owner2, demo_pet2).generate_plan()
print(f"\nTask at 09:00 (window 08-20) -> scheduled: {[t.title for t in plan2.scheduled_tasks]}")
print(f"  skipped: {[t.title for t in plan2.skipped_tasks]}")

# 3. Task outside window -> skipped
demo_pet3 = Pet(name="Pip", species="Dog")
demo_pet3.add_task(Task(title="Late snack", duration_minutes=10, priority="high", scheduled_time=time(22, 0)))
owner3 = Owner(name="Alex", available_minutes=720, day_start=time(8, 0), day_end=time(20, 0))
plan3 = Scheduler(owner3, demo_pet3).generate_plan()
print(f"\nTask at 22:00 (window 08-20) -> scheduled: {[t.title for t in plan3.scheduled_tasks]}")
print(f"  skipped: {[t.title for t in plan3.skipped_tasks]}")

# 4. available_minutes < window -> budget caps scheduling
demo_pet4 = Pet(name="Pip", species="Dog")
demo_pet4.add_task(Task(title="Walk",  duration_minutes=30, priority="high",   scheduled_time=time(9, 0)))
demo_pet4.add_task(Task(title="Feed",  duration_minutes=20, priority="medium", scheduled_time=time(10, 0)))
owner4 = Owner(name="Alex", available_minutes=30, day_start=time(8, 0), day_end=time(20, 0))
plan4 = Scheduler(owner4, demo_pet4).generate_plan()
print(f"\navail=30 min (window 720 min), tasks 30+20 min:")
print(f"  scheduled: {[t.title for t in plan4.scheduled_tasks]}  total={plan4.total_duration} min")
print(f"  skipped:   {[t.title for t in plan4.skipped_tasks]}")

# 5. Mixed timed (in-window), timed (out-of-window), and untimed tasks
demo_pet5 = Pet(name="Pip", species="Dog")
demo_pet5.add_task(Task(title="Morning walk", duration_minutes=20, priority="high",   scheduled_time=time(8, 30)))
demo_pet5.add_task(Task(title="Late snack",   duration_minutes=10, priority="high",   scheduled_time=time(21, 0)))
demo_pet5.add_task(Task(title="Brush",        duration_minutes=15, priority="medium"))
owner5 = Owner(name="Alex", available_minutes=720, day_start=time(8, 0), day_end=time(20, 0))
plan5 = Scheduler(owner5, demo_pet5).generate_plan()
print(f"\nMixed tasks (in-window timed + out-of-window timed + untimed):")
print(f"  scheduled: {[t.title for t in plan5.scheduled_tasks]}")
print(f"  skipped:   {[t.title for t in plan5.skipped_tasks]}")
print(f"  {plan5.explanation}")

print("\n" + "=" * 40)
