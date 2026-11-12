import streamlit as st
import os
import re
from groq import Groq

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
            for r in ddgs.text(query, region='wt-wt', max_results=3):
                results_text.append(f"- {r.get('title', '')}: {r.get('body', '')}")
        return "\n".join(results_text)
    except Exception:
        return ""

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        models_list = client.models.list()
        available_models = [m.id for m in models_list.data]
    except Exception:
        available_models = []

    preferred_order = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3-32b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b"
    ]
    
    selected_model = "llama-3.1-8b-instant"
    for pref in preferred_order:
        if pref in available_models:
            selected_model = pref
            break

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

            with st.spinner("🔄 جاري التحقق من المصادر واستخراج التحليل الأكاديمي والعروضي..."): 
                try:
                    clean_poem = remove_diacritics(user_prompt)
                    web_context = search_poem_context(clean_poem)
                    
                    extra_sources = ""
                    if context_content:
                        extra_sources += f"\n[مرجع المستخدم المرفق]:\n{context_content[:2000]}\n"
                    if web_context:
                        extra_sources += f"\n[نتائج البحث الأدبي]:\n{web_context}\n"

                    system_instruction = f"""
أنت بروفيسور ومحقق علمي أمين في الأدب العربي (الفصيح والشعبي) وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
تلتزم بالأمانة العلمية الصارمة وتُمنع منعاً باتاً من اختلاق معلومات أو نسب نصوص لشعراء لم يكتبوها:
1. عدد الأبيات المؤكد برمجياً هو: ({verse_count_info}). التزم به حرفياً ولا تغيره.
2. التمييز اللغوي: حدد أولاً نوع النص بدقة (هل هو شعر فصيح عمودي، أم شعر تفعيلة، أم شعر شعبي/نبطي يعتمد على اللهجة العامية).
3. قاعدة التوثيق الأمين:
   - إذا كان النص معروفاً ومؤكداً في التراث أو نتائج البحث المرفقة (مثل شعر المتنبي، شوقي، نزار قباني...) اذكر اسم الشاعر الحقيقي والمناسبة بدقة.
   - إذا لم تجد دليلاً قاطعاً في نتائج البحث المرفقة أو ذاكرتك المؤكدة على قائل النص (خاصة إذا كان شعراً نبطياً/شعبياً أو محاولة شعرية حديثة غير منشورة)، اكتب بوضوح وأمانة: "نص غير موثق في الدواوين المنشورة (قد يكون نصاً خاصاً أو لشاعر معاصر)"، ويُمنع منعاً باتاً اختراع اسم شاعر أو ديوان وهمي.
4. علم العروض والقافية: حلل موسيقى النص ووزنه وقافيته بدقة حسب نوعه (فصيح أو شعبي).
5. التنسيق: اكتب التقرير في فقرات ونقاط واضحة بعناوين فرعية، ولا تستخدم الجداول مطلقاً.
"""

                    user_message = f"""
النص الشعري المدخل:
"{user_prompt}"

النص بدون تشكيل:
"{clean_poem}"
{extra_sources}

قدم تقريراً أكاديمياً متكاملاً ومفصلاً مقسماً إلى الأقسام الأربعة التالية:

### أولاً: التوثيق التاريخي والأدبي
- نوع النص الشعري (فصيح عمودي / تفعيلة / شعبي نبطي).
- عدد الأبيات: {verse_count_info}.
- اسم الشاعر والمناسبة (بأمانة علمية تامة دون تخمين).

### ثانياً: الشرح اللغوي والدلالي
- معاني المفردات والتعابير.
- الشرح الإجمالي والدلالي العميق للأبيات.

### ثالثاً: التحليل العروضي والإيقاع الموسيقي
- الكتابة العروضية والتقطيع الصوتي (للشعر الفصيح) أو تحليل الوزن والقافية واللحن (للشعر الشعبي).
- تحديد البحر الشعري أو الوزن وتفعيلاته وحرف الروي.

### رابعاً: التحليل البلاغي والجمالي
- الصور البيانية (التشبيه، الاستعارة، الكناية).
- المحسنات البديعية والجماليات الأسلوبية.
"""
                    api_kwargs = {
                        "messages": [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_message}
                        ],
                        "model": selected_model,
                        "temperature": 0.1,
                        "max_tokens": 2500
                    }
                    
                    if "gpt-oss" in selected_model.lower():
                        api_kwargs["reasoning_effort"] = "low"
                    elif "qwen" in selected_model.lower():
                        api_kwargs["reasoning_format"] = "hidden"
                        api_kwargs["max_tokens"] = 950

                    chat_completion = client.chat.completions.create(**api_kwargs)
                    
                    st.write("---")
                    st.markdown("### ✨ تقرير الناقد الأكاديمي والعروضي المتكامل:")
                    
                    first_choice = next(iter(chat_completion.choices))
                    response_text = first_choice.message.content
                    
                    if response_text:
                        st.markdown(response_text)
                        st.download_button(
                            label="📥 تحميل التقرير النقدي (ملف نصي)",
                            data=response_text,
                            file_name="تقرير_الناقد_الذكي.txt",
                            mime="text/plain"
                        )
                    else:
                        st.warning("⚠️ تعذر استخراج التقرير حالياً، يرجى المحاولة مرة أخرى.")
                        
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ الموقع يشهد ضغطاً حالياً، يرجى الانتظار 30 ثانية ثم المحاولة مجدداً.")
                    else:
                        st.error("⚠️ حدث خطأ غير متوقع أثناء المعالجة، يرجى المحاولة مرة أخرى.")
else:
    st.info("💡 يرجى التأكد من وضع متغير GROQ_API_KEY داخل منطقة الـ Secrets في إعدادات التطبيق.")
