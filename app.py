import streamlit as st
from datetime import time as dt_time
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def _parse_time(s: str | None) -> dt_time | None:
    if not s:
        return None
    h, m = s.split(":")
    return dt_time(int(h), int(m))


def build_pet_obj(pet_name: str, pet_d: dict) -> Pet:
    pet_obj = Pet(name=pet_name, species=pet_d["species"])
    for t in pet_d["tasks"]:
        task = Task(
            title=t["title"],
            duration_minutes=t["duration_minutes"],
            priority=t["priority"],
            scheduled_time=_parse_time(t.get("scheduled_time")),
        )
        if t.get("is_complete"):
            task.mark_complete()
        pet_obj.tasks.append(task)
    return pet_obj

st.title("🐾 PawPal+")

# ── Session state defaults ────────────────────────────────────────────────────

if "profiles" not in st.session_state:
    st.session_state.profiles = {}  # {owner_name: {"available_minutes": int, "pets": {...}}}

if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

if "generated_schedules" not in st.session_state:
    st.session_state.generated_schedules = {}  # {owner_name: {"warnings": [...], "scheduled_rows": [...], ...}}

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
    existing = profiles.get(st.session_state.active_profile, {})
    owner_name = st.text_input("Your name", value=st.session_state.active_profile or "")
    col1, col2, col3 = st.columns(3)
    with col1:
        day_start_input = st.time_input(
            "Day start", value=_parse_time(existing.get("day_start")) or dt_time(8, 0)
        )
    with col2:
        day_end_input = st.time_input(
            "Day end", value=_parse_time(existing.get("day_end")) or dt_time(20, 0)
        )
    with col3:
        available_minutes = st.number_input(
            "Available minutes", min_value=1, max_value=1440,
            value=existing.get("available_minutes", 720),
        )
    save_owner = st.form_submit_button("Save profile", use_container_width=True)

if save_owner:
    name = owner_name.strip()
    if not name:
        st.warning("Name cannot be empty.")
    elif day_end_input <= day_start_input:
        st.warning("Day end must be after day start.")
    else:
        entry = {
            "available_minutes": int(available_minutes),
            "day_start": day_start_input.strftime("%H:%M"),
            "day_end": day_end_input.strftime("%H:%M"),
            "pets": profiles.get(name, {}).get("pets", {}),
        }
        profiles[name] = entry
        st.session_state.active_profile = name
        st.rerun()

if st.session_state.active_profile and st.session_state.active_profile in profiles:
    p = profiles[st.session_state.active_profile]
    st.success(
        f"Active: **{st.session_state.active_profile}** — "
        f"{p.get('day_start', '08:00')} to {p.get('day_end', '20:00')} "
        f"({p['available_minutes']} min)"
    )

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

col_time, col_toggle = st.columns([3, 1])
with col_toggle:
    use_time = st.checkbox("Set time", value=False)
with col_time:
    scheduled_time_input = st.time_input("Scheduled time", value=dt_time(8, 0), disabled=not use_time)

col_add, col_clear = st.columns(2)
with col_add:
    if st.button("Add task", use_container_width=True):
        title = task_title.strip()
        if not title:
            st.warning("Task title cannot be empty.")
        elif any(t["title"].strip().casefold() == title.casefold() for t in pet_data["tasks"]):
            st.warning(f"{selected_pet} already has a task named '{title}'.")
        else:
            task_entry = {
                "title": title,
                "duration_minutes": int(duration),
                "priority": priority,
                "scheduled_time": scheduled_time_input.strftime("%H:%M") if use_time else None,
                "is_complete": False,
            }
            pet_data["tasks"].append(task_entry)
with col_clear:
    if st.button("Clear tasks", use_container_width=True):
        pet_data["tasks"] = []

