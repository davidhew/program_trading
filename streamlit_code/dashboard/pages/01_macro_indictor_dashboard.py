import streamlit as st
import pandas as pd
import plotly.express as px
import config as config
import logging
from utility.monitor_strategy import monitor_strategy


logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

net_liquidity_file_name= "net_liquidity.csv"
credit_spread_file_name= "credit_spread.csv"

# 设置页面配置
st.set_page_config(page_title="市场相关宏观数据", layout="wide")

@st.cache_data(ttl=3600)
def load_net_liquidity_data():
    try:
        # 读取 CSV 文件
        df = pd.read_csv(config.USA_STOCK_MACRO_DATA_DIR + net_liquidity_file_name)
        df['date'] = pd.to_datetime(df['date'])

        # 将 date 列转换为日期格式
        df['date'] = pd.to_datetime(df['date'])

        # 按照日期排序
        df = df.sort_values('date')

        # 过滤掉 net_liquidity 为空的数据（防止绘图断点）
        df = df.dropna(subset=['net_liquidity'])

        return df
    except Exception as e:
        logger.error(f"找不到文件，请确保文件与脚本在同一目录下。{e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_credit_spread():
    try:
        # 读取 CSV 文件
        df = pd.read_csv(config.USA_STOCK_MACRO_DATA_DIR + credit_spread_file_name)
        df['date'] = pd.to_datetime(df['date'])

        # 将 date 列转换为日期格式
        df['date'] = pd.to_datetime(df['date'])

        # 按照日期排序
        df = df.sort_values('date')

        return df
    except Exception as e:
        logger.error(f"找不到文件，请确保文件与脚本在同一目录下。{e}")
        return pd.DataFrame()
@monitor_strategy
def show_credit_spread():
    st.title("📈 信用利差 (Credit Spread Indicator)")
    st.markdown("""
        信用利差走阔时，一般表明企业经营/整体经济有问题
        """)
    try:
        # 加载数据
        df = load_credit_spread()

        # 计算时间范围：获取最近3年的数据
        latest_date = df['date'].max()
        three_years_ago = latest_date - pd.DateOffset(years=3)

        # 过滤数据
        df_recent = df[df['date'] >= three_years_ago]

        # --- 展示核心指标卡片 ---
        col1, col2, col3 = st.columns(3)
        current_val = df_recent['high_yield_spread'].iloc[-1]
        prev_val = df_recent['high_yield_spread'].iloc[-2]
        delta = current_val - prev_val

        col1.metric("当前高收益债利差", f"{current_val:,.2f}", f"{delta:+.2f} (较上一期)")
        col2.metric("统计开始日期", three_years_ago.strftime('%Y-%m-%d'))
        col3.metric("最后更新日期", latest_date.strftime('%Y-%m-%d'))

        # --- 1. 确保单位统一 (如果加载数据时没处理，在这里处理) ---


        # --- 2. 使用 Plotly 绘制多线图 ---
        fig = px.line(
            df_recent,
            x='date',
            # 将需要展示的所有列名放入列表
            y=['high_yield_spread', 'investment_grade_spread'],
            title=f"最近三年信用利差趋势 ({three_years_ago.year} - {latest_date.year})",
            labels={
                'value': '利差',
                'date': '日期',
                'variable': '指标项目'
            },
            # 设置不同线条的颜色（可选，Plotly 有默认美观的配色）
            color_discrete_map={
                "high_yield_spread": "#007BFF",  # 蓝色
                "investment_grade_spread": "#FFC107"  # 橙色
            },
            template="plotly_white"
        )

        # --- 3. 优化交互体验 ---
        fig.update_layout(
            hovermode="x unified",  # 鼠标悬停时，同时显示四条线的所有数值
            legend_title_text='指标',  # 图例标题
            yaxis_title="利差"
        )

        # --- 4. (进阶) 让线条粗细有别 ---
        # 让净流动性(net_liquidity)更显眼一点
        fig.update_traces(patch={"line": {"width": 4}}, selector={"name": "high_yield_spread"})

        st.plotly_chart(fig, use_container_width=True)

        # --- 可选：显示原始数据表格 ---
        if st.checkbox("显示最近数据明细"):
            st.dataframe(df_recent.sort_values('date', ascending=False), use_container_width=True)
    except Exception as e:
        print(f"发生错误: {e}")
        logger.error(f"发生错误: {e}")


@monitor_strategy
def show_net_liquidity():
    st.title("📈 美联储净流动性指数 (Net Liquidity Indicator)")
    st.markdown("""
    该指标反映了美联储资产负债表扣除 TGA 账户和 逆回购(ON RRP) 后的实际市场流动性。
    公式：`Net Liquidity = Fed Assets - TGA - ON RRP`
    """)

    try:
        # 加载数据
        df = load_net_liquidity_data()

        # 计算时间范围：获取最近3年的数据
        latest_date = df['date'].max()
        three_years_ago = latest_date - pd.DateOffset(years=3)

        # 过滤数据
        df_recent = df[df['date'] >= three_years_ago]

        # --- 展示核心指标卡片 ---
        col1, col2, col3 = st.columns(3)
        current_val = df_recent['net_liquidity'].iloc[-1]
        prev_val = df_recent['net_liquidity'].iloc[-2]
        delta = current_val - prev_val

        col1.metric("当前净流动性", f"${current_val:,.2f} B", f"{delta:+.2f} B (较上一期)")
        col2.metric("统计开始日期", three_years_ago.strftime('%Y-%m-%d'))
        col3.metric("最后更新日期", latest_date.strftime('%Y-%m-%d'))

        # --- 1. 确保单位统一 (如果加载数据时没处理，在这里处理) ---


        # --- 2. 使用 Plotly 绘制多线图 ---
        fig = px.line(
            df_recent,
            x='date',
            # 将需要展示的所有列名放入列表
            y=['net_liquidity', 'fed_assets', 'tga', 'on_rrp'],
            title=f"最近三年美联储流动性构成趋势 ({three_years_ago.year} - {latest_date.year})",
            labels={
                'value': '金额 (十亿美元)',
                'date': '日期',
                'variable': '指标项目'
            },
            # 设置不同线条的颜色（可选，Plotly 有默认美观的配色）
            color_discrete_map={
                "net_liquidity": "#007BFF",  # 蓝色
                "fed_assets": "#28A745",  # 绿色
                "tga": "#DC3545",  # 红色
                "on_rrp": "#FFC107"  # 橙色
            },
            template="plotly_white"
        )

        # --- 3. 优化交互体验 ---
        fig.update_layout(
            hovermode="x unified",  # 鼠标悬停时，同时显示四条线的所有数值
            legend_title_text='指标',  # 图例标题
            yaxis_title="十亿美元 (Billion $)"
        )

        # --- 4. (进阶) 让线条粗细有别 ---
        # 让净流动性(net_liquidity)更显眼一点
        fig.update_traces(patch={"line": {"width": 4}}, selector={"name": "net_liquidity"})
        fig.update_traces(patch={"line": {"dash": "dot"}}, selector={"name": "tga"})  # TGA 用虚线

        st.plotly_chart(fig, use_container_width=True)

        # --- 可选：显示原始数据表格 ---
        if st.checkbox("显示最近数据明细"):
            st.dataframe(df_recent.sort_values('date', ascending=False), use_container_width=True)
    except Exception as e:
        print(f"发生错误: {e}")
        logger.error(f"发生错误: {e}")


# 最佳实践：确保脚本被直接运行时才执行
if __name__ == "__main__":
    show_net_liquidity()
    show_credit_spread()