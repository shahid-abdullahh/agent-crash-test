export interface TaskConstraints {
  origin?: string;
  destination?: string;
  max_price?: number;
  passenger_name?: string;
  criteria_type?: string;
}

export interface Task {
  id: string;
  name: string;
  description: string;
  constraints: TaskConstraints;
  expected_outcome_description: string;
}

export type TraceEventType =
  | 'agent_start'
  | 'agent_thinking'
  | 'tool_call'
  | 'http_request'
  | 'http_response'
  | 'tool_result'
  | 'agent_output'
  | 'error';

export interface HTTPPayload {
  method: string;
  url: string;
  headers?: Record<string, string>;
  body?: any;
  status_code?: number;
  response_body?: any;
  duration_ms?: number;
}

export interface TraceEvent {
  event_id: string;
  run_id: string;
  sequence_number: number;
  timestamp: string;
  event_type: TraceEventType;
  tool_name?: string;
  tool_arguments?: Record<string, any>;
  http_payload?: HTTPPayload;
  error_message?: string;
  metadata?: Record<string, any>;
}

export interface CriterionResult {
  name: string;
  passed: boolean;
  expected: any;
  actual: any;
  message: string;
}

export interface SideEffectEvaluation {
  is_safe: boolean;
  total_reservations_created: number;
  expected_reservations: number;
  duplicate_reservations_detected: number;
  unintended_state_mutations: string[];
}

export interface EvaluationResult {
  run_id: string;
  task_id: string;
  success: boolean;
  criteria: CriterionResult[];
  side_effects: SideEffectEvaluation;
  reasons: string[];
  evaluated_at: string;
}

export interface DiagnosisResult {
  failure_category: string;
  observed_behavior: string;
  agent_behavior: string;
  impact: string;
  likely_responsibility: string;
  recommended_remediation: string;
  evidence_events: string[];
}

export type RunStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface RunCreateRequest {
  task_id: string;
  scenario_mode: string;
  agent_type: string;
  agent_retry_policy: string;
}

export interface Run {
  id: string;
  task_id: string;
  scenario_mode: string;
  agent_type: string;
  agent_retry_policy: string;
  status: RunStatus;
  trace: TraceEvent[];
  evaluation?: EvaluationResult;
  diagnosis?: DiagnosisResult;
  created_at: string;
  completed_at?: string;
  final_output?: Record<string, any>;
}

export interface TaskReliabilityMetric {
  task_id: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  reliability_percentage: number;
}

export interface ReliabilityOverview {
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  overall_reliability_percentage: number;
  by_scenario: Record<string, number>;
  by_task: TaskReliabilityMetric[];
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  timestamp: string;
}

export interface RunComparisonSummary {
  run_id: string;
  scenario_mode: string;
  agent_type: string;
  agent_retry_policy: string;
  status: string;
  total_reservations: number;
  duplicate_reservations: number;
  is_safe: boolean;
  trace_events_count: number;
  duration_ms?: number;
  failure_category?: string;
}

export interface RunComparison {
  baseline_run: RunComparisonSummary;
  remediated_run: RunComparisonSummary;
  status_transition: string;
  side_effect_delta: string;
  trace_event_delta: number;
  remediation_strategy: string;
  remediation_effective: boolean;
  key_findings: string[];
}

export interface ReadinessFinding {
  category: string;
  status: 'PASS' | 'WARN' | 'INFO';
  title: string;
  detail: string;
}

export interface OperationDefinition {
  operation_id: string;
  method: string;
  path: string;
  summary?: string;
  description?: string;
  parameters: any[];
  request_body_schema?: any;
  response_schemas: any;
  state_changing: boolean;
  idempotency_supported: boolean;
  generated_tool_name: string;
}

export interface Integration {
  id: string;
  name: string;
  description?: string;
  version: string;
  base_url: string;
  spec_type: string;
  operations: OperationDefinition[];
  schemas: Record<string, any>;
  generated_tools_count: number;
  readiness_findings: ReadinessFinding[];
  status: string;
  created_at: string;
}

export interface ConnectorDefinition {
  id: string;
  name: string;
  integration_id: string;
  auth_type: string;
  base_url: string;
  operations_count: number;
  operations: string[];
  status: 'CONNECTED' | 'READY_FOR_TESTING' | 'TESTED';
  metadata: Record<string, any>;
}

export interface EndpointDoc {
  operation_id: string;
  method: string;
  path: string;
  summary: string;
  description: string;
  parameters: any[];
  request_example?: any;
  response_examples: Record<string, any>;
  state_changing: boolean;
  agent_guidance: string;
  recovery_considerations: string;
}

export interface APIDocumentation {
  integration_id: string;
  title: string;
  version: string;
  base_url: string;
  overview: string;
  auth_summary: string;
  endpoints: EndpointDoc[];
  agent_usage_rules: string[];
  failure_and_recovery_guide: string[];
  markdown_content: string;
  generated_at: string;
}

