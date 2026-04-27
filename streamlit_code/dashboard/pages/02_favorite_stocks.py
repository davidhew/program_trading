import streamlit as st
from streamlit_jodit import st_jodit
from database import favorite_stocks as favorite_stocks_table

# ==========================
# 1. 状态与 URL 参数同步 (优化点：确保状态持久化)
# ==========================
# 初始化
if 'page' not in st.session_state:
    st.session_state.page = 'list'
if 'edit_code' not in st.session_state:
    st.session_state.edit_code = None
if 'view_code' not in st.session_state:
    st.session_state.view_code = None

# 处理 URL 参数（从 JS 传回的数据）
# 注意：我们先检查参数，存入 session_state，但不立即 clear，
# 而是通过 session_state 来驱动逻辑，保证稳定性。
params = st.query_params
if "v_code" in params:
    st.session_state.view_code = params["v_code"]
if "e_code" in params:
    st.session_state.edit_code = params["e_code"]
    st.session_state.page = 'edit'

# ==========================
# 2. CSS 与 JS 脚本 (优化点：修复 JS 兼容性)
# ==========================
st.markdown("""
<style>
/* 整行容器样式 */
.stock-row-wrapper {
    display: flex;
    align-items: center;
    background-color: #E6F4EA;
    border-radius: 8px;
    margin: 8px 0;
    padding: 12px 15px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    color: #1a1a1a;
}
.stock-row-wrapper:hover {
    background-color: #D4EDDC;
    border: 1px solid #B7E1CD;
    transform: translateY(-1px);
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

/* 列宽度比例 */
.col-code { flex: 1; font-weight: bold; font-family: monospace; }
.col-name { flex: 2; }
.col-market { flex: 1; }
.col-tags { flex: 2; color: #666; font-size: 0.85em; }
.col-action { flex: 1; text-align: right; }

/* 模拟按钮 */
.edit-btn-html {
    background: #ffffff;
    border: 1px solid #dcdcdc;
    padding: 5px 12px;
    border-radius: 5px;
    text-decoration: none;
    color: #333;
    font-size: 13px;
}
.edit-btn-html:hover {
    background: #f8f9fa;
    border-color: #2e7d32;
    color: #2e7d32;
}

/* 详情弹窗 */
.modal-overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.7); z-index: 999999;
    display: flex; align-items: center; justify-content: center;
}
.modal-box {
    background: white; width: 85vw; height: 85vh;
    border-radius: 15px; padding: 35px; overflow-y: auto;
}
</style>

<script>
// 使用 window.location.search 修改参数，这种方式在 Streamlit 中最稳定
function navTo(key, value) {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.location.href = url.href; 
}
</script>
""", unsafe_allow_html=True)

