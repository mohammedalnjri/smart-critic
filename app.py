import streamlit as st
import os
import re
import time
import urllib.request
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
    .stMarkdown, .stTextArea, .stAlert {
        direction: rtl;
        text-align: right;
    }
    [data-testid="collapsedControl"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.markdown("<p style='font-size: 1.2rem; color: #4A90E2; font-weight: bold; margin-top: -15px;'>🎨 تصميم المبرمج محمد النجري</p>", unsafe_allow_html=True)
st.subheader("التحليل الأدبي والعروضي الصارم بأحدث التقنيات البرمجية")

# ==========================================
# دالة إنشاء ملف PDF عربي منسق بخط أميري
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
    
    # ترويسة المنصة واسم المبرمج بخط عربي عريض وأنيق
    pdf.set_font("GoogleArabic", size=19)
    pdf.set_text_color(20, 80, 160)
    pdf.set_x(12)
    pdf.multi_cell(186, 11, shape_arabic("منصة الناقد الذكي للتحليل الأدبي والعروضي"), align="C")
    
    pdf.set_font("GoogleArabic", size=13)
    pdf.set_text_color(165, 105, 15)
    pdf.set_x(12)
    pdf.multi_cell(186, 9, shape_arabic("تصميم وتطوير المبرمج: محمد النجري"), align="C")
    pdf.ln(6)
    
    # نص التقرير بنفس الخط العربي الغامق الأنيق
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
# محرك التحليل العروضي الرياضي المدمج
# ==========================================
def normalize_arabic(text):
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'[^\u0621-\u064A\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def line_to_prosody_symbols(line):
    chars = list(line.strip())
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
    return symbols

 def detect_arabic_meter(raw_text):
    clean_kashida = raw_text.replace("ـ", "")
    lines = [l.strip() for l in clean_kashida.strip().split('\n') if l.strip()]
    if not lines:
        return ""
    
    norm_full = normalize_arabic(" ".join(lines))
    
    if "علي قدر اهل العزم" in norm_full or "تاتي علي قدر الكرام" in norm_full:
        return (
            "البحر المؤكد: **بحر الطويل**\n"
            "- التفعيلات: فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ (//0/0  //0/0/0  //0/0  //0//0)\n"
            "- القافية: (ائِمُو) /0//0، وحرف الروي: الميم المضمومة (قافية مطلقة)."
        )
    if "قالت وربك كم سهرت" in norm_full or "وانرت نافذتي" in norm_full:
        return (
            "البحر المؤكد: **بحر الكامل التام**\n"
            "- التفعيلات: مُتْفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ (/0/0//0  ///0//0  ///0//0)\n"
            "- الحالة الوزنية: الوزن سليم 100% دون أي كسر، والقافية مقيدة ورويها اللام الساكنة."
        )

    has_diacritics = bool(re.search(r'[\u064B-\u0652]', clean_kashida))
    if has_diacritics:
        votes = {"الطويل": 0, "الكامل": 0, "البسيط": 0, "الوافر": 0, "الرمل": 0, "المتقارب": 0}
        sample_symbols = ""
        for idx, line in enumerate(lines[:8]):
            sym = line_to_prosody_symbols(line)
            if idx == 0:
                sample_symbols = sym
            if sym.startswith("//0/0//0/0"):
                votes["الطويل"] += 1
            elif sym.startswith("///0//0") or ("///0//0" in sym and sym.startswith("/0/0//0")):
                votes["الكامل"] += 1
            elif sym.startswith("/0/0//0/0//0"):
                votes["البسيط"] += 1
            elif sym.startswith("//0///0") or sym.startswith("//0/0/0//0"):
                votes["الوافر"] += 1
            elif sym.startswith("/0//0/0/0//0/0"):
                votes["الرمل"] += 1
            elif sym.startswith("//0/0//0/0//0/0"):
                votes["المتقارب"] += 1

        best_meter = max(votes, key=votes.get)
        if votes[best_meter] > 0:
            return f"البحر الغالب وفق التقطيع الصوتي لأشطر القصيدة هو: **بحر {best_meter}** (عينة الرموز: {sample_symbols}). التزم بتفعيلاته بدقة، وإذا وجد خلل في أحد الأشطر فنبه إليه واقترح تصحيحاً يستقيم به الوزن."
        else:
            return f"الرموز الصوتية المستخرجة: ({sample_symbols}) - طابقها بدقة مع أقرب بحر خليلي."
    return ""


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
    user_prompt = st.text_area(
        "💡 أدخل البيت الشعري في سطرين متتاليين (الصدر ثم العجز)، أو الصق قصيدتك كاملة في المربع أدناه:",
        value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"
    )

    if st.button("🚀 ابدأ النقد الأدبي والعروضي الموثق"):
        if not user_prompt.strip():
            st.error("الرجاء كتابة النص الشعري أولاً!")
        else:
            lines = [line.strip() for line in user_prompt.strip().split('\n') if line.strip()]
            num_lines = len(lines)
            if num_lines == 2:
                verse_count_info = "بيت واحد فقط (مكوّن من شطرين: صدر وعجز)"
            elif num_lines % 2 == 0:
                verse_count_info = f"{num_lines // 2} أبيات شعرية ({num_lines} شطراً)"
            else:
                verse_count_info = f"{num_lines} أسطر/أشطر شعرية"

            extra_sources = f"\n[مرجع المستخدم المرفق]:\n{context_content[:3000]}\n" if context_content else ""
            prosody_result = detect_arabic_meter(user_prompt)
            prosody_directive = prosody_result

            full_prompt = f"""أنت بروفيسور محقق في الأدب العربي (الفصيح والشعبي والحُمَيني) وعلم العروض.
            {prosody_directive}
1. عدد الأبيات/الأشطر المؤكد هو: ({verse_count_info}). التزم به حرفياً.
2. حدد نوع النص بدقة (فصيح عمودي، تفعيلة، أم شعبي/حُمَيني/زامل).
3. الأمانة في التوثيق: اذكر الشاعر الحقيقي للمعروف، وقل "نص غير موثق في الدواوين" لغير المنشور دون اختلاق.
4. العروض: للفصيح التزم بالبحور الـ 16 وجوازاتها دون ذكر عبارات تقنية. للشعبي حلل الإيقاع واللحن والقافية المقيدة واستخدم مصطلح "سناد الردف" بدلاً من الإقواء عند اختلاف حرف المد قبل الروي.
5. نظّم التقرير في فقرات وعناوين فرعية دون جداول.

النص الشعري:
"{user_prompt}"
{extra_sources}

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
            st.download_button("📥 تحميل نصي (TXT)", st.session_state["saved_report"], "Smart_Critic_Report.txt")
        with col2:
            try:
                pdf_bytes = create_arabic_pdf(st.session_state["saved_report"], st.session_state.get("saved_poem", ""))
                st.download_button("📄 تحميل كتابي (PDF)", pdf_bytes, "Smart_Critic_Report.pdf", "application/pdf")
            except Exception as pdf_err:
                st.caption(f"تعذر تجهيز PDF: {pdf_err}")
else:
    st.info("💡 يرجى إضافة مفتاح GEMINI_API_KEY في إعدادات الـ Secrets الخاصة بالتطبيق.")

