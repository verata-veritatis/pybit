"""
Inverse Futures uses the exact same WebSocket as Inverse Perpetual. Refer to
inverse_perpetual.py to access the Inverse Futures through WebSocket.
"""

from .http_manager import InverseFuturesHTTPManager


class HTTP(InverseFuturesHTTPManager):
    def place_active_order(self, **kwargs):
        """
        Places an active order. For more information, see
        https://bybit-exchange.github.io/docs/inverse_futures/#t-activeorders.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-activeorders.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/order/create"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_active_order(self, **kwargs):
        """
        Gets an active order. For more information, see
        https://bybit-exchange.github.io/docs/inverse_futures/#t-getactive.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-getactive.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/order/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_active_order(self, **kwargs):
        """
        Cancels an active order. For more information, see
        https://bybit-exchange.github.io/docs/inverse_futures/#t-cancelactive.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-cancelactive.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/order/cancel"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-cancelallactive.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/order/cancelAll"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-replaceactive.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/order/replace"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-queryactive.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/order"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def place_conditional_order(self, **kwargs):
        """
        Places a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/inverse_futures/#t-placecond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-placecond.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/stop-order/create"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def get_conditional_order(self, **kwargs):
        """
        Gets a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/inverse_futures/#t-getcond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-getcond.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/stop-order/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def cancel_conditional_order(self, **kwargs):
        """
        Cancels a conditional order. For more information, see
        https://bybit-exchange.github.io/docs/inverse_futures/#t-cancelcond.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-cancelcond.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/stop-order/cancel"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-cancelallcond.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/stop-order/cancelAll"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-replacecond.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/stop-order/replace"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-querycond.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/stop-order"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-myposition.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/position/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def change_margin(self, **kwargs):
        """
        Update margin.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-changemargin.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/position/change-position-margin"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-tradingstop.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/position/trading-stop"

        return self._submit_request(
            method="POST",
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

        suffix = "/futures/private/position/leverage/save"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-usertraderecords.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/execution/list"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-closedprofitandloss.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/trade/closed-pnl/list"

        return self._submit_request(
            method="GET",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def full_partial_position_tp_sl_switch(self, **kwargs):
        """
        Switch mode between Full or Partial

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-switchmode.
        :returns: Request results as dictionary.
        """
        suffix = "/futures/private/tpsl/switch-mode"

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
            https://bybit-exchange.github.io/docs/inverse_futures/#t-marginswitch.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/position/switch-isolated"

        return self._submit_request(
            method="POST",
            path=self.endpoint + suffix,
            query=kwargs,
            auth=True
        )

    def set_risk_limit(self, **kwargs):
        """
        Set risk limit.

        :param kwargs: See
            https://bybit-exchange.github.io/docs/inverse_futures/#t-setrisklimit.
        :returns: Request results as dictionary.
        """

        suffix = "/futures/private/position/risk-limit"

        return self._submit_request(
            method="POST",
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
