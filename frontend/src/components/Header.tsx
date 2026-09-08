import React from 'react';
import { Activity, ShieldAlert, Cpu } from 'lucide-react';
import type { ReliabilityOverview, HealthCheckResponse } from '../types';

interface HeaderProps {
  reliability: ReliabilityOverview | null;
  health: HealthCheckResponse | null;
}

export const Header: React.FC<HeaderProps> = ({ reliability, health }) => {
  const isHealthy = health?.status === 'healthy';
  const reliabilityPct = reliability ? reliability.overall_reliability_percentage : 0;

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                AGENT CRASH TEST
                <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-rose-950/60 text-rose-400 border border-rose-800/40">
                  DEVELOPER CONSOLE
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400">
              Test APIs the way autonomous agents actually use them.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Reliability Metric */}
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5">
            <Cpu className="w-4 h-4 text-sky-400" />
            <div className="text-xs">
              <span className="text-slate-400 block font-sans text-[10px] uppercase tracking-wider">
                Task Reliability
              </span>
              <span
                className={`font-mono font-bold text-sm ${
                  reliabilityPct >= 80
                    ? 'text-emerald-400'
                    : reliabilityPct > 0
                    ? 'text-amber-400'
                    : 'text-slate-400'
                }`}
              >
                {reliability ? `${reliabilityPct.toFixed(1)}%` : '--'}
              </span>
            </div>
          </div>

          {/* Backend Health Badge */}
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5">
            <Activity
              className={`w-4 h-4 ${isHealthy ? 'text-emerald-400 animate-pulse' : 'text-rose-400'}`}
            />
            <div className="text-xs">
              <span className="text-slate-400 block font-sans text-[10px] uppercase tracking-wider">
                Backend API
              </span>
              <span
                className={`font-mono font-semibold text-xs ${
                  isHealthy ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {isHealthy ? 'ONLINE' : 'UNAVAILABLE'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
