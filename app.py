import streamlit as st
import google.generativeai as genai

# --- 1. 配置区域 ---
st.set_page_config(page_title="意大利出口合规助手(Pro版)", layout="wide", page_icon="🇮🇹")

# 您的 API Key
API_KEY = "AIzaSyA4vCg-1_MmH7_Wbq5JJIcjzpmih-2qqw8"

# 配置 Gemini 模型 (使用更稳定的 flash 版本，并尝试启用搜索工具)
# 如果之后提示关于 google_search 的错误，请联系我调整
try:
    genai.configure(api_key=API_KEY)
    # 使用 gemini-1.5-flash 模型，它速度快且稳定
    model = genai.GenerativeModel('gemini-1.5-flash', tools=[{'google_search_retrieval': {}}])
except Exception as e:
    st.error(f"API 配置失败，请检查 Key 是否正确。\n错误信息: {e}")
    st.stop()

# --- 2. 页面标题与指引 ---
st.title("🇮🇹 意大利超市出口合规与包装方案生成器")
st.info("💡 产品部门请填写左侧信息，AI 将实时检索意大利 2025 最新法规，生成设计师可用的落地执行文档。")
st.markdown("---")

# --- 3. 侧边栏输入表单 (优化版) ---
with st.sidebar:
    st.header("📝 产品信息输入")
    with st.form("info_form"):
        st.subheader("基础项 (必填)")
        name = st.text_input("1. 产品品名", placeholder="例如：Tritan儿童运动水杯")
        
        st.markdown("---")
        st.markdown("👉 **[不知道 HS Code？点这里去搜索](https://www.baidu.com/s?wd=HS编码查询)**", unsafe_allow_html=True)
        hs_code = st.text_input("2. HS Code (海关编码)", placeholder="例如：39241000")
        st.markdown("---")

        st.subheader("合规关键项")
        material = st.text_input("3. 核心材质/成分说明", placeholder="例如：杯身Tritan，吸管食品级硅胶，不含BPA")
        
        # 使用单选框，选项更清晰
        power = st.radio("4. 供电/带电情况", ["无供电 (纯物理产品)", "含钮扣电池 (如CR2032)", "含内置锂电池", "插电使用 (220V)"])
        
        # 使用下拉菜单选择人群
        target = st.selectbox("5. 适用目标人群", ["通用/成人", "青少年 (14岁以上)", "儿童 (3-14岁)", "婴幼儿 (0-3岁，高风险)"])
        
        st.markdown("---")
        # 提交按钮
        submitted = st.form_submit_button("🚀 开始分析并生成方案", type="primary")

# --- 4. 主体内容生成区 ---
if submitted:
    # 校验必填项
    if not name or not hs_code:
        st.error("⚠️ 请务必填写【产品品名】和【HS Code】，这俩是查询法规的基础！")
    else:
        with st.spinner('🤖 AI 正在联网检索意大利 2025 年最新法律法规和标准，请稍候...'):
            try:
                # 构建超级详细的 Prompt
                prompt = f"""
                你现在是精通欧盟及意大利法律的零售准入合规专家。请基于最新的联网检索结果，为以下产品出具出口意大利线下超市的合规方案。

                【产品背景】
                - 品名: {name}
                - HS Code: {hs_code}
                - 核心材质: {material}
                - 供电方式: {power}
                - 适用人群: {target}

                【输出要求】请严格按照以下结构输出 Markdown 格式的内容，务必专业、准确、具有实操性：

                ## 一、准入结论与核心风险 (Executive Summary)
                * **准入难度评级**：(例如：中等/高危)
                * **核心合规门槛**：一句话总结最关键的法规要求（如：必须符合 MOCA 食品接触法规，或必须通过 EN71 玩具测试）。
                * **主要风险提示**：(例如：意大利对塑料制品的回收标识检查非常严格)。

                ## 二、必须进行的检测与认证清单 (Testing & Certification)
                请以表格形式列出：
                | 检测/认证项目 | 对应标准/指令 (EU/Italy) | 必要性说明 |
                | :--- | :--- | :--- |
                | (例如：食品接触材料迁移测试) | (例如：Reg. (EU) 10/2011 & DM 21/03/73) | (针对 Tritan 材质必须项) |
                | (例如：CE认证-玩具安全) | (例如：EN 71-1,2,3) | (针对儿童产品必须项) |
                | ... | ... | ... |
                *在此处列出需要准备的技术文档，如符合性声明 (DoC)。*

                ## 三、设计师执行清单：包装标识与图标 (Packaging Icons)
                **请明确列出包装上必须印刷的图标和标识：**
                * [图标名称]：(例如：CE 标志) - 说明：(例如：高度不小于5mm)
                * [图标名称]：(例如：适用于食品接触 (高脚杯叉子标)) - 说明：...
                * [图标名称]：(例如：Triman 或 意大利环境标签) - 说明：(需标明材质代码，如 PET 1)
                * [图标名称]：(例如：WEEE 垃圾桶打叉标) - 说明：(针对带电产品)
                * ...

                ## 四、设计师执行清单：包装文案素材 (Copywriting)
                ### 1. 中意双语对照表 (必印信息)
                | 中文说明 | 意大利语 (Italiano) | 备注 |
                | :--- | :--- | :--- |
                | 产品名称 | (请翻译) | |
                | 进口商信息 | Importato da: [此处预留进口商公司名和地址] | 法律强制要求 |
                | 制造商信息 | Prodotto da: [此处填中国工厂名和地址] Made in China | |
                | 材质成分 | Materiale: (请翻译具体材质) | |
                | 警告语 (如有) | Attenzione: (请根据产品特性生成标准的意文警告) | |
                | ... | ... | |

                ### 2. 纯意文复制块 (直接拷贝到设计稿)
                ```text
                此处生成一段整合好的、符合排版习惯的纯意大利语文本块，包含上述所有关键信息、材质标识代码（如 PAP 21 - Raccolta Carta）和必要的回收指引语句（如 "Verifica le disposizioni del tuo Comune"）。
                ```

                ## 五、官方参考来源 (References)
                请列出你检索用到的 2-3 个关键的官方法规链接（如欧盟官网、意大利 Gazzetta Ufficiale）。
                """

                # 调用模型生成内容
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.success("✅ 分析完成！请设计师根据以上内容进行包装文件制作。")

            except Exception as e:
                # 捕获并显示详细错误信息，方便排查
                st.error(f"❌ 抱歉，生成过程中发生了错误。\n\n错误详情: {e}\n\n请截图此错误信息发送给技术支持进行排查。这可能是因为网络问题或 Google 服务暂时不可用。")

# 初始状态下的提示
if not submitted:
    st.write("👈 请在左侧侧边栏填写产品信息，然后点击按钮生成方案。")
