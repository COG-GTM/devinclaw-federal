'use client';

import { useEffect, useState } from 'react';

interface TraceStep {
  step_name: string;
  step_index: number;
  status: string;
  started_at: string;
  completed_at: string;
  duration_ms: number;
  detail: Record<string, unknown>;
  errors: string[];
}

interface TaskTrace {
  task_id: string;
  status: string;
  current_step: number;
  created_at: string;
}

const PIPELINE_STEPS = [
  { name: 'intake', label: 'Intake', icon: '📥' },
  { name: 'authenticate', label: 'Authenticate', icon: '🔐' },
  { name: 'route_skill', label: 'Route Skill', icon: '🧭' },
  { name: 'check_guardrails', label: 'Guardrails', icon: '🛡️' },
  { name: 'select_spoke', label: 'Select Spoke', icon: '🔧' },
  { name: 'determine_arena', label: 'Arena Mode', icon: '🏟️' },
  { name: 'inject_memory', label: 'Memory', icon: '🧠' },
  { name: 'launch_sessions', label: 'Launch', icon: '🚀' },
  { name: 'monitor_sessions', label: 'Monitor', icon: '📊' },
  { name: 'validate_sdlc', label: 'SDLC', icon: '✅' },
  { name: 'write_audit', label: 'Audit', icon: '📝' },
  { name: 'update_memory', label: 'Learn', icon: '💡' },
];

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-700 text-gray-400',
  in_progress: 'bg-blue-900 text-blue-300 animate-pulse',
  completed: 'bg-green-900 text-green-300',
  failed: 'bg-red-900 text-red-300',
  skipped: 'bg-yellow-900 text-yellow-300',
};

export default function TracePage() {
  const [traces, setTraces] = useState<TaskTrace[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<{ steps: TraceStep[] } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8420/api/v1/visibility/traces')
      .then((r) => r.json())
      .then((data) => setTraces(data.traces || []))
      .catch(() => setError('Unable to connect to API'));
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-3xl font-bold mb-2">Task Journey Trace</h1>
      <p className="text-gray-400 mb-8">
        12-step orchestration pipeline visibility
      </p>

      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded p-4 mb-6">
          {error}
        </div>
      )}

      {/* Pipeline Steps Visualisation */}
      <div className="bg-gray-900 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Pipeline Steps</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
          {PIPELINE_STEPS.map((step, i) => {
            const traceStep = selectedTrace?.steps?.[i];
            const status = traceStep?.status || 'pending';
            return (
              <div
                key={step.name}
                className={`rounded-lg p-3 text-center ${STATUS_COLORS[status] || STATUS_COLORS.pending}`}
              >
                <div className="text-2xl mb-1">{step.icon}</div>
                <div className="text-sm font-medium">{step.label}</div>
                <div className="text-xs mt-1 opacity-75">
                  {traceStep?.duration_ms
                    ? `${traceStep.duration_ms.toFixed(0)}ms`
                    : status}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Traces */}
      <div className="bg-gray-900 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Traces</h2>
        {traces.length === 0 ? (
          <p className="text-gray-500">No traces recorded yet. Submit a task to see its journey.</p>
        ) : (
          <div className="space-y-2">
            {traces.map((t) => (
              <div
                key={t.task_id}
                className="flex items-center justify-between bg-gray-800 rounded p-3 cursor-pointer hover:bg-gray-700"
                onClick={() =>
                  fetch(`http://localhost:8420/api/v1/visibility/trace/${t.task_id}`)
                    .then((r) => r.json())
                    .then(setSelectedTrace)
                }
              >
                <div>
                  <span className="font-mono text-sm">{t.task_id.slice(0, 8)}...</span>
                  <span className="ml-3 text-gray-400 text-sm">{t.created_at}</span>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    t.status === 'completed'
                      ? 'bg-green-900 text-green-300'
                      : t.status === 'failed'
                        ? 'bg-red-900 text-red-300'
                        : 'bg-blue-900 text-blue-300'
                  }`}
                >
                  {t.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
