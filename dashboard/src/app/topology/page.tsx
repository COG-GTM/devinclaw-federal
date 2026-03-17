'use client';

import { useEffect, useState } from 'react';

interface TopologyNode {
  id: string;
  name: string;
  type: string;
  status: string;
  port?: number;
}

interface TopologyEdge {
  source: string;
  target: string;
  type: string;
}

interface Topology {
  timestamp: string;
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  summary: {
    total_nodes: number;
    healthy_nodes: number;
    total_edges: number;
  };
}

const NODE_COLORS: Record<string, string> = {
  api: 'bg-blue-900 border-blue-500',
  frontend: 'bg-purple-900 border-purple-500',
  database: 'bg-green-900 border-green-500',
  cache: 'bg-yellow-900 border-yellow-500',
  internal: 'bg-gray-800 border-gray-500',
  external: 'bg-orange-900 border-orange-500',
  local: 'bg-teal-900 border-teal-500',
  security: 'bg-red-900 border-red-500',
};

const STATUS_INDICATOR: Record<string, string> = {
  healthy: 'bg-green-400',
  degraded: 'bg-yellow-400',
  down: 'bg-red-400',
  unknown: 'bg-gray-400',
};

export default function TopologyPage() {
  const [topology, setTopology] = useState<Topology | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8420/api/v1/visibility/topology')
      .then((r) => r.json())
      .then(setTopology)
      .catch(() => setError('Unable to connect to API'));
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-3xl font-bold mb-2">Service Topology</h1>
      <p className="text-gray-400 mb-8">Real-time service mesh view</p>

      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded p-4 mb-6">
          {error}
        </div>
      )}

      {topology && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-gray-900 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-blue-400">
                {topology.summary.total_nodes}
              </div>
              <div className="text-gray-400 text-sm">Total Services</div>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-green-400">
                {topology.summary.healthy_nodes}
              </div>
              <div className="text-gray-400 text-sm">Healthy</div>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-purple-400">
                {topology.summary.total_edges}
              </div>
              <div className="text-gray-400 text-sm">Connections</div>
            </div>
          </div>

          {/* Node Grid */}
          <div className="bg-gray-900 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Services</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {topology.nodes.map((node) => (
                <div
                  key={node.id}
                  className={`rounded-lg border p-4 ${NODE_COLORS[node.type] || NODE_COLORS.internal}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{node.name}</span>
                    <span
                      className={`w-3 h-3 rounded-full ${STATUS_INDICATOR[node.status] || STATUS_INDICATOR.unknown}`}
                    />
                  </div>
                  <div className="text-xs text-gray-400">
                    {node.type}
                    {node.port ? ` :${node.port}` : ''}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Connections */}
          <div className="bg-gray-900 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Connections</h2>
            <div className="space-y-2">
              {topology.edges.map((edge, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 text-sm bg-gray-800 rounded p-2"
                >
                  <span className="font-mono text-blue-400">{edge.source}</span>
                  <span className="text-gray-500">→</span>
                  <span className="font-mono text-green-400">{edge.target}</span>
                  <span className="ml-auto text-gray-500 text-xs">{edge.type}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
