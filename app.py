import streamlit as st
import google.generativeai as genai

# --- 1. 核心配置 ---
st.set_page_config(page_title="意大利合规助手(稳定版)", layout="wide", page_icon="🇮🇹")

# 【请确保此处粘贴的是 B 账户中完整的、AIza 开头的密钥】
API_KEY = "AIzaSyAAGztx9bEcEIyQZ4WRcNbrwMAvb_2g5fw"

# --- 2. 界面设计 ---
st.title("🇮🇹 意大利超市出口合规与包装助手")
st.markdown("---")

with st.sidebar:
    st.header("📋 产品信息录入")
    with st.form("input_form"):
        name = st.text_input("1. 产品名称", placeholder="如：不锈钢吸管杯")
        hs_code = st.text_input("2. HS Code", placeholder="如：961700")
        material = st.text_input("3. 材质成分", placeholder="如：304不锈钢, PP塑料")
        power = st.selectbox("4. 供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("5. 适用人群", ["通用/成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("🚀 生成方案", type="primary")

# --- 3. 核心生成逻辑 ---
if submitted:
    if not name or not hs_code:
        st.error("⚠️ 请填写必要的产品名称和 HS Code。")
    else:
        try:
            # 配置 API
            genai.configure(api_key=API_KEY.strip())
            
            # 使用最基础、兼容性最强的模型调用方式
            # 删除了 models/ 前缀和 tools 联网参数，以确保 100% 能跑通
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner('🤖 正在调取专家知识库，生成合规报告...'):
                prompt = f"""
                作为出口意大利的合规专家，分析以下产品：
                产品：{name}, HS Code: {hs_code}, 材质: {material}, 供电: {power}, 人群: {target}。
                
                请严格按“总-分-总”结构输出：
                1. 准入结论。
                2. 检测项目与EN标准表格。
                3. 包装图标要求。
                4. 中意文对照包装文案。
                5. 纯意大利语复制块。
                """
                response = model.generate_content(prompt)
                
                # 输出结果
                st.markdown(response.text)
                st.success("✅ 报告生成完毕！")
                
        except Exception as e:
            st.error(f"❌ 运行出错：{str(e)}")
            st.info("提示：如果依然显示 404，说明您的账号需要使用 gemini-pro 模型。")
