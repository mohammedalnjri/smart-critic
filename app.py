import streamlit as st
import os
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
    # ضبط مهلة زمنية صارمة (15 ثانية كحد أقصى) لمنع تعليق الصفحة لدقيقة كاملة
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=15000)
    )

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
4. الدقة العروضية المطلقة:
   - اكتب الكتابة العروضية الصحيحة (فك الإدغام، إشباع حركة الروي، حذف همزة الوصل...).
   - قطّع البيت بالرموز (/ للمتحرك و 0 للساكن).
   - استخرج التفعيلات بدقة وحدد البحر الشعري الصحيح وحرف الروي وحركته.
5. التنسيق: نظّم التقرير في فقرات ونقاط واضحة بعناوين فرعية دون جداول معقدة.
"""

            user_message = f"""
النص الشعري المدخل:
"{user_prompt}"
{extra_sources}

قدّم تقريراً أكاديمياً متكاملاً ومفصلاً مقسماً إلى الأقسام الأربعة التالية:

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
            with st.spinner("🔄 جاري استخراج التحليل الأكاديمي والعروضي..."):
                response = None
                last_error = ""
                
                for model_name in ["gemini-3.8-flash-lite", "gemini-3.8-flash"]:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=user_message,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.1,
                                thinking_config=types.ThinkingConfig(thinking_budget=0)
                            )
                        )
                        if response and response.text:
                            break
                    except Exception as err:
                        last_error = str(err)
                        continue

                st.write("---")
                st.markdown("### ✨ تقرير الناقد الأكاديمي والعروضي المتكامل:")
                
                if response and response.text:
                    st.markdown(response.text)
                    st.download_button(
                        label="📥 تحميل التقرير النقدي (ملف نصي)",
                        data=response.text,
                        file_name="تقرير_الناقد_الذكي.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"⚠️ الخادم مشغول حالياً، يرجى المحاولة مرة أخرى بعد قليل. ({last_error})")
else:
    st.info("💡 يرجى إضافة مفتاح GEMINI_API_KEY في إعدادات الـ Secrets الخاصة بالتطبيق.")
