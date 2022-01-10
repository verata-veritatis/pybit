from .websocket_stream import SpotWebSocketManager
from .websocket_stream import _identify_ws_method


ws_name = "Spot"
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

    def trade_v1_stream(self, callback):
        topic = \
            {
                "topic": "trade",
                "event": "sub",
                "symbol": "BTCUSDT",
                "params": {
                    "binary": False
                }
            }
        self._ws_public_v1_subscribe(topic, callback)

    def outbound_account_info_stream(self, callback):
        topic = "outboundAccountInfo"
        self._ws_private_subscribe(topic=topic, callback=callback)
