import React from 'react';
import { BarChart3, CheckCircle, XCircle } from 'lucide-react';
import type { ReliabilityOverview } from '../types';

interface ReliabilityOverviewPanelProps {
  reliability: ReliabilityOverview | null;
}

export const ReliabilityOverviewPanel: React.FC<ReliabilityOverviewPanelProps> = ({
  reliability,
}) => {
  if (!reliability) {
    return null;
  }

  const overallPct = reliability.overall_reliability_percentage;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <h2 className="text-sm font-semibold tracking-wider text-slate-200 uppercase flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-sky-400" />
          Empirical Task Reliability (Live Metric)
        </h2>
        <span className="text-xs text-slate-500 font-mono">Derived Strictly From Recorded Runs</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs mb-4">
        {/* Overall Percentage */}
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex flex-col justify-between">
          <span className="text-slate-500 uppercase text-[10px] tracking-wider">
            Overall Reliability
          </span>
          <div className="mt-2 flex items-baseline space-x-2">
            <span
              className={`font-mono text-2xl font-bold ${
                overallPct >= 80
                  ? 'text-emerald-400'
                  : overallPct > 0
                  ? 'text-amber-400'
                  : 'text-slate-400'
              }`}
            >
              {overallPct.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Total Runs */}
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-500 uppercase text-[10px] tracking-wider">Total Runs</span>
          <span className="font-mono text-xl font-bold text-white mt-1 block">
            {reliability.total_runs}
          </span>
        </div>

        {/* Successful Runs */}
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-500 uppercase text-[10px] tracking-wider flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-emerald-400" /> Passed
          </span>
          <span className="font-mono text-xl font-bold text-emerald-400 mt-1 block">
            {reliability.successful_runs}
          </span>
        </div>

        {/* Failed Runs */}
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-500 uppercase text-[10px] tracking-wider flex items-center gap-1">
            <XCircle className="w-3 h-3 text-rose-400" /> Failed
          </span>
          <span className="font-mono text-xl font-bold text-rose-400 mt-1 block">
            {reliability.failed_runs}
          </span>
        </div>
      </div>

      {/* Breakdown by Scenario */}
      {Object.keys(reliability.by_scenario).length > 0 && (
        <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 text-xs">
          <span className="text-slate-400 font-medium uppercase tracking-wider block mb-2">
            Reliability by Scenario
          </span>
          <div className="space-y-2">
            {Object.entries(reliability.by_scenario).map(([scen, pct]) => (
              <div key={scen} className="flex items-center justify-between font-mono text-[11px]">
                <span className="text-slate-300">{scen}</span>
                <div className="flex items-center space-x-3">
                  <div className="w-32 bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full ${pct >= 80 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className={`font-bold ${pct >= 80 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {pct.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
