import time
import hmac
import json
import logging
import requests

from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor

from .exceptions import FailedRequestError, InvalidRequestError
from . import VERSION

# Requests will use simplejson if available.
try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError


class HTTPManager:
    def __init__(self, endpoint=None, api_key=None, api_secret=None,
                 logging_level=logging.INFO, log_requests=False,
                 request_timeout=10, recv_window=5000, force_retry=False,
                 retry_codes=None, ignore_codes=None, max_retries=3,
                 retry_delay=3, referral_id=None):
        """Initializes the HTTP class."""

        # Set the endpoint.
        if endpoint is None:
            self.endpoint = "https://api.bybit.com"
        else:
            self.endpoint = endpoint

        # Setup logger.

        self.logger = logging.getLogger(__name__)

        if len(logging.root.handlers) == 0:
            #no handler on root logger set -> we add handler just for this logger to not mess with custom logic from outside
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                                   datefmt="%Y-%m-%d %H:%M:%S"
                                                   )
                                 )
            handler.setLevel(logging_level)
            self.logger.addHandler(handler)

        self.logger.debug("Initializing HTTP session.")
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
                "User-Agent": "pybit-" + VERSION,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # Add referral ID to header.
        if referral_id:
            self.client.headers.update({"Referer": referral_id})

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
            raise PermissionError("Authenticated endpoints require keys.")

        # Append required parameters.
        params["api_key"] = api_key
        params["recv_window"] = recv_window
        params["timestamp"] = int(time.time() * 10 ** 3)

        # Sort dictionary alphabetically to create querystring.
        _val = "&".join(
            [str(k) + "=" + str(v) for k, v in sorted(params.items()) if
             (k != "sign") and (v is not None)]
        )

        # Bug fix. Replaces all capitalized booleans with lowercase.
        if method == "POST":
            _val = _val.replace("True", "true").replace("False", "false")

        # Return signature.
        return str(hmac.new(
            bytes(api_secret, "utf-8"),
            bytes(_val, "utf-8"), digestmod="sha256"
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
        query.pop("spot", "")

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
                    request=f"{method} {path}: {req_params}",
                    message="Bad Request. Retries exceeded maximum.",
                    status_code=400,
                    time=dt.utcnow().strftime("%H:%M:%S")
                )

            retries_remaining = f"{retries_attempted} retries remain."

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
                query["sign"] = signature

            # Define parameters and log the request.
            if query is not None:
                req_params = {k: v for k, v in query.items() if
                              v is not None}

            else:
                req_params = {}

            # Log the request.
            if self.log_requests:
                self.logger.debug(f"Request -> {method} {path}: {req_params}")

            # Prepare request; use "params" for GET and "data" for POST.
            if method == "GET":
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                r = self.client.prepare_request(
                    requests.Request(method, path, params=req_params,
                                     headers=headers)
                )
            else:
                if "spot" in path:
                    full_param_str = "&".join(
                        [str(k) + "=" + str(v) for k, v in
                         sorted(query.items()) if v is not None]
                    )
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded"
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
                    self.logger.error(f"{e}. {retries_remaining}")
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
                    self.logger.error(f"{e}. {retries_remaining}")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise FailedRequestError(
                        request=f"{method} {path}: {req_params}",
                        message="Conflict. Could not decode JSON.",
                        status_code=409,
                        time=dt.utcnow().strftime("%H:%M:%S")
                    )

            # If Bybit returns an error, raise.
            if s_json["ret_code"]:

                # Generate error message.
                error_msg = (
                    f"{s_json['ret_msg']} (ErrCode: {s_json['ret_code']})"
                )

                # Set default retry delay.
                err_delay = self.retry_delay

                # Retry non-fatal whitelisted error requests.
                if s_json["ret_code"] in self.retry_codes:

                    # 10002, recv_window error; add 2.5 seconds and retry.
                    if s_json["ret_code"] == 10002:
                        error_msg += ". Added 2.5 seconds to recv_window"
                        recv_window += 2500

                    # 10006, ratelimit error; wait until rate_limit_reset_ms
                    # and retry.
                    elif s_json["ret_code"] == 10006:
                        self.logger.error(
                            f"{error_msg}. Ratelimited on current request. "
                            f"Sleeping, then trying again. Request: {path}"
                        )

                        # Calculate how long we need to wait.
                        limit_reset = s_json["rate_limit_reset_ms"] / 1000
                        reset_str = time.strftime(
                            "%X", time.localtime(limit_reset)
                        )
                        err_delay = int(limit_reset) - int(time.time())
                        error_msg = (
                            f"Ratelimit will reset at {reset_str}. "
                            f"Sleeping for {err_delay} seconds"
                        )

                    # Log the error.
                    self.logger.error(f"{error_msg}. {retries_remaining}")
                    time.sleep(err_delay)
                    continue

                elif s_json["ret_code"] in self.ignore_codes:
                    pass

                else:
                    raise InvalidRequestError(
                        request=f"{method} {path}: {req_params}",
                        message=s_json["ret_msg"],
                        status_code=s_json["ret_code"],
                        time=dt.utcnow().strftime("%H:%M:%S")
                    )
            else:
                return s_json


class FuturesHTTPManager(HTTPManager):
    def orderbook(self, **kwargs):
        """
        Get the orderbook.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-orderbook.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/public/orderBook/L2"
        return self._submit_request(
            method="GET",
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

        suffix = "/v2/public/tickers"
        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_symbol(self):
        """
        Get symbol info.

        :returns: Request results as dictionary.
        """

        suffix = "/v2/public/symbols"
        return self._submit_request(
            method="GET",
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

        # Replace query param "from_id" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_id" in kwargs:
            kwargs["from"] = kwargs.pop("from_id")

        return self._submit_request(
            method="GET",
            path=self.endpoint + "/v2/public/liq-records",
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
            method="GET",
            path=self.endpoint + "/v2/public/open-interest",
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
            method="GET",
            path=self.endpoint + "/v2/public/big-deal",
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
            method="GET",
            path=self.endpoint + "/v2/public/account-ratio",
            query=kwargs
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

    def api_key_info(self):
        """
        Get user's API key info.

        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method="GET",
            path=self.endpoint + "/v2/private/account/api-key",
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
            method="GET",
            path=self.endpoint + "/v2/private/account/lcp",
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

        suffix = "/v2/private/wallet/balance"

        return self._submit_request(
            method="GET",
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

        # Replace query param "from_id" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_id" in kwargs:
            kwargs["from"] = kwargs.pop("from_id")

        return self._submit_request(
            method="GET",
            path=self.endpoint + "/v2/private/wallet/fund/records",
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
            method="GET",
            path=self.endpoint + "/v2/private/wallet/withdraw/list",
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
            method="GET",
            path=self.endpoint + "/v2/private/exchange-order/list",
            query=kwargs,
            auth=True
        )

    def server_time(self):
        """
        Get Bybit server time.

        :returns: Request results as dictionary.
        """

        suffix = "/v2/public/time"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix
        )

    def announcement(self):
        """
        Get Bybit OpenAPI announcements in the last 30 days by reverse order.

        :returns: Request results as dictionary.
        """

        return self._submit_request(
            method="GET",
            path=self.endpoint + "/v2/public/announcement"
        )


class InverseFuturesHTTPManager(FuturesHTTPManager):
    def query_kline(self, **kwargs):
        """
        Get kline.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-querykline.
        :returns: Request results as dictionary.
        """

        # Replace query param "from_time" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_time" in kwargs:
            kwargs["from"] = kwargs.pop("from_time")

        suffix = "/v2/public/kline/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
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

        # Replace query param "from_id" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_id" in kwargs:
            kwargs["from"] = kwargs.pop("from_id")

        suffix = "/v2/public/trading-records"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def get_risk_limit(self, **kwargs):
        """
        Get risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-getrisklimit.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/public/risk-limit/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

