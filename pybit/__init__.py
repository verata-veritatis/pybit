# -*- coding: utf-8 -*-

"""
pybit
------------------------

pybit is a lightweight and high-performance API connector for the
RESTful and WebSocket APIs of the Bybit exchange.

Documentation can be found at
https://github.com/verata-veritatis/pybit

:copyright: (c) 2020 verata-veritatis
:license: MIT License

"""

import time
import hmac
import json
import logging
import threading
import requests
import websocket

from concurrent.futures import ThreadPoolExecutor

VERSION = '1.0.3'


class HTTP:
    """
    Connector for Bybit's HTTP API.

    endpoint : str
        Required parameter. The endpoint URL of the HTTP API, e.g.
        'https://api-testnet.bybit.com'.
    api_key : str
        Your API key. Required for authenticated endpoints. Defaults
        to None.
    api_secret : str
        Your API secret key. Required for authenticated endpoints.
        Defaults to None.
    logging_level : int
        The logging level of the built-in logger. Defaults to
        logging.INFO. Options are CRITICAL (50), ERROR (40),
        WARNING (30), INFO (20), DEBUG (10), or NOTSET (0).
    http_timeout : int
        The timeout of each API request in seconds. Defaults to 10
        seconds.
    referral_id : str
        An optional referer ID can be added to each request for
        identification.

    """

    def __init__(self, endpoint, api_key=None, api_secret=None,
                 logging_level=logging.INFO, http_timeout=10, referral_id=None):
        """Initializes the HTTP class."""

        # Set the endpoint.
        self.endpoint = endpoint

        # Setup logger.
        logging.basicConfig(
            level=logging_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing HTTP session.')

        # Set API keys.
        self.api_key = api_key
        self.api_secret = api_secret

        # Set timeout.
        self.timeout = http_timeout

        # Initialize requests session.
        self.client = requests.Session()
        self.client.headers.update(
            {
                'User-Agent': 'pybit-' + VERSION,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        )

        # Add referral ID to header.
        if referral_id is not None:
            self.client.headers.update({'Referer': referral_id})

    def exit(self):
        """Closes the request session."""
        self.client.close()
        self.logger.info('HTTP session closed.')

    def orderbook(self, **kwargs):
        """
        Get the orderbook.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-orderbook.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/orderBook/L2',
            query=kwargs
        )

    def query_kline(self, **kwargs):
        """
        Get kline.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-querykline.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/kline/list',
            query=kwargs
        )

    def latest_information_for_symbol(self, **kwargs):
        """
        Get the latest information for symbol.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-latestsymbolinfo.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/tickers',
            query=kwargs
        )

    def public_trading_records(self, **kwargs):
        """
        Get recent trades. You can find a complete history of trades on Bybit
        at https://public.bybit.com/.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-latestsymbolinfo.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/trading-records',
            query=kwargs
        )

    def query_symbol(self):
        """
        Get symbol info.

        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/symbols'
        )

    def liquidated_orders(self, **kwargs):
        """
        Retrieve the liquidated orders. The query range is the last seven days
        of data.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-query_liqrecords.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/liq-records',
            query=kwargs
        )

    def query_mark_price_kline(self, **kwargs):
        """
        Query mark price kline (like query_kline but for mark price).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-markpricekline.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/mark-price-kline',
            query=kwargs
        )

    def open_interest(self, **kwargs):
        """
        Gets the total amount of unsettled contracts. In other words, the total
        number of contracts held in open positions.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-marketopeninterest.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/open-interest',
            query=kwargs
        )

    def latest_big_deal(self, **kwargs):
        """
        Obtain filled orders worth more than 500,000 USD within the last 24h.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-marketbigdeal.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/big-deal',
            query=kwargs
        )

    def long_short_ratio(self, **kwargs):
        """
        Gets the Bybit long-short ratio.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-marketaccountratio.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/account-ratio',
            query=kwargs
        )

    def place_active_order(self, **kwargs):
        """
        Places an active order. For more information, see
        https://bybit-exchange.github.io/docs/inverse/#t-activeorders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-activeorders.
        :returns: Request results as dictionary.
        """

        if kwargs['symbol'].endswith('USDT'):
            path = self.endpoint + '/private/linear/order/create'
        else:
            path = self.endpoint + '/v2/private/order/create'
        return self._submit_request(
            method='POST',
            path=path,
            query=kwargs,
            auth=True
        )

    def place_active_order_bulk(self, orders: list, max_in_parallel=10):
        """
        Places multiple active orders in bulk using multithreading. For more
        information on place_active_order, see
        https://bybit-exchange.github.io/docs/inverse/#t-activeorders.

        :param list orders: A list of orders and their parameters.
        :param max_in_parallel: The number of requests to be sent in parallel.
            Note that you are limited to 50 requests per second.
        :returns: Future request result dictionaries as a list.
        """

        with ThreadPoolExecutor(max_workers=max_in_parallel) as executor:
            executions = [
                executor.submit(
                    self.place_active_order,
                    **order
                ) for order in orders
            ]
        executor.shutdown()
        return [execution.result() for execution in executions]

    def get_active_order(self, **kwargs):
        """
        Gets an active order. For more information, see
        https://bybit-exchange.github.io/docs/inverse/#t-getactive.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-getactive.
        :returns: Request results as dictionary.
        """

        if kwargs['symbol'].endswith('USDT'):
            path = self.endpoint + '/private/linear/order/list'
        else:
            path = self.endpoint + '/open-api/order/list'
        return self._submit_request(
            method='GET',
            path=path,
            query=kwargs,
            auth=True
        )

    def cancel_active_order(self, **kwargs):
        """
        Cancels an active order. For more information, see
        https://bybit-exchange.github.io/docs/inverse/#t-cancelactive.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-cancelactive.
        :returns: Request results as dictionary.
        """

        if kwargs['symbol'].endswith('USDT'):
            path = self.endpoint + '/private/linear/order/cancel'
        else:
            path = self.endpoint + '/v2/private/order/cancel'
        return self._submit_request(
            method='POST',
            path=path,
            query=kwargs,
            auth=True
        )

    def cancel_active_order_bulk(self, orders: list, max_in_parallel=10):
        """
        Cancels multiple active orders in bulk using multithreading. For more
        information on cancel_active_order, see
        https://bybit-exchange.github.io/docs/inverse/#t-activeorders.

        :param list orders: A list of orders and their parameters.
        :param max_in_parallel: The number of requests to be sent in parallel.
            Note that you are limited to 50 requests per second.
        :returns: Future request result dictionaries as a list.
        """

        with ThreadPoolExecutor(max_workers=max_in_parallel) as executor:
            executions = [
                executor.submit(
                    self.cancel_active_order,
                    **order
                ) for order in orders
            ]
        executor.shutdown()
        return [execution.result() for execution in executions]

    def cancel_all_active_orders(self, **kwargs):
        """
        Cancel all active orders that are unfilled or partially filled. Fully
        filled orders cannot be cancelled.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-cancelallactive.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/v2/private/order/cancelAll',
            query=kwargs,
            auth=True
        )

    def replace_active_order(self, **kwargs):
        """
        Replace order can modify/amend your active orders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-replaceactive.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/open-api/order/replace',
            query=kwargs,
            auth=True
        )

    def replace_active_order_bulk(self, orders: list, max_in_parallel=10):
        """
        Replaces multiple active orders in bulk using multithreading. For more
        information on replace_active_order, see
        https://bybit-exchange.github.io/docs/inverse/#t-replaceactive.

        :param list orders: A list of orders and their parameters.
        :param max_in_parallel: The number of requests to be sent in parallel.
            Note that you are limited to 50 requests per second.
        :returns: Future request result dictionaries as a list.
        """

        with ThreadPoolExecutor(max_workers=max_in_parallel) as executor:
            executions = [
                executor.submit(
                    self.replace_active_order,
                    **order
                ) for order in orders
            ]
        executor.shutdown()
        return [execution.result() for execution in executions]

    def query_active_order(self, **kwargs):
        """
        Query real-time active order information.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-queryactive.
        :returns: Request results as dictionary.
        """

        if kwargs['symbol'].endswith('USDT'):
            path = self.endpoint + '/private/linear/order/search'
        else:
            path = self.endpoint + '/v2/private/order'
        return self._submit_request(
            method='GET',
            path=path,
            query=kwargs,
            auth=True
        )

    def place_conditional_order(self, **kwargs):
        """
        Places a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/inverse/#t-placecond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-placecond.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/open-api/stop-order/create',
            query=kwargs,
            auth=True
        )

    def place_conditional_order_bulk(self, orders: list, max_in_parallel=10):
        """
        Places multiple conditional orders in bulk using multithreading. For
        more information on place_active_order, see
        https://bybit-exchange.github.io/docs/inverse/#t-placecond.

        :param list orders: A list of orders and their parameters.
        :param max_in_parallel: The number of requests to be sent in parallel.
            Note that you are limited to 50 requests per second.
        :returns: Future request result dictionaries as a list.
        """

        with ThreadPoolExecutor(max_workers=max_in_parallel) as executor:
            executions = [
                executor.submit(
                    self.place_conditional_order,
                    **order
                ) for order in orders
            ]
        executor.shutdown()
        return [execution.result() for execution in executions]

    def get_conditional_order(self, **kwargs):
        """
        Gets a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/inverse/#t-getcond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-getcond.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/open-api/stop-order/list',
            query=kwargs,
            auth=True
        )

    def cancel_conditional_order(self, **kwargs):
        """
        Cancels a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/inverse/#t-cancelcond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-cancelcond.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/open-api/stop-order/cancel',
            query=kwargs,
            auth=True
        )

    def cancel_conditional_order_bulk(self, orders: list, max_in_parallel=10):
        """
        Cancels multiple conditional orders in bulk using multithreading. For
        more information on cancel_active_order, see
        https://bybit-exchange.github.io/docs/inverse/#t-cancelcond.

        :param list orders: A list of orders and their parameters.
        :param max_in_parallel: The number of requests to be sent in parallel.
            Note that you are limited to 50 requests per second.
        :returns: Future request result dictionaries as a list.
        """

        with ThreadPoolExecutor(max_workers=max_in_parallel) as executor:
            executions = [
                executor.submit(
                    self.cancel_conditional_order,
                    **order
                ) for order in orders
            ]
        executor.shutdown()
        return [execution.result() for execution in executions]

    def cancel_all_conditional_orders(self, **kwargs):
        """
        Cancel all conditional orders that are unfilled or partially filled.
        Fully filled orders cannot be cancelled.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-cancelallcond.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/v2/private/stop-order/cancelAll',
            query=kwargs,
            auth=True
        )

    def replace_conditional_order(self, **kwargs):
        """
        Replace conditional order can modify/amend your conditional orders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-replacecond.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/open-api/stop-order/replace',
            query=kwargs,
            auth=True
        )

    def replace_conditional_order_bulk(self, orders: list, max_in_parallel=10):
        """
        Replaces multiple conditional orders in bulk using multithreading. For
        more information on replace_active_order, see
        https://bybit-exchange.github.io/docs/inverse/#t-replacecond.

        :param list orders: A list of orders and their parameters.
        :param max_in_parallel: The number of requests to be sent in parallel.
            Note that you are limited to 50 requests per second.
        :returns: Future request result dictionaries as a list.
        """

        with ThreadPoolExecutor(max_workers=max_in_parallel) as executor:
            executions = [
                executor.submit(
                    self.replace_conditional_order,
                    **order
                ) for order in orders
            ]
        executor.shutdown()
        return [execution.result() for execution in executions]

    def query_conditional_order(self, **kwargs):
        """
        Query real-time conditional order information.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-querycond.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/stop-order',
            query=kwargs,
            auth=True
        )

    def my_position(self, **kwargs):
        """
        Get my position list.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-myposition.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/position/list',
            query=kwargs,
            auth=True
        )

    def change_margin(self, **kwargs):
        """
        Update margin.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-changemargin.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/position/change-position-margin',
            query=kwargs,
            auth=True
        )

    def set_trading_stop(self, **kwargs):
        """
        Set take profit, stop loss, and trailing stop for your open position.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-tradingstop.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/open-api/position/trading-stop',
            query=kwargs,
            auth=True
        )

    def user_leverage(self, **kwargs):
        """
        Get user leverage.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-getleverage.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/user/leverage',
            query=kwargs,
            auth=True
        )

    def change_user_leverage(self, **kwargs):
        """
        Change user leverage.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-changeleverage.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/user/leverage/save',
            query=kwargs,
            auth=True
        )

    def user_trade_records(self, **kwargs):
        """
        Get user's trading records. The results are ordered in ascending order
        (the first item is the oldest).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-usertraderecords.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/execution/list',
            query=kwargs,
            auth=True
        )

    def closed_profit_and_loss(self, **kwargs):
        """
        Get user's closed profit and loss records. The results are ordered in
        descending order (the first item is the latest).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-closedprofitandloss.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/trade/closed-pnl/list',
            query=kwargs,
            auth=True
        )

    def get_risk_limit(self):
        """
        Get risk limit.

        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/open-api/wallet/risk-limit/list',
            auth=True
        )

    def set_risk_limit(self, **kwargs):
        """
        Set risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-setrisklimit.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/open-api/wallet/risk-limit',
            query=kwargs,
            auth=True
        )

    def get_last_funding_rate(self, **kwargs):
        """
        The funding rate is generated every 8 hours at 00:00 UTC, 08:00 UTC and
        16:00 UTC. For example, if a request is sent at 12:00 UTC, the funding
        rate generated earlier that day at 08:00 UTC will be sent.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-fundingrate.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/open-api/funding/prev-funding-rate',
            query=kwargs,
            auth=True
        )

    def my_last_funding_fee(self, **kwargs):
        """
        Funding settlement occurs every 8 hours at 00:00 UTC, 08:00 UTC and
        16:00 UTC. The current interval's fund fee settlement is based on the
        previous interval's fund rate. For example, at 16:00, the settlement is
        based on the fund rate generated at 8:00. The fund rate generated at
        16:00 will be used at 0:00 the next day.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-mylastfundingfee.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/open-api/funding/prev-funding',
            query=kwargs,
            auth=True
        )

    def predicted_funding_rate(self, **kwargs):
        """
        Get predicted funding rate and my funding fee.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-predictedfunding.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/open-api/funding/predicted-funding',
            query=kwargs,
            auth=True)

    def api_key_info(self):
        """
        Get user's API key info.

        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/open-api/api-key',
            auth=True
        )

    def lcp_info(self, **kwargs):
        """
        Get user's LCP (data refreshes once an hour). Only supports inverse
        perpetual at present. See
        https://bybit-exchange.github.io/docs/inverse/#t-liquidity to learn
        more.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-lcp.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/account/lcp',
            query=kwargs,
            auth=True
        )

    def get_wallet_balance(self, **kwargs):
        """
        Get wallet balance info.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-balance.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/wallet/balance',
            query=kwargs,
            auth=True
        )

    def wallet_fund_records(self, **kwargs):
        """
        Get wallet fund records. This endpoint also shows exchanges from the
        Asset Exchange, where the types for the exchange are
        ExchangeOrderWithdraw and ExchangeOrderDeposit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-walletrecords.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/open-api/wallet/fund/records',
            query=kwargs,
            auth=True)

    def withdraw_records(self, **kwargs):
        """
        Get withdrawal records.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-withdrawrecords.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/open-api/wallet/withdraw/list',
            query=kwargs,
            auth=True)

    def asset_exchange_records(self, **kwargs):
        """
        Get asset exchange records.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-assetexchangerecords.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/exchange-order/list',
            query=kwargs,
            auth=True
        )

    def server_time(self):
        """
        Get Bybit server time.

        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/time'
        )

    def announcement(self):
        """
        Get Bybit OpenAPI announcements in the last 30 days by reverse order.

        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/public/announcement'
        )

    '''
    Additional Methods
    These methods use two or more requests to perform a specific
    function and are exclusive to pybit.
    '''

    def close_position(self, symbol):
        """
        Closes your open position. Makes two requests (position, order).

        Parameters
        ------------------------
        symbol : str
            Required parameter. The symbol of the market as a string,
            e.g. 'BTCUSD'.

        """

        # First we fetch the user's position.
        r = self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/position/list',
            query={'symbol': symbol},
            auth=True
        )

        # Next we detect the position size and side.
        try:
            position = r['result']['size']
            side = 'Buy' if r['result']['side'] == 'Sell' else 'Sell'
            if position == 0:
                return self.logger.error('No position detected.')

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
                'symbol': symbol,
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

    @staticmethod
    def _auth(method, params, api_key, api_secret):
        """
        Generates authentication signature per Bybit API specifications.

        Notes
        -------------------
        Since the POST method requires a JSONified dict, we need to ensure
        the signature uses lowercase booleans instead of Python's
        capitalized booleans. This is done in the bug fix below.

        """

        if api_key is None or api_secret is None:
            raise PermissionError('Authenticated endpoints require keys.')

        # Append required parameters.
        params['api_key'] = api_key
        params['timestamp'] = int(time.time() * 10 ** 3)

        # Sort dictionary alphabetically to create querystring.
        _val = '&'.join(
            [str(k) + '=' + str(v) for k, v in sorted(params.items()) if
             (k != 'sign') and (v is not None)]
        )

        # Bug fix. Replaces all capitalized booleans with lowercase.
        if method == 'POST':
            _val = _val.replace('True', 'true').replace('False', 'false')

        # Return signature.
        return str(hmac.new(
            bytes(api_secret, 'utf-8'),
            bytes(_val, 'utf-8'), digestmod='sha256'
        ).hexdigest())

    def _submit_request(self, method=None, path=None, query=None, auth=False):
        """
        Submits the request to the API.

        Notes
        -------------------
        We use the params argument for the GET method, and data argument for
        the POST method. Dicts passed to the data argument must be
        JSONified prior to submitting request.

        """

        # Authenticate if we are using a private endpoint.
        if auth:

            # Prepare signature.
            signature = self._auth(
                method=method,
                params=query,
                api_key=self.api_key,
                api_secret=self.api_secret
            )

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
        self.logger.info(f'Request -> {method} {path}: {req_params}')

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
    """
    Connector for Bybit's WebSocket API.

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
    logging_level : int
        The logging level of the built-in logger. Defaults to
        logging.INFO. Options are CRITICAL (50), ERROR (40),
        WARNING (30), INFO (20), DEBUG (10), or NOTSET (0).
    max_data_length : int
        The maximum number of rows for the stored dataset. A smaller
        number will prevent performance or memory issues.
    ping_interval : int
        The number of seconds between each automated ping.
    ping_timeout : int
        The number of seconds to wait for 'pong' before an Exception is
        raised.

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
    """

    def __init__(self, endpoint, api_key=None, api_secret=None,
                 subscriptions=None, logging_level=logging.INFO,
                 max_data_length=200, ping_interval=30, ping_timeout=10):
        """Initializes the WebSocket class."""

        if not subscriptions:
            raise Exception('Subscription list cannot be empty!')

        # Require symbol on 'trade' topic.
        if 'trade' in subscriptions:
            raise Exception('\'trade\' requires a ticker, e.g. '
                            '\'trade.BTCUSD\'.')

        # Require currency on 'insurance' topic.
        if 'insurance' in subscriptions:
            raise Exception('\'insurance\' requires a currency, e.g. '
                            '\'insurance.BTC\'.')

        # Require timeframe and ticker on 'klineV2' topic.
        if 'klineV2' in subscriptions:
            raise Exception('\'klineV2\' requires a timeframe and ticker, e.g.'
                            ' \'klineV2.5.BTCUSD\'.')

        # Setup logger.
        logging.basicConfig(
            level=logging_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing WebSocket.')

        # Ensure authentication for private topics.
        if any(i in subscriptions for i in [
            'position',
            'execution',
            'order',
            'stop_order',
            'wallet'
        ]) and api_key is None:
            raise PermissionError('You must be authorized to use '
                                  'private topics!')

        # Set endpoint.
        self.endpoint = endpoint

        # Set API keys.
        self.api_key = api_key
        self.api_secret = api_secret

        # Set topic subscriptions for WebSocket.
        self.subscriptions = subscriptions
        self.max_length = max_data_length

        # Set ping settings.
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

        # Set initial booleans.
        self.exited = False
        self.auth = False

        # Initialize dictionary and connect.
        self.data = {}
        self._connect(self.endpoint)

    def fetch(self, topic):
        """Fetches data from the subscribed topic.

        Parameters
        ------------------------
        topic : str
            Required parameter. The subscribed topic to poll.
        """

        # If topic isn't a string.
        if not isinstance(topic, str):
            self.logger.error('Topic argument must be a string.')
            return

        # If the topic given isn't in the initial subscribed list.
        if topic not in self.subscriptions:
            self.logger.error('You aren\'t subscribed to this topic.')
            return

        # Pop all trade, execution, or order data on each poll.
        if topic.startswith((
                'trade',
                'execution',
                'order',
                'stop_order'
        )) and not topic.startswith('orderBook'):
            data = self.data[topic].copy()
            self.data[topic] = []
            return data
        else:
            return self.data[topic]

    def ping(self):
        """Pings the remote server to test the connection. The status of the
        connection can be monitored using ws.ping()."""

        self.ws.send(json.dumps({'op': 'ping'}))

    def exit(self):
        """Closes the websocket connection."""

        self.exited = True
        self.ws.close()

    def _auth(self):
        """Authorize websocket connection."""

        # Generate expires.
        expires = str(int(time.time() * 10 ** 3))

        # Generate signature.
        _val = 'GET/realtime' + expires
        signature = str(hmac.new(
            bytes(self.api_secret, 'utf-8'),
            bytes(_val, 'utf-8'), digestmod='sha256'
        ).hexdigest())

        # Authenticate with API.
        self.ws.send(
            json.dumps({
                'op': 'auth',
                'args': [self.api_key, expires, signature]
            })
        )

    def _connect(self, url):
        """Connect to the websocket in a thread."""

        self.ws = websocket.WebSocketApp(
            url=url,
            on_message=self._on_message,
            on_close=self._on_close,
            on_open=self._on_open,
            on_error=self._on_error
        )

        # Setup the thread running WebSocketApp.
        self.wst = threading.Thread(target=lambda: self.ws.run_forever(
            ping_interval=self.ping_interval,
            ping_timeout=self.ping_timeout
        ))

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
                self.data[topic] = {}

    @staticmethod
    def _find_index(source, target):
        """Find the index in source list of the targeted ID."""
        return next(i for i, j in enumerate(source) if j['id'] == target['id'])

    def _on_message(self, message):
        """Parse a couple select messages. Similar structure to the
        official WS connector. """

        # Load dict of message.
        msg_json = json.loads(message)

        # If 'success' exists and is True.
        if 'success' in msg_json and msg_json['success']:

            # If 'request' exists.
            if 'request' in msg_json:

                # If we get succesful auth, notify user.
                if msg_json['request']['op'] == 'auth':
                    self.logger.info('Authorization successful.')
                    self.auth = True

                # If we get successful subscription, notify user.
                if msg_json['request']['op'] == 'subscribe':
                    sub = msg_json['request']['args'][0]
                    self.logger.info(f'Subscription to {sub} successful.')

        # If 'success' exists but is False.
        elif 'success' in msg_json and not msg_json['success']:

            response = msg_json['ret_msg']
            if 'unknown topic' in response:
                self.logger.error('Couldn\'t subscribe to topic.'
                                  f' Error: {response}.')

            # If we get unsuccesful auth, notify user.
            elif msg_json['request']['op'] == 'auth':
                self.logger.info('Authorization failed. Please check your '
                                 'API keys and restart.')

        elif 'topic' in msg_json:

            topic = msg_json['topic']

            # If incoming 'orderbookL2' data.
            if 'orderBookL2' in topic:

                # Record the initial snapshot.
                if 'snapshot' in msg_json['type']:
                    self.data[topic] = msg_json['data']

                if 'delta' in msg_json['type']:

                    # Delete.
                    for entry in msg_json['data']['delete']:
                        idx = self._find_index(self.data[topic], entry)
                        self.data[topic].pop(idx)

                    # Update.
                    for entry in msg_json['data']['update']:
                        idx = self._find_index(self.data[topic], entry)
                        self.data[topic][idx] = entry

                    # Insert.
                    for entry in msg_json['data']['insert']:
                        self.data[topic].append(entry)

            # For incoming 'trade', 'execution', 'order' and 'stop_order'
            # data.
            elif any(i in topic for i in ['trade', 'execution', 'order',
                                          'stop_order']):

                # Keep appending or create new list if not already created.
                try:
                    for i in msg_json['data']:
                        self.data[topic].append(i)
                except AttributeError:
                    self.data[topic] = [msg_json['data']]

                # If list is too long, pop the first entry.
                if len(self.data[topic]) > self.max_length:
                    self.data[topic].pop(0)

            # If incoming 'instrument_info', 'klineV2', or 'wallet' data.
            elif any(i in topic for i in ['insurance', 'klineV2', 'wallet']):

                # Record incoming data.
                self.data[topic] = msg_json['data'][0]

            # If incoming 'instrument_info' data.
            elif 'instrument_info' in topic:

                # Record the initial snapshot.
                if 'snapshot' in msg_json['type']:
                    self.data[topic] = msg_json['data']

                # Make updates according to delta response.
                elif 'delta' in msg_json['type']:
                    for i in msg_json['data']['update'][0]:
                        self.data[topic][i] = msg_json['data']['update'][0][i]

            # If incoming 'position' data.
            elif 'position' in topic:

                # Record incoming position data.
                data = msg_json['data'][0]
                self.data[topic][msg_json['data'][0]['symbol']] = data

    def _on_error(self, error):
        """Exit on errors and raise exception."""

        if not self.exited:
            self.logger.info(f'WebSocket encountered error: {error}.')
            raise websocket.WebSocketException(error)

    def _on_open(self):
        """Log WS open."""

        self.logger.debug('WebSocket opened.')

    def _on_close(self):
        """Log WS close."""

        self.logger.info('WebSocket closed.')
