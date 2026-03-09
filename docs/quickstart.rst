Quick Start
===========

Installation
------------

.. code-block:: bash

   pip install fuelog

Requires Python 3.9+ and has **no third-party dependencies**.

REST Client
-----------

.. code-block:: python

   from fuelog import FuelogClient, CreateFuelLogRequest, FuelType

   client = FuelogClient(token="your_bearer_token")

   # List recent fill-ups
   logs = client.list_logs(limit=20)
   for log in logs:
       print(f"{log.timestamp}  {log.brand}  €{log.cost}  {log.distance_km} km")

   # Create a fill-up
   new_id = client.create_log(
       CreateFuelLogRequest(
           brand="Shell",
           cost=50.00,
           distance_km=400.0,
           fuel_amount_liters=35.0,
       )
   )

   # Analytics
   stats = client.get_analytics(start_date="2025-01-01", end_date="2025-12-31")
   print(f"Avg efficiency: {stats.efficiency} km/L")
   print(f"Total spent:    {stats.home_currency} {stats.total_spent}")

MCP Client
----------

.. code-block:: python

   from fuelog import FuelogMCPClient, TrendMetric, CostOptimizationPeriod

   mcp = FuelogMCPClient(token="your_bearer_token")

   # Call a tool
   result = mcp.list_logs(limit=10, brand="Shell")
   print(result.text)

   # Read a resource
   summary = mcp.get_analytics_summary_resource()

   # Get a prompt
   prompt = mcp.monthly_report(month="2025-03")
   for msg in prompt.messages:
       print(f"[{msg.role}]", msg.content.get("text", ""))

Error Handling
--------------

All exceptions derive from :exc:`~fuelog.FuelogError`:

.. code-block:: python

   from fuelog import FuelogClient, FuelogNotFoundError, FuelogForbiddenError

   client = FuelogClient(token="sk-...")

   try:
       client.delete_log("non-existent-id")
   except FuelogNotFoundError:
       print("Log not found")
   except FuelogForbiddenError as e:
       print(f"Permission denied: {e}")

See :doc:`exceptions` for the full exception hierarchy.

Configuration
-------------

.. code-block:: python

   client = FuelogClient(
       token="your_token",
       base_url="https://api.fuelog.app",  # default
       timeout=30,                          # seconds, default
   )
