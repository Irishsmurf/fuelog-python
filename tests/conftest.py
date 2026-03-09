"""Shared pytest fixtures and test helpers."""

from __future__ import annotations

import json
from io import BytesIO
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from fuelog import FuelogClient, FuelogMCPClient

# ---------------------------------------------------------------------------
# Sample payloads
# ---------------------------------------------------------------------------

SAMPLE_LOG = {
    "id": "log-001",
    "brand": "Shell",
    "cost": 50.0,
    "distanceKm": 400.0,
    "fuelAmountLiters": 35.0,
    "currency": "EUR",
    "originalCost": 50.0,
    "exchangeRate": 1.0,
    "vehicleId": "vehicle-001",
    "latitude": 53.349805,
    "longitude": -6.26031,
    "timestamp": "2025-03-01T10:00:00Z",
}

SAMPLE_VEHICLE = {
    "id": "vehicle-001",
    "name": "My Car",
    "make": "Toyota",
    "model": "Corolla",
    "year": "2022",
    "fuelType": "Petrol",
    "isDefault": True,
    "isArchived": False,
}

SAMPLE_ANALYTICS = {
    "logCount": 42,
    "totalSpent": 1200.0,
    "homeCurrency": "EUR",
    "totalFuelLiters": 840.0,
    "totalDistanceKm": 16800.0,
    "efficiency": 20.0,
    "avgCostPerLiter": 1.43,
    "avgCostPerKm": 0.071,
    "extraField": "extra_value",
}


# ---------------------------------------------------------------------------
# HTTP mock helpers
# ---------------------------------------------------------------------------


def make_response(body: Any, status: int = 200) -> MagicMock:
    """Return a mock that behaves like urllib's response context manager."""
    raw = json.dumps(body).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw
    mock_resp.status = status
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def make_http_error(status: int, body: Any = None) -> MagicMock:
    """Return a mock HTTPError that raises on urlopen."""
    from urllib.error import HTTPError

    err_body = json.dumps(body or {"error": "error"}).encode()
    return HTTPError(
        url="https://api.fuelog.app/api/rest",
        code=status,
        msg="Error",
        hdrs=MagicMock(),
        fp=BytesIO(err_body),
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def rest_client() -> FuelogClient:
    return FuelogClient(token="test-token", base_url="https://api.fuelog.app")


@pytest.fixture()
def mcp_client() -> FuelogMCPClient:
    return FuelogMCPClient(token="test-token", base_url="https://api.fuelog.app")
