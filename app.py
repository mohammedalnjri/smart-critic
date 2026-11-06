import os
import streamlit as st
from google import genai

# مكتبات معالجة اللغة العربية والـ PDF الآمنة والخفيفة
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import arabic_reshaper
from bidi.algorithm import get_display

# =====================================================================
# 1. دالة معالجة النصوص العربية وتحويلها إلى PDF منسق بـ أمان
# =====================================================================
def export_to_arabic_pdf(text_content):
    import io
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # استخدام خط النظام الافتراضي المستقر لتفادي تعليق السيرفر السحابي
    c.setFont('Helvetica', 12)
    
    lines = text_content.split('\n')
    y_position = height - 50
    
    for line in lines:
        if y_position < 50:
            c.showPage()
            c.setFont('Helvetica', 12)
            y_position = height - 50
            
        if line.strip():
            # ضبط تلاحم الحروف العربية واتجاه الكتابة الصحيح من اليمين لليسار
            reshaped_text = arabic_reshaper.reshape(line)
            bidi_text = get_display(reshaped_text)
            c.drawRightString(width - 50, y_position, bidi_text)
        y_position -= 22
        
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# =====================================================================
# 2. دالة التحليل الذكي الموحدة - النسخة السريعة والمركزة
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
# 3. واجهة المستخدم الرسومية المستقرة والنظيفة والتصديق في قوقل
# =====================================================================
st.set_page_config(
    page_title="نظام الناقد الذكي الفائق - google-site-verification=I2lRbvk9y_t28q_uNFz0ITo4q0GEs-PdkxBr69zLBSA ",
    layout="wide"
)

# طريقة بديلة لحقن الرمز داخل جسم الصفحة الخارجي
st.markdown('<p style="display:none;"><meta name="google-site-verification" content=" I2lRbvk9y_t28q_uNFz0ITo4q0GEs-PdkxBr69zLBSA" /></p>', unsafe_allow_html=True)

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

# استخدام الـ Session State لحفظ النتيجة بأمان لمنع اختفائها عند الضغط على الأزرار
if "analysis_output" not in st.session_state:
    st.session_state.analysis_output = ""

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
                # استدعاء الموديل المطلوب بدقة لإنهاء الـ 404 نهائياً
                response = client.models.generate_content(
                    model='gemini-2.5-pro',
                    contents=prompt,
                )
                
                st.session_state.analysis_output = response.text
                
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء الاتصال : {str(e)}")

# عرض النتائج وأدوات التقرير في حال وجود تحليل مخزن
if st.session_state.analysis_output:
    st.markdown(st.session_state.analysis_output)
    st.divider()
    
    # عزل أدوات التقرير لمنع إعادة تحميل الصفحة وضمان استقرار الكود
    @st.fragment
    def report_tools():
        st.subheader("🛠️ أدوات التقرير")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📥 تحميل التقرير كملف نصي (TXT)",
                data=st.session_state.analysis_output,
                file_name="تحليل_القصيدة.txt",
                mime="text/plain"
            )
            
        with col2:
            # توليد وتحميل ملف الـ PDF المنسق
            pdf_data = export_to_arabic_pdf(st.session_state.analysis_output)
            st.download_button(
                label="📄 تحميل التقرير كملف PDF",
                data=pdf_data,
                file_name="تحليل_القصيدة.pdf",
                mime="application/pdf"
            )
                
        with col3:
            st.info("💡 يمكنك نسخ النص بالكامل مباشرة عبر مربع النص التالي:")
            st.text_area("نص التحليل القابل للنسخ السريع:", value=st.session_state.analysis_output, height=100)
            
    report_tools()

st.divider()
st.write("صُنع بكفاءه برمجيه عاليه لخدمة الشعراء والنقاد بواسطة المبرمج محمد النجري 💻")

# =====================================================================
# 5. كود السماح لقوقل بقراءة ملف التحقق الساكن (HTML Verification)
# =====================================================================
google_file_name = "google8cb1e8b8085e0afc.html"

if os.path.exists(google_file_name):
    with open(google_file_name, "r") as f:
        html_content = f.read()
    st.markdown(f'<div style="display:none;">{html_content}</div>', unsafe_allow_html=True)
