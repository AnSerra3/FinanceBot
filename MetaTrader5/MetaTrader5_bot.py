import MetaTrader5 as mt5
import pandas as pd
import time

SYMBOL1 = "BTCUSD"
SYMBOL2 = "EURUSD"
SYMBOL3 = "XAUUSD"
TIMEFRAME1 = mt5.TIMEFRAME_M15
TIMEFRAME2 = mt5.TIMEFRAME_M15
TIMEFRAME3 = mt5.TIMEFRAME_M15
VOLUME1 = 0.02
VOLUME2 = 0.02
VOLUME3 = 0.02
DEVIATION = 20
MAGIC = 10
SMA_PERIOD = 20
STANDARD_DEVIATIONS = 2
TP_SD = 2
SL_SD = 3


def market_order(symbol, volume, order_type, deviation, magic, stoploss, takeprofit):
    order_dict = {"buy": 0, "sell": 1}
    price_dict = {"buy": mt5.symbol_info_tick(symbol).ask, "sell": mt5.symbol_info_tick(symbol).bid}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "deviation": deviation,
        "magic": magic,
        "sl": stoploss,
        "tp": takeprofit,
        "comment": "python market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    print(order_result)
    return order_result


def get_signal(symbol, timeframe):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, 1, SMA_PERIOD)
    # converting to DataFrame
    df = pd.DataFrame(bars)
    # single movement average
    sma = df["close"].mean()
    # standard deviation
    sd = df["close"].std()

    lower_band = sma - STANDARD_DEVIATIONS * sd
    upper_band = sma + STANDARD_DEVIATIONS * sd

    # finding signal
    price = mt5.symbol_info_tick(symbol).bid

    if price < lower_band:
        return "buy", sd

    elif price > upper_band:
        return "sell", sd

    else:
        return [None, None]


def strategy(symbol, timeframe, volume):
    if not mt5.positions_get(symbol=symbol):
        signal, standard_deviation = get_signal(symbol, timeframe)
        tick = mt5.symbol_info_tick(symbol)
        if signal == "buy":
            market_order(symbol, volume, "buy", 20, 10, tick.bid - SL_SD * standard_deviation,
                         tick.bid + TP_SD * standard_deviation)

        elif signal == "sell":
            market_order(symbol, volume, "sell", 20, 10, tick.bid + SL_SD * standard_deviation,
                         tick.bid - TP_SD * standard_deviation)
    return


def main():
    initialized = mt5.initialize()
    if initialized:
        print("connected to MetaTrader5")
    mt5.login(7002575, "grhqpo1j", "BlueberryMarkets-Demo")
    while True:
        strategy(SYMBOL1, TIMEFRAME1, VOLUME1)
        strategy(SYMBOL2, TIMEFRAME2, VOLUME2)
        strategy(SYMBOL3, TIMEFRAME3, VOLUME3)
        # check for signal every 1 second
        time.sleep(1)


main()

