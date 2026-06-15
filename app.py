import streamlit as st
from data import load_data, save_data
from ui import inject_css, render_header, render_habits, render_analytics


def main():
    st.set_page_config(page_title="Hapits — تتبع العادات", layout="wide")
    inject_css()

    data = load_data()
    profile = data.get("profile", {})
    total_xp = profile.get("total_xp", 0)

    # Header
    render_header(profile, total_xp)

    st.markdown("---")

    # Daily Dashboard title
    st.header("لوحة اليوم — Daily Dashboard")
    from data import get_today_date, find_or_create_day_entry
    today = get_today_date()
    st.subheader(f"التاريخ: {today}")
    find_or_create_day_entry(data, today)

    # Habits UI (handles persistence)
    render_habits(data)

    # Analytics and profile editor moved into main UI
    render_analytics(data)

    st.markdown("---")
    st.write("**ملاحظات:** يتم حفظ البيانات محلياً في ملف `habits_data.json` في نفس مجلد التطبيق.")


if __name__ == "__main__":
    main()
