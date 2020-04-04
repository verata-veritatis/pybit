# -*- coding: utf-8 -*-

'''
pybit
------------------------

pybit is a lightweight and high-performance API connector for the 
RESTful and Websocket APIs of the Bybit exchange.

Documentation can be found at 
https://github.com/verata-veritatis/pybit

:copyright: (c) 2020 verata-veritatis
:license: MIT License
'''

import time, hmac, json, logging, threading
import requests, websocket

VERSION = '1.0.1'

class HTTP:

    def __init__(self, api_key=None, api_secret=None, test_net=True,
        timeout=10):
        '''Connector for Bybit's HTTP API.
        
        Parameters
        ------------------------
        api_key : str
            Your API key. Required for authenticated endpoints. Defaults
            to None.
        api_secret : str
            Your API secret key. Required for authenticated endpoints.
            Defaults to None.
        test_net : bool
            True/False. If true, endpoint will be set to testnet.
            Defaults to True, and thus, is required as False if you 
            are trying to access live trading.
        timeout : int
            The timeout of each API request in seconds. Defaults to 10
            seconds.

        '''

        '''
        if test_net:
            self.endpoint = 'api-testnet.bybit.com'
        else:
            self.endpoint = 'api.bybit.com'   
        '''

        # Set endpoint URL.
        if test_net:
            self.endpoint = 'https://api-testnet.bybit.com'
        else:
            self.endpoint = 'https://api.bybit.com'

        # Setup logger.
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Initializing HTTP session.')

        # Set API keys.
        self.api_key = api_key
        self.api_secret = api_secret

        # Set timeout.
        self.timeout = timeout

        # Initialize requests session.
        self.client = requests.Session()
        self.client.headers.update(
            {
                'User-Agent': 'pybit-' + VERSION,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        )

    def exit(self):
        '''Closes the request session.'''
        self.client.close()
        self.logger.debug('HTTP session closed.')

    '''
    Market Data Endpoints
    See https://bybit-exchange.github.io/docs/inverse/#t-marketdata
    for more information.

    /v2/public/orderBook/L2
    /v2/public/kline/list
    /v2/public/tickers
    /v2/public/trading-records
    /v2/public/symbols
    '''

    def get_orderbook(self, symbol):
        '''Get orderbook data.
        
        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string, 
            e.g. 'BTCUSD'.

        '''

        path = self.endpoint + '/v2/public/orderBook/L2'
        query = {
            'symbol': symbol
        }
        return self._submit_request(method='GET', path=path, query=query)

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

        path = self.endpoint + '/v2/public/kline/list'
        query = {
            'symbol': symbol,
            'interval': interval,
            'from': from_time,
            'limit': limit
        }
        return self._submit_request(method='GET', path=path, query=query)

    def get_tickers(self, symbol=None):
        '''Get ticker data.
        
        Parameters
        ------------------------
        symbol : str
            The symbol of the market as a string, e.g. 'BTCUSD'.

        '''

        path = self.endpoint + '/v2/public/tickers'
        query = {
            'symbol': symbol
        }
        return self._submit_request(method='GET', path=path, query=query)

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

        path = self.endpoint + '/v2/public/trading-records'
        query = {
            'symbol': symbol,
            'from': from_time,
            'limit': limit
        }
        return self._submit_request(method='GET', path=path, query=query)

    def get_symbols(self):
        '''Get trading records.
        
        There are no parameters for this method.

        '''

        path = self.endpoint + '/v2/public/symbols'
        return self._submit_request(method='GET', path=path)

    '''
    Account Data Endpoints
    See https://bybit-exchange.github.io/docs/inverse/#t-accountdata
    for more information.

    Active Orders:
    /v2/private/order/create
    /open-api/order/list
    /v2/private/order/cancel
    /v2/private/order/cancelAll
    /open-api/order/replace
    /v2/private/order

    Conditional Orders:
    /open-api/stop-order/create
    /open-api/stop-order/list
    /open-api/stop-order/cancel
    /v2/private/stop-order/cancelAll
    /open-api/stop-order/replace
    /v2/private/stop-order

    Leverage:
    /user/leverage
    /user/leverage/save

    Position:
    /v2/private/position/list
    /position/change-position-margin
    /open-api/position/trading-stop

    Risk Limit:
    /open-api/wallet/risk-limit/list
    /open-api/wallet/risk-limit

    Funding:
    /open-api/funding/prev-funding-rate
    /open-api/funding/prev-funding
    /open-api/funding/predicted-funding

    API Key Info:
    /open-api/api-key
    '''

    '''
    Active Orders
    '''

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

        if symbol.endswith('USDT'):
            path = self.endpoint + '/private/linear/order/create'
        else:
            path = self.endpoint + '/v2/private/order/create'
        query = {
            'side': side,
            'symbol': symbol,
            'order_type': order_type,
            'qty': qty,
            'price': price,
            'time_in_force': time_in_force,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'reduce_only': reduce_only,
            'close_on_trigger': close_on_trigger,
            'order_link_id': order_link_id
        }
        return self._submit_request(method='POST', path=path, query=query, 
            auth=True)

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

        Notes
        ------------------------
        Since the symbol parameter is not required, we need to handle a
        situation where we're trying to determine whether to use the
        inverse or linear URLs, yet no symbol is given. In this
        case, Python will raise an AttributeError when attempting to
        use 'endswith()' on a NoneType. We can handle catch this exception 
        and default to the inverse perp URL.

        '''

        try:
            if symbol.endswith('USDT'):
                path = self.endpoint + '/private/linear/order/list'
            else:
                path = self.endpoint + '/open-api/order/list'
        except AttributeError:
            path = self.endpoint + '/open-api/order/list'
        query = {
            'order_id': order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'order': order,
            'page': page,
            'limit': limit,
            'order_status': order_status
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

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

        if symbol.endswith('USDT'):
            path = self.endpoint + '/private/linear/order/cancel'
        else:
            path = self.endpoint + '/v2/private/order/cancel'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

    def cancel_all_active_orders(self, symbol):
        '''Cancels all open orders for a given symbol.
        
        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string, 
            e.g. 'BTCUSD'.

        '''

        path = self.endpoint + '/v2/private/order/cancelAll'
        query = {
            'symbol': symbol
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

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

        path = self.endpoint + '/open-api/order/replace'
        query = {
            'order_id': order_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

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

        if symbol.endswith('USDT'):
            path = self.endpoint + '/private/linear/order/search'
        else:
            path = self.endpoint + '/v2/private/order'
        query = {
            'symbol': symbol,
            'order_id': order_id,
            'order_link_id': order_link_id
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

    '''
    Conditional Orders
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

        path = self.endpoint + '/open-api/stop-order/create'
        query = {
            'side': side,
            'symbol': symbol,
            'order_type': order_type,
            'qty': qty,
            'price': price,
            'base_price': base_price,
            'stop_px': stop_px,
            'time_in_force': time_in_force,
            'trigger_by': trigger_by,
            'close_on_trigger': close_on_trigger,
            'order_link_id': order_link_id
        }
        return self._submit_request(method='POST', path=path, query=query, 
            auth=True)

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

        path = self.endpoint + '/open-api/stop-order/list'
        query = {
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id,
            'symbol': symbol,
            'stop_order_status': stop_order_status,
            'order': order,
            'page': page,
            'limit': limit
        }
        return self._submit_request(method='GET', path=path, query=query, 
            auth=True)

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

        path = self.endpoint + '/open-api/stop-order/cancel'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

    def cancel_all_conditional_orders(self, symbol):
        '''Cancels all open conditional orders for a given symbol.
        
        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string, 
            e.g. 'BTCUSD'.

        '''

        path = self.endpoint + '/v2/private/stop-order/cancelAll'
        query = {
            'symbol': symbol
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

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

        path = self.endpoint + '/open-api/stop-order/replace'
        query = {
            'stop_order_id': stop_order_id,
            'order_id': order_id,
            'symbol': symbol,
            'p_r_qty': p_r_qty,
            'p_r_price': p_r_price,
            'p_r_trigger_price': p_r_trigger_price
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

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

        path = self.endpoint + '/v2/private/stop-order'
        query = {
            'symbol': symbol,
            'stop_order_id': stop_order_id,
            'order_link_id': order_link_id
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

    '''
    Leverage
    '''

    def user_leverage(self):
        '''Fetches the user's leverage.
        
        There are no parameters for this method.

        '''

        path = self.endpoint + '/user/leverage'
        return self._submit_request(method='GET', path=path, query={}, 
            auth=True)

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

        path = self.endpoint + '/user/leverage/save'
        query = {
            'symbol': symbol,
            'leverage': leverage
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

    '''
    Position
    '''

    def my_position(self, symbol):
        '''Fetches the user's position.
        
        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string, 
            e.g. 'BTCUSD'.

        '''

        path = self.endpoint + '/v2/private/position/list'
        query = {
            'symbol': symbol
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

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

        path = self.endpoint + '/position/change-position-margin'
        query = {
            'symbol': symbol,
            'margin': margin
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

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

        path = self.endpoint + '/open-api/position/trading-stop'
        query = {
            'symbol': symbol,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'trailing_stop': trailing_stop,
            'new_trailing_active': new_trailing_active
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

    '''
    Risk Limit
    '''

    def get_risk_limit(self):
        '''Fetches the user's risk limit.
        
        There are no parameters for this method.

        '''

        path = self.endpoint + '/open-api/wallet/risk-limit/list'
        return self._submit_request(method='GET', path=path, query={}, 
            auth=True)

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

        path = self.endpoint + '/open-api/wallet/risk-limit'
        query = {
            'symbol': symbol,
            'risk_id': risk_id
        }
        return self._submit_request(method='POST', path=path, query=query,
            auth=True)

    '''
    Funding
    '''

    def get_last_funding_rate(self, symbol):
        '''Fetches the last funding rate for the particular symbol.
        
        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string, 
            e.g. 'BTCUSD'.

        '''

        path = self.endpoint + '/open-api/funding/prev-funding-rate'
        query = {
            'symbol': symbol
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

    def my_last_funding_fee(self, symbol):
        '''Fetches the user's last funding fee for the particular symbol.
        
        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string, 
            e.g. 'BTCUSD'.

        '''

        path = self.endpoint + '/open-api/funding/prev-funding'
        query = {
            'symbol': symbol
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

    def predicted_funding_rate(self, symbol):
        '''Fetches the next predicted funding rate for the particular 
        symbol.
        
        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string, 
            e.g. 'BTCUSD'.

        '''

        path = self.endpoint + '/open-api/funding/predicted-funding'
        query = {
            'symbol': symbol
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

    '''
    API Key Info
    '''

    def api_key_info(self):
        '''Fetches information about the user's current API key.
        
        There are no parameters for this method.

        '''

        path = self.endpoint + '/open-api/api-key'
        return self._submit_request(method='GET', path=path, query={}, 
            auth=True)

    '''
    Wallet Data Endpoints
    See https://bybit-exchange.github.io/docs/inverse/#t-wallet
    for more information.

    /v2/private/wallet/balance
    /open-api/wallet/fund/records
    /open-api/wallet/withdraw/list
    /v2/private/execution/list
    '''

    def get_wallet_balance(self, coin):
        '''Fetches the user's wallet balance.
        
        Parameters
        ------------------------
        coin : str
            Required parameter. The cryptocurrency ticker as a string, 
            e.g. 'BTC'.

        '''

        path = self.endpoint + '/v2/private/wallet/balance'
        query = {
            'coin': coin
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

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

        path = self.endpoint + '/open-api/wallet/fund/records'
        query = {
            'start_date': start_date,
            'end_date': end_date,
            'currency': currency,
            'coin': coin,
            'wallet_fund_type': wallet_fund_type,
            'page': page,
            'limit': limit
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

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

        path = self.endpoint + '/open-api/wallet/withdraw/list'
        query = {
            'start_date': start_date,
            'end_date': end_date,
            'coin': coin,
            'status': status,
            'page': page,
            'limit': limit
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

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

        path = self.endpoint + '/v2/private/execution/list'
        query = {
            'order_id': order_id,
            'symbol': symbol,
            'start_time': start_time,
            'page': page,
            'limit': limit
        }
        return self._submit_request(method='GET', path=path, query=query,
            auth=True)

    '''
    API Data Endpoints
    See https://bybit-exchange.github.io/docs/inverse/#t-wallet
    for more information.

    /v2/public/time
    /v2/public/announcement
    '''

    def server_time(self):
        '''Fetches the exchange server time.
        
        There are no parameters for this method.

        '''

        path = self.endpoint + '/v2/public/time'
        return self._submit_request(method='GET', path=path)

    def announcement(self):
        '''Fetches the exchange's recent announcements.
        
        There are no parameters for this method.

        '''

        path = self.endpoint + '/v2/public/announcement'
        return self._submit_request(method='GET', path=path)

    '''
    Additional Methods
    These methods use two or more requests to perform a specific
    function and are exclusive to pybit.
    '''

    def close_position(self, symbol):
        '''Closes your open position.

        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string, 
            e.g. 'BTCUSD'.

        '''

        # First we fetch the user's position.
        r = self._submit_request(
            method='GET', 
            path=self.endpoint + '/v2/private/position/list', 
            query={'symbol' : symbol},
            auth=True
        )

        # Next we detect the position size and side.
        try:
            position = r['result']['size']
            if position == 0:
                return self.logger.error('No position detected.')
            if r['result']['side'] == 'Buy':
                side = 'Sell'
            else:
                side = 'Buy'

        # If there is no returned position, we want to handle that.
        except IndexError:
            return self.logger.error('No position detected.')

        # We should know if we're pinging the inverse or linear perp API.
        if symbol.endswith('USDT'):
            close_path = self.endpoint + '/private/linear/order/create'
        else:
            close_path = self.endpoint + '/v2/private/order/create'
        
        # Submit a market order against your position for the same qty.
        return self._submit_request(
            method='POST', 
            path=close_path, 
            query={
                'symbol' : symbol,
                'order_type': 'Market',
                'side': side,
                'qty': position,
                'time_in_force': 'ImmediateOrCancel'
            },
            auth=True
        )

    '''
    Internal methods; signature and request submission.
    For more information about the request signature, see
    https://bybit-exchange.github.io/docs/inverse/#t-authentication.
    '''

    def _auth(self, method, params, api_key, api_secret):
        '''Generates authentication signature per Bybit API specifications.

        Notes
        -------------------
        Since the POST method requires a JSONified dict, we need to ensure
        the signature uses lowercase booleans instead of Python's
        capitalized booleans. This is done in the bug fix below.
        
        '''

        if api_key is None or api_secret is None:
            raise PermissionError('Authenticated endpoints require keys.')

        # Append required parameters.
        params['api_key'] = api_key
        params['timestamp'] = int(time.time() * 10**3)

        # Sort dictionary alphabetically to create querystring.
        _val = '&'.join(
            [str(k) + '=' + str(v) for k, v in sorted(params.items()) if
                (k != 'sign') and (v is not None)]
            )

        # Bug fix. Replaces all capitalized booleans with lowercase.
        if method == 'POST':
            _val = _val.replace('True', 'true').replace('False', 'false')

        # Return signature.    
        return str(hmac.new(bytes(api_secret, 'utf-8'), 
            bytes(_val, 'utf-8'), digestmod='sha256').hexdigest())

    def _submit_request(self, method=None, path=None, query=None, auth=False):
        '''Submits the request to the API.

        Notes
        -------------------
        We use the params argument for the GET method, and data argument for
        the POST method. Dicts passed to the data argument must be 
        JSONified prior to submitting request.
        
        '''

        # Authenticate if we are using a private endpoint.
        if auth:

            # Prepare signature.
            signature = self._auth(method=method, params=query, 
                api_key=self.api_key, api_secret=self.api_secret)

            # Sort the dictionary alphabetically.
            query = dict(sorted(query.items(), key=lambda x: x))

            # Append the signature to the dictionary.
            query['sign'] = signature

        # Define parameters and log the request.
        if query is not None:
            req_params = {k: v for k, v in query.items() if 
                v is not None}
        else:
            req_params = {}
        self.logger.debug(f'Request -> {method} {path}: {req_params}')

        # Prepare request; use 'params' for GET and 'data' for POST.
        if method == 'GET':
            r = self.client.prepare_request(
                requests.Request(method, path, params=req_params)
            )
        else:
            r = self.client.prepare_request(
                requests.Request(method, path, data=json.dumps(req_params))
            )

        # Send request and return headers with body.
        s = self.client.send(r, timeout=self.timeout)

        # Return dict.
        return s.json()

class WebSocket:
    
    def __init__(self, endpoint, api_key=None, api_secret=None, 
        subscriptions=[], data_cap=200):
        '''Connector for Bybit's WebSocket API.
        
        Parameters
        ------------------------
        endpoint : str
            Required parameter. The endpoint of the remote websocket.
        api_key : str
            Your API key. Required for authenticated endpoints. Defaults
            to None.
        api_secret : str
            Your API secret key. Required for authenticated endpoints.
            Defaults to None.
        subscriptions : list
            A list of desired topics to subscribe to. See API documentation
            for more information. Defaults to an empty list, which will
            raise an error.
        data_cap : int
            The maximum size of the data array retrieved from the API.
            This can be changed for the desired application. Higher
            values introduce latency and other slow-downs. Default value
            is 200.

        Notes
        ------------------------ 
        Inverse Perpetual endpoints:
        wss://stream-testnet.bybit.com/realtime
        wss://stream.bybit.com/realtime

        USDT Perpetual endpoints:
        wss://stream-testnet.bybit.com/realtime_public
        wss://stream-testnet.bybit.com/realtime_private
        wss://stream.bybit.com/realtime_public
        wss://stream.bybit.com/realtime_private

        '''

        if subscriptions == []:
            raise Exception('Subscription list cannot be empty!')

        # Setup logger.
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Initializing WebSocket.')

        # Ensure authentication for private topics.
        if any(i in subscriptions for i in ['position', 'execution',
            'order', 'stop_order', 'wallet']) and api_key == None:
            raise PermissionError('You must be authorized to use '
                'private topics!')

        # Set endpoint.
        self.endpoint = endpoint

        # Set API keys.
        self.api_key = api_key
        self.api_secret = api_secret

        # Set parameters for WebSocket.
        self.subscriptions = subscriptions
        self.data_cap = data_cap

        # Set initial booleans.
        self.exited = False
        self.auth = False

        # Initialize dictionary and connect.
        self.data = {}
        self._connect(self.endpoint)

    def fetch(self, topics:list):
        '''Fetches data from the subscribed topic..
        
        Parameters
        ------------------------
        topic : list
            Required parameter. The subscribed topic(s) to poll.

        '''

        try:
            return [self.data[i].pop() for i in topics]
        except KeyError as e:
            self.logger.info(f'Subscription missing: {e}')
            return []

    def ping(self):
        '''Pings the remote server to test the connection. The status of the
        ping can be monitored using fetch(['ping']).'''

        self.ws.send('{\'op\':\'ping\'}')

    def exit(self):
        '''Closes the websocket connection.'''

        self.exited = True
        self.ws.close()

    def _auth(self):
        '''Authorize websocket connection.'''

        # Generate expires.
        expires = str(int(time.time() * 10**3))

        # Generate signature.
        _val = 'GET/realtime' + expires
        signature = str(hmac.new(bytes(self.api_secret, 'utf-8'), 
            bytes(_val, 'utf-8'), digestmod='sha256').hexdigest())

        # Authenticate with API.
        self.ws.send(
            json.dumps({
                'op': 'auth',
                'args': [self.api_key, expires, signature]
            })
        )

    def _connect(self, url):
        '''Connect to the websocket in a thread.'''

        self.ws = websocket.WebSocketApp(url, 
            on_message=self._on_message, on_close=self._on_close,
            on_open=self._on_open, on_error=self._on_error,
            keep_running=True)

        # Setup the thread running WebSocketApp.
        self.wst = threading.Thread(target=lambda: self.ws.run_forever())

        # Configure as daemon; start.
        self.wst.daemon = True
        self.wst.start()

        # Attempt to connect for X seconds.
        retries = 10
        while retries > 0 and (not self.ws.sock or not self.ws.sock.connected):
            retries -= 1
            time.sleep(1)

        # If connection was not successful, raise error.
        if retries <= 0:
            self.exit()
            raise websocket.WebSocketTimeoutException('Connection failed.')

        # If given an api_key, authenticate.
        if self.api_key and self.api_secret:
            self._auth()

        # Subscribe to the requested topics.
        self.ws.send(
            json.dumps({
                'op': 'subscribe',
                'args': self.subscriptions
            })
        )

        # Initialize the topics.
        for topic in self.subscriptions:
            if topic not in self.data:
                self.data[topic] = []

    def _on_message(self, message):
        '''Parse a couple select messages. Similar structure to the
        official WS connector. '''
        
        # Load dict of message.
        msg_json = json.loads(message)

        # If 'success' exists.
        if 'success' in msg_json:   

            # If 'request' exists, look for 'auth'.
            if 'request' in msg_json and msg_json['request']['op'] == 'auth':
                self.auth = True

            # If 'ret_msg' exists, look for ping received.
            if 'ret_msg' in msg_json and msg_json['ret_msg'] == 'pong':
                self.data['pong'].append('Ping success.')

        # If 'topic' exists.
        if 'topic' in msg_json:
            
            # Append new incoming data.
            data_topic = self.data[msg_json['topic']]
            data_topic.append(msg_json['data'])

            # Shrink length of topic if it exceeds the maximum.
            if len(data_topic) > self.data_cap:
                data_topic = data_topic[self.data_cap//2:]

    def _on_error(self, error):
        '''Exit on errors and raise exception.'''

        if not self.exited:
            self.logger.info(f'WebSocket encountered error: {error}.')
            raise websocket.WebSocketException(error)

    def _on_open(self):
        '''Log WS open.'''

        self.logger.debug('WebSocket opened.')

    def _on_close(self):
        '''Log WS close.'''

        self.logger.info('WebSocket closed.')
