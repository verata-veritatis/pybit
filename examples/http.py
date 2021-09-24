"""
To see which endpoints are available, you can read the API docs at
https://bybit-exchange.github.io/docs/inverse/#t-introduction

Some methods will have required parameters, while others may be optional.
The arguments in pybit methods match those provided in the Bybit API
documentation.

The following functions are available:

exit()

Public Methods:
------------------------
orderbook()
query_kline()
latest_information_for_symbol()
public_trading_records()
query_symbol()
liquidated_orders()
query_mark_price_kline()
query_index_price_kline()
query_premium_index_kline()
open_interest()
latest_big_deal()
long_short_ratio()
get_the_last_funding_rate()

Private Methods:
(requires authentication)
------------------------
place_active_order()
get_active_order()
cancel_active_order()
cancel_all_active_orders()
replace_active_order()
query_active_order()

place_conditional_order()
get_conditional_order()
cancel_conditional_order()
cancel_all_conditional_orders()
replace_conditional_order()
query_conditional_order()

user_leverage()
change_user_leverage()
cross_isolated_margin_switch()
position_mode_switch()
full_partial_position_tp_sl_switch()

my_position()
change_margin()
set_trading_stop()

get_risk_limit()
set_risk_limit()

my_last_funding_fee()
predicted_funding_rate()

api_key_info()

get_wallet_balance()
wallet_fund_records()
withdraw_records()
user_trade_records()

server_time()
announcement()

Spot Methods:
(many of the above methods can also be used with the spot market, provided the argument spot=True is passed)
------------------------
fast_cancel_active_order()
batch_cancel_active_order()
batch_fast_cancel_active_order()
batch_cancel_active_order_by_ids()

Asset Transfer Methods:
------------------------
create_internal_transfer()
create_subaccount_transfer()
query_transfer_list()
query_subaccount_transfer_list()
query_subaccount_list()

Custom Methods:
(requires authentication)
------------------------
place_active_order_bulk()
cancel_active_order_bulk()
place_conditional_order_bulk()
cancel_conditional_order_bulk()
close_position()

"""

# Import pybit and define the HTTP object.
from pybit import HTTP

"""
You can create an authenticated or unauthenticated HTTP session. 
You can skip authentication by not passing any value for api_key
and api_secret.
"""

# Unauthenticated
session_unauth = HTTP(endpoint='https://api.bybit.com')

# Authenticated
session_auth = HTTP(
    endpoint='https://api.bybit.com',
    api_key='...',
    api_secret='...'
)

# Lets get market information about EOSUSD. Note that 'symbol' is
# a required parameter as per the Bybit API documentation.
session_unauth.latest_information_for_symbol(symbol='EOSUSD')

# We can fetch our wallet balance using an auth'd session.
session_auth.get_wallet_balance(coin='BTC')

"""
Spot API.
"""

# Unauthenticated, prefer spot endpoint
session_spot_unauth = HTTP(endpoint='https://api.bybit.com', spot=True)

# Prefer spot endpoint for this request, without specifying at obj creation
session_auth.get_wallet_balance(coin='BTC', spot=True)
