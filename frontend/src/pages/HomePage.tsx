import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  Building2,
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
  Award,
  AlertCircle,
  Activity,
  ChevronRight,
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
} from 'recharts';
import { fetchWorksSummary, fetchWorks } from '../services/api';
import type { WorksSummary, Work } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { formatCurrency, formatCurrencyShort } from '../utils/formatters';

const CHART_COLORS = ['#64748b', '#2563eb', '#059669', '#d97706', '#94a3b8'];

export const HomePage: React.FC = () => {
  const [summary, setSummary] = useState<WorksSummary | null>(null);
  const [featuredWorks, setFeaturedWorks] = useState<Work[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [summaryData, worksResponse] = await Promise.all([
          fetchWorksSummary(),
          fetchWorks({ limit: 8, sort_by: 'sanctioned_amount', sort_order: 'desc' }),
        ]);
        setSummary(summaryData);
        setFeaturedWorks(worksResponse.items || []);
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
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="max-w-4xl mx-auto my-12 p-8 rounded-2xl bg-white border border-rose-200 text-center space-y-4 shadow-sm">
        <div className="inline-flex p-4 rounded-full bg-rose-50 text-rose-600 border border-rose-200">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Backend Service Unavailable</h2>
        <p className="text-slate-600 max-w-md mx-auto text-sm">{error || 'Could not load summary data'}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-sm font-semibold transition-colors shadow-xs"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // Format State Chart Data into Crores
  const stateChartData = (summary.by_state || []).slice(0, 8).map((st) => ({
    state: st.state.length > 12 ? `${st.state.slice(0, 11)}…` : st.state,
    fullState: st.state,
    recommendedCr: Number((st.recommended_amount / 10000000).toFixed(1)),
    sanctionedCr: Number((st.sanctioned_amount / 10000000).toFixed(1)),
    sanctionRate: st.sanction_rate,
    count: st.count,
  }));

  // Format Status Chart Data
  const statusChartData = (summary.by_status || []).map((s) => ({
    name: s.status,
    value: s.count,
    amountCr: (s.recommended_amount / 10000000).toFixed(1),
  }));

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 px-4 sm:px-6 lg:px-8">
      {/* Hero Intelligence Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-white border border-slate-200 p-6 md:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-800">
              <Shield className="w-3.5 h-3.5 text-blue-700" />
              <span>OFFICIAL CIVIC OBSERVATORY</span>
              <span className="w-1 h-1 rounded-full bg-blue-600"></span>
              <span>60,362 Verified Records</span>
              <span className="w-1 h-1 rounded-full bg-blue-600"></span>
              <span>MOSPI & eSAKSHI Registry</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-slate-900">
              MPLAD Public Expenditure & Integrity Radar
            </h1>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
              Comprehensive telemetry tracking Member of Parliament Local Area Development Scheme allocations, district sanction velocity, and real capital disbursement across India.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/works"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-medium text-sm shadow-xs hover:shadow-md transition-all transform hover:-translate-y-0.5"
            >
              <Database className="w-4 h-4" />
              <span>Search All 60,362 Works</span>
            </Link>
            <Link
              to="/coverage"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-medium text-sm border border-slate-300 shadow-xs transition-colors"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Auditing Rules</span>
            </Link>
          </div>
        </div>

        {/* Highlight Stats Strip */}
        <div className="mt-6 pt-5 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-4 gap-4 text-slate-700 text-xs">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-500 shrink-0" />
            <span>
              <strong>{summary.unsanctioned_count.toLocaleString('en-IN')}</strong> Pending Sanction
            </span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              <strong>{summary.completed_count.toLocaleString('en-IN')}</strong> Completed Projects
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-600 shrink-0" />
            <span>
              <strong>{summary.ongoing_count.toLocaleString('en-IN')}</strong> Works in Progress
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-purple-600 shrink-0" />
            <span>
              <strong>{summary.high_value_count.toLocaleString('en-IN')}</strong> High Value (≥ ₹25L)
            </span>
          </div>
        </div>
      </div>

      {/* KPI Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Works Tracked"
          value={summary.total_works.toLocaleString('en-IN')}
          subtitle={`${summary.completed_count} Completed • ${summary.ongoing_count} Ongoing`}
          icon={Building2}
          accentColor="blue"
          trend={{ label: 'Official Database', positive: true }}
          tooltip="Total number of MPLAD work projects registered in the official database"
        />
        <MetricCard
          title="Total Recommended Capital"
          value={formatCurrencyShort(summary.total_recommended)}
          subtitle={formatCurrency(summary.total_recommended)}
          icon={Landmark}
          accentColor="blue"
          trend={{ label: 'MP Recommendations', positive: true }}
          tooltip="Cumulative capital allocated/recommended by MPs across all constituencies"
        />
        <MetricCard
          title="Total Sanctioned Capital"
          value={formatCurrencyShort(summary.total_sanctioned)}
          subtitle={formatCurrency(summary.total_sanctioned)}
          icon={CheckCircle2}
          accentColor="emerald"
          trend={{ label: `${summary.sanction_rate}% Sanctioned`, positive: true }}
          tooltip="Verified capital sanctioned by District Implementing Agencies"
        />
        <MetricCard
          title="District Sanction Velocity"
          value={`${summary.sanction_rate}%`}
          subtitle={`₹${((summary.total_recommended - summary.total_sanctioned) / 10000000).toFixed(0)} Cr Awaiting Sanction`}
          icon={FileSpreadsheet}
          accentColor={summary.sanction_rate > 20 ? 'emerald' : 'amber'}
          trend={{ label: summary.sanction_rate > 20 ? 'Active' : 'Bottleneck Observed', neutral: true }}
          tooltip="Ratio of sanctioned budget vs recommended allocations"
        />
      </div>

      {/* Analytics Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* State-wise Allocation vs Sanction Bar Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-6">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                State-wise Recommended vs Sanctioned Capital (₹ Crores)
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Top states by allocation showing sanction performance
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-slate-600">
                <span className="w-3 h-3 rounded-xs bg-slate-400"></span> Recommended
              </span>
              <span className="flex items-center gap-1.5 text-slate-600">
                <span className="w-3 h-3 rounded-xs bg-blue-600"></span> Sanctioned
              </span>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stateChartData} margin={{ top: 10, right: 10, left: -10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="state" tick={{ fontSize: 11, fill: '#64748b' }} angle={-25} textAnchor="end" interval={0} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} unit=" Cr" />
                <Tooltip
                  formatter={(val: any, name: any) => [
                    `₹${val} Cr`,
                    name === 'recommendedCr' ? 'Recommended' : 'Sanctioned',
                  ]}
                  labelFormatter={(lbl: any) => {
                    const row = stateChartData.find((s) => s.state === lbl);
                    return row ? `${row.fullState} (${row.count.toLocaleString()} works, ${row.sanctionRate}% sanctioned)` : String(lbl);
                  }}
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '0.75rem', fontSize: '12px' }}
                />
                <Bar dataKey="recommendedCr" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="sanctionedCr" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Status Distribution Pie Chart */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-1">
              <PieChartIcon className="w-5 h-5 text-indigo-600" />
              Work Status Pipeline
            </h2>
            <p className="text-xs text-slate-500 mb-4">
              Breakdown across 60,362 projects
            </p>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {statusChartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: any, name: any) => [
                      `${Number(value).toLocaleString('en-IN')} works`,
                      String(name),
                    ]}
                    contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '0.75rem', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-2 mt-4 pt-4 border-t border-slate-100 text-xs">
            {statusChartData.map((s, idx) => (
              <div key={s.name} className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-slate-600">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
                  ></span>
                  <span>{s.name}</span>
                </span>
                <span className="font-semibold text-slate-900">
                  {s.value.toLocaleString('en-IN')}{' '}
                  <span className="text-slate-400 font-normal">
                    ({((s.value / summary.total_works) * 100).toFixed(1)}%)
                  </span>
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top MPs by Recommended Volume */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-600" />
              Highest Capital Allocation by MPs
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Members of Parliament with highest total recommended project values
            </p>
          </div>
          <Link
            to="/works"
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <span>View All</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {(summary.top_mps || []).map((mp, index) => (
            <div
              key={`${mp.mp_name}-${index}`}
              className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-xs font-bold text-slate-400">#{index + 1}</span>
                <span className="text-xs font-semibold text-blue-700 px-2 py-0.5 rounded-full bg-blue-50 border border-blue-200">
                  {mp.works_count} works
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900 mt-2 line-clamp-1">{mp.mp_name}</h3>
              <p className="text-xs text-slate-500 line-clamp-1">
                {mp.constituency}, {mp.state}
              </p>
              <div className="mt-3 pt-3 border-t border-slate-200/80 flex items-center justify-between text-xs">
                <span className="text-slate-500">Allocated:</span>
                <span className="font-bold text-slate-900">{formatCurrencyShort(mp.recommended_amount)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Featured High-Capital Works Preview */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Landmark className="w-5 h-5 text-emerald-600" />
              Major Sanctioned Works
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              High-capital infrastructure projects approved and recorded in the system
            </p>
          </div>
          <Link
            to="/works"
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <span>Explore All 60,362 Works</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-y border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Work ID & Description</th>
                <th className="py-3 px-4 font-semibold">MP & Constituency</th>
                <th className="py-3 px-4 font-semibold">State</th>
                <th className="py-3 px-4 font-semibold text-right">Recommended</th>
                <th className="py-3 px-4 font-semibold text-right">Sanctioned</th>
                <th className="py-3 px-4 font-semibold text-center">Status</th>
                <th className="py-3 px-4 font-semibold text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {featuredWorks.map((w) => (
                <tr key={w.work_id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-4 max-w-xs">
                    <span className="font-mono text-xs text-blue-700 block font-semibold">{w.work_id}</span>
                    <span className="text-slate-800 text-xs line-clamp-1 font-medium">{w.work_description}</span>
                  </td>
                  <td className="py-3.5 px-4 text-xs">
                    <span className="font-semibold text-slate-900 block">{w.mp_name || 'N/A'}</span>
                    <span className="text-slate-500">{w.constituency || 'N/A'}</span>
                  </td>
                  <td className="py-3.5 px-4 text-xs text-slate-600">{w.state || 'N/A'}</td>
                  <td className="py-3.5 px-4 text-xs font-medium text-slate-700 text-right">
                    {formatCurrency(w.recommended_amount)}
                  </td>
                  <td className="py-3.5 px-4 text-xs font-bold text-emerald-700 text-right">
                    {formatCurrency(w.sanctioned_amount)}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <StatusBadge status={w.status} />
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <Link
                      to={`/works/${encodeURIComponent(w.work_id)}`}
                      className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-semibold"
                    >
                      <span>View</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
