import websocket
import threading
import time
import json
import hmac
import logging
import re
import copy
from . import HTTP


logger = logging.getLogger(__name__)


SUBDOMAIN_TESTNET = "stream-testnet"
SUBDOMAIN_MAINNET = "stream"
DOMAIN_MAIN = "bybit"
DOMAIN_ALT = "bytick"

INVERSE_PERPETUAL = "Inverse Perp"
USDT_PERPETUAL = "USDT Perp"
SPOT = "Spot"


class WebSocketManager:
    def __init__(self, url, callback_function, ws_name,
                 test, domain="", api_key=None, api_secret=None,
                 ping_interval=30, ping_timeout=10,
                 restart_on_error=True):

        # Set endpoint.
        subdomain = SUBDOMAIN_TESTNET if test else SUBDOMAIN_MAINNET
        domain = DOMAIN_MAIN if not domain else domain
        url = url.format(SUBDOMAIN=subdomain, DOMAIN=domain)

        # Set API keys.
        self.api_key = api_key
        self.api_secret = api_secret

        self.callback = callback_function
        self.ws_name = ws_name
        if api_key:
            self.ws_name += " (Auth)"

        # Setup the callback directory following the format:
        #   {
        #       "topic_name": function
        #   }
        self.callback_directory = {}

        # Set ping settings.
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

        # Other optional data handling settings.
        self.handle_error = restart_on_error

        # Set initial state, initialize dictionary and connect.
        self._reset()
        self._connect(url)

    def _on_open(self):
        """
        Log WS open.
        """
        logger.debug(f"WebSocket {self.ws_name} opened.")

    def _on_message(self, message):
        """
        Parse incoming messages.
        """
        self.callback(json.loads(message))

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
            raise websocket.WebSocketTimeoutException("Connection failed.")

        # If given an api_key, authenticate.
        if self.api_key and self.api_secret:
            self._auth()

    def _auth(self):
        """
        Authorize websocket connection.
        """

        # Generate expires.
        expires = int((time.time() + 1) * 1000)

        # Generate signature.
        _val = f"GET/realtime{expires}"
        signature = str(hmac.new(
            bytes(self.api_secret, "utf-8"),
            bytes(_val, "utf-8"), digestmod="sha256"
        ).hexdigest())

        # Authenticate with API.
        self.ws.send(
            json.dumps({
                "op": "auth",
                "args": [self.api_key, expires, signature]
            })
        )

    def _on_error(self, error):
        """
        Exit on errors and raise exception, or attempt reconnect.
        """

        if not self.exited:
            logger.error(f"WebSocket {self.ws_name} encountered error: {error}.")
            self.exit()

        # Reconnect.
        if self.handle_error:
            self._reset()
            self._connect(self.endpoint)

    def _on_close(self):
        """
        Log WS close.
        """
        logger.debug(f"WebSocket {self.ws_name} closed.")

    def _reset(self):
        """
        Set state booleans and initialize dictionary.
        """
        self.exited = False
        self.auth = False

    def exit(self):
        """
        Closes the websocket connection.
        """

        self.ws.close()
        while self.ws.sock:
            continue
        self.exited = True


