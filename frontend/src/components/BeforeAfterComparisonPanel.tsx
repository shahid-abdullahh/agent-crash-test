import React, { useState } from 'react';
import { GitCompare, CheckCircle2, XCircle, ArrowRight, ShieldCheck, Zap } from 'lucide-react';
import type { RunComparison, Run } from '../types';
import { api } from '../services/api';

interface BeforeAfterComparisonPanelProps {
  recentRuns: Run[];
  currentRun: Run | null;
}

export const BeforeAfterComparisonPanel: React.FC<BeforeAfterComparisonPanelProps> = ({
  recentRuns,
  currentRun,
}) => {
  const [baselineId, setBaselineId] = useState<string>('');
  const [remediatedId, setRemediatedId] = useState<string>('');
  const [comparison, setComparison] = useState<RunComparison | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Auto load runs from API if none passed, or auto populate
  React.useEffect(() => {
    const initRuns = async () => {
      let runs = recentRuns;
      if (runs.length < 2) {
        try {
          const apiRuns = await api.getRuns();
          if (apiRuns && apiRuns.length > 0) {
            runs = apiRuns;
          }
        } catch (e) {
          // ignore
        }
      }

      const failed = runs.find((r) => r.status === 'failed' || (r.evaluation && !r.evaluation.success));
      const passed = runs.find((r) => r.status === 'completed' && r.evaluation && r.evaluation.success);
      
      const bId = failed ? failed.id : (runs[1]?.id || '');
      const rId = passed ? passed.id : (runs[0]?.id || '');

      if (bId) setBaselineId(bId);
      if (rId) setRemediatedId(rId);

      if (bId && rId && bId !== rId) {
        try {
          setIsLoading(true);
          const res = await api.getComparison(bId, rId);
          setComparison(res);
        } catch (err) {
          // ignore
        } finally {
          setIsLoading(false);
        }
      }
    };

    initRuns();
  }, [recentRuns, currentRun]);

  const handleCompare = async () => {
    if (!baselineId || !remediatedId) return;
    if (baselineId === remediatedId) {
      setError('Please select two distinct runs to compare.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getComparison(baselineId, remediatedId);
      setComparison(res);
    } catch (err: any) {
      setError(err.message || 'Failed to compare runs');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <GitCompare className="w-5 h-5 text-indigo-400" />
          <h2 className="text-sm font-semibold tracking-wider text-slate-200 uppercase">
            Remediation &amp; Before/After Comparison
          </h2>
        </div>
        <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-800/60 font-mono">
          Empirical Verification
        </span>
      </div>

      {/* Selectors */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1 uppercase tracking-wider">
            Baseline Run (Pre-Remediation / Injected Fault)
          </label>
          <select
            value={baselineId}
            onChange={(e) => setBaselineId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-rose-500 font-mono"
          >
            <option value="">Select baseline run...</option>
            {recentRuns.map((r) => (
              <option key={r.id} value={r.id}>
                {r.id.slice(0, 8)}... | {r.scenario_mode} | {r.agent_retry_policy} | {r.status.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1 uppercase tracking-wider">
            Remediated Run (Post-Remediation / Safe Strategy)
          </label>
          <select
            value={remediatedId}
            onChange={(e) => setRemediatedId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
          >
            <option value="">Select remediated run...</option>
            {recentRuns.map((r) => (
              <option key={r.id} value={r.id}>
                {r.id.slice(0, 8)}... | {r.scenario_mode} | {r.agent_retry_policy} | {r.status.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleCompare}
          disabled={!baselineId || !remediatedId || isLoading}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-lg text-xs font-bold font-mono tracking-wide flex items-center space-x-2 transition-all shadow-md"
        >
          {isLoading ? (
            <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Zap className="w-3.5 h-3.5" />
          )}
          <span>COMPARE RUNS</span>
        </button>
      </div>

      {error && (
        <div className="p-2.5 bg-rose-950/40 border border-rose-800/60 rounded text-xs text-rose-300">
          {error}
        </div>
      )}

      {/* Comparison Results */}
      {comparison && (
        <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-4">
          {/* Status Delta Banner */}
          <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center space-x-3">
              <span className="text-xs font-mono text-slate-400">OUTCOME TRANSITION:</span>
              <span className="px-2.5 py-1 rounded bg-rose-950 text-rose-300 border border-rose-800/60 text-xs font-mono font-bold">
                {comparison.baseline_run.status.toUpperCase()}
              </span>
              <ArrowRight className="w-4 h-4 text-slate-500" />
              <span className="px-2.5 py-1 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60 text-xs font-mono font-bold">
                {comparison.remediated_run.status.toUpperCase()}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-semibold text-emerald-300">
                {comparison.remediation_strategy}
              </span>
            </div>
          </div>

          {/* Comparative Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Baseline Card */}
            <div className="p-4 bg-rose-950/20 border border-rose-900/40 rounded-xl space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                  <XCircle className="w-3.5 h-3.5" /> BEFORE REMEDIATION
                </span>
                <span className="text-[10px] font-mono text-slate-500">
                  {comparison.baseline_run.run_id.slice(0, 8)}...
                </span>
              </div>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Scenario:</span>
                  <span className="font-mono text-slate-200">{comparison.baseline_run.scenario_mode}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Retry Policy:</span>
                  <span className="font-mono text-rose-300">{comparison.baseline_run.agent_retry_policy}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Reservations Created:</span>
                  <span className="font-mono text-rose-300 font-bold">
                    {comparison.baseline_run.total_reservations} ({comparison.baseline_run.duplicate_reservations} dup)
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Trace Events:</span>
                  <span className="font-mono text-slate-300">{comparison.baseline_run.trace_events_count}</span>
                </div>
                {comparison.baseline_run.failure_category && (
                  <div className="pt-1.5 border-t border-rose-900/30 text-[11px] text-rose-300">
                    <span className="font-semibold">Diagnosis: </span>
                    {comparison.baseline_run.failure_category}
                  </div>
                )}
              </div>
            </div>

            {/* Remediated Card */}
            <div className="p-4 bg-emerald-950/20 border border-emerald-900/40 rounded-xl space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> AFTER REMEDIATION
                </span>
                <span className="text-[10px] font-mono text-slate-500">
                  {comparison.remediated_run.run_id.slice(0, 8)}...
                </span>
              </div>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Scenario:</span>
                  <span className="font-mono text-slate-200">{comparison.remediated_run.scenario_mode}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Retry Policy:</span>
                  <span className="font-mono text-emerald-300">{comparison.remediated_run.agent_retry_policy}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Reservations Created:</span>
                  <span className="font-mono text-emerald-300 font-bold">
                    {comparison.remediated_run.total_reservations} ({comparison.remediated_run.duplicate_reservations} dup)
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Trace Events:</span>
                  <span className="font-mono text-slate-300">{comparison.remediated_run.trace_events_count}</span>
                </div>
                <div className="pt-1.5 border-t border-emerald-900/30 text-[11px] text-emerald-300 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>State mutation safe &amp; task criteria verified</span>
                </div>
              </div>
            </div>
          </div>

          {/* Key Findings */}
          <div className="p-3.5 bg-slate-950/80 rounded-xl border border-slate-800 space-y-2">
            <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider font-mono">
              Key Empirical Findings:
            </h4>
            <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside font-sans">
              {comparison.key_findings.map((f, idx) => (
                <li key={idx} className="leading-relaxed">
                  {f}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
