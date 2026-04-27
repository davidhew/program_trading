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

# 处理 URL 参数实现 JS 到 Streamlit 的通信
params = st.query_params
if "view_code" in params:
    st.session_state.view_code = params["view_code"]
    st.query_params.clear() # 处理完清空，防止刷新重复触发
if "edit_code" in params:
    st.session_state.edit_code = params["edit_code"]
    st.session_state.page = 'edit'
    st.query_params.clear()

# --- 2. CSS 样式修复 ---
st.markdown("""
<style>
/* 股票整行容器：Flex 布局模拟列 */
.stock-row-wrapper {
    display: flex;
    align-items: center;
    background-color: #E6F4EA;
    border-radius: 8px;
    margin: 8px 0;
    padding: 12px 15px;
    cursor: pointer;
    transition: background-color 0.2s;
    border: 1px solid transparent;
}
.stock-row-wrapper:hover {
    background-color: #D4EDDC;
    border: 1px solid #B7E1CD;
}

/* 列宽度比例控制 (需与表头对应) */
.col-code { flex: 1; font-weight: bold; }
.col-name { flex: 2; }
.col-market { flex: 1; }
.col-tags { flex: 2; color: #555; font-size: 0.9em; }
.col-action { flex: 1; text-align: right; }

/* 模拟按钮样式 */
.edit-link {
    background: white;
    border: 1px solid #ccc;
    padding: 4px 12px;
    border-radius: 4px;
    text-decoration: none;
    color: #333;
    font-size: 14px;
}
.edit-link:hover {
    background: #f0f0f0;
}

/* 全屏弹窗样式保持不变 */
.modal-overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.8); z-index: 99999;
    display: flex; align-items: center; justify-content: center;
}
.modal-box {
    background: white; width: 90vw; height: 85vh;
    border-radius: 12px; padding: 40px; overflow-y: auto; position: relative;
}
</style>

<script>
// 双击跳转：修改父级 URL 参数触发 Streamlit 重绘
function handleDblClick(code) {
    const url = new URL(window.parent.location.href);
    url.searchParams.set("view_code", code);
    window.parent.location.href = url.href;
}
// 单击编辑跳转
function handleEdit(code) {
    const url = new URL(window.parent.location.href);
    url.searchParams.set("edit_code", code);
    window.parent.location.href = url.href;
}
</script>
""", unsafe_allow_html=True)

# --- 3. 列表逻辑 ---
if st.session_state.page == 'list':
    st.title("📈 重点关注股票列表")

    if st.button("➕ 添加股票"):
        st.session_state.page = 'add'
        st.rerun()

    # 搜索栏 (简化展示)
    c1, c2, c3 = st.columns(3)
    search_tag = c1.text_input("标签搜索")
    search_code = c2.text_input("代码搜索")
    search_name = c3.text_input("名称搜索")

    # 分页逻辑 (保持你的原逻辑)
    total_count = favorite_stocks_table.query_stocks_count(
        tag_filter=search_tag.strip() or None,
        code_filter=search_code.strip() or None,
        name_filter=search_name.strip() or None
    )
    total_pages = max((total_count + 19) // 20, 1)
    current_page = st.selectbox("页码", list(range(total_pages)))

    stocks = favorite_stocks_table.query_stocks_by_page(
        tag_filter=search_tag.strip() or None,
        code_filter=search_code.strip() or None,
        name_filter=search_name.strip() or None,
        page=current_page, page_size=20
    )

    # 渲染自定义表头
    st.markdown("""
        <div style="display: flex; padding: 10px 15px; font-weight: bold; color: #666; border-bottom: 2px solid #eee;">
            <div class="col-code">代码</div>
            <div class="col-name">名称</div>
            <div class="col-market">市场</div>
            <div class="col-tags">标签</div>
            <div class="col-action">操作</div>
        </div>
    """, unsafe_allow_html=True)

    # 渲染每一行
    if stocks:
        for s in stocks:
            code = s['code']
            tags_display = s.get('tags', '')
            # 使用一个完整的 HTML 块渲染整行
            st.markdown(f"""
                <div class="stock-row-wrapper" ondblclick="handleDblClick('{code}')">
                    <div class="col-code">{code}</div>
                    <div class="col-name">{s['name']}</div>
                    <div class="col-market">{s.get('market', '')}</div>
                    <div class="col-tags">{tags_display}</div>
                    <div class="col-action">
                        <a href="javascript:void(0)" class="edit-link" onclick="handleEdit('{code}')">编辑</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无数据")

    # --- 4. 详情弹窗 (Modal) ---
    if st.session_state.view_code:
        stock = favorite_stocks_table.get_stock_by_code(st.session_state.view_code)
        if stock:
            # 弹窗 HTML 结构
            st.markdown(f"""
            <div class="modal-overlay">
                <div class="modal-box">
                    <div style="display:flex; justify-content: space-between; align-items: center;">
                        <h1>📊 {stock['name']} ({stock['code']})</h1>
                        <a href="/" target="_self" style="background:#ff4444; color:white; padding:8px 20px; border-radius:6px; text-decoration:none;">关闭详情</a>
                    </div>
                    <hr>
                    <p><b>市场:</b> {stock.get('market', '-')} | <b>标签:</b> {stock.get('tags', '-')}</p>
                    <h3>📌 主营业务</h3>{stock.get('business', '暂无')}
                    <h3>📌 优势</h3>{stock.get('advantage', '暂无')}
                    <h3>📌 劣势</h3>{stock.get('disadvantage', '暂无')}
                    <h3>📌 机构观点</h3>{stock.get('institution_view', '暂无')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 备选：如果需要在 Modal 内使用 Streamlit 组件，
            # 则不能用上面的全 HTML，但目前双击弹窗建议保持这种纯 HTML 覆盖层。


# ---5. 编辑页面 ---
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