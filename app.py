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

# دالة مخصصة ومعزولة لمنع تعليق السيرفر نهائياً وتأمين الطلب
def get_critic_response(api_key, prompt_text, context):
    try:
        # تهيئة العميل داخل الدالة لضمان استقرار الاتصال
        client = genai.Client(api_key=api_key)
        
        full_prompt = f"""
        أنت خبير ناقد أكاديمي متخصص في الأدب العربي.
        السياق أو المرجع المتاح: {context if context else 'اعتمد على معارفك الأدبية العامة.'}
        المطلوب منك: قم بتحليل ونقد النص التالي نقداً أدبياً وبلاغياً وافياً: {prompt_text}
        """
        
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بالخادم: {e}"

if GEMINI_API_KEY:
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

    # 5. معالجة الطلب الآمن والمباشر
    if st.button("🚀 ابدأ التحليل والنقد الفوري"):
        if not user_prompt:
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
        else:
            with st.spinner("جاري استرجاع البيانات وتحليلها عبر الذكاء الاصطناعي..."):
                # استدعاء الدالة الآمنة المعزولة
                result = get_critic_response(GEMINI_API_KEY, user_prompt, context_content)
                
                st.write("---")
                st.markdown("### ✨ النتيجة والنقد المستخرج:")
                st.write(result)
else:
    st.info("💡 للبدء، يرجى إدخال مفتاح Gemini API في القائمة الجانبية أو ضبطه كمتغير بيئي (Environment Variable).")
