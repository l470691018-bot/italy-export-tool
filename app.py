import streamlit as st
import google.generativeai as genai

# --- 1. 初始化配置 ---
st.set_page_config(page_title="意大利超市包装交付助手", layout="wide", page_icon="🇮🇹")
st.title("🇮🇹 意大利超市出口包装交付系统")

# 安全读取密钥
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 报错：未检测到密钥！请检查 Streamlit 后台 Secrets 配置。")
    st.stop()

# --- 2. 核心函数 ---
def get_design_report(prompt):
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
        p_name = st.text_input("1. 品名", placeholder="如：PETG运动水杯")
        hs_code = st.text_input("2. HS Code", placeholder="392410")
        material = st.text_input("3. 核心材质", placeholder="如：PETG杯身, PP盖, 硅胶密封圈")
        power = st.selectbox("4. 供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("5. 适用人群", ["通用/成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("🚀 一键交付设计师版方案", type="primary")

    st.divider()
    st.link_button("🔍 HS Code 快速查询", "https://www.baidu.com/s?wd=HS编码查询")

# --- 4. 交付逻辑执行 ---
if submitted:
    if not p_name or not hs_code:
        st.error("⚠️ 必须输入品名和 HS Code 才能确定合规逻辑。")
    else:
        with st.spinner('🤖 正在构建包装交付稿...'):
            try:
                # 终极 Prompt：彻底抛弃虚假描述，只给真实数据和填空模板
                full_prompt = f"""
                你是一名精通意大利超市 (Lidl, Coop, Esselunga) 准入要求的包装设计师和合规官。
                针对产品：{p_name}, HS: {hs_code}, 材质: {material}, 供电: {power}, 受众: {target}。
                请直接输出以下两个核心环节，不要任何开场白和总结。

                ### 1/ 检测做什么 (Testing Requirements)
                请以表格形式列出该产品进入意大利超市必须通过的项目，严禁长篇大论。
                | 检测项目 | 匹配法律/EN标准 | 目的 |
                | :--- | :--- | :--- |

                ### 2/ 包装怎么做 (Packaging Design & Copy)
                请按照以下“双语对照表”形式，为设计师提供最终的、可直接复制的文案。
                左列为【模块/中文解释】，右列为【意大利语最终可复制文案】。
                
                **注意：必须基于 {material} 的真实物理属性。如果是 PETG，耐温上限必须写 60°C；严禁使用“例如”等占位符，必须根据知识库给出确定数据。**

                | 包装模块/位置 | 中文版本 (设计师参考) | 意大利语版本 (设计师复制到画稿) |
                | :--- | :--- | :--- |
                | **标题区** | 产品名称 / 规格 [由设计师填具体容量] | {p_name} [750 / 1000 / 2000] ml |
                | **图标提示 (Icon Area)** | 图标1：食品接触安全标识 | [🍷🍴 图标] Per contatto con alimenti |
                | **图标提示 (Icon Area)** | 图标2：年龄限制 (0-3岁禁用) | [🚫👶 (0-3)] Non adatto a bambini di età inferiore a 36 mesi |
                | **图标提示 (Icon Area)** | 图标3：不含双酚A (若是塑胶) | Senza BPA |
                | **核心警告 (Warnings)** | 注意事项：仅限手洗 | ⚠ AVVERTENZE: Solo lavaggio a mano |
                | **核心警告 (Warnings)** | 注意事项：不可进洗碗机 | NON mettere in lavastoviglie |
                | **核心警告 (Warnings)** | 注意事项：物理耐温上限 | 温度上限根据 {material} 实际物理属性设定 (如 Max 60°C) |
                | **环境标签 (Etichettatura)** | 标题：环境标签说明 | ETICHETTATURA AMBIENTALE |
                | **环境标签 (Etichettatura)** | 标语：请核实当地市政规定 | Verifica le disposizioni del tuo Comune. Svuotare prima di conferire. |
                | **环境标签表 (Recycling)** | 表格行1：产品本身材质 (材质码+回收路径) | (根据 {material} 属性生成，如：Borraccia: ♺ 07-PETG - Plastica) |
                | **环境标签表 (Recycling)** | 表格行2：配件/盖子材质 | (根据 {material} 属性生成，如：Tappo: ♺ 05-PP - Plastica) |
                | **强制信息栏 (Logistics)** | 批次号、原产地 | Lotto No.: [此处填生产批次] / Made in China |
                | **制造商信息 (Manufacturer)** | 厂商全称及地址 | Prodotto da: [此处填中国厂商信息] |
                | **进口商信息 (Importer)** | 意大利进口商全称及地址 | Importato da: [此处填意大利公司信息] |
                | **物流编码 (Codes)** | SKU / EAN 占位符 | SKU / EAN / Barcode [此处放条形码图形] |

                请确保所有翻译精准且符合意大利零售业包装习惯。
                """
                
                result = get_design_report(full_prompt)
                st.markdown(result)
                st.divider()
                st.success("✅ 方案已就绪，设计师可直接开始作业。")
                
            except Exception as e:
                st.error(f"❌ 运行中出现错误：{str(e)}")
