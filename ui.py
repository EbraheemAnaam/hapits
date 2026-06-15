import streamlit as st
import plotly.express as px
from data import get_level, LEVEL_XP, find_or_create_day_entry, toggle_habit_for_today, save_data, get_today_date
from analytics import get_stats_dataframe, compute_streak, top_habit_counts, longest_streak, day_of_week_rates, completion_histogram


def inject_css():
    css = """
    <style>
    :root{ --muted: #f4fbff; --blue-600: #0b6fbf; --accent: #0288d1; --text: #0b2545; --card-shadow: 0 6px 18px rgba(11,38,69,0.08); --radius: 12px; }
    /* RTL + global text color */
    .stApp, .block-container, .stMarkdown, .stText, .stHeader, h1, h2, h3, h4, p { direction: rtl; text-align: right; color:var(--text) !important; }
    .stApp{ background: linear-gradient(180deg, var(--muted) 0%, #ffffff 60%); color:var(--text); }
    .hapits-header{ background: linear-gradient(90deg, rgba(6,147,227,0.12), rgba(2,136,209,0.08)); border-radius:var(--radius); padding:18px 22px; box-shadow:var(--card-shadow); margin-bottom:12px }
    .hapits-title{ color:var(--blue-600); font-weight:700; font-size:26px }
    .habit-card{ background:#fff; border-radius:10px; padding:12px 14px; box-shadow:var(--card-shadow); margin-bottom:10px; display:flex; align-items:center; justify-content:flex-start }
    .habit-label{ font-size:16px }
    .habit-xp{ color:var(--accent); }
    .hp-progress{ background:#edf8ff; border-radius:12px; padding:6px }
    .hp-progress > .bar{ height:14px; border-radius:10px; background:linear-gradient(90deg,#66d9ff,#0b6fbf); }
    /* Ensure Streamlit widgets readable */
    .stCheckbox, .stSlider, .stButton, .stMetric, .stTextInput { color:var(--text) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color:var(--text) !important; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header(profile: dict, total_xp: int):
    level, xp_in_level, xp_to_next = get_level(total_xp)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class='hapits-header'>
          <div style='display:flex;align-items:center;gap:12px'>
            <div style='font-size:28px'>🎯</div>
            <div>
              <div class='hapits-title'>Hapits — تتبع العادات بأسلوب الألعاب</div>
              <div class='hapits-sub'>مرحباً، {profile.get('name','المستخدم')}! اجعل كل يوم فرصة جديدة.</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.metric(label="المستوى الحالي", value=f"{level}")
        progress = int((xp_in_level / LEVEL_XP) * 100)
        st.markdown(f"""
        <div style='margin-top:6px'>
          <div style='font-size:13px;margin-bottom:6px;color:#07335b'>XP داخل المستوى: {xp_in_level} / {LEVEL_XP} — للوصول للمستوى التالي: {xp_to_next}</div>
          <div class='hp-progress'><div class='bar' style='width:{progress}%;'></div></div>
        </div>
        """, unsafe_allow_html=True)


def render_habits(data: dict):
    today = find_or_create_day_entry(data, get_today_date())
    # Use local today entry to ensure existing behavior
    # Initialize session state
    for habit in data.get("habits", []):
        hid = habit.get("id")
        key = f"habit_{hid}"
        if key not in st.session_state:
            st.session_state[key] = hid in today.get("completed", [])

    # Render cards
    for habit in data.get("habits", []):
        hid = habit.get("id")
        key = f"habit_{hid}"
        emoji = habit.get('emoji','')
        name = habit.get('name')
        xp = habit.get('xp')
        col_a, col_b = st.columns([9,1])
        with col_a:
            st.markdown(f"<div class='habit-card'><div style='display:flex;align-items:center;gap:12px;width:100%'><div class='habit-label'>{emoji} {name}</div><div style='margin-left:auto;color:var(--accent);font-weight:600'>{xp} XP</div></div></div>", unsafe_allow_html=True)
        with col_b:
            st.checkbox("", key=key)

    # Persist changes
    for habit in data.get("habits", []):
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


def render_analytics(data: dict):
    st.markdown("---")
    # center analytics in the middle column
    left, center, right = st.columns([1, 6, 1])
    with center:
        st.markdown("### الإحصائيات")
        days = st.slider("عدد الأيام للعرض", min_value=7, max_value=30, value=14)

        # Completion rate over time
        df = get_stats_dataframe(data, days=days)
        st.subheader("نسبة إنجاز العادات (آخر الأيام)")
        if not df.empty:
            fig = px.bar(df.reset_index(), x='date', y='completion_rate',
                         labels={'completion_rate': 'نسبة الإنجاز', 'date': 'التاريخ'},
                         color_discrete_sequence=['#66d9ff'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              xaxis_tickangle=-45, font_color='rgb(11,37,69)', margin=dict(t=10, b=30))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية لعرض الرسم البياني.")

        # Day-of-week rates
        dow = day_of_week_rates(data, days=days)
        if not dow.empty:
            st.subheader("متوسط الإكمال حسب يوم الأسبوع")
            fig_dow = px.bar(dow.reset_index(), x='weekday', y='rate', color_discrete_sequence=['#0b6fbf'])
            fig_dow.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='rgb(11,37,69)')
            st.plotly_chart(fig_dow, use_container_width=True)

        # Histogram of completed counts per day
        hist = completion_histogram(data, days=days)
        if not hist.empty:
            st.subheader("توزيع عدد العادات المُنجَزة في اليوم")
            fig_hist = px.histogram(hist.reset_index(), x='completed_count', nbins=5, color_discrete_sequence=['#0288d1'])
            fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='rgb(11,37,69)')
            st.plotly_chart(fig_hist, use_container_width=True)

        # Summary metrics
        st.markdown("---")
        cur_streak = compute_streak(data)
        long_streak = longest_streak(data)
        st.write(f"**المسلسل الحالي (Streak):** {cur_streak} يوم")
        st.write(f"**أطول مسلسل (Longest streak):** {long_streak} يوم")

        avg = df['completion_rate'].mean() if not df.empty else 0.0
        st.write(f"**المتوسط اليومي لإنجاز العادات (آخر {days} يوماً):** {avg:.0%}")

        # Top habits pie / bar
        top_df = top_habit_counts(data, days=days)
        if not top_df.empty:
            st.subheader("أكثر العادات إنجازاً")
            fig2 = px.bar(top_df.reset_index(), x='habit', y='count', color_discrete_sequence=['#0288d1'])
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='rgb(11,37,69)')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية لعرض عادات شائعة.")
