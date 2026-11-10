import streamlit as st
import os
from groq import Groq

# 1. إعداد الصفحة والواجهة الاحترافية للموقع
st.set_page_config(
    page_title="Smart Critic - الناقد الذكي",
    page_icon="📚",
    layout="centered"
)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.subheader("التحليل الأدبي والعروضي الصارم بالذكاء الاصطناعي الأكاديمي")

# 2. جلب المفتاح تلقائياً من إعدادات الـ Secrets
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if GROQ_API_KEY:
    # 3. واجهة المراجع والملفات
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

    # 4. حقل التوجيهات
    st.write("---")
    st.markdown("### ✍️ 2. توجيهات الناقد الذكي")
    user_prompt = st.text_area(
        "اكتب النص البرومبت (Prompt) أو سؤالك النقدي حول المراجع المرفوعة:",
        value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"
    )

    # 5. معالجة الطلب وعرض النتيجة الكاملة والعروضية
    if st.button("🚀 ابدأ النقد الأدبي والعروضي الموثق"):
        if not user_prompt:
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
        else:
            with st.spinner("🔄 جاري استخراج التحليل الأكاديمي والعروضي الكامل..."): 
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    
                    # برومبت أكاديمي صارم يجبر النموذج على التقطيع العروضي الصحيح
                    full_prompt = f"""
                    أنت بروفيسور وعلامة متخصص في الأدب العربي القديم وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
                    
                    مطلوب منك تقديم تقرير أكاديمي مفصل وصحيح 100% للنص التالي:
                    "{user_prompt}"

                    تنبيهات عروضية وتاريخية حاسمة:
                    1. التوثيق التاريخي: هذا البيت هو لأبي الطيب المتنبي في مدح سيف الدولة الحمداني (العصر العباسي).
                    2. البحر الشعري: البيت من بحر الطويل.
                    3. التفاعيل الأصيلة لبحر الطويل هي: (فعولن مفاعيلن فعولن مفاعلن) في الصدر والبطن.
                    
                    المطلوب منك توليد التقرير مقسماً كالتالي:
                    أولاً: التوثيق التاريخي والمناسبة الصحيحة.
                    ثانياً: الشرح اللغوي والمعنى الإجمالي.
                    ثالثاً: التحليل العروضي والموسيقى الخارجية (يجب أن تكتب بالتفصيل: الكتابة العروضية، التقطيع بالرموز /0//0، والتفاعيل المقابلة لكل شطر بدقة أكاديمية وعلمية).
                    رابعاً: البلاغة والجماليات.
                    """
                    
                    # استدعاء الموديل المستقر والنشط حالياً مع إصلاح سطر الاستدعاء التكراري
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": full_prompt,
                            }
                        ],
                        model="llama-3.1-8b-instant",
                    )
                    
                    st.write("---")
                    st.markdown("### ✨ تقرير الناقد الأكاديمي والعروضي المتكامل:")
                    st.write(chat_completion.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ أثناء المعالجة: {e}")
else:
    st.info("💡 يرجى التأكد من وضع متغير GROQ_API_KEY داخل منطقة الـ Secrets في إعدادات التطبيق.")
