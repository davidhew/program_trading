'''

获取美股市场的净流动性指标数据

Net Liquidity = Fed Assets - TGA  ON RRP

|            指标名称            | FRED 代码	|           说明
|      Fed Assets (联储总资产)	| WALCL	    |代表美联储资产负债表的规模，即“放了多少水”。
|      TGA (财政部一般账户)	    |  WDTGAL	|代表政府手里的现金。这部分钱留在美联储，没进入市场。
|      ON RRP (隔夜逆回购)	    |RRPONTSYD	|代表金融机构“淤积”在联储的闲钱。

当这个指数掉头向下时，即便美股还在涨，往往也是“强弩之末”。
---------------------------------
获取隔夜逆回购数据（ON RRP）
隔夜逆回购（ON RRP, Overnight Reverse Repurchase Agreement），我们需要换个视角：把它想象成美联储为市场设立的一个**“超级巨型存钱罐”**。

当市场上钱太多、没处去的时候，金融机构就会把钱投进这个存钱罐，换取美联储手中的抵押品（通常是国债），第二天再换回来并赚取一点点利息。

一、 运作机制：谁在存钱？怎么存？
在常规的“回购”中，美联储是放钱的人；但在**“逆回购”**中，角色互换了：美联储是收钱的人，市场机构是借钱给美联储的人。

1. 参与者（谁有资格存钱？）
并不是所有人都能把钱存给美联储。主要的合格机构包括：

货币市场基金（MMFs）： 这是最核心的参与者，占了绝大部分份额。

政府赞助企业（GSEs）： 如房利美、房地美。

主要交易商（Primary Dealers）： 华尔街的大型投行。

存款类银行。

2. 交易流程
抵押： 每天下午，上述机构把多余的现金交给美联储。美联储把等额的美国国债作为抵押品交给这些机构。

付息： 第二天早上，美联储把钱退还，并支付一笔利息（这个利率即 ON RRP Rate，是美联储利率走廊的下限）。

循环： 这种交易每天发生，所以被称为“隔夜”。

二、 为什么要设立 ON RRP？（核心目的）
美联储设立这个工具，本质上是为了**“控制利率地板”**。

吸收过剩流动性： 当市场上现金泛滥时，由于钱太多，借钱的利率（如短期国库券利率、隔夜融资利率 SOFR）可能会跌破美联储设定的目标区间，甚至变成负利率。

保底收益： 美联储告诉这些大机构：“别在外面低价借钱给别人了，把钱存我这，我给你们固定的利息。”这样，全市场的短期利率就被强行“托住”了。

三、 对市场的影响：为什么它是流动性的“风向标”？
在你的 Python 股票分析程序中，监控 ON RRP 的余额至关重要，因为它直接反映了**“蓄水池里还有多少水”**。

1. 它是股市的“缓冲垫”
释放期（利好股市）： 当 ON RRP 的余额下降时（比如从 2 万亿降到 5000 亿），意味着原本锁在美联储里的钱流出来了，进入了私人银行体系，去买国债或者支持借贷。这相当于变相的“大放水”，能支撑美股估值。

吸水期（压力增加）： 当 ON RRP 余额上升时，意味着市场在抽水，流动性变紧，通常对成长股和高估值标的不利。

2. 与 TGA（财政部账户）的“翘翘板”
如果财政部发了很多国债（TGA增加），而这些国债是被货币基金用 ON RRP 里的钱买走的，那么市场的净流动性就保持不变，股市不会感到疼。

危险时刻： 当 ON RRP 余额见底（比如降到 2000 亿以下），如果美联储还在缩表（QT），或者政府还在大规模发债，那就没有“闲钱”可以用了。这时，银行系统里的准备金（Reserves）就会被抽走，这通常会导致股债双杀。

-------------------------------------------------------------------------------------------------------------------

如果余额接近于零： 说明美联储已经成功把过去几年的过剩资金榨干了。此时，市场的“容错率”极低。

关注利率倒挂： 如果短期国债收益率显著高于 ON RRP 利率，机构会把钱从美联储拿出来买国债，这会继续消耗 ON RRP。
'''

from fredapi import Fred
import pandas as pd
import config
import logging
import certifi
from urllib.request import urlopen

from utility import secrets_config as secrets_config
import os
os.environ['SSL_CERT_FILE'] = certifi.where()


logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
secrets = secrets_config.load_external_config()
file_name="net_liquidity.csv"
def get_data():

    # 替换为你自己的 API Key
    fred = Fred(api_key=secrets.get('FRED_KEY'))

    # 1. 获取三项原始数据
    fed_assets = fred.get_series('WALCL')  # 单位：百万美元 (需除以1000转为十亿)
    tga = fred.get_series('WDTGAL')  # 单位：十亿美元
    on_rrp = fred.get_series('RRPONTSYD')  # 单位：十亿美元

    # 2. 统一单位并合并成 DataFrame
    df = pd.DataFrame({
        'fed_assets': fed_assets / 1000,  # 转换为十亿美元
        'tga': tga/1000,
        'on_rrp': on_rrp
    })

    # 3. 处理缺失值（由于 WALCL 是每周四更新，其余是日更）（ffill代表了前向填充，也就是如果某行的某一列数据缺失，那么找到该行前面最近一行该列非空的数据，以该数据进行填充）
    df = df.ffill()

    # 4. 计算净流动性指数
    df['net_liquidity'] = df['fed_assets'] - df['tga'] - df['on_rrp']
    df.index.name='date'

    #print(df.tail())
    # 将索引转为普通列，并命名为 'date'
    #df = on_rrp.reset_index()
    #df.columns = ['date', 'ON_RRP_Balance']
    df.to_csv(config.USA_STOCK_MACRO_DATA_DIR+file_name,index=True)


