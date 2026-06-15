"""
jsonbin_client.py
=================
وحدة للتواصل مع JSONBin.io كقاعدة بيانات سحابية لمشروع Hapits.

كيفية الإعداد:
  1. أنشئ حساباً على https://jsonbin.io
  2. اذهب إلى Dashboard → API Keys وانسخ الـ Master Key
  3. أنشئ Bin جديداً يحتوي على بيانات JSON الأولية (أو استخدم init_remote_bin أدناه)
  4. انسخ الـ Bin ID من رابطه
  5. استبدل القيمتين التاليتين بمفاتيحك الحقيقية:
"""

import time
import json
import requests

# ─────────────────────────────────────────────
#  ⚠️ استبدل هذين المتغيرين بقيمك الحقيقية
# ─────────────────────────────────────────────
MASTER_KEY = "$2a$10$Ec4eijWTHqZzJSAzRw/jOud1JmK/Bky2HwYeqLtg4vzbZ4Jydlfl6"   # مثال: $2a$10$abcdef...
BIN_ID     = "6a2fe4e4f5f4af5e29f4bf6f"       # مثال: 684f2c3ae41b4d34e87b1234

# ─────────────────────────────────────────────
#  إعدادات API الثابتة — لا تعدّلها
# ─────────────────────────────────────────────
BASE_URL = "https://api.jsonbin.io/v3"
HEADERS = {
    "X-Master-Key": MASTER_KEY,
    "Content-Type": "application/json",
}

# عدد محاولات إعادة الاتصال عند الفشل
MAX_RETRIES = 3
RETRY_DELAY = 1.5  # ثانية


# ══════════════════════════════════════════════
#  الدوال الأساسية (CRUD)
# ══════════════════════════════════════════════

def fetch_data() -> dict:
    """
    GET — جلب كامل ملف JSON من JSONBin.
    يُستخدم عند تحميل التطبيق لأول مرة.

    Returns:
        dict: كائن البيانات الكامل {profile, habits, daily_log}
    Raises:
        RuntimeError: إذا فشل الاتصال بعد MAX_RETRIES محاولة
    """
    url = f"{BASE_URL}/b/{BIN_ID}/latest"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.json()["record"]
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "?"
            if status == 401:
                raise RuntimeError(
                    "❌ خطأ 401: MASTER_KEY غير صحيح أو منتهي الصلاحية."
                ) from e
            if status == 404:
                raise RuntimeError(
                    f"❌ خطأ 404: BIN_ID '{BIN_ID}' غير موجود."
                ) from e
            # أخطاء أخرى — أعد المحاولة
        except requests.exceptions.ConnectionError:
            pass  # إعادة المحاولة
        except requests.exceptions.Timeout:
            pass  # إعادة المحاولة

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"❌ فشل الاتصال بـ JSONBin بعد {MAX_RETRIES} محاولات. "
        "تحقق من اتصالك بالإنترنت."
    )


def push_data(data: dict) -> bool:
    """
    PUT — رفع كامل كائن JSON إلى JSONBin (يستبدل المحتوى القديم).
    يجب دائماً رفع الكائن كاملاً لأن JSONBin لا يدعم التحديث الجزئي.

    Args:
        data: الكائن الكامل {profile, habits, daily_log}

    Returns:
        True عند النجاح، False عند الفشل.
    """
    url = f"{BASE_URL}/b/{BIN_ID}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.put(
                url,
                headers=HEADERS,
                data=json.dumps(data, ensure_ascii=False),
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    return False


# ══════════════════════════════════════════════
#  دوال العمليات العالية المستوى
#  (تطبّق نمط: جلب → تعديل محلي → رفع)
# ══════════════════════════════════════════════

def update_profile(new_name: str = None, new_xp: int = None) -> dict:
    """
    تحديث حقل الـ profile (الاسم و/أو XP).
    مثال: update_profile(new_name="إبراهيم")

    Returns:
        البيانات المحدّثة بعد الرفع.
    """
    data = fetch_data()

    profile = data.setdefault("profile", {})
    if new_name is not None:
        profile["name"] = new_name.strip()
    if new_xp is not None:
        profile["total_xp"] = max(0, int(new_xp))

    success = push_data(data)
    if not success:
        raise RuntimeError("❌ فشل حفظ الملف الشخصي على JSONBin.")
    return data


def add_habit(name: str, xp: int, emoji: str) -> dict:
    """
    إضافة عادة جديدة إلى مصفوفة habits مع توليد ID تلقائي.

    Args:
        name:  اسم العادة
        xp:    نقاط الخبرة
        emoji: رمز الإيموجي

    Returns:
        البيانات المحدّثة بعد الرفع.
    """
    data = fetch_data()

    habits = data.setdefault("habits", [])
    # توليد ID تلقائي = أعلى ID موجود + 1
    new_id = max((h.get("id", 0) for h in habits), default=0) + 1
    habits.append({
        "id":    new_id,
        "name":  name.strip(),
        "xp":    max(0, int(xp)),
        "emoji": emoji,
    })

    success = push_data(data)
    if not success:
        raise RuntimeError("❌ فشل حفظ العادة الجديدة على JSONBin.")
    return data


