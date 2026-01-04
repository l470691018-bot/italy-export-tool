import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 极简 UI 设计 ---
st.set_page_config(page_title="Italy Compliance Tool", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; }
    .stTextInput input, .stSelectbox div { border-radius: 12px !important; border: 1px solid #d2d2d7 !important; }
    .stButton button { border-radius: 12px !important; background-color: #0071e3 !important; color: white !important; font-weight: 500 !important; }
    .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #e5e5e7; }
    h1, h2 { color: #1d1d1f; font-weight: 600; letter-spacing: -0.02em; }
    th { background-color: #fbfbfd !important; color: #86868b !important; font-size: 11px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心逻辑：安全读取与自适应模型 ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY.strip())
except:
    st.error("❌ 密钥未配置：请在 Streamlit 后台 Secrets 中设置 GEMINI_API_KEY。")
    st.stop()

def get_ai_response(prompt):
    # 自动尝试所有可能的模型 ID，彻底解决 404 问题
    model_ids = ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-pro']
    safety = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
              {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
    
    for mid in model_ids:
        try:
            model = genai.GenerativeModel(mid, safety_settings=safety)
            return model.generate_content(prompt).text
        except: continue
    raise Exception("所有可用模型均无法连接，请确认 API Key 权限。")

# --- 3. 极简侧边栏 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("input"):
        p_name = st.text_input("产品名称", placeholder="如：自行车灯")
        hs_code = st.text_input("HS Code", placeholder="851210")
        material = st.text_input("材质成分", placeholder="ABS外壳, 锂电池")
        power = st.selectbox("供电情况", ["含电池", "插电使用", "无供电"])
        target = st.selectbox("适用人群", ["通用", "儿童 (3-14岁)", "婴幼儿"])
        submitted = st.form_submit_button("生成交付方案", type="primary")

# --- 4. 交付逻辑：精准对齐，去冗余 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 请输入品名和 HS Code。")
    else:
        with st.spinner('Preparing Apple-style delivery...'):
            try:
                # 终极提示词：包含物理事实映射、1:1 翻译、全追溯信息
                prompt = f"""
                作为出口意大利超市的准入专家，为产品【{p_name}】提供最终交付文案。
                HS: {hs_code}, 材质: {material}, 供电: {power}, 受众: {target}。

                ### 严格交付指令：
                1. **品类过滤**：如果是电子产品，严禁出现食品图标。只保留相关图标。
                2. **环境标签**：必须为每个部件输出精准材质代码（如 ♺ 05 PP, ♺ 07 OTHER）。
                3. **追溯补全**：进口商/制造商信息必须包含[名称]、[地址]、[邮箱]填空位。
                4. **双语对照**：左侧中文必须是右侧意语的 1:1 翻译，严禁无关废话。

                输出结构：
                1/ 检测要求表（项目/标准/目的）
                2/ 包装交付对照表（位置 | 中文翻译 | 意大利语复制稿）
                """
                result = get_ai_response(prompt)
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
                st.success("✅ 交付文档已就绪。")
            except Exception as e:
                st.error(f"❌ 运行报错：{str(e)}")
