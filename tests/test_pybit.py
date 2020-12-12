import unittest, time
from pybit import HTTP, WebSocket

session = HTTP('https://api.bybit.com')
ws = WebSocket('wss://stream.bybit.com/realtime',
                    subscriptions=['instrument_info.100ms.BTCUSD'])

class HTTPTest(unittest.TestCase):

    def test_orderbook(self):
        self.assertEqual(
            session.orderbook(symbol='BTCUSD')['ret_msg'],
            'OK'
        )

    def test_query_kline(self):
        self.assertEqual(
            (session.query_kline(symbol='BTCUSD', interval='1', 
                from_time=int(time.time())-60*60)['ret_msg']),
            'OK'
        )
    
    def test_latest_information_for_symbol(self):
        self.assertEqual(
            session.latest_information_for_symbol()['ret_msg'],
            'OK'
        )

    def test_public_trading_records(self):
        self.assertEqual(
            session.public_trading_records(symbol='BTCUSD')['ret_msg'],
            'OK'
        )

    def test_query_symbol(self):
        self.assertEqual(
            session.query_symbol()['ret_msg'],
            'OK'
        )

    def test_server_time(self):
        self.assertEqual(
            session.server_time()['ret_msg'],
            'OK'
        )

    def test_announcement(self):
        self.assertEqual(
            session.announcement()['ret_msg'],
            'OK'
        )

    # We can't really test authenticated endpoints without keys, but we
    # can make sure it raises a PermissionError.
    def test_place_active_order(self):
        with self.assertRaises(PermissionError):
            session.place_active_order(symbol='BTCUSD', 
                order_type='Market', side='Buy', qty=1)

class WebSocketTest(unittest.TestCase):
    
    # A very simple test to ensure we're getting something from WS.
    def test_websocket(self):
        self.assertNotEqual(
            ws.fetch(['instrument_info.100ms.BTCUSD']),
            []
        )