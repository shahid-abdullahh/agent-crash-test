import uuid
from typing import Dict, Any, List, Optional
from app.agent.base import BaseAgent
from app.agent.tools import ToolDefinition, ToolExecutor
from app.schemas.task import Task
from app.schemas.trace import TraceEventType
from app.traces.collector import TraceCollector


class DeterministicTravelAgent(BaseAgent):
    """
    Deterministic Agent that accurately models decision logic for travel tasks.
    Supports both unsafe retry behavior (reproducing crash vulnerability) and safe retry.
    """
    def __init__(self, retry_policy: str = "unsafe_retry"):
        self.retry_policy = retry_policy  # "unsafe_retry" or "idempotent_retry"

    async def run(
        self,
        task: Task,
        tools: List[ToolDefinition],
        tool_executor: ToolExecutor,
        trace_collector: TraceCollector,
    ) -> Dict[str, Any]:
        trace_collector.add_event(
            event_type=TraceEventType.AGENT_START,
            metadata={"task_id": task.id, "policy": self.retry_policy},
        )

        trace_collector.add_event(
            event_type=TraceEventType.AGENT_THINKING,
            metadata={"thought": f"Goal: {task.description}. Step 1: Searching for flights matching constraints."},
        )

        # Step 1: Search flights
        search_args = {
            "origin": task.constraints.origin,
            "destination": task.constraints.destination,
            "max_price": task.constraints.max_price,
        }
        search_res = await tool_executor.execute("search_flights", search_args, trace_collector)

        flights = search_res.get("data", [])
        if not isinstance(flights, list) or len(flights) == 0:
            msg = "No flights found matching constraints."
            trace_collector.add_event(
                event_type=TraceEventType.AGENT_OUTPUT,
                metadata={"final_answer": msg, "success": False},
            )
            return {"success": False, "message": msg}

        # Step 2: Choose best flight
        best_flight = min(flights, key=lambda x: x.get("price", float("inf")))
        flight_id = best_flight["flight_id"]

        trace_collector.add_event(
            event_type=TraceEventType.AGENT_THINKING,
            metadata={
                "thought": f"Selected cheapest flight {flight_id} at price {best_flight['price']}. Inspecting flight details."
            },
        )

        # Step 3: Get flight details
        flight_res = await tool_executor.execute("get_flight", {"flight_id": flight_id}, trace_collector)
        if not flight_res.get("is_success"):
            msg = f"Failed to retrieve flight {flight_id}"
            trace_collector.add_event(
                event_type=TraceEventType.AGENT_OUTPUT,
                metadata={"final_answer": msg, "success": False},
            )
            return {"success": False, "message": msg}

        passenger_name = task.constraints.passenger_name or "Test Traveler"
        idempotency_key = str(uuid.uuid4()) if self.retry_policy == "idempotent_retry" else None

        trace_collector.add_event(
            event_type=TraceEventType.AGENT_THINKING,
            metadata={
                "thought": f"Proceeding to create reservation for flight {flight_id} under passenger {passenger_name}."
            },
        )

        # Step 4: Create reservation
        booking_args = {
            "flight_id": flight_id,
            "passenger_name": passenger_name,
            "idempotency_key": idempotency_key,
        }
        res_result = await tool_executor.execute("create_reservation", booking_args, trace_collector)

        # Step 5: Handle potential failure / timeout / retry
        if not res_result.get("is_success"):
            status_code = res_result.get("status_code", 500)
            trace_collector.add_event(
                event_type=TraceEventType.AGENT_THINKING,
                metadata={
                    "thought": f"Booking request failed with status {status_code}. Initiating retry as task is not yet confirmed."
                },
            )

            # Unsafe or safe retry
            retry_args = {
                "flight_id": flight_id,
                "passenger_name": passenger_name,
                "idempotency_key": idempotency_key,  # if idempotent, will pass the same key; if unsafe, None
            }
            res_result = await tool_executor.execute("create_reservation", retry_args, trace_collector)

        if res_result.get("is_success"):
            res_data = res_result.get("data", {})
            final_res_id = res_data.get("reservation_id") if isinstance(res_data, dict) else None
            out = {
                "success": True,
                "reservation_id": final_res_id,
                "flight_id": flight_id,
                "price_paid": best_flight.get("price"),
                "passenger_name": passenger_name,
            }
        else:
            out = {
                "success": False,
                "error": res_result.get("error") or res_result.get("data"),
            }

        trace_collector.add_event(
            event_type=TraceEventType.AGENT_OUTPUT,
            metadata={"final_output": out},
        )

        return out
