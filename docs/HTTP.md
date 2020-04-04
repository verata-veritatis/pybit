# HTTP Module
Available methods for the HTTP module of `pybit`.

## Public Endpoints

```python
def get_orderbook(self, symbol):
    '''Get orderbook data.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.

    '''

def get_klines(self, symbol, interval, from_time, limit=None):
    '''Get kline data.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    interval : str
        Required parameter. The desired candle interval. Available
        options are: 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, 
        D, M, W, Y.
    from_time : int
        Required parameter. The time from which to begin your lookup of
        candles, in epoch time (seconds).
    limit : int
        The number of candles to fetch. Defaults to 500; maximum is
        1000.

    '''

def get_tickers(self, symbol=None):
    '''Get ticker data.
    
    Parameters
    ------------------------
    symbol : str
        The symbol of the market as a string, e.g. 'BTCUSD'.

    '''

def get_trading_records(self, symbol, from_time=None, limit=None):
    '''Get trading records.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    from_time : int
        The time from which to begin your lookup, in epoch time 
        (seconds).
    limit : int
        The number of rows to fetch. Defaults to 500; maximum is 1000.

    '''

def get_symbols(self):
    '''Get trading records.
    
    There are no parameters for this method.

    '''

def server_time(self):
    '''Fetches the exchange server time.
    
    There are no parameters for this method.

    '''

def announcement(self):
    '''Fetches the exchange's recent announcements.
    
    There are no parameters for this method.

    '''
```

## Private Endpoints

