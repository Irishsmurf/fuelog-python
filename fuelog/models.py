"""
Data models for the Fuelog API.

All models use Python dataclasses with optional fields matching the API spec.
Where *pydantic* is installed the models can alternatively be built from it,
but the library intentionally keeps it as an optional dependency so that users
without pydantic can still consume the package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class FuelType(str, Enum):
    """Fuel type accepted by the Fuelog API."""

    PETROL = "Petrol"
    DIESEL = "Diesel"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"


class TrendMetric(str, Enum):
    """Metric selector for the ``trend_analysis`` MCP prompt."""

    KML = "kml"
    MPG = "mpg"
    L100KM = "l100km"
    COST = "cost"


class CostOptimizationPeriod(str, Enum):
    """Time window for the ``cost_optimization`` MCP prompt."""

    LAST_MONTH = "last_month"
    LAST_QUARTER = "last_quarter"
    LAST_YEAR = "last_year"


# ---------------------------------------------------------------------------
# Fuel-log models
# ---------------------------------------------------------------------------


@dataclass
class FuelLog:
    """A single fuel log entry returned by the API.

    All fields other than ``id`` are optional because the GET endpoint
    returns whatever the server stored at creation time.
    """

    id: str
    brand: str | None = None
    cost: float | None = None
    distance_km: float | None = None
    fuel_amount_liters: float | None = None
    currency: str | None = None
    original_cost: float | None = None
    exchange_rate: float | None = None
    vehicle_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FuelLog:
        return cls(
            id=data["id"],
            brand=data.get("brand"),
            cost=data.get("cost"),
            distance_km=data.get("distanceKm"),
            fuel_amount_liters=data.get("fuelAmountLiters"),
            currency=data.get("currency"),
            original_cost=data.get("originalCost"),
            exchange_rate=data.get("exchangeRate"),
            vehicle_id=data.get("vehicleId"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            timestamp=data.get("timestamp"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a dict suitable for the POST/PUT request body."""
        payload: dict[str, Any] = {}
        if self.brand is not None:
            payload["brand"] = self.brand
        if self.cost is not None:
            payload["cost"] = self.cost
        if self.distance_km is not None:
            payload["distanceKm"] = self.distance_km
        if self.fuel_amount_liters is not None:
            payload["fuelAmountLiters"] = self.fuel_amount_liters
        if self.currency is not None:
            payload["currency"] = self.currency
        if self.original_cost is not None:
            payload["originalCost"] = self.original_cost
        if self.exchange_rate is not None:
            payload["exchangeRate"] = self.exchange_rate
        if self.vehicle_id is not None:
            payload["vehicleId"] = self.vehicle_id
        if self.latitude is not None:
            payload["latitude"] = self.latitude
        if self.longitude is not None:
            payload["longitude"] = self.longitude
        if self.timestamp is not None:
            payload["timestamp"] = self.timestamp
        return payload


@dataclass
class CreateFuelLogRequest:
    """Parameters required to create a new fuel log entry."""

    brand: str
    cost: float
    distance_km: float
    fuel_amount_liters: float
    currency: str | None = None
    original_cost: float | None = None
    exchange_rate: float | None = None
    vehicle_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "brand": self.brand,
            "cost": self.cost,
            "distanceKm": self.distance_km,
            "fuelAmountLiters": self.fuel_amount_liters,
        }
        if self.currency is not None:
            payload["currency"] = self.currency
        if self.original_cost is not None:
            payload["originalCost"] = self.original_cost
        if self.exchange_rate is not None:
            payload["exchangeRate"] = self.exchange_rate
        if self.vehicle_id is not None:
            payload["vehicleId"] = self.vehicle_id
        if self.latitude is not None:
            payload["latitude"] = self.latitude
        if self.longitude is not None:
            payload["longitude"] = self.longitude
        if self.timestamp is not None:
            payload["timestamp"] = self.timestamp
        return payload


@dataclass
class UpdateFuelLogRequest:
    """Parameters accepted when updating an existing fuel log entry.

    All fields are optional — only non-``None`` fields are sent to the API.
    """

    brand: str | None = None
    cost: float | None = None
    distance_km: float | None = None
    fuel_amount_liters: float | None = None
    currency: str | None = None
    original_cost: float | None = None
    exchange_rate: float | None = None
    vehicle_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.brand is not None:
            payload["brand"] = self.brand
        if self.cost is not None:
            payload["cost"] = self.cost
        if self.distance_km is not None:
            payload["distanceKm"] = self.distance_km
        if self.fuel_amount_liters is not None:
            payload["fuelAmountLiters"] = self.fuel_amount_liters
        if self.currency is not None:
            payload["currency"] = self.currency
        if self.original_cost is not None:
            payload["originalCost"] = self.original_cost
        if self.exchange_rate is not None:
            payload["exchangeRate"] = self.exchange_rate
        if self.vehicle_id is not None:
            payload["vehicleId"] = self.vehicle_id
        if self.latitude is not None:
            payload["latitude"] = self.latitude
        if self.longitude is not None:
            payload["longitude"] = self.longitude
        if self.timestamp is not None:
            payload["timestamp"] = self.timestamp
        return payload


