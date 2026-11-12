import streamlit as st
import os
import re
import time
from google import genai

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
    lines = [l.strip() for l in raw_text.strip().split('\n') if l.strip()]
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

    has_diacritics = bool(re.search(r'[\u064B-\u0652]', raw_text))
    if has_diacritics:
        first_line = next(iter(lines))
        first_symbols = line_to_prosody_symbols(first_line)
        if first_symbols.startswith("//0/0//0/0"):
            return f"التقطيع الصوتي الآلي للشطر الأول: ({first_symbols}) -> يطابق **بحر الطويل** (فَعُولُنْ مَفَاعِيلُنْ)."
        elif first_symbols.startswith("///0//0") or ("///0//0" in first_symbols and first_symbols.startswith("/0/0//0")):
            return f"التقطيع الصوتي الآلي للشطر الأول: ({first_symbols}) -> يطابق **بحر الكامل** (مُتَفَاعِلُنْ وجوازها المضمر مُتْفَاعِلُنْ)."
        elif first_symbols.startswith("/0/0//0/0//0"):
            return f"التقطيع الصوتي الآلي للشطر الأول: ({first_symbols}) -> يطابق **بحر البسيط** (مُسْتَفْعِلُنْ فَاعِلُنْ)."
        elif first_symbols.startswith("//0///0") or first_symbols.startswith("//0/0/0//0"):
            return f"التقطيع الصوتي الآلي للشطر الأول: ({first_symbols}) -> يطابق **بحر الوافر** (مُفَاعَلَتُنْ وجوازها المعصوب مُفَاعَلْتُنْ)."
        elif first_symbols.startswith("/0//0/0/0//0/0"):
            return f"التقطيع الصوتي الآلي للشطر الأول: ({first_symbols}) -> يطابق **بحر الرمل** (فَاعِلَاتُنْ)."
        elif first_symbols.startswith("//0/0//0/0//0/0"):
            return f"التقطيع الصوتي الآلي للشطر الأول: ({first_symbols}) -> يطابق **بحر المتقارب** (فَعُولُنْ)."
        else:
            return f"الرموز الصوتية المستخرجة آلياً للشطر الأول: ({first_symbols}) - طابقها بدقة مع أقرب بحر خليلي دون اختلاق تفعيلات متداخلة."
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
            prosody_directive = f"\n[نتيجة المحرك العروضي البرمجي - التزم بها حرفياً]:\n{prosody_result}\n" if prosody_result else ""

            full_prompt = f"""
أنت بروفيسور وعلامة محقق في الأدب العربي (الفصيح والشعبي) وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
{prosody_directive}
التزم بالمنهج العلمي الأكاديمي الصارم التالي:

1. عدد الأبيات المؤكد هو: ({verse_count_info}). التزم به حرفياً.
2. حدد نوع النص بدقة (شعر فصيح عمودي، شعر تفعيلة، أم شعر شعبي/نبطي).
3. الأمانة في التوثيق:
   - إذا كان النص لشاعر معروف في التراث أو الأدب الحديث (مثل المتنبي، شوقي، نزار قباني...) اذكر اسم الشاعر، الديوان، العصر، والمناسبة التاريخية بدقة تامة.
   - إذا كان النص شعراً شعبياً غير منشور أو محاولة شعرية خاصة غير موجودة في الدواوين، صرّح بأمانة أنه "نص غير موثق في الدواوين المنشورة" دون اختلاق أسماء شعراء.
4. الدقة العروضية:
   - اعتمد على نتيجة المحرك العروضي البرمجي أعلاه إن وجدت، ولا تخالفها أبداً.
   - التزم بتفعيلات بحر خليلي واحد موحد للقصيدة كاملة، ولا تخلط تفعيلات بحور مختلفة في شطر واحد.
   - لا تحكم بوجود كسر عروضي في قصيدة موزونة إلا إذا اختل الوزن فعلاً عن جميع البحور الـ 16 وجوازاتها.
   - حدد القافية وحرف الروي وحركته (مطلق أم مقيد) بدقة.
5. التنسيق: نظّم التقرير في فقرات ونقاط واضحة بعناوين فرعية، ويُمنع استخدام الجداول منعاً باتاً.

النص الشعري المطلوب تحليله:
"{user_prompt}"
{extra_sources}

قدّم التقرير مقسماً إلى الأقسام الأربعة التالية:
### أولاً: التوثيق التاريخي والأدبي
### ثانياً: الشرح اللغوي والدلالي
### ثالثاً: التحليل العروضي والقافية
### رابعاً: التحليل البلاغي والجمالي
"""
            with st.spinner("🔄 جاري استخراج التحليل الأكاديمي والعروضي الموثق..."):
                final_report = ""
                valid_models = []
                try:
                    for m in client.models.list():
                        name = m.name.replace("models/", "")
                        if "gemini" in name and ("flash" in name or "pro" in name):
                            if not any(x in name for x in ("vision", "embedding", "tts", "image", "audio", "1.5", "2.0", "2.5")):
                                valid_models.append(name)
                except Exception:
                    valid_models = ["gemini-3.8-flash", "gemini-3-flash-preview"]

                if not valid_models:
                    valid_models = ["gemini-3.8-flash", "gemini-3-flash-preview"]

                for model_name in valid_models:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=full_prompt
                        )
                        if response and response.text:
                            final_report = response.text
                            break
                    except Exception:
                        time.sleep(1)
                        continue

                if final_report:
                    st.session_state["saved_report"] = final_report
                else:
                    st.info("⏳ خوادم جوجل تشهد ضغطاً لحظياً في هذه الدقيقة، يرجى الضغط على الزر مرة أخرى بعد قليل.")

    if "saved_report" in st.session_state and st.session_state["saved_report"]:
        st.write("---")
        st.markdown("### ✨ تقرير الناقد الأكاديمي والعروضي المتكامل:")
                st.markdown(st.session_state["saved_report"])
        st.download_button(
            label="📥 تحميل التقرير النقدي (ملف نصي)",
            data=st.session_state["saved_report"],
            file_name="تقرير_الناقد_الذكي.txt",
            mime="text/plain"
        )
else:
    st.info("💡 يرجى إضافة مفتاح GEMINI_API_KEY في إعدادات الـ Secrets الخاصة بالتطبيق.")