# ==========================
# 3. 详情弹窗逻辑 (独立于页面切换)
# ==========================
if st.session_state.view_code:
    stock = favorite_stocks_table.get_stock_by_code(st.session_state.view_code)
    if stock:
        st.markdown(f"""
        <div class="modal-overlay">
            <div class="modal-box">
                <div style="display:flex; justify-content: space-between; align-items: center;">
                    <h1 style="margin:0;">📊 {stock['name']} <small style="color:#666;">({stock['code']})</small></h1>
                    <a href="/" target="_self" style="background:#444; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">✕ 关闭详情</a>
                </div>
                <hr style="margin:20px 0;">
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px; background:#f9f9f9; padding:15px; border-radius:8px;">
                    <div><b>市场:</b> {stock.get('market', '-')}</div>
                    <div><b>标签:</b> {stock.get('tags', '-')}</div>
                </div>
                <h3 style="color:#2e7d32; border-left:4px solid #2e7d32; padding-left:10px; margin-top:30px;">📌 主营业务</h3>
                <div style="padding:10px;">{stock.get('business', '暂无')}</div>
                <h3 style="color:#c62828; border-left:4px solid #c62828; padding-left:10px; margin-top:20px;">📌 优势</h3>
                <div style="padding:10px;">{stock.get('advantage', '暂无')}</div>
                <h3 style="color:#1565c0; border-left:4px solid #1565c0; padding-left:10px; margin-top:20px;">📌 劣势</h3>
                <div style="padding:10px;">{stock.get('disadvantage', '暂无')}</div>
                <h3 style="color:#ef6c00; border-left:4px solid #ef6c00; padding-left:10px; margin-top:20px;">📌 机构观点</h3>
                <div style="padding:10px;">{stock.get('institution_view', '暂无')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # 点击关闭其实就是刷新 URL，清除参数
        if st.button("清理后台状态并刷新列表"):  # 备用物理按钮
            st.query_params.clear()
            st.session_state.view_code = None
            st.rerun()

# ==========================
# 4. 列表页面
# ==========================
if st.session_state.page == 'list':
    st.title("📈 重点关注股票列表")

    col_add, _ = st.columns([1, 4])
    if col_add.button("➕ 添加新股票", use_container_width=True):
        st.session_state.page = 'add'
        st.rerun()

    # 搜索区域
    with st.expander("🔍 筛选条件", expanded=True):
        c1, c2, c3 = st.columns(3)
        search_tag = c1.text_input("标签")
        search_code = c2.text_input("代码")
        search_name = c3.text_input("名称")

    # 数据获取
    stocks = favorite_stocks_table.query_stocks_by_page(
        tag_filter=search_tag or None,
        code_filter=search_code or None,
        name_filter=search_name or None,
        page=0, page_size=50
    )

    # 渲染表头
    st.markdown("""
        <div style="display: flex; padding: 10px 15px; font-weight: bold; color: #444; border-bottom: 2px solid #2e7d32; margin-bottom:10px;">
            <div class="col-code">代码</div>
            <div class="col-name">名称</div>
            <div class="col-market">市场</div>
            <div class="col-tags">标签</div>
            <div class="col-action">操作</div>
        </div>
    """, unsafe_allow_html=True)

    if stocks:
        for s in stocks:
            code = s['code']
            st.markdown(f"""
                <div class="stock-row-wrapper" ondblclick="navTo('v_code', '{code}')">
                    <div class="col-code">{code}</div>
                    <div class="col-name">{s['name']}</div>
                    <div class="col-market">{s.get('market', '')}</div>
                    <div class="col-tags">{s.get('tags', '')}</div>
                    <div class="col-action">
                        <a href="javascript:void(0)" class="edit-btn-html" onclick="navTo('e_code', '{code}')">编辑</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("未找到匹配股票")

# ==========================
# 5. 编辑页面 (修复空白问题)
# ==========================
elif st.session_state.page == 'edit':
    # 增加二次校验
    edit_code = st.session_state.edit_code
    if not edit_code:
        st.error("未找到待编辑的股票代码")
        if st.button("返回列表"):
            st.session_state.page = 'list'
            st.rerun()
    else:
        stock = favorite_stocks_table.get_stock_by_code(edit_code)
        if not stock:
            st.error(f"数据库中不存在代码为 {edit_code} 的股票")
        else:
            st.title(f"📝 编辑：{stock['name']} ({edit_code})")

            # 使用 container 包裹富文本，防止渲染冲突
            with st.container():
                st.write("---")
                new_business = st_jodit(value=stock.get('business', ''), key="ed_biz")
                new_advantage = st_jodit(value=stock.get('advantage', ''), key="ed_adv")
                new_disadvantage = st_jodit(value=stock.get('disadvantage', ''), key="ed_dis")
                new_ins_view = st_jodit(value=stock.get('institution_view', ''), key="ed_ins")

            with st.form("edit_stock_form"):
                col1, col2 = st.columns(2)
                name = col1.text_input("股票名称", value=stock['name'])
                market = col2.text_input("市场", value=stock.get('market', ''))
                tags = st.text_input("标签 (逗号分隔)", value=stock.get('tags', ''))

                if st.form_submit_button("💾 保存修改", use_container_width=True):
                    favorite_stocks_table.update_stock(edit_code, {
                        "name": name,
                        "tags": tags,
                        "market": market,
                        "business": new_business,
                        "advantage": new_advantage,
                        "disadvantage": new_disadvantage,
                        "institution_view": new_ins_view
                    })
                    st.success("更新成功！")
                    st.session_state.page = 'list'
                    st.session_state.edit_code = None
                    st.query_params.clear()
                    st.rerun()

            if st.button("🔙 放弃修改"):
                st.session_state.page = 'list'
                st.session_state.edit_code = None
                st.query_params.clear()
                st.rerun()

# ==========================
# 6. 添加页面
# ==========================
elif st.session_state.page == 'add':
    st.title("➕ 添加新股票")
    # (添加页代码逻辑基本一致，略...)
    if st.button("返回列表"):
        st.session_state.page = 'list'
        st.rerun()