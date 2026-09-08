import time
import httpx
from typing import Dict, Any, List, Optional
from app.traces.collector import TraceCollector
from app.schemas.trace import TraceEventType, HTTPPayload


class ToolDefinition:
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


def get_travel_tools() -> List[ToolDefinition]:
    return [
        ToolDefinition(
            name="search_flights",
            description="Search available flights by origin, destination, and/or max_price.",
            parameters={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin airport code, e.g. DEL"},
                    "destination": {"type": "string", "description": "Destination airport code, e.g. BOM"},
                    "max_price": {"type": "number", "description": "Maximum price in INR"},
                },
            },
        ),
        ToolDefinition(
            name="get_flight",
            description="Get details of a specific flight by flight_id.",
            parameters={
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string", "description": "Flight ID, e.g. FL-101"},
                },
                "required": ["flight_id"],
            },
        ),
        ToolDefinition(
            name="create_reservation",
            description="Book a seat on a flight for a passenger.",
            parameters={
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string", "description": "Flight ID"},
                    "passenger_name": {"type": "string", "description": "Passenger full name"},
                    "idempotency_key": {"type": "string", "description": "Optional unique client key to prevent duplicate booking on retries"},
                },
                "required": ["flight_id", "passenger_name"],
            },
        ),
        ToolDefinition(
            name="get_reservation",
            description="Retrieve an existing reservation by reservation_id.",
            parameters={
                "type": "object",
                "properties": {
                    "reservation_id": {"type": "string", "description": "Reservation ID, e.g. RES-0001"},
                },
                "required": ["reservation_id"],
            },
        ),
    ]


class ToolExecutor:
    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None):
        self.base_url = base_url.rstrip("/")
        self.client = client

    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        trace_collector: TraceCollector,
    ) -> Dict[str, Any]:
        # Record TOOL_CALL in trace
        trace_collector.add_event(
            event_type=TraceEventType.TOOL_CALL,
            tool_name=tool_name,
            tool_arguments=arguments,
        )

        # Map tool to HTTP endpoint
        method = "GET"
        endpoint = ""
        params = {}
        json_body = None

        if tool_name == "search_flights":
            method = "GET"
            endpoint = "/sandbox/flights"
            params = {k: v for k, v in arguments.items() if v is not None}
        elif tool_name == "get_flight":
            flight_id = arguments.get("flight_id", "")
            method = "GET"
            endpoint = f"/sandbox/flights/{flight_id}"
        elif tool_name == "create_reservation":
            method = "POST"
            endpoint = "/sandbox/reservations"
            json_body = {
                "flight_id": arguments.get("flight_id"),
                "passenger_name": arguments.get("passenger_name"),
                "idempotency_key": arguments.get("idempotency_key"),
            }
        elif tool_name == "get_reservation":
            reservation_id = arguments.get("reservation_id", "")
            method = "GET"
            endpoint = f"/sandbox/reservations/{reservation_id}"
        else:
            err_msg = f"Unknown tool: {tool_name}"
            trace_collector.add_event(
                event_type=TraceEventType.ERROR,
                error_message=err_msg,
            )
            return {"error": err_msg, "status_code": 400}

        url = f"{self.base_url}{endpoint}"

        # Record HTTP_REQUEST
        trace_collector.add_event(
            event_type=TraceEventType.HTTP_REQUEST,
            tool_name=tool_name,
            http_payload=HTTPPayload(
                method=method,
                url=url,
                body=json_body or params,
            ),
        )

        start_time = time.time()
        close_client_after = False
        client = self.client
        if client is None:
            client = httpx.AsyncClient()
            close_client_after = True

        try:
            if method == "GET":
                response = await client.get(url, params=params, timeout=10.0)
            elif method == "POST":
                response = await client.post(url, json=json_body, timeout=10.0)
            else:
                raise ValueError(f"Unsupported method {method}")

            duration_ms = (time.time() - start_time) * 1000.0

            try:
                resp_data = response.json()
            except Exception:
                resp_data = response.text

            # Record HTTP_RESPONSE
            trace_collector.add_event(
                event_type=TraceEventType.HTTP_RESPONSE,
                tool_name=tool_name,
                http_payload=HTTPPayload(
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    response_body=resp_data,
                    duration_ms=round(duration_ms, 2),
                ),
            )

            result = {
                "status_code": response.status_code,
                "data": resp_data,
                "is_success": response.is_success,
            }

            trace_collector.add_event(
                event_type=TraceEventType.TOOL_RESULT,
                tool_name=tool_name,
                metadata={"status_code": response.status_code, "is_success": response.is_success},
            )

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000.0
            err_str = str(e)
            trace_collector.add_event(
                event_type=TraceEventType.ERROR,
                tool_name=tool_name,
                error_message=err_str,
                http_payload=HTTPPayload(
                    method=method,
                    url=url,
                    duration_ms=round(duration_ms, 2),
                ),
            )
            return {"error": err_str, "status_code": 500, "is_success": False}
        finally:
            if close_client_after:
                await client.aclose()
