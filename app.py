import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 极简视觉 ---
st.set_page_config(page_title="Italy Export Tool", layout="wide", page_icon="🇮🇹")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; color: #1d1d1f; }
    .stTextInput input, .stSelectbox div, .stButton button { border-radius: 12px !important; border: 1px solid #d2d2d7 !important; }
    .stButton button { background-color: #0071e3 !important; color: white !important; font-weight: 500 !important; border: none !important; }
    .card { background: white; padding: 2.5rem; border-radius: 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #e5e5e7; margin-top: 1.5rem; }
    h1, h2, h3 { font-weight: 600; letter-spacing: -0.02em; border: none !important; }
    th { background-color: #fbfbfd !important; color: #86868b !important; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 安全读取与自适应模型连接 ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY.strip())
except Exception:
    st.error("❌ 密钥未配置：请在 Streamlit 后台 Secrets 中设置 GEMINI_API_KEY。")
    st.stop()

def get_pro_content(prompt):
    # 自动探测所有模型路径变体，解决 404 报错
    model_ids = ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    safety = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
              {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
    for mid in model_ids:
        try:
            model = genai.GenerativeModel(mid, safety_settings=safety)
            return model.generate_content(prompt).text
        except: continue
    raise Exception("所有可用模型均无法连接，请检查密钥权限。")

# --- 3. 极简交互界面 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("input"):
        p_name = st.text_input("产品名称", placeholder="如：自行车灯 / PETG水杯")
        hs_code = st.text_input("海关编码", placeholder="如：851210 / 392410")
        material = st.text_input("核心材质", placeholder="如：ABS, 锂电池 / PETG, PP")
        power = st.selectbox("供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("人群划分", ["成人", "儿童 (3-14岁)", "婴幼儿"])
        submitted = st.form_submit_button("生成交付方案", type="primary")

# --- 4. 极致交付逻辑 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 请填入必填项。")
    else:
        with st.spinner('Preparing professional delivery...'):
            try:
                # 强化版指令：1:1 对齐、物理事实映射、GPSR 追溯补全
                prompt = f"""
                作为出口意大利专家。针对产品：{p_name}, HS: {hs_code}, 材质: {material}, 供电: {power}, 受众: {target}。
                1/ 检测要求表：项目 | 标准 | 目的。
                2/ 包装交付对照表：位置 | 中文(审核) | 意文(设计师复制)。
                要求：
                - 物理参数：基于 {material} 材质事实（如 PETG 必须标为 60°C）。
                - 环境标签：各部件必须含材质码（如 ♺ 01 PET）。
                - 企业追溯：含[公司名]、[地址]、[邮箱/电话]完整位。
                - 绝对过滤：电子产品严禁出现食品图标。
                """
                result = get_pro_content(prompt)
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
                st.success("✅ 交付文档已就绪。")
            except Exception as e:
                st.error(f"❌ 系统错误：{str(e)}")
