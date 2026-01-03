import streamlit as st
import google.generativeai as genai

# --- 1. 初始化配置 ---
st.set_page_config(page_title="意大利合规助手-设计师增强版", layout="wide", page_icon="🇮🇹")
st.title("🇮🇹 意大利超市出口合规助手 (设计师版)")

# 安全读取密钥
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 报错：未检测到密钥！请检查 Streamlit 后台 Secrets 配置。")
    st.stop()

# --- 2. 核心函数 ---
def get_pro_report(prompt):
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
    st.header("📋 填写产品参数")
    with st.form("input_form"):
        p_name = st.text_input("1. 品名", placeholder="如：PETG运动水杯")
        hs_code = st.text_input("2. HS Code", placeholder="392330")
        material = st.text_input("3. 核心材质", placeholder="PETG材质")
        power = st.selectbox("4. 供电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("5. 适用人群", ["通用/成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("🚀 生成设计师版方案", type="primary")

# --- 4. 业务逻辑执行 ---
if submitted:
    if not p_name or not hs_code:
        st.error("⚠️ 品名和 HS Code 是生成法律依据的基础，请务必填写！")
    else:
        with st.spinner('🔍 正在计算材质属性并检索意大利最新法规...'):
            try:
                # 针对“精准文案”和“物理参数”优化的超级 Prompt
                full_prompt = f"""
                作为出口意大利超市的专家，请为产品【{p_name}】提供最终交付级的包装文案。
                产品参数：HS Code: {hs_code}, 材质: {material}, 供电: {power}, 人群: {target}。

                请严格按以下结构输出，内容必须是“最终确定态”，严禁使用“例如”：

                ## 【总】快速准入结论
                - 给出明确的准入等级。
                - 核心依据：根据 {material} 判定是否涉及 MOCA (Reg. 1935/2004) 及具体迁移测试要求。

                ## 【分】实操执行细节
                ### 1. 物理参数与使用限制 (精准数据)
                - 基于 {material} 的真实物理特性，给出最终的耐温范围、洗碗机/微波炉适用性建议。
                - **强制要求**：如果材质是 PETG，耐温上限必须注明为 60°C 或 70°C，严禁给出超出科学常识的数据。

                ### 2. 包装图标清单 (视觉元素)
                | 图标名称 | 意大利语描述 | 备注 |
                | :--- | :--- | :--- |
                | (图标名，如CE) | (图标对应的法律文案) | (设计师位置/尺寸建议) |

                ### 3. 设计师专用：双语包装文案 (填空式模板)
                请提供以下信息的精确意文翻译，并将需要用户填空的部分用 [方括号中文备注] 标出：
                - **进口商信息栏**：
                  Importato da: [此处填公司全称/Ragione Sociale]
                  Indirizzo: [此处填完整地址/Indirizzo Completo]
                  Email: [此处填联系邮箱/Email di Contatto]
                - **制造商信息栏**：
                  Prodotto da: [此处填生产工厂名称/Nome Fabbrica]
                  Made in China
                - **产品成分描述**：按照意大利法规定制翻译。

                ## 【总】设计师纯意文复制块
                请提供一段完整的、没有任何中文解释干扰的文本块。
                包含：材质回收代码 (如 {material} 对应的 PAP 21 或 PET 01)、意大利环境标签要求 (Dlgs 116/2020) 以及上述信息的占位符模板。
                """
                
                result = get_pro_report(full_prompt)
                st.markdown(result)
                st.divider()
                st.success("✅ 方案已根据产品材质属性精准生成。")
                
            except Exception as e:
                st.error(f"❌ 运行报错：{str(e)}")
