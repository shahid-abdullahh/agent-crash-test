import { useState, useEffect } from 'react';
import { api } from './services/api';
import type { Task, Run, ReliabilityOverview, HealthCheckResponse, Integration, ConnectorDefinition } from './types';
import { Header } from './components/Header';
import { OverviewDashboard } from './components/OverviewDashboard';
import { IntegrationsPanel } from './components/IntegrationsPanel';
import { ConnectorsPanel } from './components/ConnectorsPanel';
import { DocumentationPanel } from './components/DocumentationPanel';
import { TestConfigPanel } from './components/TestConfigPanel';
import { RunResultPanel } from './components/RunResultPanel';
import { EvaluationPanel } from './components/EvaluationPanel';
import { DiagnosisPanel } from './components/DiagnosisPanel';
import { TraceViewer } from './components/TraceViewer';
import { ReliabilityOverviewPanel } from './components/ReliabilityOverviewPanel';
import { BeforeAfterComparisonPanel } from './components/BeforeAfterComparisonPanel';
import { AlertCircle, RefreshCw } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');

  const [tasks, setTasks] = useState<Task[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [connectors, setConnectors] = useState<ConnectorDefinition[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [scenarioMode, setScenarioMode] = useState<string>('normal');
  const [agentType, setAgentType] = useState<string>('deterministic');
  const [retryPolicy, setRetryPolicy] = useState<string>('unsafe_retry');

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [currentRun, setCurrentRun] = useState<Run | null>(null);
  const [recentRuns, setRecentRuns] = useState<Run[]>([]);
  const [reliability, setReliability] = useState<ReliabilityOverview | null>(null);
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load initial data
  const loadInitialData = async () => {
    try {
      setErrorMessage(null);
      const [tasksData, relData, healthData, intData, connData] = await Promise.all([
        api.getTasks(),
        api.getReliability(),
        api.getHealth().catch(() => null),
        api.getIntegrations().catch(() => []),
        api.getConnectors().catch(() => []),
      ]);

      setTasks(tasksData);
      if (tasksData.length > 0 && !selectedTaskId) {
        setSelectedTaskId(tasksData[0].id);
      }
      setReliability(relData);
      setHealth(healthData);
      setIntegrations(intData);
      setConnectors(connData);
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
      setRecentRuns((prev) => [run, ...prev.filter((r) => r.id !== run.id)]);

      // Refresh reliability metrics
      const updatedRel = await api.getReliability();
      setReliability(updatedRel);
    } catch (err: any) {
      setErrorMessage(`Test execution failed: ${err.message || 'Unknown network error'}`);
    } finally {
      setIsRunning(false);
    }
  };

  // Reset demo environment
  const handleResetDemo = async () => {
    setIsResetting(true);
    try {
      await api.resetDemoEnvironment();
      setCurrentRun(null);
      setRecentRuns([]);
      await loadInitialData();
    } catch (err: any) {
      setErrorMessage(`Reset failed: ${err.message}`);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans selection:bg-rose-500/30">
      <Header
        reliability={reliability}
        health={health}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onResetDemo={handleResetDemo}
        isResetting={isResetting}
      />

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

        {/* Tab 1: Overview Dashboard */}
        {activeTab === 'overview' && (
          <OverviewDashboard
            integrations={integrations}
            connectors={connectors}
            reliability={reliability}
            recentRuns={recentRuns}
            onNavigateTab={setActiveTab}
          />
        )}

        {/* Tab 2: Smart API Integrations & Analyzer */}
        {activeTab === 'integrations' && (
          <IntegrationsPanel
            integrations={integrations}
            onRefresh={loadInitialData}
          />
        )}

        {/* Tab 3: Multi-Service Connectors */}
        {activeTab === 'connectors' && (
          <ConnectorsPanel connectors={connectors} />
        )}

        {/* Tab 4: Autonomous Crash Testing Console */}
        {activeTab === 'testing' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
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
        )}

        {/* Tab 5: Before / After Remediation Diff */}
        {activeTab === 'remediation' && (
          <BeforeAfterComparisonPanel recentRuns={recentRuns} currentRun={currentRun} />
        )}

        {/* Tab 6: AI-Based API Documentation Builder */}
        {activeTab === 'docs' && (
          <DocumentationPanel integrations={integrations} />
        )}

        {/* Tab 7: Reliability Analytics */}
        {activeTab === 'reliability' && (
          <div className="max-w-3xl mx-auto space-y-6">
            <ReliabilityOverviewPanel reliability={reliability} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

