import streamlit as st
import google.generativeai as genai

# --- 1. 初始化配置 ---
st.set_page_config(page_title="意大利超市包装交付助手-V4", layout="wide", page_icon="🇮🇹")
st.title("🇮🇹 意大利超市出口包装交付系统 (设计师直供版)")

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
        hs_code = st.text_input("2. HS Code", placeholder="如：851210 (电子) / 392410 (塑胶)")
        material = st.text_input("3. 材质成分", placeholder="如：ABS外壳, 锂电池 / 不锈钢杯身, PP盖")
        power = st.selectbox("4. 供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("5. 适用人群", ["通用/成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("🚀 生成交付级包装方案", type="primary")

# --- 4. 交付逻辑执行 ---
if submitted:
    if not p_name or not hs_code:
        st.error("⚠️ 必须输入品名和 HS Code。")
    else:
        with st.spinner('🤖 正在根据品类属性过滤不相关信息并构建文案...'):
            try:
                # 针对“品类过滤”和“文案原子化”深度优化的 Prompt
                full_prompt = f"""
                你是一名精通意大利包装法 (Dlgs 116/2020) 和零售准入的专业合规官。
                当前产品：{p_name}, HS: {hs_code}, 材质: {material}, 供电: {power}, 受众: {target}。

                ### 关键任务：
                1. **品类过滤**：根据 HS Code 和品名判定产品属性。如果是【非食品容器】（如电子产品、工具），严禁出现“食品接触标”、“BPA Free”、“洗碗机适用”等任何干扰信息。
                2. **文案原子化**：环境标签（Etichettatura Ambientale）部分必须将每个部件拆分为独立的行。严禁将不同部件写在同一单元格内。每一行必须包含：[部件名称] | [材质标识] | [回收路径文案]。

                请直接输出以下两个模块：

                ### 1/ 检测做什么 (Testing Requirements)
                以表格形式列出进入意大利超市必须通过的项目，严禁长文。
                | 检测项目 | 匹配法律/EN标准 | 目的 |
                | :--- | :--- | :--- |

                ### 2/ 包装怎么做 (Packaging Design - Ready to Copy)
                请提供三列对照表：【包装模块/位置】 | 【中文版本 (供理解)】 | 【意大利语版本 (设计师直接复制)】。
                
                **注意：意大利语版本必须是“最终文案”，设计师直接粘贴，不需进行二次判断或删减。**

                | 包装模块/位置 | 中文版本 (设计师参考) | 意大利语版本 (设计师直接复制) |
                | :--- | :--- | :--- |
                | **标题信息** | 产品名称及核心规格 | {p_name} [根据实际参数填写规格] |
                | **必放图标1** | 根据品类判定（如：CE标 / 0-3禁令标） | [图标说明：此处放置对应的图标符号] |
                | **必放图标2** | 仅当产品带电时展示：WEEE垃圾桶打叉标 | (仅带电产品显示：[Simbolo: bidone barrato]) |
                | **核心警告** | 物理/安全警告 (如：严禁直视光源/Max 60°C) | ⚠ AVVERTENZE: [基于 {p_name} 属性生成的精准意文] |
                | **环境标签标题** | 环境标签总标题及引导语 | ETICHETTATURA AMBIENTALE. Verifica le disposizioni del tuo Comune. |
                | **环境标签-部件A** | 主体材质 (如杯身或灯壳) | [部件名]: ♺ [材质码] - [回收容器名] |
                | **环境标签-部件B** | 配件材质 (如盖子或电池) | [部件名]: [材质码或回收说明] - [回收容器名] |
                | **环境标签-部件C** | 包装材料 (如纸盒或塑料袋) | [部件名]: [材质码] - [回收容器名] |
                | **制造/进口商** | 制造商及进口商占位符 | Prodotto da: [Fabbrica] / Importato da: [Importatore] |
                | **追溯信息** | 生产批次及产地 | Lotto No.: [Lotto] / Made in China |

                请确保物理常识准确（如 PETG 不超过 60°C，电子产品不提食品安全）。
                """
                
                result = get_final_delivery_report(full_prompt)
                st.markdown(result)
                st.divider()
                st.success("✅ 交付方案已根据品类属性精准过滤，设计师可直接取用。")
                
            except Exception as e:
                st.error(f"❌ 运行中出现错误：{str(e)}")
