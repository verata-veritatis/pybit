from .http_manager import FuturesHTTPManager
from .websocket_stream import FuturesWebSocketManager
from .websocket_stream import USDT_PERPETUAL
from .websocket_stream import _identify_ws_method


ws_name = USDT_PERPETUAL
PUBLIC_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime_public"
PRIVATE_WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime_private"


class HTTP(FuturesHTTPManager):
    def query_kline(self, **kwargs):
        """
        Get kline.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-querykline.
        :returns: Request results as dictionary.
        """

        # Replace query param "from_time" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_time" in kwargs:
            kwargs["from"] = kwargs.pop("from_time")

        suffix = "/public/linear/kline"

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
            https://bybit-exchange.github.io/docs/linear/#t-publictradingrecords.
        :returns: Request results as dictionary.
        """

        # Replace query param "from_id" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_id" in kwargs:
            kwargs["from"] = kwargs.pop("from_id")

        suffix = "/public/linear/recent-trading-records"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_mark_price_kline(self, **kwargs):
        """
        Query mark price kline (like query_kline but for mark price).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-markpricekline.
        :returns: Request results as dictionary.
        """

        # Replace query param "from_time" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_time" in kwargs:
            kwargs["from"] = kwargs.pop("from_time")

        suffix = "/public/linear/mark-price-kline"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_index_price_kline(self, **kwargs):
        """
        Query index price kline (like query_kline but for index price).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-queryindexpricekline.
        :returns: Request results as dictionary.
        """

        # Replace query param "from_time" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_time" in kwargs:
            kwargs["from"] = kwargs.pop("from_time")

        suffix = "/public/linear/index-price-kline"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def query_premium_index_kline(self, **kwargs):
        """
        Query premium index kline (like query_kline but for the premium index
        discount).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-querypremiumindexkline.
        :returns: Request results as dictionary.
        """

        # Replace query param "from_time" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_time" in kwargs:
            kwargs["from"] = kwargs.pop("from_time")

        suffix = "/public/linear/premium-index-kline"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs
        )

    def place_active_order(self, **kwargs):
        """
        Places an active order. For more information, see
        https://bybit-exchange.github.io/docs/linear/#t-activeorders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-activeorders.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/order/create"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_active_order(self, **kwargs):
        """
        Gets an active order. For more information, see
        https://bybit-exchange.github.io/docs/linear/#t-getactive.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-getactive.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/order/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_active_order(self, **kwargs):
        """
        Cancels an active order. For more information, see
        https://bybit-exchange.github.io/docs/linear/#t-cancelactive.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-cancelactive.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/order/cancel"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_all_active_orders(self, **kwargs):
        """
        Cancel all active orders that are unfilled or partially filled. Fully
        filled orders cannot be cancelled.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-cancelallactive.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/order/cancel-all"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def replace_active_order(self, **kwargs):
        """
        Replace order can modify/amend your active orders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-replaceactive.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/order/replace"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def query_active_order(self, **kwargs):
        """
        Query real-time active order information.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-queryactive.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/order/search"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def place_conditional_order(self, **kwargs):
        """
        Places a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/linear/#t-placecond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-placecond.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/stop-order/create"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_conditional_order(self, **kwargs):
        """
        Gets a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/linear/#t-getcond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-getcond.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/stop-order/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_conditional_order(self, **kwargs):
        """
        Cancels a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/linear/#t-cancelcond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-cancelcond.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/stop-order/cancel"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_all_conditional_orders(self, **kwargs):
        """
        Cancel all conditional orders that are unfilled or partially filled.
        Fully filled orders cannot be cancelled.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-cancelallcond.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/stop-order/cancel-all"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def replace_conditional_order(self, **kwargs):
        """
        Replace conditional order can modify/amend your conditional orders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-replacecond.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/stop-order/replace"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def query_conditional_order(self, **kwargs):
        """
        Query real-time conditional order information.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-querycond.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/stop-order/search"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def my_position(self, **kwargs):
        """
        Get my position list.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-myposition.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/position/list"

        return self._submit_request(
            method="GET",
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
            method="POST",
            path=self.endpoint + "/private/linear/position/set-auto-add-margin",
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

        suffix = "/private/linear/position/set-leverage"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cross_isolated_margin_switch(self, **kwargs):
        """
        Switch Cross/Isolated; must be leverage value when switching from Cross
        to Isolated.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-marginswitch.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/position/switch-isolated"

        return self._submit_request(
            method="POST",
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
            https://bybit-exchange.github.io/docs/linear/#t-switchpositionmode.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/position/switch-mode"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def full_partial_position_tp_sl_switch(self, **kwargs):
        """
        Switch mode between Full or Partial

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-switchmode.
        :returns: Request results as dictionary.
        """
        suffix = "/private/linear/tpsl/switch-mode"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_trading_stop(self, **kwargs):
        """
        Set take profit, stop loss, and trailing stop for your open position.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-tradingstop.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/position/trading-stop"

        return self._submit_request(
            method="POST",
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
            method="GET",
            path=self.endpoint + "/private/linear/position/add-margin",
            query=kwargs,
            auth=True
        )

    def user_trade_records(self, **kwargs):
        """
        Get user's trading records. The results are ordered in ascending order
        (the first item is the oldest).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-usertraderecords.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/trade/execution/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def closed_profit_and_loss(self, **kwargs):
        """
        Get user's closed profit and loss records. The results are ordered in
        descending order (the first item is the latest).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-closedprofitandloss.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/trade/closed-pnl/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_risk_limit(self, **kwargs):
        """
        Get risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-getrisklimit.
        :returns: Request results as dictionary.
        """

        suffix = "/public/linear/risk-limit"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_risk_limit(self, **kwargs):
        """
        Set risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-setrisklimit.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/position/set-risk"

        return self._submit_request(
            method="POST",
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
            https://bybit-exchange.github.io/docs/linear/#t-fundingrate.
        :returns: Request results as dictionary.
        """

        suffix = "/public/linear/funding/prev-funding-rate"

        return self._submit_request(
            method="GET",
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
            https://bybit-exchange.github.io/docs/linear/#t-mylastfundingfee.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/funding/prev-funding"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def predicted_funding_rate(self, **kwargs):
        """
        Get predicted funding rate and my funding fee.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/linear/#t-predictedfunding.
        :returns: Request results as dictionary.
        """

        suffix = "/private/linear/funding/predicted-funding"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
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
            e.g. "BTCUSD".

        """

        # First we fetch the user's position.
        try:
            r = self.my_position(symbol=symbol)["result"]

        # If there is no returned position, we want to handle that.
        except KeyError:
            return self.logger.error("No position detected.")

        # Next we generate a list of market orders
        orders = [
            {
                "symbol": symbol,
                "order_type": "Market",
                "side": "Buy" if p["side"] == "Sell" else "Sell",
                "qty": p["size"],
                "time_in_force": "ImmediateOrCancel",
                "reduce_only": True,
                "close_on_trigger": True
            } for p in (r if isinstance(r, list) else [r]) if p["size"] > 0
        ]

        if len(orders) == 0:
            return self.logger.error("No position detected.")

        # Submit a market order against each open position for the same qty.
        return self.place_active_order_bulk(orders)


class WebSocket:
    def __init__(self, test, domain="",
                 api_key=False, api_secret=False):
        self.ws_public = None
        self.ws_private = None

        self.test = test
        self.domain = domain
        self.api_key = api_key
        self.api_secret = api_secret

    def _ws_public_subscribe(self, topic, callback, symbol):
        if not self.ws_public:
            self.ws_public = FuturesWebSocketManager(
                PUBLIC_WSS, ws_name, self.test, domain=self.domain
            )
        self.ws_public.subscribe(topic, callback, symbol)

    def _ws_private_subscribe(self, topic, callback):
        if not self.ws_private:
            self.ws_private = FuturesWebSocketManager(
                PRIVATE_WSS, ws_name, self.test, domain=self.domain,
                api_key=self.api_key, api_secret=self.api_secret
            )
        self.ws_private.subscribe(topic, callback)

    def custom_topic_stream(self, wss_url, topic, callback):
        subscribe = _identify_ws_method(
            wss_url,
            {
                PUBLIC_WSS: self._ws_public_subscribe,
                PRIVATE_WSS: self._ws_private_subscribe
            })
        symbol = FuturesWebSocketManager._extract_symbol(topic)
        if symbol:
            subscribe(topic, callback, symbol)
        else:
            subscribe(topic, callback)

    def orderbook_25_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketorderbook25
        """
        topic = "orderBookL2_25.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def orderbook_200_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketorderbook200
        """
        topic = "orderBook_200.100ms.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def trade_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websockettrade
        """
        topic = "trade.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def instrument_info_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketinstrumentinfo
        """
        topic = "instrument_info.100ms.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    def kline_stream(self, callback, symbol, interval):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketkline
        """
        topic = "candle.{}.{}"
        topic = topic.format(str(interval), "{}")
        self._ws_public_subscribe(topic, callback, symbol)

    def liquidation_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketliquidation
        """
        topic = "liquidation.{}"
        self._ws_public_subscribe(topic, callback, symbol)

    # Private topics
    def position_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketposition
        """
        topic = "position"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def execution_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketexecution
        """
        topic = "execution"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketorder
        """
        topic = "order"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def stop_order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketstoporder
        """
        topic = "stop_order"
        self._ws_private_subscribe(topic=topic, callback=callback)

    def wallet_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/linear/#t-websocketwallet
        """
        topic = "wallet"
        self._ws_private_subscribe(topic=topic, callback=callback)
