import streamlit as st
from streamlit_jodit import st_jodit

from database import favorite_stocks as favorite_stocks_table

# --- 状态初始化 ---
if 'page' not in st.session_state:
    st.session_state.page = 'list'
if 'edit_code' not in st.session_state:
    st.session_state.edit_code = None
if 'view_code' not in st.session_state:
    st.session_state.view_code = None

# ==========================
# 🔥 修复1：CSS（背景完整覆盖整行 + 双击区域）
# ==========================
st.markdown("""
<style>
/* 股票卡片：完整覆盖整行 */
.stock-row-container {
    background-color: #E6F4EA;
    border-radius: 8px;
    margin: 6px 0;
    cursor: pointer;
    transition: all 0.2s;
    padding: 14px 10px;
}
.stock-row-container:hover {
    background-color: #D4EDDC;
}
/* 分割线 */
.divider-line {
    height: 1px;
    background: #E0E0E0;
    margin: 2px 0;
}
/* 全屏弹窗 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.7);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
}
.modal-box {
    background: white;
    width: 94vw;
    height: 90vh;
    border-radius: 12px;
    padding: 30px;
    overflow-y: auto;
    position: relative;
}
.close-btn {
    position: absolute;
    top: 20px;
    right: 25px;
    background: #ff4444;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 15px;
    cursor: pointer;
}
</style>

<!-- 双击触发 JS -->
<script>
function openDetail(code) {
    window.parent.location.href = window.parent.location.pathname + "?view_code=" + code;
}
</script>
""", unsafe_allow_html=True)

# ==========================
# 读取 URL 参数
# ==========================
query_params = st.query_params
view_code_js = query_params.get("view_code", None)

if view_code_js:
    st.session_state.view_code = view_code_js
    st.query_params.clear()

# --- 列表页面 ---
if st.session_state.page == 'list':
    st.title("📈 重点关注股票列表")

    if st.button("➕ 添加股票"):
        st.session_state.page = 'add'
        st.rerun()

    # 搜索
    search_tag = st.text_input("按标签搜索", "")
    search_code = st.text_input("按代码搜索", "")
    search_name = st.text_input("按名称搜索", "")

    page_size = 20
    total_count = favorite_stocks_table.query_stocks_count(
        tag_filter=search_tag.strip() or None,
        code_filter=search_code.strip() or None,
        name_filter=search_name.strip() or None
    )

    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
    page_options = list(range(total_pages))
    current_page = st.selectbox("页码（从0开始）", page_options, index=0)

    stocks = favorite_stocks_table.query_stocks_by_page(
        tag_filter=search_tag.strip() or None,
        code_filter=search_code.strip() or None,
        name_filter=search_name.strip() or None,
        page=current_page,
        page_size=page_size
    )

    # 表头
    cols = st.columns([1,2,1,2,1])
    cols[0].write("**代码**")
    cols[1].write("**名称**")
    cols[2].write("**市场**")
    cols[3].write("**标签**")
    cols[4].write("操作")

    # ==========================
    # 🔥 修复2：双击事件绑定（整行都可点击）
    # ==========================
    if stocks:
        for idx, s in enumerate(stocks):
            code = s['code']

            # 用一个完整的div包裹整行，并绑定双击事件
            st.markdown(f'''
            <div class="stock-row-container" ondblclick="openDetail('{code}')">
            ''', unsafe_allow_html=True)

            cols = st.columns([1,2,1,2,1])
            cols[0].write(s['code'])
            cols[1].write(s['name'])
            cols[2].write(s.get('market', ''))
            cols[3].write(s.get('tags', ''))
            if cols[4].button("编辑", key=f"edit_{code}"):
                st.session_state.edit_code = code
                st.session_state.page = 'edit'
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

            # 分割线
            if idx != len(stocks)-1:
                st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
    else:
        st.info("暂无匹配的股票数据")

