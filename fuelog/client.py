"""
Synchronous REST client for the Fuelog API.

Usage::

    from fuelog import FuelogClient, CreateFuelLogRequest

    client = FuelogClient(token="your_bearer_token")
    logs = client.list_logs(limit=10)
    for log in logs:
        print(log.id, log.brand, log.cost)
"""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fuelog._version import __version__
from fuelog.exceptions import (
    FuelogAPIError,
    FuelogAuthError,
    FuelogForbiddenError,
    FuelogNotFoundError,
    FuelogRateLimitError,
    FuelogServerError,
    FuelogValidationError,
)
from fuelog.models import (
    AnalyticsStats,
    CreateFuelLogRequest,
    CreateVehicleRequest,
    FuelLog,
    UpdateFuelLogRequest,
    UpdateVehicleRequest,
    Vehicle,
)

_DEFAULT_BASE_URL = "https://api.fuelog.app"
_DEFAULT_TIMEOUT = 30  # seconds


def _raise_for_status(status_code: int, body: str) -> None:
    """Map HTTP error codes to typed exceptions."""
    try:
        detail = json.loads(body).get("error") or json.loads(body).get("message") or body
    except Exception:
        detail = body

    if status_code == 401:
        raise FuelogAuthError(detail, status_code=status_code, response_body=body)
    if status_code == 403:
        raise FuelogForbiddenError(detail, status_code=status_code, response_body=body)
    if status_code == 404:
        raise FuelogNotFoundError(detail, status_code=status_code, response_body=body)
    if status_code == 422:
        raise FuelogValidationError(detail, status_code=status_code, response_body=body)
    if status_code == 429:
        raise FuelogRateLimitError(detail, status_code=status_code, response_body=body)
    if status_code >= 500:
        raise FuelogServerError(detail, status_code=status_code, response_body=body)
    raise FuelogAPIError(detail, status_code=status_code, response_body=body)


