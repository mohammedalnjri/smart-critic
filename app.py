import os
import streamlit as st
from google import genai
import pyarabic.araby as araby

# =====================================================================
# 1. الخوارزمية العروضية المطورة للأبيات الكاملة
# =====================================================================
def advanced_arabic_prosody(text):
    if not text.strip():
        return ""
    cleaned_text = araby.strip_tatweel(text).strip()
    vowels = [araby.FATHA, araby.DAMMA, araby.KASRA]
    tanween = [araby.FATHATAN, araby.DAMMATAN, araby.KASRATAN]
    
    prosody_text = []
    i = 0
    while i < len(cleaned_text):
        char = cleaned_text[i]
        next_char = cleaned_text[i+1] if i + 1 < len(cleaned_text) else ""
        next_next_char = cleaned_text[i+2] if i + 2 < len(cleaned_text) else ""
        
        if next_char == araby.SHADDA:
            prosody_text.append("0") 
            if next_next_char in vowels:
                prosody_text.append("1")
                i += 2
            else:
                prosody_text.append("1")
                i += 1
            i += 1
            continue
        elif char in tanween:
            prosody_text.append("0") 
            i += 1
            continue
        elif char == araby.SUKOON:
            prosody_text.append("0")
            i += 1
            continue
        elif char in vowels:
            prosody_text.append("1")
            i += 1
            continue
        elif char in [araby.ALEF, araby.WAW, araby.YEH, araby.ALEF_MAKSURA]:
            if next_char not in vowels and next_char != araby.SHADDA and next_char not in tanween:
                prosody_text.append("0")
        elif char.isspace() or char in ['،', '؛', '.', ':', '-']:
            pass
        i += 1
    return "".join(prosody_text)

# =====================================================================
# 2. الاستعلام البلاغي الموسع للقصائد الطويلة
# =====================================================================
def analyze_full_poem_with_ai(poem_text, api_key):
    if not api_key:
        return "⚠️ رجاءً قم بإدخال مفتاح الـ API في القائمة الجانبية لتفعيل التحليل الذكي."
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        بصفتك بروفيسور وعالم نقد أدبي ومحقق دواوين، قم بتحليل القصيدة التالية تحليلاً أكاديمياً موسعاً وشاملاً لكل الأبيات دون أي اختصار أو إيجاز:
        
        القصيدة الكاملة:
        {poem_text}
        
        المطلوب منك في التقرير:
        1. المدخل الفكري: (شرح السياق العام للقصيدة، الغرض الشعري الرئيسي، والعاطفة المهيمنة).
        2. التحليل التفصيلي والجمعي (بيت ببيت):
           امسك الأبيات بالتتابع، ولكل بيت اذكر:
           - شرح البيت بأسلوب أدبي بليغ.
           - علم البيان والبديع (الصور البيانية كالتشبيه والاستعارة والمحسنات كالجناس والطباق الخاصة بهذا البيت).
        3. التحليل الموسيقي والنقدي العام: (تحديد بحر القصيدة الخليلي، القافية والروي، وتقييم جودة السبك اللغوي وتماسك القصيدة).
        
        يرجى كتابة التحليل بلغة عربية فصحى رفيعة وتنسيقه بعناوين ونقاط واضحة جداً.
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ حدث خطأ أثناء التحليل الأدبي: {str(e)}"

# =====================================================================
# 3. واجهة المستخدم الرسومية للتحليل الكامل
# =====================================================================
st.title("✒️ نظام الناقد الذكي لتحليل وشرح القصائد")
st.caption("أداة أكاديمية متطورة | فكرة وتطوير المبرمج محمد النِجْري ✨")


with st.sidebar:
    st.header("⚙️ إعدادات المحرك")
    api_key = st.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")
    st.markdown("[اضغط هنا للحصول على مفتاحك المجاني](https://google.com)")
    st.divider()
    st.markdown("### 👨‍💻 مطوّر النظام")
    st.info("تمت البرمجة والتطوير بواسطة: المبرمج محمد النِجْري")

st.subheader("📋 اكتب أو الصق القصيدة الكاملة هنا")
default_poem = "عَلى قَدْرِ أهْلِ العَزْمِ تَأتِي العَزائِمُ\nوَتَأتِي عَلَى قَدْرِ الكِرامِ المَكارِمُ"

poem_input = st.text_area("أدخل أبيات القصيدة (كل بيت في سطر منفصل):", value=default_poem, height=250)

if st.button("🚀 ابدأ التحليل الشامل والعميق للقصيدة بالكامل"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 التقطيع الرقمي للأبيات")
        lines = poem_input.split('\n')
        for idx, line in enumerate(lines):
            if line.strip():
                pattern = advanced_arabic_prosody(line)
                st.markdown(f"**البيت {idx+1}:** {line}")
                st.code(f"النمط: {pattern}", language="text")
                st.divider()
                
    with col2:
        st.subheader("🧠 الشرح الأكاديمي والتحليل البلاغي المفصل")
        with st.spinner("جاري قراءة القصيدة بالكامل وتحليل معانيها وصورها البلاغية بيتًا بيتك..."):
            ai_report = analyze_full_poem_with_ai(poem_input, api_key)
            st.markdown(ai_report)

st.divider()
st.write("صُنع بكفاءة برمجية عالية لخدمة لغة الضاد بواسطة المبرمج محمد النِجْري 💻")
