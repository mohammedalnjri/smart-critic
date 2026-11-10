import streamlit as st
import os
from google import genai

# 1. إعداد الصفحة والواجهة الاحترافية للموقع
st.set_page_config(
    page_title="Smart Critic - الناقد الذكي",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.subheader("تحليل ونقد النصوص والمراجع العربية بالذكاء الاصطناعي")

# 2. إعداد مفتاح API الخاص بـ Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("أدخل مفتاح Gemini API المجاني الخاص بك:", type="password")

if GEMINI_API_KEY:
    # تهيئة عميل جوجل الحديث
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 3. قسم رفع المراجع والملفات العربية
    st.write("---")
    st.markdown("### 📚 1. المراجع والنصوص المراد تحليلها")
    uploaded_file = st.file_uploader("ارفع الملف أو المرجع العربي (TXT أو PDF):", type=["txt", "pdf"])
    
    context_content = ""
    if uploaded_file is not None:
        try:
            context_content = uploaded_file.read().decode("utf-8", errors="ignore")
            st.success("تم تحميل المرجع بنجاح!")
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")

    # 4. قسم كتابة الأوامر والنقد (مع تثبيت البيت الشعري بالتشكيل الكامل)
    st.write("---")
    st.markdown("### ✍️ 2. توجيهات الناقد الذكي")
    user_prompt = st.text_area(
        "اكتب النص البرومبت (Prompt) أو سؤالك النقدي حول المراجع المرفوعة:",
        value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"
    )

    # 5. معالجة الطلب وإرساله إلى النموذج المحدث
    if st.button("🚀 ابدأ التحليل والنقد الفوري"):
        if not user_prompt:
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
        else:
            with st.spinner("جاري استرجاع البيانات وتحليلها عبر الذكاء الاصطناعي..."):
                try:
                    # صياغة الطلب بشكل مبسط ومباشر لضمان السرعة القصوى
                    full_prompt = f"""
                    أنت خبير ناقد أكاديمي متخصص في الأدب العربي.
                    السياق أو المرجع المتاح: {context_content if context_content else 'اعتمد على معارفك الأدبية العامة.'}
                    المطلوب منك: قم بتحليل ونقد النص التالي نقداً أدبياً وبلاغياً وافياً: {user_prompt}
                    """
                    
                    # تم استخدام اسم النموذج المحدث والمفتوح رسمياً لتلافي خطأ الـ 404 تماماً
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_prompt,
                    )
                    
                    st.write("---")
                    st.markdown("### ✨ النتيجة والنقد المستخرج:")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالخادم: {e}")
else:
    st.info("💡 للبدء، يرجى إدخال مفتاح Gemini API في القائمة الجانبية أو ضبطه كمتغير بيئي (Environment Variable).")
