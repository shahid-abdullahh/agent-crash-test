import React from 'react';
import { ShieldCheck, ShieldAlert, Check, X, AlertCircle } from 'lucide-react';
import type { EvaluationResult } from '../types';

interface EvaluationPanelProps {
  evaluation: EvaluationResult;
}

export const EvaluationPanel: React.FC<EvaluationPanelProps> = ({ evaluation }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <h2 className="text-sm font-semibold tracking-wider text-slate-200 uppercase flex items-center gap-2">
          {evaluation.success ? (
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          ) : (
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          )}
          Deterministic Evaluation Engine
        </h2>
        <span className="text-xs text-slate-500 font-mono">Independent State & Constraint Checks</span>
      </div>

      <div className="space-y-4">
        {/* Criteria Checklist */}
        <div>
          <span className="text-xs text-slate-400 font-medium uppercase tracking-wider block mb-2">
            Verification Criteria
          </span>
          <div className="space-y-2">
            {evaluation.criteria.map((criterion, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border text-xs flex items-start justify-between gap-3 ${
                  criterion.passed
                    ? 'bg-emerald-950/20 border-emerald-800/40 text-slate-200'
                    : 'bg-rose-950/20 border-rose-800/40 text-slate-200'
                }`}
              >
                <div className="flex items-start space-x-2.5">
                  <div className="mt-0.5">
                    {criterion.passed ? (
                      <div className="p-0.5 bg-emerald-500/20 text-emerald-400 rounded">
                        <Check className="w-3.5 h-3.5" />
                      </div>
                    ) : (
                      <div className="p-0.5 bg-rose-500/20 text-rose-400 rounded">
                        <X className="w-3.5 h-3.5" />
                      </div>
                    )}
                  </div>
                  <div>
                    <span className="font-mono font-semibold text-slate-300 block">
                      {criterion.name.replace(/_/g, ' ').toUpperCase()}
                    </span>
                    <p className="text-slate-400 mt-0.5">{criterion.message}</p>
                  </div>
                </div>

                <div className="shrink-0 font-mono text-[11px]">
                  {criterion.passed ? (
                    <span className="px-2 py-0.5 bg-emerald-900/60 text-emerald-300 rounded font-bold">
                      PASS
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 bg-rose-900/60 text-rose-300 rounded font-bold">
                      FAIL
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Side-Effect Safety Snapshot */}
        <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 text-xs">
          <span className="text-slate-400 font-medium uppercase tracking-wider block mb-2">
            Sandbox Side-Effects Inspection
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono">
            <div className="p-2 bg-slate-900 rounded border border-slate-800/80">
              <span className="text-[10px] text-slate-500 block">RESERVATIONS CREATED</span>
              <span className="text-sm font-bold text-white">
                {evaluation.side_effects.total_reservations_created} (expected:{' '}
                {evaluation.side_effects.expected_reservations})
              </span>
            </div>

            <div className="p-2 bg-slate-900 rounded border border-slate-800/80">
              <span className="text-[10px] text-slate-500 block">DUPLICATES DETECTED</span>
              <span
                className={`text-sm font-bold ${
                  evaluation.side_effects.duplicate_reservations_detected > 0
                    ? 'text-rose-400'
                    : 'text-emerald-400'
                }`}
              >
                {evaluation.side_effects.duplicate_reservations_detected}
              </span>
            </div>

            <div className="p-2 bg-slate-900 rounded border border-slate-800/80 col-span-2 sm:col-span-1">
              <span className="text-[10px] text-slate-500 block">SIDE EFFECT SAFETY</span>
              <span
                className={`text-sm font-bold ${
                  evaluation.side_effects.is_safe ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {evaluation.side_effects.is_safe ? 'SAFE (AT-MOST-ONCE)' : 'UNSAFE CORRUPTION'}
              </span>
            </div>
          </div>

          {evaluation.side_effects.unintended_state_mutations.length > 0 && (
            <div className="mt-3 p-2 bg-rose-950/30 rounded border border-rose-800/30 text-rose-300 text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold block">Detected Unintended Mutations:</span>
                <ul className="list-disc list-inside mt-0.5 space-y-0.5 text-rose-300/90">
                  {evaluation.side_effects.unintended_state_mutations.map((m, i) => (
                    <li key={i}>{m}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
