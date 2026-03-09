"""Unit tests for fuelog.exceptions."""

from __future__ import annotations

import pytest

from fuelog.exceptions import (
    FuelogAPIError,
    FuelogAuthError,
    FuelogError,
    FuelogForbiddenError,
    FuelogMCPError,
    FuelogNotFoundError,
    FuelogRateLimitError,
    FuelogServerError,
    FuelogValidationError,
)


class TestExceptionHierarchy:
    def test_fuelog_error_is_base(self):
        assert issubclass(FuelogAPIError, FuelogError)
        assert issubclass(FuelogAuthError, FuelogAPIError)
        assert issubclass(FuelogForbiddenError, FuelogAPIError)
        assert issubclass(FuelogNotFoundError, FuelogAPIError)
        assert issubclass(FuelogValidationError, FuelogAPIError)
        assert issubclass(FuelogRateLimitError, FuelogAPIError)
        assert issubclass(FuelogServerError, FuelogAPIError)
        assert issubclass(FuelogMCPError, FuelogError)

    def test_api_error_attributes(self):
        exc = FuelogAPIError("bad request", status_code=400, response_body='{"error":"bad"}')
        assert str(exc) == "bad request"
        assert exc.status_code == 400
        assert exc.response_body == '{"error":"bad"}'

    def test_api_error_defaults(self):
        exc = FuelogAPIError("oops")
        assert exc.status_code is None
        assert exc.response_body is None

    def test_api_error_repr(self):
        exc = FuelogAPIError("not found", status_code=404)
        r = repr(exc)
        assert "404" in r
        assert "not found" in r

    def test_mcp_error_attributes(self):
        exc = FuelogMCPError("rpc error", code=-32601, data={"detail": "x"})
        assert str(exc) == "rpc error"
        assert exc.code == -32601
        assert exc.data == {"detail": "x"}

    def test_mcp_error_defaults(self):
        exc = FuelogMCPError("mcp fail")
        assert exc.code is None
        assert exc.data is None

    def test_mcp_error_repr(self):
        exc = FuelogMCPError("method not found", code=-32601)
        r = repr(exc)
        assert "-32601" in r
        assert "method not found" in r

    def test_catch_by_base_class(self):
        with pytest.raises(FuelogError):
            raise FuelogAuthError("unauthorized", status_code=401)

        with pytest.raises(FuelogAPIError):
            raise FuelogNotFoundError("not found", status_code=404)

        with pytest.raises(FuelogError):
            raise FuelogMCPError("mcp error")