def delete_habit(habit_id: int) -> dict:
    """
    حذف عادة من مصفوفة habits باستخدام الـ ID.
    يُنظّف أيضاً سجل daily_log من أي إشارة للعادة المحذوفة.

    Args:
        habit_id: الـ id الخاص بالعادة المراد حذفها

    Returns:
        البيانات المحدّثة بعد الرفع.
    """
    data = fetch_data()

    # حذف العادة من القائمة
    data["habits"] = [
        h for h in data.get("habits", []) if h.get("id") != habit_id
    ]

    # تنظيف daily_log من أي إشارة للعادة المحذوفة
    for entry in data.get("daily_log", []):
        completed = entry.get("completed", [])
        if habit_id in completed:
            entry["completed"] = [c for c in completed if c != habit_id]

    success = push_data(data)
    if not success:
        raise RuntimeError(f"❌ فشل حذف العادة {habit_id} من JSONBin.")
    return data


def toggle_habit_completion(habit_id: int, date_str: str, mark_done: bool) -> dict:
    """
    تعليم عادة كـ "مكتملة" أو "غير مكتملة" ليوم معين مع تحديث XP.

    Args:
        habit_id:  ID العادة
        date_str:  التاريخ بصيغة 'YYYY-MM-DD'
        mark_done: True = إكمال، False = إلغاء الإكمال

    Returns:
        البيانات المحدّثة بعد الرفع.
    """
    data = fetch_data()

    # ابحث عن إدخال اليوم أو أنشئ واحداً
    daily_log = data.setdefault("daily_log", [])
    day_entry = next((e for e in daily_log if e.get("date") == date_str), None)
    if day_entry is None:
        day_entry = {"date": date_str, "completed": []}
        daily_log.append(day_entry)

    # ابحث عن بيانات العادة لمعرفة قيمة XP
    habit = next((h for h in data.get("habits", []) if h.get("id") == habit_id), None)
    if habit is None:
        raise ValueError(f"العادة ذات ID={habit_id} غير موجودة.")

    habit_xp = habit.get("xp", 0)
    completed = day_entry.setdefault("completed", [])
    current_xp = data["profile"].get("total_xp", 0)

    if mark_done and habit_id not in completed:
        completed.append(habit_id)
        data["profile"]["total_xp"] = current_xp + habit_xp
    elif not mark_done and habit_id in completed:
        completed.remove(habit_id)
        data["profile"]["total_xp"] = max(0, current_xp - habit_xp)

    success = push_data(data)
    if not success:
        raise RuntimeError("❌ فشل تحديث حالة العادة على JSONBin.")
    return data


# ══════════════════════════════════════════════
#  أداة الإعداد الأولي (تشغيل مرة واحدة فقط)
# ══════════════════════════════════════════════

def init_remote_bin(initial_data: dict = None) -> str:
    """
    إنشاء Bin جديد على JSONBin وتعبئته بالبيانات الأولية.
    استخدم هذه الدالة مرة واحدة فقط عند الإعداد الأول.

    Args:
        initial_data: البيانات الابتدائية. إذا تركتها فارغة، سيُستخدم الهيكل الافتراضي.

    Returns:
        BIN_ID الخاص بالـ Bin الجديد.
    """
    if initial_data is None:
        initial_data = {
            "profile": {"name": "المستخدم", "total_xp": 0},
            "habits": [
                {"id": 1, "name": "استيقاظ 4:30",        "xp": 150, "emoji": "⏰"},
                {"id": 2, "name": "صلاة الفجر",           "xp": 100, "emoji": "🕌"},
                {"id": 3, "name": "ذهاب للجيم",           "xp": 200, "emoji": "🏋️‍♂️"},
                {"id": 4, "name": "قراءة 30 دقيقة",       "xp": 120, "emoji": "📚"},
                {"id": 5, "name": "صيام صحي/وجبة صحية", "xp":  80, "emoji": "🥗"},
                {"id": 6, "name": "تدوين يومي/تأمل",     "xp":  90, "emoji": "📝"},
                {"id": 7, "name": "تعلم لغة/مهارة",      "xp": 160, "emoji": "💡"},
                {"id": 8, "name": "قراءة القران",         "xp": 100, "emoji": "🎯"},
            ],
            "daily_log": [],
        }

    create_headers = {
        "X-Master-Key":  MASTER_KEY,
        "Content-Type":  "application/json",
        "X-Bin-Private": "true",      # اجعل الـ Bin خاصاً
        "X-Bin-Name":    "hapits-db", # اسم وصفي (اختياري)
    }

    response = requests.post(
        f"{BASE_URL}/b",
        headers=create_headers,
        data=json.dumps(initial_data, ensure_ascii=False),
        timeout=10,
    )
    response.raise_for_status()
    new_bin_id = response.json()["metadata"]["id"]
    print(f"✅ تم إنشاء Bin بنجاح! BIN_ID = {new_bin_id}")
    print("📋 انسخ هذا الـ ID وضعه في متغير BIN_ID أعلى الملف.")
    return new_bin_id


# ══════════════════════════════════════════════
#  اختبار سريع (شغّله مباشرةً للتحقق)
# ══════════════════════════════════════════════
if __name__ == "__main__":
    print("🔍 جاري اختبار الاتصال بـ JSONBin...")
    try:
        data = fetch_data()
        print(f"✅ تم جلب البيانات بنجاح!")
        print(f"   👤 المستخدم : {data['profile']['name']}")
        print(f"   ⭐ إجمالي XP: {data['profile']['total_xp']}")
        print(f"   📋 عدد العادات: {len(data['habits'])}")
        print(f"   📅 عدد أيام السجل: {len(data['daily_log'])}")
    except RuntimeError as e:
        print(e)