class FuturesWebSocketManager(WebSocketManager):
    def __init__(self, url, ws_name,
                 test, domain="", api_key=None, api_secret=None):
        super().__init__(
            url, self._handle_incoming_message, ws_name,
            test, domain=domain, api_key=api_key, api_secret=api_secret
        )

        self.private_topics = ["position", "execution", "order", "stop_order",
                               "wallet"]

        self.symbol_wildcard = "*"
        self.symbol_separator = "|"

    def subscribe(self, topic, callback, symbol=None):
        if symbol is None:
            symbol = []
        elif type(symbol) == str:
            symbol = [symbol]

        def prepare_subscription_args(list_of_symbols):
            """
            Prepares the topic for subscription by formatting it with the
            desired symbols.
            """
            def get_all_usdt_symbols():
                query_symbol_response = HTTP().query_symbol()["result"]
                for symbol_spec in query_symbol_response:
                    symbol = symbol_spec["name"]
                    if symbol.endswith("USDT"):
                        list_of_symbols.append(symbol)
                return list_of_symbols

            if topic in self.private_topics:
                # private topics do not support filters
                return [topic]
            elif list_of_symbols == self.symbol_wildcard or not list_of_symbols:
                # different WSS URL support may or may not support the
                # wildcard; for USDT, we need to manually get all symbols
                if self.ws_name != USDT_PERPETUAL:
                    return [topic.format(self.symbol_wildcard)]
                list_of_symbols = get_all_usdt_symbols()

            topics = []
            for symbol in list_of_symbols:
                topics.append(topic.format(symbol))
            return topics

        subscription_args = prepare_subscription_args(symbol)
        self._check_callback_directory(subscription_args)

        self.ws.send(
            json.dumps({
                "op": "subscribe",
                "args": subscription_args
            })
        )
        self._set_callback(topic, callback)

    def _handle_incoming_message(self, message):
        def is_auth_message():
            if message.get("request", {}).get("op") == "auth":
                return True
            else:
                return False

        def is_subscription_message():
            if message.get("request", {}).get("op") == "subscribe":
                return True
            else:
                return False

        # Check auth
        if is_auth_message():
            # If we get successful futures auth, notify user
            if message.get("success") is True:
                logger.debug(f"Authorization for {self.ws_name} successful.")
                self.auth = True
            # If we get unsuccessful auth, notify user.
            elif message.get("success") is False:
                logger.debug(f"Authorization for {self.ws_name} failed. Please "
                             f"check your API keys and restart.")

        # Check subscription
        elif is_subscription_message():
            sub = message["request"]["args"]
            # If we get successful futures subscription, notify user
            if message.get("success") is True:
                logger.debug(f"Subscription to {sub} successful.")
            # Futures subscription fail
            elif message.get("success") is False:
                response = message["ret_msg"]
                logger.error("Couldn't subscribe to topic."
                             f"Error: {response}.")
                self._pop_callback(sub[0])

        else:
            topic = message["topic"]
            callback_function = self._get_callback(topic)
            callback_function(message)

    def custom_topic_stream(self, topic, callback):
        return self.subscribe(topic=topic, callback=callback)

    def _extract_topic(self, topic_string):
        """
        Regex to return the topic without the symbol.
        """
        if topic_string in self.private_topics:
            return topic_string
        topic_without_symbol = re.match(r".*(\..*|)(?=\.)", topic_string)
        return topic_without_symbol[0]

    @staticmethod
    def _extract_symbol(topic_string):
        """
        Regex to return the symbol without the topic.
        """
        symbol_without_topic = re.search(r"(?!.*\.)[A-Z*|]*$", topic_string)
        return symbol_without_topic[0]

    def _check_callback_directory(self, topics):
        for topic in topics:
            if topic in self.callback_directory:
                raise Exception(f"You have already subscribed to this topic: "
                                f"{topic}")

    def _set_callback(self, topic, callback_function):
        topic = self._extract_topic(topic)
        self.callback_directory[topic] = callback_function

    def _get_callback(self, topic):
        topic = self._extract_topic(topic)
        return self.callback_directory[topic]

    def _pop_callback(self, topic):
        topic = self._extract_topic(topic)
        self.callback_directory.pop(topic)


