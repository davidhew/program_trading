import streamlit as st

from database import favorite_stocks as stock_table

# --- 数据库初始化 ---

from database import favorite_stocks as favorite_stocks_table

# --- 页面逻辑 ---

# 初始化页面状态：'list' 表示列表页，'edit' 表示编辑页
if 'page' not in st.session_state:
    st.session_state.page = 'list'
if 'edit_code' not in st.session_state:
    st.session_state.edit_code = None

# --- 1. 列表页面 (包含搜索功能) ---
if st.session_state.page == 'list':
    st.title("📈 重点关注股票列表")

    # ======================
    # ✅ 这里加了【添加股票】按钮
    # ======================
    if st.button("➕ 添加股票"):
        st.session_state.page = 'add'
        st.rerun()

    # 功能 3：按标签搜索
    search_tag = st.text_input("按标签搜索 (留空显示全部)", "")
    search_code = st.text_input("按代码搜索 (模糊匹配)", "")
    search_name = st.text_input("按名称搜索 (模糊匹配)", "")

    # 查询数据（三个条件独立生效）
    stocks = favorite_stocks_table.query_stocks(
        tag_filter=search_tag.strip() if search_tag.strip() else None,
        code_filter=search_code.strip() if search_code.strip() else None,
        name_filter=search_name.strip() if search_name.strip() else None
    )

    # 功能 1：展示列表
    if stocks:
        # 使用表格表头
        cols = st.columns([1, 2, 1,2, 1])
        cols[0].write("**代码**")
        cols[1].write("**名称**")
        cols[2].write("**市场**")
        cols[3].write("**标签**")
        cols[4].write("**操作**")

        for s in stocks:
            cols = st.columns([1, 2, 2, 1])
            cols[0].write(s['code'])
            cols[1].write(s['name'])
            cols[2].write(s['market'])
            cols[3].write(s['tags'])
            # 功能 2：选中一行并进入编辑
            if cols[4].button("编辑", key=f"edit_{s['code']}"):
                st.session_state.edit_code = s['code']
                st.session_state.page = 'edit'
                st.rerun()
    else:
        st.info("暂无匹配的股票数据")

# --- 2. 编辑页面 ---
elif st.session_state.page == 'edit':
    stock_code = st.session_state.edit_code
    stock_data = favorite_stocks_table.get_stock_by_code(stock_code)

    st.title(f"📝 编辑股票: {stock_data['name']} ({stock_code})")

    with st.form("edit_form"):
        # 功能 2：编辑框展示当前字段内容
        new_name = st.text_input("股票名称", value=stock_data['name'])
        new_tags = st.text_input("标签 (逗号分隔)", value=stock_data['tags'])
        new_market = st.text_input("市场", value=stock_data['market'])
        new_business = st.text_area("主营业务", value=stock_data.get('business', ''))
        new_advantage = st.text_area("优势", value=stock_data.get('advantage', ''))
        new_disadvantage = st.text_area("劣势", value=stock_data.get('disadvantage', ''))
        new_milestones = st.text_area("重要里程碑", value=stock_data.get('milestones', ''))

        submit_button = st.form_submit_button("保存更新")

        if submit_button:
            # 执行更新逻辑
            update_data = {
                'code': stock_code,
                'name': new_name,
                'tags': new_tags,
                'market': new_market,
                'business': new_business,
                'advantage': new_advantage,
                'disadvantage': new_disadvantage,
                'milestones': new_milestones
            }
            favorite_stocks_table.update_stock(stock_code, update_data)
            st.success("✅ 数据库已更新！")

    # 返回按钮
    if st.button("返回列表"):
        st.session_state.page = 'list'
        st.session_state.edit_code = None
        st.rerun()
# ==============================
elif st.session_state.page == 'add':
    st.title("➕ 添加新股票")

    with st.form("add_form"):
        code = st.text_input("股票代码（必填）")
        name = st.text_input("股票名称（必填）")
        tags = st.text_input("标签（逗号分隔，如：AI,新能源）")
        market = st.text_input("所属市场")
        business = st.text_area("主营业务")
        advantage = st.text_area("优势")
        disadvantage = st.text_area("劣势")
        milestones = st.text_area("重要里程碑")

        # 保存按钮
        save_btn = st.form_submit_button("✅ 保存")

        if save_btn:
            if not code or not name:
                st.error("❌ 股票代码和名称不能为空！")
            else:
                # 保存到数据库
                favorite_stocks_table.add_stock(
                    code=code,
                    name=name,
                    tags=tags.split(','),  # 自动按逗号切割成数组
                    market=market,
                    business=business,
                    advantage=advantage,
                    disadvantage=disadvantage,
                    milestones=milestones
                )
                st.success("✅ 股票添加成功！")
                # 返回列表
                st.session_state.page = 'list'
                st.rerun()

    # 返回按钮
    if st.button("🔙 返回列表"):
        st.session_state.page = 'list'
        st.rerun()

# ==============================