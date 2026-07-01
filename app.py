import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session state defaults ────────────────────────────────────────────────────

if "profiles" not in st.session_state:
    st.session_state.profiles = {}  # {owner_name: {"available_minutes": int, "pets": {...}}}

if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

# ── Owner Profiles ────────────────────────────────────────────────────────────

st.header("Owner Profile")

profiles = st.session_state.profiles

col_select, col_new = st.columns([2, 1])
with col_select:
    if profiles:
        selected_profile = st.selectbox(
            "Switch profile",
            list(profiles.keys()),
            index=list(profiles.keys()).index(st.session_state.active_profile)
            if st.session_state.active_profile in profiles else 0,
        )
        if selected_profile != st.session_state.active_profile:
            st.session_state.active_profile = selected_profile
            st.rerun()
    else:
        st.info("No profiles yet. Create one below.")

with col_new:
    if st.button("+ New profile", use_container_width=True):
        st.session_state.active_profile = None

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    existing = profiles.get(st.session_state.active_profile, {})
    with col1:
        owner_name = st.text_input("Your name", value=st.session_state.active_profile or "")
    with col2:
        available_minutes = st.number_input(
            "Available minutes today", min_value=1, max_value=480,
            value=existing.get("available_minutes", 60),
        )
    save_owner = st.form_submit_button("Save profile", use_container_width=True)

if save_owner:
    name = owner_name.strip()
    if not name:
        st.warning("Name cannot be empty.")
    else:
        if name not in profiles:
            profiles[name] = {"available_minutes": int(available_minutes), "pets": {}}
        else:
            profiles[name]["available_minutes"] = int(available_minutes)
        st.session_state.active_profile = name
        st.rerun()

if st.session_state.active_profile and st.session_state.active_profile in profiles:
    p = profiles[st.session_state.active_profile]
    st.success(f"Active: **{st.session_state.active_profile}** — {p['available_minutes']} min available today")

    if st.button("Delete this profile", type="secondary"):
        del profiles[st.session_state.active_profile]
        st.session_state.active_profile = next(iter(profiles), None)
        st.rerun()

st.divider()

# ── Pets ──────────────────────────────────────────────────────────────────────

if not st.session_state.active_profile or st.session_state.active_profile not in profiles:
    st.info("Save an owner profile above to manage pets.")
    st.stop()

pets = profiles[st.session_state.active_profile]["pets"]

st.header("My Pets")

with st.expander("Add a new pet", expanded=len(pets) == 0):
    with st.form("add_pet_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_pet_name = st.text_input("Pet name", value="Mochi")
        with col2:
            new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
        add_pet = st.form_submit_button("Add pet", use_container_width=True)

    if add_pet:
        if new_pet_name.strip() == "":
            st.warning("Pet name cannot be empty.")
        elif new_pet_name in pets:
            st.warning(f"A pet named '{new_pet_name}' already exists.")
        else:
            pets[new_pet_name] = {"species": new_pet_species, "tasks": []}
            st.success(f"Added {new_pet_name}!")

if not pets:
    st.info("No pets yet. Add one above.")
    st.stop()

selected_pet = st.selectbox("Select a pet to manage", list(pets.keys()))
pet_data = pets[selected_pet]

st.markdown(f"**{selected_pet}** — {pet_data['species']}")

if st.button(f"Remove {selected_pet}", type="secondary"):
    del pets[selected_pet]
    st.rerun()

st.divider()

# ── Tasks ─────────────────────────────────────────────────────────────────────

st.subheader(f"Tasks for {selected_pet}")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col_add, col_clear = st.columns(2)
with col_add:
    if st.button("Add task", use_container_width=True):
        pet_data["tasks"].append({
            "title": task_title,
            "duration_minutes": int(duration),
            "priority": priority,
        })
with col_clear:
    if st.button("Clear tasks", use_container_width=True):
        pet_data["tasks"] = []

if pet_data["tasks"]:
    st.table(pet_data["tasks"])
else:
    st.info(f"No tasks for {selected_pet} yet.")

st.divider()

# ── Schedule ──────────────────────────────────────────────────────────────────

st.header("Generate Schedule")

if st.button("Generate schedule for all pets", type="primary"):
    any_tasks = any(d["tasks"] for d in pets.values())
    if not any_tasks:
        st.warning("Add at least one task to a pet before generating a schedule.")
    else:
        owner_data = profiles[st.session_state.active_profile]
        remaining_minutes = owner_data["available_minutes"]

        for pet_name, pet_data in pets.items():
            if not pet_data["tasks"]:
                continue

            st.markdown(f"### {pet_name} ({pet_data['species']})")

            pet = Pet(name=pet_name, species=pet_data["species"])
            for t in pet_data["tasks"]:
                pet.add_task(Task(
                    title=t["title"],
                    duration_minutes=t["duration_minutes"],
                    priority=t["priority"],
                ))

            pet_owner = Owner(
                name=st.session_state.active_profile,
                available_minutes=remaining_minutes,
            )
            schedule = Scheduler(owner=pet_owner, pet=pet).generate_plan()

            if schedule.scheduled_tasks:
                st.success(f"{len(schedule.scheduled_tasks)} task(s) scheduled — {schedule.total_duration} min")
                for task in schedule.scheduled_tasks:
                    st.markdown(f"- **{task.title}** — {task.duration_minutes} min [{task.priority}]")
                remaining_minutes -= schedule.total_duration
            else:
                st.error(f"No tasks fit — only {remaining_minutes} min remaining.")

            if schedule.skipped_tasks:
                st.markdown("**Skipped:**")
                for task in schedule.skipped_tasks:
                    st.markdown(f"- {task.title} — {task.duration_minutes} min [{task.priority}]")

            st.caption(schedule.explanation)

        st.info(f"Total remaining time after all pets: {remaining_minutes} min")
