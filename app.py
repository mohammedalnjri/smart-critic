import streamlit as st
import os
from groq import Groq

st.set_page_config(
    page_title="Smart Critic - الناقد الذكي",
    page_icon="📚",
    layout="centered"
)

# تحسين عرض اللغة العربية من اليمين إلى اليسار (RTL)
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
        available_models = ["qwen/qwen3-32b", "openai/gpt-oss-120b", "llama-3.1-8b-instant"]

    # إعطاء الأولوية للنماذج الأقوى في اللغة العربية والتراث
    preferred_order = [
        "qwen/qwen3-32b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-20b"
    ]
    
    default_index = 0
    for pref in preferred_order:
        if pref in available_models:
            default_index = available_models.index(pref)
            break

    with st.sidebar:
        st.header("⚙️ إعدادات المحرك")
        selected_model = st.selectbox(
            "اختر نموذج الذكاء الاصطناعي:",
            options=available_models,
            index=default_index
        )
        st.info("💡 نصيحة: إذا لاحظت أي خطأ عروضي من نموذج معين، جرب التبديل إلى نموذج آخر من القائمة أعلاه (مثل عائلة Qwen أو GPT-OSS-120B).")

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
        if not user_prompt:
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
        else:
            with st.spinner(f"🔄 جاري التحليل الأكاديمي الدقيق عبر ({selected_model})..."): 
                try:
                    reference_text = f"\nاعتمد على المرجع المرفق التالي في توثيقك:\n{context_content}" if context_content else ""
                    
                    system_instruction = """
أنت محقق تراثي، وأستاذ كرسي في الأدب العربي القديم وعلم العروض والقافية وفق منهج الخليل بن أحمد الفراهيدي.
قواعد صارمة لا يجوز مخالفتها:
1. التوثيق الدقيق: لا تنسب الشعر الكلاسيكي المشهور إلى "التراث الشعبي" أو "العصر الحديث" أبداً. ابحث في ذاكرتك الأدبية بدقة عن الشاعر الحقيقي والديوان والمناسبة (مثلاً: بيت "على قدر أهل العزم" هو لأبي الطيب المتنبي من قصيدته الميمية الشهيرة في مدح سيف الدولة الحمداني بمناسبة بناء قلعة الحدث الحمراء عام 343 هـ).
2. الدقة العروضية المطلقة: طابق التفعيلات مع اسم البحر بدقة متناهية:
   - (فعولن مفاعيلن فعولن مفاعيلن) هو حصراً (بحر الطويل) وليس الرجز.
   - (مستفعلن مستفعلن مستفعلن) هو (بحر الرجز).
   - (مفاعلتن مفاعلتن فعولن) هو (بحر الوافر).
   - (متفاعلن متفاعلن متفاعلن) هو (بحر الكامل).
3. عد الأبيات بدقة: البيت الواحد يتكون من شطرين (صدر وعجز). لا تخلط بين عدد الأبيات وعدد الأشطر.
"""

                    user_message = f"""
قدم تقريراً أكاديمياً متكاملاً ومفصلاً للنص الشعري التالي:
"{user_prompt}"
{reference_text}

قسّم التقرير بوضوح إلى الأقسام الأربعة التالية:
أولاً: التوثيق التاريخي والأدبي (عدد الأبيات بدقة، اسم الشاعر، العصر، الديوان، ومناسبة القصيدة بالتفصيل).
ثانياً: الشرح اللغوي والدلالي (معاني المفردات الصعبة، وشرح المعنى الإجمالي العميق).
ثالثاً: التحليل العروضي والقافية (الكتابة العروضية للصدر والعجز، الرموز العروضية /0//0، التفعيلات، اسم البحر الشعري الصحيح، وحرف الروي والقافية).
رابعاً: التحليل البلاغي والجمالي (البيان: التشبيه والاستعارة والكناية، والبديع: الطباق والمقابلة والجناس، وأثرها في المعنى).
"""
                    
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_message}
                        ],
                        model=selected_model,
                        temperature=0.1,
                        max_tokens=8192
                    )
                    
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
                        st.warning("⚠️ لم يُرجع النموذج نصاً، جرب اختيار نموذج آخر من القائمة الجانبية.")
                        
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ أثناء المعالجة: {e}")
else:
    st.info("💡 يرجى التأكد من وضع متغير GROQ_API_KEY داخل منطقة الـ Secrets في إعدادات التطبيق.")
