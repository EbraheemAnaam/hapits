import pandas as pd
from datetime import date, timedelta


def get_stats_dataframe(data: dict, days: int = 14) -> pd.DataFrame:
    today = date.today()
    log_map = {entry["date"]: entry.get("completed", []) for entry in data.get("daily_log", [])}
    rows = []
    total_habits = max(1, len(data.get("habits", [])))
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        completed = len(log_map.get(d, []))
        rows.append({"date": d, "completion_rate": completed / total_habits})
    df = pd.DataFrame(rows).set_index("date")
    return df


def compute_streak(data: dict) -> int:
    today = date.today()
    log_map = {entry["date"]: entry.get("completed", []) for entry in data.get("daily_log", [])}
    streak = 0
    i = 0
    while True:
        d = (today - timedelta(days=i)).isoformat()
        completed = len(log_map.get(d, []))
        if completed > 0:
            streak += 1
            i += 1
        else:
            break
    return streak


def top_habit_counts(data: dict, days: int = None) -> pd.DataFrame:
    cutoff = None
    if days is not None:
        cutoff = (date.today() - timedelta(days=days - 1)).isoformat()
    counts = {}
    habits_map = {h["id"]: h for h in data.get("habits", [])}
    for entry in data.get("daily_log", []):
        d = entry.get("date")
        if cutoff and d < cutoff:
            continue
        for hid in entry.get("completed", []):
            counts[hid] = counts.get(hid, 0) + 1
    rows = []
    for hid, cnt in counts.items():
        name = habits_map.get(hid, {}).get("name", str(hid))
        rows.append({"habit": name, "count": cnt})
    if not rows:
        return pd.DataFrame(columns=["habit", "count"])
    df = pd.DataFrame(rows).sort_values("count", ascending=False).set_index("habit")
    return df


def longest_streak(data: dict) -> int:
    """Compute the longest consecutive-day streak in the data."""
    dates = sorted([entry["date"] for entry in data.get("daily_log", [])])
    if not dates:
        return 0
    # convert to date objects
    from datetime import datetime, timedelta
    parsed = [datetime.fromisoformat(d).date() for d in dates]
    max_streak = 0
    cur_streak = 1
    for i in range(1, len(parsed)):
        if parsed[i] - parsed[i - 1] == timedelta(days=1) and len([e for e in data.get("daily_log", []) if e["date"] == parsed[i].isoformat() and e.get("completed")]):
            cur_streak += 1
        else:
            max_streak = max(max_streak, cur_streak)
            cur_streak = 1
    max_streak = max(max_streak, cur_streak)
    return max_streak


def day_of_week_rates(data: dict, days: int = None) -> pd.DataFrame:
    """Return average completion_rate per day of week (Mon-Sun) over given window."""
    from datetime import date, timedelta, datetime
    total_habits = max(1, len(data.get("habits", [])))
    counts = {i: [] for i in range(7)}
    today = date.today()
    for entry in data.get("daily_log", []):
        d = datetime.fromisoformat(entry["date"]).date()
        if days is not None and d < (today - timedelta(days=days - 1)):
            continue
        comp = len(entry.get("completed", [])) / total_habits
        counts[d.weekday()].append(comp)
    rows = []
    names = ['الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت','الأحد']
    for i in range(7):
        vals = counts.get(i, [])
        avg = sum(vals) / len(vals) if vals else 0.0
        rows.append({"weekday": names[i], "rate": avg})
    df = pd.DataFrame(rows).set_index("weekday")
    return df


def completion_histogram(data: dict, days: int = None) -> pd.DataFrame:
    """Return per-day counts of completed habits for histogram/charting."""
    from datetime import date, timedelta, datetime
    today = date.today()
    rows = []
    for entry in data.get("daily_log", []):
        d = datetime.fromisoformat(entry["date"]).date()
        if days is not None and d < (today - timedelta(days=days - 1)):
            continue
        rows.append({"date": entry["date"], "completed_count": len(entry.get("completed", []))})
    if not rows:
        return pd.DataFrame(columns=["date", "completed_count"]).set_index("date")
    df = pd.DataFrame(rows).set_index("date")
    return df
