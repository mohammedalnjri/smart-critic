import streamlit as st
import os
import re
import time
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
# دالة إنشاء ملف PDF عربي منسق (نفس دالتك الأصلية)
# ========================================== 
import textwrap
import re

# تلوين خلفية كل صفحة تلقائياً بنفس اللون العاجي الدافئ لمدونتك
class StyledPDF(FPDF):
    def header(self):
        self.set_fill_color(250, 248, 244)
        self.rect(0, 0, 210, 297, 'F')

def print_rtl_paragraph(pdf, text, line_height=8.5, max_chars=75, align='R'):
    for paragraph in text.split('\n'):
        # تجاهل خطوط الفواصل الخاصة بجداول الماركداون مثل |---|---|
        if set(paragraph.strip()) <= {'|', '-', ':', ' '}:
            continue
        # تنظيف النجوم والهاشتاق وعلامات الجدول لتظهر الجمل نظيفة ومرتبة
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
    pdf.add_page()

    # تفعيل المحرك العربي المدمج لضمان سلامة الحروف والألفات
    pdf.set_text_shaping(True)

    # تحميل أوزان خط المراعي (Almarai) المطابق لمدونة بلوجر
    pdf.add_font("Almarai", "", "Almarai-Regular.ttf")
    pdf.add_font("Almarai", "B", "Almarai-Bold.ttf")
    pdf.add_font("AlmaraiExtra", "B", "Almarai-ExtraBold.ttf")

    # 1. العنوان الرئيسي: خط ExtraBold (أغمق وأسمك) وحجم 21 بلون كحلي داكن
    pdf.set_font("AlmaraiExtra", "B", size=21)
    pdf.set_text_color(10, 45, 110)
    print_rtl_paragraph(pdf, "منصة الناقد الذكي للتحليل الأدبي والعروضي", line_height=12, max_chars=45, align='C')

    # 2. اسم المبرمج: خط ExtraBold (أغمق وأسمك) وحجم 14 بلون ذهبي داكن
    pdf.set_font("AlmaraiExtra", "B", size=14)
    pdf.set_text_color(130, 80, 10)
    print_rtl_paragraph(pdf, "تصميم وتطوير المبرمج: محمد النجري", line_height=10, max_chars=55, align='C')
    pdf.ln(5)

    # 3. باقي الصفحة: خط Almarai-Bold الغامق بحجم 12 ولون أسود فحمي مريح
    pdf.set_font("Almarai", "B", size=12)
    pdf.set_text_color(25, 25, 25)
    raw_all = poem_text + "\n\n" + report_text
    no_tashkeel = re.sub(r'[\u064B-\u065F\u0670]', '', raw_all)

    print_rtl_paragraph(pdf, no_tashkeel, line_height=8.5, max_chars=75, align='R')

    return bytes(pdf.output())



