import streamlit as st
import os
import time
from google import genai
from google.genai.errors import APIError

# 1. إعداد الصفحة والواجهة الاحترافية للموقع
st.set_page_config(
    page_title="Smart Critic - الناقد الذكي",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 منصة الناقد الذكي - Smart Critic")
st.subheader("تحليل ونقد النصوص والمراجع العربية بالذكاء الاصطناعي")

# 2. إعداد مفتاح API الخاص بـ Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("أدخل مفتاح Gemini API المجاني الخاص بك:", type="password")

if GEMINI_API_KEY:
    # 3. قسم رفع المراجع والملفات العربية
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

    # 4. قسم كتابة الأوامر والنقد (مع تثبيت البيت الشعري بالتشكيل الكامل)
    st.write("---")
    st.markdown("### ✍️ 2. توجيهات الناقد الذكي")
    user_prompt = st.text_area(
        "اكتب النص البرومبت (Prompt) أو سؤالك النقدي حول المراجع المرفوعة:",
        value="عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"
    )

    # 5. معالجة الطلب الآمن والمباشر بدون رسائل جانبية وبدعم إعادة المحاولة عند الضغط
    if st.button("🚀 ابدأ التحليل والنقد الفوري"):
        if not user_prompt:
            st.error("الرجاء كتابة التوجيه أو السؤال أولاً!")
        else:
            # استخدام شريط التحميل الأصلي لـ Streamlit فقط وبدون أي نصوص برمجية إضافية
            with st.spinner(""): 
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                full_prompt = f"""
                أنت خبير ناقد أكاديمي متخصص في الأدب العربي.
                السياق أو المرجع المتاح: {context_content if context_content else 'اعتمد على معارفك الأدبية العامة.'}
                المطلوب منك: قم بتحليل ونقد النص التالي نقداً أدبياً وبلاغياً وافياً بأسلوب فصيح وممتاز: {user_prompt}
                """
                
                # نظام ذكي لإعادة المحاولة 3 مرات تلقائياً في حال كان خادم جوجل مضغوطاً (خطأ 503)
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=full_prompt,
                        )
                        # إذا نجح الطلب، اعرض النتيجة فوراً واكسر التكرار
                        st.write("---")
                        st.markdown("### ✨ النتيجة والنقد المستخرج:")
                        st.write(response.text)
                        break
                    except APIError as e:
                        # إذا كان الخطأ بسبب الضغط (503) ولم ننتهِ من المحاولات، انتظر ثانية وأعد المحاولة
                        if e.code == 503 and attempt < max_retries - 1:
                            time.sleep(1.5)
                            continue
                        else:
                            st.error(f"⚠️ الخادم مشغول حالياً بسبب ضغط الطلبات العالي، يرجى النقر مرة أخرى بعد لحظات. (تفاصيل: {e.message})")
                            break
                    except Exception as e:
                        st.error(f"⚠️ تفاصيل الخطأ: {e}")
                        break
else:
    st.info("💡 للبدء، يرجى إدخل مفتاح Gemini API في القائمة الجانبية أو ضبطه كمتغير بيئي (Environment Variable).")
