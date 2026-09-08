import React, { useState } from 'react';
import {
  FileText,
  ChevronDown,
  ChevronRight,
  Terminal,
  Globe,
  AlertCircle,
  Lightbulb,
  CheckCircle,
} from 'lucide-react';
import type { TraceEvent, TraceEventType } from '../types';

interface TraceViewerProps {
  events: TraceEvent[];
}

export const TraceViewer: React.FC<TraceViewerProps> = ({ events }) => {
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpandedEvents((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const getBadge = (type: TraceEventType) => {
    switch (type) {
      case 'agent_start':
        return {
          label: 'AGENT START',
          color: 'bg-slate-800 text-slate-300 border-slate-700',
          icon: Terminal,
        };
      case 'agent_thinking':
        return {
          label: 'AGENT THOUGHT',
          color: 'bg-amber-950/70 text-amber-300 border-amber-800/60',
          icon: Lightbulb,
        };
      case 'tool_call':
        return {
          label: 'TOOL CALL',
          color: 'bg-sky-950/70 text-sky-300 border-sky-800/60',
          icon: Terminal,
        };
      case 'http_request':
        return {
          label: 'HTTP REQ',
          color: 'bg-purple-950/70 text-purple-300 border-purple-800/60',
          icon: Globe,
        };
      case 'http_response':
        return {
          label: 'HTTP RESP',
          color: 'bg-emerald-950/70 text-emerald-300 border-emerald-800/60',
          icon: Globe,
        };
      case 'tool_result':
        return {
          label: 'TOOL RESULT',
          color: 'bg-cyan-950/70 text-cyan-300 border-cyan-800/60',
          icon: CheckCircle,
        };
      case 'agent_output':
        return {
          label: 'AGENT OUTPUT',
          color: 'bg-teal-950/70 text-teal-300 border-teal-800/60',
          icon: CheckCircle,
        };
      case 'error':
        return {
          label: 'ERROR',
          color: 'bg-rose-950/80 text-rose-300 border-rose-800/80 animate-pulse',
          icon: AlertCircle,
        };
      default:
        return {
          label: String(type).toUpperCase(),
          color: 'bg-slate-800 text-slate-400 border-slate-700',
          icon: FileText,
        };
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <h2 className="text-sm font-semibold tracking-wider text-slate-200 uppercase flex items-center gap-2">
          <FileText className="w-4 h-4 text-sky-400" />
          Chronological Trace Evidence ({events.length} Events)
        </h2>
        <span className="text-xs text-slate-500 font-mono">Live Monotonic Execution Stream</span>
      </div>

      <div className="space-y-2">
        {events.map((ev) => {
          const badge = getBadge(ev.event_type);
          const hasPayload = Boolean(
            ev.http_payload ||
            ev.tool_arguments ||
            ev.metadata ||
            ev.error_message
          );
          const isExpanded = Boolean(expandedEvents[ev.event_id]);

          return (
            <div
              key={ev.event_id}
              className={`border rounded-lg transition-colors ${
                ev.event_type === 'error'
                  ? 'border-rose-900/60 bg-rose-950/10'
                  : ev.http_payload && ev.http_payload.status_code && ev.http_payload.status_code >= 400
                  ? 'border-rose-800/40 bg-rose-950/10'
                  : 'border-slate-800/80 bg-slate-950/60 hover:border-slate-700'
              }`}
            >
              {/* Event Header */}
              <div
                onClick={() => hasPayload && toggleExpand(ev.event_id)}
                className={`p-3 flex items-center justify-between text-xs cursor-pointer select-none ${
                  hasPayload ? 'hover:bg-slate-900/40' : ''
                }`}
              >
                <div className="flex items-center space-x-3 overflow-hidden">
                  <span className="font-mono text-[11px] text-slate-500 w-6 shrink-0">
                    {String(ev.sequence_number).padStart(2, '0')}
                  </span>

                  <span
                    className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded border shrink-0 ${badge.color}`}
                  >
                    {badge.label}
                  </span>

                  {ev.tool_name && (
                    <span className="font-mono text-xs font-semibold text-slate-200 shrink-0">
                      {ev.tool_name}()
                    </span>
                  )}

                  {ev.http_payload && (
                    <span className="font-mono text-xs text-slate-300 truncate">
                      <span className="text-purple-400 font-bold">{ev.http_payload.method}</span>{' '}
                      {ev.http_payload.url.replace(/^https?:\/\/[^/]+/, '')}
                    </span>
                  )}

                  {ev.metadata?.thought && (
                    <span className="text-xs text-amber-300/90 italic truncate">
                      "{ev.metadata.thought}"
                    </span>
                  )}

                  {ev.error_message && (
                    <span className="text-xs text-rose-400 font-mono truncate">
                      {ev.error_message}
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-3 shrink-0">
                  {ev.http_payload?.status_code && (
                    <span
                      className={`font-mono text-xs font-bold px-2 py-0.5 rounded ${
                        ev.http_payload.status_code >= 500
                          ? 'bg-rose-900 text-rose-200'
                          : ev.http_payload.status_code >= 400
                          ? 'bg-amber-900 text-amber-200'
                          : 'bg-emerald-950 text-emerald-300 border border-emerald-800/40'
                      }`}
                    >
                      HTTP {ev.http_payload.status_code}
                    </span>
                  )}

                  {ev.http_payload?.duration_ms !== undefined && (
                    <span className="font-mono text-[11px] text-slate-500">
                      {ev.http_payload.duration_ms}ms
                    </span>
                  )}

                  {hasPayload && (
                    <div className="text-slate-500">
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Expandable Payload Body */}
              {isExpanded && (
                <div className="px-3 pb-3 pt-1 border-t border-slate-900 text-[11px] font-mono space-y-2 bg-slate-950">
                  {ev.tool_arguments && Object.keys(ev.tool_arguments).length > 0 && (
                    <div>
                      <span className="text-slate-500 block uppercase text-[10px]">
                        Tool Arguments:
                      </span>
                      <pre className="mt-1 p-2 bg-slate-900 rounded border border-slate-800 text-slate-300 overflow-x-auto">
                        {JSON.stringify(ev.tool_arguments, null, 2)}
                      </pre>
                    </div>
                  )}

                  {ev.http_payload?.body && (
                    <div>
                      <span className="text-slate-500 block uppercase text-[10px]">
                        HTTP Request Payload:
                      </span>
                      <pre className="mt-1 p-2 bg-slate-900 rounded border border-slate-800 text-slate-300 overflow-x-auto">
                        {JSON.stringify(ev.http_payload.body, null, 2)}
                      </pre>
                    </div>
                  )}

                  {ev.http_payload?.response_body && (
                    <div>
                      <span className="text-slate-500 block uppercase text-[10px]">
                        HTTP Response Body:
                      </span>
                      <pre className="mt-1 p-2 bg-slate-900 rounded border border-slate-800 text-slate-300 overflow-x-auto">
                        {typeof ev.http_payload.response_body === 'string'
                          ? ev.http_payload.response_body
                          : JSON.stringify(ev.http_payload.response_body, null, 2)}
                      </pre>
                    </div>
                  )}

                  {ev.metadata && Object.keys(ev.metadata).length > 0 && (
                    <div>
                      <span className="text-slate-500 block uppercase text-[10px]">
                        Event Metadata:
                      </span>
                      <pre className="mt-1 p-2 bg-slate-900 rounded border border-slate-800 text-slate-400 overflow-x-auto">
                        {JSON.stringify(ev.metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
