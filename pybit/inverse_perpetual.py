from .websocket_stream import FuturesWebSocketManager
from .websocket_stream import INVERSE_PERPETUAL


ws_name = INVERSE_PERPETUAL
WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime"


class WebSocket(FuturesWebSocketManager):
    def __init__(self, test, domain="",
                 api_key=None, api_secret=None):
        super().__init__(WSS, ws_name, test=test, domain=domain,
                         api_key=api_key, api_secret=api_secret)

    def instrument_info_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketinstrumentinfo
        """
        topic = "instrument_info.100ms.{}"
        self.subscribe(topic, callback, symbol)

    def position_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketposition
        """
        topic = "position"
        self.subscribe(topic, callback)
