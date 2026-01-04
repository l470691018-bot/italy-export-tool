import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 极简视觉设计 ---
st.set_page_config(page_title="Italy Compliance", layout="wide", page_icon="🇮🇹")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; }
    .stTextInput, .stSelectbox, .stButton button { border-radius: 10px !important; }
    h1, h2, h3 { color: #1d1d1f; border-bottom: none; }
    .card { background: white; padding: 25px; border-radius: 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 20px; }
    table { width: 100%; border-radius: 12px; overflow: hidden; border: none !important; }
    th { background-color: #fbfbfd !important; font-size: 12px; color: #86868b !important; }
    </style>
    """, unsafe_allow_html=True)

# 从 Secrets 安全读取 Key
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 未找到 API KEY。请在 Streamlit 后台 Secrets 配置 GEMINI_API_KEY。")
    st.stop()

# --- 2. 核心逻辑：自动侦察模型路径，解决 404 ---
def get_reliable_model():
    # 尝试常见的模型名称变体
    candidate_names = ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-flash']
    safety = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    
    # 自动探测哪个名称有效
    for name in candidate_names:
        try:
            model = genai.GenerativeModel(model_name=name, safety_settings=safety)
            # 测试性调用，确认模型存在
            model.generate_content("test", generation_config={"max_output_tokens": 1})
            return model
        except:
            continue
    
    # 如果都失败，尝试动态列出可用模型
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and '1.5-flash' in m.name:
                return genai.GenerativeModel(model_name=m.name, safety_settings=safety)
    except:
        pass
    
    raise Exception("无法连接到任何有效的 Gemini 模型，请检查 API Key 权限。")

# --- 3. 极简交互界面 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("input_form"):
        p_name = st.text_input("产品名称", placeholder="例如：自行车灯")
        hs_code = st.text_input("HS Code", placeholder="851210")
        material = st.text_input("材质成分", placeholder="ABS外壳, 锂电池, 纸盒")
        power = st.selectbox("供电情况", ["含电池", "插电", "无供电"])
        target = st.selectbox("适用人群", ["成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("生成包装方案", type="primary")

# --- 4. 交付结果生成 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 请输入产品名称和 HS Code。")
    else:
        with st.spinner('Preparing delivery documents...'):
            try:
                model = get_reliable_model()
                
                prompt = f"""
                作为意大利零售合规专家，请为产品【{p_name}】提供最终交付级的包装文案。
                HS Code: {hs_code}, 材质: {material}, 供电: {power}, 受众: {target}。

                ### 交付规范：
                1. **环境标签(Dlgs 116/2020)**：必须为每个部件输出材质代码（如 ♺ 01 PET, ♺ 20 PAP）。
                2. **责任实体**：制造商与进口商信息必须包含[公司名]、[完整地址]、[联系邮箱/电话]。
                3. **内容精准**：如果不是食品容器，严禁出现🍷🍴标；如果带电，必须有WEEE图标提示。
                4. **审核对齐**：中文列必须是意大利语的 1:1 精确翻译。

                请严格按表格输出：
                ### 1/ 检测项目表
                | 项目 | 标准 | 目的 |

                ### 2/ 包装交付稿 (三列对照)
                | 模块/位置 | 中文(审核) | 意大利语(复制) |
                | :--- | :--- | :--- |
                | 标题信息 | {p_name} 规格 | {p_name} [Specifiche] |
                | 图标提示 | [图标说明：CE, WEEE等] | [Simbolo: XXX] |
                | 环境标签 | 环境标签说明引导语 | ETICHETTATURA AMBIENTALE... |
                | 部件A标识 | [部件A]: [材质码] - [回收容器] | [Componente]: [Codice] - [Raccolta] |
                | 进口商信息 | 进口商: [名] / 地址: [地址] / 邮箱: [邮箱] | Importato da: [Name] / Indirizzo: [Address] / Email: [Mail] |
                | 制造商信息 | 制造商: [名] / 地址: [地址] / 产地 | Prodotto da: [Name] / Indirizzo: [Address] / Made in China |
                """
                
                response = model.generate_content(prompt)
                st.markdown(f'<div class="card">{response.text}</div>', unsafe_allow_html=True)
                st.success("✅ 方案生成完毕。")
            except Exception as e:
                st.error(f"❌ 运行报错：{str(e)}")
