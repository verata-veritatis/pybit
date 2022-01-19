from .websocket_stream import FuturesWebSocketManager
from .websocket_stream import USDT_PERPETUAL
from .websocket_stream import _identify_ws_method


ws_name = USDT_PERPETUAL
PUBLIC_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime_public"
PRIVATE_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime_private"


class WebSocket:
    def __init__(self, test, domain="",
                 api_key=False, api_secret=False):
        self.ws_public = None
        self.ws_private = None

        self.test = test
        self.domain = domain
        self.api_key = api_key
        self.api_secret = api_secret

    def _ws_public_subscribe(self, topic, callback, symbol):
        if not self.ws_public:
            self.ws_public = FuturesWebSocketManager(
                PUBLIC_WSS, ws_name, self.test, domain=self.domain
            )
        self.ws_public.subscribe(topic, callback, symbol)

    def _ws_private_subscribe(self, topic, callback):
        if not self.ws_private:
            self.ws_private = FuturesWebSocketManager(
                PRIVATE_WSS, ws_name, self.test, domain=self.domain,
                api_key=self.api_key, api_secret=self.api_secret
            )
        self.ws_private.subscribe(topic, callback)

    def custom_topic_stream(self, topic, callback, wss_url):
        subscribe = _identify_ws_method(
            wss_url,
            {
                PUBLIC_WSS: self._ws_public_subscribe,
                PRIVATE_WSS: self._ws_private_subscribe
            })
        subscribe(topic, callback)

    def orderbook_25_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketorderbook25
        """
        topic = "orderBookL2_25.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def orderbook_200_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketorderbook200
        """
        topic = "orderBook_200.100ms.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def trade_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websockettrade
        """
        topic = "trade.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def instrument_info_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketinstrumentinfo
        """
        topic = "instrument_info.100ms.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def kline_stream(self, callback, symbol, interval):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketkline
        """
        topic = "candle.{}.{}"
        topic = topic.format(str(interval), "{}")
        self._ws_public_subscribe(topic, callback, symbol)

    def liquidation_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketliquidation
        """
        topic = "liquidation.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    # Private topics
    def position_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketposition
        """
        topic = "position"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def execution_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketexecution
        """
        topic = "execution"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketorder
        """
        topic = "order"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def stop_order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketstoporder
        """
        topic = "stop_order"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def wallet_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketwallet
        """
        topic = "wallet"
        self._ws_private_subscribe(topic=topic, callback=callback)
