import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  Building2,
  TrendingUp,
  FileSpreadsheet,
  AlertTriangle,
  ArrowUpRight,
  Database,
  PieChart as PieChartIcon,
  BarChart3,
  CheckCircle2,
  Clock,
  Landmark,
  Shield,
  Layers,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { fetchWorks } from '../services/api';
import type { Work } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { AuditBadge } from '../components/AuditBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { formatCurrency, formatCurrencyShort } from '../utils/formatters';

const CHART_COLORS = ['#059669', '#d97706', '#2563eb', '#0284c7', '#e11d48', '#7c3aed'];

export const HomePage: React.FC = () => {
  const [works, setWorks] = useState<Work[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'HIGH_VALUE' | 'COMPLETED' | 'ONGOING'>('ALL');

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        const worksData = await fetchWorks({ limit: 500 });
        setWorks(worksData || []);
        setLoading(false);
      } catch (err: any) {
        console.error('Failed to load dashboard data:', err);
        setError('Failed to connect to backend service. Please ensure the backend is running on http://localhost:8000');
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <LoadingSkeleton rows={6} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto my-12 p-8 rounded-2xl bg-white border border-rose-200 text-center space-y-4 shadow-sm">
        <div className="inline-flex p-4 rounded-full bg-rose-50 text-rose-600 border border-rose-200">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Backend Service Unavailable</h2>
        <p className="text-slate-600 max-w-md mx-auto text-sm">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-sm font-semibold transition-colors shadow-xs"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // Filtered dataset for dynamic exploration
  const filteredWorks = works.filter((w) => {
    if (activeFilter === 'HIGH_VALUE') {
      return (w.sanctioned_amount || 0) >= 2500000;
    }
    if (activeFilter === 'COMPLETED') {
      return (w.status || '').toUpperCase() === 'COMPLETED';
    }
    if (activeFilter === 'ONGOING') {
      const st = (w.status || '').toUpperCase();
      return st === 'ONGOING' || st === 'IN_PROGRESS';
    }
    return true;
  });

  // Analytics Computations
  const totalWorks = works.length;
  const totalSanctioned = works.reduce((sum, w) => sum + (w.sanctioned_amount || 0), 0);
  const totalExpenditure = works.reduce((sum, w) => sum + (w.actual_expenditure || 0), 0);
  const utilizationRate = totalSanctioned > 0 ? (totalExpenditure / totalSanctioned) * 100 : 0;
  const avgSanctionPerWork = totalWorks > 0 ? totalSanctioned / totalWorks : 0;

  const completedCount = works.filter((w) => (w.status || '').toUpperCase() === 'COMPLETED').length;
  const ongoingCount = works.filter((w) => (w.status || '').toUpperCase() === 'ONGOING' || (w.status || '').toUpperCase() === 'IN_PROGRESS').length;

  // Chart 1: Status Breakdown
  const statusMap = works.reduce<Record<string, number>>((acc, w) => {
    const st = w.status || 'Not publicly observed';
    acc[st] = (acc[st] || 0) + 1;
    return acc;
  }, {});

  const statusChartData = Object.entries(statusMap).map(([name, value]) => ({
    name,
    value,
  }));

  // Chart 2: State Distribution
  const stateMap = works.reduce<Record<string, { count: number; sanctioned: number; expenditure: number }>>((acc, w) => {
    const st = w.state || 'Unspecified';
    if (!acc[st]) {
      acc[st] = { count: 0, sanctioned: 0, expenditure: 0 };
    }
    acc[st].count += 1;
    acc[st].sanctioned += w.sanctioned_amount || 0;
    acc[st].expenditure += w.actual_expenditure || 0;
    return acc;
  }, {});

  const stateChartData = Object.entries(stateMap)
    .map(([state, data]) => ({
      state,
      works: data.count,
      sanctionedLakhs: Number((data.sanctioned / 100000).toFixed(1)),
      expenditureLakhs: Number((data.expenditure / 100000).toFixed(1)),
    }))
    .sort((a, b) => b.works - a.works)
    .slice(0, 8);

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Hero / Header intelligence Banner in Clean White / Navy */}
      <div className="relative overflow-hidden rounded-2xl bg-white border border-slate-200 p-6 md:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-800">
              <Shield className="w-3.5 h-3.5 text-blue-700" />
              <span>OFFICIAL CIVIC OBSERVATORY</span>
              <span className="w-1 h-1 rounded-full bg-blue-600"></span>
              <span>18th Lok Sabha & eSAKSHI Monitoring</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-slate-900">
              MPLAD Public Expenditure & Integrity Radar
            </h1>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
              Real-time audit telemetry tracking Member of Parliament Local Area Development Scheme allocations, execution lifecycle lags, and public fund utilization fidelity.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/works"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-medium text-sm shadow-xs hover:shadow-md transition-all transform hover:-translate-y-0.5"
            >
              <Database className="w-4 h-4" />
              <span>Explore All Works</span>
            </Link>
            <Link
              to="/coverage"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-medium text-sm border border-slate-300 shadow-xs transition-colors"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Detector Rules</span>
            </Link>
          </div>
        </div>

        {/* Quick Filter Bar */}
        <div className="mt-6 pt-5 border-t border-slate-100 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 mr-2 flex items-center gap-1">
            <Layers className="w-3.5 h-3.5" /> Quick View:
          </span>
          {[
            { id: 'ALL', label: `All Works (${totalWorks})` },
            { id: 'HIGH_VALUE', label: 'High Capital (≥ ₹25L)' },
            { id: 'COMPLETED', label: `Completed (${completedCount})` },
            { id: 'ONGOING', label: `Ongoing (${ongoingCount})` },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.id as any)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                activeFilter === f.id
                  ? 'bg-blue-700 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Works Ingested"
          value={totalWorks.toLocaleString('en-IN')}
          subtitle={`${completedCount} Completed • ${ongoingCount} Ongoing`}
          icon={Building2}
          accentColor="blue"
          trend={{ label: 'Live Database', positive: true }}
          tooltip="Total number of MPLAD work projects tracked in the local database"
        />
        <MetricCard
          title="Total Sanctioned Capital"
          value={formatCurrencyShort(totalSanctioned)}
          subtitle={formatCurrency(totalSanctioned)}
          icon={Landmark}
          accentColor="emerald"
          trend={{ label: 'Approved Budget', positive: true }}
          tooltip="Cumulative capital sanctioned by District Authorities"
        />
        <MetricCard
          title="Total Actual Expenditure"
          value={formatCurrencyShort(totalExpenditure)}
          subtitle={formatCurrency(totalExpenditure)}
          icon={TrendingUp}
          accentColor="cyan"
          trend={{ label: `${utilizationRate.toFixed(1)}% Disbursed`, positive: true }}
          tooltip="Total verified public funds disbursed and recorded"
        />
        <MetricCard
          title="Fund Utilization Rate"
          value={`${utilizationRate.toFixed(1)}%`}
          subtitle={`Avg Sanction: ${formatCurrencyShort(avgSanctionPerWork)}`}
          icon={FileSpreadsheet}
          accentColor={utilizationRate > 75 ? 'emerald' : 'amber'}
          trend={{ label: utilizationRate > 75 ? 'Optimal' : 'Active Execution', neutral: true }}
          tooltip="Percentage of sanctioned funds actually expended"
        />
      </div>

      {/* Interactive Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Chart: Status Distribution */}
        <div className="lg:col-span-5 rounded-2xl bg-white border border-slate-200 p-6 flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <PieChartIcon className="w-5 h-5 text-blue-700" />
                <h3 className="text-base font-bold text-slate-900">Work Status Distribution</h3>
              </div>
              <span className="text-xs font-mono text-slate-500 font-semibold">{totalWorks} Projects</span>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Breakdown of projects across administrative execution phases.
            </p>
          </div>

          <div className="h-64 w-full">
            {statusChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={88}
                    paddingAngle={3}
                    labelLine={false}
                  >
                    {statusChartData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={CHART_COLORS[index % CHART_COLORS.length]}
                        stroke="#ffffff"
                        strokeWidth={2}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0];
                        return (
                          <div className="bg-white border border-slate-200 p-2.5 rounded-lg shadow-md text-xs">
                            <p className="font-bold text-slate-900">{data.name}</p>
                            <p className="text-blue-700 font-semibold mt-0.5">
                              {data.value} Works (
                              {((Number(data.value) / totalWorks) * 100).toFixed(1)}%)
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    formatter={(value) => (
                      <span className="text-xs text-slate-600 font-medium">{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">
                No status data available
              </div>
            )}
          </div>
        </div>

        {/* Right Chart: State-wise Project & Financial Allocations */}
        <div className="lg:col-span-7 rounded-2xl bg-white border border-slate-200 p-6 flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-emerald-700" />
                <h3 className="text-base font-bold text-slate-900">State-wise Allocation & Expenditure</h3>
              </div>
              <span className="text-xs text-slate-500 font-semibold">Values in ₹ Lakhs</span>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Comparison between sanctioned capital and actual public expenditure across states.
            </p>
          </div>

          <div className="h-64 w-full">
            {stateChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stateChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis
                    dataKey="state"
                    tick={{ fill: '#64748b', fontSize: 11 }}
                    axisLine={{ stroke: '#cbd5e1' }}
                  />
                  <YAxis
                    tick={{ fill: '#64748b', fontSize: 11 }}
                    axisLine={{ stroke: '#cbd5e1' }}
                  />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-white border border-slate-200 p-3 rounded-lg shadow-md text-xs space-y-1">
                            <p className="font-bold text-slate-900 border-b border-slate-100 pb-1">{label}</p>
                            <p className="text-emerald-700 font-semibold">Sanctioned: ₹{payload[0]?.value} Lakhs</p>
                            <p className="text-blue-700 font-semibold">Expenditure: ₹{payload[1]?.value} Lakhs</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend
                    verticalAlign="top"
                    height={30}
                    formatter={(value) => (
                      <span className="text-xs text-slate-600 font-medium">
                        {value === 'sanctionedLakhs' ? 'Sanctioned (₹ Lakhs)' : 'Expenditure (₹ Lakhs)'}
                      </span>
                    )}
                  />
                  <Bar dataKey="sanctionedLakhs" fill="#059669" radius={[4, 4, 0, 0]} maxBarSize={32} />
                  <Bar dataKey="expenditureLakhs" fill="#2563eb" radius={[4, 4, 0, 0]} maxBarSize={32} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">
                No geographic distribution data
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Featured Works Monitored Table */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-blue-700" />
              <h2 className="text-lg font-bold text-slate-900">Monitored MPLAD Works Overview</h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Sample of active public works recorded from official eSAKSHI repository.
            </p>
          </div>
          <Link
            to="/works"
            className="inline-flex items-center gap-1 text-xs font-semibold text-blue-700 hover:text-blue-900 group"
          >
            <span>View All Records in Explorer</span>
            <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </Link>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 uppercase tracking-wider font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Work ID</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4">MP & Constituency</th>
                <th className="py-3 px-4">State</th>
                <th className="py-3 px-4">Sanctioned Capital</th>
                <th className="py-3 px-4">Expenditure</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {filteredWorks.slice(0, 5).map((work) => (
                <tr key={work.work_id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-blue-700 whitespace-nowrap">
                    {work.work_id}
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-900 max-w-xs truncate">
                    {work.work_description || <AuditBadge value={null} />}
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900">{work.mp_name || <AuditBadge value={null} />}</div>
                    <div className="text-[11px] text-slate-500">{work.constituency || 'Constituency not listed'}</div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    {work.state || <AuditBadge value={null} />}
                  </td>
                  <td className="py-3 px-4 font-mono text-emerald-700 font-semibold whitespace-nowrap">
                    {formatCurrency(work.sanctioned_amount)}
                  </td>
                  <td className="py-3 px-4 font-mono text-blue-700 font-semibold whitespace-nowrap">
                    {formatCurrency(work.actual_expenditure)}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <StatusBadge status={work.status} size="sm" />
                  </td>
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    <Link
                      to={`/works/${encodeURIComponent(work.work_id)}`}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-blue-700 text-slate-700 hover:text-white transition-colors text-xs font-medium"
                    >
                      <span>Dossier</span>
                      <ArrowUpRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))}
              {filteredWorks.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    No work records matching active view criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detector Engine Status & Integrity Notice */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-2 shadow-xs">
          <div className="flex items-center gap-2 text-blue-700 font-bold text-sm">
            <CheckCircle2 className="w-4 h-4" />
            <span>Strict Truthfulness Standard</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Every unobserved field is explicitly marked with audit tags. The engine never interpolates or fabricates missing government records.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-2 shadow-xs">
          <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
            <Database className="w-4 h-4" />
            <span>Multi-Source Provenance</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Connected to official eSAKSHI data streams with cryptographic and source URL audit tracking.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-2 shadow-xs">
          <div className="flex items-center gap-2 text-amber-700 font-bold text-sm">
            <Clock className="w-4 h-4" />
            <span>Automated Anomaly Scans</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Continuous evaluation for cost inflations, milestone delays, duplicate proposals, and geographic boundary compliance.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
