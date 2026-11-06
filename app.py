import os
import streamlit as st
from google import genai

# =====================================================================
# 1. دالة التحليل الذكي الموحدة - النسخة السريعة والمركزة
# =====================================================================
def get_poetry_analysis_prompt(poem_text):
    return f"""
    قم بتحليل القصيدة التالية سريعاً ومباشرة دون مقدمات طويلة:
    
    القصيدة:
    {poem_text}
    
    المطلوب باختصار مركز ومباشر:
    1. بحر القصيدة العروضي والقافية بدقة.
    2. شرح الأبيات بأسلوب أدبي موجز ومباشر.
    3. أهم الصور البلاغية والمحسنات البديعية بوضوح.
    """

# =====================================================================
# 2. واجهة المستخدم الرسومية المستقرة والنظيفة والتصديق في قوقل
# =====================================================================
# وضعت لك الرمز السري هنا مباشرة في عنوان المتصفح ليقرأه قوقل فوراً قبل تحميل السيرفر
st.set_page_config(
    page_title="نظام الناقد الذكي الفائق - google-site-verification=I2lRbvk9y_t28q_uNFz0ITo4q0GEs-PdkxBr69zLBSA ",
    layout="wide"
)

# طريقة بديلة لحقن الرمز داخل جسم الصفحة الخارجي
st.html('<meta name="google-site-verification" content="I2lRbvk9y_t28q_uNFz0ITo4q0GEs-PdkxBr69zLBSA" />')


st.title("✒️ نظام الناقد الذكي لتحليل وشرح القصائد")
st.write("### فكرة وتطوير المبرمج محمد النجري ✨")

with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    st.success("🔒 النظام متصل ومحمي تلقائياً بالسيرفر السحابي الآمن والسريع.")
    st.divider()
    st.markdown("### 👨‍💻 مطوّر النظام")
    st.info("تمت البرمجة والتطوير بواسطة: المبرمج محمد النِجْري")

st.subheader("📋 اكتب أو الصق القصيدة الكاملة هنا")
default_poem = "عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"

poem_input = st.text_area("أدخل أبيات القصيدة (كل بيت في سطر منفصل):", value=default_poem, height=250)

if st.button("🚀 ابدأ التحليل الشامل والعميق للقصيدة بالكامل"):
    st.subheader("🧠 الشرح الأكاديمي والتحليل البلاغي والعروضي المفصل")
    
    # جلب مفتاح التشغيل السري من الخلفية
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ نظام الحماية السري قيد الإعداد على السيرفر، يرجى وضع المفتاح في لوحة التحكم.")
    else:
        try:
            # تهيئة عميل جوجل بالربط المباشر
            client = genai.Client(api_key=api_key)
            prompt = get_poetry_analysis_prompt(poem_input)
            
            with st.spinner("جاري قراءة القصيدة وتحليلها بسرعة..."):
                response = client.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=prompt,
                )
                
                analysis_result = response.text
                st.markdown(analysis_result)
                st.divider()
                
                # أدوات التقرير المساعدة للمستخدم
                st.subheader("🛠️ أدوات التقرير")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 تحميل التقرير كملف نصي (TXT)",
                        data=analysis_result,
                        file_name="تحليل_القصيدة.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    st.info("💡 يمكنك نسخ النص بالكامل مباشرة عبر الضغط على أيقونة النسخ التي تظهر أعلى زاوية مربع النص التالي:")
                    st.text_area("نص التحليل القابل للنسخ السريع:", value=analysis_result, height=150)
                
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء الاتصال : {str(e)}")

st.divider()
st.write("صُنع بكفاءه برمجيه عاليه لخدمة الشعراء والنقاد بواسطة المبرمج محمد النجري 💻")

# =====================================================================
# 3. كود السماح لقوقل بقراءة ملف التحقق الساكن (HTML Verification)
# =====================================================================
google_file_name = "google8cb1e8b8085e0afc.html"

if os.path.exists(google_file_name):
    with open(google_file_name, "r") as f:
        html_content = f.read()
    st.markdown(f'<div style="display:none;">{html_content}</div>', unsafe_allow_html=True)

