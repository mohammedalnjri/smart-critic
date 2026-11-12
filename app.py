import streamlit as st
import os
from groq import Groq

st.set_page_config(
    page_title="Smart Critic - الناقد الذكي",
    page_icon="📚",
    layout="centered"
)

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
        available_models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

    preferred_order = [
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "qwen/qwen3-32b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    
    default_index = 0
    for pref in preferred_order:
        if pref in available_models:
            default_index = available_models.index(pref)
            break

    with st.sidebar:
        st.header("⚙️ إعدادات المحرك")
        selected_model = st.selectbox(
            "اختر نموذج الذكاء الاصطناعي المتاح في حسابك:",
            options=available_models,
            index=default_index
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
        if not user_prompt:
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
        else:
            with st.spinner(f"🔄 جاري استخراج التحليل الأكاديمي الشامل عبر ({selected_model})..."): 
                try:
                    reference_text = f"\nاستعن بالمرجع الإضافي التالي إن لزم الأمر:\n{context_content}" if context_content else ""
                    
                    full_prompt = f"""
أنت بروفيسور وعلامة متخصص في الأدب العربي القديم وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.

مطلوب منك تقديم تقرير أكاديمي طويل، مفصل، وموسع ومكتمل الأركان 100% للنص الشعري التالي، وممنوع منعاً باتاً الاختصار أو إغفال أي قسم:
"{user_prompt}"
{reference_text}

تنبيهات صارمة لا تقبل التجاوز:
1. عدّ الأبيات بدقة: قم بعدّ الأبيات المدخلة بدقة (إذا كان المدخل بيتاً واحداً مقسماً لشطرين، اذكر في التقرير أنه "بيت واحد" وممنوع منعاً باتاً وصفه بأنه بيتين).
2. التوثيق التاريخي: حدد قائل النص بدقة والمناسبة التاريخية الصحيحة (إذا كان النص لبيت المتنبي المذكور، اذكر أنه في مدح سيف الدولة الحمداني في العصر العباسي).

يجب أن يحتوي ردك بالتفصيل الكامل على الأقسام الأربعة التالية دون نقص:
أولاً: التوثيق التاريخي والمناسبة الصحيحة بالتفصيل.
ثانياً: الشرح اللغوي المفصل لمعاني المفردات والمعنى الإجمالي والدلالي العميق للبيت.
ثالثاً: التحليل العروضي والموسيقى الخارجية (اكتب إجبارياً: الكتابة العروضية للصدر والعجز، التقطيع بالرموز /0//0، وتعيين البحر بدقة وتحديد تفاعيله الأصيلة في جدول أو نقاط واضحة).
رابعاً: التحليل البلاغي والجمالي (اشرح الاستعارات، الكنايات، والمحسنات البديعية كاملة).
"""
                    
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": full_prompt}],
                        model=selected_model,
                        temperature=0.2,
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
