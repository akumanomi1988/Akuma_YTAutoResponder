class YouTubeAutoResponderError(Exception):
    """Base exception class for all package errors"""
    pass

class AuthenticationError(YouTubeAutoResponderError):
    """Authentication related errors"""
    def __init__(self, message="Check your client_secrets.json path and contents"):
        super().__init__(message)

class APIQuotaExceeded(YouTubeAutoResponderError):
    """API quota exceeded exception"""
    pass