class FailedRequestError(Exception):
    """
    Exception raised for failed requests.

    Attributes:
        request -- The original request that caused the error.
        message -- Explanation of the error.
        status_code -- The code number returned.
        time -- The time of the error.
    """
    def __init__(self, request, message, status_code, time):
        self.request = request
        self.message = message
        self.status_code = status_code
        self.time = time
        super().__init__(
            f'{message.capitalize()} (ErrCode: {status_code}) (ErrTime: {time})'
            f'.\nRequest → {request}.'
        )


class InvalidRequestError(Exception):
    """
    Exception raised for returned Bybit errors.

    Attributes:
        request -- The original request that caused the error.
        message -- Explanation of the error.
        status_code -- The code number returned.
        time -- The time of the error.
    """
    def __init__(self, request, message, status_code, time):
        self.request = request
        self.message = message
        self.status_code = status_code
        self.time = time
        super().__init__(
            f'{message.capitalize()} (ErrCode: {status_code}) (ErrTime: {time})'
            f'.\nRequest → {request}.'
        )
