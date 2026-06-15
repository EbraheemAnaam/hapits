import streamlit as st
import plotly.express as px
from data_cloud import get_level, LEVEL_XP, find_or_create_day_entry, toggle_habit_for_today, save_data, get_today_date
from analytics import get_stats_dataframe, compute_streak, top_habit_counts, longest_streak, day_of_week_rates, completion_histogram


def inject_css():
    css = """
    <style>
    @import url('https://fonts.bunny.net/css?family=tajawal:300,400,500,700,900&display=swap');

    :root {
        --primary: #4F46E5;
        --secondary: #06B6D4;
        --background: #f8fafc;
        --card-bg: #ffffff;
        --text-main: #0f172a;
        --text-sub: #475569;
        --accent: #6366f1;
        --card-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        --radius-lg: 16px;
        --radius-md: 12px;
    }

    /* RTL Layout and fonts */
    html, body, [class*="css"], .stApp {
        font-family: 'Tajawal', 'Segoe UI', Tahoma, Arial, sans-serif !important;
        direction: rtl;
        text-align: right;
        color: var(--text-main);
    }
    .stApp * {
        font-family: 'Tajawal', 'Segoe UI', Tahoma, Arial, sans-serif !important;
    }

    /* =====================================================
       FORCE VISIBLE TEXT - CONTENT AREAS ONLY (not widgets)
       ===================================================== */
    [data-testid="stMarkdownContainer"] *,
    [data-testid="stText"] *,
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricDelta"] {
        color: #0f172a !important;
    }

    /* Force the app background and base text */
    .block-container, .main .block-container {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* Input fields — force light background with dark text */
    input, textarea,
    [data-baseweb="base-input"] input,
    [data-baseweb="input"] input,
    .stTextInput input,
    .stNumberInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-color: #cbd5e1 !important;
    }
    [data-baseweb="base-input"],
    [data-baseweb="input"] {
        background-color: #ffffff !important;
    }

    /* Buttons — force readable style */
    .stButton > button {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #e2e8f0 !important;
        border-color: #94a3b8 !important;
    }
    /* Delete button — red style */
    button[kind="secondary"] {
        background-color: #fff1f2 !important;
        color: #dc2626 !important;
        border-color: #fecaca !important;
    }

    /* Number input +/- stepper buttons */
    [data-testid="stNumberInput"] button,
    [data-testid="stNumberInputStepUp"],
    [data-testid="stNumberInputStepDown"],
    [data-baseweb="spinner"] button,
    button[aria-label="increment"],
    button[aria-label="decrement"] {
        background-color: #e2e8f0 !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }
    [data-testid="stNumberInput"] button:hover,
    button[aria-label="increment"]:hover,
    button[aria-label="decrement"]:hover {
        background-color: #cbd5e1 !important;
        color: #0f172a !important;
    }

    /* Date input widget */
    [data-testid="stDateInput"] input,
    [data-baseweb="datepicker"] input,
    input[type="date"],
    .stDateInput div[data-baseweb="input"],
    [data-testid="stDateInput"] [data-baseweb="base-input"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    /* Date picker calendar popover */
    [data-baseweb="popover"],
    [data-baseweb="calendar"],
    [data-baseweb="calendar"] * {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    /* Date segments (day/month/year blocks) */
    [data-testid="stDateInput"] span,
    [data-baseweb="input"] span,
    div[data-baseweb="input"] span {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }

    /* Restore white text ONLY inside profile dashboard */
    .profile-dashboard,
    .profile-dashboard p,
    .profile-dashboard span,
    .profile-dashboard div,
    .profile-dashboard .avatar-level,
    .profile-dashboard .profile-name,
    .profile-dashboard .profile-subtitle,
    .profile-dashboard .xp-label,
    .profile-dashboard .xp-values,
    .profile-dashboard .xp-percentage,
    .profile-dashboard .xp-next-level {
        color: #ffffff !important;
    }

    /* Habit card text colors */
    .habit-name-new { color: #0f172a !important; }
    .habit-xp-new { color: #06B6D4 !important; }

    .stApp {
        background-color: var(--background);
        color: var(--text-main);
    }

    /* Override block-containers to center layout nicely */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 900px !important;
    }

    /* RPG Dashboard Styles */
    .profile-dashboard {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border-radius: var(--radius-lg);
        padding: 24px;
        color: #ffffff !important;
        box-shadow: 0 10px 25px rgba(49, 46, 129, 0.15);
        margin-bottom: 24px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .profile-dashboard .profile-name,
    .profile-dashboard .profile-subtitle,
    .profile-dashboard .xp-label,
    .profile-dashboard .xp-values,
    .profile-dashboard .xp-percentage,
    .profile-dashboard .xp-next-level,
    .profile-dashboard .avatar-level {
        color: #ffffff !important;
    }
    .profile-avatar-section {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .avatar-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        border: 4px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.5);
    }
    .avatar-level {
        font-size: 32px;
        font-weight: 900;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .profile-info {
        display: flex;
        flex-direction: column;
    }
    .profile-name {
        margin: 0 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    .profile-subtitle {
        margin: 4px 0 0 0 !important;
        font-size: 14px !important;
        opacity: 0.8;
    }
    .xp-progress-section {
        flex-grow: 1;
        max-width: 420px;
        width: 100%;
    }
    .xp-details {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .xp-bar-container {
        height: 18px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .xp-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #06b6d4 0%, #3b82f6 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 8px;
        transition: width 0.5s ease;
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
    }
    .xp-percentage {
        font-size: 11px;
        font-weight: 700;
    }
    .xp-next-level {
        margin: 6px 0 0 0 !important;
        font-size: 12px !important;
        opacity: 0.8;
        text-align: left;
    }

    /* Habit Cards Styling */
    .habit-card-new {
        background: var(--card-bg);
        border-radius: var(--radius-md);
        padding: 14px 18px;
        box-shadow: var(--card-shadow);
        border: 1px solid #e2e8f0;
        transition: all 0.25s ease;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 8px;
        width: 100%;
    }
    .habit-card-new:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }
    .habit-completed {
        opacity: 0.65;
        background-color: #f8fafc;
        border-color: #e2e8f0;
    }
    .habit-emoji-wrapper {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: #f1f5f9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }
    .habit-completed .habit-emoji-wrapper {
        background: #e2e8f0;
    }
    .habit-content-wrapper {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .habit-name-new {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-main) !important;
        margin: 0 !important;
    }
    .habit-xp-new {
        font-size: 13px;
        font-weight: 700;
        color: var(--secondary) !important;
        margin-top: 2px;
    }

    /* Horizontal block columns custom alignment */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
        background: transparent;
        padding: 4px 0;
    }

    /* Streamlit tabs override */
    div[data-testid="stTabBar"] {
        background: transparent;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 24px;
    }
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: var(--text-sub) !important;
        padding: 10px 16px !important;
        transition: all 0.2s ease !important;
        border-bottom: 3px solid transparent !important;
    }
    button[data-baseweb="tab"]:hover {
        color: var(--primary) !important;
    }
    button[aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
    }

    /* Streamlit interactive widgets custom alignment */
    div[data-testid="stCheckbox"] {
        margin: 0 !important;
        padding: 0 !important;
        display: flex;
        justify-content: center;
    }
    div[data-testid="stCheckbox"] label {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Success message & widgets styling */
    .stAlert {
        border-radius: var(--radius-md) !important;
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header(profile: dict, total_xp: int):
    level, xp_in_level, xp_to_next = get_level(total_xp)
    progress = int((xp_in_level / LEVEL_XP) * 100)
    
    st.markdown(f"""
    <div class='profile-dashboard'>
        <div class='profile-avatar-section'>
            <div class='avatar-circle'>
                <span class='avatar-level'>{level}</span>
            </div>
            <div class='profile-info'>
                <h2 class='profile-name'>أهلاً بك، {profile.get('name','المستخدم')} 👋</h2>
                <p class='profile-subtitle'>مستواك الحالي في عالم العادات. استمر في السعي نحو التميز!</p>
            </div>
        </div>
        <div class='xp-progress-section'>
            <div class='xp-details'>
                <span class='xp-label'>نقاط الخبرة (XP)</span>
                <span class='xp-values'>{xp_in_level} / {LEVEL_XP} XP</span>
            </div>
            <div class='xp-bar-container'>
                <div class='xp-bar-fill' style='width: {progress}%'>
                    <span class='xp-percentage'>{progress}%</span>
                </div>
            </div>
            <p class='xp-next-level'>متبقي {xp_to_next} XP للوصول للمستوى {level + 1} 🚀</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_habits(data: dict):
    today = find_or_create_day_entry(data, get_today_date())
    
    # Initialize session state for all habits
    for habit in data.get("habits", []):
        hid = habit.get("id")
        key = f"habit_{hid}"
        if key not in st.session_state:
            st.session_state[key] = hid in today.get("completed", [])

    # Render cards
    habits_list = data.get("habits", [])
    if not habits_list:
        st.info("لا توجد عادات مضافة بعد. انتقل إلى علامة التبويب 'إدارة العادات' لإضافة عادتك الأولى! ➕")
        return

    for habit in habits_list:
        hid = habit.get("id")
        key = f"habit_{hid}"
        emoji = habit.get('emoji', '🎯')
        name = habit.get('name')
        xp = habit.get('xp')
        
        # Determine current status
        checked = bool(st.session_state.get(key, False))
        
        # Checkbox column first (appears on the right in RTL), card column second (left in RTL)
        col_check, col_card = st.columns([1, 12])
        with col_check:
            st.checkbox("", key=key, label_visibility="collapsed")
        with col_card:
            card_class = "habit-card-new habit-completed" if checked else "habit-card-new"
            display_name = f"<s>{name}</s>" if checked else name
            st.markdown(f"""
            <div class='{card_class}'>
                <div class='habit-emoji-wrapper'>{emoji}</div>
                <div class='habit-content-wrapper'>
                    <p class='habit-name-new'>{display_name}</p>
                    <span class='habit-xp-new'>+{xp} XP</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Persist changes
    for habit in habits_list:
        hid = habit.get("id")
        key = f"habit_{hid}"
        checked = bool(st.session_state.get(key, False))
        today_entry = find_or_create_day_entry(data, get_today_date())
        currently_checked = hid in today_entry.get("completed", [])
        if checked != currently_checked:
            leveled_up, prev_level, new_level = toggle_habit_for_today(data, hid, checked)
            save_data(data)
            if leveled_up:
                st.success(f"تهانينا! ارتقيت من المستوى {prev_level} إلى المستوى {new_level} 🎉")
                st.balloons()
            st.rerun()


def render_analytics(data: dict):
    st.markdown("### 📊 لوحة التحليلات والإحصائيات")
    days = st.slider("عدد الأيام للعرض", min_value=7, max_value=30, value=14)

    # Summary metrics in 3 columns
    cur_streak = compute_streak(data)
    long_streak = longest_streak(data)
    df = get_stats_dataframe(data, days=days)
    avg = df['completion_rate'].mean() if not df.empty else 0.0

    st.markdown("<div style='margin-top:15px'></div>", unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="🔥 المسلسل الحالي (Streak)", value=f"{cur_streak} يوم")
    with col_m2:
        st.metric(label="🏆 أطول مسلسل متتالي", value=f"{long_streak} يوم")
    with col_m3:
        st.metric(label="📈 متوسط الإنجاز", value=f"{avg:.0%}")
    st.markdown("<div style='margin-bottom:25px'></div>", unsafe_allow_html=True)

    # Charts section
    # 1. Completion rate over time
    st.markdown("#### 📅 نسبة إنجاز العادات اليومية")
    if not df.empty:
        fig = px.bar(df.reset_index(), x='date', y='completion_rate',
                     labels={'completion_rate': 'نسبة الإنجاز', 'date': 'التاريخ'},
                     color_discrete_sequence=['#4F46E5'])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45,
            font_family='Tajawal, Segoe UI, Tahoma, Arial',
            font_color='#0f172a',
            margin=dict(t=10, b=30, l=10, r=10),
            xaxis=dict(showgrid=False, linecolor='#E2E8F0'),
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9', linecolor='#E2E8F0', tickformat='.0%')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات كافية لعرض الرسم البياني اليومي.")

    # 2. Day of week and Completion Histogram side-by-side
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("#### 🗓️ متوسط الإنجاز حسب أيام الأسبوع")
        dow = day_of_week_rates(data, days=days)
        if not dow.empty:
            fig_dow = px.bar(dow.reset_index(), x='weekday', y='rate', 
                             labels={'rate': 'نسبة الإكمال', 'weekday': 'اليوم'},
                             color_discrete_sequence=['#06B6D4'])
            fig_dow.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='Tajawal, Segoe UI, Tahoma, Arial',
                font_color='#0f172a',
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis=dict(showgrid=False, linecolor='#E2E8F0'),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9', linecolor='#E2E8F0', tickformat='.0%')
            )
            st.plotly_chart(fig_dow, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية.")

    with col_c2:
        st.markdown("#### 📊 توزيع عدد العادات المنجزة")
        hist = completion_histogram(data, days=days)
        if not hist.empty:
            fig_hist = px.histogram(hist.reset_index(), x='completed_count',
                                    labels={'completed_count': 'عدد العادات المنجزة', 'count': 'عدد الأيام'},
                                    color_discrete_sequence=['#6366F1'])
            fig_hist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='Tajawal',
                font_color='#0f172a',
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis=dict(showgrid=False, linecolor='#E2E8F0', dtick=1),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9', linecolor='#E2E8F0')
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية.")

    # 3. Top habits counts
    st.markdown("#### 🏆 أكثر العادات إنجازاً وسلوكاً")
    top_df = top_habit_counts(data, days=days)
    if not top_df.empty:
        fig2 = px.bar(top_df.reset_index(), x='habit', y='count',
                      labels={'count': 'مرات التكرار', 'habit': 'العادة'},
                      color_discrete_sequence=['#10B981'])
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family='Tajawal',
            font_color='#0f172a',
            margin=dict(t=10, b=20, l=10, r=10),
            xaxis=dict(showgrid=False, linecolor='#E2E8F0'),
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9', linecolor='#E2E8F0')
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا توجد بيانات كافية لعرض إحصائيات العادات.")


def render_settings(data: dict):
    st.markdown("### ⚙️ إدارة العادات وملف التعريف")
    
    # Profile update card
    with st.container(border=True):
        st.subheader("👤 تعديل الملف الشخصي")
        current_name = data.get("profile", {}).get("name", "المستخدم")
        new_name = st.text_input("الاسم الجديد", value=current_name)
        if st.button("حفظ اسم المستخدم", key="save_profile_name"):
            from data_cloud import update_profile_name, save_data
            update_profile_name(data, new_name)
            save_data(data)
            st.success("تم تحديث الاسم بنجاح! 🎉")
            st.rerun()

    # Add habit card
    with st.container(border=True):
        st.subheader("➕ إضافة عادة جديدة")
        col_n, col_x, col_e = st.columns([3, 1, 1])
        with col_n:
            h_name = st.text_input("اسم العادة (مثال: قراءة القرآن، النوم مبكراً)")
        with col_x:
            h_xp = st.number_input("النقاط (XP)", min_value=10, max_value=1000, value=100, step=10)
        with col_e:
            h_emoji = st.text_input("الرمز التعبيري", value="🎯")
            
        if st.button("إضافة العادة", key="btn_add_habit"):
            if not h_name.strip():
                st.error("الرجاء إدخال اسم العادة!")
            else:
                from data_cloud import add_habit, save_data
                add_habit(data, h_name, int(h_xp), h_emoji)
                save_data(data)
                st.success(f"تمت إضافة العادة '{h_name}' بنجاح! 🎉")
                st.rerun()

    # Existing habits list card
    with st.container(border=True):
        st.subheader("🗑️ إدارة العادات الحالية")
        habits = data.get("habits", [])
        if not habits:
            st.info("لا توجد عادات حالياً.")
        else:
            for habit in habits:
                hid = habit.get("id")
                col_info, col_del = st.columns([6, 1])
                with col_info:
                    st.markdown(f"""
                    <div style='display: flex; align-items: center; gap: 12px; padding: 8px 0;'>
                        <span style='font-size: 20px;'>{habit.get('emoji', '🎯')}</span>
                        <div>
                            <span style='font-weight: 600; font-size: 16px; color: var(--text-main);'>{habit.get('name')}</span>
                            <span style='color: var(--primary); font-weight: 700; margin-right: 8px; font-size: 14px;'>+{habit.get('xp')} XP</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    # Render a red delete button
                    if st.button("حذف", key=f"del_{hid}", type="secondary"):
                        from data_cloud import delete_habit, save_data
                        delete_habit(data, hid)
                        save_data(data)
                        st.success(f"تم حذف العادة! 🗑️")
                        st.rerun()
