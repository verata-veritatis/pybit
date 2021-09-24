"""
To see which endpoints and topics are available, check the Bybit API 
documentation: https://bybit-exchange.github.io/docs/inverse/#t-websocket

Inverse Perpetual endpoints:
wss://stream-testnet.bybit.com/realtime
wss://stream.bybit.com/realtime

USDT Perpetual endpoints:
wss://stream-testnet.bybit.com/realtime_public
wss://stream-testnet.bybit.com/realtime_private
wss://stream.bybit.com/realtime_public
wss://stream.bybit.com/realtime_private

Spot endpoints:
wss://stream-testnet.bybit.com/spot/quote/ws/v1
wss://stream-testnet.bybit.com/spot/quote/ws/v2
wss://stream-testnet.bybit.com/spot/ws
wss://stream.bybit.com/spot/quote/ws/v1
wss://stream.bybit.com/spot/quote/ws/v2
wss://stream.bybit.com/spot/ws

Futures Public Topics:
orderBookL2_25
orderBookL2-200
trade
insurance
instrument_info
klineV2

Futures Private Topics:
position
execution
order
stop_order
wallet

Spot Topics:
Subscribing to spot topics uses the JSON format to pass the topic name and
filters, as opposed to futures WS where the topic and filters are pass in a
single string. So, it's recommended to pass a JSON or python dict in your
subscriptions, which also be used to fetch the topic's updates. Examples can
be found in the code panel here: https://bybit-exchange.github.io/docs/spot/#t-publictopics

However, as private spot topics do not require a subscription, the following
strings can be used to fetch data:
outboundAccountInfo
executionReport
ticketInfo
"""

# Import the WebSocket object from pybit.
from pybit import WebSocket

"""
We can also import the HTTP object at the same time using:

from pybit import HTTP, WebSocket

Additionally, we can simply import all of pybit and use each
object selectively.

import pybit
client = pybit.HTTP(...)
ws = pybit.WebSocket(...)
"""

# Define your endpoint URLs and subscriptions.
endpoint_public = 'wss://stream.bybit.com/realtime_public'
endpoint_private = 'wss://stream.bybit.com/realtime_private'
subs = [
    'orderBookL2_25.BTCUSD',
    'instrument_info.100ms.BTCUSD',
    'instrument_info.100ms.ETHUSD'
]

# Connect without authentication!
ws_unauth = WebSocket(endpoint_public, subscriptions=subs)

# Connect with authentication!
ws_auth = WebSocket(
    endpoint_private,
    subscriptions=['position'],
    api_key='...',
    api_secret='...'
)

# Let's fetch the orderbook for BTCUSD.
print(
    ws_unauth.fetch('orderBookL2_25.BTCUSD')
)

# We can also create a dict containing multiple results.
print(
    {i: ws_unauth.fetch(i) for i in subs}
)

# Check on your position. Note that no position data is received until a
# change in your position occurs (initially, there will be no data).
print(
    ws_auth.fetch('position')
)


"""
Spot websocket sample usage.
As using the spot websocket works slightly differently, separate sample usage is
listed here.
"""

# Define endpoints and subscriptions
endpoint_spot_v1 = "wss://stream.bybit.com/spot/quote/ws/v1"
endpoint_spot_private = "wss://stream.bybit.com/spot/ws"
trade_v1 = """
{
    "topic": "trade",
    "event": "sub",
    "symbol": "BTCUSDT",
    "params": {
        "binary": false
    }
}"""
realtimes_v1 = """
{
    "topic": "realtimes",
    "event": "sub",
    "symbol": "BTCUSDT",
    "params": {
        "binary": false
    }
}"""
subs = [trade_v1, realtimes_v1]

# Connect to the unauth spot websocket
ws_spot_unauth = WebSocket(endpoint=endpoint_spot_v1, subscriptions=subs)

# Fetch this subscription
print(ws_spot_unauth.fetch(trade_v1))

# Connect to the auth spot websocket (subscriptions are not required)
ws_spot_auth = WebSocket(endpoint=endpoint_spot_private)

print(ws_spot_auth.fetch('outboundAccountInfo'))
