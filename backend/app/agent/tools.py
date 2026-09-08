import time
import httpx
from typing import Dict, Any, List, Optional
from app.traces.collector import TraceCollector
from app.schemas.trace import TraceEventType, HTTPPayload


class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        method: str = "GET",
        path: str = "",
        path_param_names: Optional[List[str]] = None,
        query_param_names: Optional[List[str]] = None,
        request_body_schema: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.method = method.upper()
        self.path = path
        self.path_param_names = path_param_names or []
        self.query_param_names = query_param_names or []
        self.request_body_schema = request_body_schema

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "method": self.method,
            "path": self.path,
            "parameters": self.parameters,
            "path_param_names": self.path_param_names,
            "query_param_names": self.query_param_names,
            "request_body_schema": self.request_body_schema,
        }


def get_travel_tools() -> List[ToolDefinition]:
    """Generate standardized travel tools dynamically from FastAPI sandbox OpenAPI spec."""
    from app.main import app
    from app.openapi.generator import OpenAPIToolGenerator

    # Generate tools directly from the live OpenAPI schema
    generator = OpenAPIToolGenerator(app.openapi())
    tools = generator.generate_tools(path_prefix="/sandbox")
    
    # Filter out administrative sandbox state endpoints (reset, configure, state)
    # Keeping the domain business operations for the agent
    allowed_operations = {"search_flights", "get_flight", "create_reservation", "get_reservation"}
    return [t for t in tools if t.name in allowed_operations]


class ToolExecutor:
    """Executes OpenAPI-driven ToolDefinitions via real HTTP requests."""

    def __init__(
        self,
        base_url: str,
        client: Optional[httpx.AsyncClient] = None,
        tools: Optional[List[ToolDefinition]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.client = client
        self.tools_map: Dict[str, ToolDefinition] = {t.name: t for t in (tools or [])}

    def register_tools(self, tools: List[ToolDefinition]):
        for tool in tools:
            self.tools_map[tool.name] = tool

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

        # Dynamic tool resolution
        tool_def = self.tools_map.get(tool_name)
        if tool_def:
            method = tool_def.method
            endpoint = tool_def.path

            # Format path parameters (e.g. /sandbox/flights/{flight_id})
            params = {}
            json_body = {}
            for k, v in arguments.items():
                if v is None:
                    continue
                if k in tool_def.path_param_names:
                    endpoint = endpoint.replace(f"{{{k}}}", str(v))
                elif k in tool_def.query_param_names:
                    params[k] = v
                else:
                    json_body[k] = v

            if method == "GET" and not params and json_body:
                # If GET and parameters weren't explicitly marked query, treat non-path args as query
                params = json_body
                json_body = None
            elif method != "GET" and not json_body:
                json_body = None
        else:
            # Fallback mapping for backward compatibility if tool not in registry
            if tool_name == "search_flights":
                method = "GET"
                endpoint = "/sandbox/flights"
                params = {k: v for k, v in arguments.items() if v is not None}
                json_body = None
            elif tool_name == "get_flight":
                flight_id = arguments.get("flight_id", "")
                method = "GET"
                endpoint = f"/sandbox/flights/{flight_id}"
                params = {}
                json_body = None
            elif tool_name == "create_reservation":
                method = "POST"
                endpoint = "/sandbox/reservations"
                params = {}
                json_body = {
                    "flight_id": arguments.get("flight_id"),
                    "passenger_name": arguments.get("passenger_name"),
                    "idempotency_key": arguments.get("idempotency_key"),
                }
            elif tool_name == "get_reservation":
                reservation_id = arguments.get("reservation_id", "")
                method = "GET"
                endpoint = f"/sandbox/reservations/{reservation_id}"
                params = {}
                json_body = None
            else:
                err_msg = f"Unknown tool: {tool_name}"
                trace_collector.add_event(
                    event_type=TraceEventType.ERROR,
                    error_message=err_msg,
                )
                return {"error": err_msg, "status_code": 400, "is_success": False}

        url = f"{self.base_url}{endpoint}"

        # Record HTTP_REQUEST
        trace_collector.add_event(
            event_type=TraceEventType.HTTP_REQUEST,
            tool_name=tool_name,
            http_payload=HTTPPayload(
                method=method,
                url=url,
                body=json_body if json_body is not None else params,
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
            elif method == "PUT":
                response = await client.put(url, json=json_body, timeout=10.0)
            elif method == "DELETE":
                response = await client.delete(url, params=params, timeout=10.0)
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
