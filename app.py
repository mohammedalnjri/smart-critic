import streamlit as st
import os
import re
import pandas as pd
from google import genai
from google.genai import types
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="Smart Critic - الناقد الذكي", page_icon="📚", layout="centered")
st.markdown("""<style>.stMarkdown, .stTextArea, .stAlert, .stDataFrame { direction: rtl; text-align: right; }</style>""", unsafe_allow_html=True)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.markdown("<p style='font-size: 1.2rem; color: #4A90E2; font-weight: bold; margin-top: -15px;'>🎨 تصميم المبرمج محمد النجري</p>", unsafe_allow_html=True)
st.subheader("التحليل الأدبي والعروضي الصارم بأحدث التقنيات البرمجية")

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

def line_to_prosody_symbols(line: str, is_fusha: bool = True) -> str:
    text = line.strip().replace("ـ", "").replace('آ', 'أَا')
    chars = list(text)
    expanded = []
    for ch in chars:
        if ch == '\u0651' and expanded:
            expanded.extend(['\u0652', expanded[-1]])
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
                symbols += '0' if i == len(text) - 1 else '/'
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

def classify_symbols(sym: str) -> tuple:
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
    return ("يُستنتج من البصمة الصوتية", "تفعيلات قياسية")

def analyze_full_poem_prosody(raw_text: str, is_fusha: bool):
    clean_kashida = raw_text.replace("ـ", "")
    raw_lines = [l.strip() for l in clean_kashida.strip().split('\n') if l.strip()]
    if not raw_lines:
        return "", pd.DataFrame(), "غير محدد"
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
        if "يُستنتج" not in meter_name:
            votes[meter_name] = votes.get(meter_name, 0) + 1
        rows.append({"م": idx + 1, "الشطر": shatr, "الرموز العروضية": sym, "البحر": meter_name, "التفعيلات": tafeelat})
    df = pd.DataFrame(rows)
    dominant_meter = max(votes, key=votes.get) if votes else "يُحدد بالتحليل الصوتي المرفق"
    dominant_tafeelat = next((taf for name, taf, _ in METERS_SIGNATURES if name == dominant_meter), "")
    sample_syms = "\n".join([f"- الشطر ({r['م']}): {r['الشطر']} -> الرموز: {r['الرموز العروضية']} ({r['البحر']})" for r in rows[:6]])
    prosody_summary = f"البحر الشعري المؤكد رياضياً (من {len(rows)} شطر): **بحر {dominant_meter}**\n- التفعيلات: **{dominant_tafeelat}**\n- عينة التقطيع:\n{sample_syms}"
    return prosody_summary, df, dominant_meter

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    st.error("⚠️ مفتاح GEMINI_API_KEY غير موجود في Secrets.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

st.write("---")
with st.form("critic_form"):
    st.markdown("### ✍️ أدخل القصيدة للتحليل والتقطيع")
    poem_style = st.radio("نمط القصيدة:", ["شعر فصيح (عمودي)", "شعر شعبي / نبطي / يمني"], horizontal=True)
    user_prompt = st.text_area("اكتب الأبيات هنا (يدعم حتى 1000+ بيت):", height=180, value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ")
    submitted = st.form_submit_button("🚀 ابدأ النقد الأدبي والعروضي الموثق", type="primary", use_container_width=True)

if submitted:
    if not user_prompt.strip():
        st.error("الرجاء كتابة النص الشعري أولاً!")
    else:
        is_fusha = (poem_style == "شعر فصيح (عمودي)")
        prosody_report, scansion_df, dominant_meter = analyze_full_poem_prosody(user_prompt, is_fusha)
        st.session_state["scansion_df"] = scansion_df
        st.session_state["dominant_meter"] = dominant_meter
        st.session_state["final_poem"] = user_prompt
        
        with st.spinner("جاري صياغة التقرير النقدي..."):
            poem_sample_for_ai = "\n".join(user_prompt.strip().split('\n')[:60])
            system_instruction = "أنت ناقد أدبي وعروضي خبير. اعتمد كلياً على التقرير العروضي المرفق ولا تخالفه. ميز بدقة بين الكامل (مُتَفَاعِلُنْ) والوافر (مُفَاعَلَتُنْ)، وبين السريع/الصخري (مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ) والرجز. انتبه للقوافي المزدوجة في الشعر الشعبي. نظم الإجابة إلى: أولاً: المعنى العام. ثانياً: التحليل البلاغي. ثالثاً: التحليل العروضي والإيقاعي. رابعاً: ملاحظات وتوجيهات."
            full_prompt = f"{prosody_report}\n\nالنص الشعري:\n{poem_sample_for_ai}"
            try:
                response = client.models.generate_content(model="gemini-2.5-flash", contents=full_prompt, config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2))
                st.session_state["final_report"] = response.text
            except Exception as e:
                st.error(f"خطأ في الاتصال بالنموذج: {e}")

if "scansion_df" in st.session_state:
    st.write("---")
    st.success(f"⚖️ **النتيجة العروضية:** البحر السائد هو **{st.session_state['dominant_meter']}** (تم تقطيع {len(st.session_state['scansion_df'])} شطر)."
if "final_report" in st.session_state:
if "scansion_df" in st.session_state:
    st.write("---")
    st.success(f"⚖️ **النتيجة العروضية:** البحر السائد هو **{st.session_state['dominant_meter']}** (تم تقطيع {len(st.session_state['scansion_df'])} شطر).")
if "final_report" in st.session_state:
        st.markdown(st.session_state["final_report"])
    st.write("---")
    st.markdown("### 📊 جدول التقطيع العروضي التفصيلي")
    st.dataframe(st.session_state["scansion_df"], use_container_width=True, height=350)
    col1, col2 = st.columns(2)
    with col1:
        pdf_bytes = create_arabic_pdf(st.session_state.get("final_report", "تقرير التقطيع العروضي"), st.session_state["final_poem"])
        st.download_button(label="📄 تحميل التقرير (PDF)", data=pdf_bytes, file_name="Smart_Critic_Report.pdf", mime="application/pdf", use_container_width=True)
    with col2:
        csv_bytes = st.session_state["scansion_df"].to_csv(index=False).encode("utf-8-sig")
        st.download_button(label="📥 تحميل تقطيع الأبيات (CSV)", data=csv_bytes, file_name="Prosody_Scansion_Table.csv", mime="text/csv", use_container_width=True)
