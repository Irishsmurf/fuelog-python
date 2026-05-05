"""
Client for the Fuelog MCP (Model Context Protocol) server.

The MCP server at ``/api/mcp`` accepts JSON-RPC 2.0 requests over HTTP
(Streamable HTTP Server Transport).  This client wraps all registered
tools, resources, and prompts.

Usage::

    from fuelog import FuelogMCPClient

    mcp = FuelogMCPClient(token="your_bearer_token")

    # Call a tool
    result = mcp.list_logs(limit=5)
    print(result.text)

    # Read a resource
    print(mcp.read_resource("fuelog://analytics/summary"))

    # Get a prompt
    prompt = mcp.monthly_report(month="2025-03")
    for msg in prompt.messages:
        print(msg.role, msg.content)
"""

from __future__ import annotations

import itertools
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fuelog._version import __version__
from fuelog.exceptions import FuelogAPIError, FuelogMCPError
from fuelog.models import (
    CostOptimizationPeriod,
    FuelType,
    MCPPromptResult,
    MCPToolResult,
    TrendMetric,
)

_DEFAULT_BASE_URL = "https://api.fuelog.app"
_DEFAULT_TIMEOUT = 30

# Thread-safe counter for JSON-RPC IDs
_id_counter = itertools.count(1)


def _next_id() -> int:
    return next(_id_counter)


