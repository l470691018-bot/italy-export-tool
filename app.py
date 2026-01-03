import streamlit as st
import google.generativeai as genai

# --- 1. 初始化与安全配置 ---
st.set_page_config(page_title="意大利合规助手-终极交付版", layout="wide")
st.title("🇮🇹 意大利超市出口合规助手")

# 从后台 Secrets 安全读取 Key
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 报错：未在网页后台检测到 GEMINI_API_KEY！")
    st.info("请在 Streamlit Cloud 的 Settings -> Secrets 中添加您的密钥。")
    st.stop()

# --- 2. 核心函数：确保内容 100% 输出 ---
def get_report(prompt):
    # 关闭所有安全拦截，防止内容因涉及法律被拦截
    safety = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    ]
    
    # 自动搜索可用模型名
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target = next((m for m in models if 'gemini-1.5-flash' in m), models[0])
    
    model = genai.GenerativeModel(model_name=target, safety_settings=safety)
    response = model.generate_content(prompt)
    return response.text

# --- 3. 界面设计 ---
with st.sidebar:
    st.header("📋 填写产品信息")
    with st.form("input_form"):
        p_name = st.text_input("品名", placeholder="如：不锈钢杯")
        hs_code = st.text_input("HS Code", placeholder="961700")
        material = st.text_input("材质", placeholder="304不锈钢")
        power = st.selectbox("带电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("适用人群", ["成人", "儿童", "婴幼儿"])
        submitted = st.form_submit_button("🚀 生成报告", type="primary")

# --- 4. 总-分-总 逻辑输出 ---
if submitted:
    if not p_name or not hs_code:
        st.error("⚠️ 品名和 HS Code 必填！")
    else:
        with st.spinner('🔍 正在检索意大利 2026 最新标准并生成表格...'):
            try:
                # 强化 Prompt：确保表格不乱码
                prompt = f"""
                作为出口意大利超市的合规专家，请分析：{p_name}(HS:{hs_code}, 材质:{material}, 供电:{power}, 人群:{target})。
                
                请严格按此结构输出，不要省略任何细节：
                1. 【总】：一句话给结论。
                2. 【分】：
                   - 用标准表格列出 3-5 项检测项目、EN标准号。
                   - 用标准表格列出包装必须包含的中意双语对照文案。
                   - 列出包装必须印刷的图标。
                3. 【总】：提供一段方便复制的纯意大利语文本块，包含材质回收标识代码。
                """
                result = get_report(prompt)
                st.markdown(result)
                st.success("✅ 报告生成完毕")
            except Exception as e:
                st.error(f"❌ 运行中出现错误：{str(e)}")
