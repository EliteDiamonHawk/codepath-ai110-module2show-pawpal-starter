from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name="Alex", available_minutes=90)

dog = Pet(name="Biscuit", species="Dog")
cat = Pet(name="Luna", species="Cat")

dog.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", reoccurring_daily=True))
dog.add_task(Task(title="Feed breakfast", duration_minutes=10, priority="high", reoccurring_daily=True))
dog.add_task(Task(title="Brush fur", duration_minutes=15, priority="medium", reoccurring_weekly=True))

cat.add_task(Task(title="Clean litter box", duration_minutes=10, priority="high", reoccurring_daily=True))
cat.add_task(Task(title="Playtime", duration_minutes=20, priority="medium"))
cat.add_task(Task(title="Vet checkup", duration_minutes=60, priority="low"))

owner.add_pet(dog)
owner.add_pet(cat)

print("=" * 40)
print("        TODAY'S SCHEDULE")
print("=" * 40)

for pet in owner.pets:
    scheduler = Scheduler(owner=owner, pet=pet)
    schedule = scheduler.generate_plan()
    print(f"\n[ {pet.name} the {pet.species} ]")
    print(schedule.summary())

print("\n" + "=" * 40)