class FuelogMCPClient:
    """Client for the Fuelog MCP server at ``/api/mcp``.

    Args:
        token: Bearer token used for all requests.
        base_url: Override the default API base URL (useful for testing).
        timeout: HTTP timeout in seconds (default: 30).
    """

    def __init__(
        self,
        token: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Core JSON-RPC transport
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"fuelog-python/{__version__}",
        }

    def _rpc(self, method: str, params: dict[str, Any]) -> Any:
        """Send a JSON-RPC 2.0 request and return the ``result`` field.

        Raises:
            FuelogMCPError: If the server returns a JSON-RPC error object.
            FuelogAPIError: On network / HTTP-level failures.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": _next_id(),
            "method": method,
            "params": params,
        }
        url = f"{self._base_url}/api/mcp"
        data = json.dumps(payload).encode()
        req = Request(url, data=data, headers=self._headers(), method="POST")
        try:
            with urlopen(req, timeout=self._timeout) as resp:
                body = json.loads(resp.read().decode())
        except HTTPError as exc:
            body_text = exc.read().decode(errors="replace")
            raise FuelogAPIError(
                f"HTTP {exc.code}: {body_text}", status_code=exc.code, response_body=body_text
            ) from exc
        except URLError as exc:
            raise FuelogAPIError(f"Network error: {exc.reason}") from exc

        if "error" in body:
            err = body["error"]
            raise FuelogMCPError(
                err.get("message", "Unknown MCP error"),
                code=err.get("code"),
                data=err.get("data"),
            )
        return body.get("result")

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def list_logs(
        self,
        limit: int = 100,
        vehicle_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        brand: str | None = None,
    ) -> MCPToolResult:
        """Invoke the ``list_logs`` MCP tool.

        Args:
            limit: Maximum entries to return (default 100).
            vehicle_id: Optional vehicle filter.
            start_date: Optional ISO 8601 start filter.
            end_date: Optional ISO 8601 end filter.
            brand: Optional brand/station name filter.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        args: dict[str, Any] = {"limit": limit}
        if vehicle_id is not None:
            args["vehicleId"] = vehicle_id
        if start_date is not None:
            args["startDate"] = start_date
        if end_date is not None:
            args["endDate"] = end_date
        if brand is not None:
            args["brand"] = brand
        result = self._rpc("tools/call", {"name": "list_logs", "arguments": args})
        return MCPToolResult.from_dict(result)

    def log_fuel(
        self,
        brand: str,
        cost: float,
        distance_km: float,
        fuel_amount_liters: float,
        currency: str | None = None,
        original_cost: float | None = None,
        exchange_rate: float | None = None,
        vehicle_id: str | None = None,
        timestamp: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> MCPToolResult:
        """Invoke the ``log_fuel`` MCP tool.

        Requires the ``write:logs`` scope.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        if latitude is not None and not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"latitude must be between -90 and 90, got {latitude}")
        if longitude is not None and not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"longitude must be between -180 and 180, got {longitude}")

        args: dict[str, Any] = {
            "brand": brand,
            "cost": cost,
            "distanceKm": distance_km,
            "fuelAmountLiters": fuel_amount_liters,
        }
        if currency is not None:
            args["currency"] = currency
        if original_cost is not None:
            args["originalCost"] = original_cost
        if exchange_rate is not None:
            args["exchangeRate"] = exchange_rate
        if vehicle_id is not None:
            args["vehicleId"] = vehicle_id
        if timestamp is not None:
            args["timestamp"] = timestamp
        if latitude is not None:
            args["latitude"] = latitude
        if longitude is not None:
            args["longitude"] = longitude
        result = self._rpc("tools/call", {"name": "log_fuel", "arguments": args})
        return MCPToolResult.from_dict(result)

    def edit_fuel_log(
        self,
        log_id: str,
        brand: str | None = None,
        cost: float | None = None,
        distance_km: float | None = None,
        fuel_amount_liters: float | None = None,
        currency: str | None = None,
        original_cost: float | None = None,
        exchange_rate: float | None = None,
        vehicle_id: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> MCPToolResult:
        """Invoke the ``edit_fuel_log`` MCP tool.

        Requires the ``write:logs`` scope.

        Args:
            log_id: ID of the log entry to update.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        if latitude is not None and not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"latitude must be between -90 and 90, got {latitude}")
        if longitude is not None and not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"longitude must be between -180 and 180, got {longitude}")

        args: dict[str, Any] = {"logId": log_id}
        if brand is not None:
            args["brand"] = brand
        if cost is not None:
            args["cost"] = cost
        if distance_km is not None:
            args["distanceKm"] = distance_km
        if fuel_amount_liters is not None:
            args["fuelAmountLiters"] = fuel_amount_liters
        if currency is not None:
            args["currency"] = currency
        if original_cost is not None:
            args["originalCost"] = original_cost
        if exchange_rate is not None:
            args["exchangeRate"] = exchange_rate
        if vehicle_id is not None:
            args["vehicleId"] = vehicle_id
        if latitude is not None:
            args["latitude"] = latitude
        if longitude is not None:
            args["longitude"] = longitude
        result = self._rpc("tools/call", {"name": "edit_fuel_log", "arguments": args})
        return MCPToolResult.from_dict(result)

    def delete_fuel_log(self, log_id: str) -> MCPToolResult:
        """Invoke the ``delete_fuel_log`` MCP tool.

        Requires the ``write:logs`` scope.  The ``confirm: true`` parameter
        is added automatically.

        Args:
            log_id: ID of the log entry to permanently delete.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        result = self._rpc(
            "tools/call",
            {"name": "delete_fuel_log", "arguments": {"logId": log_id, "confirm": True}},
        )
        return MCPToolResult.from_dict(result)

    def list_vehicles(self, include_archived: bool = False) -> MCPToolResult:
        """Invoke the ``list_vehicles`` MCP tool.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        result = self._rpc(
            "tools/call",
            {
                "name": "list_vehicles",
                "arguments": {"includeArchived": include_archived},
            },
        )
        return MCPToolResult.from_dict(result)

    def add_vehicle(
        self,
        name: str,
        make: str,
        model: str,
        year: str,
        fuel_type: FuelType | str,
        is_default: bool | None = None,
    ) -> MCPToolResult:
        """Invoke the ``add_vehicle`` MCP tool.

        Requires the ``write:vehicles`` scope.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        args: dict[str, Any] = {
            "name": name,
            "make": make,
            "model": model,
            "year": year,
            "fuelType": fuel_type.value if isinstance(fuel_type, FuelType) else fuel_type,
        }
        if is_default is not None:
            args["isDefault"] = is_default
        result = self._rpc("tools/call", {"name": "add_vehicle", "arguments": args})
        return MCPToolResult.from_dict(result)

    def update_vehicle(
        self,
        vehicle_id: str,
        name: str | None = None,
        make: str | None = None,
        model: str | None = None,
        year: str | None = None,
        fuel_type: FuelType | str | None = None,
        is_default: bool | None = None,
        is_archived: bool | None = None,
    ) -> MCPToolResult:
        """Invoke the ``update_vehicle`` MCP tool.

        Requires the ``write:vehicles`` scope.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        args: dict[str, Any] = {"vehicleId": vehicle_id}
        if name is not None:
            args["name"] = name
        if make is not None:
            args["make"] = make
        if model is not None:
            args["model"] = model
        if year is not None:
            args["year"] = year
        if fuel_type is not None:
            args["fuelType"] = fuel_type.value if isinstance(fuel_type, FuelType) else fuel_type
        if is_default is not None:
            args["isDefault"] = is_default
        if is_archived is not None:
            args["isArchived"] = is_archived
        result = self._rpc("tools/call", {"name": "update_vehicle", "arguments": args})
        return MCPToolResult.from_dict(result)

    def get_analytics(
        self,
        vehicle_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> MCPToolResult:
        """Invoke the ``get_analytics`` MCP tool.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        args: dict[str, Any] = {}
        if vehicle_id is not None:
            args["vehicleId"] = vehicle_id
        if start_date is not None:
            args["startDate"] = start_date
        if end_date is not None:
            args["endDate"] = end_date
        result = self._rpc("tools/call", {"name": "get_analytics", "arguments": args})
        return MCPToolResult.from_dict(result)

    def compare_vehicles(
        self,
        vehicle_ids: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> MCPToolResult:
        """Invoke the ``compare_vehicles`` MCP tool.

        Returns:
            :class:`~fuelog.models.MCPToolResult`
        """
        args: dict[str, Any] = {}
        if vehicle_ids is not None:
            args["vehicleIds"] = vehicle_ids
        if start_date is not None:
            args["startDate"] = start_date
        if end_date is not None:
            args["endDate"] = end_date
        result = self._rpc("tools/call", {"name": "compare_vehicles", "arguments": args})
        return MCPToolResult.from_dict(result)

    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    def read_resource(self, uri: str) -> Any:
        """Read an MCP resource by its ``fuelog://`` URI.

        Available resources:
        - ``fuelog://logs``
        - ``fuelog://logs/{id}``
        - ``fuelog://vehicles``
        - ``fuelog://vehicles/{id}``
        - ``fuelog://analytics/summary``
        - ``fuelog://analytics/monthly``
        - ``fuelog://analytics/vehicles``
        - ``fuelog://profile``

        Returns:
            The parsed resource contents (dict or list).
        """
        return self._rpc("resources/read", {"uri": uri})

    def get_all_logs_resource(self) -> Any:
        """Read the ``fuelog://logs`` resource (up to 200 entries)."""
        return self.read_resource("fuelog://logs")

    def get_log_resource(self, log_id: str) -> Any:
        """Read a specific log resource by ID."""
        return self.read_resource(f"fuelog://logs/{log_id}")

    def get_vehicles_resource(self) -> Any:
        """Read the ``fuelog://vehicles`` resource."""
        return self.read_resource("fuelog://vehicles")

    def get_vehicle_resource(self, vehicle_id: str) -> Any:
        """Read a specific vehicle resource by ID."""
        return self.read_resource(f"fuelog://vehicles/{vehicle_id}")

    def get_analytics_summary_resource(self) -> Any:
        """Read the ``fuelog://analytics/summary`` resource."""
        return self.read_resource("fuelog://analytics/summary")

    def get_analytics_monthly_resource(self) -> Any:
        """Read the ``fuelog://analytics/monthly`` resource."""
        return self.read_resource("fuelog://analytics/monthly")

    def get_analytics_vehicles_resource(self) -> Any:
        """Read the ``fuelog://analytics/vehicles`` resource."""
        return self.read_resource("fuelog://analytics/vehicles")

    def get_profile_resource(self) -> Any:
        """Read the ``fuelog://profile`` resource."""
        return self.read_resource("fuelog://profile")

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------

    def _get_prompt(self, name: str, arguments: dict[str, Any]) -> MCPPromptResult:
        result = self._rpc("prompts/get", {"name": name, "arguments": arguments})
        return MCPPromptResult.from_dict(result)

    def monthly_report(
        self,
        month: str,
        vehicle_id: str | None = None,
    ) -> MCPPromptResult:
        """Get the ``monthly_report`` prompt populated with data.

        Args:
            month: Target month in ``YYYY-MM`` format.
            vehicle_id: Optional vehicle scope.

        Returns:
            :class:`~fuelog.models.MCPPromptResult`
        """
        args: dict[str, Any] = {"month": month}
        if vehicle_id is not None:
            args["vehicleId"] = vehicle_id
        return self._get_prompt("monthly_report", args)

    def trend_analysis(
        self,
        start_date: str,
        end_date: str,
        metric: TrendMetric | str | None = None,
        vehicle_id: str | None = None,
    ) -> MCPPromptResult:
        """Get the ``trend_analysis`` prompt populated with data.

        Args:
            start_date: ISO 8601 start date.
            end_date: ISO 8601 end date.
            metric: One of ``kml``, ``mpg``, ``l100km``, or ``cost``.
            vehicle_id: Optional vehicle scope.

        Returns:
            :class:`~fuelog.models.MCPPromptResult`
        """
        args: dict[str, Any] = {"startDate": start_date, "endDate": end_date}
        if metric is not None:
            args["metric"] = metric.value if isinstance(metric, TrendMetric) else metric
        if vehicle_id is not None:
            args["vehicleId"] = vehicle_id
        return self._get_prompt("trend_analysis", args)

    def cost_optimization(
        self,
        period: CostOptimizationPeriod | str | None = None,
    ) -> MCPPromptResult:
        """Get the ``cost_optimization`` prompt populated with data.

        Args:
            period: One of ``last_month``, ``last_quarter`` (default), or ``last_year``.

        Returns:
            :class:`~fuelog.models.MCPPromptResult`
        """
        args: dict[str, Any] = {}
        if period is not None:
            args["period"] = period.value if isinstance(period, CostOptimizationPeriod) else period
        return self._get_prompt("cost_optimization", args)
