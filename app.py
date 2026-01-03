import streamlit as st
import google.generativeai as genai

# --- 1. 初始化配置 ---
st.set_page_config(page_title="意大利超市交付助手-最终版", layout="wide", page_icon="🇮🇹")
st.title("🇮🇹 意大利超市出口包装交付系统 (审核/设计对齐版)")

# 安全读取密钥
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 报错：未检测到密钥！请检查 Streamlit 后台 Secrets 配置。")
    st.stop()

# --- 2. 核心函数 ---
def get_final_delivery_report(prompt):
    safety = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    ]
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target = next((m for m in models if 'gemini-1.5-flash' in m), models[0])
    model = genai.GenerativeModel(model_name=target, safety_settings=safety)
    return model.generate_content(prompt).text

# --- 3. 界面设计 ---
with st.sidebar:
    st.header("📋 产品核心参数")
    with st.form("input_form"):
        p_name = st.text_input("1. 品名", placeholder="如：自行车灯 / PETG水杯")
        hs_code = st.text_input("2. HS Code", placeholder="如：851210 / 392410")
        material = st.text_input("3. 材质成分", placeholder="如：ABS外壳, 锂电池 / 不锈钢, PP盖")
        power = st.selectbox("4. 供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("5. 适用人群", ["通用/成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("🚀 生成交付级包装方案", type="primary")

# --- 4. 交付逻辑执行 ---
if submitted:
    if not p_name or not hs_code:
        st.error("⚠️ 必须输入品名和 HS Code。")
    else:
        with st.spinner('🤖 正在过滤冗余信息并进行双语对齐...'):
            try:
                # 终极 Prompt：要求绝对隐藏不相关项，且中文必须为 1:1 翻译
                full_prompt = f"""
                你是一名精通意大利包装法和零售准入的专业合规官。针对产品：{p_name}, HS: {hs_code}, 材质: {material}, 供电: {power}, 受众: {target}。
                
                ### 强制指令：
                1. **绝对隐藏（Zero Noise）**：如果该产品不需要某个图标（例如非食品接触产品），严禁在回答中出现该项，连“不适用”三个字都不要写。只输出【必须体现】的内容。
                2. **双语对齐（1:1 Translation）**：输出的表格中，【中文内容】必须是【意大利语内容】的精准翻译，目的是让设计师能通过中文审核意大利语的意思。
                3. **环境标签原子化**：将每个包装部件拆分为独立的行。每一行必须包含：部件名 | 材质码 | 回收建议。

                请直接输出以下内容：

                ### 1/ 检测做什么 (Testing Requirements)
                | 检测项目 | 匹配法律/EN标准 | 目的 |
                | :--- | :--- | :--- |

                ### 2/ 包装怎么做 (Packaging Design - Final Copy)
                请提供三列对照表：【模块/位置】 | 【中文内容 (精准翻译)】 | 【意大利语内容 (直接复制)】。

                | 模块/位置 | 中文内容 (设计师审核) | 意大利语内容 (设计师直接复制) |
                | :--- | :--- | :--- |
                | **标题信息** | {p_name} [规格参数] | {p_name} [Specifiche] |
                | **图标标识** | [图标说明：仅列出必须放置的图标名] | [Simbolo: 图标名，如 CE 或 WEEE] |
                | **核心警告** | 警告：[这里是警告语的中文翻译] | ⚠ AVVERTENZE: [对应的精准意大利语] |
                | **环境标签** | 环境标签：请核实当地市政规定。丢弃前请清空。 | ETICHETTATURA AMBIENTALE: Verifica le disposizioni del tuo Comune. Svuotare prima di conferire. |
                | **环境标签-部件A** | [部件A名称]: [材质码] - [回收容器名] | [部件A]: [Codice] - [Raccolta] |
                | **环境标签-部件B** | [部件B名称]: [材质码] - [回收容器名] | [部件B]: [Codice] - [Raccolta] |
                | **制造商/进口商** | 制造商: [中国厂商名] / 进口商: [意大利公司名] | Prodotto da: [Fabbrica] / Importato da: [Importatore] |
                | **追溯信息** | 批次号: [批次号] / 中国制造 | Lotto No.: [Lotto] / Made in China |

                *注：如果产品不涉及食品安全，严禁出现任何食品相关的图标及翻译。如果产品不带电，严禁出现 WEEE 图标及翻译。*
                """
                
                result = get_final_delivery_report(full_prompt)
                st.markdown(result)
                st.divider()
                st.success("✅ 方案已剔除所有冗余项，双语已完全对齐。")
                
            except Exception as e:
                st.error(f"❌ 运行中出现错误：{str(e)}")
