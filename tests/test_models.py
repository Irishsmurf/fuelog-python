"""Unit tests for fuelog.models."""

from __future__ import annotations

from fuelog.models import (
    AnalyticsStats,
    CostOptimizationPeriod,
    CreateFuelLogRequest,
    CreateVehicleRequest,
    FuelLog,
    FuelType,
    MCPPromptResult,
    MCPToolResult,
    TrendMetric,
    UpdateFuelLogRequest,
    UpdateVehicleRequest,
    Vehicle,
)

# ---------------------------------------------------------------------------
# FuelLog
# ---------------------------------------------------------------------------


class TestFuelLog:
    def test_from_dict_full(self):
        data = {
            "id": "log-1",
            "brand": "BP",
            "cost": 40.0,
            "distanceKm": 300.0,
            "fuelAmountLiters": 28.0,
            "currency": "GBP",
            "originalCost": 35.0,
            "exchangeRate": 0.88,
            "vehicleId": "v1",
            "latitude": 51.5,
            "longitude": -0.1,
            "timestamp": "2025-01-01T12:00:00Z",
        }
        log = FuelLog.from_dict(data)
        assert log.id == "log-1"
        assert log.brand == "BP"
        assert log.cost == 40.0
        assert log.distance_km == 300.0
        assert log.fuel_amount_liters == 28.0
        assert log.currency == "GBP"
        assert log.original_cost == 35.0
        assert log.exchange_rate == 0.88
        assert log.vehicle_id == "v1"
        assert log.latitude == 51.5
        assert log.longitude == -0.1
        assert log.timestamp == "2025-01-01T12:00:00Z"

    def test_from_dict_minimal(self):
        log = FuelLog.from_dict({"id": "log-2"})
        assert log.id == "log-2"
        assert log.brand is None
        assert log.cost is None

    def test_to_dict_omits_none(self):
        log = FuelLog(id="log-3", brand="Shell", cost=50.0)
        d = log.to_dict()
        assert d == {"brand": "Shell", "cost": 50.0}
        assert "distanceKm" not in d
        assert "id" not in d  # id is not part of the write payload

    def test_to_dict_full(self):
        log = FuelLog(
            id="log-4",
            brand="Esso",
            cost=60.0,
            distance_km=500.0,
            fuel_amount_liters=45.0,
            currency="USD",
            original_cost=55.0,
            exchange_rate=1.1,
            vehicle_id="v2",
            latitude=40.7,
            longitude=-74.0,
            timestamp="2025-06-01T08:00:00Z",
        )
        d = log.to_dict()
        assert d["brand"] == "Esso"
        assert d["distanceKm"] == 500.0
        assert d["fuelAmountLiters"] == 45.0
        assert d["currency"] == "USD"
        assert d["vehicleId"] == "v2"
        assert d["timestamp"] == "2025-06-01T08:00:00Z"


# ---------------------------------------------------------------------------
# CreateFuelLogRequest
# ---------------------------------------------------------------------------


class TestCreateFuelLogRequest:
    def test_required_fields_in_dict(self):
        req = CreateFuelLogRequest(
            brand="Shell", cost=50.0, distance_km=400.0, fuel_amount_liters=35.0
        )
        d = req.to_dict()
        assert d["brand"] == "Shell"
        assert d["cost"] == 50.0
        assert d["distanceKm"] == 400.0
        assert d["fuelAmountLiters"] == 35.0

    def test_optional_fields_omitted_when_none(self):
        req = CreateFuelLogRequest(
            brand="Shell", cost=50.0, distance_km=400.0, fuel_amount_liters=35.0
        )
        d = req.to_dict()
        assert "currency" not in d
        assert "vehicleId" not in d
        assert "latitude" not in d

    def test_optional_fields_included_when_set(self):
        req = CreateFuelLogRequest(
            brand="Shell",
            cost=50.0,
            distance_km=400.0,
            fuel_amount_liters=35.0,
            currency="GBP",
            original_cost=45.0,
            exchange_rate=0.9,
            vehicle_id="v99",
            latitude=51.5,
            longitude=-0.1,
            timestamp="2025-01-01T00:00:00Z",
        )
        d = req.to_dict()
        assert d["currency"] == "GBP"
        assert d["originalCost"] == 45.0
        assert d["exchangeRate"] == 0.9
        assert d["vehicleId"] == "v99"
        assert d["latitude"] == 51.5
        assert d["longitude"] == -0.1
        assert d["timestamp"] == "2025-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# UpdateFuelLogRequest
