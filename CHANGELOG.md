# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-03-09

### Added
- `FuelogClient` — synchronous REST API client covering logs, vehicles, and analytics.
- `FuelogMCPClient` — MCP server client covering all registered tools, resources, and prompts.
- Typed dataclass models: `FuelLog`, `Vehicle`, `AnalyticsStats`, `MCPToolResult`, `MCPPromptResult`, and associated request types.
- Enumerations: `FuelType`, `TrendMetric`, `CostOptimizationPeriod`.
- Typed exception hierarchy: `FuelogError` → `FuelogAPIError` → sub-classes per HTTP status code; `FuelogMCPError` for JSON-RPC errors.
- Full unit test suite with ≥ 90 % branch coverage.
- PyPI packaging via Hatchling with OIDC Trusted Publishing workflow.
- GitHub Actions CI across Python 3.9 – 3.12 with Codecov integration.
- Ruff linting/formatting and mypy strict type-checking in CI.
- Zero third-party runtime dependencies.
