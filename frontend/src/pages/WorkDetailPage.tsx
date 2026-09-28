import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
  DollarSign,
  MapPin,
  ShieldCheck,
  ExternalLink,
  Clock,
  Landmark,
  AlertCircle,
  FileCheck2,
  Layers,
  ChevronRight,
  Copy,
  Check,
  Printer,
} from 'lucide-react';
import { fetchWorkById } from '../services/api';
import type { Work } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { AuditBadge } from '../components/AuditBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { formatCurrency, formatDate, formatDateTime } from '../utils/formatters';

export const WorkDetailPage: React.FC = () => {
  const { workId } = useParams<{ workId: string }>();
  const [work, setWork] = useState<Work | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'financials' | 'timeline' | 'geo' | 'audit'>('overview');
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    const loadWorkDossier = async () => {
      if (!workId) return;
      try {
        setLoading(true);
        setError(null);
        const data = await fetchWorkById(workId);
        setWork(data);
        setLoading(false);
      } catch (err: any) {
        console.error(`Error loading work ${workId}:`, err);
        setError(`Work dossier "${workId}" not found in database.`);
        setLoading(false);
      }
    };

    loadWorkDossier();
  }, [workId]);

  const copyToClipboard = () => {
    if (!work) return;
    navigator.clipboard.writeText(work.work_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const printDossier = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <LoadingSkeleton rows={10} />
      </div>
    );
  }

  if (error || !work) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-8 rounded-2xl bg-white border border-slate-200 text-center space-y-4 shadow-sm">
        <AlertCircle className="w-12 h-12 text-rose-600 mx-auto" />
        <h2 className="text-xl font-bold text-slate-900">Work Dossier Not Found</h2>
        <p className="text-slate-600 text-sm">{error || 'Unable to find record in database'}</p>
        <Link
          to="/works"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-sm font-semibold transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Work Explorer</span>
        </Link>
      </div>
    );
  }

  const utilizationRate =
    work.sanctioned_amount && work.sanctioned_amount > 0 && work.actual_expenditure !== null
      ? (work.actual_expenditure / work.sanctioned_amount) * 100
      : null;

  const unspentCapital =
    work.sanctioned_amount !== null && work.actual_expenditure !== null
      ? work.sanctioned_amount - work.actual_expenditure
      : null;

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <Link to="/" className="hover:text-slate-900">Dashboard</Link>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
        <Link to="/works" className="hover:text-slate-900">Works Explorer</Link>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
        <span className="text-blue-700 font-mono font-semibold">{work.work_id}</span>
      </div>

      {/* Dossier Header Banner in Clean White */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 sm:p-8 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="space-y-2 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-md bg-blue-50 text-blue-800 border border-blue-200">
                {work.work_id}
              </span>
              <StatusBadge status={work.status} size="md" />
              {work.financial_year && (
                <span className="text-xs px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 border border-slate-200 font-medium">
                  FY: {work.financial_year}
                </span>
              )}
            </div>
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 leading-snug">
              {work.work_description || <AuditBadge value={null} />}
            </h1>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={copyToClipboard}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold border border-slate-200 transition-colors shadow-xs"
              title="Copy Work ID"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy ID'}</span>
            </button>
            <button
              onClick={printDossier}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold border border-slate-200 transition-colors shadow-xs"
              title="Print Dossier"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print</span>
            </button>
            <Link
              to="/works"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-800 text-xs font-semibold border border-blue-200 transition-colors shadow-xs"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Explorer</span>
            </Link>
          </div>
        </div>

        {/* Quick MP & Geo Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-100 text-xs">
          <div>
            <span className="text-slate-500 uppercase font-semibold text-[10px] block">Member of Parliament</span>
            <span className="font-semibold text-slate-900">{work.mp_name || <AuditBadge value={null} />}</span>
          </div>
          <div>
            <span className="text-slate-500 uppercase font-semibold text-[10px] block">Constituency</span>
            <span className="font-semibold text-slate-900">{work.constituency || <AuditBadge value={null} />}</span>
          </div>
          <div>
            <span className="text-slate-500 uppercase font-semibold text-[10px] block">State</span>
            <span className="font-semibold text-slate-900">{work.state || <AuditBadge value={null} />}</span>
          </div>
          <div>
            <span className="text-slate-500 uppercase font-semibold text-[10px] block">Implementing Agency</span>
            <span className="font-semibold text-slate-900">{work.implementing_agency || <AuditBadge value={null} />}</span>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-slate-200 space-x-1 overflow-x-auto text-xs font-semibold">
        {[
          { id: 'overview', label: 'Overview & Identity', icon: Layers },
          { id: 'financials', label: 'Financial Integrity', icon: DollarSign },
          { id: 'timeline', label: 'Milestone Timeline', icon: Clock },
          { id: 'geo', label: 'Geographic & Quotas', icon: MapPin },
          { id: 'audit', label: 'Provenance & Audit Trail', icon: ShieldCheck },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 whitespace-nowrap transition-all ${
                isActive
                  ? 'border-blue-700 text-blue-700 bg-blue-50/60 font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content 1: Overview & Identity */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-blue-700" />
              <span>Project Specification</span>
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Work ID</span>
                <span className="font-mono text-slate-900 font-bold">{work.work_id}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Source Work ID</span>
                <span className="font-mono text-slate-800">{work.source_work_id || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Sector / Category</span>
                <span className="text-slate-800 font-medium">{work.sector || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Financial Year</span>
                <span className="text-slate-800 font-medium">{work.financial_year || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-500">Status</span>
                <StatusBadge status={work.status} size="sm" />
              </div>
            </div>
          </div>

          <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <Landmark className="w-4 h-4 text-emerald-700" />
              <span>Implementing Authority & Contracting</span>
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Implementing Agency (IA)</span>
                <span className="text-slate-900 font-semibold">{work.implementing_agency || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Contractor / Vendor</span>
                <span className="text-slate-900 font-semibold">{work.contractor_name || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Asset Owner Type</span>
                <span className="text-slate-800 font-medium">{work.asset_owner_type || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-500">Beneficiary Group</span>
                <span className="text-slate-800 font-medium">{work.beneficiary_type || <AuditBadge value={null} />}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Content 2: Financial Integrity */}
      {activeTab === 'financials' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-xl bg-white border border-slate-200 p-5 space-y-1 shadow-xs">
              <span className="text-slate-500 text-xs font-semibold uppercase">Recommended Outlay</span>
              <p className="text-xl font-bold text-slate-900">{formatCurrency(work.recommended_amount)}</p>
              <span className="text-[11px] text-slate-500">MP proposal</span>
            </div>
            <div className="rounded-xl bg-white border border-emerald-200 p-5 space-y-1 shadow-xs">
              <span className="text-emerald-700 text-xs font-semibold uppercase">Sanctioned Capital</span>
              <p className="text-xl font-bold text-emerald-700">{formatCurrency(work.sanctioned_amount)}</p>
              <span className="text-[11px] text-slate-500">District Authority Sanction</span>
            </div>
            <div className="rounded-xl bg-white border border-blue-200 p-5 space-y-1 shadow-xs">
              <span className="text-blue-700 text-xs font-semibold uppercase">Actual Public Expenditure</span>
              <p className="text-xl font-bold text-blue-700">{formatCurrency(work.actual_expenditure)}</p>
              <span className="text-[11px] text-slate-500">Verified recorded spend</span>
            </div>
            <div className="rounded-xl bg-white border border-slate-200 p-5 space-y-1 shadow-xs">
              <span className="text-slate-700 text-xs font-semibold uppercase">Remaining / Unspent</span>
              <p className="text-xl font-bold text-slate-800">
                {unspentCapital !== null ? formatCurrency(unspentCapital) : <AuditBadge value={null} />}
              </p>
              <span className="text-[11px] text-slate-500">Sanctioned - Expenditure</span>
            </div>
          </div>

          {/* Utilization & Anomaly Radar bar */}
          <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 flex items-center justify-between">
              <span>Financial Utilization Fidelity</span>
              {utilizationRate !== null && (
                <span className="text-blue-700 font-mono text-xs font-bold">{utilizationRate.toFixed(1)}% of Sanctioned</span>
              )}
            </h3>
            {utilizationRate !== null ? (
              <div className="space-y-2">
                <div className="w-full bg-slate-100 rounded-full h-3.5 overflow-hidden border border-slate-200">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      utilizationRate > 100
                        ? 'bg-rose-600'
                        : utilizationRate > 80
                        ? 'bg-emerald-600'
                        : 'bg-blue-600'
                    }`}
                    style={{ width: `${Math.min(100, utilizationRate)}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-[11px] text-slate-500 font-medium">
                  <span>₹0 Expended</span>
                  <span>Sanctioned: {formatCurrency(work.sanctioned_amount)}</span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">
                Sufficient financial amounts not publicly observed to calculate utilization ratio.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Tab Content 3: Timeline & Milestone Tracker */}
      {activeTab === 'timeline' && (
        <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-6 shadow-xs">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-700" />
              <span>Administrative Execution Lifecycle</span>
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Chronological milestones from initial recommendation to final project closure.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Recommendation Date', date: work.recommendation_date, desc: 'MP submission' },
              { label: 'Sanction Date', date: work.sanction_date, desc: 'District administrative sanction' },
              { label: 'IA Assignment Date', date: work.ia_assignment_date, desc: 'Handover to agency' },
              { label: 'Expected Completion', date: work.expected_completion_date, desc: 'Target deadline' },
              { label: 'Actual Completion', date: work.actual_completion_date, desc: 'Work physically completed' },
              { label: 'Final Payment Date', date: work.final_payment_date, desc: 'Final financial settlement' },
              { label: 'Marked Complete Date', date: work.marked_complete_date, desc: 'Official portal sign-off' },
            ].map((step, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl border ${
                  step.date
                    ? 'bg-blue-50/40 border-blue-200 text-slate-900'
                    : 'bg-slate-50 border-slate-200 text-slate-500'
                }`}
              >
                <span className="text-[11px] font-bold block text-slate-600">{step.label}</span>
                <p className="text-sm font-semibold mt-1">
                  {step.date ? formatDate(step.date) : <AuditBadge value={null} />}
                </p>
                <span className="text-[10px] text-slate-500 mt-1 block">{step.desc}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab Content 4: Geographic & Quotas */}
      {activeTab === 'geo' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-blue-700" />
              <span>Location & Geographic Coordinates</span>
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Location Text</span>
                <span className="text-slate-900 font-semibold">{work.location_text || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">Constituency</span>
                <span className="text-slate-900 font-semibold">{work.constituency || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">District</span>
                <span className="text-slate-900 font-semibold">{work.district || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-slate-500">State</span>
                <span className="text-slate-900 font-semibold">{work.state || <AuditBadge value={null} />}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-500">Coordinates (Lat / Long)</span>
                <span className="font-mono text-blue-700 font-semibold">
                  {work.latitude !== null && work.longitude !== null
                    ? `${work.latitude}, ${work.longitude}`
                    : <AuditBadge value={null} />}
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-700" />
              <span>Boundary & Reserved Area Compliance</span>
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="text-slate-500">Within Constituency Boundary</span>
                <span>
                  {work.is_within_constituency === null ? (
                    <AuditBadge value={null} />
                  ) : work.is_within_constituency ? (
                    <span className="text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded">Yes (Compliant)</span>
                  ) : (
                    <span className="text-rose-700 font-bold bg-rose-50 px-2 py-0.5 rounded">No (Out of Constituency)</span>
                  )}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="text-slate-500">Scheduled Caste (SC) Quota Area</span>
                <span>
                  {work.is_sc_area === null ? (
                    <AuditBadge value={null} />
                  ) : work.is_sc_area ? (
                    <span className="text-blue-700 font-bold bg-blue-50 px-2 py-0.5 rounded">Yes (SC Area)</span>
                  ) : (
                    <span className="text-slate-500">No</span>
                  )}
                </span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-slate-500">Scheduled Tribe (ST) Quota Area</span>
                <span>
                  {work.is_st_area === null ? (
                    <AuditBadge value={null} />
                  ) : work.is_st_area ? (
                    <span className="text-blue-700 font-bold bg-blue-50 px-2 py-0.5 rounded">Yes (ST Area)</span>
                  ) : (
                    <span className="text-slate-500">No</span>
                  )}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Content 5: Provenance & Audit Trail */}
      {activeTab === 'audit' && (
        <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-6 shadow-xs">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <FileCheck2 className="w-5 h-5 text-blue-700" />
              <span>Data Provenance & Audit Verification</span>
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Source telemetry tracking public observation and dataset ingestion history.
            </p>
          </div>

          <div className="space-y-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-slate-600 font-bold">Source URL:</span>
              {work.source_url ? (
                <div className="flex items-center gap-2">
                  <a
                    href={work.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-700 hover:underline break-all font-medium"
                  >
                    {work.source_url}
                  </a>
                  <ExternalLink className="w-3.5 h-3.5 text-blue-700 shrink-0" />
                </div>
              ) : (
                <AuditBadge value={null} />
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-slate-600 font-bold block mb-1">Source Last Updated in eSAKSHI:</span>
                <span className="font-mono text-slate-900 font-semibold">
                  {work.source_last_updated ? formatDateTime(work.source_last_updated) : <AuditBadge value={null} />}
                </span>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-slate-600 font-bold block mb-1">Ingested into Local Database:</span>
                <span className="font-mono text-slate-900 font-semibold">
                  {work.created_at ? formatDateTime(work.created_at) : <AuditBadge value={null} />}
                </span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-xs text-slate-700 space-y-1">
              <span className="font-bold text-blue-900">Strict Non-Invention Policy:</span>
              <p className="text-slate-600 leading-relaxed">
                Fields marked with &apos;Not publicly observed&apos; indicate that data was omitted in upstream government disclosures. The Integrity Engine preserves NULL values to prevent speculative analysis.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkDetailPage;