# ---------------------------------------------------------------------------
# Vehicle models
# ---------------------------------------------------------------------------


@dataclass
class Vehicle:
    """A vehicle profile returned by the API."""

    id: str
    name: str | None = None
    make: str | None = None
    model: str | None = None
    year: str | None = None
    fuel_type: str | None = None
    is_default: bool | None = None
    is_archived: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Vehicle:
        return cls(
            id=data["id"],
            name=data.get("name"),
            make=data.get("make"),
            model=data.get("model"),
            year=data.get("year"),
            fuel_type=data.get("fuelType"),
            is_default=data.get("isDefault"),
            is_archived=data.get("isArchived"),
        )


@dataclass
class CreateVehicleRequest:
    """Parameters required to register a new vehicle."""

    name: str
    make: str
    model: str
    year: str
    fuel_type: FuelType
    is_default: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "fuelType": self.fuel_type.value
            if isinstance(self.fuel_type, FuelType)
            else self.fuel_type,
        }
        if self.is_default is not None:
            payload["isDefault"] = self.is_default
        return payload


@dataclass
class UpdateVehicleRequest:
    """Parameters accepted when updating a vehicle.  All fields are optional."""

    name: str | None = None
    make: str | None = None
    model: str | None = None
    year: str | None = None
    fuel_type: FuelType | str | None = None
    is_default: bool | None = None
    is_archived: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.name is not None:
            payload["name"] = self.name
        if self.make is not None:
            payload["make"] = self.make
        if self.model is not None:
            payload["model"] = self.model
        if self.year is not None:
            payload["year"] = self.year
        if self.fuel_type is not None:
            payload["fuelType"] = (
                self.fuel_type.value if isinstance(self.fuel_type, FuelType) else self.fuel_type
            )
        if self.is_default is not None:
            payload["isDefault"] = self.is_default
        if self.is_archived is not None:
            payload["isArchived"] = self.is_archived
        return payload


# ---------------------------------------------------------------------------
# Analytics models
# ---------------------------------------------------------------------------


@dataclass
class AnalyticsStats:
    """Aggregated analytics stats returned by :meth:`~fuelog.FuelogClient.get_analytics`."""

    log_count: int | None = None
    total_spent: float | None = None
    home_currency: str | None = None
    total_fuel_liters: float | None = None
    total_distance_km: float | None = None
    efficiency: float | None = None
    avg_cost_per_liter: float | None = None
    avg_cost_per_km: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalyticsStats:
        known = {
            "logCount",
            "totalSpent",
            "homeCurrency",
            "totalFuelLiters",
            "totalDistanceKm",
            "efficiency",
            "avgCostPerLiter",
            "avgCostPerKm",
        }
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(
            log_count=data.get("logCount"),
            total_spent=data.get("totalSpent"),
            home_currency=data.get("homeCurrency"),
            total_fuel_liters=data.get("totalFuelLiters"),
            total_distance_km=data.get("totalDistanceKm"),
            efficiency=data.get("efficiency"),
            avg_cost_per_liter=data.get("avgCostPerLiter"),
            avg_cost_per_km=data.get("avgCostPerKm"),
            extra=extra,
        )


# ---------------------------------------------------------------------------
# MCP models
# ---------------------------------------------------------------------------


@dataclass
class MCPToolResult:
    """Result returned by an MCP tool invocation."""

    content: list[dict[str, Any]]
    is_error: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MCPToolResult:
        return cls(
            content=data.get("content", []),
            is_error=data.get("isError", False),
        )

    @property
    def text(self) -> str:
        """Convenience: concatenate all text-type content blocks."""
        parts = [block.get("text", "") for block in self.content if block.get("type") == "text"]
        return "\n".join(parts)


@dataclass
class MCPPromptMessage:
    """A single message in an MCP prompt response."""

    role: str
    content: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MCPPromptMessage:
        return cls(role=data["role"], content=data["content"])


@dataclass
class MCPPromptResult:
    """Result returned by an MCP prompt/get invocation."""

    description: str | None
    messages: list[MCPPromptMessage]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MCPPromptResult:
        return cls(
            description=data.get("description"),
            messages=[MCPPromptMessage.from_dict(m) for m in data.get("messages", [])],
        )
