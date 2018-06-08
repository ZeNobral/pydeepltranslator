class DeepLException(Exception):
    pass


class WrongRequest(DeepLException):
    pass


class AuthorizationFailed(DeepLException):
    pass


class RequestEntityTooLarge(DeepLException):
    pass


class TooManyRequests(DeepLException):
    pass


class QuotaExceeded(DeepLException):
    pass