# ---------------------------------------------------------------------------


class TestUpdateFuelLogRequest:
    def test_empty_produces_empty_dict(self):
        req = UpdateFuelLogRequest()
        assert req.to_dict() == {}

    def test_partial_update(self):
        req = UpdateFuelLogRequest(brand="Texaco", cost=55.0)
        d = req.to_dict()
        assert d == {"brand": "Texaco", "cost": 55.0}

    def test_all_fields(self):
        req = UpdateFuelLogRequest(
            brand="BP",
            cost=48.0,
            distance_km=350.0,
            fuel_amount_liters=32.0,
            currency="EUR",
            original_cost=48.0,
            exchange_rate=1.0,
            vehicle_id="v3",
            latitude=52.0,
            longitude=4.0,
            timestamp="2025-02-15T14:00:00Z",
        )
        d = req.to_dict()
        assert len(d) == 11
        assert d["distanceKm"] == 350.0
        assert d["fuelAmountLiters"] == 32.0


# ---------------------------------------------------------------------------
# Vehicle
# ---------------------------------------------------------------------------


class TestVehicle:
    def test_from_dict_full(self):
        data = {
            "id": "v1",
            "name": "My Car",
            "make": "Toyota",
            "model": "Corolla",
            "year": "2022",
            "fuelType": "Petrol",
            "isDefault": True,
            "isArchived": False,
        }
        vehicle = Vehicle.from_dict(data)
        assert vehicle.id == "v1"
        assert vehicle.name == "My Car"
        assert vehicle.make == "Toyota"
        assert vehicle.model == "Corolla"
        assert vehicle.year == "2022"
        assert vehicle.fuel_type == "Petrol"
        assert vehicle.is_default is True
        assert vehicle.is_archived is False

    def test_from_dict_minimal(self):
        v = Vehicle.from_dict({"id": "v2"})
        assert v.id == "v2"
        assert v.name is None
        assert v.fuel_type is None


# ---------------------------------------------------------------------------
# CreateVehicleRequest
# ---------------------------------------------------------------------------


class TestCreateVehicleRequest:
    def test_fuel_type_enum_serialised(self):
        req = CreateVehicleRequest(
            name="X", make="BMW", model="3 Series", year="2020", fuel_type=FuelType.DIESEL
        )
        d = req.to_dict()
        assert d["fuelType"] == "Diesel"

    def test_fuel_type_string_passthrough(self):
        req = CreateVehicleRequest(
            name="X", make="Honda", model="Civic", year="2019", fuel_type="Petrol"
        )
        d = req.to_dict()
        assert d["fuelType"] == "Petrol"

    def test_is_default_included_when_set(self):
        req = CreateVehicleRequest(
            name="X",
            make="Ford",
            model="Focus",
            year="2021",
            fuel_type=FuelType.PETROL,
            is_default=True,
        )
        d = req.to_dict()
        assert d["isDefault"] is True

    def test_is_default_omitted_when_none(self):
        req = CreateVehicleRequest(
            name="X", make="Ford", model="Focus", year="2021", fuel_type=FuelType.PETROL
        )
        d = req.to_dict()
        assert "isDefault" not in d


# ---------------------------------------------------------------------------
# UpdateVehicleRequest
# ---------------------------------------------------------------------------