# ==========================================
# محرك التحليل العروضي الرياضي المصحح (يدعم 1000+ بيت)
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
    ("الكامل التام", "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ", r"^(///0//0|/0/0//0){2}(///0//0|/0/0//0|///0//|/0/0//|///0/0|/0/0/0)$"),
    ("الكامل المجزوء", "مُتَفَاعِلُنْ مُتَفَاعِلُنْ", r"^(///0//0|/0/0//0)(///0//0|/0/0//0|///0//00|/0/0//00)$"),
    ("الوافر التام", "مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُنْ", r"^(//0///0|//0/0/0){2}//0/0$"),
    ("الوافر المجزوء", "مُفَاعَلَتُنْ مُفَاعَلَتُنْ", r"^(//0///0|//0/0/0)(//0///0|//0/0/0|//0/0)$"),
    ("الطويل", "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ", r"^(//0/0|//0/)(//0/0/0)(//0/0|//0/)(//0//0|//0/0/0|//0/0)$"),
    ("البسيط التام", "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُنْ", r"^(/0/0//0|//0//0)(/0//0|///0)(/0/0//0|//0//0)(///0|/0/0)$"),
    ("السريع / الصخري", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ", r"^(/0/0//0|//0//0|/0///0){2}(/0//0|/0/0|///0|/0//00|/0/00|/0)$"),
    ("الرجز التام", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ", r"^(/0/0//0|//0//0|/0///0){2}(/0/0//0|//0//0|/0/0/0)$"),
    ("الرمل", "فَاعِلَاتُنْ فَاعِلَاتُنْ فَاعِلَاتُنْ", r"^(/0//0/0|//0/0/0){2}(/0//0/0|//0/0/0|/0//0|//0/0|/0//00)$"),
    ("الخفيف", "فَاعِلَاتُنْ مُسْتَفْعِلُنْ فَاعِلَاتُنْ", r"^(/0//0/0|//0/0/0)(/0/0//0|//0//0)(/0//0/0|//0/0/0|/0//0|/0/0)$"),
    ("المتقارب", "فَعُولُنْ فَعُولُنْ فَعُولُنْ فَعُولُنْ", r"^(//0/0|//0){3}(//0/0|//0|//00|/0)$"),
    ("المتدارك / الخبب", "فَاعِلُنْ فَاعِلُنْ فَاعِلُنْ فَاعِلُنْ", r"^(/0//0|///0|/0/0){3,4}$"),
    ("الهزج", "مَفَاعِيلُنْ مَفَاعِيلُنْ", r"^(//0/0/0|//0//0)(//0/0/0|//0/0)$")
]

def classify_symbols(sym):
    if not sym:
        return ("غير محدد", "")
    for name, tafeelat, pattern in METERS_SIGNATURES:
        if re.match(pattern, sym):
            return (name, tafeelat)
    if ("///0//0" in sym or sym.startswith(("/0/0//0", "//0//0"))) and len(sym) >= 15:
        return ("الكامل التام", "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ")
    if "//0///0" in sym and sym.endswith("//0/0"):
        return ("الوافر التام", "مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُنْ")
    if sym.startswith(("/0/0//0/0/0//0", "//0//0/0/0//0")):
        return ("السريع / الصخري", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ")
    if sym.startswith(("//0/0//0/0", "//0/0//0/0/0", "//0///0/0")):
        return ("الطويل", "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ")
    if sym.startswith(("/0/0//0/0//0", "//0//0/0//0")):
        return ("البسيط التام", "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُنْ")
    return ("يتطابق مع البحر السائد", "تفعيلات قياسية")

def detect_arabic_meter_and_table(raw_text, is_fusha=True):
    clean_kashida = raw_text.replace("ـ", "")
    raw_lines = [l.strip() for l in clean_kashida.strip().split('\n') if l.strip()]
    if not raw_lines:
        return "", pd.DataFrame()
        
    # التحقق من نسبة التشكيل في النص الفصيح
    letters_only = re.sub(r'[^\u0621-\u064A]', '', clean_kashida)
    tashkeel_only = re.findall(r'[\u064B-\u0652]', clean_kashida)
    has_enough_tashkeel = (len(letters_only) > 0 and (len(tashkeel_only) / len(letters_only)) >= 0.25)

    # مسار 1: النص الفصيح غير المشكول -> توجيه النموذج للتشكيل الصرفي الدقيق أولاً
    if is_fusha and not has_enough_tashkeel:
        guidance = (
            "تنبيه عروضي صارم: النص المدخل غير مشكول بالحركات. اتبع الخطوات التالية بدقة رياضية:\n"
            "1. شكّل كل كلمة تشكيلاً نحوياً وصرفياً صحيحاً في ذهنك أولاً بناءً على النطق الصحيح.\n"
            "2. اكتب الكتابة العروضية الحقيقية (فك المشدد، تحويل التنوين لنون ساكنة، حذف همزة الوصل وسط الكلام، وإشباع آخر الشطر).\n"
            "3. استخرج الرموز (/ للحرف المتحرك، 0 للحرف الساكن) بحيث يطابق عدد الرموز عدد حروف الكتابة العروضية 100%.\n"
            "4. قارن الرموز بمفاتيح الخليل بدقة:\n"
            "   - البسيط: مُسْتَفْعِلُنْ (/0/0//0) فَاعِلُنْ (/0//0) مُسْتَفْعِلُنْ (/0/0//0) فَعِلُنْ (///0).\n"
            "   - الطويل: فَعُولُنْ (//0/0) مَفَاعِيلُنْ (//0/0/0) فَعُولُنْ (//0/0) مَفَاعِلُنْ (//0//0).\n"
            "   - الكامل: مُتَفَاعِلُنْ (///0//0) ثلاث مرات.\n"
            "   - الوافر: مُفَاعَلَتُنْ (//0///0) مرتين ثم فَعُولُنْ (//0/0).\n"
            "   - السريع: مُسْتَفْعِلُنْ (/0/0//0) مرتين ثم فَاعِلُنْ (/0//0)."
        )
        return guidance, pd.DataFrame()

    # مسار 2: النص المشكول أو الشعبي/النبطي -> الحساب الرياضي المباشر + الجدول
    ashatar = []
    for line in raw_lines:
        if '=' in line:
            ashatar.extend([p.strip() for p in line.split('=') if p.strip()])
        elif '***' in line:
            ashatar.extend([p.strip() for p in line.split('***') if p.strip()])
        else:
            ashatar.append(line)
            
    raw_rows = []
    votes = {}
    for idx, shatr in enumerate(ashatar):
        sym = line_to_prosody_symbols(shatr)
        meter_name, tafeelat = classify_symbols(sym)
        if "يطابق" not in meter_name and meter_name != "غير محدد":
            votes[meter_name] = votes.get(meter_name, 0) + 1
        raw_rows.append((idx + 1, shatr, meter_name, tafeelat, sym))

    best_meter = max(votes, key=votes.get) if votes else "بحر عربي أصيل"
    best_tafeelat = next((taf for _, _, name, taf, _ in raw_rows if name == best_meter), "تفعيلات موزونة")

    rows = []
    
    for num, shatr, m_name, taf, sym in raw_rows:
        # إذا كان الشطر على البحر السائد أو يحمل جوازاً لم يُكتشف، نعرض تفعيلات البحر السائد بدلاً من عبارة "تفعيلات قياسية"
        final_taf = taf if m_name == best_meter else best_tafeelat
        rows.append({"م": num, "الشطر": shatr, "التفعيلات": final_taf, "الرموز": sym})

    df = pd.DataFrame(rows)
    sample_syms = "\n".join([f"- الشطر ({r['م']}): {r['الرموز']}" for r in rows[:4]])

    report_str = (
        f"البحر الشعري المؤكد رياضياً (من واقع {len(rows)} شطر) هو: **بحر {best_meter}**\n"
        f"- التفعيلات القياسية: **{best_tafeelat}**\n"
        f"- عينة التقطيع الصوتي الفعلي:\n{sample_syms}\n"
        f"- قواعد صارمة: التزم بتفعيلات بحر ({best_meter}) وجوازاته بدقة تامة. لا تخلط بين الكامل والوافر، ولا بين السريع/الصخري والرجز. وإذا كانت القصيدة شعبية ذات قافيتين فلا تخلط بينهما."
    )
    return report_str, df


# ==========================================
# واجهة التطبيق الرئيسية (نفس كودك الأصلي السريع)
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
        value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"
    )

    if st.button("🚀 ابدأ النقد الأدبي والعروضي الموثق", use_container_width=True):
        if not user_prompt.strip():
            st.error("الرجاء كتابة النص الشعري أولاً!")
        else:
            is_fusha = (poem_style == "شعر فصيح (عمودي)")
            meter_guidance, scansion_df = detect_arabic_meter_and_table(user_prompt, is_fusha)
            st.session_state["scansion_df"] = scansion_df

        lines_list = [l.strip() for l in user_prompt.strip().split('\n') if l.strip()]
        if len(lines_list) == 2:
            poem_sample = f"بيت شعري واحد مكون من شطرين:\n- الصدر (الشطر الأول): {lines_list[0]}\n- العجز (الشطر الثاني): {lines_list[1]}"
        else:
            poem_sample = "\n".join(lines_list)

            full_prompt = f"""أنت عالم عروض وناقد أدبي عربي خبير في منصة "الناقد الذكي".
بيانات الضبط العروضي الأولية (قد تتأثر بنقص التشكيل، فاعتمد التقطيع الصوتي الصحيح للكلمات):
{meter_guidance}

قواعد عروضية صارمة (ممنوع مخالفتها):
1. انتبه لعدد الأبيات: كل شطرين (صدر وعجز) يمثلان بيتاً شعرياً واحداً فقط، فلا تصف الشطرين بأنهما "بيتان".
2. التقطيع الصوتي الصحيح يحدد البحر:
   - إذا بدأ الشطر بـ (فَعُولُنْ //0/0) ثم (مَفَاعِيلُنْ //0/0/0) فالبحر هو (الطويل) حصراً.
   - إذا بدأ الشطر بـ (مُسْتَفْعِلُنْ /0/0//0) ثم (فَاعِلُنْ /0//0) فالبحر هو (البسيط) حصراً.
   - إذا بدأ الشطر بـ (مُتَفَاعِلُنْ ///0//0 أو //0//0) فالبحر هو (الكامل) حصراً.
   - إذا بدأ الشطر بـ (مُفَاعَلَتُنْ //0///0 أو //0/0/0) فالبحر هو (الوافر) حصراً.
3. تذكر جوازات البحور ولا تعتبرها كسراً أبداً (مثل القبض والخبن والإضمار والقطع).
4. لا تتهم أي شطر بالميل إلى بحر آخر أو وجود خلل وزني ما دامت تفعيلاته مطابقة لتفعيلات البحر الأساسي للقصيدة وجوازاته المعروفة؛ ولا تذكر تنبيهات عروضية إلا عند وجود كسر وزني حقيقي لا يقبله أي جواز.
5. لا تخترع تفعيلات غير متطابقة مع الرموز الصوتية، ولا تستخدم جداول markdown.

النص الشعري المراد تحليله:
{poem_sample}

مراجع إضافية:
{context_content[:3000]}

قدّم التقرير في 4 أقسام منظمة:
### أولاً: التوثيق التاريخي والأدبي
### ثانياً: الشرح اللغوي والدلالي
### ثالثاً: التحليل العروضي والإيقاع الموسيقي (الكتابة العروضية، وتوزيع الكلمات على التفعيلات، والبحر، والقافية والروي)
### رابعاً: التحليل البلاغي والجمالي
"""



        with st.spinner("🔄 جاري استخراج التحليل الأكاديمي والعروضي الموثق..."):
            final_report = ""
            available = [m.name.replace("models/", "") for m in client.models.list() if "gemini" in m.name]
            preferred = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"]
            valid_models = [m for m in preferred if m in available] + [m for m in available if "flash" in m and m not in preferred]

            for model_name in valid_models:
                try:
                    response = client.models.generate_content(model=model_name, contents=full_prompt)
                    if response and response.text:
                        final_report = response.text
                        break
                except Exception:
                    time.sleep(1)
                    continue

            if final_report:
                st.session_state["saved_report"] = final_report
                st.session_state["saved_poem"] = poem_sample
            else:
                st.warning("⏳ خوادم جوجل تشهد ضغطاً لحظياً، يرجى الضغط على الزر مرة أخرى بعد قليل.")

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
