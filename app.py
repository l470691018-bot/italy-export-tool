import streamlit as st
import google.generativeai as genai

# --- 1. Apple-Style 极简 UI 设计 ---
st.set_page_config(page_title="Italy Export Compliance", layout="wide", page_icon="🇮🇹")

st.markdown("""
    <style>
    /* 苹果官网极简风格 */
    .stApp { background-color: #f5f5f7; font-family: -apple-system, system-ui, sans-serif; color: #1d1d1f; }
    .stTextInput input, .stSelectbox div, .stButton button { border-radius: 12px !important; border: 1px solid #d2d2d7 !important; }
    .stButton button { background-color: #0071e3 !important; color: white !important; font-weight: 500 !important; border: none !important; }
    .card { background: white; padding: 2.5rem; border-radius: 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #e5e5e7; margin-top: 1.5rem; }
    h1, h2, h3 { font-weight: 600; letter-spacing: -0.02em; border: none !important; }
    th { background-color: #fbfbfd !important; color: #86868b !important; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 安全层：密钥保护与自适应模型连接 ---
try:
    # 必须在 Streamlit 后台 Secrets 配置 GEMINI_API_KEY
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY.strip())
except Exception:
    st.error("❌ 密钥未配置：请在 Streamlit 控制台 Settings -> Secrets 中设置 GEMINI_API_KEY。")
    st.stop()

def get_pro_delivery_content(prompt):
    # 自动探测所有可能的模型路径变体，彻底解决 404 报错
    model_variants = ['gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    safety = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
              {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
    
    for m_name in model_variants:
        try:
            model = genai.GenerativeModel(m_name, safety_settings=safety)
            # 尝试联网搜索以获取 2026 最新标准
            try:
                model = genai.GenerativeModel(m_name, tools=[{'google_search_retrieval': {}}], safety_settings=safety)
            except: pass
            return model.generate_content(prompt).text
        except: continue
    raise Exception("API 连接失败：请检查密钥是否被封禁或配额是否耗尽。")

# --- 3. 侧边栏 ---
with st.sidebar:
    st.title("Compliance")
    with st.form("input_form"):
        p_name = st.text_input("产品名称", placeholder="例如：PETG 运动水杯")
        hs_code = st.text_input("海关编码 (HS Code)", placeholder="例如：392410")
        material = st.text_input("材质成分", placeholder="例如：PETG 杯身, PP 盖子")
        power = st.selectbox("供电情况", ["无供电", "含电池", "插电使用"])
        target = st.selectbox("人群划分", ["通用/成人", "儿童 (3-14岁)", "婴幼儿"])
        submitted = st.form_submit_button("生成交付方案", type="primary")
    
    st.divider()
    st.link_button("🔍 HS Code 快速查询", "https://www.baidu.com/s?wd=HS编码查询")

# --- 4. 业务逻辑执行 ---
if submitted:
    if not p_name or not hs_code:
        st.warning("⚠️ 基础参数缺失，无法生成合规报告。")
    else:
        with st.spinner('Preparing professional delivery doc...'):
            try:
                # 终极 Prompt：去冗余 + 1:1 对齐 + 真实物理常识
                prompt = f"""
                你是出口意大利超市的合规交付专家。产品：{p_name}, HS: {hs_code}, 材质: {material}, 供电: {power}, 人群: {target}。
                
                请直接输出以下模块，严禁任何废话：

                ### 1/ 检测做什么 (Testing Requirements)
                请以表格列出必须通过的项目及其 2026 最新标准。
                | 检测项目 | 匹配法律/标准 | 目的 |
                | :--- | :--- | :--- |

                ### 2/ 包装怎么做 (Packaging Design & Copy)
                请提供三列对照表：【位置】 | 【中文翻译 (审核用)】 | 【意大利语内容 (设计师复制)】。
                
                **强制要求：**
                1. **品类识别**：如果是电子类(HS 84/85)，严禁出现食品图标。如果是食品接触类，必须包含高脚杯叉子标。
                2. **物理常识**：基于材质 {material} 输出确定参数（如 PETG 不超 60°C），严禁使用“例如”。
                3. **环境标签**：每个部件必须包含具体代码（如 ♺ 01 PET, ♺ 05 PP）和回收去向。
                4. **责任实体**：进口商/制造商信息必须包含 [名称]、[地址]、[邮箱/电话] 完整结构。

                | 包装位置 | 中文翻译 (精准对齐) | 意大利语版本 (设计师直接复制) |
                | :--- | :--- | :--- |
                | **标题信息** | {p_name} [规格参数] | {p_name} [Specifiche] |
                | **必放图标** | [根据品类精准判定的图标名称] | [Simbolo: XXX] |
                | **使用警告** | 警告：[基于属性生成的精准物理限制翻译] | ⚠ AVVERTENZE: [Precisely Translated] |
                | **环境标签** | 环境标签：请核实当地规定。丢弃前清空。 | ETICHETTATURA AMBIENTALE... |
                | **部件标识** | [部件名]: [材质码] - [回收路径] | [Componente]: [Codice] - [Raccolta] |
                | **企业信息** | 进口商/制造商: [公司名] / 地址: [完整地址] / 邮箱: [联系方式] | [Importer/Manufacturer details in Italian structure] |
                """
                
                result = get_pro_delivery_content(prompt)
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
                st.success("✅ 方案已根据 2026 意大利最新法规生成完毕。")
                
            except Exception as e:
                st.error(f"❌ 系统级错误：{str(e)}")
