from .websocket_stream import FuturesWebSocketManager


ws_name = "Inverse Perp"


class WebSocket(FuturesWebSocketManager):
    def __init__(self, endpoint, api_key=None, api_secret=None):
        super().__init__(endpoint, ws_name,
                         api_key=api_key, api_secret=api_secret)

    def instrument_info_stream(self, callback):
        topic = "instrument_info.100ms.BTCUSD"
        self._subscribe(topic=topic, callback=callback)

    def position_stream(self, callback):
        topic = "position"
        self._subscribe(topic, callback)
