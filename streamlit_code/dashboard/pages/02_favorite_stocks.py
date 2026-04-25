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

    # 功能 3：按标签搜索
    search_tag = st.text_input("按标签搜索 (留空显示全部)", "")

    stocks = favorite_stocks_table.query_stocks(tag_filter=search_tag if search_tag else None)

    # 功能 1：展示列表
    if stocks:
        # 使用表格表头
        cols = st.columns([1, 2, 2, 1])
        cols[0].write("**代码**")
        cols[1].write("**名称**")
        cols[2].write("**标签**")
        cols[3].write("**操作**")

        for s in stocks:
            cols = st.columns([1, 2, 2, 1])
            cols[0].write(s['code'])
            cols[1].write(s['name'])
            cols[2].write(s['tags'])
            # 功能 2：选中一行并进入编辑
            if cols[3].button("编辑", key=f"edit_{s['code']}"):
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