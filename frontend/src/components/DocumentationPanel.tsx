import React, { useState, useEffect } from 'react';
import { BookOpen, Copy, Download, Check, Sparkles } from 'lucide-react';
import type { Integration, APIDocumentation } from '../types';
import { api } from '../services/api';

interface DocumentationPanelProps {
  integrations: Integration[];
}

export const DocumentationPanel: React.FC<DocumentationPanelProps> = ({ integrations }) => {
  const [selectedIntegrationId, setSelectedIntegrationId] = useState<string>(
    integrations.length > 0 ? integrations[0].id : ''
  );
  const [doc, setDoc] = useState<APIDocumentation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDocumentation = async (intId: string) => {
    if (!intId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getDocumentation(intId);
      setDoc(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load API documentation');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedIntegrationId) {
      loadDocumentation(selectedIntegrationId);
    }
  }, [selectedIntegrationId]);

  const handleCopy = () => {
    if (doc) {
      navigator.clipboard.writeText(doc.markdown_content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (!doc) return;
    const blob = new Blob([doc.markdown_content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${doc.title.toLowerCase().replace(/\s+/g, '_')}_api_doc.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-purple-400" />
            <h2 className="text-base font-bold text-white tracking-wide">
              AI-Based API Documentation Builder
            </h2>
          </div>
          <p className="text-xs text-slate-400">
            Contract-derived API documentation generator featuring endpoint schemas, parameter rules, autonomous agent usage guidelines, and failure/recovery considerations.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            disabled={!doc}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 rounded text-xs font-mono flex items-center space-x-1.5 transition-all shadow"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'COPIED' : 'COPY MARKDOWN'}</span>
          </button>
          <button
            onClick={handleDownload}
            disabled={!doc}
            className="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white rounded text-xs font-mono font-bold flex items-center space-x-1.5 transition-all shadow"
          >
            <Download className="w-3.5 h-3.5" />
            <span>DOWNLOAD .MD</span>
          </button>
        </div>
      </div>

      {/* Integration Selector */}
      {integrations.length > 0 && (
        <div className="flex space-x-2 border-b border-slate-800 pb-2">
          {integrations.map((item) => (
            <button
              key={item.id}
              onClick={() => setSelectedIntegrationId(item.id)}
              className={`px-4 py-2 rounded-lg text-xs font-mono font-medium transition-all ${
                selectedIntegrationId === item.id
                  ? 'bg-slate-800 text-purple-300 border border-purple-500/40 shadow-sm'
                  : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 border border-slate-900'
              }`}
            >
              {item.name}
            </button>
          ))}
        </div>
      )}

      {error && (
        <div className="p-3 bg-rose-950/40 border border-rose-800 text-rose-300 rounded-lg text-xs">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="p-12 text-center text-slate-500">
          <div className="w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <span className="text-xs font-mono">Generating Contract-Derived Documentation...</span>
        </div>
      ) : doc ? (
        <div className="space-y-6">
          {/* Agent Guidelines Banner */}
          <div className="p-4 bg-purple-950/30 border border-purple-800/50 rounded-xl space-y-2">
            <span className="text-xs font-bold text-purple-300 uppercase font-mono tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Autonomous Agent Execution Guidelines:
            </span>
            <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside">
              {doc.agent_usage_rules.map((rule, idx) => (
                <li key={idx} className="leading-relaxed">{rule}</li>
              ))}
            </ul>
          </div>

          {/* Endpoints Documentation Cards */}
          <div className="space-y-4">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono block">
              Documented Endpoints ({doc.endpoints.length})
            </span>
            {doc.endpoints.map((ep) => (
              <div
                key={ep.operation_id}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3"
              >
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        ep.method === 'GET'
                          ? 'bg-sky-950 text-sky-300 border border-sky-800'
                          : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      }`}
                    >
                      {ep.method}
                    </span>
                    <span className="font-mono text-sm font-bold text-slate-100">{ep.path}</span>
                    <span className="text-xs font-mono text-slate-500">({ep.operation_id})</span>
                  </div>
                  <span
                    className={`text-[11px] px-2 py-0.5 rounded font-mono ${
                      ep.state_changing
                        ? 'bg-amber-950/60 text-amber-300 border border-amber-800/60'
                        : 'bg-slate-950 text-slate-400 border border-slate-800'
                    }`}
                  >
                    {ep.state_changing ? '⚠️ Mutating' : '✅ Read-Only'}
                  </span>
                </div>

                <p className="text-xs text-slate-300">{ep.description}</p>

                {/* Parameters */}
                {ep.parameters.length > 0 && (
                  <div>
                    <span className="text-[11px] font-mono font-bold text-slate-400 uppercase block mb-1">
                      Parameters:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                      {ep.parameters.map((p, idx) => (
                        <div key={idx} className="p-2 bg-slate-950 rounded border border-slate-800 font-mono text-[11px]">
                          <span className="text-indigo-300 font-bold">{p.name}</span>
                          <span className="text-slate-500"> ({p.in})</span>: {p.schema?.type || 'any'}
                          {p.required && <span className="text-rose-400 ml-1 font-sans">*required</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Agent Guidance & Failure Considerations */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs font-sans">
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 space-y-1">
                    <span className="text-[11px] font-mono font-bold text-purple-300 uppercase block">
                      Autonomous Decision Rule:
                    </span>
                    <p className="text-slate-300 leading-relaxed">{ep.agent_guidance}</p>
                  </div>

                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 space-y-1">
                    <span className="text-[11px] font-mono font-bold text-amber-300 uppercase block">
                      Failure &amp; Recovery Rule:
                    </span>
                    <p className="text-slate-300 leading-relaxed">{ep.recovery_considerations}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Raw Markdown Output */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <span className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider block">
              Generated Markdown Contract
            </span>
            <pre className="p-4 bg-slate-950 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto max-h-[360px] border border-slate-800/80 leading-relaxed">
              {doc.markdown_content}
            </pre>
          </div>
        </div>
      ) : null}
    </div>
  );
};
