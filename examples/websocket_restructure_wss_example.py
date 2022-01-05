from pybit import inverse_perpetual, usdt_perpetual
from time import sleep

import logging
logging.basicConfig(filename="websocket_restructure_wss_example.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")


api_key = ""
api_secret = ""
test = True  # testnet or mainnet


def instrument_info_callback(message):
    print(f"instrument_info_callback()")
    print(message)
    pass


def position_callback(message):
    print(f"position_callback()")
    print(message)
    pass


inverse_ws = inverse_perpetual.WebSocket(test=test, api_key=api_key, api_secret=api_secret)

inverse_instrument_info_sub = inverse_ws.instrument_info_stream(instrument_info_callback)
inverse_position_sub = inverse_ws.position_stream(position_callback)


usdt_ws = usdt_perpetual.WebSocket(test=test, api_key=api_key, api_secret=api_secret)

usdt_instrument_info_sub = usdt_ws.custom_topic_stream("instrument_info.100ms.BTCUSDT", instrument_info_callback, usdt_perpetual.PUBLIC_WSS)
usdt_position_sub = usdt_ws.custom_topic_stream("position", position_callback, usdt_perpetual.PRIVATE_WSS)

while True:
    # Proceed with trading strategy whilst still receiving callbacks for new
    #  websocket messages
    print(1)
    sleep(1)


