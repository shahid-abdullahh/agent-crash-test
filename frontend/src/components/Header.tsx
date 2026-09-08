import React from 'react';
import { Activity, ShieldAlert, Cpu, Layers, Network, BookOpen, GitCompare, Play, BarChart3, RefreshCw } from 'lucide-react';
import type { ReliabilityOverview, HealthCheckResponse } from '../types';

interface HeaderProps {
  reliability: ReliabilityOverview | null;
  health: HealthCheckResponse | null;
  activeTab: string;
  onTabChange: (tab: string) => void;
  onResetDemo: () => void;
  isResetting?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  reliability,
  health,
  activeTab,
  onTabChange,
  onResetDemo,
  isResetting = false,
}) => {
  const isHealthy = health?.status === 'healthy';
  const reliabilityPct = reliability ? reliability.overall_reliability_percentage : 0;

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'integrations', label: 'API Integrations', icon: Layers },
    { id: 'connectors', label: 'Connectors', icon: Network },
    { id: 'testing', label: 'Crash Tests', icon: Play },
    { id: 'remediation', label: 'Remediation Diff', icon: GitCompare },
    { id: 'docs', label: 'API Docs', icon: BookOpen },
    { id: 'reliability', label: 'Reliability', icon: BarChart3 },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
                AGENT CRASH TEST
                <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-rose-950/60 text-rose-400 border border-rose-800/40">
                  SMART CONNECTIVITY &amp; RELIABILITY
                </span>
              </h1>
            </div>
            <p className="text-[11px] text-slate-400">
              Test APIs the way autonomous agents actually use them.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Demo Reset Button */}
          <button
            onClick={onResetDemo}
            disabled={isResetting}
            title="Reset sandbox state and demo runs"
            className="px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 rounded-lg text-xs font-mono flex items-center space-x-1.5 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-400 ${isResetting ? 'animate-spin' : ''}`} />
            <span>RESET STATE</span>
          </button>

          {/* Reliability Metric */}
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1">
            <Cpu className="w-3.5 h-3.5 text-sky-400" />
            <div className="text-xs">
              <span className="text-slate-400 block font-sans text-[9px] uppercase tracking-wider">
                Reliability
              </span>
              <span
                className={`font-mono font-bold text-xs ${
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
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1">
            <Activity
              className={`w-3.5 h-3.5 ${isHealthy ? 'text-emerald-400 animate-pulse' : 'text-rose-400'}`}
            />
            <div className="text-xs">
              <span className="text-slate-400 block font-sans text-[9px] uppercase tracking-wider">
                API Backend
              </span>
              <span
                className={`font-mono font-semibold text-[11px] ${
                  isHealthy ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {isHealthy ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 border-t border-slate-900 overflow-x-auto py-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium flex items-center space-x-1.5 transition-all shrink-0 ${
                isActive
                  ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};

