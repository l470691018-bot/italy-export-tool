import streamlit as st
import google.generativeai as genai

# --- 1. 配置区域 ---
st.set_page_config(page_title="意大利合规助手-安全版", layout="wide")
st.title("🇮🇹 意大利超市出口合规助手")

# 从 Streamlit 后台安全读取 API Key
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("⚠️ 未检测到安全密钥！请在 Streamlit Cloud 后台配置 GEMINI_API_KEY。")
    st.stop()

# --- 2. 核心函数 ---
def get_clean_response(prompt):
    # 自动获取可用模型
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target = next((m for m in models if 'gemini-1.5-flash' in m), models[0])
    model = genai.GenerativeModel(target)
    return model.generate_content(prompt).text

# --- 3. 界面设计 ---
with st.sidebar:
    st.header("📋 产品参数")
    with st.form("input_form"):
        p_name = st.text_input("品名", placeholder="如：不锈钢杯")
        hs_code = st.text_input("HS Code", placeholder="961700")
        material = st.text_input("材质", placeholder="304不锈钢")
        power = st.selectbox("带电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("适用人群", ["成人", "儿童", "婴幼儿"])
        submitted = st.form_submit_button("🚀 生成报告", type="primary")

# --- 4. 逻辑执行 ---
if submitted:
    if not p_name or not hs_code:
        st.error("请填入必填项")
    else:
        with st.spinner('🔍 正在生成无乱码合规报告...'):
            try:
                prompt = f"""
                作为意大利准入专家，分析：{p_name}(HS:{hs_code},材质:{material},供电:{power},人群:{target})。
                要求：
                1. 严格总-分-总结构。
                2. 必须输出标准 Markdown 表格，确保行列对齐。
                3. 提供中意文对照包装文案。
                4. 提供纯意大利语复制块。
                """
                result = get_clean_response(prompt)
                # 使用 Markdown 容器确保表格排版
                st.markdown(result)
                st.success("✅ 生成完毕")
            except Exception as e:
                st.error(f"运行出错：{str(e)}")
