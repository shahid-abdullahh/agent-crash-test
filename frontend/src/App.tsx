import { useState, useEffect } from 'react';
import { api } from './services/api';
import type { Task, Run, ReliabilityOverview, HealthCheckResponse } from './types';
import { Header } from './components/Header';
import { TestConfigPanel } from './components/TestConfigPanel';
import { RunResultPanel } from './components/RunResultPanel';
import { EvaluationPanel } from './components/EvaluationPanel';
import { DiagnosisPanel } from './components/DiagnosisPanel';
import { TraceViewer } from './components/TraceViewer';
import { ReliabilityOverviewPanel } from './components/ReliabilityOverviewPanel';
import { AlertCircle, RefreshCw } from 'lucide-react';

export function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [scenarioMode, setScenarioMode] = useState<string>('normal');
  const [agentType, setAgentType] = useState<string>('deterministic');
  const [retryPolicy, setRetryPolicy] = useState<string>('unsafe_retry');

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentRun, setCurrentRun] = useState<Run | null>(null);
  const [reliability, setReliability] = useState<ReliabilityOverview | null>(null);
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load initial data
  const loadInitialData = async () => {
    try {
      setErrorMessage(null);
      const [tasksData, relData, healthData] = await Promise.all([
        api.getTasks(),
        api.getReliability(),
        api.getHealth().catch(() => null),
      ]);

      setTasks(tasksData);
      if (tasksData.length > 0 && !selectedTaskId) {
        setSelectedTaskId(tasksData[0].id);
      }
      setReliability(relData);
      setHealth(healthData);
    } catch (err: any) {
      setErrorMessage(
        'Failed to connect to Agent Crash Test backend. Ensure the FastAPI server is running on http://127.0.0.1:8000'
      );
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Execute Crash Test
  const handleRunTest = async () => {
    if (!selectedTaskId) return;

    setIsRunning(true);
    setErrorMessage(null);

    try {
      const run = await api.createAndExecuteRun({
        task_id: selectedTaskId,
        scenario_mode: scenarioMode,
        agent_type: agentType,
        agent_retry_policy: retryPolicy,
      });

      setCurrentRun(run);

      // Refresh reliability metrics
      const updatedRel = await api.getReliability();
      setReliability(updatedRel);
    } catch (err: any) {
      setErrorMessage(`Test execution failed: ${err.message || 'Unknown network error'}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans selection:bg-rose-500/30">
      <Header reliability={reliability} health={health} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full space-y-6">
        {/* Connection Error Banner */}
        {errorMessage && (
          <div className="p-4 bg-rose-950/40 border border-rose-600/60 rounded-xl text-xs text-rose-300 flex items-start justify-between gap-3">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={loadInitialData}
              className="px-2.5 py-1 bg-rose-900/60 hover:bg-rose-800/60 text-white rounded font-mono text-[11px] flex items-center gap-1 shrink-0"
            >
              <RefreshCw className="w-3 h-3" /> Retry Connection
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Test Configuration & Reliability */}
          <div className="lg:col-span-5 space-y-6">
            <TestConfigPanel
              tasks={tasks}
              selectedTaskId={selectedTaskId}
              onSelectTask={setSelectedTaskId}
              scenarioMode={scenarioMode}
              onSelectScenario={setScenarioMode}
              agentType={agentType}
              onSelectAgentType={setAgentType}
              retryPolicy={retryPolicy}
              onSelectRetryPolicy={setRetryPolicy}
              isRunning={isRunning}
              onRunTest={handleRunTest}
            />

            <ReliabilityOverviewPanel reliability={reliability} />
          </div>

          {/* Right Column: Execution Output, Evaluation, Diagnosis, Trace */}
          <div className="lg:col-span-7 space-y-6">
            {currentRun ? (
              <>
                <RunResultPanel run={currentRun} />

                {currentRun.diagnosis && <DiagnosisPanel diagnosis={currentRun.diagnosis} />}

                {currentRun.evaluation && <EvaluationPanel evaluation={currentRun.evaluation} />}

                <TraceViewer events={currentRun.trace} />
              </>
            ) : (
              <div className="bg-slate-900/50 border border-dashed border-slate-800 rounded-xl p-12 text-center text-slate-500 space-y-3">
                <div className="w-12 h-12 rounded-full bg-slate-800/60 flex items-center justify-center mx-auto text-slate-400">
                  <RefreshCw className="w-6 h-6" />
                </div>
                <h3 className="text-sm font-semibold text-slate-300 font-mono">
                  NO TEST EXECUTED YET
                </h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto font-sans">
                  Select an evaluation task and sandbox scenario on the left, then click{' '}
                  <span className="text-slate-300 font-mono font-bold">RUN CRASH TEST</span> to
                  observe the agent execution loop and capture traces live.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
