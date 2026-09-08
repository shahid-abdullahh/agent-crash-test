import React from 'react';
import { Wrench, FileSearch, ShieldX } from 'lucide-react';
import type { DiagnosisResult } from '../types';

interface DiagnosisPanelProps {
  diagnosis: DiagnosisResult;
}

export const DiagnosisPanel: React.FC<DiagnosisPanelProps> = ({ diagnosis }) => {
  return (
    <div className="bg-rose-950/20 border-2 border-rose-600/60 rounded-xl p-5 shadow-xl shadow-rose-950/20">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-rose-800/40">
        <h2 className="text-sm font-bold tracking-wider text-rose-300 uppercase flex items-center gap-2">
          <ShieldX className="w-5 h-5 text-rose-400" />
          Failure Root Cause Diagnosis
        </h2>
        <span className="text-xs text-rose-400 font-mono bg-rose-900/50 px-2 py-0.5 rounded border border-rose-700/50">
          AUTOMATED ROOT-CAUSE ENGINE
        </span>
      </div>

      <div className="space-y-4 text-xs">
        {/* Category & Impact */}
        <div className="bg-slate-950/80 p-3.5 rounded-lg border border-rose-900/40">
          <div className="flex items-start justify-between gap-2">
            <div>
              <span className="text-[10px] text-rose-400/80 uppercase font-mono tracking-wider block">
                Failure Category
              </span>
              <h3 className="text-sm font-bold text-white mt-0.5">{diagnosis.failure_category}</h3>
            </div>
            <span className="text-[11px] font-mono px-2 py-1 rounded bg-rose-950 text-rose-300 border border-rose-800/60">
              Responsibility: {diagnosis.likely_responsibility}
            </span>
          </div>

          <div className="mt-3 pt-3 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-mono">
                Observed API Behavior
              </span>
              <p className="text-slate-300 mt-1">{diagnosis.observed_behavior}</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-mono">
                Agent Integration Behavior
              </span>
              <p className="text-slate-300 mt-1">{diagnosis.agent_behavior}</p>
            </div>
          </div>
        </div>

        {/* Impact */}
        <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-mono">
            Environment Impact
          </span>
          <p className="text-rose-300 font-mono text-xs mt-1 font-semibold">{diagnosis.impact}</p>
        </div>

        {/* Evidence Events */}
        {diagnosis.evidence_events.length > 0 && (
          <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-mono flex items-center gap-1.5">
              <FileSearch className="w-3.5 h-3.5 text-sky-400" />
              Trace Evidence Links
            </span>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {diagnosis.evidence_events.map((evId, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-slate-900 border border-slate-700/80 text-sky-300 font-mono text-[11px] rounded"
                >
                  Event #{idx + 1}: {evId}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Remediation */}
        <div className="bg-emerald-950/30 p-3.5 rounded-lg border border-emerald-500/40 text-slate-200">
          <span className="text-[10px] text-emerald-400 font-mono uppercase tracking-wider block flex items-center gap-1.5">
            <Wrench className="w-3.5 h-3.5 text-emerald-400" />
            Recommended Remediation
          </span>
          <p className="text-emerald-200 font-sans mt-1.5 whitespace-pre-line leading-relaxed">
            {diagnosis.recommended_remediation}
          </p>
        </div>
      </div>
    </div>
  );
};
