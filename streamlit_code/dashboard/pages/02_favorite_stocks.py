import streamlit as st
from streamlit_jodit import st_jodit

from database import favorite_stocks as favorite_stocks_table

# --- 页面状态初始化 ---
if 'page' not in st.session_state:
    st.session_state.page = 'list'
if 'edit_code' not in st.session_state:
    st.session_state.edit_code = None

# --- 1. 列表页面 ---
if st.session_state.page == 'list':
    st.title("📈 重点关注股票列表")

    if st.button("➕ 添加股票"):
        st.session_state.page = 'add'
        st.rerun()

    # 搜索框
    search_tag = st.text_input("按标签搜索 (留空显示全部)", "")
    search_code = st.text_input("按代码搜索", "")
    search_name = st.text_input("按名称搜索", "")

    page_size = 20

    # 查询总数
    total_count = favorite_stocks_table.query_stocks_count(
        tag_filter=search_tag.strip() or None,
        code_filter=search_code.strip() or None,
        name_filter=search_name.strip() or None
    )

    total_pages = (total_count + page_size - 1) / page_size if total_count > 0 else 1
    page_options = list(range(int(total_pages))) if total_pages > 0 else [0]
    current_page = st.selectbox("页码（从0开始）", page_options, index=0)

    # 查询数据
    stocks = favorite_stocks_table.query_stocks_by_page(
        tag_filter=search_tag.strip() or None,
        code_filter=search_code.strip() or None,
        name_filter=search_name.strip() or None,
        page=current_page,
        page_size=page_size
    )

    # 展示列表
    if stocks:
        cols = st.columns([1, 2, 1, 2, 1])
        cols[0].write("**代码**")
        cols[1].write("**名称**")
        cols[2].write("**市场**")
        cols[3].write("**标签**")
        cols[4].write("**操作**")

        for s in stocks:
            cols = st.columns([1, 2, 1, 2, 1])
            cols[0].write(s['code'])
            cols[1].write(s['name'])
            cols[2].write(s.get('market', ''))
            cols[3].write(s.get('tags', ''))
            if cols[4].button("编辑", key=f"edit_{s['code']}"):
                st.session_state.edit_code = s['code']
                st.session_state.page = 'edit'
                st.rerun()
    else:
        st.info("暂无匹配的股票数据")

# --- 2. 编辑页面（富文本已集成） ---
elif st.session_state.page == 'edit':
    stock_code = st.session_state.edit_code
    stock_data = favorite_stocks_table.get_stock_by_code(stock_code)

    st.title(f"📝 编辑股票: {stock_data['name']} ({stock_code})")

    with st.form("edit_form"):
        new_name = st.text_input("股票名称", value=stock_data['name'])
        new_tags = st.text_input("标签 (逗号分隔)", value=stock_data['tags'])
        new_market = st.text_input("市场", value=stock_data.get('market', ''))

        st.subheader("📊 主营业务")
        new_business = st_jodit(
            value=stock_data.get('business', ''),
            config={"minHeight": 250, "uploader": {"insertImageAsBase64URI": True}}
        )

        st.subheader("📈 优势")
        new_advantage = st_jodit(
            value=stock_data.get('advantage', ''),
            config={"minHeight": 200, "uploader": {"insertImageAsBase64URI": True}}
        )

        st.subheader("📉 劣势")
        new_disadvantage = st_jodit(
            value=stock_data.get('disadvantage', ''),
            config={"minHeight": 200, "uploader": {"insertImageAsBase64URI": True}}
        )

        st.subheader("🏆 重要里程碑")
        new_milestones = st_jodit(
            value=stock_data.get('milestones', ''),
            config={"minHeight": 200, "uploader": {"insertImageAsBase64URI": True}}
        )

        st.subheader("🏛 机构观点")
        new_institution_view = st_jodit(
            value=stock_data.get('institution_view', ''),
            config={"minHeight": 250, "uploader": {"insertImageAsBase64URI": True}}
        )

        submit_button = st.form_submit_button("保存更新")

        if submit_button:
            update_data = {
                'code': stock_code,
                'name': new_name,
                'tags': new_tags,
                'market': new_market,
                'business': new_business,
                'advantage': new_advantage,
                'disadvantage': new_disadvantage,
                'milestones': new_milestones,
                'institution_view': new_institution_view
            }
            favorite_stocks_table.update_stock(stock_code, update_data)
            st.success("✅ 保存成功！")

    if st.button("返回列表"):
        st.session_state.page = 'list'
        st.session_state.edit_code = None
        st.rerun()

# --- 3. 添加页面（富文本已集成） ---
elif st.session_state.page == 'add':
    st.title("➕ 添加新股票")

    with st.form("add_form"):
        code = st.text_input("股票代码（必填）")
        name = st.text_input("股票名称（必填）")
        tags = st.text_input("标签（逗号分隔）")
        market = st.text_input("所属市场")

        st.subheader("📊 主营业务")
        business = st_jodit(
            value="",
            config={"minHeight": 250, "uploader": {"insertImageAsBase64URI": True}}
        )

        st.subheader("📈 优势")
        advantage = st_jodit(value="", config={"minHeight": 200, "uploader": {"insertImageAsBase64URI": True}})

        st.subheader("📉 劣势")
        disadvantage = st_jodit(value="", config={"minHeight": 200, "uploader": {"insertImageAsBase64URI": True}})

        st.subheader("🏆 重要里程碑")
        milestones = st_jodit(value="", config={"minHeight": 200, "uploader": {"insertImageAsBase64URI": True}})

        st.subheader("🏛 机构观点")
        institution_view = st_jodit(value="", config={"minHeight": 250, "uploader": {"insertImageAsBase64URI": True}})

        save_btn = st.form_submit_button("✅ 保存")

        if save_btn:
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