if pet_data["tasks"]:
    # Build a temporary Scheduler to drive sorted views
    _prof = profiles[st.session_state.active_profile]
    tmp_owner = Owner(
        name=st.session_state.active_profile,
        available_minutes=_prof["available_minutes"],
        day_start=_parse_time(_prof.get("day_start")) or dt_time(8, 0),
        day_end=_parse_time(_prof.get("day_end")) or dt_time(20, 0),
    )
    tmp_pet = build_pet_obj(selected_pet, pet_data)
    scheduler = Scheduler(owner=tmp_owner, pet=tmp_pet)

    sort_mode = st.radio(
        "Sort tasks by", ["Priority", "Duration"], horizontal=True, label_visibility="visible"
    )
    if sort_mode == "Duration":
        display_tasks = scheduler.sort_by_duration()
    else:
        display_tasks = tmp_pet.get_tasks_by_priority()

    table_rows = [
        {
            "": PRIORITY_EMOJI.get(t.priority, ""),
            "Done": "✅" if t.is_complete else "—",
            "Task": t.title,
            "Time": t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "—",
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority,
        }
        for t in display_tasks
    ]
    st.table(table_rows)

    incomplete_titles = [t["title"] for t in pet_data["tasks"] if not t.get("is_complete")]
    if incomplete_titles:
        col_task, col_btn = st.columns([3, 1])
        with col_task:
            task_to_complete = st.selectbox("Mark a task complete", incomplete_titles)
        with col_btn:
            st.write("")
            if st.button("Mark complete", use_container_width=True):
                for t in pet_data["tasks"]:
                    if t["title"] == task_to_complete:
                        t["is_complete"] = True
                        break
                # Keep the already-generated schedule's Done column in sync
                # instead of forcing the user to regenerate it.
                stored = st.session_state.generated_schedules.get(st.session_state.active_profile)
                if stored:
                    for row in stored["scheduled_rows"] + stored["skipped_rows"]:
                        if row["Pet"] == selected_pet and row["Task"] == task_to_complete:
                            row["Done"] = "✅"
                st.rerun()
    else:
        st.caption("All tasks for this pet are complete. 🎉")
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

        _day_start = _parse_time(owner_data.get("day_start")) or dt_time(8, 0)
        _day_end = _parse_time(owner_data.get("day_end")) or dt_time(20, 0)

        # Build a full owner with all pets for conflict detection
        full_owner = Owner(
            name=st.session_state.active_profile,
            available_minutes=owner_data["available_minutes"],
            day_start=_day_start,
            day_end=_day_end,
        )
        for pn, pd in pets.items():
            if pd["tasks"]:
                full_owner.add_pet(build_pet_obj(pn, pd))

        # Conflict warnings across all pets
        if full_owner.pets:
            conflict_checker = Scheduler(owner=full_owner, pet=full_owner.pets[0])
            for warning in conflict_checker.detect_conflicts():
                st.warning(warning)

        # Build a combined pet with all tasks; track pet name + completion per task via id()
        combined_pet = Pet(name="All Pets", species="combined")
        task_pet_map: dict[int, str] = {}
        task_done_map: dict[int, bool] = {}
        for pn, pd in pets.items():
            for t_dict in pd["tasks"]:
                task = Task(
                    title=t_dict["title"],
                    duration_minutes=t_dict["duration_minutes"],
                    priority=t_dict["priority"],
                    scheduled_time=_parse_time(t_dict.get("scheduled_time")),
                )
                # Use direct append (not add_task) since the duplicate-name
                # guard is scoped per-pet, not across this synthetic combined pet.
                combined_pet.tasks.append(task)
                task_pet_map[id(task)] = pn
                task_done_map[id(task)] = bool(t_dict.get("is_complete"))

        combined_owner = Owner(
            name=st.session_state.active_profile,
            available_minutes=owner_data["available_minutes"],
            day_start=_day_start,
            day_end=_day_end,
        )
        schedule = Scheduler(owner=combined_owner, pet=combined_pet).generate_plan()

        def _row(t):
            return {
                "": PRIORITY_EMOJI.get(t.priority, ""),
                "Done": "✅" if task_done_map.get(id(t)) else "—",
                "Pet": task_pet_map.get(id(t), "?"),
                "Task": t.title,
                "Time": t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "—",
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
            }

        # Persist the generated schedule so switching pets or marking a task
        # complete elsewhere on the page doesn't clear this section.
        st.session_state.generated_schedules[st.session_state.active_profile] = {
            "available_minutes": owner_data["available_minutes"],
            "day_start": owner_data.get("day_start", "08:00"),
            "day_end": owner_data.get("day_end", "20:00"),
            "total_duration": schedule.total_duration,
            "scheduled_rows": [_row(t) for t in schedule.scheduled_tasks],
            "skipped_rows": [_row(t) for t in schedule.skipped_tasks],
        }

if st.session_state.active_profile in st.session_state.generated_schedules:
    stored = st.session_state.generated_schedules[st.session_state.active_profile]

    if stored["scheduled_rows"]:
        st.success(
            f"✅ {len(stored['scheduled_rows'])} task(s) scheduled across all pets — "
            f"{stored['total_duration']} of {stored['available_minutes']} min "
            f"({stored['day_start']}–{stored['day_end']})"
        )
        st.table(stored["scheduled_rows"])
    else:
        st.error(f"❌ No tasks fit within {stored['available_minutes']} available minutes.")

    if stored["skipped_rows"]:
        with st.expander(f"⏭ {len(stored['skipped_rows'])} skipped task(s) — not enough time"):
            st.table(stored["skipped_rows"])

    remaining = stored["available_minutes"] - stored["total_duration"]
    st.info(f"⏱ {remaining} min remaining after scheduling")
