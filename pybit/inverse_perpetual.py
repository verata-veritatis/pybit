from .http_manager import InverseFuturesHTTPManager
from .websocket_stream import FuturesWebSocketManager
from .websocket_stream import INVERSE_PERPETUAL


ws_name = INVERSE_PERPETUAL
WSS = "wss://{SUBDOMAIN}.{DOMAIN}.com/realtime"


class HTTP(InverseFuturesHTTPManager):
    def query_mark_price_kline(self, **kwargs):
        """
        Query mark price kline (like query_kline but for mark price).

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-markpricekline.
        :returns: Request results as dictionary.
        """

        # Replace query param "from_time" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_time" in kwargs:
            kwargs["from"] = kwargs.pop("from_time")

        suffix = "/v2/public/mark-price-kline"

        return self._submit_request(
            method="GET",
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

        # Replace query param "from_time" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_time" in kwargs:
            kwargs["from"] = kwargs.pop("from_time")

        suffix = "/v2/public/index-price-kline"

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
            https://bybit-exchange.github.io/docs/inverse/#t-querypremiumindexkline.
        :returns: Request results as dictionary.
        """

        # Replace query param "from_time" since "from" keyword is reserved.
        # Temporary workaround until Bybit updates official request params
        if "from_time" in kwargs:
            kwargs["from"] = kwargs.pop("from_time")

        suffix = "/v2/public/premium-index-kline"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
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

        suffix = "/v2/private/order/create"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_active_order(self, **kwargs):
        """
        Gets an active order. For more information, see
        https://bybit-exchange.github.io/docs/inverse/#t-getactive.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-getactive.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/order/list"

        return self._submit_request(
            method="GET",
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

        suffix = "/v2/private/order/cancel"

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
            https://bybit-exchange.github.io/docs/inverse/#t-cancelallactive.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/order/cancelAll"

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
            https://bybit-exchange.github.io/docs/inverse/#t-replaceactive.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/order/replace"

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
            https://bybit-exchange.github.io/docs/inverse/#t-queryactive.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/order"

        return self._submit_request(
            method="GET",
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

        suffix = "/v2/private/stop-order/create"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_conditional_order(self, **kwargs):
        """
        Gets a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/inverse/#t-getcond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse/#t-getcond.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/stop-order/list"

        return self._submit_request(
            method="GET",
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

        suffix = "/v2/private/stop-order/cancel"

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
            https://bybit-exchange.github.io/docs/inverse/#t-cancelallcond.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/stop-order/cancelAll"

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
            https://bybit-exchange.github.io/docs/inverse/#t-replacecond.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/stop-order/replace"

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
            https://bybit-exchange.github.io/docs/inverse/#t-querycond.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/stop-order"

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
            https://bybit-exchange.github.io/docs/inverse/#t-myposition.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/position/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_leverage(self, **kwargs):
        """
        Change user leverage.
        If you want to switch between cross margin and isolated margin, please
        see cross_isolated_margin_switch.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inerse/#t-setleverage.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/position/leverage/save"

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
            https://bybit-exchange.github.io/docs/inverse/#t-marginswitch.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/position/switch-isolated"

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
            https://bybit-exchange.github.io/docs/inverse/#t-switchmode.
        :returns: Request results as dictionary.
        """
        suffix = "/v2/private/tpsl/switch-mode"

        return self._submit_request(
            method="POST",
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

        suffix = "/v2/private/position/change-position-margin"

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
            https://bybit-exchange.github.io/docs/inverse/#t-tradingstop.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/position/trading-stop"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
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

        suffix = "/v2/private/execution/list"

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
            https://bybit-exchange.github.io/docs/inverse/#t-closedprofitandloss.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/trade/closed-pnl/list"

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
            https://bybit-exchange.github.io/docs/inverse/#t-setrisklimit.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/position/risk-limit"

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
            https://bybit-exchange.github.io/docs/inverse/#t-fundingrate.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/public/funding/prev-funding-rate"

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
            https://bybit-exchange.github.io/docs/inverse/#t-mylastfundingfee.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/funding/prev-funding"

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
            https://bybit-exchange.github.io/docs/inverse/#t-predictedfunding.
        :returns: Request results as dictionary.
        """

        suffix = "/v2/private/funding/predicted-funding"

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


class WebSocket(FuturesWebSocketManager):
    def __init__(self, test, domain="",
                 api_key=None, api_secret=None):
        super().__init__(WSS, ws_name, test=test, domain=domain,
                         api_key=api_key, api_secret=api_secret)

    def orderbook_25_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketorderbook25
        """
        topic = "orderBookL2_25.{}"
        self.subscribe(topic, callback, symbol)

    def orderbook_200_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketorderbook200
        """
        topic = "orderBook_200.100ms.{}"
        self.subscribe(topic, callback, symbol)

    def trade_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websockettrade
        """
        topic = "trade.{}"
        self.subscribe(topic, callback, symbol)

    def insurance_stream(self, callback, symbol):
        """
        symbol should be the base currency. Eg, "BTC" instead of "BTCUSD"
        https://bybit-exchange.github.io/docs/inverse/#t-websocketinsurance
        """
        topic = "insurance.{}"
        self.subscribe(topic, callback, symbol)

    def kline_stream(self, callback, symbol, interval):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketklinev2
        """
        topic = "klineV2.{}.{}"
        topic = topic.format(str(interval), "{}")
        self.subscribe(topic, callback, symbol)

    def instrument_info_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketinstrumentinfo
        """
        topic = "instrument_info.100ms.{}"
        self.subscribe(topic, callback, symbol)

    def liquidation_stream(self, callback, symbol):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketliquidation
        """
        topic = "liquidation.{}"
        self.subscribe(topic, callback, symbol)

    # Private topics
    def position_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketposition
        """
        topic = "position"
        self.subscribe(topic, callback)

    def execution_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketexecution
        """
        topic = "execution"
        self.subscribe(topic, callback)

    def order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketorder
        """
        topic = "order"
        self.subscribe(topic, callback)

    def stop_order_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketstoporder
        """
        topic = "stop_order"
        self.subscribe(topic, callback)

    def wallet_stream(self, callback):
        """
        https://bybit-exchange.github.io/docs/inverse/#t-websocketwallet
        """
        topic = "wallet"
        self.subscribe(topic, callback)
