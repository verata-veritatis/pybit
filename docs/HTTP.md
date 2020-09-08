# HTTP Module
Available methods for the HTTP module of `pybit`.

## Public Endpoints

```python
def orderbook(self, **kwargs):
    """
    Get the orderbook.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-orderbook.
    :returns: Request results as dictionary.
    """

def query_kline(self, **kwargs):
    """
    Get kline.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-querykline.
    :returns: Request results as dictionary.
    """

def latest_information_for_symbol(self, **kwargs):
    """
    Get the latest information for symbol.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-latestsymbolinfo.
    :returns: Request results as dictionary.
    """

def public_trading_records(self, **kwargs):
    """
    Get recent trades. You can find a complete history of trades on Bybit
    at https://public.bybit.com/.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-latestsymbolinfo.
    :returns: Request results as dictionary.
    """

def query_symbol(self):
    """
    Get symbol info.

    :returns: Request results as dictionary.
    """

def liquidated_orders(self, **kwargs):
    """
    Retrieve the liquidated orders. The query range is the last seven days
    of data.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-query_liqrecords.
    :returns: Request results as dictionary.
    """

def query_mark_price_kline(self, **kwargs):
    """
    Query mark price kline (like query_kline but for mark price).

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-markpricekline.
    :returns: Request results as dictionary.
    """

def open_interest(self, **kwargs):
    """
    Gets the total amount of unsettled contracts. In other words, the total
    number of contracts held in open positions.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-marketopeninterest.
    :returns: Request results as dictionary.
    """

def latest_big_deal(self, **kwargs):
    """
    Obtain filled orders worth more than 500,000 USD within the last 24h.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-marketbigdeal.
    :returns: Request results as dictionary.
    """

def long_short_ratio(self, **kwargs):
    """
    Gets the Bybit long-short ratio.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-marketaccountratio.
    :returns: Request results as dictionary.
    """

def place_active_order(self, **kwargs):
    """
    Places an active order. For more information, see
    https://bybit-exchange.github.io/docs/inverse/#t-activeorders.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-activeorders.
    :returns: Request results as dictionary.
    """

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

def get_active_order(self, **kwargs):
    """
    Gets an active order. For more information, see
    https://bybit-exchange.github.io/docs/inverse/#t-getactive.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-getactive.
    :returns: Request results as dictionary.
    """

def cancel_active_order(self, **kwargs):
    """
    Cancels an active order. For more information, see
    https://bybit-exchange.github.io/docs/inverse/#t-cancelactive.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-cancelactive.
    :returns: Request results as dictionary.
    """

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

def cancel_all_active_orders(self, **kwargs):
    """
    Cancel all active orders that are unfilled or partially filled. Fully
    filled orders cannot be cancelled.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-cancelallactive.
    :returns: Request results as dictionary.
    """

def replace_active_order(self, **kwargs):
    """
    Replace order can modify/amend your active orders.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-replaceactive.
    :returns: Request results as dictionary.
    """

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

def query_active_order(self, **kwargs):
    """
    Query real-time active order information.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-queryactive.
    :returns: Request results as dictionary.
    """

def place_conditional_order(self, **kwargs):
    """
    Places a conditional order. For more information, see
    https://bybit-exchange.github.io/docs/inverse/#t-placecond.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-placecond.
    :returns: Request results as dictionary.
    """

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

def get_conditional_order(self, **kwargs):
    """
    Gets a conditional order. For more information, see
    https://bybit-exchange.github.io/docs/inverse/#t-getcond.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-getcond.
    :returns: Request results as dictionary.
    """

def cancel_conditional_order(self, **kwargs):
    """
    Cancels a conditional order. For more information, see
    https://bybit-exchange.github.io/docs/inverse/#t-cancelcond.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-cancelcond.
    :returns: Request results as dictionary.
    """

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



def cancel_all_conditional_orders(self, **kwargs):
    """
    Cancel all conditional orders that are unfilled or partially filled.
    Fully filled orders cannot be cancelled.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-cancelallcond.
    :returns: Request results as dictionary.
    """

def replace_conditional_order(self, **kwargs):
    """
    Replace conditional order can modify/amend your conditional orders.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-replacecond.
    :returns: Request results as dictionary.
    """

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

def query_conditional_order(self, **kwargs):
    """
    Query real-time conditional order information.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-querycond.
    :returns: Request results as dictionary.
    """

def my_position(self, **kwargs):
    """
    Get my position list.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-myposition.
    :returns: Request results as dictionary.
    """

def set_auto_add_margin(self, **kwargs):
    """
    For linear markets only. Set auto add margin, or Auto-Margin
    Replenishment.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/linear/#t-setautoaddmargin.
    :returns: Request results as dictionary.
    """

def set_leverage(self, **kwargs):
    """
    For linear markets only. Change user leverage.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/linear/#t-setleverage.
    :returns: Request results as dictionary.
    """

def cross_isolated_margin_switch(self, **kwargs):
    """
    For linear markets only. Switch Cross/Isolated; must be leverage value
    when switching from Cross to Isolated.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/linear/#t-marginswitch.
    :returns: Request results as dictionary.
    """


def change_margin(self, **kwargs):
    """
    Update margin.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-changemargin.
    :returns: Request results as dictionary.
    """

def set_trading_stop(self, **kwargs):
    """
    Set take profit, stop loss, and trailing stop for your open position.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-tradingstop.
    :returns: Request results as dictionary.
    """

def add_reduce_margin(self, **kwargs):
    """
    For linear markets only. Add margin.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/linear/#t-addmargin.
    :returns: Request results as dictionary.
    """

def user_leverage(self, **kwargs):
    """
    Get user leverage.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-getleverage.
    :returns: Request results as dictionary.
    """

def change_user_leverage(self, **kwargs):
    """
    Change user leverage.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-changeleverage.
    :returns: Request results as dictionary.
    """

def user_trade_records(self, **kwargs):
    """
    Get user's trading records. The results are ordered in ascending order
    (the first item is the oldest).

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-usertraderecords.
    :returns: Request results as dictionary.
    """

def closed_profit_and_loss(self, **kwargs):
    """
    Get user's closed profit and loss records. The results are ordered in
    descending order (the first item is the latest).

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-closedprofitandloss.
    :returns: Request results as dictionary.
    """

def get_risk_limit(self, is_linear=False):
    """
    Get risk limit.

    :param is_linear: True for linear, False for inverse. Defaults to
        False.
    :returns: Request results as dictionary.
    """

def set_risk_limit(self, **kwargs):
    """
    Set risk limit.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-setrisklimit.
    :returns: Request results as dictionary.
    """

def get_the_last_funding_rate(self, **kwargs):
    """
    The funding rate is generated every 8 hours at 00:00 UTC, 08:00 UTC and
    16:00 UTC. For example, if a request is sent at 12:00 UTC, the funding
    rate generated earlier that day at 08:00 UTC will be sent.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-fundingrate.
    :returns: Request results as dictionary.
    """

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

def predicted_funding_rate(self, **kwargs):
    """
    Get predicted funding rate and my funding fee.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-predictedfunding.
    :returns: Request results as dictionary.
    """

def api_key_info(self):
    """
    Get user's API key info.

    :returns: Request results as dictionary.
    """

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

def get_wallet_balance(self, **kwargs):
    """
    Get wallet balance info.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-balance.
    :returns: Request results as dictionary.
    """

def wallet_fund_records(self, **kwargs):
    """
    Get wallet fund records. This endpoint also shows exchanges from the
    Asset Exchange, where the types for the exchange are
    ExchangeOrderWithdraw and ExchangeOrderDeposit.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-walletrecords.
    :returns: Request results as dictionary.
    """

def withdraw_records(self, **kwargs):
    """
    Get withdrawal records.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-withdrawrecords.
    :returns: Request results as dictionary.
    """

def asset_exchange_records(self, **kwargs):
    """
    Get asset exchange records.

    :param kwargs: See
        https://bybit-exchange.github.io/docs/inverse/#t-assetexchangerecords.
    :returns: Request results as dictionary.
    """

def server_time(self):
    """
    Get Bybit server time.

    :returns: Request results as dictionary.
    """

def announcement(self):
    """
    Get Bybit OpenAPI announcements in the last 30 days by reverse order.

    :returns: Request results as dictionary.
    """

```

## Custom Methods

```python
def close_position(self, symbol):
    """
    Closes your open position. Makes two requests (position, order).

    :param symbol: Required parameter. The symbol of the market as a string,
        e.g. 'BTCUSD'.
    :returns: Request results as dictionary.

    """
```