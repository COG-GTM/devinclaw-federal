'use client';

import { useEffect, useState } from 'react';

interface Rollups {
  timestamp: string;
  summary: {
    total_tasks: number;
    avg_duration_seconds: number;
    avg_compliance_score: number;
    total_guardrail_violations: number;
  };
  tasks_by_date: Record<string, number>;
  tasks_by_skill: Record<string, number>;
  guardrail_violations: Record<string, number>;
}

interface DashboardData {
  audience: string;
  timestamp: string;
  [key: string]: unknown;
}

export default function RollupsPage() {
  const [rollups, setRollups] = useState<Rollups | null>(null);
  const [audience, setAudience] = useState<'dev' | 'pm' | 'ciso'>('pm');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8420/api/v1/visibility/rollups')
      .then((r) => r.json())
      .then(setRollups)
      .catch(() => setError('Unable to connect to API'));
  }, []);

  useEffect(() => {
    fetch(`http://localhost:8420/api/v1/visibility/dashboard/${audience}`)
      .then((r) => r.json())
      .then(setDashboardData)
      .catch(() => {});
  }, [audience]);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-3xl font-bold mb-2">Metrics &amp; Rollups</h1>
      <p className="text-gray-400 mb-8">
        Aggregate metrics and multi-audience dashboards
      </p>

      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded p-4 mb-6">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      {rollups && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-900 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-blue-400">
              {rollups.summary.total_tasks}
            </div>
            <div className="text-gray-400 text-sm">Total Tasks</div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-green-400">
              {rollups.summary.avg_duration_seconds.toFixed(1)}s
            </div>
            <div className="text-gray-400 text-sm">Avg Duration</div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-purple-400">
              {(rollups.summary.avg_compliance_score * 100).toFixed(1)}%
            </div>
            <div className="text-gray-400 text-sm">Compliance Score</div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-red-400">
              {rollups.summary.total_guardrail_violations}
            </div>
            <div className="text-gray-400 text-sm">Violations</div>
          </div>
        </div>
      )}

      {/* Skill Utilisation */}
      {rollups && Object.keys(rollups.tasks_by_skill).length > 0 && (
        <div className="bg-gray-900 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Skill Utilisation</h2>
          <div className="space-y-2">
            {Object.entries(rollups.tasks_by_skill).map(([skill, count]) => (
              <div key={skill} className="flex items-center gap-3">
                <span className="w-40 text-sm font-mono text-gray-300">{skill}</span>
                <div className="flex-1 bg-gray-800 rounded-full h-4">
                  <div
                    className="bg-blue-600 rounded-full h-4"
                    style={{
                      width: `${Math.min(100, (count / Math.max(...Object.values(rollups.tasks_by_skill))) * 100)}%`,
                    }}
                  />
                </div>
                <span className="text-sm text-gray-400 w-8 text-right">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Multi-Audience Dashboard Selector */}
      <div className="bg-gray-900 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Dashboard View</h2>
        <div className="flex gap-2 mb-4">
          {(['dev', 'pm', 'ciso'] as const).map((a) => (
            <button
              key={a}
              onClick={() => setAudience(a)}
              className={`px-4 py-2 rounded text-sm font-medium ${
                audience === a
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {a.toUpperCase()}
            </button>
          ))}
        </div>

        {dashboardData && (
          <pre className="bg-gray-800 rounded p-4 text-sm text-gray-300 overflow-auto max-h-96">
            {JSON.stringify(dashboardData, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
