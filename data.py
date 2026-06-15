import json
import os
from datetime import date

# Constants
DATA_FILE = "habits_data.json"
LEVEL_XP = 1000


def get_today_date() -> str:
    return date.today().isoformat()


def load_data(path: str = DATA_FILE) -> dict:
    if not os.path.exists(path):
        return init_data(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict, path: str = DATA_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_data(path: str = DATA_FILE) -> dict:
    default = {
        "profile": {"name": "المستخدم", "total_xp": 0},
        "habits": [
            {"id": 1, "name": "استيقاظ 4:30", "xp": 150, "emoji": "⏰"},
            {"id": 2, "name": "صلاة الفجر", "xp": 100, "emoji": "🕌"},
            {"id": 3, "name": "ذهاب للجيم", "xp": 200, "emoji": "🏋️‍♂️"},
            {"id": 4, "name": "قراءة 30 دقيقة", "xp": 120, "emoji": "📚"},
            {"id": 5, "name": "صيام صحي/وجبة صحية", "xp": 80, "emoji": "🥗"},
            {"id": 6, "name": "تدوين يومي/تأمل", "xp": 90, "emoji": "📝"},
            {"id": 7, "name": "تعلم لغة/مهارة", "xp": 160, "emoji": "💡"}
        ],
        "daily_log": []
    }
    save_data(default, path)
    return default


def find_or_create_day_entry(data: dict, day: str) -> dict:
    for entry in data.get("daily_log", []):
        if entry.get("date") == day:
            return entry
    new = {"date": day, "completed": []}
    data.setdefault("daily_log", []).append(new)
    return new


def get_habit_by_id(data: dict, hid: int) -> dict:
    for h in data.get("habits", []):
        if h.get("id") == hid:
            return h
    return None


def get_level(total_xp: int):
    level = (total_xp // LEVEL_XP) + 1
    xp_in_level = total_xp % LEVEL_XP
    xp_to_next = LEVEL_XP - xp_in_level
    return level, xp_in_level, xp_to_next


def toggle_habit_for_today(data: dict, habit_id: int, checked: bool):
    today = get_today_date()
    entry = find_or_create_day_entry(data, today)
    habit = get_habit_by_id(data, habit_id)
    if habit is None:
        return False, None, None
    prev_total = data["profile"].get("total_xp", 0)
    prev_level = get_level(prev_total)[0]
    if checked:
        if habit_id not in entry["completed"]:
            entry["completed"].append(habit_id)
            data["profile"]["total_xp"] = prev_total + habit.get("xp", 0)
    else:
        if habit_id in entry["completed"]:
            entry["completed"].remove(habit_id)
            data["profile"]["total_xp"] = max(0, prev_total - habit.get("xp", 0))
    new_total = data["profile"].get("total_xp", 0)
    new_level = get_level(new_total)[0]
    leveled_up = new_level > prev_level
    return leveled_up, prev_level, new_level


def update_profile_name(data: dict, new_name: str) -> None:
    data.setdefault("profile", {})["name"] = new_name


def add_habit(data: dict, name: str, xp: int, emoji: str) -> None:
    habits = data.setdefault("habits", [])
    new_id = max([h.get("id", 0) for h in habits]) + 1 if habits else 1
    habits.append({
        "id": new_id,
        "name": name,
        "xp": xp,
        "emoji": emoji
    })


def delete_habit(data: dict, habit_id: int) -> None:
    data["habits"] = [h for h in data.get("habits", []) if h.get("id") != habit_id]
    # Clean up from completed list of logs to keep data clean
    for entry in data.get("daily_log", []):
        if habit_id in entry.get("completed", []):
            try:
                entry["completed"].remove(habit_id)
            except ValueError:
                pass

