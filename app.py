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
def shape_arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def create_arabic_pdf(report_text, poem_text):
    import matplotlib.font_manager as fm
    pdf = FPDF()
    pdf.set_margins(12, 12, 12)
    pdf.add_page()
    
    noto_path = "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf"
    if not os.path.exists(noto_path):
        noto_path = fm.findfont("DejaVu Sans:weight=bold")
    pdf.add_font("GoogleArabic", "", noto_path)
    
    pdf.set_font("GoogleArabic", size=19)
    pdf.set_text_color(20, 80, 160)
    pdf.set_x(12)
    pdf.multi_cell(186, 11, shape_arabic("منصة الناقد الذكي للتحليل الأدبي والعروضي"), align="C")
    
    pdf.set_font("GoogleArabic", size=13)
    pdf.set_text_color(165, 105, 15)
    pdf.set_x(12)
    pdf.multi_cell(186, 9, shape_arabic("تصميم وتطوير المبرمج: محمد النجري"), align="C")
    pdf.ln(6)
    
    pdf.set_font("GoogleArabic", size=12)
    pdf.set_text_color(25, 25, 25)
    raw_all = poem_text + "\n\n" + report_text
    no_tashkeel = re.sub(r'[\u064B-\u065F\u0670*#`/0]', '', raw_all)
    for line in no_tashkeel.split('\n'):
        stripped = line.strip()
        if stripped and stripped != "التقطيع الصوتي بالرموز:":
            pdf.set_x(12)
            pdf.multi_cell(186, 8.5, shape_arabic(stripped), align="R")
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
    if "///0//0" in sym and len(sym) >= 18:
        return ("الكامل التام", "مُتَفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ")
    if "//0///0" in sym and sym.endswith("//0/0"):
        return ("الوافر التام", "مُفَاعَلَتُنْ مُفَاعَلَتُنْ فَعُولُنْ")
    if sym.startswith(("/0/0//0/0/0//0", "//0//0/0/0//0")):
        return ("السريع / الصخري", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ") if len(sym) <= 18 else ("الرجز التام", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ")
    if sym.startswith(("//0/0//0/0", "//0///0/0")):
        return ("الطويل", "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ")
    if sym.startswith(("/0/0//0/0//0", "/0/0//0///0")):
        return ("البسيط التام", "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُنْ")
    return ("يُطابق مع البحر السائد", "تفعيلات قياسية")

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
            
    rows = []
    votes = {}
    for idx, shatr in enumerate(ashatar):
        sym = line_to_prosody_symbols(shatr, is_fusha=is_fusha)
        meter_name, tafeelat = classify_symbols(sym)
        if "يُطابق" not in meter_name:
            votes[meter_name] = votes.get(meter_name, 0) + 1
        rows.append({"م": idx + 1, "الشطر": shatr, "الرموز العروضية": sym, "البحر": meter_name, "التفعيلات": tafeelat})
        
    df = pd.DataFrame(rows)
    best_meter = max(votes, key=votes.get) if votes else "يُحدد من التقطيع الصوتي الدقيق"
    best_tafeelat = next((taf for name, taf, _ in METERS_SIGNATURES if name == best_meter), "")
    sample_syms = "\n".join([f"- الشطر ({r['م']}): {r['الشطر']} -> الرموز: {r['الرموز العروضية']} ({r['البحر']})" for r in rows[:6]])
    
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

            poem_sample = "\n".join(user_prompt.strip().split('\n')[:60])
            full_prompt = f"""أنت ناقد أدبي وعروضي أكاديمي خبير في منصة الناقد الذكي.
بيانات الضبط العروضي الرياضي المؤكدة:
{meter_guidance}

النص الشعري المراد تحليله:
{poem_sample}

مراجع إضافية مرفقة:
{context_content[:3000]}

قدّم التقرير في 4 أقسام:
### أولاً: التوثيق التاريخي والأدبي
### ثانياً: الشرح اللغوي والدلالي
### ثالثاً: التحليل العروضي والإيقاع الموسيقي (اكتب الكتابة العروضية، والتقطيع الصوتي بالرموز / و 0، والتفعيلات، والبحر، والقافية والروي)
### رابعاً: التحليل البلاغي والجمالي"""

            with st.spinner("🔄 جاري استخراج التحليل الأكاديمي والعروضي الموثق..."):
                final_report = ""
                valid_models = []
                for m in client.models.list():
                    name = m.name.replace("models/", "")
                    if "gemini" in name and "flash" in name and not any(x in name for x in ("vision", "embedding", "tts", "image", "audio", "1.5", "2.0", "2.5")):
                        valid_models.append(name)

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
                    st.session_state["saved_poem"] = user_prompt
                else:
                    st.info("⏳ خوادم جوجل تشهد ضغطاً لحظياً، يرجى الضغط على الزر مرة أخرى بعد قليل.")

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
