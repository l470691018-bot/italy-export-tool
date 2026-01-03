import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(page_title="意大利合规助手-侦察版", layout="wide")
st.title("🇮🇹 意大利超市出口合规助手 (自适应版)")

# 【请粘贴您 B 账户中那个以 AIza 开头的完整密钥】
API_KEY = "AIzaSyAAGztx9bEcEIyQZ4WRcNbrwMAvb_2g5fw"

# --- 2. 核心逻辑：自动寻找可用模型 ---
def safe_generate(prompt):
    genai.configure(api_key=API_KEY.strip())
    
    # 第一步：侦察。看看你的 Key 到底能用哪些模型
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except Exception as e:
        raise Exception(f"无法获取模型列表，请检查 API Key。错误：{str(e)}")

    if not available_models:
        raise Exception("您的 API Key 没看到任何可用模型，请确认在 AI Studio 中已启用 Gemini API。")

    # 第二步：排序。优先用 1.5-flash，没有就用第一个能用的
    target_model = ""
    for m in available_models:
        if 'gemini-1.5-flash' in m:
            target_model = m
            break
    if not target_model:
        target_model = available_models[0]

    st.write(f"🔍 诊断信息：已自动为您连接模型 `{target_model}`")

    # 第三步：生成内容
    model = genai.GenerativeModel(target_model)
    response = model.generate_content(prompt)
    return response.text

# --- 3. 界面设计 ---
with st.sidebar:
    st.header("📋 产品参数")
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
        st.error("请填入品名和 HS Code")
    else:
        try:
            with st.spinner('正在调取合规专家库...'):
                prompt = f"你是意大利零售准入专家。分析产品：{p_name}(HS:{hs_code},材质:{material},供电:{power},人群:{target})。输出要求：1.结论；2.检测项目表；3.包装图标清单；4.双语对照文案；5.纯意文复制块。"
                result = safe_generate(prompt)
                st.markdown(result)
                st.success("✅ 任务完成！")
        except Exception as e:
            st.error(f"❌ 运行报错：{str(e)}")
            st.info("如果还是 403/404，请确认您的 Google AI Studio 是否设置了结算信息（虽然免费档通常不需要）。")
