"""Unit tests for fuelog.FuelogClient (REST API)."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from fuelog import (
    FuelogAuthError,
    FuelogForbiddenError,
    FuelogNotFoundError,
    FuelogRateLimitError,
    FuelogServerError,
    FuelogValidationError,
)
from fuelog.models import (
    CreateFuelLogRequest,
    CreateVehicleRequest,
    FuelType,
    UpdateFuelLogRequest,
    UpdateVehicleRequest,
)
from tests.conftest import (
    SAMPLE_ANALYTICS,
    SAMPLE_LOG,
    SAMPLE_VEHICLE,
    make_http_error,
    make_response,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def urlopen_returning(body, status=200):
    return patch("fuelog.client.urlopen", return_value=make_response(body, status))


def urlopen_raising(exc):
    return patch("fuelog.client.urlopen", side_effect=exc)


# ---------------------------------------------------------------------------
# Logs — list
# ---------------------------------------------------------------------------


class TestListLogs:
    def test_returns_list_of_fuel_logs(self, rest_client):
        with urlopen_returning({"logs": [SAMPLE_LOG]}):
            logs = rest_client.list_logs()
        assert len(logs) == 1
        assert logs[0].id == "log-001"
        assert logs[0].brand == "Shell"
        assert logs[0].cost == 50.0
        assert logs[0].distance_km == 400.0
        assert logs[0].vehicle_id == "vehicle-001"

    def test_empty_list(self, rest_client):
        with urlopen_returning({"logs": []}):
            logs = rest_client.list_logs()
        assert logs == []

    def test_limit_param_sent_in_url(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            return make_response({"logs": []})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.list_logs(limit=5)

        assert "limit=5" in captured["url"]

    def test_default_limit_is_100(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            return make_response({"logs": []})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.list_logs()

        assert "limit=100" in captured["url"]

    def test_401_raises_auth_error(self, rest_client):
        with urlopen_raising(make_http_error(401)), pytest.raises(FuelogAuthError) as exc_info:
            rest_client.list_logs()
        assert exc_info.value.status_code == 401

    def test_500_raises_server_error(self, rest_client):
        with urlopen_raising(make_http_error(500)), pytest.raises(FuelogServerError):
            rest_client.list_logs()

    def test_429_raises_rate_limit_error(self, rest_client):
        with urlopen_raising(make_http_error(429)), pytest.raises(FuelogRateLimitError):
            rest_client.list_logs()


# ---------------------------------------------------------------------------
# Logs — create
# ---------------------------------------------------------------------------


class TestCreateLog:
    def test_returns_new_id(self, rest_client):
        with urlopen_returning({"id": "log-new-001"}, status=201):
            new_id = rest_client.create_log(
                CreateFuelLogRequest(
                    brand="Texaco",
                    cost=45.0,
                    distance_km=350.0,
                    fuel_amount_liters=30.0,
                )
            )
        assert new_id == "log-new-001"

    def test_request_body_serialised_correctly(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["body"] = json.loads(req.data.decode())
            return make_response({"id": "x"})

        req = CreateFuelLogRequest(
            brand="Shell",
            cost=50.0,
            distance_km=400.0,
            fuel_amount_liters=35.0,
            vehicle_id="v1",
        )
        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.create_log(req)

        body = captured["body"]
        assert body["brand"] == "Shell"
        assert body["cost"] == 50.0
        assert body["distanceKm"] == 400.0
        assert body["fuelAmountLiters"] == 35.0
        assert body["vehicleId"] == "v1"

    def test_403_raises_forbidden(self, rest_client):
        with (
            urlopen_raising(make_http_error(403, {"error": "Insufficient scope"})),
            pytest.raises(FuelogForbiddenError) as exc_info,
        ):
            rest_client.create_log(
                CreateFuelLogRequest(brand="X", cost=1.0, distance_km=1.0, fuel_amount_liters=1.0)
            )
        assert exc_info.value.status_code == 403

    def test_422_raises_validation_error(self, rest_client):
        with urlopen_raising(make_http_error(422)), pytest.raises(FuelogValidationError):
            rest_client.create_log(
                CreateFuelLogRequest(brand="X", cost=1.0, distance_km=1.0, fuel_amount_liters=1.0)
            )


# ---------------------------------------------------------------------------
# Logs — update
# ---------------------------------------------------------------------------


class TestUpdateLog:
    def test_returns_true_on_success(self, rest_client):
        with urlopen_returning({"success": True}):
            result = rest_client.update_log("log-001", UpdateFuelLogRequest(brand="BP"))
        assert result is True

    def test_correct_id_in_url(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            return make_response({"success": True})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.update_log("log-XYZ", UpdateFuelLogRequest(cost=60.0))

        assert "id=log-XYZ" in captured["url"]

    def test_404_raises_not_found(self, rest_client):
        with urlopen_raising(make_http_error(404)), pytest.raises(FuelogNotFoundError):
            rest_client.update_log("no-such-log", UpdateFuelLogRequest())


# ---------------------------------------------------------------------------
# Logs — delete
# ---------------------------------------------------------------------------


class TestDeleteLog:
    def test_returns_true_on_success(self, rest_client):
        with urlopen_returning({"success": True}):
            result = rest_client.delete_log("log-001")
        assert result is True

    def test_correct_method_and_id(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["method"] = req.method
            captured["url"] = req.full_url
            return make_response({"success": True})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.delete_log("log-DEL")

        assert captured["method"] == "DELETE"
        assert "id=log-DEL" in captured["url"]

    def test_404_raises_not_found(self, rest_client):
        with urlopen_raising(make_http_error(404)), pytest.raises(FuelogNotFoundError):
            rest_client.delete_log("ghost")


# ---------------------------------------------------------------------------
# Vehicles — list
# ---------------------------------------------------------------------------


class TestListVehicles:
    def test_returns_list_of_vehicles(self, rest_client):
        with urlopen_returning({"vehicles": [SAMPLE_VEHICLE]}):
            vehicles = rest_client.list_vehicles()
        assert len(vehicles) == 1
        assert vehicles[0].id == "vehicle-001"
        assert vehicles[0].fuel_type == "Petrol"

    def test_include_archived_adds_param(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            return make_response({"vehicles": []})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.list_vehicles(include_archived=True)

        assert "includeArchived=true" in captured["url"]

    def test_archived_excluded_by_default(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            return make_response({"vehicles": []})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.list_vehicles()

        assert "includeArchived" not in captured["url"]


# ---------------------------------------------------------------------------
# Vehicles — create
# ---------------------------------------------------------------------------


class TestCreateVehicle:
    def test_returns_new_id(self, rest_client):
        with urlopen_returning({"id": "vehicle-new"}, status=201):
            new_id = rest_client.create_vehicle(
                CreateVehicleRequest(
                    name="Yaris",
                    make="Toyota",
                    model="Yaris",
                    year="2023",
                    fuel_type=FuelType.HYBRID,
                )
            )
        assert new_id == "vehicle-new"

    def test_fuel_type_enum_serialised(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["body"] = json.loads(req.data.decode())
            return make_response({"id": "v1"})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.create_vehicle(
                CreateVehicleRequest(
                    name="Test",
                    make="Test",
                    model="Test",
                    year="2023",
                    fuel_type=FuelType.ELECTRIC,
                )
            )

        assert captured["body"]["fuelType"] == "Electric"


# ---------------------------------------------------------------------------
# Vehicles — update
# ---------------------------------------------------------------------------


class TestUpdateVehicle:
    def test_returns_true_on_success(self, rest_client):
        with urlopen_returning({"success": True}):
            result = rest_client.update_vehicle(
                "vehicle-001", UpdateVehicleRequest(name="New Name")
            )
        assert result is True

    def test_archive_vehicle(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["body"] = json.loads(req.data.decode())
            return make_response({"success": True})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.update_vehicle("v1", UpdateVehicleRequest(is_archived=True))

        assert captured["body"]["isArchived"] is True


# ---------------------------------------------------------------------------
# Vehicles — delete
# ---------------------------------------------------------------------------


class TestDeleteVehicle:
    def test_returns_true_on_success(self, rest_client):
        with urlopen_returning({"success": True}):
            result = rest_client.delete_vehicle("vehicle-001")
        assert result is True

    def test_404_raises_not_found(self, rest_client):
        with urlopen_raising(make_http_error(404)), pytest.raises(FuelogNotFoundError):
            rest_client.delete_vehicle("ghost-vehicle")


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class TestGetAnalytics:
    def test_returns_stats_object(self, rest_client):
        with urlopen_returning(SAMPLE_ANALYTICS):
            stats = rest_client.get_analytics()
        assert stats.log_count == 42
        assert stats.total_spent == 1200.0
        assert stats.home_currency == "EUR"
        assert stats.efficiency == 20.0

    def test_filters_sent_in_url(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            return make_response(SAMPLE_ANALYTICS)

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.get_analytics(
                vehicle_id="v1",
                start_date="2025-01-01",
                end_date="2025-12-31",
            )

        assert "vehicleId=v1" in captured["url"]
        assert "startDate=2025-01-01" in captured["url"]
        assert "endDate=2025-12-31" in captured["url"]

    def test_no_filters_by_default(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            return make_response(SAMPLE_ANALYTICS)

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.get_analytics()

        assert "vehicleId" not in captured["url"]
        assert "startDate" not in captured["url"]

    def test_extra_fields_captured(self, rest_client):
        with urlopen_returning(SAMPLE_ANALYTICS):
            stats = rest_client.get_analytics()
        assert stats.extra.get("extraField") == "extra_value"


# ---------------------------------------------------------------------------
# Auth header
# ---------------------------------------------------------------------------


class TestAuthHeader:
    def test_bearer_token_sent(self, rest_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["auth"] = req.get_header("Authorization")
            return make_response({"logs": []})

        with patch("fuelog.client.urlopen", side_effect=fake_urlopen):
            rest_client.list_logs()

        assert captured["auth"] == "Bearer test-token"


# ---------------------------------------------------------------------------
# Network error
# ---------------------------------------------------------------------------


class TestNetworkError:
    def test_url_error_raises_api_error(self, rest_client):
        from urllib.error import URLError

        from fuelog import FuelogAPIError

        with (
            urlopen_raising(URLError("Connection refused")),
            pytest.raises(FuelogAPIError) as exc_info,
        ):
            rest_client.list_logs()

        assert "Network error" in str(exc_info.value)
