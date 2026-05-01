import streamlit as st
import math
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

# 初始化搜索与分页状态
if 'search_code' not in st.session_state:
    st.session_state.search_code = ""
if 'search_tag' not in st.session_state:
    st.session_state.search_tag = ""
if 'search_name' not in st.session_state:
    st.session_state.search_name = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

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
/* 搜索框容器样式 */
.search-container {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
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
                    <p><b>📊 {stock['name']} ({code})</b></p>
                    <a href="/favorite_stocks" target="_self" style="padding:4px 15px; background:#444; color:white; border-radius:5px; text-decoration:none;">关闭</a>
                </div>
                <hr>
                <div style="line-height:1.6;">
                    <p><b>市场:</b> {stock.get('market', '-')} | <b>标签:</b> {stock.get('tags', '-')}</p>
                    <p><b>主营业务</b></p><div>{stock.get('business', '暂无内容')}</div>
                    <p><b>优势</b></p><div>{stock.get('advantage', '暂无内容')}</div>
                    <p><b>劣势</b></p><div>{stock.get('disadvantage', '暂无内容')}</div>
                    <p><b>重要里程碑</b></p><div>{stock.get('milestones', '暂无内容')}</div>
                    <p><b>机构观点</b></p><div>{stock.get('institution_view', '暂无内容')}</div>
                    <p><b>财报信息</b></p><div>{stock.get('financial_statements', '暂无内容')}</div>
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
    with st.container():
        col_search1, col_search2,col_search3 = st.columns(3)
        with col_search1:
            search_code = st.text_input("股票代码搜索", value=st.session_state.search_code,
                                        placeholder="输入代码模糊搜索...")
        with col_search2:
            search_name = st.text_input("股票名称搜索", value=st.session_state.search_name,
                                       placeholder="输入名称模糊搜索...")
        with col_search3:
            search_tag = st.text_input("股票标签搜索", value=st.session_state.search_tag,
                                       placeholder="输入标签模糊搜索...")
        # 如果搜索词改变，重置页码到第1页
        if search_code != st.session_state.search_code or search_tag != st.session_state.search_tag or search_name!=st.session_state.search_name:
            st.session_state.search_code = search_code
            st.session_state.search_tag = search_tag
            st.session_state.search_name = search_name
            st.session_state.current_page = 1
            st.rerun()
    total_count = favorite_stocks_table.query_stocks_count(tag_filter=search_tag,code_filter=search_code,name_filter=search_name)
    PAGE_SIZE=20
    total_pages = math.ceil(total_count / PAGE_SIZE) if total_count > 0 else 1

    page_options = list(range(1, total_pages + 1))
    selected_page = st.selectbox(
        "跳转至页码",
        options=page_options,
        index=st.session_state.current_page - 1 if st.session_state.current_page <= total_pages else 0,
        key="page_selector"
    )

    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

    stocks = favorite_stocks_table.query_stocks_by_page(tag_filter=search_tag,code_filter=search_code,name_filter=search_name,page=st.session_state.current_page-1, page_size=PAGE_SIZE)

    # --- 列表展示 ---
    st.write(f"共找到 {total_count} 条记录，当前第 {st.session_state.current_page}/{total_pages} 页")

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
        # 1. 业务描述
        st.markdown("###业务描述")
        new_business = st_jodit(value=stock.get('business', ''), key="ed_b")
        st.markdown("###竞争优势")
        new_advantage = st_jodit(value=stock.get('advantage', ''), key="ed_a")
        st.markdown("###竞争劣势&风险")
        new_disadvantage = st_jodit(value=stock.get('disadvantage', ''), key="ed_d")

        st.markdown("###重要里程碑")
        new_milestones = st_jodit(value=stock.get('milestones', ''), key="ed_m")

        st.markdown("###机构观点")
        new_institution_view = st_jodit(value=stock.get('institution_view', ''), key="ed_i")


        st.markdown("###财报信息")
        new_financial_statements = st_jodit(value=stock.get('financial_statements', ''), key="ed_f")


        name = st.text_input("股票名称", value=stock['name'])
        market = st.text_input("市场", value=stock.get('market', ''))
        tags = st.text_input("标签", value=stock.get('tags', ''))

        # 3. 操作按钮布局
        col1, col2 = st.columns([1, 5])

        with col1:
            # 使用普通的 st.button
            if st.button("💾 保存更新", type="primary"):
                print("new_business is:"+new_business)
                favorite_stocks_table.update_stock(edit_code, {
                    "code":edit_code,
                    "name": name,
                    "market": market,
                    "tags": ",".join((tags or "").split()),
                    "business": new_business,
                    "advantage": new_advantage,
                    "disadvantage": new_disadvantage,
                    "institution_view": new_institution_view,
                    "financial_statements": new_financial_statements,
                    "milestones": new_milestones
                })
                st.success("更新成功！")
                # 延迟一下再跳转，确保用户看到成功提示
                import time

                time.sleep(1)
                st.session_state.page = 'list'
                st.session_state.edit_code = None
                st.rerun()

        with col2:
            if st.button("🔙 取消"):
                st.session_state.page = 'list'
                st.session_state.edit_code = None
                st.rerun()

# ==========================
# 7. 添加页面 (略)
# ==========================
# ==========================
# 7. 添加页面 (完整版 - 集成富文本)
# ==========================
elif st.session_state.page == 'add':
    st.title("➕ 添加新股票")

    # 普通输入字段
    st.write("---")
    code = st.text_input("股票代码（必填）")
    name = st.text_input("股票名称（必填）")
    market = st.text_input("市场（如：A股,美股）")
    tags = st.text_input("标签（逗号分隔，如：AI,新能源,算力）")

    # 富文本编辑器区域
    st.write("---")
    st.markdown("### 业务描述")
    business = st_jodit(value="", key="add_business")

    st.markdown("### 竞争优势")
    advantage = st_jodit(value="", key="add_advantage")

    st.markdown("### 竞争劣势&风险")
    disadvantage = st_jodit(value="", key="add_disadvantage")

    st.markdown("### 机构观点")
    institution_view = st_jodit(value="", key="add_institution_view")

    st.markdown("### 重要里程碑")
    milestones = st_jodit(value="", key="add_milestones")

    st.markdown("###财报信息")
    financial_statements = st_jodit(value="", key="financial_statements")



    # 按钮区域
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("✅ 保存股票", type="primary"):
            if not code or not name:
                st.error("❌ 股票代码和名称不能为空！")
            else:
                # 插入数据库
                favorite_stocks_table.add_stock(
                    code=code,
                    name=name,
                    market=market,
                    tags=",".join((tags or "").split()),
                    business=business,
                    advantage=advantage,
                    disadvantage=disadvantage,
                    institution_view=institution_view,
                    milestones=milestones,
                    financial_statements=financial_statements
                )
                st.success("✅ 股票添加成功！")
                import time
                time.sleep(1)
                st.session_state.page = "list"
                st.rerun()

    with col2:
        if st.button("🔙 返回列表"):
            st.session_state.page = "list"
            st.rerun()