import streamlit as st
import os
import re
from google import genai
from google.genai import types

try:
    from duckduckgo_search import DDGS
    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False

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

def remove_diacritics(text):
    arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
    return re.sub(arabic_diacritics, '', text)

def search_poem_context(clean_text):
    if not HAS_SEARCH:
        return ""
    try:
        lines = [l.strip() for l in clean_text.split('\n') if l.strip()]
        first_line = next(iter(lines))[:80]
        query = f'"{first_line}" قصيدة الشاعر'
        results_text = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, region='wt-wt', max_results=2):
                results_text.append(f"- {r.get('title', '')}: {r.get('body', '')}")
        return "\n".join(results_text)
    except Exception:
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

            with st.spinner("🔄 جاري التحقق السريع من المصادر..."): 
                clean_poem = remove_diacritics(user_prompt)
                web_context = search_poem_context(clean_poem)

            extra_sources = ""
            if context_content:
                extra_sources += f"\n[مرجع المستخدم المرفق]:\n{context_content[:3000]}\n"
            if web_context:
                extra_sources += f"\n[نتائج البحث الأدبي]:\n{web_context}\n"

            system_instruction = f"""
أنت بروفيسور وعلامة محقق في الأدب العربي (الفصيح والشعبي) وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
تلتزم بالمنهج العلمي الأكاديمي الصارم:
1. عدد الأبيات المؤكد برمجياً هو: ({verse_count_info}). التزم به حرفياً.
2. التمييز اللغوي: حدد أولاً نوع النص بدقة (شعر فصيح عمودي، شعر تفعيلة، أم شعر شعبي/نبطي).
3. الأمانة في التوثيق:
   - إذا كان النص لشاعر معروف في التراث أو الأدب الحديث (مثل المتنبي، شوقي، نزار قباني...) اذكر اسم الشاعر، الديوان، العصر، والمناسبة التاريخية بدقة تامة.
   - إذا كان النص شعراً شعبياً غير منشور أو محاولة شعرية خاصة غير موجودة في الدواوين أو نتائج البحث، صرّح بأمانة أنه "نص غير موثق في الدواوين المنشورة" دون اختلاق أسماء شعراء.
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
            st.write("---")
            st.markdown("### ✨ تقرير الناقد الأكاديمي والعروضي المتكامل:")
            
            # مكان عرض النص المباشر أثناء الكتابة
            report_placeholder = st.empty()
            full_response = ""
            
            models_to_try = ["gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-3.8-pro"]
            success = False

            for model_name in models_to_try:
                try:
                    response_stream = client.models.generate_content_stream(
                        model=model_name,
                        contents=user_message,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.1,
                        )
                    )
                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            report_placeholder.markdown(full_response + " ▌")
                    
                    report_placeholder.markdown(full_response)
                    success = True
                    break
                except Exception:
                    full_response = ""
                    continue

            if success and full_response:
                st.download_button(
                    label="📥 تحميل التقرير النقدي (ملف نصي)",
                    data=full_response,
                    file_name="تقرير_الناقد_الذكي.txt",
                    mime="text/plain"
                )
            else:
                st.warning("⚠️ الخوادم تشهد ضغطاً لحظياً، يرجى الضغط على زر التحليل مرة أخرى.")
else:
    st.info("💡 يرجى إضافة مفتاح GEMINI_API_KEY في إعدادات الـ Secrets الخاصة بالتطبيق.")
