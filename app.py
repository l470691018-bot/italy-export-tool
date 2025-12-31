import streamlit as st
import google.generativeai as genai

# --- 1. 配置区域 ---
st.set_page_config(page_title="意大利出口合规助手(修正版)", layout="wide", page_icon="🇮🇹")

# 【重要：请确保这里填入的是您在账号 B 中重新生成的、状态正常的 API Key】
API_KEY = "AIzaSyAAGztx9bEcEIyQZ4WRcNbrwMAvb_2g5fw"

def get_gemini_response(prompt):
    """带容错机制的模型调用函数"""
    # 尝试多种模型名称，防止 404 报错
    model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    for m_name in model_names:
        try:
            model = genai.GenerativeModel(m_name, tools=[{'google_search_retrieval': {}}])
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # 如果是模型未找到错误，尝试下一个
            if "not found" in str(e).lower():
                continue
            else:
                raise e
    raise Exception("所有可用模型均无法连接，请检查 API Key 状态。")

# --- 2. 页面与表单 ---
st.title("🇮🇹 意大利超市出口合规与包装助手")
st.info("💡 这是一个实时联网工具。如果报错，请检查 API Key 是否已在 Google AI Studio 激活。")

with st.sidebar:
    st.header("📝 输入产品参数")
    with st.form("main_form"):
        name = st.text_input("1. 产品名称", placeholder="例如：不锈钢保温杯")
        st.markdown("🔗 [HS Code 搜索助手](https://www.baidu.com/s?wd=HS编码查询)")
        hs_code = st.text_input("2. HS Code", placeholder="例如：961700")
        material = st.text_input("3. 材质成分", placeholder="例如：304不锈钢，PP塑料")
        power = st.selectbox("4. 供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("5. 适用人群", ["通用/成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("🚀 生成报告", type="primary")

# --- 3. 逻辑执行 ---
if submitted:
    if not name or not hs_code:
        st.error("请完整填写品名和 HS Code。")
    else:
        try:
            genai.configure(api_key=API_KEY)
            with st.spinner('🔍 正在检索意大利 2025 最新法规...'):
                prompt = f"你作为合规专家，检索意大利法规对{name}(HS:{hs_code},材质:{material},供电:{power},人群:{target})的要求。输出：1.准入结论；2.检测表格；3.包装图标要求；4.中意对照文案；5.纯意文复制块。"
                result = get_gemini_response(prompt)
                st.markdown(result)
                st.success("✅ 报告生成完毕！")
        except Exception as e:
            st.error(f"❌ 运行出错：{str(e)}")
            st.warning("建议：请登录账号 B 的 Google AI Studio，确认 API Key 数量不为 0。")
