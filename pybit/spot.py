from .websocket_stream import SpotWebSocketManager
from .websocket_stream import SPOT
from .websocket_stream import _identify_ws_method


ws_name = SPOT
PUBLIC_V1_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/spot/quote/ws/v1"
PUBLIC_V2_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/spot/quote/ws/v2"
PRIVATE_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/spot/ws"


class WebSocket:
    def __init__(self, test, domain="",
                 api_key=False, api_secret=False):
        self.ws_public_v1 = None
        self.ws_public_v2 = None
        self.ws_private = None

        self.test = test
        self.domain = domain
        self.api_key = api_key
        self.api_secret = api_secret

    def _ws_public_v1_subscribe(self, topic, callback):
        if not self.ws_public_v1:
            self.ws_public_v1 = SpotWebSocketManager(
                PUBLIC_V1_WSS, ws_name, self.test, domain=self.domain
            )
        self.ws_public_v1.subscribe(topic, callback)

    def _ws_public_v2_subscribe(self, topic, callback):
        if not self.ws_public_v2:
            self.ws_public_v2 = SpotWebSocketManager(
                PUBLIC_V2_WSS, ws_name, self.test, domain=self.domain
            )
        self.ws_public_v2.subscribe(topic, callback)

    def _ws_private_subscribe(self, topic, callback):
        if not self.ws_private:
            self.ws_private = SpotWebSocketManager(
                PRIVATE_WSS, ws_name, self.test, domain=self.domain,
                api_key=self.api_key, api_secret=self.api_secret
            )
        self.ws_private.subscribe(topic, callback)

    def custom_topic_stream(self, topic, callback, wss_url):
        subscribe = _identify_ws_method(
            wss_url,
            {
                PUBLIC_V1_WSS: self._ws_public_v1_subscribe,
                PUBLIC_V2_WSS: self._ws_public_v2_subscribe,
                PRIVATE_WSS: self._ws_private_subscribe
            })
        subscribe(topic, callback)

    def trade_v1_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websockettrade
        """
        topic = \
            {
                "topic": "trade",
                "event": "sub",
                "symbol": symbol,
                "params": {
                    "binary": False
                }
            }
        self._ws_public_v1_subscribe(topic, callback)

    def realtimes_v1_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketrealtimes
        """
        topic = \
            {
                "topic": "realtimes",
                "event": "sub",
                "symbol": symbol,
                "params": {
                    "binary": False
                }
            }
        self._ws_public_v1_subscribe(topic, callback)

    def kline_v1_stream(self, callback, symbol, interval):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketkline
        """
        topic = \
            {
                "topic": "kline_{}".format(str(interval)),
                "event": "sub",
                "symbol": symbol,
                "params": {
                    "binary": False
                }
            }
        self._ws_public_v1_subscribe(topic, callback)

    def depth_v1_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketdepth
        """
        topic = \
            {
                "topic": "depth",
                "event": "sub",
                "symbol": symbol,
                "params": {
                    "binary": False
                }
            }
        self._ws_public_v1_subscribe(topic, callback)

    def merged_depth_v1_stream(self, callback, symbol, dump_scale):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketmergeddepth
        """
        topic = \
            {
                "topic": "mergedDepth",
                "event": "sub",
                "symbol": symbol,
                "params": {
                    "dumpScale": int(dump_scale),
                    "binary": False
                }
            }
        self._ws_public_v1_subscribe(topic, callback)

    def diff_depth_v1_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketdiffdepth
        """
        topic = \
            {
                "topic": "diffDepth",
                "event": "sub",
                "symbol": symbol,
                "params": {
                    "binary": False
                }
            }
        self._ws_public_v1_subscribe(topic, callback)

    def depth_v2_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketv2depth
        """
        topic = \
            {
                "topic": "trade",
                "event": "sub",
                "params": {
                    "symbol": symbol,
                    "binary": False
                }
            }
        self._ws_public_v2_subscribe(topic, callback)

    def kline_v2_stream(self, callback, symbol, interval):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketv2kline
        """
        topic = \
            {
                "topic": "kline",
                "event": "sub",
                "params": {
                    "symbol": symbol,
                    "klineType": interval,
                    "binary": False
                }
            }
        self._ws_public_v2_subscribe(topic, callback)

    def trade_v2_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketv2trade
        """
        topic = \
            {
                "topic": "trade",
                "event": "sub",
                "params": {
                    "symbol": symbol,
                    "binary": False
                }
            }
        self._ws_public_v2_subscribe(topic, callback)

    def book_ticker_v2_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketv2bookticker
        """
        topic = \
            {
                "topic": "bookTicker",
                "event": "sub",
                "params": {
                    "symbol": symbol,
                    "binary": False
                }
            }
        self._ws_public_v2_subscribe(topic, callback)

    def realtimes_v2_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/spot/#t-websocketv2realtimes
        """
        topic = \
            {
                "topic": "realtimes",
                "event": "sub",
                "params": {
                    "symbol": symbol,
                    "binary": False
                }
            }
        self._ws_public_v2_subscribe(topic, callback)

    def outbound_account_info_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/spot/#t-outboundaccountinfo
        """
        topic = "outboundAccountInfo"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def execution_report_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/spot/#t-executionreport
        """
        topic = "executionReport"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def ticket_info_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/spot/#t-ticketinfo
        """
        topic = "ticketInfo"
        self._ws_private_subscribe(topic=topic, callback=callback)
