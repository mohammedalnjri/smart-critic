import os
import streamlit as st
from google import genai

# مكتبات معالجة اللغة العربية والـ PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

# =====================================================================
# 1. دالة معالجة النصوص العربية وتحويلها إلى PDF منسق
# =====================================================================
def export_to_arabic_pdf(text_content):
    import io
    buffer = io.BytesIO()
    
    # إنشاء صفحة PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # تسجيل خط الأميري الأكاديمي إذا كان مرفوعاً، أو استخدام الخط الافتراضي كبديل آمن
    try:
        pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
        font_name = 'Amiri'
    except:
        font_name = 'Helvetica' # بديل افترافي في حال عدم توفر ملف الخط
        
    c.setFont(font_name, 14)
    
    # تقسيم النص إلى أسطر للكتابة داخل الصفحة
    lines = text_content.split('\n')
    y_position = height - 50 # نقطة البداية من أعلى الصفحة
    
    for line in lines:
        if y_position < 50: # إنشاء صفحة جديدة إذا امتلأت الحالية
            c.showPage()
            c.setFont(font_name, 14)
            y_position = height - 50
            
        if line.strip():
            # إعادة تشكيل الحروف العربية وقلب الاتجاه لتظهر صحيحة من اليمين لليسار
            reshaped_text = arabic_reshaper.reshape(line)
            bidi_text = get_display(reshaped_text)
            
            # الكتابة محاذاة إلى اليمين (RTL)
            c.drawRightString(width - 50, y_position, bidi_text)
        y_position -= 25 # الانتقال للسطر التالي
        
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
    page_title="نظام الناقد الذكي الفائق لنقد وتحليل الشعر",
    layout="wide"
)

# حقن كود التحقق والـ Analytics بشكل آمن خلفي ومستقر
st.markdown('<p style="display:none;"><meta name="google-site-verification" content="I2lRbvk9y_t28q_uNFz0ITo4q0GEs-PdkxBr69zLBSA" /></p>', unsafe_allow_html=True)

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

# استخدام الـ Session State لحفظ النتيجة بأمان لمنع اختفائها
if "analysis_output" not in st.session_state:
    st.session_state.analysis_output = ""

if st.button("🚀 ابدأ التحليل الشامل والعميق للقصيدة بالكامل"):
    st.subheader("🧠 الشرح الأكاديمي والتحليل البلاغي والعروضي المفصل")
    
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ نظام الحماية السري قيد الإعداد على السيرفر، يرجى وضع المفتاح في لوحة التحكم.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            prompt = get_poetry_analysis_prompt(poem_input)
            
            with st.spinner("جاري قراءة القصيدة وتحليلها بسرعة..."):
                response = client.models.generate_content(
                    model='gemini-3.8-flash',



                    contents=prompt,
                )
                st.session_state.analysis_output = response.text
                
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء الاتصال : {str(e)}")

# عرض النتائج وأدوات التقرير المطورة في حال وجود تحليل مخزن
if st.session_state.analysis_output:
    st.markdown(st.session_state.analysis_output)
    st.divider()
    
    # عزل أدوات التقرير لمنع إعادة معالجة النصوص وحفظ الأداء الخارق للتطبيق
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
            # زر تحميل الـ PDF الاحترافي الجديد والداعم للغة العربية
            pdf_data = export_to_arabic_pdf(st.session_state.analysis_output)
            st.download_button(
                label="📄 تحميل التقرير كملف PDF أكاديمي",
                data=pdf_data,
                file_name="تحليل_القصيدة.pdf",
                mime="application/pdf"
            )
        
        with col3:
            st.info("💡 يمكنك نسخ النص بالكامل مباشرة عبر أيقونة النسخ.")
            st.text_area("نص التحليل القابل للنسخ السريع:", value=st.session_state.analysis_output, height=100)
            
    report_tools()

st.divider()
st.write("صُنع بكفاءه برمجيه عاليه لخدمة الشعراء والنقاد بواسطة المبرمج محمد النجري 💻")
