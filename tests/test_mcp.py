"""Unit tests for fuelog.FuelogMCPClient (MCP server)."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from fuelog import FuelogAPIError, FuelogMCPError
from fuelog.models import CostOptimizationPeriod, FuelType, TrendMetric
from tests.conftest import make_http_error, make_response

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOOL_RESPONSE = {
    "content": [{"type": "text", "text": "Tool result text"}],
    "isError": False,
}

PROMPT_RESPONSE = {
    "description": "A test prompt",
    "messages": [
        {"role": "user", "content": {"type": "text", "text": "Report content here"}},
    ],
}


def _rpc_success(result):
    """Build a JSON-RPC 2.0 success envelope."""
    return {"jsonrpc": "2.0", "id": 1, "result": result}


def _rpc_error(code, message):
    """Build a JSON-RPC 2.0 error envelope."""
    return {"jsonrpc": "2.0", "id": 1, "error": {"code": code, "message": message}}


def urlopen_returning(body, status=200):
    return patch("fuelog.mcp.urlopen", return_value=make_response(body, status))


def urlopen_raising(exc):
    return patch("fuelog.mcp.urlopen", side_effect=exc)


# ---------------------------------------------------------------------------
# JSON-RPC transport
# ---------------------------------------------------------------------------


class TestMCPTransport:
    def test_sends_correct_jsonrpc_envelope(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["body"] = json.loads(req.data.decode())
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.list_vehicles()

        body = captured["body"]
        assert body["jsonrpc"] == "2.0"
        assert body["method"] == "tools/call"
        assert "id" in body
        assert body["params"]["name"] == "list_vehicles"

    def test_bearer_token_in_header(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["auth"] = req.get_header("Authorization")
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.list_vehicles()

        assert captured["auth"] == "Bearer test-token"

    def test_rpc_error_raises_mcp_error(self, mcp_client):
        with (
            urlopen_returning(_rpc_error(-32601, "Method not found")),
            pytest.raises(FuelogMCPError) as exc_info,
        ):
            mcp_client.list_vehicles()

        assert exc_info.value.code == -32601
        assert "Method not found" in str(exc_info.value)

    def test_http_error_raises_api_error(self, mcp_client):
        with urlopen_raising(make_http_error(500)), pytest.raises(FuelogAPIError):
            mcp_client.list_vehicles()

    def test_network_error_raises_api_error(self, mcp_client):
        from urllib.error import URLError

        with urlopen_raising(URLError("Connection refused")), pytest.raises(FuelogAPIError):
            mcp_client.list_vehicles()

    def test_ids_are_unique_across_calls(self, mcp_client):
        ids = []

        def fake_urlopen(req, timeout):
            ids.append(json.loads(req.data.decode())["id"])
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.list_vehicles()
            mcp_client.list_vehicles()

        assert len(set(ids)) == 2


# ---------------------------------------------------------------------------
# Tools — list_logs
# ---------------------------------------------------------------------------


class TestMCPListLogs:
    def test_basic_call(self, mcp_client):
        with urlopen_returning(_rpc_success(TOOL_RESPONSE)):
            result = mcp_client.list_logs()
        assert result.text == "Tool result text"
        assert result.is_error is False

    def test_arguments_passed_correctly(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.list_logs(
                limit=25,
                vehicle_id="v1",
                start_date="2025-01-01",
                end_date="2025-12-31",
                brand="Shell",
            )

        args = captured["args"]
        assert args["limit"] == 25
        assert args["vehicleId"] == "v1"
        assert args["startDate"] == "2025-01-01"
        assert args["endDate"] == "2025-12-31"
        assert args["brand"] == "Shell"

    def test_optional_args_omitted_when_none(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.list_logs()

        args = captured["args"]
        assert "vehicleId" not in args
        assert "brand" not in args


# ---------------------------------------------------------------------------
# Tools — log_fuel
# ---------------------------------------------------------------------------


class TestMCPLogFuel:
    def test_required_and_optional_args(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.log_fuel(
                brand="Shell",
                cost=50.0,
                distance_km=400.0,
                fuel_amount_liters=35.0,
                currency="EUR",
                vehicle_id="v1",
                latitude=53.0,
                longitude=-6.0,
            )

        args = captured["args"]
        assert args["brand"] == "Shell"
        assert args["cost"] == 50.0
        assert args["distanceKm"] == 400.0
        assert args["fuelAmountLiters"] == 35.0
        assert args["currency"] == "EUR"
        assert args["vehicleId"] == "v1"
        assert args["latitude"] == 53.0
        assert args["longitude"] == -6.0

    def test_result_returned(self, mcp_client):
        with urlopen_returning(_rpc_success(TOOL_RESPONSE)):
            result = mcp_client.log_fuel(
                brand="BP", cost=30.0, distance_km=200.0, fuel_amount_liters=20.0
            )
        assert result.text == "Tool result text"


# ---------------------------------------------------------------------------
# Tools — edit_fuel_log
# ---------------------------------------------------------------------------


class TestMCPEditFuelLog:
    def test_log_id_required(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.edit_fuel_log("log-001", brand="Texaco", cost=55.0)

        assert captured["args"]["logId"] == "log-001"
        assert captured["args"]["brand"] == "Texaco"
        assert captured["args"]["cost"] == 55.0

    def test_optional_fields_omitted(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.edit_fuel_log("log-001")

        args = captured["args"]
        assert args == {"logId": "log-001"}


# ---------------------------------------------------------------------------
# Tools — delete_fuel_log
# ---------------------------------------------------------------------------


class TestMCPDeleteFuelLog:
    def test_confirm_true_sent_automatically(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.delete_fuel_log("log-001")

        assert captured["args"]["logId"] == "log-001"
        assert captured["args"]["confirm"] is True


# ---------------------------------------------------------------------------
# Tools — list_vehicles
# ---------------------------------------------------------------------------


class TestMCPListVehicles:
    def test_include_archived_default_false(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.list_vehicles()

        assert captured["args"]["includeArchived"] is False

    def test_include_archived_true(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.list_vehicles(include_archived=True)

        assert captured["args"]["includeArchived"] is True


# ---------------------------------------------------------------------------
# Tools — add_vehicle
# ---------------------------------------------------------------------------


class TestMCPAddVehicle:
    def test_fuel_type_enum_serialised(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.add_vehicle(
                name="Yaris",
                make="Toyota",
                model="Yaris",
                year="2023",
                fuel_type=FuelType.HYBRID,
                is_default=True,
            )

        args = captured["args"]
        assert args["fuelType"] == "Hybrid"
        assert args["isDefault"] is True

    def test_fuel_type_string_passthrough(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.add_vehicle(name="X", make="X", model="X", year="2020", fuel_type="Electric")

        assert captured["args"]["fuelType"] == "Electric"


# ---------------------------------------------------------------------------
# Tools — update_vehicle
# ---------------------------------------------------------------------------


class TestMCPUpdateVehicle:
    def test_vehicle_id_required(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.update_vehicle("v1", name="New Name", is_archived=True)

        assert captured["args"]["vehicleId"] == "v1"
        assert captured["args"]["name"] == "New Name"
        assert captured["args"]["isArchived"] is True

    def test_optional_fields_omitted(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.update_vehicle("v1")

        assert captured["args"] == {"vehicleId": "v1"}


# ---------------------------------------------------------------------------
# Tools — get_analytics / compare_vehicles
# ---------------------------------------------------------------------------


class TestMCPAnalytics:
    def test_get_analytics_no_filters(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.get_analytics()

        assert captured["args"] == {}

    def test_get_analytics_with_filters(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.get_analytics(vehicle_id="v1", start_date="2025-01-01")

        assert captured["args"]["vehicleId"] == "v1"
        assert captured["args"]["startDate"] == "2025-01-01"

    def test_compare_vehicles_with_ids(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(TOOL_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.compare_vehicles(vehicle_ids=["v1", "v2"])

        assert captured["args"]["vehicleIds"] == ["v1", "v2"]


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


class TestMCPResources:
    def test_read_resource_sends_correct_uri(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["params"] = json.loads(req.data.decode())["params"]
            return make_response(_rpc_success({"data": "resource content"}))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.read_resource("fuelog://logs")

        assert captured["params"]["uri"] == "fuelog://logs"

    def test_convenience_resource_methods(self, mcp_client):
        """All helper resource methods call read_resource with the right URI."""
        expectations = {
            "get_all_logs_resource": "fuelog://logs",
            "get_vehicles_resource": "fuelog://vehicles",
            "get_analytics_summary_resource": "fuelog://analytics/summary",
            "get_analytics_monthly_resource": "fuelog://analytics/monthly",
            "get_analytics_vehicles_resource": "fuelog://analytics/vehicles",
            "get_profile_resource": "fuelog://profile",
        }
        for method_name, expected_uri in expectations.items():
            captured = {}

            def fake_urlopen(req, timeout, _uri=expected_uri, _captured=captured):
                _captured["uri"] = json.loads(req.data.decode())["params"]["uri"]
                return make_response(_rpc_success({}))

            with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
                getattr(mcp_client, method_name)()

            assert captured["uri"] == expected_uri, f"Failed for {method_name}"

    def test_get_log_resource(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["uri"] = json.loads(req.data.decode())["params"]["uri"]
            return make_response(_rpc_success({}))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.get_log_resource("log-123")

        assert captured["uri"] == "fuelog://logs/log-123"

    def test_get_vehicle_resource(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["uri"] = json.loads(req.data.decode())["params"]["uri"]
            return make_response(_rpc_success({}))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.get_vehicle_resource("v-abc")

        assert captured["uri"] == "fuelog://vehicles/v-abc"


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


class TestMCPPrompts:
    def test_monthly_report_prompt(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            payload = json.loads(req.data.decode())
            captured["method"] = payload["method"]
            captured["params"] = payload["params"]
            return make_response(_rpc_success(PROMPT_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            result = mcp_client.monthly_report("2025-03", vehicle_id="v1")

        assert captured["method"] == "prompts/get"
        assert captured["params"]["name"] == "monthly_report"
        assert captured["params"]["arguments"]["month"] == "2025-03"
        assert captured["params"]["arguments"]["vehicleId"] == "v1"
        assert result.description == "A test prompt"
        assert result.messages[0].role == "user"

    def test_trend_analysis_prompt_with_metric_enum(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(PROMPT_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.trend_analysis(
                start_date="2025-01-01",
                end_date="2025-12-31",
                metric=TrendMetric.KML,
            )

        assert captured["args"]["startDate"] == "2025-01-01"
        assert captured["args"]["endDate"] == "2025-12-31"
        assert captured["args"]["metric"] == "kml"

    def test_trend_analysis_prompt_with_metric_string(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(PROMPT_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.trend_analysis(start_date="2025-01-01", end_date="2025-12-31", metric="mpg")

        assert captured["args"]["metric"] == "mpg"

    def test_cost_optimization_default_period(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(PROMPT_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.cost_optimization()

        # No period argument sent when not specified
        assert "period" not in captured["args"]

    def test_cost_optimization_with_period_enum(self, mcp_client):
        captured = {}

        def fake_urlopen(req, timeout):
            captured["args"] = json.loads(req.data.decode())["params"]["arguments"]
            return make_response(_rpc_success(PROMPT_RESPONSE))

        with patch("fuelog.mcp.urlopen", side_effect=fake_urlopen):
            mcp_client.cost_optimization(period=CostOptimizationPeriod.LAST_YEAR)

        assert captured["args"]["period"] == "last_year"