class TestUpdateVehicleRequest:
    def test_empty_produces_empty_dict(self):
        assert UpdateVehicleRequest().to_dict() == {}

    def test_archive_flag(self):
        req = UpdateVehicleRequest(is_archived=True)
        assert req.to_dict() == {"isArchived": True}

    def test_fuel_type_enum(self):
        req = UpdateVehicleRequest(fuel_type=FuelType.HYBRID)
        assert req.to_dict() == {"fuelType": "Hybrid"}


# ---------------------------------------------------------------------------
# AnalyticsStats
# ---------------------------------------------------------------------------


class TestAnalyticsStats:
    def test_from_dict_populates_known_fields(self):
        data = {
            "logCount": 10,
            "totalSpent": 500.0,
            "homeCurrency": "EUR",
            "totalFuelLiters": 200.0,
            "totalDistanceKm": 4000.0,
            "efficiency": 20.0,
            "avgCostPerLiter": 2.5,
            "avgCostPerKm": 0.125,
        }
        stats = AnalyticsStats.from_dict(data)
        assert stats.log_count == 10
        assert stats.total_spent == 500.0
        assert stats.home_currency == "EUR"
        assert stats.total_fuel_liters == 200.0
        assert stats.total_distance_km == 4000.0
        assert stats.efficiency == 20.0
        assert stats.avg_cost_per_liter == 2.5
        assert stats.avg_cost_per_km == 0.125
        assert stats.extra == {}

    def test_extra_fields_captured(self):
        data = {"logCount": 5, "unknownField": "surprise"}
        stats = AnalyticsStats.from_dict(data)
        assert stats.extra == {"unknownField": "surprise"}

    def test_all_none_on_empty_dict(self):
        stats = AnalyticsStats.from_dict({})
        assert stats.log_count is None
        assert stats.extra == {}


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class TestEnumerations:
    def test_fuel_type_values(self):
        assert FuelType.PETROL.value == "Petrol"
        assert FuelType.DIESEL.value == "Diesel"
        assert FuelType.HYBRID.value == "Hybrid"
        assert FuelType.ELECTRIC.value == "Electric"

    def test_trend_metric_values(self):
        assert TrendMetric.KML.value == "kml"
        assert TrendMetric.MPG.value == "mpg"
        assert TrendMetric.L100KM.value == "l100km"
        assert TrendMetric.COST.value == "cost"

    def test_cost_optimization_period_values(self):
        assert CostOptimizationPeriod.LAST_MONTH.value == "last_month"
        assert CostOptimizationPeriod.LAST_QUARTER.value == "last_quarter"
        assert CostOptimizationPeriod.LAST_YEAR.value == "last_year"


# ---------------------------------------------------------------------------
# MCPToolResult
# ---------------------------------------------------------------------------


class TestMCPToolResult:
    def test_text_property_concatenates_text_blocks(self):
        result = MCPToolResult.from_dict(
            {
                "content": [
                    {"type": "text", "text": "Hello"},
                    {"type": "text", "text": "World"},
                    {"type": "image", "url": "https://example.com/img.png"},
                ],
                "isError": False,
            }
        )
        assert result.text == "Hello\nWorld"
        assert result.is_error is False

    def test_error_flag(self):
        result = MCPToolResult.from_dict({"content": [], "isError": True})
        assert result.is_error is True

    def test_empty_content(self):
        result = MCPToolResult.from_dict({})
        assert result.content == []
        assert result.text == ""


# ---------------------------------------------------------------------------
# MCPPromptResult
# ---------------------------------------------------------------------------


class TestMCPPromptResult:
    def test_from_dict(self):
        data = {
            "description": "Monthly fuel report",
            "messages": [
                {"role": "user", "content": {"type": "text", "text": "Here is your report..."}},
            ],
        }
        pr = MCPPromptResult.from_dict(data)
        assert pr.description == "Monthly fuel report"
        assert len(pr.messages) == 1
        assert pr.messages[0].role == "user"
        assert pr.messages[0].content["type"] == "text"

    def test_empty_messages(self):
        pr = MCPPromptResult.from_dict({"messages": []})
        assert pr.messages == []
        assert pr.description is None
