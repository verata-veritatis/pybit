from .websocket_stream import FuturesWebSocketManager


ws_name = "Inverse Perp"
WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime"


class WebSocket(FuturesWebSocketManager):
    def __init__(self, test, domain="",
                 api_key=None, api_secret=None):
        super().__init__(WSS, ws_name, test=test, domain=domain,
                         api_key=api_key, api_secret=api_secret)

    def instrument_info_stream(self, callback):
        topic = "instrument_info.100ms.BTCUSD"
        self.subscribe(topic, callback)

    def position_stream(self, callback):
        topic = "position"
        self.subscribe(topic, callback)
