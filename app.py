import streamlit as st
import os
import re
import time
import textwrap
import pandas as pd
from google import genai
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(
    page_title="Smart Critic - الناقد الذكي",
    page_icon="📚",
    layout="centered"
)

st.markdown("""
<style>
    .stMarkdown, .stTextArea, .stAlert, .stDataFrame {
        direction: rtl;
        text-align: right;
    }
    [data-testid="collapsedControl"] {
        display: none;
    }
    div.stButton > button {
        background-color: #1E6BE6 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    div.stButton > button:hover {
        background-color: #1554B8 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.markdown("<p style='font-size: 1.2rem; color: #4A90E2; font-weight: bold; margin-top: -15px;'>🎨 تصميم المبرمج محمد النجري</p>", unsafe_allow_html=True)
st.subheader("التحليل الأدبي والعروضي الصارم بأحدث التقنيات البرمجية")

# ==========================================
# دالة إنشاء ملف PDF عربي منسق مع تذييل تلقائي
# ==========================================
class StyledPDF(FPDF):
    def header(self):
        self.set_fill_color(250, 248, 244)
        self.rect(0, 0, 210, 297, 'F')

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(180, 150, 90)
        self.line(12, 280, 198, 280)
        self.set_font("Almarai", "B", size=10)
        self.set_text_color(20, 90, 200)
        self.set_x(12)
        self.cell(
            186,
            8,
            f"المدونة الأدبية للمبرمج محمد النجري: alnjrimohammed.blogspot.com  |  صفحة {self.page_no()}",
            align='C',
            link="https://alnjrimohammed.blogspot.com/"
        )

def print_rtl_paragraph(pdf, text, line_height=8.5, max_chars=75, align='R'):
    for paragraph in text.split('\n'):
        if set(paragraph.strip()) <= {'|', '-', ':', ' '}:
            continue
        clean_para = paragraph.replace('**', '').replace('###', '').replace('|', ' - ').strip(' -')
        if not clean_para:
            continue
        lines = textwrap.wrap(clean_para, width=max_chars)
        for line in lines:
            pdf.set_x(12)
            pdf.cell(186, line_height, line, ln=True, align=align)

def create_arabic_pdf(report_text, poem_text=""):
    pdf = StyledPDF()
    pdf.set_margins(12, 12, 12)
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.add_font("Almarai", "", "Almarai-Regular.ttf")
    pdf.add_font("Almarai", "B", "Almarai-Bold.ttf")
    pdf.add_font("AlmaraiExtra", "B", "Almarai-ExtraBold.ttf")
    pdf.add_page()
    pdf.set_text_shaping(True)

    # 1. العنوان الرئيسي
    pdf.set_font("AlmaraiExtra", "B", size=21)
    pdf.set_text_color(10, 45, 110)
    print_rtl_paragraph(pdf, "منصة الناقد الذكي للتحليل الأدبي والعروضي", line_height=12, max_chars=45, align='C')

    # 2. اسم المبرمج
    pdf.set_font("AlmaraiExtra", "B", size=14)
    pdf.set_text_color(130, 80, 10)
    print_rtl_paragraph(pdf, "تصميم وتطوير المبرمج: محمد النجري", line_height=10, max_chars=55, align='C')
    pdf.ln(5)

    # 3. الأبيات الشعرية بالخط العريض واللون الأزرق الملكي
    if poem_text.strip():
        pdf.set_font("AlmaraiExtra", "B", size=13)
        pdf.set_text_color(10, 55, 130)
        clean_poem = re.sub(r'[\u064B-\u065F\u0670]', '', poem_text)
        print_rtl_paragraph(pdf, clean_poem, line_height=9.5, max_chars=75, align='R')
        pdf.ln(4)

    # 4. نص التقرير التحليلي
    pdf.set_font("Almarai", "B", size=12)
    pdf.set_text_color(10, 10, 10)
    clean_report = re.sub(r'[\u064B-\u065F\u0670]', '', report_text)
    print_rtl_paragraph(pdf, clean_report, line_height=8.5, max_chars=75, align='R')
    return bytes(pdf.output())

# ==========================================
# محرك التحليل العروضي الشامل لجميع البحور
# ==========================================
def line_to_prosody_symbols(line, is_fusha=True):
    text = line.strip().replace("ـ", "").replace('آ', 'أَا')
    chars = list(text)
    expanded = []
    for ch in chars:
        if ch == '\u0651' and expanded:
            prev_letter = expanded[-1]
            expanded.append('\u0652')
            expanded.append(prev_letter)
        else:
            expanded.append(ch)
    
    text = "".join(expanded)
    text = re.sub(r'(?<=\S)\s+ال', ' لْ', text)
    text = re.sub(r'^ال', 'اَلْ', text)
    
    symbols = ""
    vowels = {'\u064E', '\u064F', '\u0650'}
    tanween = {'\u064B', '\u064C', '\u064D'}
    sukun = '\u0652'
    long_vowels = {'ا', 'و', 'ي', 'ى'}
    
    i = 0
    while i < len(text):
        ch = text[i]
        if '\u0621' <= ch <= '\u064A':
            nxt = text[i + 1] if i + 1 < len(text) else ''
            if nxt in vowels:
                symbols += '/'
                i += 2
                continue
            elif nxt in tanween:
                symbols += '/0'
                i += 2
                continue
            elif nxt == sukun:
                symbols += '0'
                i += 2
                continue
            elif ch in long_vowels and symbols.endswith('/'):
                symbols += '0'
                i += 1
                continue
            else:
                if i == len(text) - 1:
                    symbols += '0'
                else:
                    symbols += '/'
        i += 1
    if is_fusha and symbols.endswith('/'):
        symbols += '0'
    return symbols

METERS_SIGNATURES = [
    ("الكامل التام", "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ", r"^(///0//0|/0/0//0|//0//0|////0|//0///0|///0//00|/0/0//00){1,3}(///0//0|/0/0//0|//0//0|///0//|/0/0//|///0/0|/0/0/0|///0|/0/0|///0//00|/0/0//00|///0//0/0|/0/0//0/0)?$"),
    ("الوافر التام", "مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُنْ", r"^(//0///0|//0/0/0|//0//0){2}(//0/0|//00|/0)$"),
    ("الطويل", "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ", r"^(//0/0|//0/)(//0/0/0|//0//0)(//0/0|//0/)(//0//0|//0/0/0|//0/0|//0/00)$"),
    ("البسيط التام", "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُنْ", r"^(/0/0//0|//0//0|/0///0)(/0//0|///0|/0/0)(/0/0//0|//0//0|/0///0)(///0|/0/0|/0//0|///00|/0/00)$"),
    ("السريع / الصخري", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ", r"^(/0/0//0|//0//0|/0///0){2}(/0//0|/0/0|///0|/0//00|/0/00|/0)$"),
    ("الرجز التام", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ", r"^(/0/0//0|//0//0|/0///0|////0){2}(/0/0//0|//0//0|/0///0|/0/0/0|/0/0//00)$"),
    ("الرمل", "فَاعِلَاتُنْ فَاعِلَاتُنْ فَاعِلَاتُنْ", r"^(/0//0/0|//0/0/0|/0//0|//0/0){2}(/0//0/0|//0/0/0|/0//0|//0/0|/0//00)$"),
    ("الخفيف", "فَاعِلَاتُنْ مُسْتَفْعِلُنْ فَاعِلَاتُنْ", r"^(/0//0/0|//0/0/0|/0//0)(/0/0//0|//0//0|/0///0)(/0//0/0|//0/0/0|/0//0|/0/0)$"),
    ("المتقارب", "فَعُولُنْ فَعُولُنْ فَعُولُنْ فَعُولُنْ", r"^(//0/0|//0){3}(//0/0|//0|//00|/0)$")
]

def classify_symbols(sym):
    if not sym:
        return ("غير محدد", "")
    for name, tafeelat, pattern in METERS_SIGNATURES:
        if re.match(pattern, sym):
            return (name, tafeelat)
    if ("///0//0" in sym or sym.count("/0/0//0") >= 2) and len(sym) >= 15:
        return ("الكامل التام", "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ")
    if "//0///0" in sym:
        return ("الوافر التام", "مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُنْ")
    return ("يُطابق مع البحر السائد", "تفعيلات قياسية")

def detect_arabic_meter_and_table(raw_text, is_fusha=True):
    clean_kashida = raw_text.replace("ـ", "")
    raw_lines = [l.strip() for l in clean_kashida.strip().split('\n') if l.strip()]
    if not raw_lines:
        return "", pd.DataFrame()
        
    ashatar = []
    for line in raw_lines:
        if '=' in line:
            ashatar.extend([p.strip() for p in line.split('=') if p.strip()])
        elif '***' in line:
            ashatar.extend([p.strip() for p in line.split('***') if p.strip()])
        else:
            ashatar.append(line)
            
    rows = []
    votes = {}
    for idx, shatr in enumerate(ashatar):
        sym = line_to_prosody_symbols(shatr, is_fusha=is_fusha)
        meter_name, tafeelat = classify_symbols(sym)
        if "يُطابق" not in meter_name and "غير محدد" not in meter_name:
            votes[meter_name] = votes.get(meter_name, 0) + 1
        rows.append({"م": idx + 1, "الشطر": shatr, "الرموز العروضية": sym, "البحر": meter_name, "التفعيلات": tafeelat})
        
    best_meter = max(votes, key=votes.get) if votes else "الكامل التام"
    best_tafeelat = next((taf for name, taf, _ in METERS_SIGNATURES if name == best_meter), "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ")

    # وراثة البحر السائد للأشطر غير المحسومة بسبب نقص التشكيل
    for r in rows:
        if "يُطابق" in r["البحر"] or "غير محدد" in r["البحر"]:
            r["البحر"] = f"{best_meter} (موزون)"
            r["التفعيلات"] = best_tafeelat

    df = pd.DataFrame(rows)
    sample_syms = "\n".join([f"- الشطر ({r['م']}): {r['الشطر']} -> الرموز: {r['الرموز العروضية']} ({r['البحر']})" for r in rows[:6]])
    
    report_str = (
        f"البحر الشعري للقصيدة هو: **بحر {best_meter}**\n"
        f"- التفعيلات القياسية: **{best_tafeelat}**\n"
        f"- عينة التقطيع الصوتي الفعلي:\n{sample_syms}\n"
        f"- قواعد صارمة: التزم بتفعيلات بحر ({best_meter}) وجوازاته بدقة تامة."
    )
    return report_str, df

# ==========================================
# واجهة التطبيق الرئيسية (مع حماية الحصة اليومية)
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

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

    st.write("---")
    st.markdown("### ✍️ 2. توجيهات الناقد الذكي")
    poem_style = st.radio("اختر نمط القصيدة:", ["شعر فصيح (عمودي)", "شعر شعبي / نبطي / يمني"], horizontal=True)
    user_prompt = st.text_area(
        "💡 أدخل البيت الشعري في سطرين متتاليين (الصدر ثم العجز)، أو الصق قصيدتك كاملة في المربع أدناه:",
        value="فَتَاةٌ مَاس جِيـــدٌ كالغَزَال\nرَنَت وتَربَّعت عَرش الدَّلَال"
    )

    if st.button("🚀 ابدأ النقد الأدبي والعروضي الموثق", use_container_width=True):
        clean_input = user_prompt.strip()
        if not clean_input:
            st.error("الرجاء كتابة النص الشعري أولاً!")
        else:
            is_fusha = (poem_style == "شعر فصيح (عمودي)")
            meter_guidance, scansion_df = detect_arabic_meter_and_table(clean_input, is_fusha)
            st.session_state["scansion_df"] = scansion_df

            cache_key = f"{poem_style}::{clean_input}"
            if st.session_state.get("last_cache_key") == cache_key and st.session_state.get("saved_report"):
                st.info("⚡ تم استرجاع التقرير المحفوظ لهذا النص دون استهلاك رصيد إضافي.")
            else:
                lines_list = [l.strip() for l in clean_input.split('\n') if l.strip()]
                if len(lines_list) == 2:
                    poem_sample = f"بيت شعري واحد مكون من شطرين:\n- الصدر (الشطر الأول): {lines_list[0]}\n- العجز (الشطر الثاني): {lines_list[1]}"
                else:
                    poem_sample = "\n".join(lines_list)

                full_prompt = f"""أنت عالم عروض وناقد أدبي عربي خبير في منصة "الناقد الذكي".
بيانات الضبط العروضي الأولية:
{meter_guidance}

قواعد عروضية صارمة (ممنوع مخالفتها):
1. انتبه لعدد الأبيات: كل شطرين (صدر وعجز) يمثلان بيتاً شعرياً واحداً فقط.
2. التزم بالبحر المكتشف والتحليل العروضي الصحيح بدقة.
3. لا تستخدم جداول markdown.

النص الشعري المراد تحليله:
{poem_sample}

مراجع إضافية:
{context_content[:2000]}

قدّم التقرير في 4 أقسام منظمة:
### أولاً: التوثيق التاريخي والأدبي
### ثانياً: الشرح اللغوي والدلالي
### ثالثاً: التحليل العروضي والإيقاع الموسيقي (الكتابة العروضية، التفعيلات، البحر، القافية والروي)
### رابعاً: التحليل البلاغي والجمالي
"""

                with st.spinner("🔄 جاري استخراج التحليل الأكاديمي والعروضي الموثق..."):
                    final_report = ""
                    last_error = ""
                    free_fast_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]

                    for model_name in free_fast_models:
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=full_prompt
                            )
                            if response and response.text:
                                final_report = response.text
                                break
                        except Exception as e:
                            last_error = str(e)
                            if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                                break
                            continue

                    if final_report:
                        st.session_state["saved_report"] = final_report
                        st.session_state["saved_poem"] = clean_input
                        st.session_state["last_cache_key"] = cache_key
                    else:
                        if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                            st.warning("⚠️ تم استهلاك الحد اليومي المجاني لمفتاح API الحالي. يرجى المحاولة لاحقاً أو تحديث المفتاح.")
                        else:
                            st.warning("⏳ خوادم جوجل تشهد ضغطاً لحظياً، يرجى الضغط على الزر مرة أخرى بعد قليل.")
                        st.caption(f"التفاصيل التقنية: {last_error}")

    if "saved_report" in st.session_state and st.session_state["saved_report"]:
        st.write("---")
        st.markdown("### ✨ تقرير الناقد الأكاديمي والعروضي المتكامل:")
        st.markdown(st.session_state["saved_report"])

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 تحميل نصي (TXT)", st.session_state["saved_report"], "Smart_Critic_Report.txt", use_container_width=True)
        with col2:
            try:
                pdf_bytes = create_arabic_pdf(st.session_state["saved_report"], st.session_state.get("saved_poem", ""))
                st.download_button("📄 تحميل كتابي (PDF)", pdf_bytes, "Smart_Critic_Report.pdf", "application/pdf", use_container_width=True)
            except Exception as pdf_err:
                st.caption(f"تعذر تجهيز PDF: {pdf_err}")

    if "scansion_df" in st.session_state and not st.session_state["scansion_df"].empty:
        st.write("---")
        st.markdown("### 📊 جدول التقطيع العروضي التفصيلي لجميع الأشطر")
        st.dataframe(st.session_state["scansion_df"], use_container_width=True, height=350)
        csv_bytes = st.session_state["scansion_df"].to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 تحميل جدول تقطيع الأبيات (Excel / CSV)", csv_bytes, "Prosody_Scansion_Table.csv", "text/csv", use_container_width=True)

else:
    st.info("💡 يرجى إضافة مفتاح GEMINI_API_KEY في إعدادات الـ Secrets الخاصة بالتطبيق.")
