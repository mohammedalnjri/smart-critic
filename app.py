import streamlit as st
import os
from google import genai
from google.genai import types

# 1. إعداد الصفحة والواجهة الاحترافية للموقع
st.set_page_config(
    page_title="Smart Critic - الناقد الذكي",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.subheader("تحليل ونقد النصوص والمراجع العربية بالذكاء الاصطناعي")

# 2. إعداد مفتاح API الخاص بـ Gemini
# يفضل وضع المفتاح في شاشة الإعدادات (Secrets) في الاستضافة لحمايته
# يمكنك الحصول عليه مجاناً من Google AI Studio
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # حل مؤقت للمرحلة التجريبية إذا لم تضعه في الإعدادات البيئية
    GEMINI_API_KEY = st.sidebar.text_input("أدخل مفتاح Gemini API المجاني الخاص بك:", type="password")

if GEMINI_API_KEY:
    # تهيئة عميل جوجل المطور الحديث
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 3. قسم رفع المراجع والملفات العربية
    st.write("---")
    st.markdown("### 📚 1. المراجع والنصوص المراد تحليلها")
    uploaded_file = st.file_uploader("ارفع الملف أو المرجع العربي (TXT أو PDF):", type=["txt", "pdf"])
    
    context_content = ""
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            context_content = str(uploaded_file.read(), "utf-8")
            st.success(" تم تحميل النص من المرجع بنجاح!")
        else:
            # هنا يمكن إضافة مكتبة pypdf مستقبلاً لقراءة ملفات PDF المعقدة
            st.warning("تنبيه: لقراءة ملفات PDF الضخمة بكفاءة، يفضل تحويلها إلى نص (TXT) في المرحلة التجريبية الحالية.")
            context_content = str(uploaded_file.read(), "utf-8", errors="ignore")

    # 4. قسم كتابة الأوامر والنقد
    st.write("---")
    st.markdown("### ✍️ 2. توجيهات الناقد الذكي")
    user_prompt = st.text_area(
        "اكتب النص البرومبت (Prompt) أو سؤالك النقدي حول المراجع المرفوعة:",
        placeholder="مثال: قم بنقد هذا النص نقداً أدبياً مفصلاً بناءً على معايير البلاغة العربية..."
    )

    # 5. معالجة الطلب وإرساله إلى Gemini
    if st.button("🚀 ابدأ التحليل والنقد الفوري"):
        if not user_prompt:
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
        else:
            with st.spinner("جاري استرجاع البيانات وتحليلها عبر الذكاء الاصطناعي..."):
                try:
                    # صياغة البرومبت الهندسي للـ RAG لضمان الالتزام بالمراجع المرفوعة
                    full_prompt = f"""
                    أنت خبير ناقد أكاديمي متخصص في الأدب والمراجع العربية. 
                    بناءً على المرجع المرفق أدناه فقط، قم بالإجابة على سؤال المستخدم أو تنفيذ طلبه بكل دقة ومصداقية علمية.
                    
                    [المرجع والسياق المتاح]:
                    {context_content if context_content else 'لم يتم رفع مرجع مخصص، اعتمد على معارفك العربية الموسعة.'}
                    
                    [طلب المستخدم]:
                    {user_prompt}
                    
                    الرد الموائم (اكتب باللغة العربية الفصحى وبأسلوب نقد محترف):
                    """
                    
                    # استدعاء نموذج gemini-2.5-flash السريع والمجاني والممتاز للعربية
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_prompt,
                    )
                    
                    # عرض النتيجة المذهلة للمستخدم
                    st.write("---")
                    st.markdown("### ✨ النتيجة والنقد المستخرج:")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالخادم: {e}")
else:
    st.info("💡 للبدء، يرجى إدخال مفتاح Gemini API في القائمة الجانبية أو ضبطه كمتغير بيئي (Environment Variable).")