class SpotWebSocketManager(WebSocketManager):
    def __init__(self, url, ws_name,
                 test, domain="", api_key=None, api_secret=None):
        super().__init__(
            url, self._handle_incoming_message, ws_name,
            test, domain=domain, api_key=api_key, api_secret=api_secret
        )
        self.public_v1_websocket = True if url.endswith("v1") else False
        self.public_v2_websocket = True if url.endswith("v2") else False
        self.private_websocket = True if api_key else False

    def subscribe(self, topic, callback):
        """
        Formats and sends the subscription message, given a topic. Saves the
        provided callback function, to be called by incoming messages.
        """
        def format_topic_with_multiple_symbols(topic):
            symbol = topic["symbol"]
            if type(symbol) == str:
                return topic
            elif type(symbol) == list:
                symbol_string = ""
                for item in symbol:
                    symbol_string += item + ","
                symbol_string = symbol_string[:-1]
                symbol = symbol_string
            else:
                raise Exception(f"Could not recognise symbol: "
                                f"({type(symbol)}) {symbol}")
            topic["symbol"] = symbol
            return topic

        if self.private_websocket:
            # Spot private topics don't need a subscription message
            self._set_callback(topic, callback)
            return

        conformed_topic = self._conform_topic(topic)

        if conformed_topic in self.callback_directory:
            raise Exception(f"You have already subscribed to this topic: "
                            f"{topic}")

        if self.public_v1_websocket:
            topic = format_topic_with_multiple_symbols(topic)
        self.ws.send(json.dumps(topic))
        topic = conformed_topic
        self._set_callback(topic, callback)

    def _handle_incoming_message(self, message):
        def is_ping_message():
            if type(message) == dict and message.get("ping"):
                # This is an unconventional ping message which looks like:
                # {"ping":1641489450001}
                # For now, we will not worry about responding to this,
                # as websocket-client automatically sends conventional ping
                # frames every 30 seconds, which successfully receive a pong
                # frame response.
                # https://websocket-client.readthedocs.io/en/latest/examples.html#ping-pong-usage
                return True
            else:
                return False

        def is_auth_message():
            if type(message) == dict and message.get("auth"):
                return True
            else:
                return False

        def is_subscription_message():
            if type(message) == dict and \
                    (message.get("event") == "sub" or message.get("code")):
                return True
            else:
                return False

        if is_ping_message():
            return

        # Check auth
        if is_auth_message():
            # If we get successful spot auth, notify user
            if message.get("auth") == "success":
                logger.debug(f"Authorization for {self.ws_name} successful.")
                self.auth = True
            # If we get unsuccessful auth, notify user.
            elif message.get("auth") == "fail":
                logger.debug(f"Authorization for {self.ws_name} failed. Please "
                             f"check your API keys and restart.")

        # Check subscription
        elif is_subscription_message():
            # If we get successful spot subscription, notify user
            if message.get("success") is True:
                sub = self._conform_topic(message)
                logger.debug(f"Subscription to {sub} successful.")
            # Spot subscription fail
            elif message.get("code") != "0":
                # There is no way to confirm the incoming message is related to
                #  any particular subscription message sent by the client, as
                #  the incoming message only includes an error code and
                #  message. Maybe a workaround could be developed in the future.
                logger.debug(f"Subscription failed: {message}")
                raise Exception("Spot subscription failed.")

        else:  # Standard topic push
            if self.private_websocket:
                for item in message:
                    topic_name = item["e"]
                    if self.callback_directory.get(topic_name):
                        callback_function = self.callback_directory[topic_name]
                        callback_function(item)
            else:
                callback_function = \
                    self.callback_directory[self._conform_topic(message)]
                callback_function(message)

    @staticmethod
    def _conform_topic(topic):
        """
        For spot API. Due to the fact that the JSON received in update
        messages does not include a simple "topic" key, and parameters all
        have their own separate keys, we need to compare the entire JSON.
        Therefore, we need to strip the JSON of any unnecessary keys, cast some
        values, and dump the JSON with sort_keys.
        """
        if isinstance(topic, str):
            topic = json.loads(topic)
        else:
            topic = copy.deepcopy(topic)
        topic.pop("event", "")
        topic.pop("symbolName", "")
        topic.pop("symbol", "")
        topic["params"].pop("realtimeInterval", "")
        topic["params"].pop("symbolName", "")
        topic["params"].pop("symbol", "")
        if topic["params"].get("klineType"):
            topic["topic"] += "_" + topic["params"].get("klineType")
            topic["params"].pop("klineType")
        if topic["params"].get("binary"):
            binary = topic["params"]["binary"]
            binary = False if binary == "false" else "true"
            topic["params"]["binary"] = binary
        if topic["params"].get("dumpScale"):
            topic["params"]["dumpScale"] = int(topic["params"]["dumpScale"])
        topic.pop("data", "")
        topic.pop("f", "")
        topic.pop("sendTime", "")
        topic.pop("shared", "")
        return json.dumps(topic, sort_keys=True, separators=(",", ":"))

    def _set_callback(self, topic, callback_function):
        topic = self._conform_topic(topic)
        self.callback_directory[topic] = callback_function

    def _get_callback(self, topic):
        topic = self._conform_topic(topic)
        return self.callback_directory[topic]

    def _pop_callback(self, topic):
        topic = self._conform_topic(topic)
        self.callback_directory.pop(topic)

    def _check_callback_directory(self, topics):
        for topic in topics:
            if topic in self.callback_directory:
                raise Exception(f"You have already subscribed to this topic: "
                                f"{topic}")


def _identify_ws_method(input_wss_url, wss_dictionary):
    """
    This method matches the input_wss_url with a particular WSS method. This
    helps ensure that, when subscribing to a custom topic, the topic
    subscription message is sent down the correct WSS connection.
    """
    path = re.compile("(wss://)?([^/\s]+)(.*)")
    input_wss_url_path = path.match(input_wss_url).group(3)
    for wss_url, function_call in wss_dictionary.items():
        wss_url_path = path.match(wss_url).group(3)
        if input_wss_url_path == wss_url_path:
            return function_call
