import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.schemas.trace import TraceEvent, TraceEventType, HTTPPayload


class TraceCollector:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.events: List[TraceEvent] = []
        self._sequence_counter = 1

    def add_event(
        self,
        event_type: TraceEventType,
        tool_name: Optional[str] = None,
        tool_arguments: Optional[Dict[str, Any]] = None,
        http_payload: Optional[HTTPPayload] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TraceEvent:
        event = TraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=self.run_id,
            sequence_number=self._sequence_counter,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            tool_name=tool_name,
            tool_arguments=tool_arguments,
            http_payload=http_payload,
            error_message=error_message,
            metadata=metadata,
        )
        self._sequence_counter += 1
        self.events.append(event)
        return event

    def get_events(self) -> List[TraceEvent]:
        return list(self.events)
