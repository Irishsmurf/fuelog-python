# fuelog-python

[![CI](https://github.com/Irishsmurf/fuelog-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Irishsmurf/fuelog-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Irishsmurf/fuelog-python/branch/main/graph/badge.svg)](https://codecov.io/gh/Irishsmurf/fuelog-python)
[![PyPI version](https://badge.fury.io/py/fuelog.svg)](https://badge.fury.io/py/fuelog)
[![Python versions](https://img.shields.io/pypi/pyversions/fuelog.svg)](https://pypi.org/project/fuelog/)
[![Docs](https://readthedocs.org/projects/fuelog-python/badge/?version=latest)](https://fuelog-python.readthedocs.io/en/latest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Official Python client library for the [Fuelog](https://fuelog.paddez.com/) API.

Covers the full **REST API** *and* the **MCP (Model Context Protocol) server** — with zero
third-party dependencies, typed models, and a comprehensive test suite.

---

## Installation

```bash
pip install fuelog
```

Requires **Python 3.9+**.  No external dependencies.

---

## Quick Start

### REST Client

```python
from fuelog import FuelogClient, CreateFuelLogRequest, CreateVehicleRequest, FuelType

client = FuelogClient(token="your_bearer_token")

# ── Logs ───────────────────────────────────────────────────────────────────

# List the 20 most recent fill-ups
logs = client.list_logs(limit=20)
for log in logs:
    print(f"{log.timestamp}  {log.brand}  €{log.cost}  {log.distance_km} km")

# Create a new fill-up
new_id = client.create_log(
    CreateFuelLogRequest(
        brand="Shell",
        cost=50.00,
        distance_km=400.0,
        fuel_amount_liters=35.0,
        vehicle_id="vehicle-abc",
    )
)
print(f"Created log: {new_id}")

# Update a log
from fuelog import UpdateFuelLogRequest
client.update_log(new_id, UpdateFuelLogRequest(brand="Shell Express", cost=51.00))

# Delete a log
client.delete_log(new_id)

# ── Vehicles ───────────────────────────────────────────────────────────────

vehicles = client.list_vehicles()

vehicle_id = client.create_vehicle(
    CreateVehicleRequest(
        name="My Corolla",
        make="Toyota",
        model="Corolla",
        year="2022",
        fuel_type=FuelType.PETROL,
        is_default=True,
    )
)

from fuelog import UpdateVehicleRequest
client.update_vehicle(vehicle_id, UpdateVehicleRequest(name="Daily Driver"))
client.delete_vehicle(vehicle_id)

# Include archived vehicles
all_vehicles = client.list_vehicles(include_archived=True)

# ── Analytics ──────────────────────────────────────────────────────────────

stats = client.get_analytics(
    vehicle_id="vehicle-abc",
    start_date="2025-01-01",
    end_date="2025-12-31",
)
print(f"Avg efficiency: {stats.efficiency} km/L")
print(f"Total spent:    {stats.home_currency} {stats.total_spent}")
```

---

### MCP Client

The MCP client wraps all tools, resources, and prompts registered on the
`/api/mcp` endpoint.

```python
from fuelog import FuelogMCPClient, FuelType, TrendMetric, CostOptimizationPeriod

mcp = FuelogMCPClient(token="your_bearer_token")

# ── Tools ──────────────────────────────────────────────────────────────────

# List logs (with optional filters)
result = mcp.list_logs(limit=10, brand="Shell")
print(result.text)

# Log a fill-up
result = mcp.log_fuel(
    brand="BP",
    cost=45.0,
    distance_km=300.0,
    fuel_amount_liters=28.0,
    vehicle_id="v1",
)

# Edit and delete
mcp.edit_fuel_log("log-id", cost=46.0)
mcp.delete_fuel_log("log-id")  # confirm=True added automatically

# Vehicles
mcp.add_vehicle(name="EV", make="Tesla", model="Model 3", year="2024",
                fuel_type=FuelType.ELECTRIC, is_default=True)
mcp.update_vehicle("v1", is_archived=True)

# Analytics
result = mcp.get_analytics(vehicle_id="v1")
result = mcp.compare_vehicles(vehicle_ids=["v1", "v2"])

# ── Resources ──────────────────────────────────────────────────────────────

summary = mcp.get_analytics_summary_resource()
monthly = mcp.get_analytics_monthly_resource()
profile = mcp.get_profile_resource()

# By ID
log_data    = mcp.get_log_resource("log-123")
vehicle_data = mcp.get_vehicle_resource("v-abc")

# Raw URI access
data = mcp.read_resource("fuelog://analytics/vehicles")

# ── Prompts ────────────────────────────────────────────────────────────────

# Monthly report for March 2025
prompt = mcp.monthly_report(month="2025-03")
for msg in prompt.messages:
    print(f"[{msg.role}]", msg.content.get("text", ""))

# Trend analysis
prompt = mcp.trend_analysis(
    start_date="2025-01-01",
    end_date="2025-12-31",
    metric=TrendMetric.KML,
)

# Cost optimisation suggestions
prompt = mcp.cost_optimization(period=CostOptimizationPeriod.LAST_QUARTER)
```

---

## Error Handling

All errors derive from `FuelogError`:

| Exception                | When it's raised                                  |
|--------------------------|---------------------------------------------------|
| `FuelogAuthError`        | `401 Unauthorized` — invalid or missing token     |
| `FuelogForbiddenError`   | `403 Forbidden` — token lacks the required scope  |
| `FuelogNotFoundError`    | `404 Not Found` — resource doesn't exist          |
| `FuelogValidationError`  | `422 Unprocessable` — bad request body            |
| `FuelogRateLimitError`   | `429 Too Many Requests`                           |
| `FuelogServerError`      | `5xx` server-side error                           |
| `FuelogAPIError`         | Any other HTTP error (base class for the above)   |
| `FuelogMCPError`         | JSON-RPC error from the MCP server                |

```python
from fuelog import FuelogClient, FuelogNotFoundError, FuelogForbiddenError

client = FuelogClient(token="sk-...")

try:
    client.delete_log("non-existent-id")
except FuelogNotFoundError:
    print("Log not found")
except FuelogForbiddenError as e:
    print(f"Permission denied: {e}")
```

---

## Configuration

```python
client = FuelogClient(
    token="your_token",
    base_url="https://api.fuelog.app",  # default
    timeout=30,                          # seconds, default
)
```

---

## Development

```bash
# Clone and install in editable mode with dev dependencies
git clone https://github.com/Irishsmurf/fuelog-python.git
cd fuelog-python
pip install -e ".[dev]"

# Run the test suite with coverage
pytest --cov=fuelog --cov-report=term-missing

# Lint
ruff check fuelog/ tests/

# Type check
mypy fuelog/

# Build for release
pip install hatch
hatch build
```

---

## Publishing to PyPI

Releases are published automatically via GitHub Actions when a GitHub Release
is created.  The workflow uses [OIDC Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
— no PyPI API token is stored in repository secrets.

To set up a new repo:

1. Create a Trusted Publisher on [pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/) pointing to this repository.
2. Tag a release: `git tag vX.Y.Z && git push --tags`.
3. Create a GitHub Release from the tag — the `publish.yml` workflow triggers automatically.

---

## License

[MIT](LICENSE)
