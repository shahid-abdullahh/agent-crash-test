import pytest
from app.traces.collector import TraceCollector
from app.schemas.trace import TraceEventType, HTTPPayload


def test_trace_collector_ordering_and_monotonic_sequence():
    collector = TraceCollector(run_id="run-test-123")

    ev1 = collector.add_event(event_type=TraceEventType.AGENT_START)
    ev2 = collector.add_event(
        event_type=TraceEventType.TOOL_CALL,
        tool_name="search_flights",
        tool_arguments={"origin": "DEL", "destination": "BOM"},
    )
    ev3 = collector.add_event(
        event_type=TraceEventType.HTTP_REQUEST,
        http_payload=HTTPPayload(
            method="GET",
            url="http://testserver/sandbox/flights?origin=DEL&destination=BOM",
        ),
    )
    ev4 = collector.add_event(
        event_type=TraceEventType.HTTP_RESPONSE,
        http_payload=HTTPPayload(
            method="GET",
            url="http://testserver/sandbox/flights",
            status_code=200,
            duration_ms=12.5,
        ),
    )

    events = collector.get_events()
    assert len(events) == 4
    assert [e.sequence_number for e in events] == [1, 2, 3, 4]
    assert all(e.run_id == "run-test-123" for e in events)
    assert events[0].event_type == TraceEventType.AGENT_START
    assert events[1].tool_name == "search_flights"
    assert events[3].http_payload.status_code == 200
