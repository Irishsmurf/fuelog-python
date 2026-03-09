"""
fuelog-python — Python client for the Fuelog API
=================================================

The package exposes two top-level clients:

* :class:`~fuelog.FuelogClient` – synchronous REST API client
* :class:`~fuelog.FuelogMCPClient` – MCP (Model Context Protocol) server client

Quick start::

    from fuelog import FuelogClient, CreateFuelLogRequest, FuelType

    client = FuelogClient(token="sk-...")

    # List your recent logs
    logs = client.list_logs(limit=10)

    # Add a new fill-up
    new_id = client.create_log(
        CreateFuelLogRequest(
            brand="Shell",
            cost=50.00,
            distance_km=400,
            fuel_amount_liters=35.0,
        )
    )

    # Fetch analytics
    stats = client.get_analytics()
    print(stats.efficiency)
"""

from fuelog._version import __version__
from fuelog.client import FuelogClient
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
from fuelog.mcp import FuelogMCPClient
from fuelog.models import (
    AnalyticsStats,
    CostOptimizationPeriod,
    CreateFuelLogRequest,
    CreateVehicleRequest,
    FuelLog,
    FuelType,
    MCPPromptMessage,
    MCPPromptResult,
    MCPToolResult,
    TrendMetric,
    UpdateFuelLogRequest,
    UpdateVehicleRequest,
    Vehicle,
)

__all__ = [
    "__version__",
    # Clients
    "FuelogClient",
    "FuelogMCPClient",
    # Models
    "FuelLog",
    "CreateFuelLogRequest",
    "UpdateFuelLogRequest",
    "Vehicle",
    "CreateVehicleRequest",
    "UpdateVehicleRequest",
    "AnalyticsStats",
    "MCPToolResult",
    "MCPPromptResult",
    "MCPPromptMessage",
    # Enums
    "FuelType",
    "TrendMetric",
    "CostOptimizationPeriod",
    # Exceptions
    "FuelogError",
    "FuelogAPIError",
    "FuelogAuthError",
    "FuelogForbiddenError",
    "FuelogNotFoundError",
    "FuelogValidationError",
    "FuelogRateLimitError",
    "FuelogServerError",
    "FuelogMCPError",
]
