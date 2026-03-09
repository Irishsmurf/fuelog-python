"""
Exceptions raised by the Fuelog Python client.
"""

from __future__ import annotations


class FuelogError(Exception):
    """Base exception for all Fuelog errors."""


class FuelogAPIError(FuelogError):
    """Raised when the Fuelog API returns an error response.

    Attributes:
        status_code: The HTTP status code returned by the API.
        message: The error message from the API response body.
        response_body: The raw response body as a string.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={str(self)!r}, status_code={self.status_code!r})"


class FuelogAuthError(FuelogAPIError):
    """Raised when authentication fails (HTTP 401)."""


class FuelogForbiddenError(FuelogAPIError):
    """Raised when the token lacks the required scope (HTTP 403)."""


class FuelogNotFoundError(FuelogAPIError):
    """Raised when a requested resource does not exist (HTTP 404)."""


class FuelogValidationError(FuelogAPIError):
    """Raised when the request body fails server-side validation (HTTP 422)."""


class FuelogRateLimitError(FuelogAPIError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""


class FuelogServerError(FuelogAPIError):
    """Raised when the Fuelog server returns a 5xx error."""


class FuelogMCPError(FuelogError):
    """Raised when the MCP JSON-RPC layer returns an error.

    Attributes:
        code: The JSON-RPC error code.
        data: Optional additional data attached to the error.
    """

    def __init__(
        self,
        message: str,
        code: int | None = None,
        data: object | None = None,
    ) -> None:
        self.code = code
        self.data = data
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={str(self)!r}, code={self.code!r})"
