import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 极简视觉方案 ---
st.set_page_config(page_title="Italy Export Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; }
    .stTextInput input, .stSelectbox div, .stButton button { border-radius: 12px !important; }
    .stButton button { background-color: #0071e3 !important; color: white !important; font-weight: 500 !important; width: 100%; border: none !important; }
    .card { background: white; padding: 2.5rem; border-radius: 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #e5e5e7; margin-top: 1.5rem; }
    h1, h2 { font-weight: 600; letter-spacing: -0.02em; border: none !important; }
    th { background-color: #fbfbfd !important; color: #86868b !important; font-size: 11px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 诊断与连接模块 ---
try:
    # 严格从 Secrets 读取
    RAW_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=RAW_KEY.strip())
except Exception as e:
    st.error("❌ 钥匙还没放进保险箱：请在 Streamlit 后台 Secrets 中配置 GEMINI_API_KEY")
    st.stop()

def get_delivery_content(prompt):
    # 自动尝试所有模型变体，彻底解决 404
    model_variants = ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-flash']
    safety = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
              {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
    
    for m_name in model_variants:
        try:
            model = genai.GenerativeModel(m_name, safety_settings=safety)
            return model.generate_content(prompt).text
        except Exception as e:
            last_err = str(e)
            continue
    raise Exception(f"连接失败。具体原因: {last_err}")

# --- 3. 极简侧边栏 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("input"):
        p_name = st.text_input("产品品名", placeholder="例如：PETG 运动水杯")
        hs_code = st.text_input("海关编码", placeholder="例如：392410")
        material = st.text_input("核心材质", placeholder="例如：PETG, PP, 硅胶")
        power = st.selectbox("供电情况", ["无供电", "含电池", "插电使用"])
        target = st.selectbox("人群划分", ["通用/成人", "儿童 (3-14岁)", "婴幼儿"])
        submitted = st.form_submit_button("一键生成交付方案")

# --- 4. 极致交付逻辑执行 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 基础参数缺失，无法判断合规逻辑。")
    else:
        with st.spinner('Preparing Apple-style delivery documents...'):
            try:
                # 强化版 Prompt：强制物理事实 + 1:1 双语对照 + GPSR 补全
                prompt = f"""
                作为出口意大利超市渠道的合规交付专家。分析产品：{p_name}, HS: {hs_code}, 材质: {material}, 供电: {power}, 人群: {target}。
                
                请直接输出以下内容，禁止任何解释：
                1/ 检测要求表（项目/2026标准/目的）
                
                2/ 包装交付对照表（位置 | 中文翻译/审核 | 意大利语/直接复制）
                
                **注意：**
                - 物理参数：必须基于材质 {material} 事实。如果是 PETG，耐温上限必须锁定为 60°C。
                - 标识过滤：自行车灯等非食品类严禁出现🍷🍴图标。
                - 追溯信息：进口商/制造商信息需包含[名称]、[地址]、[邮箱/电话]完整位。
                - 环境标签：各部件必须有材质码（如 ♺ 01 PET, ♺ 05 PP）。
                """
                result = get_delivery_content(prompt)
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
                st.success("✅ 方案生成完毕。")
            except Exception as e:
                st.error(f"❌ 运行报错: {str(e)}")
