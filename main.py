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
