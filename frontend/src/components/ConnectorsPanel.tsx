import React from 'react';
import { Network, Layers } from 'lucide-react';
import type { ConnectorDefinition } from '../types';

interface ConnectorsPanelProps {
  connectors: ConnectorDefinition[];
}

export const ConnectorsPanel: React.FC<ConnectorsPanelProps> = ({ connectors }) => {
  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-1">
        <div className="flex items-center space-x-2">
          <Network className="w-5 h-5 text-teal-400" />
          <h2 className="text-base font-bold text-white tracking-wide">
            Multi-Service Connector Framework
          </h2>
        </div>
        <p className="text-xs text-slate-400">
          Lightweight service connector instances enabling autonomous agents to coordinate multi-service workflows (Flight Search → Reservation → Payment) under active fault monitoring.
        </p>
      </div>

      {/* Multi-Service Architecture Flow Visualizer */}
      <div className="p-4 bg-slate-950 rounded-xl border border-slate-800/80 space-y-3">
        <span className="text-xs font-bold text-slate-400 uppercase font-mono tracking-wider">
          Multi-Service Autonomous Coordination Loop:
        </span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="p-3 bg-slate-900/80 border border-sky-900/40 rounded-lg text-xs space-y-1">
            <span className="px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800 font-mono text-[10px] font-bold block w-fit">
              SERVICE 1
            </span>
            <span className="font-bold text-slate-200 block">Flight Discovery Service</span>
            <p className="text-slate-400 text-[11px]">Queries availability &amp; budget constraints (`GET /sandbox/flights`).</p>
          </div>

          <div className="p-3 bg-slate-900/80 border border-amber-900/40 rounded-lg text-xs space-y-1">
            <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 font-mono text-[10px] font-bold block w-fit">
              SERVICE 2
            </span>
            <span className="font-bold text-slate-200 block">Reservation Service</span>
            <p className="text-slate-400 text-[11px]">Stateful booking &amp; seat allocation (`POST /sandbox/reservations`).</p>
          </div>

          <div className="p-3 bg-slate-900/80 border border-emerald-900/40 rounded-lg text-xs space-y-1">
            <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono text-[10px] font-bold block w-fit">
              SERVICE 3
            </span>
            <span className="font-bold text-slate-200 block">Payment Gateway Service</span>
            <p className="text-slate-400 text-[11px]">Transaction settlement &amp; idempotent charge (`POST /sandbox/payments`).</p>
          </div>
        </div>
      </div>

      {/* Active Connectors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {connectors.map((conn) => (
          <div
            key={conn.id}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3 shadow-lg"
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-teal-400" />
                <span className="text-xs font-bold text-slate-200 uppercase font-mono">{conn.name}</span>
              </div>
              <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-teal-950 text-teal-300 border border-teal-800/60 font-mono">
                {conn.status}
              </span>
            </div>

            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400 font-mono">Connector ID:</span>
                <span className="font-mono text-slate-200">{conn.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 font-mono">Base URL:</span>
                <span className="font-mono text-slate-200">{conn.base_url}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 font-mono">Operations:</span>
                <span className="font-mono text-teal-300 font-bold">{conn.operations_count} available</span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800/80">
              <span className="text-[10px] text-slate-500 block uppercase font-mono mb-1">
                Connected Operations:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {conn.operations.map((opId) => (
                  <span
                    key={opId}
                    className="px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800 font-mono text-[11px]"
                  >
                    {opId}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
