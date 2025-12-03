# -*- coding: utf-8 -*-
"""SmartWaste Streamlit app.

تطبيق توعوي حول إعادة تدوير النفايات الخطرة (بما فيها المواد الملوّثة بالفيروسات)
مع دمج مساعد Gemini كتشاتبوت ذكي.
"""

import os
from typing import List, Tuple

import google.generativeai as genai
import streamlit as st


# =========================
#   إعدادات Gemini
# =========================
ENV_GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()


def resolve_api_key() -> str:
    """Resolve the API key from session state or environment."""

    session_key = st.session_state.get("gemini_api_key", "").strip()
    return session_key or ENV_GEMINI_API_KEY


def configure_gemini(api_key: str):
    """Configure the Gemini client if an API key is provided."""

    if not api_key:
        return (
            None,
            False,
            "❌ لم يتم العثور على مفتاح API. يمكنك لصقه في الشريط الجانبي أو ضبط متغير البيئة GEMINI_API_KEY.",
        )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model, True, ""
    except Exception as exc:  # pragma: no cover - relies on external service
        return None, False, str(exc)


def sync_gemini_state(force_refresh: bool = False):
    """Ensure Gemini configuration is available in the current session."""

    needs_refresh = force_refresh or "gemini_model" not in st.session_state
    if not needs_refresh:
        return

    model, configured, error = configure_gemini(resolve_api_key())
    st.session_state["gemini_model"] = model
    st.session_state["gemini_configured"] = configured
    st.session_state["gemini_error"] = error


sync_gemini_state()


# =========================
#   إعداد الصفحة
# =========================
st.set_page_config(page_title="SmartWaste", page_icon="♻️", layout="wide")

