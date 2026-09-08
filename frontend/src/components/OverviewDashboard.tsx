import React from 'react';
import { Layers, Zap, ShieldCheck, ArrowRight, Play, BookOpen } from 'lucide-react';
import type { Integration, ConnectorDefinition, ReliabilityOverview, Run } from '../types';

interface OverviewDashboardProps {
  integrations: Integration[];
  connectors: ConnectorDefinition[];
  reliability: ReliabilityOverview | null;
  recentRuns: Run[];
  onNavigateTab: (tab: string) => void;
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  integrations,
  connectors,
  reliability,
  recentRuns,
  onNavigateTab,
}) => {
  const totalOperations = integrations.reduce((acc, i) => acc + i.operations.length, 0);
  const totalTools = integrations.reduce((acc, i) => acc + i.generated_tools_count, 0);
  const totalRuns = reliability?.total_runs || 0;
  const failedRuns = reliability?.failed_runs || 0;
  const overallRel = reliability?.overall_reliability_percentage ?? 100;

  return (
    <div className="space-y-6">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-xs font-mono font-semibold text-indigo-400 uppercase tracking-widest block">
              IBM SkillUp Hackathon • Track #4: Smart API Integration &amp; AI-Ready Connectivity
            </span>
            <h1 className="text-xl sm:text-2xl font-black text-white tracking-wide">
              Agent Crash Test
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              An AI-ready API integration and reliability framework that ingests API contracts, generates authorized integration tools and connector artifacts, produces API usage documentation, and then tests whether autonomous AI agents can safely use those integrations to accomplish real multi-step tasks.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onNavigateTab('testing')}
              className="px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold font-mono flex items-center space-x-2 shadow-lg shadow-rose-950/50 transition-all"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>RUN CRASH TEST</span>
            </button>
            <button
              onClick={() => onNavigateTab('integrations')}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-mono font-medium flex items-center space-x-2 transition-all"
            >
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>IMPORT OPENAPI</span>
            </button>
          </div>
        </div>
      </div>

      {/* Primary KPI Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 block tracking-wider">
            Connected APIs
          </span>
          <span className="text-2xl font-black text-white font-mono">{integrations.length}</span>
          <span className="text-[11px] text-slate-500 block font-mono">OpenAPI 3.x</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 block tracking-wider">
            Generated Tools
          </span>
          <span className="text-2xl font-black text-indigo-300 font-mono">{totalTools}</span>
          <span className="text-[11px] text-slate-500 block font-mono">{totalOperations} operations</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 block tracking-wider">
            Connectors
          </span>
          <span className="text-2xl font-black text-teal-300 font-mono">{connectors.length}</span>
          <span className="text-[11px] text-slate-500 block font-mono">Multi-service</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 block tracking-wider">
            Crash Tests Run
          </span>
          <span className="text-2xl font-black text-white font-mono">{totalRuns}</span>
          <span className="text-[11px] text-slate-500 block font-mono">Recorded runs</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 block tracking-wider">
            Task Reliability
          </span>
          <span className={`text-2xl font-black font-mono ${overallRel >= 70 ? 'text-emerald-400' : 'text-amber-400'}`}>
            {overallRel.toFixed(1)}%
          </span>
          <span className="text-[11px] text-slate-500 block font-mono">Empirical metrics</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400 block tracking-wider">
            Failures Caught
          </span>
          <span className="text-2xl font-black text-rose-400 font-mono">{failedRuns}</span>
          <span className="text-[11px] text-slate-500 block font-mono">Side-effects / 504</span>
        </div>
      </div>

      {/* Two-Column Feature Navigation & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Product Architecture Pillars */}
        <div className="lg:col-span-7 space-y-4">
          <span className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider block">
            End-to-End System Capabilities
          </span>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div
              onClick={() => onNavigateTab('integrations')}
              className="p-4 bg-slate-900 hover:bg-slate-800/80 border border-slate-800 rounded-xl cursor-pointer transition-all space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-indigo-400" />
                  <span className="text-xs font-bold text-slate-200">1. OpenAPI Analyzer</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 transition-transform group-hover:translate-x-1" />
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Ingest API contracts, generate authorized tools, resolve schemas, and inspect AI-readiness.
              </p>
            </div>

            <div
              onClick={() => onNavigateTab('connectors')}
              className="p-4 bg-slate-900 hover:bg-slate-800/80 border border-slate-800 rounded-xl cursor-pointer transition-all space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 text-teal-400" />
                  <span className="text-xs font-bold text-slate-200">2. Multi-Service Connectors</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-teal-400 transition-transform group-hover:translate-x-1" />
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Coordinate multi-service chains (Flight Discovery → Reservation → Payment Gateway).
              </p>
            </div>

            <div
              onClick={() => onNavigateTab('docs')}
              className="p-4 bg-slate-900 hover:bg-slate-800/80 border border-slate-800 rounded-xl cursor-pointer transition-all space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <BookOpen className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-bold text-slate-200">3. AI Documentation Builder</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-purple-400 transition-transform group-hover:translate-x-1" />
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Auto-generate developer documentation with autonomous decision rules &amp; failure guidelines.
              </p>
            </div>

            <div
              onClick={() => onNavigateTab('testing')}
              className="p-4 bg-slate-900 hover:bg-slate-800/80 border border-slate-800 rounded-xl cursor-pointer transition-all space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-rose-400" />
                  <span className="text-xs font-bold text-slate-200">4. Crash Testing &amp; Reliability</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-rose-400 transition-transform group-hover:translate-x-1" />
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Execute autonomous agents, capture HTTP traces, detect duplicate side-effects, and compare before/after.
              </p>
            </div>
          </div>
        </div>

        {/* Right: Recent Runs Timeline */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider">
              Recent Crash Test Runs
            </span>
            <button
              onClick={() => onNavigateTab('testing')}
              className="text-[11px] font-mono text-indigo-400 hover:text-indigo-300"
            >
              VIEW ALL →
            </button>
          </div>

          <div className="space-y-2">
            {recentRuns.length > 0 ? (
              recentRuns.slice(0, 5).map((run) => (
                <div
                  key={run.id}
                  className="p-3 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between text-xs font-mono"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-300 font-bold">{run.id.slice(0, 10)}...</span>
                      <span className="text-slate-500">|</span>
                      <span className="text-slate-400">{run.scenario_mode}</span>
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Policy: {run.agent_retry_policy} • Events: {run.trace.length}
                    </div>
                  </div>

                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      run.status === 'completed'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-rose-950 text-rose-300 border border-rose-800'
                    }`}
                  >
                    {run.status.toUpperCase()}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-8 bg-slate-900/40 border border-dashed border-slate-800 rounded-xl text-center text-slate-500 text-xs font-mono">
                No runs recorded yet. Launch a test to populate live metrics.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
