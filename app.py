import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 极简视觉 ---
st.set_page_config(page_title="Italy Export Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; }
    .stTextInput input, .stSelectbox div, .stButton button { border-radius: 12px !important; }
    .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-top: 20px; }
    h1, h2 { color: #1d1d1f; font-weight: 600; border: none !important; }
    th { background-color: #fbfbfd !important; color: #86868b !important; font-size: 11px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 稳健的模型连接逻辑 ---
try:
    # 强制从 Secrets 读取，不给泄露留机会
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY.strip())
except:
    st.error("❌ 密钥缺失：请在 Streamlit 后台 Secrets 中配置 GEMINI_API_KEY。")
    st.stop()

def get_delivery_response(prompt):
    # 自动探测所有可用路径，解决 404 顽疾
    for m_name in ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-flash']:
        try:
            model = genai.GenerativeModel(m_name, safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ])
            return model.generate_content(prompt).text
        except: continue
    raise Exception("API 连接失败，请确认 Key 状态。")

# --- 3. 极简侧边栏 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("input"):
        p_name = st.text_input("产品品名", placeholder="如：不锈钢咖啡杯")
        hs_code = st.text_input("海关编码", placeholder="961700")
        material = st.text_input("核心材质", placeholder="如：304不锈钢, PP盖")
        power = st.selectbox("带电情况", ["无供电", "含电池", "插电使用"])
        target = st.selectbox("人群划分", ["成人", "儿童 (3-14岁)", "婴幼儿"])
        submitted = st.form_submit_button("生成交付方案", type="primary")

# --- 4. 精准交付逻辑 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 基础参数缺失。")
    else:
        with st.spinner('Preparing delivery documents...'):
            try:
                # 强化版指令：事实映射、1:1 对齐、完整追溯
                prompt = f"""
                作为出口意大利合规专家。分析：{p_name}, HS:{hs_code}, 材质:{material}, 供电:{power}, 人群:{target}。
                要求：
                1. 物理事实：基于 {material} 材质事实（如 PETG 必须标为 60°C）。
                2. 环境标签：各部件必须有材质码（如 ♺ 05 PP）。
                3. 责任实体：包含 [公司名]、[完整地址]、[邮箱/电话] 填空位。
                4. 翻译对齐：中文列必须是意大利语的 1:1 翻译。
                
                直接输出：
                - 检测项目表格 (项目/标准/目的)
                - 包装交付对照表 (位置 | 中文审核 | 意大利语复制稿)
                """
                result = get_delivery_response(prompt)
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
                st.success("✅ 方案生成完毕。")
            except Exception as e:
                st.error(f"❌ 系统错误：{str(e)}")
