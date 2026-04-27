import streamlit as st
from streamlit_jodit import st_jodit

# --- 状态初始化 ---
if 'page' not in st.session_state:
    st.session_state.page = 'list'
if 'edit_code' not in st.session_state:
    st.session_state.edit_code = None
if 'view_code' not in st.session_state:
    st.session_state.view_code = None

# ==========================
# 全局 CSS + 双击 JS（无报错版）
# ==========================
st.markdown("""
<style>
/* 淡墨绿色背景 */
.stock-card {
    background-color: #E6F4EA;
    padding: 14px;
    border-radius: 8px;
    margin: 6px 0;
    cursor: pointer;
    transition: all 0.2s;
}
.stock-card:hover {
    background-color: #D4EDDC;
}
/* 分割线 */
.divider {
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

<script>
// 双击触发：通过 Streamlit 路由刷新传递代码
function setViewCode(code) {
    window.parent.location.href = window.parent.location.pathname + "?view_code=" + code;
}
</script>
""", unsafe_allow_html=True)

# ==========================
# 修复：新版 Streamlit 获取参数（无 experimental）
# ==========================
query_params = st.query_params  # 新版官方写法
view_code_js = query_params.get("view_code", None)

if view_code_js:
    st.session_state.view_code = view_code_js
    st.query_params.clear()  # 清空参数

# ==========================
# 数据库导入
# ==========================
from database import favorite_stocks as favorite_stocks_table

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

    # 股票列表（双击打开）
    if stocks:
        for idx, s in enumerate(stocks):
            code = s['code']
            st.markdown(f'''
            <div class="stock-card" ondblclick="setViewCode('{code}')">
            ''', unsafe_allow_html=True)

            cols = st.columns([1,2,1,2,1])
            cols[0].write(s['code'])
            cols[1].write(s['name'])
            cols[2].write(s.get('market', ''))
            cols[3].write(s.get('tags', ''))
            if cols[4].button("编辑", key=f"e_{code}"):
                st.session_state.edit_code = code
                st.session_state.page = 'edit'
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

            # 分割线
            if idx != len(stocks)-1:
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    else:
        st.info("暂无股票")

# ==========================
# 双击弹出：全屏只读详情页
# ==========================
if st.session_state.get('view_code'):
    code = st.session_state.view_code
    stock = favorite_stocks_table.get_stock_by_code(code)

    st.markdown('''
    <div class="modal-overlay">
        <div class="modal-box">
    ''', unsafe_allow_html=True)

    # 关闭按钮
    if st.button("❌ 关闭详情页", key="close"):
        st.session_state.view_code = None
        st.rerun()

    st.title(f"📊 {stock['name']} ({code})")
    st.markdown(f"**市场**: {stock.get('market','-')} | **标签**: {stock.get('tags','-')}")
    st.divider()

    # 富文本只读展示
    st.subheader("📌 主营业务")
    st.markdown(stock.get('business','无'), unsafe_allow_html=True)
    st.divider()

    st.subheader("📌 优势")
    st.markdown(stock.get('advantage','无'), unsafe_allow_html=True)
    st.divider()

    st.subheader("📌 劣势")
    st.markdown(stock.get('disadvantage','无'), unsafe_allow_html=True)
    st.divider()

    st.subheader("📌 重要里程碑")
    st.markdown(stock.get('milestones','无'), unsafe_allow_html=True)
    st.divider()

    st.subheader("📌 机构观点")
    st.markdown(stock.get('institution_view','无'), unsafe_allow_html=True)

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

    with st.form("edit"):
        name = st.text_input("名称", value=stock['name'])
        tags = st.text_input("标签", value=stock['tags'])
        market = st.text_input("市场", value=stock.get('market',''))
        if st.form_submit_button("保存"):
            favorite_stocks_table.update_stock(stock['code'], {
                "name":name,"tags":tags,"market":market,
                "business":new_business,"advantage":new_advantage,
                "disadvantage":new_disadvantage,"milestones":new_milestones,
                "institution_view":new_institution_view
            })
            st.success("保存成功")
            st.session_state.page = 'list'
            st.rerun()
    if st.button("返回"):
        st.session_state.page='list'
        st.rerun()

# --- 添加页面 ---
elif st.session_state.page == 'add':
    st.title("➕ 添加股票")
    biz = st_jodit(value="", key="add_biz")
    adv = st_jodit(value="", key="add_adv")
    dis = st_jodit(value="", key="add_dis")
    mil = st_jodit(value="", key="add_mil")
    ins = st_jodit(value="", key="add_ins")

    with st.form("add"):
        code = st.text_input("股票代码")
        name = st.text_input("名称")
        tags = st.text_input("标签")
        market = st.text_input("市场")
        if st.form_submit_button("保存"):
            favorite_stocks_table.add_stock(
                code=code,name=name,tags=tags.split(','),market=market,
                business=biz,advantage=adv,disadvantage=dis,milestones=mil,institution_view=ins
            )
            st.success("添加成功")
            st.session_state.page='list'
            st.rerun()
    if st.button("返回"):
        st.session_state.page='list'
        st.rerun()