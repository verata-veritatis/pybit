from pybit import inverse_perpetual, usdt_perpetual
from time import sleep

import logging
logging.basicConfig(filename="websocket_restructure_wss_example.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")


api_key = ""
api_secret = ""


def instrument_info_callback(message):
    print(f"instrument_info_callback()")
    print(message)
    pass


def position_callback(message):
    print(f"position_callback()")
    print(message)


#inverse_ws = inverse_perpetual.WebSocket("wss://stream.bybit.com/realtime", api_key=api_key, api_secret=api_secret)
#
#inverse_instrument_info_sub = inverse_ws.custom_topic_stream("instrument_info.100ms.BTCUSD", instrument_info_callback)
#inverse_position_sub = inverse_ws.position_stream(position_callback)


usdt_public_ws = usdt_perpetual.PublicWebSocket("wss://stream.bybit.com/realtime_public")
usdt_private_ws = usdt_perpetual.PrivateWebSocket("wss://stream.bybit.com/realtime_private", api_key=api_key, api_secret=api_secret)

usdt_instrument_info_sub = usdt_public_ws.custom_topic_stream("instrument_info.100ms.BTCUSDT", instrument_info_callback)
usdt_position_sub = usdt_private_ws.position_stream(position_callback)

while True:
    # Proceed with trading strategy whilst still receiving callbacks for new
    #  websocket messages
    print(1)
    sleep(1)


