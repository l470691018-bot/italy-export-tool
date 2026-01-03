import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(page_title="意大利合规助手-正式版", layout="wide", page_icon="🇮🇹")
st.title("🇮🇹 意大利超市出口合规助手 (正式版)")

# 【此处确保粘贴您 B 账户中完整的、AIza 开头的密钥】
API_KEY = "AIzaSyAAGztx9bEcEIyQZ4WRcNbrwMAvb_2g5fw"

# --- 2. 核心逻辑：获取清洁的输出 ---
def generate_compliance_report(prompt):
    genai.configure(api_key=API_KEY.strip())
    
    # 获取可用模型列表
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target = next((m for m in models if 'gemini-1.5-flash' in m), models[0])
    
    model = genai.GenerativeModel(target)
    # 限制候选词，增加输出稳定性
    response = model.generate_content(prompt)
    return response.text

# --- 3. 界面设计 ---
with st.sidebar:
    st.header("📋 产品参数输入")
    with st.form("input_form"):
        p_name = st.text_input("品名", placeholder="如：保温杯")
        hs_code = st.text_input("HS Code", placeholder="961700")
        material = st.text_input("材质", placeholder="304不锈钢")
        power = st.selectbox("带电情况", ["无供电", "含电池", "插电"])
        target = st.selectbox("适用人群", ["成人", "儿童 (3-14岁)", "婴幼儿 (0-3岁)"])
        submitted = st.form_submit_button("🚀 生成方案报告", type="primary")

# --- 4. 结果展示逻辑 ---
if submitted:
    if not p_name or not hs_code:
        st.error("请完整填写品名和 HS Code")
    else:
        try:
            with st.spinner('🔍 正在生成精简版合规报告...'):
                # 强化 Prompt，强制 Markdown 格式和总-分-总结构
                prompt = f"""
                作为意大利零售合规专家，请分析产品：{p_name}(HS:{hs_code}, 材质:{material}, 供电:{power}, 人群:{target})。
                
                请严格遵守以下格式要求：
                1. 使用“总-分-总”结构：先给结论，再罗列要素，最后引导结果。
                2. 必须使用标准 Markdown 表格（| 标题 | 标题 |）。
                3. 文字要简明扼要，逻辑清晰。
                4. 包装要求必须提供中意双语对照。
                5. 生成一个纯意大利语的文本块方便复制。
                6. 提及官方法规链接时，请以 Markdown 链接形式展示。

                输出结构：
                ## 【总】快速准入结论
                ## 【分】详细合规要素
                ### 1. 检测与证书清单 (表格)
                ### 2. 包装图标与文案要求 (表格)
                ## 【总】下一步行动引导
                """
                
                result = generate_compliance_report(prompt)
                
                # 直接展示渲染后的内容
                st.markdown(result)
                
                st.divider()
                st.success("✅ 报告已按要求生成。")
                
        except Exception as e:
            st.error(f"❌ 运行报错：{str(e)}")
