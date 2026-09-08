import React, { useState } from 'react';
import { Layers, Plus, Code, CheckCircle, AlertTriangle, Info, Copy, Check } from 'lucide-react';
import type { Integration } from '../types';
import { api } from '../services/api';

interface IntegrationsPanelProps {
  integrations: Integration[];
  onRefresh: () => void;
}

export const IntegrationsPanel: React.FC<IntegrationsPanelProps> = ({ integrations, onRefresh }) => {
  const [selectedIntegrationId, setSelectedIntegrationId] = useState<string>(
    integrations.length > 0 ? integrations[0].id : ''
  );
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [importName, setImportName] = useState('');
  const [importUrl, setImportUrl] = useState('');
  const [importContent, setImportContent] = useState('');
  const [codePkg, setCodePkg] = useState<Record<string, string> | null>(null);
  const [selectedFile, setSelectedFile] = useState<string>('client.py');
  const [copied, setCopied] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedIntegration =
    integrations.find((i) => i.id === selectedIntegrationId) || integrations[0];

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!importName) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await api.importIntegration({
        name: importName,
        spec_url: importUrl || undefined,
        spec_content: importContent || undefined,
      });
      setIsImportModalOpen(false);
      setImportName('');
      setImportUrl('');
      setImportContent('');
      onRefresh();
    } catch (err: any) {
      setError(err.message || 'Failed to import OpenAPI specification');
    } finally {
      setIsSubmitting(false);
    }
  };

  const loadCode = async (integrationId: string) => {
    try {
      const code = await api.getIntegrationCode(integrationId);
      setCodePkg(code);
      setSelectedFile('client.py');
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white tracking-wide">
              Smart API Integration Generator &amp; Analyzer
            </h2>
          </div>
          <p className="text-xs text-slate-400">
            Ingest OpenAPI 3.x contracts, inspect operation semantics, evaluate AI-readiness, and generate client/tool integration artifacts.
          </p>
        </div>
        <button
          onClick={() => setIsImportModalOpen(true)}
          className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold font-mono flex items-center space-x-1.5 transition-all shadow"
        >
          <Plus className="w-4 h-4" />
          <span>IMPORT OPENAPI SPEC</span>
        </button>
      </div>

      {/* Integration Selector Tabs */}
      {integrations.length > 0 && (
        <div className="flex space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
          {integrations.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setSelectedIntegrationId(item.id);
                setCodePkg(null);
              }}
              className={`px-4 py-2 rounded-lg text-xs font-mono font-medium transition-all shrink-0 ${
                selectedIntegration?.id === item.id
                  ? 'bg-slate-800 text-indigo-300 border border-indigo-500/40 shadow-sm'
                  : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 border border-slate-900'
              }`}
            >
              {item.name} ({item.operations.length} ops)
            </button>
          ))}
        </div>
      )}

      {selectedIntegration && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Integration Metadata & Operations */}
          <div className="lg:col-span-7 space-y-6">
            {/* Overview Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                  Contract Overview
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                  {selectedIntegration.status}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="bg-slate-950 p-2.5 rounded border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Base URL</span>
                  <span className="font-mono text-slate-200 truncate block">{selectedIntegration.base_url}</span>
                </div>
                <div className="bg-slate-950 p-2.5 rounded border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Spec Version</span>
                  <span className="font-mono text-slate-200">{selectedIntegration.version}</span>
                </div>
                <div className="bg-slate-950 p-2.5 rounded border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Generated Tools</span>
                  <span className="font-mono text-indigo-300 font-bold">{selectedIntegration.generated_tools_count}</span>
                </div>
              </div>

              {/* AI-Readiness Findings */}
              <div className="space-y-2 pt-2">
                <span className="text-[11px] font-bold text-slate-300 uppercase font-mono tracking-wider">
                  AI-Readiness Findings:
                </span>
                <div className="space-y-1.5">
                  {selectedIntegration.readiness_findings.map((f, idx) => (
                    <div
                      key={idx}
                      className={`p-2.5 rounded-lg border text-xs flex items-start space-x-2.5 ${
                        f.status === 'PASS'
                          ? 'bg-emerald-950/30 border-emerald-800/50 text-emerald-300'
                          : f.status === 'WARN'
                          ? 'bg-amber-950/30 border-amber-800/50 text-amber-300'
                          : 'bg-sky-950/30 border-sky-800/50 text-sky-300'
                      }`}
                    >
                      {f.status === 'PASS' ? (
                        <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      ) : f.status === 'WARN' ? (
                        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                      ) : (
                        <Info className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
                      )}
                      <div>
                        <span className="font-bold">{f.title}: </span>
                        <span className="opacity-90">{f.detail}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 flex justify-end">
                <button
                  onClick={() => loadCode(selectedIntegration.id)}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 rounded text-xs font-mono font-medium flex items-center space-x-1.5 transition-all"
                >
                  <Code className="w-3.5 h-3.5" />
                  <span>EXPORT INTEGRATION CODE</span>
                </button>
              </div>
            </div>

            {/* Operations Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                Extracted Operations &amp; Tools ({selectedIntegration.operations.length})
              </span>
              <div className="space-y-2">
                {selectedIntegration.operations.map((op) => (
                  <div
                    key={op.operation_id}
                    className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            op.method === 'GET'
                              ? 'bg-sky-950 text-sky-300 border border-sky-800'
                              : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          }`}
                        >
                          {op.method}
                        </span>
                        <span className="font-mono text-slate-200">{op.path}</span>
                      </div>
                      <span className="text-[11px] font-mono text-indigo-300 font-semibold">
                        → tool: {op.generated_tool_name}
                      </span>
                    </div>
                    {op.summary && <p className="text-slate-400 text-[11px]">{op.summary}</p>}
                    <div className="flex flex-wrap gap-2 text-[10px] font-mono text-slate-500 pt-1">
                      <span>State Mutating: {op.state_changing ? '⚠️ YES' : '✅ NO'}</span>
                      <span>•</span>
                      <span>Idempotency Key: {op.idempotency_supported ? '✅ Supported' : '❌ None'}</span>
                      <span>•</span>
                      <span>Params: {op.parameters.length}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Code Generation Viewer */}
          <div className="lg:col-span-5 space-y-6">
            {codePkg ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 shadow-lg sticky top-6">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <Code className="w-4 h-4 text-indigo-400" />
                    <span className="text-xs font-bold text-slate-200 uppercase font-mono">
                      Generated Integration Artifacts
                    </span>
                  </div>
                  <button
                    onClick={() => handleCopy(codePkg[selectedFile])}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-mono flex items-center space-x-1"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copied ? 'COPIED' : 'COPY'}</span>
                  </button>
                </div>

                {/* File Tabs */}
                <div className="flex space-x-2 border-b border-slate-800 pb-2">
                  {Object.keys(codePkg).map((fname) => (
                    <button
                      key={fname}
                      onClick={() => setSelectedFile(fname)}
                      className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                        selectedFile === fname
                          ? 'bg-slate-800 text-indigo-300 border border-indigo-600/40 font-bold'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {fname}
                    </button>
                  ))}
                </div>

                {/* Code Body */}
                <pre className="p-3 bg-slate-950 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto max-h-[480px] border border-slate-800/80 leading-relaxed">
                  {codePkg[selectedFile]}
                </pre>
              </div>
            ) : (
              <div className="bg-slate-900/50 border border-dashed border-slate-800 rounded-xl p-8 text-center text-slate-500 space-y-2">
                <Code className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs font-mono">Click &quot;EXPORT INTEGRATION CODE&quot; to inspect auto-generated Python client, tools schema, and README.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Import Modal */}
      {isImportModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white uppercase font-mono flex items-center gap-2">
              <Plus className="w-4 h-4 text-indigo-400" />
              Import OpenAPI Specification
            </h3>

            <form onSubmit={handleImport} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 uppercase font-mono text-[11px] mb-1">
                  Integration Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Payments Gateway API"
                  value={importName}
                  onChange={(e) => setImportName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 uppercase font-mono text-[11px] mb-1">
                  OpenAPI Spec URL (optional)
                </label>
                <input
                  type="url"
                  placeholder="https://api.example.com/openapi.json"
                  value={importUrl}
                  onChange={(e) => setImportUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 uppercase font-mono text-[11px] mb-1">
                  Or Paste Spec JSON / YAML (optional)
                </label>
                <textarea
                  rows={6}
                  placeholder="Paste OpenAPI 3.x schema..."
                  value={importContent}
                  onChange={(e) => setImportContent(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500 font-mono text-[11px]"
                />
              </div>

              {error && (
                <div className="p-2.5 bg-rose-950/40 border border-rose-800 text-rose-300 rounded text-xs">
                  {error}
                </div>
              )}

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsImportModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-mono"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-mono font-bold"
                >
                  {isSubmitting ? 'ANALYZING...' : 'PARSE & INTEGRATE'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
