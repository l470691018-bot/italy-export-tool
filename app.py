import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 视觉设计 ---
st.set_page_config(page_title="Italy Export Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; }
    .stTextInput input, .stSelectbox div, .stButton button { border-radius: 12px !important; }
    .card { background: white; padding: 2.5rem; border-radius: 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #e5e5e7; margin-top: 1.5rem; }
    .stButton button { background-color: #0071e3 !important; color: white !important; width: 100%; border: none !important; }
    th { background-color: #fbfbfd !important; color: #86868b !important; text-transform: uppercase; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 自诊断与安全连接模块 ---
def initialize_engine():
    try:
        # 强制从后台 Secrets 读取
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("📋 诊断信息：Secrets 中未找到 'GEMINI_API_KEY'，请检查后台配置。")
            st.stop()
        
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
        
        # 自动探测模型路径变体
        model_paths = ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-flash']
        for path in model_paths:
            try:
                model = genai.GenerativeModel(path)
                # 预检：尝试极小量生成
                model.generate_content("ping", generation_config={"max_output_tokens": 1})
                return model
            except:
                continue
        raise Exception("所有模型路径均不可用 (404/403)")
    except Exception as e:
        st.error(f"❌ 引擎连接失败: {str(e)}")
        st.info("提示：如果是 403 错误，请在 AI Studio 重新生成一个'全新项目'下的 Key。")
        st.stop()

# --- 3. 极简侧边栏与输入 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("input_area"):
        p_name = st.text_input("产品品名", placeholder="如：不锈钢水杯")
        hs_code = st.text_input("海关编码", placeholder="392410")
        material = st.text_input("材质成分", placeholder="如：304不锈钢, PP")
        power = st.selectbox("带电情况", ["无供电", "含电池", "插电使用"])
        target = st.selectbox("人群划分", ["通用", "儿童 (3-14岁)", "婴幼儿"])
        submitted = st.form_submit_button("一键生成交付稿")

# --- 4. 核心交付逻辑 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 请填入必填参数。")
    else:
        model = initialize_engine()
        with st.spinner('Preparing delivery documents...'):
            try:
                prompt = f"""
                作为出口意大利合规交付专家。分析：{p_name}, HS: {hs_code}, 材质: {material}。
                请直接输出以下两个模块，严禁解释：
                1/ 检测要求表 (2026版标准)
                2/ 包装交付对照表 (位置 | 中文翻译/审核 | 意大利语/直接复制)
                
                要求：
                - 物理参数：基于材质 {material} 事实映射（如 PETG 不超 60°C）。
                - 环境标签：各部件须有材质码（如 ♺ 01 PET）。
                - 追溯信息：包含 [公司名]、[地址]、[邮箱/电话] 完整位。
                - 自动过滤：非食品类绝对禁止出现食品图标。
                """
                response = model.generate_content(prompt)
                st.markdown(f'<div class="card">{response.text}</div>', unsafe_allow_html=True)
                st.success("✅ 方案生成完毕。")
            except Exception as e:
                st.error(f"运行异常: {str(e)}")
