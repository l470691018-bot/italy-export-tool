import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style CSS 注入 ---
st.set_page_config(page_title="Italy Compliance", layout="wide", page_icon="🇮🇹")

st.markdown("""
    <style>
    /* 苹果风极简排版 */
    .stApp { background-color: #f5f5f7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .stTextInput, .stSelectbox, .stButton button { border-radius: 12px !important; }
    .stAlert { border-radius: 16px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1d1d1f; font-weight: 600; }
    .main-card { background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.04); margin-bottom: 20px; }
    /* 针对表格的优化 */
    table { border-collapse: collapse !important; border-radius: 10px; overflow: hidden; }
    th { background-color: #fbfbfd !important; color: #86868b !important; text-transform: uppercase; font-size: 11px; letter-spacing: 0.1em; }
    </style>
    """, unsafe_allow_html=True)

# 安全读取密钥
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ Secrets Error: GEMINI_API_KEY not found in settings.")
    st.stop()

# --- 2. 核心函数 ---
def get_final_delivery(prompt):
    safety = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    ]
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', safety_settings=safety)
    return model.generate_content(prompt).text

# --- 3. 极简侧边栏 ---
with st.sidebar:
    st.title("Italy Compliance")
    with st.form("input_form"):
        p_name = st.text_input("产品名称", placeholder="如：Tritan运动水杯")
        hs_code = st.text_input("HS Code", placeholder="392410")
        material = st.text_input("材质成分", placeholder="如：Tritan杯身, PP盖子, 硅胶圈")
        power = st.selectbox("供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("适用人群", ["成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("生成交付方案", type="primary")
    
    st.markdown("---")
    st.link_button("🔍 HS Code 查询", "https://www.baidu.com/s?wd=HS编码查询")

# --- 4. 逻辑输出 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 请输入必要的产品参数。")
    else:
        with st.spinner('Preparing delivery documents...'):
            try:
                # 增强版交付 Prompt：强制包含代码、地址、邮箱和精准翻译
                prompt = f"""
                你是一名精通意大利 116/2020 包装法令及欧盟 GPSR 安全标准的合规专家。
                针对产品：{p_name}, HS: {hs_code}, 材质: {material}, 供电: {power}, 受众: {target}。

                ### 强制要求：
                1. **环境标签完整性**：必须为【每个】材质组件（如主体、盖子、密封圈、包装盒）提供精准的材质代码（如 PET 01, PP 05, PAP 21 等）及回收路径。
                2. **法律责任项**：制造商和进口商信息必须包含 [名称]、[地址]、[邮箱/联系方式] 三个独立占位符。
                3. **视觉风格**：输出内容必须极其干净。不相关图标绝对隐藏。
                4. **翻译质量**：中文列必须是意语的 1:1 精准翻译。

                输出结构：

                ### 1/ 检测要求 (Testing Requirements)
                | 检测项目 | 匹配法律/EN标准 | 目的 |
                | :--- | :--- | :--- |

                ### 2/ 包装交付稿 (Packaging Copy - Designer Ready)
                | 模块/位置 | 中文版本 (审核用) | 意大利语版本 (设计师复制) |
                | :--- | :--- | :--- |
                | **标题信息** | {p_name} [规格参数] | {p_name} [Specifiche] |
                | **核心警告** | 警告：[基于材质属性生成的精准物理限制翻译] | ⚠ AVVERTENZE: [Precisely Italian Text] |
                | **环境标签** | 环境标签：请查阅当地市政规定。 | ETICHETTATURA AMBIENTALE: Verifica le disposizioni del tuo Comune. |
                | **环境标识-主体** | [部件名A]: [材质码, 如 ♺ 07 OTHER] - [回收容器] | [Componente A]: [Codice] - [Raccolta] |
                | **环境标识-配件** | [部件名B]: [材质码] - [回收容器] | [Componente B]: [Codice] - [Raccolta] |
                | **环境标识-包装** | [部件名C]: [材质码] - [回收容器] | [Componente C]: [Codice] - [Raccolta] |
                | **进口商信息** | 进口商: [公司名] / 地址: [完整地址] / 邮箱: [联系邮箱] | Importato da: [Ragione Sociale] / Indirizzo: [Indirizzo] / Email: [Contatto] |
                | **制造商信息** | 制造商: [工厂名] / 地址: [完整地址] / 中国制造 | Prodotto da: [Nome Fabbrica] / Indirizzo: [Indirizzo] / Made in China |
                | **追溯/物流** | 批次号: [填入] / 条形码 | Lotto No.: [Lotto] / EAN & Barcode |

                *注：如果是电子产品，必须增加 WEEE 图标提示；如果是食品容器，必须增加高脚杯叉子标提示。*
                """
                
                result = get_final_delivery(prompt)
                st.markdown(f'<div class="main-card">{result}</div>', unsafe_allow_html=True)
                st.success("✅ 交付方案已就绪。")
                
            except Exception as e:
                st.error(f"❌ 运行报错：{str(e)}")
