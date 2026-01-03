import streamlit as st
import google.generativeai as genai

# --- 1. 页面设置 ---
st.set_page_config(page_title="意大利合规助手-终极稳定版", layout="wide")

# 【请确保粘贴账号 B 中那个以 AIza 开头的完整密钥】
API_KEY = "AIzaSyAAGztx9bEcEIyQZ4WRcNbrwMAvb_2g5fw"

# --- 2. 核心逻辑：暴力尝试所有可用模型 ---
def get_response_brute_force(prompt):
    # 尝试所有可能的模型名称，总有一个能跑通
    model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    last_error = ""
    
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue # 如果这个模型不行，立刻换下一个
            
    raise Exception(f"所有模型尝试均失败。最后一次报错：{last_error}")

# --- 3. 界面设计 ---
st.title("🇮🇹 意大利超市出口合规助手 (稳定版)")
st.info("提示：如果点击生成后依然报错，请看下方红字的提示。")

with st.sidebar:
    st.header("产品参数录入")
    with st.form("input_form"):
        p_name = st.text_input("品名", placeholder="如：保温杯")
        hs_code = st.text_input("HS Code", placeholder="961700")
        material = st.text_input("材质", placeholder="不锈钢")
        power = st.selectbox("带电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("适用人群", ["成人", "儿童", "婴幼儿"])
        submitted = st.form_submit_button("🚀 生成方案", type="primary")

# --- 4. 运行 ---
if submitted:
    if not p_name or not hs_code:
        st.error("请完整填写品名和 HS Code")
    else:
        try:
            genai.configure(api_key=API_KEY.strip())
            with st.spinner('正在调取合规专家库...'):
                prompt = f"你是意大利零售准入专家。分析产品：{p_name}(HS:{hs_code},材质:{material},供电:{power},人群:{target})。输出：1.结论；2.检测项目表；3.包装图标；4.双语对照文案；5.纯意文复制块。"
                result = get_response_brute_force(prompt)
                st.markdown(result)
                st.success("✅ 生成成功！")
        except Exception as e:
            st.error(f"❌ 最终尝试失败：{str(e)}")
            st.warning("如果看到 API_KEY_INVALID，说明 Key 复制错了；如果看到 404，请联系我更换模型库。")