```python
def place_active_order(self, symbol, order_type, side, qty, price=None, 
    time_in_force='GoodTillCancel', take_profit=None, stop_loss=None, 
    reduce_only=False, close_on_trigger=False, order_link_id=None):
    '''Places a standard order.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    order_type : str
        Required parameter. The type of order to place. The options 
        are 'Market' or 'Limit'.
    side : str
        Required parameter. Which side of the orderbook to place an
        order. The options are 'Buy' or 'Sell'.
    qty : int
        Required parameter. Number of contracts for the order. Must
        be an integer and cannot be fractional.
    price : float
        Required parameter ONLY if the order_type is 'Limit'. The price 
        at which to set the order.  Must be rounded to the nearest 
        half (0.5).
    time_in_force : str
        The execution method of the order. 'GoodTillCancel' will keep
        your order alive until you cancel it. 'ImmediateOrCancel' will
        cancel the order if it is not at least partially filled
        immediately. 'FillOrKill' forces the order to be completely
        filled immediately, otherwise it is canceled. 'PostOnly' will
        cancel the order if it would have been executed immediately
        at market, preventing accidental fills.
    take_profit : float
        The price at which to set an optional take profit order once
        your order is filled. Must be rounded to the nearest half 
        (0.5).
    stop_loss : float
        The price at which to set an optional stop loss order once
        your order is filled. Must be rounded to the nearest half 
        (0.5).
    reduce_only : bool
        The order wqill only execute if it reduces your open position.
        otherwise it will be canceled.
    close_on_trigger : bool
        Useful for orders that are meant to close your position. When
        this order is filled, it will close your position and cancel
        all orders for the given market.
    order_link_id : str
        Used to set a custom order ID that can be later used to 
        retrieve information about this particular order.

    '''

def get_active_order(self, order_id=None, order_link_id=None, symbol=None,
    order=None, page=None, limit=None, order_status=None):
    '''Get information about an open order.
    
    Parameters
    ------------------------
    order_id : str
        This is the ID set by the exchange.
    order_link_id : str
        This is the ID set by the user.
    symbol : str
        The symbol of the market as a string, e.g. 'BTCUSD'. Used to
        filter your results.
    order : int
        Used to sort orders by the creation date, in epoch time 
        (seconds).
    page : int
        The number of pages of data to retrieve.
    limit : int
        The total number of orders to retrieve.
    order_status : str
        Filter results by the status of the order.

    '''

def cancel_active_order(self, symbol, order_id=None, order_link_id=None):
    '''Cancels an open order.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    order_id : str
        Required parameter ONLY if order_link_id is not provided.
        This is the ID set by the exchange.
    order_link_id : str
        Required parameter ONLY if order_id is not provided.
        This is the ID set by the user.

    '''

def cancel_all_active_orders(self, symbol):
    '''Cancels all open orders for a given symbol.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.

    '''

def replace_active_order(self, order_id, symbol, p_r_qty=None, 
    p_r_price=None):
    '''Replaces or amends an open order.
    
    Parameters
    ------------------------
    order_id : str
        Required parameter. This is the ID set by the exchange.
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    p_r_qty : int
        Used to change the quantity of your current order.
    p_r_price : float
        Used to change the price at which the current order is set.
        Must be rounded to the nearest half (0.5).

    '''

def query_active_order(self, symbol, order_id=None, order_link_id=None):
    '''Search for a particular order.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    order_id : str
        Required parameter ONLY if order_link_id is not provided.
        This is the ID set by the exchange.
    order_link_id : str
        Required parameter ONLY if order_id is not provided.
        This is the ID set by the user.

    '''

def place_conditional_order(self, symbol, order_type, side, qty, 
    base_price, stop_px, price=None, time_in_force='GoodTillCancel', 
    trigger_by=None, close_on_trigger=False, order_link_id=None):
    '''Places a conditional order.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    order_type : str
        Required parameter. The type of order to place. The options 
        are 'Market' or 'Limit'.
    side : str
        Required parameter. Which side of the orderbook to place an
        order. The options are 'Buy' or 'Sell'.
    qty : int
        Required parameter. Number of contracts for the order. Must
        be an integer and cannot be fractional.
    base_price : float
        Required parameter. Used to compare with the value of 'stop_px', 
        to decide whether your conditional order will be triggered by 
        the crossing trigger price from upper side or lower side, 
        determining the expected direction of the current conditional 
        order. Must be rounded to the nearest half (0.5).
    stop_px : float
        Required parameter. The trigger price. Must be rounded to the 
        nearest half (0.5).
    price : float
        Required parameter ONLY if the order_type is 'Limit'. The price 
        at which to set the order.  Must be rounded to the nearest 
        half (0.5).
    time_in_force : str
        The execution method of the order. 'GoodTillCancel' will keep
        your order alive until you cancel it. 'ImmediateOrCancel' will
        cancel the order if it is not at least partially filled
        immediately. 'FillOrKill' forces the order to be completely
        filled immediately, otherwise it is canceled. 'PostOnly' will
        cancel the order if it would have been executed immediately
        at market, preventing accidental fills.
    trigger_by : str
        The price used for the trigger. Options are 'LastPrice', 
        'MarkPrice', and 'IndexPrice'. Defaults to 'LastPrice'.
    close_on_trigger : bool
        Useful for orders that are meant to close your position. When
        this order is filled, it will close your position and cancel
        all orders for the given market.
    order_link_id : str
        Used to set a custom order ID that can be later used to 
        retrieve information about this particular order.

    '''

def get_conditional_order(self, stop_order_id=None, order_link_id=None,
    symbol=None, stop_order_status=None, order=None, page=None,
    limit=None):
    '''Get information about an open conditional order.
    
    Parameters
    ------------------------
    stop_order_id : str
        This is the ID set by the exchange.
    order_link_id : str
        This is the ID set by the user.
    symbol : str
        The symbol of the market as a string, e.g. 'BTCUSD'. Used to
        filter your results.
    stop_order_status : str
        Filter results by the status of the conditional order.
    order : int
        Used to sort orders by the creation date, in epoch time 
        (seconds).
    page : int
        The number of pages of data to retrieve.
    limit : int
        The total number of orders to retrieve.
    '''

def cancel_conditional_order(self, symbol, stop_order_id=None,
    order_link_id=None):
    '''Cancels an open conditional order.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    stop_order_id : str
        Required parameter ONLY if order_link_id is not provided.
        This is the ID set by the exchange.
    order_link_id : str
        Required parameter ONLY if order_id is not provided.
        This is the ID set by the user.

    '''

def cancel_all_conditional_orders(self, symbol):
    '''Cancels all open conditional orders for a given symbol.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.

    '''

def replace_conditional_order(self, stop_order_id, order_id, symbol, 
    p_r_qty=None, p_r_price=None, p_r_trigger_price=None):
    '''Replaces or amends an open order.
    
    Parameters
    ------------------------
    stop_order_id : str
        Required parameter. This is the ID set by the exchange.
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    p_r_qty : int
        Used to change the quantity of your current order.
    p_r_price : float
        Used to change the price at which the current order is set.
        Must be rounded to the nearest half (0.5).
    p_r_trigger_price : float
        Used to change the price at which the stop order is triggered.
        Must be rounded to the nearest half (0.5).

    '''

def query_conditional_order(self, symbol, stop_order_id=None, 
    order_link_id=None):
    '''Search for a specific conditional order.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    stop_order_id : str
        Required parameter ONLY if order_link_id is not provided.
        This is the ID set by the exchange.
    order_link_id : str
        Required parameter ONLY if order_id is not provided.
        This is the ID set by the user.

    '''

def user_leverage(self):
    '''Fetches the user's leverage.
    
    There are no parameters for this method.

    '''

def change_user_leverage(self, symbol, leverage):
    '''Sets the user's leverage.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    leverage : float
        Required parameter. The desired leverage. Set to 0 for cross
        leverage.

    '''

def my_position(self, symbol):
    '''Fetches the user's position.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.

    '''

def change_margin(self, symbol, margin):
    '''Changes the margin of the current position.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    margin : str
        Required parameter. Desired margin. 

    '''

def set_trading_stop(self, symbol, take_profit=None, stop_loss=None,
    trailing_stop=None, new_trailing_active=None):
    '''Sets conditions for the open position..
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    take_profit : float
        The price at which to set an optional take profit for the 
        current position. Must be rounded to the nearest half (0.5).
        Setting a 0 will cancel the position's take profit.
    stop_loss : float
        The price at which to set an optional stop loss for the 
        current position. Must be rounded to the nearest half (0.5).
        Setting a 0 will cancel the position's stop loss.
    trailing_stop : float
        The price at which to set an optional trailing stop for the
        current position. Must be rounded to the nearest half (0.5).
        Setting a 0 will cancel the position's trailing stop.
    new_trailing_active : float
        The trigger price of the trailing stop, if set. Must be rounded 
        to the nearest half (0.5).

    '''

def get_risk_limit(self):
    '''Fetches the user's risk limit.
    
    There are no parameters for this method.

    '''

def set_risk_limit(self, symbol, risk_id):
    '''Sets the user's risk limit.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    risk_id : str
        Required parameter. The risk identifier. Can be found with
        get_risk_limit().

    '''

def get_last_funding_rate(self, symbol):
    '''Fetches the last funding rate for the particular symbol.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.

    '''

def my_last_funding_fee(self, symbol):
    '''Fetches the user's last funding fee for the particular symbol.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.

    '''

def predicted_funding_rate(self, symbol):
    '''Fetches the next predicted funding rate for the particular 
    symbol.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.

    '''

def api_key_info(self):
    '''Fetches information about the user's current API key.
    
    There are no parameters for this method.

    '''

def get_wallet_balance(self, coin):
    '''Fetches the user's wallet balance.
    
    Parameters
    ------------------------
    coin : str
        Required parameter. The cryptocurrency ticker as a string, 
        e.g. 'BTC'.

    '''

def wallet_fund_records(self, start_date=None, end_date=None,
    currency=None, coin=None, wallet_fund_type=None, page=None,
    limit=None):
    '''Fetches the user's wallet records.
    
    Parameters
    ------------------------
    start_date : int
        The start date of your record search, in epoch time (seconds).
    end_date : int
        The end date of your record search, in epoch time (seconds).
    currency : str
        A specific coin/currency to search for.
    coin : str
        An alias for currrency.
    wallet_fund_type : str
        The type of events to search for. Options are 'Deposit', 
        'Withdraw', 'RealisedPNL', 'Commission', 'Refund', 'Prize',
        'ExchangeOrderWithdraw', and 'ExchangeOrderDeposit'.
    page : int
        The number of pages of data to retrieve.
    limit : int
        The total number of orders to retrieve.

    '''

def withdraw_records(self, start_date=None, end_date=None, coin=None,
    status=None, page=None, limit=None):
    '''Fetches the user's withdrawal records.
    
    Parameters
    ------------------------
    start_date : int
        The start date of your record search, in epoch time (seconds).
    end_date : int
        The end date of your record search, in epoch time (seconds).
    coin : str
        A specific coin/currency to search for.
    status : str
        Filter results by the status of the withdrawal.
    page : int
        The number of pages of data to retrieve.
    limit : int
        The total number of orders to retrieve.

    '''

def user_trade_records(self, symbol, order_id=None, start_time=None, 
    page=None, limit=None):
    '''Fetches the user's trade records.
    
    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.
    order_id : str
        This is the ID set by the exchange.
    start_time : int
        The start time of your record search, in epoch time (seconds).
    page : int
        The number of pages of data to retrieve.
    limit : int
        The total number of orders to retrieve.

    '''
```

## Custom Methods

```python
def close_position(self, symbol):
    '''Closes your open position.

    Parameters
    ------------------------
    symbol : str
        Required parameter. The symbol of the market as a string, 
        e.g. 'BTCUSD'.

    '''
```