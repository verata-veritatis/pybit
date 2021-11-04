# -*- coding: utf-8 -*-

"""
pybit
------------------------

pybit is a lightweight and high-performance API connector for the
RESTful and WebSocket APIs of the Bybit exchange.

Documentation can be found at
https://github.com/verata-veritatis/pybit

:copyright: (c) 2020-2021 verata-veritatis
:license: MIT License

"""

import time
import hmac
import json
import logging
import threading
import requests
import websocket

from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor

from .exceptions import FailedRequestError, InvalidRequestError

# Requests will use simplejson if available.
try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError

# Versioning.
VERSION = '1.3.2'


class HTTP:
    """
    Connector for Bybit's HTTP API.

    :param endpoint: The endpoint URL of the HTTP API, e.g.
        'https://api-testnet.bybit.com'.
    :type endpoint: str

    :param api_key: Your API key. Required for authenticated endpoints. Defaults
        to None.
    :type api_key: str

    :param api_secret: Your API secret key. Required for authenticated
        endpoints. Defaults to None.
    :type api_secret: str

    :param logging_level: The logging level of the built-in logger. Defaults to
        logging.INFO. Options are CRITICAL (50), ERROR (40), WARNING (30),
        INFO (20), DEBUG (10), or NOTSET (0).
    :type logging_level: Union[int, logging.level]

    :param log_requests: Whether or not pybit should log each HTTP request.
    :type log_requests: bool

    :param request_timeout: The timeout of each API request in seconds. Defaults
        to 10 seconds.
    :type request_timeout: int

    :param recv_window: How long an HTTP request is valid in ms. Default is
        5000.
    :type recv_window: int

    :param force_retry: Whether or not pybit should retry a timed-out request.
    :type force_retry: bool

    :param retry_codes: A list of non-fatal status codes to retry on.
    :type retry_codes: set

    :param ignore_codes: A list of non-fatal status codes to ignore.
    :type ignore_codes: set

    :param max_retries: The number of times to re-attempt a request.
    :type max_retries: int

    :param retry_delay: Seconds between retries for returned error or timed-out
        requests. Default is 3 seconds.
    :type retry_delay: int

    :param referral_id: An optional referer ID can be added to each request for
        identification.
    :type referral_id: str

    :returns: pybit.HTTP session.

    """

    def __init__(self, endpoint=None, api_key=None, api_secret=None,
                 logging_level=logging.INFO, log_requests=False,
                 request_timeout=10, recv_window=5000, force_retry=False,
                 retry_codes=None, ignore_codes=None, max_retries=3,
                 retry_delay=3, referral_id=None, spot=False):
        """Initializes the HTTP class."""

        # Set the endpoint.
        if endpoint is None:
            self.endpoint = 'https://api.bybit.com'
        else:
            self.endpoint = endpoint

        # Setup logger.

        self.logger = logging.getLogger(__name__)

        if len(logging.root.handlers) == 0:
            #no handler on root logger set -> we add handler just for this logger to not mess with custom logic from outside
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                                   datefmt='%Y-%m-%d %H:%M:%S'
                                                   )
                                 )
            handler.setLevel(logging_level)
            self.logger.addHandler(handler)

        self.logger.debug('Initializing HTTP session.')
        self.log_requests = log_requests

        # Set API keys.
        self.api_key = api_key
        self.api_secret = api_secret

        # Set timeout.
        self.timeout = request_timeout
        self.recv_window = recv_window
        self.force_retry = force_retry
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Set whitelist of non-fatal Bybit status codes to retry on.
        if retry_codes is None:
            self.retry_codes = {10002, 10006, 30034, 30035, 130035, 130150}
        else:
            self.retry_codes = retry_codes

        # Set whitelist of non-fatal Bybit status codes to ignore.
        if ignore_codes is None:
            self.ignore_codes = set()
        else:
            self.ignore_codes = ignore_codes

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
        if referral_id:
            self.client.headers.update({'Referer': referral_id})

        # If True, calls spot endpoints rather than futures endpoints.
        self.spot = spot

    def _exit(self):
        """Closes the request session."""
        self.client.close()
        self.logger.debug('HTTP session closed.')

    def orderbook(self, **kwargs):
        """
        Get the orderbook.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-orderbook.
        :returns: Request results as dictionary.
        """

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/quote/v1/depth'
        else:
            suffix = '/v2/public/orderBook/L2'
        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def merged_orderbook(self, **kwargs):
        """
        Get the merged orderbook.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/spot/#t-mergedorderbook.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/spot/quote/v1/depth/merged',
            query=kwargs
        )

    def query_kline(self, **kwargs):
        """
        Get kline.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-querykline.
        :returns: Request results as dictionary.
        """

        # Replace query param 'from_time' since 'from' keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if 'from_time' in kwargs:
            kwargs['from'] = kwargs.pop('from_time')

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/quote/v1/kline'
        elif kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/public/linear/kline'
        else:
            suffix = '/v2/public/kline/list'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def latest_information_for_symbol(self, **kwargs):
        """
        Get the latest information for symbol.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-latestsymbolinfo.
        :returns: Request results as dictionary.
        """

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/quote/v1/ticker/24hr'
        else:
            suffix = '/v2/public/tickers'
        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def last_traded_price(self, **kwargs):
        """
        Get the last traded price.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/spot/#t-lasttradedprice.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/spot/quote/v1/ticker/price',
            query=kwargs
        )

    def best_bid_ask_price(self, **kwargs):
        """
        Get the best bid/ask price.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/spot/#t-bestbidask.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/spot/quote/v1/ticker/book_ticker',
            query=kwargs
        )

    def public_trading_records(self, **kwargs):
        """
        Get recent trades. You can find a complete history of trades on Bybit
        at https://public.bybit.com/.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-publictradingrecords.
        :returns: Request results as dictionary.
        """

        # Replace query param 'from_id' since 'from' keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if 'from_id' in kwargs:
            kwargs['from'] = kwargs.pop('from_id')

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/quote/v1/trades'
        elif kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/public/linear/recent-trading-records'
        else:
            suffix = '/v2/public/trading-records'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_symbol(self, **kwargs):
        """
        Get symbol info.

        :returns: Request results as dictionary.
        """

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/v1/symbols'
        else:
            suffix = '/v2/public/symbols'
        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix
        )

    def liquidated_orders(self, **kwargs):
        """
        Retrieve the liquidated orders. The query range is the last seven days
        of data.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-query_liqrecords.
        :returns: Request results as dictionary.
        """

        # Replace query param 'from_id' since 'from' keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if 'from_id' in kwargs:
            kwargs['from'] = kwargs.pop('from_id')

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

        # Replace query param 'from_time' since 'from' keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if 'from_time' in kwargs:
            kwargs['from'] = kwargs.pop('from_time')

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/public/linear/mark-price-kline'
        else:
            suffix = '/v2/public/mark-price-kline'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_index_price_kline(self, **kwargs):
        """
        Query index price kline (like query_kline but for index price).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-queryindexpricekline.
        :returns: Request results as dictionary.
        """

        # Replace query param 'from_time' since 'from' keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if 'from_time' in kwargs:
            kwargs['from'] = kwargs.pop('from_time')

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/public/linear/index-price-kline'
        else:
            suffix = '/v2/public/index-price-kline'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_premium_index_kline(self, **kwargs):
        """
        Query premium index kline (like query_kline but for the premium index
        discount).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-querypremiumindexkline.
        :returns: Request results as dictionary.
        """

        # Replace query param 'from_time' since 'from' keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if 'from_time' in kwargs:
            kwargs['from'] = kwargs.pop('from_time')

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/public/linear/premium-index-kline'
        else:
            suffix = '/v2/public/premium-index-kline'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
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

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/v1/order'
        elif kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/order/create'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/order/create'
        else:
            suffix = '/v2/private/order/create'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
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

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/v1/history-orders'
        elif kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/order/list'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/order/list'
        else:
            suffix = '/v2/private/order/list'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
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

        method = 'POST'
        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/v1/order'
            method = 'DELETE'
        elif kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/order/cancel'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/order/cancel'
        else:
            suffix = '/v2/private/order/cancel'

        return self._submit_request(
            method=method,
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def fast_cancel_active_order(self, **kwargs):
        """
        Fast cancels an active order.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/spot/#t-fastcancelactiveorder.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='DELETE',
            path=self.endpoint + '/spot/v1/order/fast',
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/order/cancel-all'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/order/cancelAll'
        else:
            suffix = '/v2/private/order/cancelAll'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def batch_cancel_active_order(self, **kwargs):
        """
        Batch cancels active orders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/spot/#t-batchcancelactiveorder.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='DELETE',
            path=self.endpoint + '/spot/order/batch-cancel',
            query=kwargs,
            auth=True
        )

    def batch_fast_cancel_active_order(self, **kwargs):
        """
        Batch fast cancels active orders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/spot/#t-batchfastcancelactiveorder.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='DELETE',
            path=self.endpoint + '/spot/order/batch-fast-cancel',
            query=kwargs,
            auth=True
        )

    def batch_cancel_active_order_by_ids(self, **kwargs):
        """
        Batch cancels active order by ids.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/spot/#t-batchcancelactiveorderbyids.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='DELETE',
            path=self.endpoint + '/spot/order/batch-cancel-by-ids',
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/order/replace'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/order/replace'
        else:
            suffix = '/v2/private/order/replace'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
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

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/v1/open-orders'
        elif kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/order/search'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/order'
        else:
            suffix = '/v2/private/order'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/stop-order/create'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/stop-order/create'
        else:
            suffix = '/v2/private/stop-order/create'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def place_conditional_order_bulk(self, orders: list, max_in_parallel=10):
        """
        Places multiple conditional orders in bulk using multithreading. For
        more information on place_active_order, see
        https://bybit-exchange.github.io/docs/inverse/#t-placecond.

        :param orders: A list of orders and their parameters.
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/stop-order/list'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/stop-order/list'
        else:
            suffix = '/v2/private/stop-order/list'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/stop-order/cancel'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/stop-order/cancel'
        else:
            suffix = '/v2/private/stop-order/cancel'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/stop-order/cancel-all'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/stop-order/cancelAll'
        else:
            suffix = '/v2/private/stop-order/cancelAll'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/stop-order/replace'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/stop-order/replace'
        else:
            suffix = '/v2/private/stop-order/replace'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/stop-order/search'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/stop-order'
        else:
            suffix = '/v2/private/stop-order'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def my_position(self, endpoint="", **kwargs):
        """
        Get my position list.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-myposition.
        :param endpoint: The endpoint path, such as "/v2/private/position/list".
            This allows the user to bypass the "symbol" arg, and instead specify
            the desired market contract type (inverse perp, linear perp, etc)
            and receive multiple symbols in the response.
        :returns: Request results as dictionary.
        """

        if endpoint:
            suffix = endpoint
        else:
            if kwargs.get('symbol', '').endswith('USDT'):
                suffix = '/private/linear/position/list'
            elif kwargs.get('symbol', '')[-2:].isdigit():
                suffix = '/futures/private/position/list'
            else:
                suffix = '/v2/private/position/list'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_auto_add_margin(self, **kwargs):
        """
        For linear markets only. Set auto add margin, or Auto-Margin
        Replenishment.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-setautoaddmargin.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='POST',
            path=self.endpoint + '/private/linear/position/set-auto-add-margin',
            query=kwargs,
            auth=True
        )

    def set_leverage(self, **kwargs):
        """
        Change user leverage.
        If you want to switch between cross margin and isolated margin, please
        see cross_isolated_margin_switch.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-setleverage.
        :returns: Request results as dictionary.
        """

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/position/set-leverage'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/position/leverage/save'
        else:
            suffix = '/v2/private/position/leverage/save'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cross_isolated_margin_switch(self, **kwargs):
        """
        Switch Cross/Isolated; must be leverage value when switching from Cross
        to Isolated.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-marginswitch.
        :returns: Request results as dictionary.
        """

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/position/switch-isolated'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/position/switch-isolated'
        else:
            suffix = '/v2/private/position/switch-isolated'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def position_mode_switch(self, **kwargs):
        """
        If you are in One-Way Mode, you can only open one position on Buy or
        Sell side;
        If you are in Hedge Mode, you can open both Buy and Sell side positions
        simultaneously.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-switchpositionmode.
        :returns: Request results as dictionary.
        """

        if kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/position/switch-mode'
        else:
            suffix = '/v2/private/position/switch-mode'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def full_partial_position_tp_sl_switch(self, **kwargs):
        """
        Switch mode between Full or Partial

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-switchmode.
        :returns: Request results as dictionary.
        """
        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/tpsl/switch-mode'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/tpsl/switch-mode'
        else:
            suffix = '/v2/private/tpsl/switch-mode'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/position/change-position-margin'
        else:
            suffix = '/v2/private/position/change-position-margin'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/position/trading-stop'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/position/trading-stop'
        else:
            suffix = '/v2/private/position/trading-stop'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def add_reduce_margin(self, **kwargs):
        """
        For linear markets only. Add margin.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-addmargin.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/private/linear/position/add-margin',
            query=kwargs,
            auth=True
        )

    def user_leverage(self, **kwargs):
        """
        ABANDONED! Please use my_position instead. Fetches user leverage by
        fetching user position.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-getleverage.
        :returns: Request results as dictionary.
        """

        self.logger.warning('This endpoint is deprecated and will be removed. Use my_position()')

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/position/list',
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

        self.logger.warning('This endpoint is deprecated and will be removed. Use set_leverage()')

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

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/v1/myTrades'
        elif kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/trade/execution/list'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/execution/list'
        else:
            suffix = '/v2/private/execution/list'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/trade/closed-pnl/list'
        elif kwargs.get('symbol', '')[-2:].isdigit():
            suffix = '/futures/private/trade/closed-pnl/list'
        else:
            suffix = '/v2/private/trade/closed-pnl/list'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_risk_limit(self, **kwargs):
        """
        Get risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-getrisklimit.
        :returns: Request results as dictionary.
        """

        if kwargs.get('is_linear') in (False, True):
            self.logger.warning("The is_linear argument is obsolete.")

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/public/linear/risk-limit'
        else:
            suffix = '/v2/public/risk-limit/list'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_risk_limit(self, **kwargs):
        """
        Set risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-setrisklimit.
        :returns: Request results as dictionary.
        """

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/position/set-risk'
        else:
            suffix = '/v2/private/position/risk-limit'

        return self._submit_request(
            method='POST',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_the_last_funding_rate(self, **kwargs):
        """
        The funding rate is generated every 8 hours at 00:00 UTC, 08:00 UTC and
        16:00 UTC. For example, if a request is sent at 12:00 UTC, the funding
        rate generated earlier that day at 08:00 UTC will be sent.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-fundingrate.
        :returns: Request results as dictionary.
        """

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/public/linear/funding/prev-funding-rate'
        else:
            suffix = '/v2/public/funding/prev-funding-rate'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/funding/prev-funding'
        else:
            suffix = '/v2/private/funding/prev-funding'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
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

        if kwargs.get('symbol', '').endswith('USDT'):
            suffix = '/private/linear/funding/predicted-funding'
        else:
            suffix = '/v2/private/funding/predicted-funding'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def api_key_info(self):
        """
        Get user's API key info.

        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/account/api-key',
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

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/v1/account'
        else:
            suffix = '/v2/private/wallet/balance'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
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

        # Replace query param 'from_id' since 'from' keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if 'from_id' in kwargs:
            kwargs['from'] = kwargs.pop('from_id')

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/wallet/fund/records',
            query=kwargs,
            auth=True
        )

    def withdraw_records(self, **kwargs):
        """
        Get withdrawal records.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-withdrawrecords.
        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method='GET',
            path=self.endpoint + '/v2/private/wallet/withdraw/list',
            query=kwargs,
            auth=True
        )

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

    def server_time(self, **kwargs):
        """
        Get Bybit server time.

        :returns: Request results as dictionary.
        """

        if self.spot is True or kwargs.get('spot', '') is True:
            suffix = '/spot/v1/time'
        else:
            suffix = '/v2/public/time'

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix
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
        try:
            r = self.my_position(symbol=symbol)['result']

        # If there is no returned position, we want to handle that.
        except KeyError:
            return self.logger.error('No position detected.')

        # Next we generate a list of market orders
        orders = [
            {
                'symbol': symbol,
                'order_type': 'Market',
                'side': 'Buy' if p['side'] == 'Sell' else 'Sell',
                'qty': p['size'],
                'time_in_force': 'ImmediateOrCancel',
                'reduce_only': True,
                'close_on_trigger': True
            } for p in (r if isinstance(r, list) else [r]) if p['size'] > 0
        ]

        if len(orders) == 0:
            return self.logger.error('No position detected.')

        # Submit a market order against each open position for the same qty.
        return self.place_active_order_bulk(orders)
    '''
    Below are methods under https://bybit-exchange.github.io/docs/account_asset
    '''
    def create_internal_transfer(self, **kwargs):
        """
        Create internal transfer.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/account_asset/#t-createinternaltransfer.
        :returns: Request results as dictionary.
        """

        suffix="/asset/v1/private/transfer"
        if self._verify_string(kwargs,'amount'):
            return self._submit_request(
                method='POST',
                path=self.endpoint + suffix,
                query=kwargs,
                auth=True
            )
        else:
            self.logger.error('amount must be in string format')

    def create_subaccount_transfer(self, **kwargs):
        """
        Create internal transfer.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/account_asset/#t-createsubaccounttransfer.
        :returns: Request results as dictionary.
        """

        suffix="/asset/v1/private/sub-member/transfer"

        if self._verify_string(kwargs, 'amount'):
            return self._submit_request(
                method='POST',
                path=self.endpoint + suffix,
                query=kwargs,
                auth=True
            )
        else:
            self.logger.error('amount must be in string format')

    def query_transfer_list(self, **kwargs):
        """
        Create internal transfer.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/account_asset/#t-querytransferlist.
        :returns: Request results as dictionary.
        """

        suffix="/asset/v1/private/transfer/list"

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def query_subaccount_list(self):
        """
        Create internal transfer.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/account_asset/#t-querysubaccountlist.
        :returns: Request results as dictionary.
        """

        suffix="/asset/v1/private/sub-member/member-ids"

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query={},
            auth=True
        )

    def query_subaccount_transfer_list(self,**kwargs):
        """
        Create internal transfer.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/account_asset/#t-querysubaccounttransferlist.
        :returns: Request results as dictionary.
        """

        suffix="/asset/v1/private/sub-member/transfer/list"

        return self._submit_request(
            method='GET',
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )
    '''
    Internal methods; signature and request submission.
    For more information about the request signature, see
    https://bybit-exchange.github.io/docs/inverse/#t-authentication.
    '''

    def _auth(self, method, params, recv_window):
        """
        Generates authentication signature per Bybit API specifications.

        Notes
        -------------------
        Since the POST method requires a JSONified dict, we need to ensure
        the signature uses lowercase booleans instead of Python's
        capitalized booleans. This is done in the bug fix below.

        """

        api_key = self.api_key
        api_secret = self.api_secret

        if api_key is None or api_secret is None:
            raise PermissionError('Authenticated endpoints require keys.')

        # Append required parameters.
        params['api_key'] = api_key
        params['recv_window'] = recv_window
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

    def _verify_string(self,params,key):
        if key in params:
            if not isinstance(params[key], str):
                return False
            else:
                return True
        return True

    def _submit_request(self, method=None, path=None, query=None, auth=False):
        """
        Submits the request to the API.

        Notes
        -------------------
        We use the params argument for the GET method, and data argument for
        the POST method. Dicts passed to the data argument must be
        JSONified prior to submitting request.

        """

        if query is None:
            query = {}

        # Remove internal spot arg
        query.pop('spot', '')

        # Store original recv_window.
        recv_window = self.recv_window

        # Bug fix: change floating whole numbers to integers to prevent
        # auth signature errors.
        if query is not None:
            for i in query.keys():
                if isinstance(query[i], float) and query[i] == int(query[i]):
                    query[i] = int(query[i])

        # Send request and return headers with body. Retry if failed.
        retries_attempted = self.max_retries
        req_params = None

        while True:

            retries_attempted -= 1
            if retries_attempted < 0:
                raise FailedRequestError(
                    request=f'{method} {path}: {req_params}',
                    message='Bad Request. Retries exceeded maximum.',
                    status_code=400,
                    time=dt.utcnow().strftime("%H:%M:%S")
                )

            retries_remaining = f'{retries_attempted} retries remain.'

            # Authenticate if we are using a private endpoint.
            if auth:
                # Prepare signature.
                signature = self._auth(
                    method=method,
                    params=query,
                    recv_window=recv_window,
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

            # Log the request.
            if self.log_requests:
                self.logger.debug(f'Request -> {method} {path}: {req_params}')

            # Prepare request; use 'params' for GET and 'data' for POST.
            if method == 'GET':
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                r = self.client.prepare_request(
                    requests.Request(method, path, params=req_params,
                                     headers=headers)
                )
            else:
                if 'spot' in path:
                    full_param_str = '&'.join(
                        [str(k) + '=' + str(v) for k, v in
                         sorted(query.items()) if v is not None]
                    )
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                    r = self.client.prepare_request(
                        requests.Request(method, path + f"?{full_param_str}",
                                         headers=headers)
                    )

                else:
                    r = self.client.prepare_request(
                        requests.Request(method, path,
                                         data=json.dumps(req_params))
                    )

            # Attempt the request.
            try:
                s = self.client.send(r, timeout=self.timeout)

            # If requests fires an error, retry.
            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.SSLError,
                requests.exceptions.ConnectionError
            ) as e:
                if self.force_retry:
                    self.logger.error(f'{e}. {retries_remaining}')
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise e

            # Convert response to dictionary, or raise if requests error.
            try:
                s_json = s.json()

            # If we have trouble converting, handle the error and retry.
            except JSONDecodeError as e:
                if self.force_retry:
                    self.logger.error(f'{e}. {retries_remaining}')
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise FailedRequestError(
                        request=f'{method} {path}: {req_params}',
                        message='Conflict. Could not decode JSON.',
                        status_code=409,
                        time=dt.utcnow().strftime("%H:%M:%S")
                    )

            # If Bybit returns an error, raise.
            if s_json['ret_code']:

                # Generate error message.
                error_msg = (
                    f'{s_json["ret_msg"]} (ErrCode: {s_json["ret_code"]})'
                )

                # Set default retry delay.
                err_delay = self.retry_delay

                # Retry non-fatal whitelisted error requests.
                if s_json['ret_code'] in self.retry_codes:

                    # 10002, recv_window error; add 2.5 seconds and retry.
                    if s_json['ret_code'] == 10002:
                        error_msg += '. Added 2.5 seconds to recv_window'
                        recv_window += 2500

                    # 10006, ratelimit error; wait until rate_limit_reset_ms
                    # and retry.
                    elif s_json['ret_code'] == 10006:
                        self.logger.error(
                            f'{error_msg}. Ratelimited on current request. '
                            f'Sleeping, then trying again. Request: {path}'
                        )

                        # Calculate how long we need to wait.
                        limit_reset = s_json['rate_limit_reset_ms'] / 1000
                        reset_str = time.strftime(
                            '%X', time.localtime(limit_reset)
                        )
                        err_delay = int(limit_reset) - int(time.time())
                        error_msg = (
                            f'Ratelimit will reset at {reset_str}. '
                            f'Sleeping for {err_delay} seconds'
                        )

                    # Log the error.
                    self.logger.error(f'{error_msg}. {retries_remaining}')
                    time.sleep(err_delay)
                    continue

                elif s_json['ret_code'] in self.ignore_codes:
                    pass

                else:
                    raise InvalidRequestError(
                        request=f'{method} {path}: {req_params}',
                        message=s_json["ret_msg"],
                        status_code=s_json["ret_code"],
                        time=dt.utcnow().strftime("%H:%M:%S")
                    )
            else:
                return s_json


