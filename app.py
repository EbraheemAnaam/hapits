import streamlit as st
from data_cloud import load_data, save_data, get_today_date, find_or_create_day_entry
from ui import inject_css, render_header, render_habits, render_analytics, render_settings


def main():
    st.set_page_config(page_title="Hapits — تتبع العادات بأسلوب الألعاب", layout="wide")
    
    # Load user data
    data = load_data()
    profile = data.get("profile", {})
    total_xp = profile.get("total_xp", 0)

    # Inject custom modern styles
    inject_css()

    # RPG Level and Info Header
    render_header(profile, total_xp)

    # Initialize today's log entry
    today = get_today_date()
    find_or_create_day_entry(data, today)

    # Create top level tabs for modern visual hierarchy
    tab1, tab2, tab3 = st.tabs([
        "🎯 تتبع اليوم (Daily Log)",
        "📊 الإحصائيات والتحليلات (Analytics)",
        "⚙️ إدارة العادات والملف الشخصي (Settings)"
    ])

    with tab1:
        st.markdown(f"### 📅 تتبع العادات ليوم: <span style='color:#4F46E5; font-weight:700;'>{today}</span>", unsafe_allow_html=True)
        st.markdown("قم بإكمال عاداتك اليوم للحصول على نقاط الخبرة (XP) والارتقاء بالمستوى!")
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        render_habits(data)

    with tab2:
        render_analytics(data)

    with tab3:
        render_settings(data)

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: var(--text-sub); font-size: 14px;'>🛡️ يتم حفظ بياناتك وإنجازاتك تلقائياً في ملف <code>habits_data.json</code> المحلي.</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
