import streamlit as st
import pandas as pd
import plotly.express as px
import config as config
from datetime import datetime, timedelta
import logging

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
file_name="net_liquidity.csv"

# 设置页面配置
st.set_page_config(page_title="美联储净流动性监控", layout="wide")


def load_data():
    # 读取 CSV 文件
    df = pd.read_csv(config.USA_STOCK_MACRO_DATA_DIR + file_name)
    df['date'] = pd.to_datetime(df['date'])

    # 将 date 列转换为日期格式
    df['date'] = pd.to_datetime(df['date'])

    # 按照日期排序
    df = df.sort_values('date')

    # 过滤掉 net_liquidity 为空的数据（防止绘图断点）
    df = df.dropna(subset=['net_liquidity'])

    return df


def main():
    st.title("📈 美联储净流动性指数 (Net Liquidity Indicator)")
    st.markdown("""
    该指标反映了美联储资产负债表扣除 TGA 账户和 逆回购(ON RRP) 后的实际市场流动性。
    公式：`Net Liquidity = Fed Assets - TGA - ON RRP`
    """)

    try:
        # 加载数据
        df = load_data()

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

        # --- 使用 Plotly 绘制交互式折线图 ---
        fig = px.line(
            df_recent,
            x='date',
            y='net_liquidity',
            title=f"最近三年流动性趋势 ({three_years_ago.year} - {latest_date.year})",
            labels={'net_liquidity': '净流动性 (十亿美元)', 'date': '日期'},
            template="plotly_white"
        )

        # 优化图表样式
        fig.update_traces(line_color='#007BFF', line_width=2)
        fig.update_layout(
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor='LightGray'),
            yaxis=dict(showgrid=True, gridcolor='LightGray'),
        )

        # 在 Streamlit 中显示图表
        st.plotly_chart(fig, use_container_width=True)

        # --- 可选：显示原始数据表格 ---
        if st.checkbox("显示最近数据明细"):
            st.dataframe(df_recent.sort_values('date', ascending=False), use_container_width=True)

    except FileNotFoundError:
        logger.error("找不到 net_liquidity.csv 文件，请确保文件与脚本在同一目录下。")
    except Exception as e:
        logger.error(f"发生错误: {e}")