class WebSocket:
    """
    Connector for Bybit's WebSocket API.
    """

    def __init__(self, endpoint, api_key=None, api_secret=None,
                 subscriptions=None, logging_level=logging.INFO,
                 max_data_length=200, ping_interval=30, ping_timeout=10,
                 restart_on_error=True, purge_on_fetch=True,
                 trim_data=True):
        """
        Initializes the websocket session.

        :param endpoint: Required parameter. The endpoint of the remote
            websocket.
        :param api_key: Your API key. Required for authenticated endpoints.
            Defaults to None.
        :param api_secret: Your API secret key. Required for authenticated
            endpoints. Defaults to None.
        :param subscriptions: A list of desired topics to subscribe to. See API
            documentation for more information. Defaults to an empty list, which
            will raise an error.
        :param logging_level: The logging level of the built-in logger. Defaults
            to logging.INFO. Options are CRITICAL (50), ERROR (40),
            WARNING (30), INFO (20), DEBUG (10), or NOTSET (0).
        :param max_data_length: The maximum number of rows for the stored
            dataset. A smaller number will prevent performance or memory issues.
        :param ping_interval: The number of seconds between each automated ping.
        :param ping_timeout: The number of seconds to wait for 'pong' before an
            Exception is raised.
        :param restart_on_error: Whether or not the connection should restart on
            error.
        :param purge_on_fetch: Whether or not stored data should be purged each
            fetch. For example, if the user subscribes to the 'trade' topic, and
            fetches, should the data show all trade history up to the maximum
            length or only get the data since the last fetch?
        :param trim_data: Decide whether the returning data should be
            trimmed to only provide the data value.

        :returns: WebSocket session.
        """

        self.spot = True if "spot" in endpoint else False
        self.spot_unauth = True if [True for v in ['v1', 'v2'] if v in
                                    endpoint] else False
        self.spot_auth = True if "spot" in endpoint and not \
            self.spot_unauth else False
        if not self.spot_auth:
            if not subscriptions:
                raise Exception('Subscription list cannot be empty!')
        if not self.spot:
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

        # Check if subscriptions are in the correct format
        if self.spot and not self.spot_auth:
            for subscription in subscriptions.copy():
                if isinstance(subscription, str):
                    try:
                        subscriptions.pop(subscriptions.index(subscription))
                        subscriptions.append(json.loads(subscription))
                    except JSONDecodeError:
                        raise Exception('Spot subscriptions should be dicts, '
                                        'or strings that are valid JSONs.')
        elif not self.spot:
            for subscription in subscriptions:
                if not isinstance(subscription, str):
                    raise Exception('Futures subscriptions should be strings.')

            for subscription in subscriptions:
                if ('v2' in endpoint and 'symbol' in subscription) or \
                   ('v1' in endpoint and 'symbol' in subscription['params']):
                    raise Exception('Cannot subscribe to v1 topics with v2 '
                                    'endpoint, or vice versa.')

        # set websocket name for logging purposes
        self.wsName = 'Authenticated' if api_key else 'Non-Authenticated'

        # Setup logger.
        self.logger = logging.getLogger(__name__)

        if len(logging.root.handlers) == 0:
            # no handler on root logger set -> we add handler just for this logger to not mess with custom logic from outside
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                                   datefmt='%Y-%m-%d %H:%M:%S'
                                                   )
                                 )
            handler.setLevel(logging_level)
            self.logger.addHandler(handler)

        self.logger.debug(f'Initializing {self.wsName} WebSocket.')

        # Ensure authentication for private topics.
        if not self.spot and any(i in subscriptions for i in [
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
        # Checking if using auth spot connection.
        if '/spot/ws' in self.endpoint:
            self.subscriptions = ['outboundAccountInfo', 'executionReport',
                                  'ticketInfo']
        self.max_length = max_data_length

        # Set ping settings.
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

        # Other optional data handling settings.
        self.handle_error = restart_on_error
        self.purge = purge_on_fetch
        self.trim = trim_data

        # Set initial state, initialize dictionary and connect.
        self._reset()
        self._connect(self.endpoint)

    def fetch(self, topic):
        """
        Fetches data from the subscribed topic.

        :param topic: Required parameter. The subscribed topic to poll.
        :returns: Filtered data as dict.
        """

        if self.spot and self.spot_unauth:
            topic = self.conform_topic(topic)
        # If the topic given isn't in the initial subscribed list.
        if topic not in self.subscriptions:
            self.logger.error(f'You aren\'t subscribed to the {topic} topic.')
            return

        # Pop all trade or execution data on each poll.
        # don't pop order or stop_order data as we will lose valuable state
        if any(i in topic for i in ['trade', 'execution']) \
                and not topic.startswith('orderBook') and \
                "executionReport" not in topic:
            data = self.data[topic].copy()
            if self.purge:
                self.data[topic] = []
            return data
        else:
            try:
                return self.data[topic]
            except KeyError:
                return []

    def ping(self):
        """
        Pings the remote server to test the connection. The status of the
        connection can be monitored using ws.ping().
        """

        self.ws.send(json.dumps({'op': 'ping'}))

    def exit(self):
        """
        Closes the websocket connection.
        """

        self.ws.close()
        while self.ws.sock:
            continue
        self.exited = True

    def _auth(self):
        """
        Authorize websocket connection.
        """

        # Generate expires.
        expires = int((time.time() + 1) * 1000)

        # Generate signature.
        _val = f'GET/realtime{expires}'
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
        """
        Open websocket in a thread.
        """

        self.ws = websocket.WebSocketApp(
            url=url,
            on_message=lambda ws, msg: self._on_message(msg),
            on_close=self._on_close(),
            on_open=self._on_open(),
            on_error=lambda ws, err: self._on_error(err)
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
        if self.api_key and self.api_secret and not self.spot_unauth:
            self._auth()

        # Check if subscriptions is a list.
        if isinstance(self.subscriptions, (str, dict)):
            self.subscriptions = [self.subscriptions]

        # Subscribe to the requested topics.
        if not self.spot_auth and self.spot_unauth:
            for subscription in self.subscriptions:
                if not subscription.get('event'):
                    subscription['event'] = 'sub'
                if not subscription.get('params'):
                    subscription['params'] = {}
                    if 'v2' in self.endpoint:
                        raise Exception('v2 spot websocket topics require the '
                                        '"symbol" key within "params"')
                if not subscription.get('binary') or \
                        subscription['params'].get('binary'):
                    subscription['params']['binary'] = False
                self.ws.send(json.dumps(subscription))
        elif not self.spot:
            self.ws.send(
                json.dumps({
                    'op': 'subscribe',
                    'args': self.subscriptions
                })
            )

        # Initialize the topics.
        if not self.spot_auth and self.spot:
            # Strip the subscription dict
            for subscription in self.subscriptions:
                index = self.subscriptions.index(subscription)
                subscription = subscription if isinstance(subscription, dict) \
                    else json.loads(subscription)
                subscription.pop('event')
                subscription['params']['binary'] = str(subscription['params'][
                    'binary']).lower()
                if subscription['params'].get('dumpScale'):
                    subscription['params']['dumpScale'] = str(subscription[
                        'params']['dumpScale'])
                self.subscriptions[index] = \
                    self.conform_topic(subscription)

        topics = self.subscriptions
        for topic in topics:
            if topic not in self.data:
                self.data[topic] = {}

    @staticmethod
    def _find_index(source, target, key):
        """
        Find the index in source list of the targeted ID.
        """
        return next(i for i, j in enumerate(source) if j[key] == target[key])

    def _on_message(self, message):
        """
        Parse incoming messages. Similar structure to the
        official WS connector.
        """

        # Load dict of message.
        msg_json = json.loads(message)

        # Did we receive a message regarding auth or subscription?
        auth_message = True if isinstance(msg_json, dict) and \
            (msg_json.get('auth') or
             msg_json.get('request', {}).get('op') == 'auth') else False
        subscription_message = True if isinstance(msg_json, dict) and \
            ((msg_json.get('event') == 'sub' or msg_json.get('code')) or
             msg_json.get('request', {}).get('op') == 'subscribe') else False

        # Check auth
        if auth_message:
            # If we get successful futures/spot auth, notify user.
            if msg_json.get('success') is True or \
                    msg_json.get('auth') == 'success':
                self.logger.debug('Authorization successful.')
                self.auth = True
            # If we get unsuccessful auth, notify user.
            elif msg_json.get('auth') == 'fail' or \
                    msg_json.get('success') is False:
                self.logger.debug('Authorization failed. Please check your '
                                  'API keys and restart.')

        # Check subscription
        if subscription_message:
            # If we get successful futures/spot subscription, notify user.
            if msg_json.get('success') is True or \
                    msg_json.get('msg') == 'Success':
                sub = msg_json['topic'] if self.spot else msg_json[
                    'request']['args']
                self.logger.debug(f'Subscription to {sub} successful.')
            # Futures subscription fail
            elif msg_json.get('success') is False:
                response = msg_json['ret_msg']
                if 'unknown topic' in response:
                    self.logger.error('Couldn\'t subscribe to topic.'
                                      f' Error: {response}.')
            # Spot subscription fail
            elif msg_json.get('code'):
                self.logger.error('Couldn\'t subscribe to topic.'
                                  f' Error code: {msg_json["code"]}.'
                                  f' Error message: {msg_json.get("desc")}.')

        elif 'topic' in msg_json:

            if self.spot:
                # Conform received topic data so that we can match with our
                # subscribed topic
                topic = self.conform_topic(msg_json.copy())
            else:
                topic = msg_json['topic']

            # If incoming 'orderbookL2' data.
            if 'orderBook' in topic:

                # Make updates according to delta response.
                if 'delta' in msg_json['type']:

                    # Delete.
                    for entry in msg_json['data']['delete']:
                        index = self._find_index(self.data[topic], entry, 'id')
                        self.data[topic].pop(index)

                    # Update.
                    for entry in msg_json['data']['update']:
                        index = self._find_index(self.data[topic], entry, 'id')
                        self.data[topic][index] = entry

                    # Insert.
                    for entry in msg_json['data']['insert']:
                        self.data[topic].append(entry)

                # Record the initial snapshot.
                elif 'snapshot' in msg_json['type']:
                    if 'order_book' in msg_json['data']:
                        self.data[topic] = msg_json['data']['order_book'] if self.trim else msg_json
                    else:
                        self.data[topic] = msg_json['data'] if self.trim else msg_json
                    #self.data[topic] = msg_json['data']

            # If incoming 'diffDepth' data.
            elif 'diffDepth' in topic:

                book_sides = {'b': msg_json['data'][0]['b'],
                              'a': msg_json['data'][0]['a']}

                if not self.data[topic]:
                    self.data[topic] = book_sides
                    return

                for side, entries in book_sides.items():
                    for entry in entries:

                        # Delete.
                        if float(entry[1]) == 0:
                            index = self._find_index(
                                self.data[topic][side], entry, 0)
                            self.data[topic][side].pop(index)
                            continue

                        # Insert.
                        price_level_exists = entry[0] in \
                            [level[0] for level in self.data[topic][side]]
                        if not price_level_exists:
                            self.data[topic][side].append(entry)
                            continue

                        # Update.
                        qty_changed = entry[1] != next(
                            level[1] for level in self.data[topic][side] if
                            level[0] == entry[0])
                        if price_level_exists and qty_changed:
                            index = self._find_index(
                                self.data[topic][side], entry, 0)
                            self.data[topic][side][index] = entry
                            continue

            # For incoming 'order' and 'stop_order' data.
            elif any(i in topic for i in ['order', 'stop_order']):

                # record incoming data
                for i in msg_json['data']:
                    try:
                        # update existing entries
                        # temporary workaround for field anomaly in stop_order data
                        ord_id = topic + '_id' if i['symbol'].endswith('USDT') else 'order_id'
                        index = self._find_index(self.data[topic], i, ord_id)
                        self.data[topic][index] = i
                    except StopIteration:
                        # Keep appending or create new list if not already created.
                        try:
                            self.data[topic].append(i)
                        except AttributeError:
                            self.data[topic] = msg_json['data']

            # For incoming 'trade' and 'execution' data.
            elif any(i in topic for i in ['trade', 'execution']):

                # Keep appending or create new list if not already created.
                try:
                    trades = [msg_json['data']] if isinstance(
                        msg_json['data'], dict) else msg_json['data']
                    for i in trades:
                        self.data[topic].append(i)
                except AttributeError:
                    self.data[topic] = msg_json['data']

                # If list is too long, pop the first entry.
                if len(self.data[topic]) > self.max_length:
                    self.data[topic].pop(0)

            # If incoming data is in a topic which only pushes messages in
            # the snapshot format
            elif any(i in topic for i in ['insurance', 'kline', 'wallet',
                                          'candle', 'realtimes', '"depth"',
                                          '"mergedDepth"', 'bookTicker']):

                # Record incoming data.
                if 'v2' in self.endpoint:
                    self.data[topic] = msg_json['data'] if self.trim else msg_json
                else:
                    self.data[topic] = msg_json['data'][0] if self.trim else msg_json

            # If incoming 'instrument_info' data.
            elif 'instrument_info' in topic:

                # Make updates according to delta response.
                if 'delta' in msg_json['type']:
                    for i in msg_json['data']['update'][0]:
                        self.data[topic][i] = msg_json['data']['update'][0][i]

                # Record the initial snapshot.
                elif 'snapshot' in msg_json['type']:
                    self.data[topic] = msg_json['data'] if self.trim else msg_json

            # If incoming 'position' data.
            elif 'position' in topic:

                # Record incoming position data.
                for p in msg_json['data']:

                    # linear (USDT) positions have Buy|Sell side and
                    # updates contain all USDT positions.
                    # For linear tickers...
                    if p['symbol'].endswith('USDT'):
                        try:
                            self.data[topic][p['symbol']][p['side']] = p
                        # if side key hasn't been created yet...
                        except KeyError:
                            self.data[topic][p['symbol']] = {p['side']: p}

                    # For non-linear tickers...
                    else:
                        self.data[topic][p['symbol']] = p

        elif isinstance(msg_json, list):
            for item in msg_json:
                topic = item.get('e')
                if topic == "outboundAccountInfo":
                    self.data[topic] = item
                elif any(i in topic for i in ['executionReport', 'ticketInfo']):
                    # Keep appending or create new list if not already created.
                    try:
                        self.data[topic].append(item)
                    except AttributeError:
                        self.data[topic] = item
                    self.data[topic] = item

    def _on_error(self, error):
        """
        Exit on errors and raise exception, or attempt reconnect.
        """

        if not self.exited:
            self.logger.error(f'WebSocket {self.wsName} encountered error: {error}.')
            self.exit()

        # Reconnect.
        if self.handle_error:
            self._reset()
            self._connect(self.endpoint)

    def _on_open(self):
        """
        Log WS open.
        """
        self.logger.debug(f'WebSocket {self.wsName} opened.')

    def _on_close(self):
        """
        Log WS close.
        """
        self.logger.debug(f'WebSocket {self.wsName} closed.')

    def _reset(self):
        """
        Set state booleans and initialize dictionary.
        """
        self.exited = False
        self.auth = False
        self.data = {}

    @staticmethod
    def conform_topic(topic):
        """
        For spot API. Due to the fact that the JSON received in update
        messages does not include a simple "topic" key, and parameters all
        have their own separate keys, we need to compare the entire JSON.
        Therefore, we need to strip the JSON of any unnecessary keys,
        cast some values, and dump the JSON with sort_keys.
        """
        if isinstance(topic, str):
            topic = json.loads(topic)
        topic.pop('symbolName', '')
        topic['params'].pop('realtimeInterval', '')
        topic['params'].pop('symbolName', '')
        if topic['params'].get('klineType'):
            topic['topic'] += "_" + topic['params'].get('klineType')
            topic['params'].pop('klineType')
        topic.pop('data', '')
        topic.pop('f', '')
        topic.pop('sendTime', '')
        topic.pop('shared', '')
        return json.dumps(topic, sort_keys=True, separators=(',', ':'))