# ==========================
# 双击弹出全屏详情页
# ==========================
if st.session_state.get('view_code'):
    code = st.session_state.view_code
    stock = favorite_stocks_table.get_stock_by_code(code)

    st.markdown('''
    <div class="modal-overlay">
        <div class="modal-box">
    ''', unsafe_allow_html=True)

    if st.button("❌ 关闭详情页", key="close_modal"):
        st.session_state.view_code = None
        st.rerun()

    st.title(f"📊 {stock['name']} ({code})")
    st.markdown(f"**市场**: {stock.get('market','-')} | **标签**: {stock.get('tags','-')}")
    st.divider()

    st.subheader("📌 主营业务")
    st.markdown(stock.get('business','<p>暂无内容</p>'), unsafe_allow_html=True)
    st.divider()

    st.subheader("📌 优势")
    st.markdown(stock.get('advantage','<p>暂无内容</p>'), unsafe_allow_html=True)
    st.divider()

    st.subheader("📌 劣势")
    st.markdown(stock.get('disadvantage','<p>暂无内容</p>'), unsafe_allow_html=True)
    st.divider()

    st.subheader("📌 重要里程碑")
    st.markdown(stock.get('milestones','<p>暂无内容</p>'), unsafe_allow_html=True)
    st.divider()

    st.subheader("📌 机构观点")
    st.markdown(stock.get('institution_view','<p>暂无内容</p>'), unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

# --- 编辑页面 ---
elif st.session_state.page == 'edit':
    stock = favorite_stocks_table.get_stock_by_code(st.session_state.edit_code)
    st.title(f"📝 编辑 {stock['name']}")

    new_business = st_jodit(value=stock.get('business',''), key="edit_biz")
    new_advantage = st_jodit(value=stock.get('advantage',''), key="edit_adv")
    new_disadvantage = st_jodit(value=stock.get('disadvantage',''), key="edit_dis")
    new_milestones = st_jodit(value=stock.get('milestones',''), key="edit_mil")
    new_institution_view = st_jodit(value=stock.get('institution_view',''), key="edit_ins")

    with st.form("edit_form"):
        name = st.text_input("股票名称", value=stock['name'])
        tags = st.text_input("标签 (逗号分隔)", value=stock['tags'])
        market = st.text_input("市场", value=stock.get('market',''))
        if st.form_submit_button("保存更新"):
            favorite_stocks_table.update_stock(stock['code'], {
                "name": name,
                "tags": tags,
                "market": market,
                "business": new_business,
                "advantage": new_advantage,
                "disadvantage": new_disadvantage,
                "milestones": new_milestones,
                "institution_view": new_institution_view
            })
            st.success("✅ 保存成功！")
            st.session_state.page = 'list'
            st.rerun()

    if st.button("返回列表"):
        st.session_state.page = 'list'
        st.session_state.edit_code = None
        st.rerun()

# --- 添加页面 ---
elif st.session_state.page == 'add':
    st.title("➕ 添加新股票")

    business = st_jodit(value="", key="add_biz")
    advantage = st_jodit(value="", key="add_adv")
    disadvantage = st_jodit(value="", key="add_dis")
    milestones = st_jodit(value="", key="add_mil")
    institution_view = st_jodit(value="", key="add_ins")

    with st.form("add_form"):
        code = st.text_input("股票代码（必填）")
        name = st.text_input("股票名称（必填）")
        tags = st.text_input("标签（逗号分隔）")
        market = st.text_input("所属市场")
        if st.form_submit_button("✅ 保存"):
            if not code or not name:
                st.error("❌ 代码和名称不能为空！")
            else:
                favorite_stocks_table.add_stock(
                    code=code,
                    name=name,
                    tags=tags.split(','),
                    market=market,
                    business=business,
                    advantage=advantage,
                    disadvantage=disadvantage,
                    milestones=milestones,
                    institution_view=institution_view
                )
                st.success("✅ 添加成功！")
                st.session_state.page = 'list'
                st.rerun()

    if st.button("🔙 返回列表"):
        st.session_state.page = 'list'
        st.rerun()