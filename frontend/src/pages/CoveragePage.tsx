import React, { useEffect, useState } from 'react';
import {
  Radar,
  CheckCircle2,
  Database,
  Info,
  Search,
} from 'lucide-react';
import { fetchCoverage } from '../services/api';
import type { DetectorCoverage } from '../types';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const CoveragePage: React.FC = () => {
  const [coverage, setCoverage] = useState<DetectorCoverage | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterQuery, setFilterQuery] = useState<string>('');

  useEffect(() => {
    const loadCoverageData = async () => {
      try {
        setLoading(true);
        const covRes = await fetchCoverage();
        setCoverage(covRes);
        setLoading(false);
      } catch (err: any) {
        console.error('Failed to load coverage data:', err);
        setLoading(false);
      }
    };

    loadCoverageData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <LoadingSkeleton rows={6} />
      </div>
    );
  }

  const detectorsList = [
    {
      id: 'cost_anomaly',
      name: 'Cost & Expenditure Anomaly Detector',
      description: 'Scans for expenditure exceeding sanctioned budget, negative expenditures, or abnormal cost per beneficiary metrics.',
      statusKey: 'Cost Anomaly (Sanction vs Expenditure)',
      indicators: ['Expenditure > 120% Sanction', 'Negative Outlay', 'Zero Expenditure on Closed Projects'],
    },
    {
      id: 'timeline_anomaly',
      name: 'Timeline & Milestone Lag Detector',
      description: 'Detects impossible execution durations (e.g. completion before sanction) and chronic execution delays exceeding 365 days.',
      statusKey: 'Timeline Anomaly (Completion & Lags)',
      indicators: ['Negative Timeline Lag', 'Unrealistic Rapid Sign-off (< 3 days)', 'Stagnant Ongoing > 3 Years'],
    },
    {
      id: 'potential_duplicate',
      name: 'Potential Duplicate Works Detector',
      description: 'Employs fuzzy text matching and geographic clustering to detect duplicate sanction proposals across financial years.',
      statusKey: 'Potential Duplicate Works',
      indicators: ['Identical MP + Location Match', 'High Jaccard Text Similarity > 85%', 'Split Bill Clones'],
    },
    {
      id: 'data_quality',
      name: 'Data Quality & Provenance Auditor',
      description: 'Verifies schema integrity, missing mandatory public fields, invalid financial year patterns, and ISO date validity.',
      statusKey: 'Data Quality & Completeness Audit',
      indicators: ['Missing MP or Agency', 'Invalid Currency Formats', 'Unobserved Geolocation Tracking'],
    },
    {
      id: 'geographic_compliance',
      name: 'Geographic & Boundary Compliance Detector',
      description: 'Audits whether proposed works fall within the MP constituency boundaries as mandated by MPLADS guidelines.',
      statusKey: 'Geographic & Boundary Compliance',
      indicators: ['Out-of-Constituency Flagging', 'State Border Mismatch', 'District Admin Cross-allocation'],
    },
    {
      id: 'sc_st_quota',
      name: 'SC/ST Reserved Quota Compliance Tracker',
      description: 'Audits adherence to statutory MPLADS guidelines (minimum 15% allocation for SC areas, 7.5% for ST areas).',
      statusKey: 'SC/ST Reserved Quota Tracking',
      indicators: ['15% SC Target Allocation Ratio', '7.5% ST Target Allocation Ratio', 'Beneficiary Area Audit'],
    },
  ];

  const filteredDetectors = detectorsList.filter(
    (d) =>
      !filterQuery ||
      d.name.toLowerCase().includes(filterQuery.toLowerCase()) ||
      d.description.toLowerCase().includes(filterQuery.toLowerCase()) ||
      d.id.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Header Banner */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 md:p-8 shadow-xs space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-800">
          <Radar className="w-3.5 h-3.5 text-blue-700" />
          <span>INTEGRITY MATRIX & DETECTOR COVERAGE</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
          Anomaly Detectors & Rule Suite
        </h1>
        <p className="text-xs sm:text-sm text-slate-600 max-w-3xl leading-relaxed">
          The MPLAD Integrity Engine continuously assesses public records across cost fidelity, lifecycle milestones, duplicate allocations, and statutory guideline compliance.
        </p>

        {/* Search Filter Bar */}
        <div className="pt-4 max-w-md relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Filter detector rules..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* Summary Matrix Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDetectors.map((detector) => {
          const isCovered = coverage ? coverage[detector.statusKey] : true;
          return (
            <div
              key={detector.id}
              className="rounded-2xl bg-white border border-slate-200 p-6 flex flex-col justify-between space-y-4 hover:border-blue-300 transition-all shadow-xs"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <span className="font-mono text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    {detector.id}
                  </span>
                  <span
                    className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${
                      isCovered
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-amber-50 text-amber-700 border border-amber-200'
                    }`}
                  >
                    {isCovered ? (
                      <>
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>FULLY_EVALUABLE</span>
                      </>
                    ) : (
                      <>
                        <Info className="w-3 h-3 text-amber-600" />
                        <span>SCHEMA_READY</span>
                      </>
                    )}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 leading-snug">
                  {detector.name}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {detector.description}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 space-y-2">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">
                  Evaluated Signatures:
                </span>
                <ul className="space-y-1">
                  {detector.indicators.map((ind, i) => (
                    <li key={i} className="text-[11px] text-slate-700 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                      <span>{ind}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>

      {/* Source Registry Telemetry */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-4 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-700" />
            <h2 className="text-base font-bold text-slate-900">Upstream Source Registry</h2>
          </div>
          <span className="text-xs text-slate-500 font-mono font-medium">MOSPI / eSAKSHI Feeds</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-900 block">18th Lok Sabha Recommended Works</span>
            <span className="text-[11px] text-slate-500 block">Upstream: MOSPI / eSAKSHI (175k records)</span>
            <span className="inline-block mt-2 font-mono text-[10px] text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-semibold">
              PROVENANCE: VERIFIED
            </span>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-900 block">18th Lok Sabha Completed Works</span>
            <span className="text-[11px] text-slate-500 block">Upstream: MOSPI / eSAKSHI (44k records)</span>
            <span className="inline-block mt-2 font-mono text-[10px] text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-semibold">
              PROVENANCE: VERIFIED
            </span>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-900 block">18th Lok Sabha Vendor & Disbursals</span>
            <span className="text-[11px] text-slate-500 block">Upstream: MOSPI / eSAKSHI (143k records)</span>
            <span className="inline-block mt-2 font-mono text-[10px] text-blue-800 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded font-semibold">
              SCHEMA READY
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoveragePage;
