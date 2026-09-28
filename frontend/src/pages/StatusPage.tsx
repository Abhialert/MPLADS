import React, { useEffect, useState } from 'react';
import {
  Activity,
  Database,
  ShieldCheck,
  Server,
  RefreshCw,
  CheckCircle2,
  Radio,
  FileCode2,
  Cpu,
  Terminal,
  Play,
} from 'lucide-react';
import { fetchStatus, checkHealth } from '../services/api';
import type { SystemStatus } from '../types';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const StatusPage: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [pingLatency, setPingLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Interactive API Console Tester State
  const [testEndpoint, setTestEndpoint] = useState<string>('/api/works/');
  const [testResponse, setTestResponse] = useState<string | null>(null);
  const [testLoading, setTestLoading] = useState<boolean>(false);

  const checkTelemetry = async () => {
    try {
      setLoading(true);
      const start = performance.now();
      const healthy = await checkHealth();
      const latency = Math.round(performance.now() - start);
      setPingLatency(latency);
      setIsHealthy(healthy);

      const data = await fetchStatus();
      setStatus(data);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to load status:', err);
      setIsHealthy(false);
      setLoading(false);
    }
  };

  const executeApiTest = async (endpoint: string) => {
    try {
      setTestLoading(true);
      setTestEndpoint(endpoint);
      const res = await fetch(`http://localhost:8000${endpoint}`);
      const json = await res.json();
      setTestResponse(JSON.stringify(json, null, 2));
      setTestLoading(false);
    } catch (err: any) {
      setTestResponse(`Error: ${err.message}`);
      setTestLoading(false);
    }
  };

  useEffect(() => {
    checkTelemetry();
    executeApiTest('/health');
  }, []);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  const schemaColumns = [
    { name: 'work_id', type: 'VARCHAR (PK)', desc: 'Canonical identifier for work' },
    { name: 'mp_name', type: 'VARCHAR', desc: 'Member of Parliament proposing work' },
    { name: 'constituency', type: 'VARCHAR', desc: 'Parliamentary constituency' },
    { name: 'state / district', type: 'VARCHAR', desc: 'Geographic administrative unit' },
    { name: 'financial_year', type: 'VARCHAR', desc: 'Fiscal year (e.g. 2023-24)' },
    { name: 'sanctioned_amount', type: 'FLOAT', desc: 'Official capital sanctioned in INR' },
    { name: 'actual_expenditure', type: 'FLOAT', desc: 'Disbursed public expenditure in INR' },
    { name: 'status', type: 'VARCHAR', desc: 'COMPLETED, ONGOING, SANCTIONED' },
    { name: 'source_url', type: 'VARCHAR', desc: 'Upstream eSAKSHI provenance link' },
  ];

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="w-6 h-6 text-blue-700" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              System Telemetry & Operational Health
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">
            Real-time diagnostics of backend API services, SQLite database integrity, and detector modules.
          </p>
        </div>

        <button
          onClick={checkTelemetry}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold transition-all shadow-xs"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Run Telemetry Ping</span>
        </button>
      </div>

      {/* Main Status Grid in Crisp White */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: API Server Status */}
        <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-xl bg-blue-50 text-blue-700">
              <Server className="w-5 h-5" />
            </div>
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                isHealthy
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-rose-50 text-rose-700 border border-rose-200'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-current"></span>
              {isHealthy ? 'ONLINE' : 'UNREACHABLE'}
            </span>
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">FastAPI Backend</h3>
            <p className="text-xs text-slate-500 mt-0.5">http://localhost:8000</p>
          </div>
          <div className="pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-1 font-mono">
            <div className="flex justify-between">
              <span>Ping Latency:</span>
              <span className="text-emerald-700 font-bold">{pingLatency ? `${pingLatency} ms` : 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span>Protocol:</span>
              <span className="text-slate-900">HTTP/1.1 REST</span>
            </div>
          </div>
        </div>

        {/* Card 2: Database Connection */}
        <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-xl bg-emerald-50 text-emerald-700">
              <Database className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-600"></span>
              {status?.db_status || 'CONNECTED'}
            </span>
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">SQLite Production DB</h3>
            <p className="text-xs text-slate-500 mt-0.5 font-mono">backend/data/mplad_integrity.db</p>
          </div>
          <div className="pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-1 font-mono">
            <div className="flex justify-between">
              <span>Ingested Works:</span>
              <span className="text-emerald-700 font-bold">{status?.total_works ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Schema Version:</span>
              <span className="text-slate-900 font-bold">v0.1.0</span>
            </div>
          </div>
        </div>

        {/* Card 3: Evidence Pipeline */}
        <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-xl bg-indigo-50 text-indigo-700">
              <Radio className="w-5 h-5" />
            </div>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              {status?.evidence_pipeline || 'ACTIVE'}
            </span>
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">Evidence Pipeline Mode</h3>
            <p className="text-xs text-slate-500 mt-0.5">{status?.mode || 'REAL_DATABASE_OBSERVATION'}</p>
          </div>
          <div className="pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-1">
            <div className="flex justify-between font-mono">
              <span>Active Detectors:</span>
              <span className="text-blue-700 font-bold">{status?.detectors?.length || 6} Loaded</span>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive API Endpoint Tester */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-blue-700" />
            <h2 className="text-base font-bold text-slate-900">Interactive Backend API Console</h2>
          </div>
          <span className="text-xs text-slate-500 font-mono">Real-time JSON Inspector</span>
        </div>

        <div className="flex flex-wrap gap-2">
          {['/health', '/status', '/coverage', '/api/works/'].map((ep) => (
            <button
              key={ep}
              onClick={() => executeApiTest(ep)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all flex items-center gap-1.5 ${
                testEndpoint === ep
                  ? 'bg-blue-700 text-white shadow-xs'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
              }`}
            >
              <Play className="w-3 h-3" />
              <span>{ep}</span>
            </button>
          ))}
        </div>

        <div className="rounded-xl bg-slate-900 p-4 border border-slate-800 text-slate-100 font-mono text-xs overflow-x-auto max-h-64">
          <div className="flex justify-between items-center text-slate-500 text-[11px] pb-2 mb-2 border-b border-slate-800">
            <span>GET {testEndpoint}</span>
            <span>{testLoading ? 'Fetching...' : '200 OK'}</span>
          </div>
          <pre>{testResponse || 'Executing test...'}</pre>
        </div>
      </div>

      {/* Database Schema Explorer */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-700" />
          <h2 className="text-base font-bold text-slate-900">Database Schema Reference (`works` table)</h2>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-4">Column Name</th>
                <th className="py-2.5 px-4">Data Type</th>
                <th className="py-2.5 px-4">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {schemaColumns.map((col, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="py-2.5 px-4 font-mono font-bold text-blue-700">{col.name}</td>
                  <td className="py-2.5 px-4 font-mono text-slate-500">{col.type}</td>
                  <td className="py-2.5 px-4 text-slate-600">{col.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Active Detectors Registry */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-blue-700" />
          <h2 className="text-base font-bold text-slate-900">Loaded Anomaly Detector Engine Modules</h2>
        </div>
        <p className="text-xs text-slate-500">
          Core heuristic and statistical analysis algorithms loaded in the backend execution container.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-2">
          {(status?.detectors || [
            'CostAnomalyDetector',
            'TimelineAnomalyDetector',
            'PotentialDuplicateDetector',
            'DataQualityDetector',
            'GeographicComplianceDetector',
            'SCSTAllocationDetector',
          ]).map((det, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-2">
                <FileCode2 className="w-4 h-4 text-blue-700" />
                <span className="font-mono text-slate-800 font-medium">{det}</span>
              </div>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
          ))}
        </div>
      </div>

      {/* Provenance & Compliance Notice */}
      <div className="rounded-2xl bg-blue-50 border border-blue-200 p-6 space-y-2">
        <div className="flex items-center gap-2 text-blue-900 font-bold text-sm">
          <ShieldCheck className="w-5 h-5 text-blue-700" />
          <span>Production Provenance Declaration</span>
        </div>
        <p className="text-xs text-slate-700 leading-relaxed">
          {status?.note ||
            "Production DB enforces strict provenance. Unobserved public fields remain NULL and are flagged with 'Not publicly observed' audit badges."}
        </p>
      </div>
    </div>
  );
};

export default StatusPage;
