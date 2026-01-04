import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 视觉设计 ---
st.set_page_config(page_title="Italy Compliance Pro", layout="wide", page_icon="🇮🇹")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; }
    .stTextInput, .stSelectbox, .stButton button { border-radius: 12px !important; }
    h1, h2, h3 { color: #1d1d1f; font-weight: 600; border: none; }
    .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-top: 20px; }
    table { width: 100%; border-radius: 12px; overflow: hidden; border: none !important; }
    th { background-color: #fbfbfd !important; color: #86868b !important; text-transform: uppercase; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 深度稳健的模型连接逻辑 ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY.strip())
except:
    st.error("❌ 未检测到 Secrets 密钥！请在 Streamlit 后台配置 GEMINI_API_KEY。")
    st.stop()

def get_delivery_content(prompt):
    # 自动探测可用模型路径，彻底解决 404 问题
    model_variants = ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-flash']
    safety = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
              {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
    
    for m_name in model_variants:
        try:
            model = genai.GenerativeModel(model_name=m_name, safety_settings=safety)
            return model.generate_content(prompt).text
        except: continue
    raise Exception("API 响应失败，请检查 Key 是否在 AI Studio 中生效。")

# --- 3. 极简交互界面 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("input_form"):
        p_name = st.text_input("产品名称", placeholder="如：PETG运动水杯")
        hs_code = st.text_input("HS Code", placeholder="392410")
        material = st.text_input("材质成分", placeholder="如：PETG杯身, PP盖, 硅胶圈")
        power = st.selectbox("供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("适用人群", ["成人", "儿童 (3-14岁)", "婴幼儿"])
        submitted = st.form_submit_button("生成交付方案", type="primary")

# --- 4. 极致交付逻辑 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 请填写品名和 HS Code。")
    else:
        with st.spinner('Preparing Apple-style delivery documents...'):
            try:
                # 终极 Prompt：基于材质事实，1:1 对齐翻译，填空式模板
                prompt = f"""
                作为出口意大利超市渠道的合规专家，针对产品：{p_name}, HS: {hs_code}, 材质: {material}。
                
                请直接输出以下两个核心模块，严禁任何废话：

                ### 1/ 检测做什么 (Testing Requirements)
                | 检测项目 | 对应标准/法规 | 目的 |
                | :--- | :--- | :--- |

                ### 2/ 包装怎么做 (Packaging Design & Copy)
                请提供三列对照表：【模块位置】 | 【中文版本 (供审核)】 | 【意大利语版本 (设计师直拷贝)】。
                
                **强制要求：**
                1. 物理参数必须基于 {material} 真实属性（例如：PETG 严禁超过 60°C）。
                2. 包装文案必须包含：[公司名]、[完整地址]、[联系邮箱/电话] 等填空式占位符。
                3. 环境标签必须输出材质代码（如 ♺ 01 PET, ♺ 05 PP）。
                4. 绝对隐藏不相关的图标（如非食品不显示 🍷🍴）。

                | 模块位置 | 中文版本 (精准对齐) | 意大利语版本 (设计师直接复制) |
                | :--- | :--- | :--- |
                | **标题区** | {p_name} [规格参数] | {p_name} [Specifiche] |
                | **图标区** | [图标说明：CE, WEEE 或 MOCA 等] | [Simbolo: XXX] |
                | **使用警告** | 警告：[具体的物理限制翻译] | ⚠ AVVERTENZE: [Precise Italian] |
                | **环境标签引导** | 环境标签：请核实当地规定 | ETICHETTATURA AMBIENTALE: Verifica le disp... |
                | **环境标识-主体** | [部件A]: [材质码] - [回收容器] | [Componente]: [Codice] - [Raccolta] |
                | **环境标识-包装** | [部件B]: [材质码] - [回收容器] | [Imballaggio]: [Codice] - [Raccolta] |
                | **进口商/地址/邮箱** | 进口商: [填名] / 地址: [填地址] / 邮箱: [填邮箱] | Importato da: [Name] / Indirizzo: [Address] / Email: [Mail] |
                | **制造商/地址/产地** | 制造商: [填名] / 地址: [填地址] / 中国制造 | Prodotto da: [Name] / Indirizzo: [Address] / Made in China |
                | **物流批次** | 批次号: [填入] / EAN码 | Lotto No.: [Lotto] / EAN & Barcode |
                """
                
                result = get_delivery_content(prompt)
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
                st.success("✅ 交付方案已就绪。")
            except Exception as e:
                st.error(f"❌ 运行报错：{str(e)}")
