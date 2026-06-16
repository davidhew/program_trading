import streamlit as st
import math
from streamlit_jodit import st_jodit
from database import knowledge_doc as knowledge_doc_table
import logging
logger = logging.getLogger("dashboard")

# --- 1. 基础配置 ---
st.set_page_config(layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'list'
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None
if 'view_id' not in st.session_state:
    st.session_state.view_id = None

# 初始化搜索与分页状态
if 'search_title' not in st.session_state:
    st.session_state.search_title = ""
if 'search_tag' not in st.session_state:
    st.session_state.search_tag = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# ==========================
# 2. 核心：处理 URL 参数 (放在最前面)
# ==========================
params = st.query_params
# 如果 URL 中有 v_code，说明是要查看详情
if "v_id" in params:
    st.session_state.view_id = params["v_id"]
    # 立即清除参数防止刷新时反复弹窗，但要配合 rerun
    st.query_params.clear()
    st.rerun()

# 如果 URL 中有 e_code，说明是要进入编辑
if "e_id" in params:
    logger.info("e_id is:"+params["e_id"])
    st.session_state.edit_id = params["e_id"]
    st.session_state.page = 'edit'
    st.query_params.clear()
    st.rerun()

# ==========================
# 3. 样式与脚本修复 (解决 React #231 报错)
# ==========================
# ==========================
# 3. 样式与脚本修复 (完美解决 React #231 及动态刷新问题)
# ==========================
st.html("""
<style>
.doc-row-container {
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
.doc-row-container:hover {
    background-color: #D4EDDC;
    border-color: #B7E1CD;
}
.col-date { flex: 1; font-weight: bold; }
.col-title { flex: 1; }
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
// 使用事件委托：直接监听父级 document 的全局点击与双击事件
// 这样无论 Streamlit 如何局部刷新 DOM 列表，只要带有对应 class 的元素被触发，就能实时拿到它当前的最新 data-code。
(function() {
    const parentDoc = window.parent.document;

    // 防止在全局范围内重复初始化监听器
    if (parentDoc.__tmb_listeners_bound__) return;

    // 1. 全局双击事件监听：查看详情
    parentDoc.addEventListener('dblclick', function(e) {
        // 向上寻找是否点击在 stock-row-container 行内部
        const row = e.target.closest('.doc-row-container');
        if (row) {
            const docId = row.getAttribute('doc-id');
            if (docId) {
                const url = new URL(parentDoc.location.href);
                url.searchParams.set('v_id', docId);
                parentDoc.location.href = url.href;
            }
        }
    });

    // 2. 全局点击事件监听：处理编辑按钮点击
    parentDoc.addEventListener('click', function(e) {
        // 检查点击的元素是否是编辑按钮（或者其内部节点）
        const editBtn = e.target.closest('.edit-trigger');
        if (editBtn) {
            e.stopPropagation(); // 阻止冒泡
            const row = editBtn.closest('.doc-row-container');
            if (row) {
                const docId = row.getAttribute('doc-id');
                if (docId) {
                    const url = new URL(parentDoc.location.href);
                    url.searchParams.set('e_id', docId);
                    parentDoc.location.href = url.href;
                }
            }
        }
    });

    // 标记已绑定状态，防止无限叠加
    parentDoc.__tmb_listeners_bound__ = true;
    console.log("Global event delegation for knowledge doc table successfully initialized.");
})();
</script>
""", unsafe_allow_javascript=True)

# ==========================
# 4. 详情弹窗逻辑
# ==========================
if st.session_state.view_id:
    doc_id = st.session_state.view_id
    doc = knowledge_doc_table.get_doc_by_id(doc_id)
    if doc:
        st.markdown(f"""
        <div class="modal-overlay">
            <div class="modal-box">
                <div style="display:flex; justify-content:space-between;">
                    <p><b>📊 {doc['title']} </b></p>
                    <a href="/knowledge_doc" target="_self" style="padding:4px 15px; background:#444; color:white; border-radius:5px; text-decoration:none;">关闭</a>
                </div>
                <hr>
                <div style="line-height:1.6;">
                    <p><b>创建日期:</b> {doc.get('create_time', '-').strftime('%Y-%m-%d')}</p>
                    <p><b>文章来源:</b> {doc.get('source', '-')}</p>
                    <p><b>标签:</b> {doc.get('tags', '-')}</p>
                    <p><b>内容</b></p><div>{doc.get('content', '暂无内容')}</div>
           
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # 提供一个备用的 Streamlit 按钮清除状态
        if st.button("返回列表", key="back_btn_modal"):
            st.session_state.view_id = None
            st.rerun()

# ==========================
# 5. 主列表页面
# ==========================
if st.session_state.page == 'list':
    st.title("知识库文档")

    if st.button("➕ 添加文档"):
        st.session_state.page = 'add'
        st.rerun()
    with st.container():
        col_search1, col_search2 = st.columns(2)
        with col_search1:
            search_title = st.text_input("文档标题搜索", value=st.session_state.search_title,
                                        placeholder="输入标调模糊搜索...")
        with col_search2:
            search_tag = st.text_input("文档标签搜索", value=st.session_state.search_tag,
                                       placeholder="输入标签模糊搜索...")

        # 如果搜索词改变，重置页码到第1页
        if search_title != st.session_state.search_title or search_tag != st.session_state.search_tag :
            st.session_state.search_title = search_title
            st.session_state.search_tag = search_tag
            st.session_state.current_page = 1
            st.rerun()
    total_count = knowledge_doc_table.query_doc_count(tag_filter=search_tag,title_filter=search_title)
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

    docs = knowledge_doc_table.query_doc_by_page(tag_filter=search_tag,title_filter=search_title,page=st.session_state.current_page-1, page_size=PAGE_SIZE)

    # --- 列表展示 ---
    st.write(f"共找到 {total_count} 条记录，当前第 {st.session_state.current_page}/{total_pages} 页")

    # 表头
    st.markdown("""
        <div style="display: flex; padding: 10px 15px; font-weight: bold; border-bottom: 2px solid #eee;">
            <div class="col-date">创建日期</div><div class="col-title">名称</div>
            <div class="col-tags">标签</div>
            <div class="col-action">操作</div>
        </div>
    """, unsafe_allow_html=True)

    # 列表内容
    for doc in docs:
        doc_id = doc['id']
        # 注意：这里不再写 ondblclick，而是写 data-code
        st.markdown(f"""
        <div class="doc-row-container" doc-id="{doc_id}">
            <div class="col-date">{doc['create_time'].strftime('%Y-%m-%d')}</div>
            <div class="col-title">{doc['title']}</div>
            <div class="col-tags">{doc.get('tags', '')}</div>
            <div class="col-action">
                <button class="edit-trigger" style="cursor:pointer; padding:2px 8px;">编辑</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================
# 6. 编辑页面 (修复空白问题)
# ==========================
elif st.session_state.page == 'edit':
    edit_id = st.session_state.edit_id
    doc = knowledge_doc_table.get_doc_by_id(edit_id)

    if not doc:
        st.error(f"未找到文档数据: {edit_id}")
        if st.button("返回列表"):
            st.session_state.page = 'list'
            st.rerun()
    else:
        st.title(f"📝 编辑：{doc['title']}")

        # 修复：将编辑器放在 form 之外或确保 key 唯一
        # Jodit 编辑器在某些 Streamlit 版本中不能很好地在 form 里初始化
        st.write("---")

        title = st.text_input("标题", value=doc.get('title', ''))
        source = st.text_input("文章来源", value=doc.get('source', ''))
        tags = st.text_input("标签", value=doc.get('tags', ''))
        # 1. 文档内容
        st.markdown("###内容")
        new_content = st_jodit(value=doc.get('content', ''), key="ed_c")



        # 3. 操作按钮布局
        col1, col2 = st.columns([1, 5])

        with col1:
            # 使用普通的 st.button
            if st.button("💾 保存更新", type="primary"):

                knowledge_doc_table.update_doc({
                    "id": edit_id,
                    "title": title,
                    "source": source,
                    "tags": ",".join((tags or "").split()),
                    "content": new_content
                })
                st.success("更新成功！")
                # 延迟一下再跳转，确保用户看到成功提示
                import time

                time.sleep(1)
                st.session_state.page = 'list'
                st.session_state.edit_id = None
                st.rerun()

        with col2:
            if st.button("🔙 取消"):
                st.session_state.page = 'list'
                st.session_state.edit_id = None
                st.rerun()

# ==========================
# 7. 添加页面 (略)
# ==========================
# ==========================
# 7. 添加页面 (完整版 - 集成富文本)
# ==========================
elif st.session_state.page == 'add':
    st.title("➕ 添加新文档")

    # 普通输入字段
    st.write("---")
    title = st.text_input("标题（必填）")
    source = st.text_input("文章来源")
    tags = st.text_input("标签（逗号分隔，如：AI,新能源,算力）")

    # 富文本编辑器区域
    st.write("---")
    st.markdown("### 内容")
    content = st_jodit(value="", key="add_content")


    # 按钮区域
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("✅ 保存文档", type="primary"):
            if not title or not content:
                st.error("❌ 文档标题和内容不能为空！")
            else:
                # 插入数据库
                knowledge_doc_table.add_doc(
                    title=title,
                    source=source,
                    tags=",".join((tags or "").split()),
                    content=content
                )
                st.success("✅ 文档添加成功！")
                import time
                time.sleep(1)
                st.session_state.page = "list"
                st.rerun()

    with col2:
        if st.button("🔙 返回列表"):
            st.session_state.page = "list"
            st.rerun()