# =========================
#   التصميم
# =========================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #d0d0d0;
        margin-bottom: 2rem;
    }
    .hero {
        border-radius: 20px;
        padding: 2rem;
        background: linear-gradient(135deg, #1b5e20, #004d40);
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .section-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #00c853;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .card {
        background: #0f1f16;
        border: 1px solid #1c5137;
        padding: 1rem;
        border-radius: 12px;
        height: 100%;
    }
    .metric-box {
        background: #0f1f16;
        border-radius: 14px;
        padding: 1.1rem;
        border: 1px solid #1c5137;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
#   المساعدة على التنقل
# =========================
st.sidebar.title("♻️ SmartWaste")
page = st.sidebar.radio(
    "اختر صفحة:",
    ["الصفحة الرئيسية", "تشاتبوت إعادة التدوير", "دليل السلامة"],
)

st.sidebar.subheader("🔐 إعدادات اتصال Gemini")
st.sidebar.text_input(
    "مفتاح API (لن يُحفظ)",
    key="gemini_api_key",
    type="password",
    help="أدخل مفتاحك ثم اضغط تحديث لتفعيل الاتصال أثناء الجلسة.",
    placeholder="قم بلصق مفتاح Gemini هنا",
)
if st.sidebar.button("تحديث الاتصال"):
    sync_gemini_state(force_refresh=True)
    if st.session_state.get("gemini_configured"):
        st.sidebar.success("تم تفعيل Gemini لهذه الجلسة.")
    else:
        st.sidebar.error("ما زال الاتصال غير مفعّل. تحقق من المفتاح أو الشبكة.")


# =========================
#   مكونات مساعدة
# =========================
def render_metrics():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("نسبة خفض العدوى الممكنة", "85%", "+ سلامة")
    with col2:
        st.metric("وقت التعقيم", "15 دقيقة", "متوسط")
    with col3:
        st.metric("مواد معاد تدويرها", "12 طن/سنوياً", "تقديري")


def render_resource_cards():
    cards: List[Tuple[str, str]] = [
        (
            "💉 التخلص من النفايات الحيوية",
            "تعقيم المواد الملوّثة بالفيروسات بالبخار المضغوط قبل النقل إلى محارق آمنة.",
        ),
        (
            "🧪 فرز المواد الكيميائية",
            "إبقاء المواد الحادة والمحاليل المفصولة في حاويات صلبة محكمة الغلق بعلامات واضحة.",
        ),
        (
            "♻️ إعادة التدوير الآمن",
            "بلاستيك وأدوات المختبر غير الملوّثة يمكن غسلها وتعقيمها وإعادة تدويرها ضمن مسار منفصل.",
        ),
    ]

    cols = st.columns(len(cards))
    for col, (title, body) in zip(cols, cards):
        with col:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader(title)
            st.write(body)
            st.markdown("</div>", unsafe_allow_html=True)


def render_checklist():
    st.markdown('<div class="section-title">✅ قائمة فحص سريعة</div>', unsafe_allow_html=True)
    tasks = [
        "ارتداء قفازات وكمامة قبل التعامل مع النفايات.",
        "عزل الأدوات الملوّثة في أكياس حمراء مزدوجة السُمك.",
        "التأكد من إغلاق الحاويات بإحكام قبل النقل.",
        "تسجيل مصدر النفايات وتاريخ التعقيم.",
    ]
    for item in tasks:
        st.checkbox(item)


def render_home():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">مرحبًا بك في SmartWaste</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">تطبيق ذكي يركّز على إدارة وإعادة تدوير النفايات الملوّثة بالفيروسات بطرق آمنة ومستدامة.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    render_metrics()
    st.markdown('<div class="section-title">📘 مصادر سريعة</div>', unsafe_allow_html=True)
    render_resource_cards()
    render_checklist()


# =========================
#   صفحة التشاتبوت
# =========================
def render_chatbot():
    st.markdown('<div class="section-title">💬 تشاتبوت إعادة التدوير</div>', unsafe_allow_html=True)

    sync_gemini_state()

    if not st.session_state.get("gemini_configured"):
        st.error("❌ Gemini غير مفعّل.")
        st.code(st.session_state.get("gemini_error", ""))
        st.info("أدخل مفتاحك في الشريط الجانبي ثم اضغط تحديث الاتصال أو اضبط متغير البيئة GEMINI_API_KEY.")
        return

    st.write("استعن بالمساعد لاقتراح خطوات آمنة للتخلص أو إعادة التدوير.")

    presets = [
        "كيف أعقم أدوات مختبر ملوّثة بفيروس قبل التخلص منها؟",
        "خطة إدارة نفايات لمركز صحي صغير.",
        "مواد يمكن إعادة تدويرها بعد التعقيم من نفايات بيولوجية.",
    ]

    st.write("اقتراحات سريعة:")
    preset_cols = st.columns(len(presets))
    for col, text in zip(preset_cols, presets):
        with col:
            if st.button(text):
                st.session_state.user_q = text

    user_question = st.text_area(
        "اكتب سؤالك هنا:",
        key="user_q",
        placeholder="مثال: ما هي أفضل طريقة لنقل عينات ملوّثة بفيروس بأمان؟",
    )

    tone = st.selectbox("النبرة المفضلة للرد", ["مختصرة", "تعليمية", "قائمة خطوات"], index=2)

    if "history" not in st.session_state:
        st.session_state.history = []

    if st.button("إرسال") and user_question.strip():
        prompt = (
            "أنت مساعد ذكي متخصص في إدارة وإعادة تدوير النفايات الملوّثة بالفيروسات.\n"
            "التزم بإجراءات السلامة واللوائح الصحية، وقدّم إرشادات قابلة للتنفيذ.\n"
            f"النبرة المطلوبة: {tone}.\n\n"
            f"سؤال المستخدم: {user_question}"
        )
        try:
            response = st.session_state["gemini_model"].generate_content(prompt)
            answer = response.text
            st.session_state.history.append((user_question, answer))
        except Exception as exc:  # pragma: no cover - relies on external service
            st.error("حدث خطأ أثناء الاتصال بـ Gemini.")
            st.code(str(exc))

    for idx, (question, answer) in enumerate(reversed(st.session_state.history), start=1):
        st.markdown(f"**سؤال {idx}:** {question}")
        st.success("إجابة النموذج:")
        st.write(answer)
        st.divider()


# =========================
#   دليل السلامة
# =========================
def render_guidelines():
    st.markdown('<div class="section-title">🛡️ دليل السلامة</div>', unsafe_allow_html=True)

    st.info(
        "يغطّي هذا الدليل خطوات عملية لإدارة النفايات الملوّثة بالفيروسات في المختبرات والمراكز الصحية."
    )

    with st.expander("تعقيم وتجهيز قبل النقل"):
        st.write(
            "استخدم الأوتوكلاف عند 121° لمدة لا تقل عن 15 دقيقة، وضع ملصقًا يوضح تاريخ التعقيم واسم المشرف."  # noqa: E501
        )
    with st.expander("النقل والتتبع"):
        st.write("انقل الحاويات في صناديق صلبة مضادة للتسرب مع مستند شحن يوضح مصدر النفايات وجهتها.")
    with st.expander("التخزين المؤقت"):
        st.write("احتفِظ بالنفايات المعبأة في مكان بارد وظلّل بعيدًا عن المرور الكثيف وبمدة تخزين لا تتجاوز 48 ساعة.")
    with st.expander("إعادة التدوير/الإتلاف"):
        st.write(
            "بعد التعقيم، يمكن إعادة تدوير المعادن والبلاستيك غير المتحلل ميكروبيًا ضمن مسار منفصل؛ النفايات غير القابلة تُتلف بالحرق أو الطمر الآمن."  # noqa: E501
        )

    st.markdown('<div class="section-title">📋 نماذج جاهزة</div>', unsafe_allow_html=True)
    st.write(
        "نزّل أو انسخ النماذج أدناه لتوثيق مسارات النفايات: سجل استلام، نموذج تعقيم، ونموذج تتبع نقل."
    )
    st.code(
        """
        نموذج سجل استلام:
        - التاريخ | المصدر | نوع النفايات | الكمية | المسؤول

        نموذج تعقيم:
        - التاريخ | الطريقة | المدة | درجة الحرارة | المراقب

        نموذج تتبع نقل:
        - التاريخ | الوجهة | وسيلة النقل | حالة الحاويات | التوقيع
        """
    )


# =========================
#   التوجيه العام
# =========================
if page == "الصفحة الرئيسية":
    render_home()
elif page == "تشاتبوت إعادة التدوير":
    render_chatbot()
elif page == "دليل السلامة":
    render_guidelines()

