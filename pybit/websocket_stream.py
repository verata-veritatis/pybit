import websocket
import threading
import time
import json
import hmac
import logging
import re


logger = logging.getLogger(__name__)


SUBDOMAIN_TESTNET = "stream-testnet"
SUBDOMAIN_MAINNET = "stream"
DOMAIN_MAIN = "bybit"
DOMAIN_ALT = "bytick"


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

    def subscribe(self, topic, callback):
        if topic in self.callback_directory:
            raise Exception(f"You have already subscribed to this topic: "
                            f"{topic}")
        self.ws.send(
            json.dumps({
                "op": "subscribe",
                "args": [topic]
            })
        )
        self.callback_directory[topic] = callback

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
                if "unknown topic" in response:
                    logger.error("Couldn't subscribe to topic."
                                 f"Error: {response}.")
                self.callback_directory.pop(sub[0])

        else:
            topic = message["topic"]
            callback_function = self.callback_directory[topic]
            callback_function(message)

    def custom_topic_stream(self, topic, callback):
        return self.subscribe(topic=topic, callback=callback)


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
