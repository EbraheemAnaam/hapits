"""
data_cloud.py
=============
نسخة محسّنة من data.py تستخدم JSONBin.io بدلاً من الملف المحلي.

كيفية الاستخدام:
  بدّل في app.py السطر:
      from data import load_data, save_data, ...
  إلى:
      from data_cloud import load_data, save_data, ...
"""

from datetime import date
from jsonbin_client import (
    fetch_data,
    push_data,
    add_habit     as _add_habit_remote,
    delete_habit  as _delete_habit_remote,
    update_profile as _update_profile_remote,
)

# ─────────────────────────────────────────────
#  ثوابت
# ─────────────────────────────────────────────
LEVEL_XP = 1000


# ══════════════════════════════════════════════
#  دوال متوافقة تماماً مع data.py الأصلية
#  (نفس الأسماء ونفس المعاملات)
# ══════════════════════════════════════════════

def get_today_date() -> str:
    return date.today().isoformat()


def load_data(*args, **kwargs) -> dict:
    """جلب البيانات من JSONBin (يحل محل قراءة الملف المحلي)."""
    return fetch_data()


def save_data(data: dict, *args, **kwargs) -> None:
    """رفع البيانات الكاملة إلى JSONBin (يحل محل الكتابة للملف المحلي)."""
    push_data(data)


def find_or_create_day_entry(data: dict, day: str) -> dict:
    """ابحث عن إدخال اليوم في daily_log أو أنشئ واحداً جديداً."""
    for entry in data.get("daily_log", []):
        if entry.get("date") == day:
            return entry
    new = {"date": day, "completed": []}
    data.setdefault("daily_log", []).append(new)
    return new


def get_habit_by_id(data: dict, hid: int) -> dict:
    """البحث عن عادة باستخدام الـ ID."""
    for h in data.get("habits", []):
        if h.get("id") == hid:
            return h
    return None


def get_level(total_xp: int):
    """حساب المستوى الحالي وتفاصيل XP."""
    level = (total_xp // LEVEL_XP) + 1
    xp_in_level = total_xp % LEVEL_XP
    xp_to_next = LEVEL_XP - xp_in_level
    return level, xp_in_level, xp_to_next


def toggle_habit_for_today(data: dict, habit_id: int, checked: bool):
    """
    تعليم عادة كمكتملة أو غير مكتملة لليوم الحالي.
    يحفظ التغييرات تلقائياً على JSONBin.

    Returns:
        (leveled_up: bool, prev_level: int, new_level: int)
    """
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

    # ─── حفظ التغييرات على السحابة ───
    save_data(data)

    new_total = data["profile"].get("total_xp", 0)
    new_level = get_level(new_total)[0]
    leveled_up = new_level > prev_level

    return leveled_up, prev_level, new_level


def update_profile_name(data: dict, new_name: str) -> None:
    """تحديث اسم المستخدم في الملف الشخصي وحفظه على JSONBin."""
    data.setdefault("profile", {})["name"] = new_name
    save_data(data)


def add_habit(data: dict, name: str, xp: int, emoji: str) -> None:
    """
    إضافة عادة جديدة بـ ID تلقائي وحفظها على JSONBin.
    يُحدّث كائن data محلياً أيضاً.
    """
    habits = data.setdefault("habits", [])
    new_id = max((h.get("id", 0) for h in habits), default=0) + 1
    new_habit = {
        "id":    new_id,
        "name":  name.strip(),
        "xp":    max(0, int(xp)),
        "emoji": emoji,
    }
    habits.append(new_habit)
    save_data(data)


def delete_habit(data: dict, habit_id: int) -> None:
    """
    حذف عادة من data وتنظيف daily_log منها، ثم الحفظ على JSONBin.
    """
    data["habits"] = [
        h for h in data.get("habits", []) if h.get("id") != habit_id
    ]
    # تنظيف السجل اليومي من أي إشارة للعادة المحذوفة
    for entry in data.get("daily_log", []):
        completed = entry.get("completed", [])
        if habit_id in completed:
            entry["completed"] = [c for c in completed if c != habit_id]
    save_data(data)
