from .websocket_stream import FuturesWebSocketManager


ws_name = "Linear Perp"


class PublicWebSocket(FuturesWebSocketManager):
    def __init__(self, endpoint):
        super().__init__(endpoint, ws_name)

    def instrument_info_stream(self, callback):
        topic = "instrument_info.100ms.BTCUSDT"
        self._subscribe(topic=topic, callback=callback)


class PrivateWebSocket(FuturesWebSocketManager):
    def __init__(self, endpoint, api_key, api_secret):
        super().__init__(endpoint, ws_name,
                         api_key=api_key, api_secret=api_secret)

    def position_stream(self, callback):
        topic = "position"
        self._subscribe(topic=topic, callback=callback)
