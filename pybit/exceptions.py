class FailedRequestError(Exception):
    """
    Exception raised for failed requests.

    Attributes:
        message -- Explanation of the error.
        status_code -- The code number returned.
    """
    def __init__(self, message, status_code, time):
        self.message = message
        self.status_code = status_code,
        self.time = time
        super().__init__((
            f'{message} (ErrCode: {status_code}) (ErrTime: {time})'
        ))


class InvalidRequestError(Exception):
    """
    Exception raised for returned Bybit errors.

    Attributes:
        message -- Explanation of the error.
        status_code -- The code number returned.
    """
    def __init__(self, message, status_code, time):
        self.message = message
        self.status_code = status_code,
        self.time = time
        super().__init__((
            f'{message} (ErrCode: {status_code}) (ErrTime: {time} UTC)'
        ))
