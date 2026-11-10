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
st.markdown("<p style='font-size: 1.2rem; color: #4A90E2; font-weight: bold; margin-top: -15px;'>🎨 تصميم المبرمج محمد النجري</p>", unsafe_allow_html=True)
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
        "💡 أدخل البيت الشعري في سطرين متتاليين (الصدر ثم العجز)، أو الصق قصيدتك كاملة في المربع أدناه:",
        value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"
    )

    # 5. معالجة الطلب وعرض النتيجة الكاملة والعروضية
    if st.button("🚀 ابدأ النقد الأدبي والعروضي الموثق"):
        if not user_prompt:
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
        else:
            with st.spinner("🔄 جاري استخراج التحليل الأكاديمي الشامل..."): 
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    
                    full_prompt = f"""
                    أنت بروفيسور وعلامة متخصص في الأدب العربي القديم وعلم العروض والقافية وفق مدرسة الخليل بن أحمد الفراهيدي.
                    اكتب تقريراً أكاديمياً شاملاً ومكتمل الأركان ومباشر وبدون جمل مقدمات طويلة للنص الشعري التالي:
                    "{user_prompt}"

                    الشروط الصارمة:
                    1. التوثيق: البيت لأبي الطيب المتنبي في مدح سيف الدولة الحمداني (العصر العباسي)، والعدد هو بيت واحد فقط.
                    2. العروض: البيت من بحر الطويل، تفاعيله (فعولن مفاعيلن فعولن مفاعلن) في الصدر والبطن.
                    
                    الأقسام المطلوبة بالاختصار المفيد المكتمل:
                    أولاً: التوثيق التاريخي والمناسبة.
                    ثانياً: الشرح اللغوي والمعنى الإجمالي.
                    ثالثاً: التحليل العروضي كاملاً بالتفصيل (الكتابة العروضية للصدر والعجز، التقطيع بالرموز /0//0، وتعيين التفعيلات الأصيلة لبحر الطويل كاملة في نقاط أو جدول واضح).
                    رابعاً: التحليل البلاغي والجماليات.
                    """
                    
                    # استخدام الطراز الافتراضي المستقر والمتاح دائماً للحسابات
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "user", "content": full_prompt}
                        ],
                        model="llama3-70b-8192",
                        temperature=0.2,
                        max_tokens=2000
                    )
                    
                    st.write("---")
                    st.markdown("### ✨ تقرير الناقد الأكاديمي والعروضي المتكامل:")
                    st.write(chat_completion.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ أثناء المعالجة: {e}")
else:
    st.info("💡 يرجى التأكد من وضع متغير GROQ_API_KEY داخل منطقة الـ Secrets في إعدادات التطبيق.")
