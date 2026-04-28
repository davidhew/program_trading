import streamlit as st
from streamlit_jodit import st_jodit
from database import favorite_stocks as favorite_stocks_table

# --- 1. 基础配置 ---
st.set_page_config(layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'list'
if 'edit_code' not in st.session_state:
    st.session_state.edit_code = None
if 'view_code' not in st.session_state:
    st.session_state.view_code = None

# ==========================
# 2. 核心：处理 URL 参数 (放在最前面)
# ==========================
params = st.query_params
# 如果 URL 中有 v_code，说明是要查看详情
if "v_code" in params:
    st.session_state.view_code = params["v_code"]
    # 立即清除参数防止刷新时反复弹窗，但要配合 rerun
    st.query_params.clear()
    st.rerun()

# 如果 URL 中有 e_code，说明是要进入编辑
if "e_code" in params:
    st.session_state.edit_code = params["e_code"]
    st.session_state.page = 'edit'
    st.query_params.clear()
    st.rerun()

# ==========================
# 3. 样式与脚本修复 (解决 React #231 报错)
# ==========================
st.html("""
<style>
.stock-row-container {
    display: flex;
    align-items: center;
    background-color: #E6F4EA;
    border-radius: 8px;
    margin: 8px 0;
    padding: 12px 15px;
    cursor: pointer;
    transition: background 0.2s;
    border: 1px solid transparent;
}
.stock-row-container:hover {
    background-color: #D4EDDC;
    border-color: #B7E1CD;
}
.col-code { flex: 1; font-weight: bold; }
.col-name { flex: 2; }
.col-market { flex: 1; }
.col-tags { flex: 2; color: #666; }
.col-action { flex: 1; text-align: right; }

/* 详情遮罩层 */
.modal-overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.7); z-index: 9999;
    display: flex; align-items: center; justify-content: center;
}
.modal-box {
    background: white; width: 85vw; height: 85vh;
    border-radius: 12px; padding: 30px; overflow-y: auto; color: black;
}
</style>

<script>
// 动态绑定事件，避免 React 属性注入错误
function setupListeners() {
    const rows = window.parent.document.querySelectorAll('.stock-row-container');
    rows.forEach(row => {
        // 防止重复绑定
        if (row.getAttribute('data-bound')) return;

        const code = row.getAttribute('data-code');

        // 双击查看详情
        row.addEventListener('dblclick', () => {
            const url = new URL(window.parent.location.href);
            url.searchParams.set('v_code', code);
            window.parent.location.href = url.href;
        });

        // 点击编辑按钮 (查找内部的编辑链接)
        const editBtn = row.querySelector('.edit-trigger');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // 阻止触发整行的双击/单击
                const url = new URL(window.parent.location.href);
                url.searchParams.set('e_code', code);
                window.parent.location.href = url.href;
            });
        }

        row.setAttribute('data-bound', 'true');
    });
}

// 每隔一秒检查一次是否有新行渲染出来
setInterval(setupListeners, 1000);
</script>
""", unsafe_allow_javascript=True)

# ==========================
# 4. 详情弹窗逻辑
# ==========================
if st.session_state.view_code:
    code = st.session_state.view_code
    stock = favorite_stocks_table.get_stock_by_code(code)
    if stock:
        st.markdown(f"""
        <div class="modal-overlay">
            <div class="modal-box">
                <div style="display:flex; justify-content:space-between;">
                    <h2>📊 {stock['name']} ({code})</h2>
                    <a href="/" target="_self" style="padding:8px 15px; background:#444; color:white; border-radius:5px; text-decoration:none;">关闭</a>
                </div>
                <hr>
                <div style="line-height:1.6;">
                    <p><b>市场:</b> {stock.get('market', '-')} | <b>标签:</b> {stock.get('tags', '-')}</p>
                    <h4>📌 主营业务</h4><div>{stock.get('business', '暂无内容')}</div>
                    <h4>📌 优势</h4><div>{stock.get('advantage', '暂无内容')}</div>
                    <h4>📌 劣势</h4><div>{stock.get('disadvantage', '暂无内容')}</div>
                    <h4>📌 机构观点</h4><div>{stock.get('institution_view', '暂无内容')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # 提供一个备用的 Streamlit 按钮清除状态
        if st.button("返回列表", key="back_btn_modal"):
            st.session_state.view_code = None
            st.rerun()

# ==========================
# 5. 主列表页面
# ==========================
if st.session_state.page == 'list':
    st.title("📈 重点关注股票列表")

    if st.button("➕ 添加股票"):
        st.session_state.page = 'add'
        st.rerun()

    stocks = favorite_stocks_table.query_stocks_by_page(page=0, page_size=50)

    # 表头
    st.markdown("""
        <div style="display: flex; padding: 10px 15px; font-weight: bold; border-bottom: 2px solid #eee;">
            <div class="col-code">代码</div><div class="col-name">名称</div>
            <div class="col-market">市场</div><div class="col-tags">标签</div>
            <div class="col-action">操作</div>
        </div>
    """, unsafe_allow_html=True)

    # 列表内容
    for s in stocks:
        code = s['code']
        # 注意：这里不再写 ondblclick，而是写 data-code
        st.markdown(f"""
        <div class="stock-row-container" data-code="{code}">
            <div class="col-code">{code}</div>
            <div class="col-name">{s['name']}</div>
            <div class="col-market">{s.get('market', '')}</div>
            <div class="col-tags">{s.get('tags', '')}</div>
            <div class="col-action">
                <button class="edit-trigger" style="cursor:pointer; padding:2px 8px;">编辑</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================
# 6. 编辑页面 (修复空白问题)
# ==========================
elif st.session_state.page == 'edit':
    edit_code = st.session_state.edit_code
    stock = favorite_stocks_table.get_stock_by_code(edit_code)

    if not stock:
        st.error(f"未找到股票数据: {edit_code}")
        if st.button("返回列表"):
            st.session_state.page = 'list'
            st.rerun()
    else:
        st.title(f"📝 编辑：{stock['name']} ({edit_code})")

        # 修复：将编辑器放在 form 之外或确保 key 唯一
        # Jodit 编辑器在某些 Streamlit 版本中不能很好地在 form 里初始化
        st.write("---")
        b_val = st_jodit(stock.get('business', ''), key="ed_b")
        a_val = st_jodit(stock.get('advantage', ''), key="ed_a")
        d_val = st_jodit(stock.get('disadvantage', ''), key="ed_d")
        i_val = st_jodit(stock.get('institution_view', ''), key="ed_i")

        with st.form("save_form"):
            name = st.text_input("股票名称", value=stock['name'])
            market = st.text_input("市场", value=stock.get('market', ''))
            tags = st.text_input("标签", value=stock.get('tags', ''))

            if st.form_submit_button("💾 保存更新"):
                favorite_stocks_table.update_stock(edit_code, {
                    "name": name, "market": market, "tags": tags,
                    "business": b_val, "advantage": a_val,
                    "disadvantage": d_val, "institution_view": i_val
                })
                st.success("更新成功！")
                st.session_state.page = 'list'
                st.session_state.edit_code = None
                st.rerun()

        if st.button("🔙 取消"):
            st.session_state.page = 'list'
            st.session_state.edit_code = None
            st.rerun()

# ==========================
# 7. 添加页面 (略)
# ==========================
elif st.session_state.page == 'add':
    st.title("➕ 添加新股票")
    if st.button("返回"):
        st.session_state.page = 'list'
        st.rerun()