import streamlit as st
import os
import re
import pandas as pd
from google import genai
from google.genai import types
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import mishkal.tashkeel
import pyarabic.araby as araby

st.set_page_config(page_title="Smart Critic - الناقد الذكي", page_icon="📚", layout="centered")

st.markdown("""<style>.stMarkdown, .stTextArea, .stAlert, .stDataFrame { direction: rtl; text-align: right; } [data-testid="collapsedControl"] { display: none; }</style>""", unsafe_allow_html=True)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.markdown("<p style='font-size: 1.2rem; color: #4A90E2; font-weight: bold; margin-top: -15px;'>🎨 تصميم المبرمج محمد النجري</p>", unsafe_allow_html=True)
st.subheader("التحليل الأدبي والعروضي الصارم بأحدث التقنيات البرمجية")

@st.cache_resource
def load_vocalizer():
    return mishkal.tashkeel.TashkeelClass()

vocalizer = load_vocalizer()

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

def auto_diacritize_if_needed(text: str, is_fusha: bool) -> str:
    if not is_fusha:
        return text
    letters_count = len(araby.strip_tashkeel(text))
    tashkeel_count = len(text) - letters_count
    if letters_count > 0 and (tashkeel_count / letters_count) < 0.25:
        return vocalizer.tashkeel(text)
    return text

def line_to_prosody_symbols(line: str, is_fusha: bool = True) -> str:
    text = line.strip().replace("ـ", "")
    text = text.replace('آ', 'أَا')
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
        if len(sym) <= 18:
            return ("السريع / الصخري", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ فَاعِلُنْ")
        else:
            return ("الرجز التام", "مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ مُسْتَفْعِلُنْ")
    if sym.startswith(("//0/0//0/0", "//0///0/0")):
        return ("الطويل", "فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ")
    if sym.startswith(("/0/0//0/0//0", "/0/0//0///0")):
        return ("البسيط التام", "مُسْتَفْعِلُنْ فَاعِلُنْ مُسْتَفْعِلُنْ فَعِلُنْ")
    return ("بحر مركب / يحتاج مراجعة التشكيل", "يُرجى ضبط الحركات")

def analyze_full_poem_prosody(raw_text: str, is_fusha: bool):
    clean_kashida = raw_text.replace("ـ", "")
    raw_lines = [l.strip() for l in clean_kashida.strip().split('\n') if l.strip()]
    if not raw_lines:
        return "", pd.DataFrame(), "غير محدد"

    ashطر = []
    for line in raw_lines:
        if '=' in line:
            ashطر.extend([p.strip() for p in line.split('=') if p.strip()])
        elif '***' in line:
            ashطر.extend([p.strip() for p in line.split('***') if p.strip()])
        else:
            ashطر.append(line)

    rows = []
    votes = {}
    for idx, shatr in enumerate(ashطر):
        vocalized_shatr = auto_diacritize_if_needed(shatr, is_fusha)
        sym = line_to_prosody_symbols(vocalized_shatr, is_fusha=is_fusha)
        meter_name, tafeelat = classify_symbols(sym)
        if "يحتاج مراجعة" not in meter_name:
            votes[meter_name] = votes.get(meter_name, 0) + 1
        rows.append({"م": idx + 1, "الشطر": shatr, "التشكيل المعتمد": vocalized_shatr if is_fusha else "نطق شعبي مسكّن", "الرموز العروضية": sym, "البحر": meter_name, "التفعيلات": tafeelat})

    df = pd.DataFrame(rows)
    dominant_meter = max(votes, key=votes.get) if votes else "يحتاج مراجعة التشكيل"
    dominant_tafeelat = ""
    for name, taf, _ in METERS_SIGNATURES:
        if name == dominant_meter:
            dominant_tafeelat = taf
            break

    sample_syms = "\n".join([f"- الشطر ({r['م']}): {r['الشطر']} -> الرموز: {r['الرموز العروضية']} ({r['البحر']})" for r in rows[:6]])
    prosody_summary = f"""البحر الشعري المؤكد رياضياً للقصيدة (من واقع تحليل {len(rows)} شطر): **بحر {dominant_meter}**
- التفعيلات القياسية: **{dominant_tafeelat}**
- عينة من التقطيع الصوتي الفعلي للأشطر الأولى:
{sample_syms}
تنبيه صارم للنموذج: التزم بهذا البحر وتفعيلاته بدقة 100% ولا تغيره أبداً."""
    return prosody_summary, df, dominant_meter

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

    st.write("---")
    st.markdown("### 📚 1. المراجع والنصوص المراد تحليلها (اختياري)")
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
    
    poem_style = st.radio("اختر نمط القصيدة لضبط خوارزمية التقطيع:", ["شعر فصيح (عمودي)", "شعر شعبي / نبطي / يمني"], horizontal=True)
    
    user_prompt = st.text_area("💡 أدخل البيت الشعري في سطرين متتاليين (الصدر ثم العجز)، أو الصق قصيدتك كاملة (يدعم حتى 1000+ بيت):", height=200, value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ")

    if st.button("🚀 ابدأ النقد الأدبي والعروضي الموثق", use_container_width=True):
        if not user_prompt.strip():
            st.error("الرجاء كتابة النص الشعري أولاً!")
        else:
            is_fusha = (poem_style == "شعر فصيح (عمودي)")
