class FailedRequestError(Exception):
    """
    Exception raised for failed requests.

    Attributes:
        message -- Explanation of the error.
        status_code -- The code number returned.
    """
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidRequestError(Exception):
    """
    Exception raised for returned Bybit errors.

    Attributes:
        message -- Explanation of the error.
        status_code -- The code number returned.
    """
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
