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

Public Topics:
orderBookL2_25
orderBookL2-200
trade
insurance
instrument_info
klineV2

Private Topics:
position
execution
order
stop_order
wallet
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

# Define your endpoint URL and subscriptions.
endpoint = 'wss://stream.bybit.com/realtime'
subs = [
    'orderBookL2_25.BTCUSD',
    'instrument_info.100ms.BTCUSD',
    'instrument_info.100ms.ETHUSD'
]

# Connect without authentication!
ws_unauth = WebSocket(endpoint, subscriptions=subs)

# Connect with authentication!
ws_auth = WebSocket(
    endpoint,
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
