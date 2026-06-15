# Hapits — Habit Tracker (Streamlit)

تطبيق محلي لتتبع العادات بأسلوب الألعاب (Gamification) مكتوب بـ Python + Streamlit ويستخدم ملف JSON محلي كقاعدة بيانات.

## الملفات
- `app.py` — ملف التشغيل الرئيسي (مبسّط، يستورد الموديولات).
- `data.py` — تحميل/حفظ بيانات JSON ومنطق الـ XP.
- `analytics.py` — دوال إحصائية وتحليلات.
- `ui.py` — العرض (Streamlit UI) وحقن CSS.
- `habits_data.json` — ملف البيانات المحلي (سيُنشأ تلقائياً).
- `requirements.txt` — الاعتماديات.

## تشغيل محلي
1. إنشاء بيئة افتراضية (موصى):

```bash
python -m venv .venv
.\.venv\Scripts\activate    # Windows PowerShell
```

2. تثبيت الاعتماديات:

```bash
pip install -r requirements.txt
```

3. تشغيل التطبيق:

```bash
streamlit run app.py
```

## رفع إلى GitHub
1. أنشئ مستودعًا جديدًا على GitHub (مثلاً `Hapits`).
2. اربط المستودع المحلي بالـ remote ثم ادفع الفرع `main`:

```bash
git remote add origin https://github.com/<your-username>/<repo>.git
git branch -M main
git push -u origin main
```

إذا أردت، أستطيع إعداد الـ git محليًا وتنفيذ `commit` أولي هنا، لكن لا أستطيع دفع الملفات إلى GitHub بدون بيانات اعتمادك (token).
