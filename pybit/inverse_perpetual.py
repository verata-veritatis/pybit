from .websocket_stream import FuturesWebSocketManager
from .websocket_stream import INVERSE_PERPETUAL


ws_name = INVERSE_PERPETUAL
WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime"


class WebSocket(FuturesWebSocketManager):
    def __init__(self, test, domain="",
                 api_key=None, api_secret=None):
        super().__init__(WSS, ws_name, test=test, domain=domain,
                         api_key=api_key, api_secret=api_secret)

    def orderbook_25_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketorderbook25
        """
        topic = "orderBookL2_25.{}"
        self.subscribe(topic, callback, symbol)

    def orderbook_200_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketorderbook200
        """
        topic = "orderBook_200.100ms.{}"
        self.subscribe(topic, callback, symbol)

    def trade_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websockettrade
        """
        topic = "trade.{}"
        self.subscribe(topic, callback, symbol)

    def insurance_stream(self, callback, symbol):
        """
        symbol should be the base currency. Eg, "BTC" instead of "BTCUSD"
        https://bybit-exchange.github.io/docs/inverse/#t-websocketinsurance
        """
        topic = "insurance.{}"
        self.subscribe(topic, callback, symbol)

    def kline_stream(self, callback, symbol, interval):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketklinev2
        """
        topic = "klineV2.{}.{}"
        topic = topic.format(str(interval), "{}")
        self.subscribe(topic, callback, symbol)

    def instrument_info_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketinstrumentinfo
        """
        topic = "instrument_info.100ms.{}"
        self.subscribe(topic, callback, symbol)

    def liquidation_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketliquidation
        """
        topic = "liquidation.{}"
        self.subscribe(topic, callback, symbol)

    # Private topics
    def position_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketposition
        """
        topic = "position"
        self.subscribe(topic, callback)

    def execution_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketexecution
        """
        topic = "execution"
        self.subscribe(topic, callback)

    def order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketorder
        """
        topic = "order"
        self.subscribe(topic, callback)

    def stop_order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketstoporder
        """
        topic = "stop_order"
        self.subscribe(topic, callback)

    def wallet_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketwallet
        """
        topic = "wallet"
        self.subscribe(topic, callback)

