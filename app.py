import streamlit as st
import google.generativeai as genai

# 已为您整合提供的 API KEY
API_KEY = "AIzaSyA4vCg-1_MmH7_Wbq5JJIcjzpmih-2qqw8"

# 配置 Gemini 模型
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash', tools=[{'google_search_retrieval': {}}])

st.set_page_config(page_title="意大利超市合规助手", layout="wide")
st.title("🇮🇹 意大利超市出口合规与包装生成器")
st.markdown("---")

# 输入表单
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("产品品名", placeholder="如：Tritan水杯")
    with col2:
        hs_code = st.text_input("HS Code", placeholder="392410")
    with col3:
        material = st.text_input("核心材质", placeholder="Tritan塑料")
    
    submitted = st.button("🚀 生成合规报告 & 设计师包装方案")

if submitted:
    if not name or not hs_code:
        st.warning("请至少输入品名和 HS Code。")
    else:
        with st.spinner('正在检索 2025 意大利最新法律法规...'):
            prompt = f"""
            你现在是意大利零售渠道准入专家。
            请针对产品：{name}, HS Code: {hs_code}, 材质: {material}，进行深度检索并回答。
            要求采用“总-分-总”结构：
            1. 【准入结论】简述进入意大利超市的门槛和核心风险。
            2. 【检测清单】表格形式列出必须进行的检测项目、EN标准、所需证书。
            3. 【设计师专用：图标清单】明确列出包装必须出现的图标（如CE, MOCA高脚杯叉子, PAP回收标识等）。
            4. 【包装文案区】提供中意对照表。
            5. 【纯意文复制块】提供一段完整的、符合意大利法规要求的包装纯文本，方便设计师直接粘贴。
            """
            response = model.generate_content(prompt)
            st.markdown(response.text)