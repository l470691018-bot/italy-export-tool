import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 极简 UI 设计 ---
st.set_page_config(page_title="Italy Export Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; color: #1d1d1f; }
    .stTextInput input, .stSelectbox div, .stButton button { border-radius: 12px !important; border: 1px solid #d2d2d7 !important; }
    .stButton button { background-color: #0071e3 !important; color: white !important; font-weight: 500 !important; width: 100%; border: none !important; }
    .card { background: white; padding: 2.5rem; border-radius: 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #e5e5e7; margin-top: 1.5rem; }
    h1, h2, h3 { font-weight: 600; letter-spacing: -0.02em; border: none !important; }
    th { background-color: #fbfbfd !important; color: #86868b !important; font-size: 11px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 诊断模块：在页面上直接告知状态 ---
def initialize_engine():
    try:
        # 严格从后台 Secrets 物理隔离读取
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("❌ 诊断：Secrets 中未找到 'GEMINI_API_KEY'。请检查控制台后台配置。")
            st.stop()
        
        raw_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=raw_key)
        
        # 自动尝试所有模型变体，解决 404 报错
        variants = ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-flash']
        for v in variants:
            try:
                model = genai.GenerativeModel(v)
                # 预检
                model.generate_content("ping", generation_config={"max_output_tokens": 1})
                return model
            except: continue
        raise Exception("所有路径均无法连接 (可能 Key 再次被 Google 历史记录封禁)")
    except Exception as e:
        st.error(f"❌ 引擎失效: {str(e)}")
        st.info("提示：若报 403 泄露，请在 AI Studio 重新生成一个'全新项目'下的 Key，且严禁贴入任何代码位置。")
        st.stop()

# --- 3. 极简侧边栏与输入 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("main_form"):
        p_name = st.text_input("产品品名", placeholder="如：不锈钢咖啡杯")
        hs_code = st.text_input("海关编码", placeholder="如：961700")
        material = st.text_input("材质成分", placeholder="如：304不锈钢, PP盖")
        power = st.selectbox("供电情况", ["无供电", "含电池", "插电使用"])
        target = st.selectbox("人群划分", ["通用/成人", "儿童 (3-14岁)", "婴幼儿"])
        submitted = st.form_submit_button("一键生成交付方案")

# --- 4. 交付结果执行 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 基础参数缺失，无法判断合规逻辑。")
    else:
        model = initialize_engine()
        with st.spinner('Preparing Apple-style delivery documents...'):
            try:
                # 强化版 Prompt：强制事实/1:1 翻译/全追溯信息
                prompt = f"""
                作为出口意大利超市渠道的合规交付专家。分析产品：{p_name}, HS: {hs_code}, 材质: {material}, 供电: {power}, 人群: {target}。
                
                直接输出以下表格：
                1/ 检测要求表 (2026最新标准)
                2/ 包装交付对照表 (模块位置 | 中文翻译/审核用 | 意大利语/直接复制)
                
                注意：
                - 物理参数：必须基于材质 {material} 事实。如果是 PETG，耐温上限必须锁定为 60°C。
                - 环境标签：各部件必须有材质码（如 ♺ 01 PET, ♺ 05 PP）。
                - 责任实体：进口商/制造商信息含 [公司名]、[地址]、[邮箱/电话] 完整位。
                - 逻辑过滤：自行车灯等非食品类绝对禁止出现食品图标。
                """
                response = model.generate_content(prompt)
                st.markdown(f'<div class="card">{response.text}</div>', unsafe_allow_html=True)
                st.success("✅ 交付方案已就绪。")
            except Exception as e:
                st.error(f"❌ 运行异常: {str(e)}")
