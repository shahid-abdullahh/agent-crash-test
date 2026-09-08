import React from 'react';
import { CheckCircle2, XCircle, Hash } from 'lucide-react';
import type { Run } from '../types';

interface RunResultPanelProps {
  run: Run;
}

export const RunResultPanel: React.FC<RunResultPanelProps> = ({ run }) => {
  const isSuccess = run.status === 'completed';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 mb-4 border-b border-slate-800 gap-3">
        <div>
          <span className="text-xs text-slate-500 font-mono block">RUN RESULT & VERIFICATION</span>
          <div className="flex items-center space-x-2 mt-0.5">
            <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
              <Hash className="w-3.5 h-3.5 text-slate-500" />
              {run.id}
            </span>
          </div>
        </div>

        <div>
          {isSuccess ? (
            <div className="inline-flex items-center space-x-2 bg-emerald-950/70 border border-emerald-500/80 px-4 py-1.5 rounded-full text-emerald-300 shadow-lg shadow-emerald-950/30">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span className="font-bold text-sm tracking-wider">SUCCESS — TASK VERIFIED</span>
            </div>
          ) : (
            <div className="inline-flex items-center space-x-2 bg-rose-950/70 border border-rose-500/80 px-4 py-1.5 rounded-full text-rose-300 shadow-lg shadow-rose-950/30 animate-pulse">
              <XCircle className="w-5 h-5 text-rose-400" />
              <span className="font-bold text-sm tracking-wider">FAILURE — SAFETY VIOLATION</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-500 block uppercase text-[10px] tracking-wider">Scenario</span>
          <span className="font-mono text-slate-200 font-semibold mt-0.5 block truncate">
            {run.scenario_mode}
          </span>
        </div>

        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-500 block uppercase text-[10px] tracking-wider">Agent Type</span>
          <span className="font-mono text-slate-200 font-semibold mt-0.5 block truncate">
            {run.agent_type}
          </span>
        </div>

        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-500 block uppercase text-[10px] tracking-wider">Retry Policy</span>
          <span className="font-mono text-slate-200 font-semibold mt-0.5 block truncate">
            {run.agent_retry_policy}
          </span>
        </div>

        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-500 block uppercase text-[10px] tracking-wider">Trace Events</span>
          <span className="font-mono text-sky-400 font-semibold mt-0.5 block">
            {run.trace.length} recorded
          </span>
        </div>
      </div>
    </div>
  );
};
