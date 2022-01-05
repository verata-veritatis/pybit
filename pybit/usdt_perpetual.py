from .websocket_stream import FuturesWebSocketManager
from .websocket_stream import _identify_ws_method


ws_name = "USDT Perp"
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

    def _ws_public_subscribe(self, topic, callback):
        if not self.ws_public:
            self.ws_public = FuturesWebSocketManager(
                PUBLIC_WSS, ws_name, self.test, domain=self.domain
            )
        self.ws_public.subscribe(topic, callback)

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

    def instrument_info_stream(self, callback):
        topic = "instrument_info.100ms.BTCUSDT"
        self._ws_public_subscribe(topic, callback)

    def position_stream(self, callback):
        topic = "position"
        self._ws_private_subscribe(topic=topic, callback=callback)
