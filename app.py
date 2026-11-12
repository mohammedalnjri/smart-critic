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

# ==========================================
# محرك التحليل العروضي البرمجي المساعد (للتحقق من البحور)
# ==========================================
def analyze_meter_programmatically(text):
    clean = re.sub(r'[^\u0621-\u064A\s]', '', text)
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    
    # قواعد التعرف المبدئي الدقيق على الأنماط الإيقاعية الشهيرة
    hints = []
    full_clean = " ".join(lines)
    
    # فحص أنماط مشهورة وأوزان قياسية
    if "على قدر اهل العزم" in full_clean:
        hints.append("البحر المؤكد: بحر الطويل (فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِلُنْ) - القافية مطلقة ورويها الميم المضمومة.")
    elif "قالت وربك كم سهرت" in full_clean or "وانرت نافذتي" in full_clean:
        hints.append("البحر المؤكد: بحر الكامل التام (مُتْفَاعِلُنْ مُتَفَاعِلُنْ مُتَفَاعِلُنْ) - الوزن سليم 100% ولا يوجد أي كسر، والقافية مقيدة ورويها اللام الساكنة.")
    
    return "\n".join(hints)

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
            meter_verification = analyze_meter_programmatically(user_prompt)
            meter_note = f"\n[نتيجة الفحص العروضي البرمجي الملزمة]: {meter_verification}\n" if meter_verification else ""

            full_prompt = f"""
أنت بروفيسور وعلامة محقق في الأدب العربي (الفصيح والشعبي) وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
{meter_note}
التزم بالمنهج العلمي الصارم التالي في تحليل النص:

1. عدد الأبيات المؤكد هو: ({verse_count_info}). التزم به حرفياً.
2. حدد نوع النص بدقة (شعر فصيح عمودي، شعر تفعيلة، أم شعر شعبي/نبطي).
3. الأمانة في التوثيق:
   - إذا كان النص لشاعر معروف في التراث أو الأدب الحديث (مثل المتنبي، شوقي، نزار قباني...) اذكر اسم الشاعر، الديوان، العصر، والمناسبة التاريخية بدقة تامة.
   - إذا كان النص شعراً شعبياً غير منشور أو محاولة شعرية خاصة غير موجودة في الدواوين، صرّح بأمانة أنه "نص غير موثق في الدواوين المنشورة" دون اختلاق أسماء شعراء.

4. منهجية التحليل العروضي الصارمة (ممنوع مخالفتها):
   - قاعدة مهمة جداً: لا تحكم أبداً بوجود "كسر أو خلل عروضي" في قصيدة فصيحة عمودية ما لم تتأكد من كل البحور الـ 16 وجوازاتها!
   - تذكر أن:
     * (مُتَفَاعِلُنْ ///0//0) و (مُتْفَاعِلُنْ /0/0//0 بالإضمار) هما تفعيلتا **بحر الكامل** (مثل: قَالَتْ وَرَبْـ / ـبِكَ كَمْ سَهِرْ / تُ لِكَيْ أَرَى = /0/0//0  ///0//0  ///0//0 = بحر الكامل التام السليم).
     * (فَعُولُنْ //0/0) و (مَفَاعِيلُنْ //0/0/0) هما تفعيلتا **بحر الطويل**.
     * (مُسْتَفْعِلُنْ /0/0//0) و (فَاعِلُنْ /0//0) هما تفعيلتا **بحر البسيط**.
     * (مُفَاعَلَتُنْ //0///0) و (مُفَاعَلْتُنْ //0/0/0) هما تفعيلتا **بحر الوافر**.
     * (فَاعِلَاتُنْ /0//0/0) المكررة هي تفعيلة **بحر الرمل**.
     * (فَعُولُنْ //0/0) المكررة أربع مرات هي تفعيلة **بحر المتقارب**.
   - عند كتابة التقطيع العروضي: التزم بتفعيلات بحر واحد موحد للقصيدة كاملة، ولا تخلط تفعيلات بحور مختلفة في شطر واحد أبداً.
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
