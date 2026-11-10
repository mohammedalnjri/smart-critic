import streamlit as st
import os
import google.generativeai as genai

# 1. إعداد الصفحة والواجهة الاحترافية للموقع
st.set_page_config(
    page_title="Smart Critic - الناقد الذكي الأكاديمي",
    page_icon="📚",
    layout="centered"
)

st.title("📚 منصة الناقد الذكي - Smart Critic")
st.subheader("التحليل الأدبي والعروضي الصارم بالذكاء الاصطناعي")

# 2. جلب مفتاح سري موحد ومستقر من إعدادات الـ Secrets لعدم ضياعه
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

if GEMINI_API_KEY:
    try:
        # تهيئة مكتبة جوجل المستقرة
        genai.configure(api_key=GEMINI_API_KEY)
        
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

        # 4. حقل التوجيهات مع البيت المشكّل كتابةً وصياغةً بشكل صحيح تماماً
        st.write("---")
        st.markdown("### ✍️ 2. النص المراد نقده وتحليله عروضياً")
        user_prompt = st.text_area(
            "أدخل النص الشعري أو النثري:",
            value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"
        )

        # 5. المعالجة الأكاديمية الصارمة عبر عملاق جوجل التوليدي
        if st.button("🚀 ابدأ النقد الأدبي والعروضي الموثق"):
            if not user_prompt:
                st.error("الرجاء كتابة النص أولاً!")
            else:
                with st.spinner("🔄 جاري الاتصال بالخادم واستخراج التحليل الأكاديمي..."): 
                    try:
                        # صياغة توجيه هندسي صارم يمنع التخريف والأخطاء الفاضحة والخلط التاريخي
                        full_prompt = f"""
                        أنت بروفيسور وعالم علامة متخصص في علوم الأدب العربي، النقد الأكاديمي، وعلم العروض والقافية للشعر العربي القديم.
                        
                        مطلوب منك نقد النص التالي نقداً علمياً صارماً لا يحتمل الخطأ أو التخمين:
                        "{user_prompt}"
                        
                        السياق الإضافي المحمل (إن وجد): {context_content}
                        
                        التزم بالنقاط التالية بدقة بالغة وبأسلوب فصيح:
                        1. التوثيق التاريخي: حدد قائل النص بدقة والمناسبة التاريخية الصحيحة (مثال: هذا البيت لأبي الطيب المتنبي من قصيدته الشهيرة في مدح سيف الدولة الحمداني التي مطلعها "عذيرك من أشفاقك المتلفت").
                        2. الشرح اللغوي والبلاغي: اشرح مفردات البيت (العزم، العزائم، الكرام، المكارم)، ثم وضح المعنى الإجمالي والمجاز والتشبيه والمحسنات البديعية (مثل المقابلة والطباق والالتفات).
                        3. التحليل العروضي والموسيقي: قم بتقطيع الأبيات شعرياً، حدد البحر الشعري بدقة وعلمية (بحر الطويل)، واذكر تفعيلاته المقابلة الأصيلة (فعولن مفاعيلن فعولن مفاعيلن) وعيّن العروض والضرب والحشو والزحافات إن وجدت.
                        """
                        
                        # استخدام النموذج الموسوعي الأقوى والأسرع في اللغة العربية
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        response = model.generate_content(full_prompt)
                        
                        st.write("---")
                        st.markdown("### ✨ تقرير الناقد الأكاديمي الموثق:")
                        st.write(response.text)
                        
                    except Exception as e:
                        st.error(f"⚠️ حدث خطأ أثناء المعالجة: {e}")
    except Exception as e:
        st.error(f"خطأ في تهيئة المكتبة: {e}")
else:
    st.info("💡 يرجى وضع مفتاح GEMINI_API_KEY في الـ Secrets أو القائمة الجانبية لتشغيل المحرك الأكاديمي الموثق.")
