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
    .stMarkdown, .stTextArea, .stAlert, table {
        direction: rtl;
        text-align: right;
    }
    /* إخفاء زر القائمة الجانبية للإبقاء على واجهة نظيفة للزوار */
    [data-testid="collapsedControl"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.markdown("<p style='font-size: 1.2rem; color: #4A90E2; font-weight: bold; margin-top: -15px;'>🎨 تصميم المبرمج محمد النجري</p>", unsafe_allow_html=True)
st.subheader("التحليل الأدبي والعروضي الصارم بأحدث التقنيات البرمجية")

# دالة لإزالة التشكيل لتسهيل تعرف المحرك والبحث على القصيدة
def remove_diacritics(text):
    arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
    return re.sub(arabic_diacritics, '', text)

# دالة للبحث السريع عن الشاعر والمناسبة من المصادر الأدبية
def search_poem_context(clean_text):
    if not HAS_SEARCH:
        return ""
    try:
        first_line = clean_text.split('\n')[0][:80]
        query = f'"{first_line}" الشاعر قصيدة'
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
    
    # اختيار أفضل محرك متاح في الحساب بصمت
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
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
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
                        extra_sources += f"\n[نتائج التوثيق من المصادر الأدبية]:\n{web_context}\n"

                    system_instruction = f"""
أنت بروفيسور ومحقق في الأدب العربي القديم والحديث وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
تلتزم بالقواعد الصارمة التالية:
1. عدد الأبيات المؤكد هو: ({verse_count_info}). التزم به ولا تغيره.
2. التوثيق التاريخي: استعن بالمصادر المرفقة وبمعرفتك الأدبية لتحديد الشاعر الحقيقي بدقة (مثلاً: قصيدة "على قدر أهل العزم" هي لأبي الطيب المتنبي في مدح سيف الدولة الحمداني في العصر العباسي). لا تقل أبداً "شاعر غير معروف" لنص مشهور.
3. علم العروض والقافية: قطّع البيت صوتياً بدقة وحدد البحر الصحيح وتفعيلاته (فعولن مفاعيلن = الطويل).
4. التنسيق: اكتب التقرير في فقرات ونقاط واضحة ومنظمة بعناوين فرعية، وتجنب استخدام الجداول المعقدة حتى لا ينكسر التنسيق.
"""

                    user_message = f"""
النص الشعري المشكول:
"{user_prompt}"

النص بدون تشكيل:
"{clean_poem}"
{extra_sources}

اكتب تقريراً أكاديمياً متكاملاً مقسماً إلى:
### أولاً: التوثيق التاريخي والأدبي
(اذكر عدد الأبيات: {verse_count_info}، اسم الشاعر الحقيقي، العصر الأدبي، ومناسبة النص بالتفصيل).

### ثانياً: الشرح اللغوي والدلالي
(معاني المفردات، وشرح المعنى الإجمالي العميق).

### ثالثاً: التحليل العروضي والقافية
(الكتابة العروضية للصدر والعجز، التقطيع بالرموز /0//0، التفعيلات، اسم البحر الشعري الصحيح، وحرف الروي).

### رابعاً: التحليل البلاغي والجمالي
(الصور البيانية من تشبيه واستعارة وكناية، والمحسنات البديعية).
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
