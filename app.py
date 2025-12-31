import streamlit as st
import google.generativeai as genai

# --- 1. 基础配置 ---
st.set_page_config(page_title="意大利出口合规专家", layout="wide")

# 【此处粘贴您 B 账户中完整的 API Key】
API_KEY = "AIzaSyAAGztx9bEcEIyQZ4WRcNbrwMAvb_2g5fw"

def call_gemini(prompt):
    """自适应模型调用逻辑，解决 404 问题"""
    # 尝试不同的模型名称写法
    test_models = ['gemini-1.5-flash', 'models/gemini-1.5-flash']
    last_err = ""
    
    for model_name in test_models:
        try:
            # 尝试开启联网搜索
            model = genai.GenerativeModel(model_name, tools=[{'google_search_retrieval': {}}])
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_err = str(e)
            try:
                # 如果联网搜索报错，尝试标准模式
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except:
                continue
    raise Exception(f"模型连接失败。原始错误：{last_err}")

# --- 2. 页面设计 ---
st.title("🇮🇹 意大利超市出口合规助手")
st.info("💡 填入信息后点击生成。如果持续报错，请检查 API Key 复制是否包含空格。")

with st.sidebar:
    st.header("📋 产品参数输入")
    with st.form("main_form"):
        name = st.text_input("1. 产品名称", placeholder="如：不锈钢保温杯")
        
        # 跳转按钮：HS Code 搜索
        st.markdown('<a href="https://www.baidu.com/s?wd=HS编码查询" target="_blank"><button style="cursor:pointer;background-color:#007bff;color:white;border:none;padding:8px 15px;border-radius:5px;width:100%">🔍 没编码？点此去百度搜</button></a>', unsafe_allow_html=True)
        
        hs_code = st.text_input("2. HS Code", placeholder="如：961700")
        material = st.text_input("3. 材质成分", placeholder="如：304不锈钢")
        power = st.selectbox("4. 供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("5. 适用人群", ["通用/成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("🚀 生成方案报告", type="primary")

# --- 3. 业务逻辑执行 ---
if submitted:
    if not name or not hs_code:
        st.error("⚠️ 品名和 HS Code 是必填项。")
    else:
        try:
            genai.configure(api_key=API_KEY.strip()) # 自动去除可能存在的空格
            with st.spinner('🤖 正在联网检索 2025 意大利最新法规...'):
                prompt = f"""
                你现在是意大利零售准入专家。针对产品：{name}, HS Code: {hs_code}, 材质: {material}, 供电: {power}, 人群: {target}。
                请严格按照“总-分-总”形式输出：
                1. 总：给出准入结论。
                2. 分：
                   - 用【表格】罗列检测项目及标准。
                   - 用【表格】罗列包装必印的中意文案。
                   - 罗列包装必须呈现的【图标清单】。
                3. 总：提供一段【纯意文复制块】，方便设计师直接使用。
                """
                result = call_gemini(prompt)
                st.markdown(result)
                st.success("✅ 报告生成完毕！")
        except Exception as e:
            st.error(f"❌ 运行报错：{str(e)}")
            st.warning("提示：如果看到 API_KEY_INVALID，请重新去 AI Studio 复制。")
