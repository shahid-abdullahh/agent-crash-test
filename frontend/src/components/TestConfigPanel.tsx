import React from 'react';
import { Play, Flame, CheckCircle2, AlertTriangle } from 'lucide-react';
import type { Task } from '../types';

interface TestConfigPanelProps {
  tasks: Task[];
  selectedTaskId: string;
  onSelectTask: (taskId: string) => void;
  scenarioMode: string;
  onSelectScenario: (mode: string) => void;
  agentType: string;
  onSelectAgentType: (type: string) => void;
  retryPolicy: string;
  onSelectRetryPolicy: (policy: string) => void;
  isRunning: boolean;
  onRunTest: () => void;
}

export const TestConfigPanel: React.FC<TestConfigPanelProps> = ({
  tasks,
  selectedTaskId,
  onSelectTask,
  scenarioMode,
  onSelectScenario,
  agentType,
  onSelectAgentType,
  retryPolicy,
  onSelectRetryPolicy,
  isRunning,
  onRunTest,
}) => {
  const currentTask = tasks.find((t) => t.id === selectedTaskId);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <h2 className="text-sm font-semibold tracking-wider text-slate-200 uppercase flex items-center gap-2">
          <Flame className="w-4 h-4 text-rose-400" />
          Test Execution Control
        </h2>
        <span className="text-xs text-slate-500 font-mono">1. Select Target & Fault Scenario</span>
      </div>

      <div className="space-y-4">
        {/* Task Selection */}
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
            Evaluation Task
          </label>
          <select
            value={selectedTaskId}
            onChange={(e) => onSelectTask(e.target.value)}
            disabled={isRunning}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500 disabled:opacity-50"
          >
            {tasks.map((task) => (
              <option key={task.id} value={task.id}>
                {task.name} ({task.id})
              </option>
            ))}
          </select>
          {currentTask && (
            <div className="mt-2 p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/80 text-xs text-slate-300">
              <p className="font-sans mb-1">{currentTask.description}</p>
              <div className="flex flex-wrap gap-2 text-[11px] text-slate-400 font-mono">
                {currentTask.constraints.origin && (
                  <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    Route: {currentTask.constraints.origin} → {currentTask.constraints.destination}
                  </span>
                )}
                {currentTask.constraints.max_price && (
                  <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-amber-300">
                    Budget: ≤ ₹{currentTask.constraints.max_price}
                  </span>
                )}
                {currentTask.constraints.passenger_name && (
                  <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-sky-300">
                    Passenger: {currentTask.constraints.passenger_name}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Fault Injection Scenario */}
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
            Sandbox Fault Injection Scenario
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <button
              type="button"
              onClick={() => onSelectScenario('normal')}
              disabled={isRunning}
              className={`p-3 rounded-lg border text-left transition-all ${
                scenarioMode === 'normal'
                  ? 'bg-emerald-950/30 border-emerald-500/50 text-emerald-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-xs text-white">Normal (Happy Path)</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Standard API execution with nominal network responses and zero injected faults.
              </p>
            </button>

            <button
              type="button"
              onClick={() => onSelectScenario('timeout_after_commit')}
              disabled={isRunning}
              className={`p-3 rounded-lg border text-left transition-all ${
                scenarioMode === 'timeout_after_commit'
                  ? 'bg-rose-950/40 border-rose-500/60 text-rose-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span className="font-semibold text-xs text-white">Timeout After Commit (Fault)</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Server commits mutation, then drops response (HTTP 504) to expose uncoordinated retries.
              </p>
            </button>
          </div>
        </div>

        {/* Agent & Policy Selection */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
              Agent Implementation
            </label>
            <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800">
              <button
                type="button"
                onClick={() => onSelectAgentType('deterministic')}
                disabled={isRunning}
                className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${
                  agentType === 'deterministic'
                    ? 'bg-slate-800 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Deterministic Agent
              </button>
              <button
                type="button"
                onClick={() => onSelectAgentType('llm')}
                disabled={isRunning}
                className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${
                  agentType === 'llm'
                    ? 'bg-purple-900/60 text-purple-200 border border-purple-700/50 shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                LLM Provider Agent
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
              Agent Retry Behavior
            </label>
            <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800">
              <button
                type="button"
                onClick={() => onSelectRetryPolicy('unsafe_retry')}
                disabled={isRunning}
                className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${
                  retryPolicy === 'unsafe_retry'
                    ? 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Unsafe Blind Retry
              </button>
              <button
                type="button"
                onClick={() => onSelectRetryPolicy('idempotent_retry')}
                disabled={isRunning}
                className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${
                  retryPolicy === 'idempotent_retry'
                    ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Idempotent Key (Safe)
              </button>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-2">
          <button
            type="button"
            onClick={onRunTest}
            disabled={isRunning || !selectedTaskId}
            className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide text-sm flex items-center justify-center space-x-2 transition-all shadow-lg ${
              isRunning
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : scenarioMode === 'timeout_after_commit'
                ? 'bg-gradient-to-r from-rose-600 to-amber-600 hover:from-rose-500 hover:to-amber-500 text-white shadow-rose-950/50'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-950/50'
            }`}
          >
            {isRunning ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
                <span>AGENT EXECUTING TEST AGAINST SANDBOX...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>RUN CRASH TEST</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
