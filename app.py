import streamlit as st
import os
import time
from google import genai
from google.genai import types

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

            full_prompt = f"""
بصفتك بروفيسوراً ومحققاً في الأدب العربي (الفصيح والشعبي) وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي، التزم بالقواعد الصارمة التالية:

1. عدد الأبيات المؤكد هو: ({verse_count_info}). التزم به حرفياً.
2. حدد نوع النص بدقة (شعر فصيح عمودي، شعر تفعيلة، أم شعر شعبي/نبطي).
3. الأمانة في التوثيق:
   - إذا كان النص لشاعر معروف في التراث أو الأدب الحديث (مثل المتنبي، شوقي، نزار قباني...) اذكر اسم الشاعر، الديوان، العصر، والمناسبة التاريخية بدقة تامة.
   - إذا كان النص شعراً شعبياً غير منشور أو محاولة شعرية خاصة غير موجودة في الدواوين، صرّح بأمانة أنه "نص غير موثق في الدواوين المنشورة" دون اختلاق أسماء شعراء.
4. قواعد التحقق العروضي الصارمة:
   - اكتب البيت كتابة عروضية صوتية دقيقة (فك الإدغام، حذف همزة الوصل، حذف ألف المد عند التقاء الساكنين، وإشباع حركة الروي).
   - حوّل كل حرف متحرك إلى (/) وكل حرف ساكن أو حرف مد إلى (0).
   - طابق بداية الشطر مع الميزان العروضي الحقيقي قبل تسمية البحر:
     * إذا بدأ الشطر بـ (//0/0 = فَعُولُنْ) وتلاه (//0/0/0 = مَفَاعِيلُنْ) فالبحر هو (بحر الطويل) قطعاً، ويُمنع تسميته بالبسيط أو الرجز.
     * إذا بدأ الشطر بـ (/0/0//0 = مُسْتَفْعِلُنْ) وتلاه (/0//0 = فَاعِلُنْ) فالبحر هو (بحر البسيط).
     * إذا بدأ الشطر بـ (//0///0 = مُفَاعَلَتُنْ) فالبحر هو (بحر الوافر).
     * إذا بدأ الشطر بـ (///0//0 = مُتَفَاعِلُنْ) فالبحر هو (بحر الكامل).
     * إذا بدأ الشطر بـ (/0//0/0 = فَاعِلَاتُنْ) فالبحر هو (بحر الرمل).
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
                
                # جلب نماذج Gemini المتاحة فعلياً في مفتاحك فقط
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
