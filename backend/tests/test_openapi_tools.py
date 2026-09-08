import pytest
import httpx
from app.main import app
from app.openapi.generator import OpenAPIToolGenerator
from app.agent.tools import ToolExecutor, get_travel_tools
from app.traces.collector import TraceCollector


def test_sandbox_openapi_schema_available():
    schema = app.openapi()
    assert isinstance(schema, dict)
    assert "paths" in schema
    assert "/sandbox/flights" in schema["paths"]
    assert "/sandbox/flights/{flight_id}" in schema["paths"]
    assert "/sandbox/reservations" in schema["paths"]


def test_openapi_tool_generation_semantics():
    schema = app.openapi()
    generator = OpenAPIToolGenerator(schema)
    tools = generator.generate_tools(path_prefix="/sandbox")
    tool_map = {t.name: t for t in tools}

    # 1. Verify GET tools generated
    assert "search_flights" in tool_map
    search_tool = tool_map["search_flights"]
    assert search_tool.method == "GET"
    assert search_tool.path == "/sandbox/flights"
    assert "origin" in search_tool.parameters["properties"]
    assert "destination" in search_tool.parameters["properties"]
    assert "max_price" in search_tool.parameters["properties"]
    assert "origin" in search_tool.query_param_names

    # 2. Verify Path Parameter tool
    assert "get_flight" in tool_map
    get_flight_tool = tool_map["get_flight"]
    assert get_flight_tool.method == "GET"
    assert get_flight_tool.path == "/sandbox/flights/{flight_id}"
    assert "flight_id" in get_flight_tool.path_param_names
    assert "flight_id" in get_flight_tool.parameters["required"]

    # 3. Verify POST Request Body tool
    assert "create_reservation" in tool_map
    create_res_tool = tool_map["create_reservation"]
    assert create_res_tool.method == "POST"
    assert create_res_tool.path == "/sandbox/reservations"
    assert "flight_id" in create_res_tool.parameters["properties"]
    assert "passenger_name" in create_res_tool.parameters["properties"]
    assert "idempotency_key" in create_res_tool.parameters["properties"]
    assert "flight_id" in create_res_tool.parameters["required"]
    assert "passenger_name" in create_res_tool.parameters["required"]


@pytest.mark.asyncio
async def test_dynamic_execution_of_generated_tools(async_client: httpx.AsyncClient):
    tools = get_travel_tools()
    executor = ToolExecutor(base_url="http://testserver", client=async_client, tools=tools)
    collector = TraceCollector(run_id="run-openapi-test")

    # 1. Execute GET query
    search_res = await executor.execute(
        "search_flights",
        {"origin": "DEL", "destination": "BOM", "max_price": 8000},
        collector,
    )
    assert search_res["is_success"] is True
    assert len(search_res["data"]) == 1
    assert search_res["data"][0]["flight_id"] == "FL-101"

    # 2. Execute GET path parameter
    flight_res = await executor.execute(
        "get_flight",
        {"flight_id": "FL-101"},
        collector,
    )
    assert flight_res["is_success"] is True
    assert flight_res["data"]["flight_id"] == "FL-101"

    # 3. Execute POST body
    book_res = await executor.execute(
        "create_reservation",
        {"flight_id": "FL-101", "passenger_name": "Test OpenAPI User"},
        collector,
    )
    assert book_res["is_success"] is True
    assert book_res["data"]["passenger_name"] == "Test OpenAPI User"
    assert book_res["data"]["reservation_id"].startswith("RES-")

    # Verify Trace recorded dynamic executions
    events = collector.get_events()
    assert len(events) >= 9
    http_events = [e for e in events if e.http_payload]
    assert any(e.http_payload.url.endswith("/sandbox/flights") for e in http_events)
    assert any(e.http_payload.url.endswith("/sandbox/flights/FL-101") for e in http_events)
    assert any(e.http_payload.url.endswith("/sandbox/reservations") for e in http_events)
