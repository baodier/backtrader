from datetime import datetime
import backtrader as bt
from utils.abroker import ABroker
import argparse
# Create a subclass of Strategy to define the indicators and logic

class RandomStrategy(bt.Strategy):
    def __init__(self):
        pass

    # 日志函数
    def log(self, txt, dt=None):
        '''日志函数'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，无动作
            return

        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行, {}, pos={}'.format(order.executed.price, self.getposition().size))

            elif order.issell():
                self.log('卖单执行, {}, pos={}'.format(order.executed.price, self.getposition().size))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单 Canceled/Margin/Rejected')

    def next(self):
        if self.data.close[0] > self.data.open[0]:  # 当前收盘价高于开盘价
            self.log('will buy, pos={}'.format(self.getposition().size))
            self.buy(size=100)  # 买入操作
        else:
            pos = self.getposition().size
            sell_size = 100 if pos >= 100 else pos
            # print('sell_size={}'.format(sell_size))
            if sell_size > 0:
                self.log('will sell, pos={}'.format(self.getposition().size))
                self.sell(size=sell_size)  # 卖出操作
            else:
                self.log('no position, cannot sell')



cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

# Create a data feed
# args = parse_args()
# 创建行情数据对象，加载数据
data = bt.feeds.GenericCSVData(
    dataname='data/sh600000',
    datetime=0,  # 日期行所在列
    open=2,  # 开盘价所在列
    high=3,  # 最高价所在列
    low=4,  # 最低价所在列
    close=5,  # 收盘价价所在列
    volume=6,  # 成交量所在列
    openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
    dtformat=('%Y-%m-%d %H:%M:%S'),  # 日期格式
    # tmformat=('%H:%M:%S'),  # 时间格式
    fromdate=datetime(2023, 7, 1),  # 起始日
    todate=datetime(2023, 7, 5),
    timeframe=bt.TimeFrame.Minutes
)  # 结束日

cerebro.adddata(data)
# cerebro.broker = bt.brokers.BackBroker(**eval('dict(' + args.broker + ')'))
cerebro.setbroker(ABroker())
cerebro.addstrategy(RandomStrategy)  # Add the trading strategy
cerebro.run()  # run it all
cerebro.plot()  # and plot it with a single command