class FuelogClient:
    """Synchronous client for the Fuelog REST API.

    Args:
        token: Bearer token used for all requests.
        base_url: Override the default API base URL (useful for testing).
        timeout: HTTP timeout in seconds (default: 30).

    Example::

        client = FuelogClient(token="sk-...")
        vehicle_id = client.create_vehicle(
            CreateVehicleRequest(
                name="My Car",
                make="Toyota",
                model="Corolla",
                year="2022",
                fuel_type=FuelType.PETROL,
            )
        )
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
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": f"fuelog-python/{__version__}",
            "Accept": "application/json",
        }

    def _url(self, params: dict[str, Any]) -> str:
        query = urlencode({k: v for k, v in params.items() if v is not None})
        return f"{self._base_url}/api/rest?{query}"

    def _request(
        self,
        method: str,
        params: dict[str, Any],
        body: dict[str, Any] | None = None,
    ) -> Any:
        url = self._url(params)
        data = json.dumps(body).encode() if body is not None else None
        req = Request(url, data=data, headers=self._headers(), method=method)
        try:
            with urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as exc:
            body_text = exc.read().decode(errors="replace")
            _raise_for_status(exc.code, body_text)
        except URLError as exc:
            raise FuelogAPIError(f"Network error: {exc.reason}") from exc

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------

    def list_logs(self, limit: int = 100) -> list[FuelLog]:
        """Retrieve fuel logs for the authenticated user, newest first.

        Args:
            limit: Maximum number of entries to return (default 100).

        Returns:
            List of :class:`~fuelog.models.FuelLog` objects.
        """
        resp = self._request("GET", {"type": "logs", "limit": limit})
        return [FuelLog.from_dict(item) for item in resp.get("logs", [])]

    def create_log(self, request: CreateFuelLogRequest) -> str:
        """Create a new fuel log entry.

        Args:
            request: A :class:`~fuelog.models.CreateFuelLogRequest` with the required fields.

        Returns:
            The newly created log's ID string.

        Raises:
            FuelogForbiddenError: If the token lacks the ``write:logs`` scope.
        """
        resp = self._request("POST", {"type": "logs"}, body=request.to_dict())
        return str(resp["id"])

    def update_log(self, log_id: str, request: UpdateFuelLogRequest) -> bool:
        """Update an existing fuel log entry.

        Args:
            log_id: ID of the log to update.
            request: Fields to update wrapped in :class:`~fuelog.models.UpdateFuelLogRequest`.

        Returns:
            ``True`` on success.

        Raises:
            FuelogNotFoundError: If no log with ``log_id`` exists.
            FuelogForbiddenError: If the token lacks the ``write:logs`` scope.
        """
        resp = self._request("PUT", {"type": "logs", "id": log_id}, body=request.to_dict())
        return bool(resp.get("success", False))

    def delete_log(self, log_id: str) -> bool:
        """Delete a fuel log entry.

        Args:
            log_id: ID of the log to delete.

        Returns:
            ``True`` on success.

        Raises:
            FuelogNotFoundError: If no log with ``log_id`` exists.
            FuelogForbiddenError: If the token lacks the ``write:logs`` scope.
        """
        resp = self._request("DELETE", {"type": "logs", "id": log_id})
        return bool(resp.get("success", False))

    # ------------------------------------------------------------------
    # Vehicles
    # ------------------------------------------------------------------

    def list_vehicles(self, include_archived: bool = False) -> list[Vehicle]:
        """Retrieve the user's vehicle profiles.

        Args:
            include_archived: When ``True``, archived vehicles are included.

        Returns:
            List of :class:`~fuelog.models.Vehicle` objects.
        """
        params: dict[str, Any] = {"type": "vehicles"}
        if include_archived:
            params["includeArchived"] = "true"
        resp = self._request("GET", params)
        return [Vehicle.from_dict(item) for item in resp.get("vehicles", [])]

    def create_vehicle(self, request: CreateVehicleRequest) -> str:
        """Register a new vehicle.

        Args:
            request: A :class:`~fuelog.models.CreateVehicleRequest` with the required fields.

        Returns:
            The newly created vehicle's ID string.

        Raises:
            FuelogForbiddenError: If the token lacks the ``write:vehicles`` scope.
        """
        resp = self._request("POST", {"type": "vehicles"}, body=request.to_dict())
        return str(resp["id"])

    def update_vehicle(self, vehicle_id: str, request: UpdateVehicleRequest) -> bool:
        """Update an existing vehicle profile.

        Args:
            vehicle_id: ID of the vehicle to update.
            request: Fields to update wrapped in :class:`~fuelog.models.UpdateVehicleRequest`.

        Returns:
            ``True`` on success.

        Raises:
            FuelogNotFoundError: If no vehicle with ``vehicle_id`` exists.
            FuelogForbiddenError: If the token lacks the ``write:vehicles`` scope.
        """
        resp = self._request(
            "PUT",
            {"type": "vehicles", "id": vehicle_id},
            body=request.to_dict(),
        )
        return bool(resp.get("success", False))

    def delete_vehicle(self, vehicle_id: str) -> bool:
        """Delete a vehicle profile.

        Args:
            vehicle_id: ID of the vehicle to delete.

        Returns:
            ``True`` on success.

        Raises:
            FuelogNotFoundError: If no vehicle with ``vehicle_id`` exists.
            FuelogForbiddenError: If the token lacks the ``write:vehicles`` scope.
        """
        resp = self._request("DELETE", {"type": "vehicles", "id": vehicle_id})
        return bool(resp.get("success", False))

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_analytics(
        self,
        vehicle_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> AnalyticsStats:
        """Retrieve aggregated fuel efficiency and cost statistics.

        Args:
            vehicle_id: Optional vehicle ID to scope the analytics.
            start_date: Optional ISO 8601 start date filter.
            end_date: Optional ISO 8601 end date filter.

        Returns:
            An :class:`~fuelog.models.AnalyticsStats` object.
        """
        params: dict[str, Any] = {"type": "analytics"}
        if vehicle_id is not None:
            params["vehicleId"] = vehicle_id
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        resp = self._request("GET", params)
        return AnalyticsStats.from_dict(resp)
