import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
import ssl
import threading


class WebSocket:

    def __init__(self):

        self.data = {}

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            "wss://stream.bytick.com/realtime",
            on_open=self._on_open(self.ws),
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close(self.ws),
        )
        # Setup the thread running WebSocketApp.
        self.wst = threading.Thread(target=lambda: self.ws.run_forever(
            sslopt={"cert_reqs": ssl.CERT_NONE},
        ))

        # Configure as daemon; start.
        self.wst.daemon = True
        self.wst.start()

    def orderbook(self):
        return self.data.get('orderBook_200.100ms.BTCUSD')

    @staticmethod
    def _on_message(self, message):
        m = json.loads(message)
        if 'topic' in m and m.get('topic') == 'orderBook_200.100ms.BTCUSD' and m.get('type') == 'snapshot':
            print('Hi!')
            self.data[m.get('topic')] = m.get('data')

    @staticmethod
    def _on_error(self, error):
        print(error)

    @staticmethod
    def _on_close(ws):
        print("### closed ###")

    @staticmethod
    def _on_open(ws):
        print('Submitting subscriptions...')
        ws.send(json.dumps({
            'op': 'subscribe',
            'args': ['orderBook_200.100ms.BTCUSD']
        }))


if __name__ == '__main__':
    session = WebSocket()

    time.sleep(5)

    print(session.orderbook())
