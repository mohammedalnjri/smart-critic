import streamlit as st
import os
from google import genai
from google.genai import types
from groq import Groq

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

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if GEMINI_API_KEY or GROQ_API_KEY:
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

            system_instruction = f"""
أنت بروفيسور وعلامة محقق في الأدب العربي (الفصيح والشعبي) وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
تلتزم بالمنهج العلمي الأكاديمي الصارم:

1. عدد الأبيات المؤكد برمجياً هو: ({verse_count_info}). التزم به حرفياً.
2. التمييز اللغوي: حدد أولاً نوع النص بدقة (شعر فصيح عمودي، شعر تفعيلة، أم شعر شعبي/نبطي).
3. الأمانة في التوثيق:
   - إذا كان النص لشاعر معروف في التراث أو الأدب الحديث (مثل المتنبي، شوقي، نزار قباني...) اذكر اسم الشاعر، الديوان، العصر، والمناسبة التاريخية بدقة تامة.
   - إذا كان النص شعراً شعبياً غير منشور أو محاولة شعرية خاصة غير موجودة في الدواوين، صرّح بأمانة أنه "نص غير موثق في الدواوين المنشورة" دون اختلاق أسماء شعراء.

4. قواعد التحقق العروضي الصارمة (ممنوع مخالفتها):
   - الخطوة الأولى: اكتب البيت كتابة عروضية صوتية دقيقة (فك الإدغام، حذف همزة الوصل في درج الكلام، حذف ألف المد عند التقاء الساكنين مثل "تَأْتِي الْعَزَائِمُ" تُكتب "تَأْتِ لْعَزَائِمُو"، وإشباع حركة الروي).
   - الخطوة الثانية: حوّل كل حرف متحرك إلى (/) وكل حرف ساكن أو حرف مد إلى (0) بدقة متناهية.
   - الخطوة الثالثة (مفتاح البحور الـ 16): طابق بداية الشطر وتفعيلاته مع الميزان الصحيح قبل تسمية البحر:
     * إذا بدأ بـ (//0/0 = فَعُولُنْ) وتلاه (//0/0/0 = مَفَاعِيلُنْ) فهو (بحر الطويل) قطعاً، ويُمنع تسميته بالبسيط أو الرجز.
     * إذا بدأ بـ (/0/0//0 = مُسْتَفْعِلُنْ) وتلاه (/0//0 = فَاعِلُنْ) فهو (بحر البسيط).
     * إذا بدأ بـ (//0///0 = مُفَاعَلَتُنْ) مكررة فهو (بحر الوافر).
     * إذا بدأ بـ (///0//0 = مُتَفَاعِلُنْ) مكررة فهو (بحر الكامل).
     * إذا بدأ بـ (/0//0/0 = فَاعِلَاتُنْ) مكررة فهو (بحر الرمل).
     * إذا بدأ بـ (//0/0 = فَعُولُنْ) مكررة أربع مرات فهو (بحر المتقارب).
     * إذا بدأ بـ (/0/0//0 = مُسْتَفْعِلُنْ) مكررة ثلاث مرات فهو (بحر الرجز).
     * إذا بدأ بـ (//0/0/0 = مَفَاعِيلُنْ) مكررة مرتين في كل شطر فهو (بحر الهزج).
   - الخطوة الرابعة: استخرج القافية (من آخر ساكن إلى أول ساكن يليه مع المتحرك الذي قبله) وحدد حرف الروي وحركته بدقة.

5. التنسيق: نظّم التقرير في فقرات ونقاط واضحة بعناوين فرعية، ويُمنع استخدام الجداول منعاً باتاً.
"""

            user_message = f"""
النص الشعري المدخل:
"{user_prompt}"
{extra_sources}

قدّم تقريراً أكاديمياً متكاملاً ومفصلاً مقسماً إلى الأقسام الأربعة التالية في فقرات ونقاط واضحة دون جداول:

### أولاً: التوثيق التاريخي والأدبي
- نوع النص الشعري.
- عدد الأبيات: {verse_count_info}.
- اسم الشاعر، العصر، ومناسبة النص بالتفصيل.

### ثانياً: الشرح اللغوي والدلالي
- معاني المفردات والتراكيب.
- الشرح الإجمالي والدلالي العميق.

### ثالثاً: التحليل العروضي والقافية
- الكتابة العروضية للصدر والعجز.
- التقطيع الصوتي بالرموز (/ و 0).
- التفعيلات، اسم البحر الشعري، والقافية وحرف الروي وحركته.

### رابعاً: التحليل البلاغي والجمالي
- الصور البيانية (التشبيه، الاستعارة، الكناية).
- المحسنات البديعية والجماليات الأسلوبية.
"""
            with st.spinner("🔄 جاري استخراج التحليل الأكاديمي والعروضي الموثق..."):
                final_report = ""
                
                # المحاولة 1: Gemini (إذا لم يكن مزدحماً في هذه الثانية)
                if GEMINI_API_KEY:
                    try:
                        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                        response = gemini_client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=user_message,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.1,
                            )
                        )
                        if response and response.text:
                            final_report = response.text
                    except Exception:
                        pass

                # المحاولة 2: Groq مع مفتاح البحور الـ 16 الصارم (يضمن العمل الفوري وعدم ترك الشاشة فارغة)
                if not final_report and GROQ_API_KEY:
                    groq_client = Groq(api_key=GROQ_API_KEY)
                    for g_model in ("openai/gpt-oss-120b", "llama-3.1-8b-instant"):
                        try:
                            kwargs = {
                                "messages": [
                                    {"role": "system", "content": system_instruction},
                                    {"role": "user", "content": user_message}
                                ],
                                "model": g_model,
                                "temperature": 0.1,
                                "max_tokens": 2500
                            }
                            if "gpt-oss" in g_model:
                                kwargs["reasoning_effort"] = "low"
                                
                            chat_completion = groq_client.chat.completions.create(**kwargs)
                            first_choice = next(iter(chat_completion.choices))
                            if first_choice.message.content:
                                final_report = first_choice.message.content
                                break
                        except Exception:
                            continue

                if final_report:
                    st.session_state["saved_report"] = final_report

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
    st.info("💡 يرجى التأكد من إضافة مفاتيح API في إعدادات الـ Secrets الخاصة بالتطبيق.")
