from Algo import CandlestickStrategy
import datetime
import talib

reconciliation_trades = 'Trade_Recon/{}.xlsx'


class SMACrossover(CandlestickStrategy):
    def __init__(self, short, long):
        super().__init__(name='SMA Crossover ({}, {})'.format(short, long), bars_no=long+1)
        self.short = short
        self.long = long

    async def on_bar(self, datatype, ticker, df):
        if datatype == 'K_3M':
            df['SMA_short'] = talib.SMA(df['close'], timeperiod=self.short)
            df['SMA_long'] = talib.SMA(df['close'], timeperiod=self.long)

            sma_short_last = df['SMA_short'].iloc[-2]
            sma_short_cur = df['SMA_short'].iloc[-1]

            sma_long_last = df['SMA_long'].iloc[-2]
            sma_long_cur = df['SMA_long'].iloc[-1]

            print(f'Datetime: {df["datetime"].iloc[-1]} , Last: {sma_short_last}/{sma_long_last}, Current: {sma_short_cur}/{sma_long_cur}')
            print('\n')
            df.to_excel(f'Trade_Recon/{datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")}_{ticker}.xlsx')

            if (sma_short_last <= sma_long_last) and (sma_short_cur > sma_long_cur) and (self.get_qty(ticker) == 0):
                self.buy_limit(ticker=ticker, quantity=self.get_lot_size(ticker),
                               price=self.get_price(ticker=ticker)+1)

                df.to_excel(f'Trade_Recon_Trade/{datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")}_BUY_{ticker}.xlsx')

            elif (sma_short_last >= sma_long_last) and (sma_short_cur < sma_long_cur) and (self.get_qty(ticker) > 0):
                self.sell_limit(ticker=ticker, quantity=self.get_lot_size(ticker),
                                      price=self.get_price(ticker=ticker)-1)
                df.to_excel(f'Trade_Recon_Trade/{datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")}_SELL_{ticker}.xlsx')
        else:
            pass

    async def on_order_update(self, order_id, df):
        self.logger.info(
            f'{df["order_status"].iloc[-1]} {df["order_type"].iloc[-1]} order to {df["trd_side"].iloc[-1]} {df["dealt_qty"].iloc[-1]}/{df["qty"].iloc[-1]} shares of {df["ticker"].iloc[-1]} @ {df["price"].iloc[-1]}, orderID: {df["order_id"].iloc[-1]}')

    async def on_orderbook(self, ticker, df):
        pass

    async def on_other_data(self, datatype, ticker, df):
        pass

    async def on_quote(self, ticker, df):
        pass

    async def on_tick(self, ticker, df):
        pass


if __name__ == '__main__':
    algo = SMACrossover(short=10, long=20)
    algo.initialize(initial_capital=20000000.0, mq_ip='tcp://127.0.0.1:8001',
                    hook_ip='http://127.0.0.1:8000',
                    hook_name='FUTU', trading_environment='SIMULATE',
                    trading_universe=['HK.00700', 'HK.54544554', 'HK.09988', 'HK.09999', 'HK.02318'], datatypes=['K_3M'])
    algo.run(5000)
