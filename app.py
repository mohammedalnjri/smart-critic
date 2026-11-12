import streamlit as st
import os
from groq import Groq

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
</style>
""", unsafe_allow_html=True)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.markdown("<p style='font-size: 1.2rem; color: #4A90E2; font-weight: bold; margin-top: -15px;'>🎨 تصميم المبرمج محمد النجري</p>", unsafe_allow_html=True)
st.subheader("التحليل الأدبي والعروضي الصارم بأحدث التقنيات البرمجية")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        models_list = client.models.list()
        available_models = [
            m.id for m in models_list.data 
            if "whisper" not in m.id.lower() and "guard" not in m.id.lower() and "orpheus" not in m.id.lower()
        ]
    except Exception:
        available_models = ["llama-3.1-8b-instant", "qwen/qwen3-32b", "openai/gpt-oss-120b"]

    # إعطاء الأولوية لنماذج Llama و Qwen لأنها أدق في الأدب العربي ولا تهلوس في التوثيق
    preferred_order = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3-32b",
        "openai/gpt-oss-120b"
    ]
    
    default_index = 0
    for pref in preferred_order:
        if pref in available_models:
            default_index = available_models.index(pref)
            break

    with st.sidebar:
        st.header("⚙️ إعدادات المحرك")
        selected_model = st.selectbox(
            "اختر محرك التحليل:",
            options=available_models,
            index=default_index
        )
        max_out_tokens = st.slider(
            "الحد الأقصى لطول التقرير:",
            min_value=800,
            max_value=4000,
            value=2000,
            step=100
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

            # رسالة انتظار نظيفة بدون إظهار اسم أي نموذج تقني
            with st.spinner("🔄 جاري استخراج التحليل الأكاديمي والعروضي الموثق..."): 
                try:
                    reference_text = f"\nاعتمد على المرجع المرفق التالي في توثيقك:\n{context_content}" if context_content else ""
                    
                    system_instruction = f"""
أنت بروفيسور محقق في الأدب العربي القديم وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
تلتزم بالقواعد العلمية الصارمة التالية دون أي تخمين أو هلوسة:
1. عدد الأبيات في النص المدخل هو تحديداً: ({verse_count_info}). التزم بهذا العدد حرفياً.
2. التوثيق التاريخي: اذكر القائل الحقيقي للقصيدة بدقة (على سبيل المثال: بيت "على قدر أهل العزم تأتي العزائم" هو من أشهر أبيات أبي الطيب المتنبي في مدح سيف الدولة الحمداني في العصر العباسي). يُمنع منعاً باتاً ادعاء أن الشعر الكلاسيكي المشهور يعود لشاعر معاصر مجهول أو للقرن العشرين.
3. علم العروض والقافية: قطّع البيت صوتياً وعروضياً بدقة متناهية وطابق التفعيلات مع البحر الصحيح:
   - (فعولن مفاعيلن فعولن مفاعيلن) = بحر الطويل.
   - (مستفعلن مستفعلن مستفعلن) = بحر الرجز.
   - (مفاعلتن مفاعلتن فعولن) = بحر الوافر.
   - (متفاعلن متفاعلن متفاعلن) = بحر الكامل.
   - (فاعلاتن فاعلاتن فاعلاتن) = بحر الرمل.
"""

                    user_message = f"""
قدم تقريراً أكاديمياً متكاملاً ودقيقاً للنص الشعري التالي:
"{user_prompt}"
{reference_text}

قسّم التقرير بوضوح إلى الأقسام الأربعة التالية:
أولاً: التوثيق التاريخي والأدبي (عدد الأبيات: {verse_count_info}، اسم الشاعر الحقيقي، العصر الأدبي، ومناسبة النص).
ثانياً: الشرح اللغوي والدلالي (معاني المفردات، وشرح المعنى الإجمالي للبيت).
ثالثاً: التحليل العروضي والقافية (الكتابة العروضية للصدر والعجز، التقطيع بالرموز /0//0، التفعيلات، اسم البحر الشعري الصحيح، وحرف الروي).
رابعاً: التحليل البلاغي والجمالي (الصور البيانية من تشبيه واستعارة وكناية، والمحسنات البديعية).
"""
                    api_kwargs = {
                        "messages": [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_message}
                        ],
                        "model": selected_model,
                        "temperature": 0.1,
                        "max_tokens": max_out_tokens
                    }
                    
                    if "gpt-oss" in selected_model.lower():
                        api_kwargs["reasoning_effort"] = "low"
                    elif "qwen" in selected_model.lower():
                        api_kwargs["reasoning_format"] = "hidden"
                        api_kwargs["max_tokens"] = min(max_out_tokens, 950)

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
                        st.warning("⚠️ لم يُرجع المحرك نصاً، جرب اختيار محرك آخر من القائمة الجانبية (>>).")
                        
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ تجاوزت الحد المجاني للدقيقة. انتظر دقيقة واحدة أو اختر محركاً آخر من القائمة الجانبية (>>).")
                    else:
                        st.error(f"⚠️ حدث خطأ أثناء المعالجة: {e}")
else:
    st.info("💡 يرجى التأكد من وضع متغير GROQ_API_KEY داخل منطقة الـ Secrets في إعدادات التطبيق.")
