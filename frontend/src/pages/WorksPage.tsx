import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  ArrowUpDown,
  Download,
  ChevronLeft,
  ChevronRight,
  Database,
  RefreshCw,
  Eye,
  SlidersHorizontal,
  X,
  Check,
} from 'lucide-react';
import { fetchWorks } from '../services/api';
import type { Work } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { AuditBadge } from '../components/AuditBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { formatCurrency, formatCurrencyShort } from '../utils/formatters';

export const WorksPage: React.FC = () => {
  const [works, setWorks] = useState<Work[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [exported, setExported] = useState<boolean>(false);

  // Client-side Search and Filtering Controls
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedState, setSelectedState] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedYear, setSelectedYear] = useState<string>('ALL');
  const [sortField, setSortField] = useState<keyof Work>('sanctioned_amount');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Pagination
  const [page, setPage] = useState<number>(0);
  const [limit, setLimit] = useState<number>(10);

  const loadAllWorks = async () => {
    try {
      setLoading(true);
      const data = await fetchWorks({ limit: 1000 });
      setWorks(data || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load works:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllWorks();
  }, []);

  // Compute unique filter dropdown options
  const filterOptions = useMemo(() => {
    const states = new Set<string>();
    const statuses = new Set<string>();
    const years = new Set<string>();

    works.forEach((w) => {
      if (w.state) states.add(w.state);
      if (w.status) statuses.add(w.status);
      if (w.financial_year) years.add(w.financial_year);
    });

    return {
      states: Array.from(states).sort(),
      statuses: Array.from(statuses).sort(),
      years: Array.from(years).sort(),
    };
  }, [works]);

  // Filter and sort the dataset
  const filteredAndSortedWorks = useMemo(() => {
    return works
      .filter((w) => {
        // Search term match across multiple fields
        const query = searchTerm.toLowerCase();
        const matchesSearch =
          !searchTerm ||
          w.work_id?.toLowerCase().includes(query) ||
          w.work_description?.toLowerCase().includes(query) ||
          w.mp_name?.toLowerCase().includes(query) ||
          w.constituency?.toLowerCase().includes(query) ||
          w.implementing_agency?.toLowerCase().includes(query) ||
          w.state?.toLowerCase().includes(query);

        // State filter
        const matchesState = selectedState === 'ALL' || w.state === selectedState;

        // Status filter
        const matchesStatus = selectedStatus === 'ALL' || w.status === selectedStatus;

        // Year filter
        const matchesYear = selectedYear === 'ALL' || w.financial_year === selectedYear;

        return matchesSearch && matchesState && matchesStatus && matchesYear;
      })
      .sort((a, b) => {
        const valA = a[sortField];
        const valB = b[sortField];

        if (valA === null || valA === undefined) return 1;
        if (valB === null || valB === undefined) return -1;

        if (typeof valA === 'number' && typeof valB === 'number') {
          return sortOrder === 'asc' ? valA - valB : valB - valA;
        }

        const strA = String(valA).toLowerCase();
        const strB = String(valB).toLowerCase();
        return sortOrder === 'asc' ? strA.localeCompare(strB) : strB.localeCompare(strA);
      });
  }, [works, searchTerm, selectedState, selectedStatus, selectedYear, sortField, sortOrder]);

  // Financial summary for filtered dataset
  const filteredSummary = useMemo(() => {
    const totalSanctioned = filteredAndSortedWorks.reduce((sum, w) => sum + (w.sanctioned_amount || 0), 0);
    const totalExpenditure = filteredAndSortedWorks.reduce((sum, w) => sum + (w.actual_expenditure || 0), 0);
    return {
      count: filteredAndSortedWorks.length,
      sanctioned: totalSanctioned,
      expenditure: totalExpenditure,
    };
  }, [filteredAndSortedWorks]);

  // Paginated slice
  const paginatedWorks = useMemo(() => {
    const start = page * limit;
    return filteredAndSortedWorks.slice(start, start + limit);
  }, [filteredAndSortedWorks, page, limit]);

  const totalPages = Math.ceil(filteredAndSortedWorks.length / limit);

  const handleSort = (field: keyof Work) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedState('ALL');
    setSelectedStatus('ALL');
    setSelectedYear('ALL');
    setPage(0);
  };

  // Export filtered data as CSV
  const exportToCSV = () => {
    if (filteredAndSortedWorks.length === 0) return;

    const headers = [
      'Work ID',
      'MP Name',
      'Constituency',
      'State',
      'District',
      'Financial Year',
      'Work Description',
      'Implementing Agency',
      'Recommended Amount (INR)',
      'Sanctioned Amount (INR)',
      'Actual Expenditure (INR)',
      'Status',
      'Recommendation Date',
      'Sanction Date',
      'Actual Completion Date',
      'Source URL',
    ];

    const rows = filteredAndSortedWorks.map((w) => [
      `"${w.work_id || ''}"`,
      `"${(w.mp_name || '').replace(/"/g, '""')}"`,
      `"${(w.constituency || '').replace(/"/g, '""')}"`,
      `"${(w.state || '').replace(/"/g, '""')}"`,
      `"${(w.district || '').replace(/"/g, '""')}"`,
      `"${w.financial_year || ''}"`,
      `"${(w.work_description || '').replace(/"/g, '""')}"`,
      `"${(w.implementing_agency || '').replace(/"/g, '""')}"`,
      w.recommended_amount !== null ? w.recommended_amount : '',
      w.sanctioned_amount !== null ? w.sanctioned_amount : '',
      w.actual_expenditure !== null ? w.actual_expenditure : '',
      `"${w.status || ''}"`,
      w.recommendation_date || '',
      w.sanction_date || '',
      w.actual_completion_date || '',
      `"${w.source_url || ''}"`,
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `mplad_works_audit_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setExported(true);
    setTimeout(() => setExported(false), 3000);
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-6 h-6 text-blue-700" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              Work Projects Explorer
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">
            Search, filter, and audit verified MPLAD public development works.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={exportToCSV}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 text-xs font-semibold shadow-xs transition-all"
            title="Export filtered works to CSV"
          >
            {exported ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-700">Exported CSV</span>
              </>
            ) : (
              <>
                <Download className="w-3.5 h-3.5 text-slate-600" />
                <span>Export CSV ({filteredAndSortedWorks.length})</span>
              </>
            )}
          </button>
          <button
            onClick={loadAllWorks}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 text-xs font-medium shadow-xs transition-colors"
            title="Refresh database records"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Toolbar */}
      <div className="rounded-2xl bg-white border border-slate-200 p-5 space-y-4 shadow-xs">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
          {/* Search Input */}
          <div className="md:col-span-5 relative">
            <Search className="absolute left-3.5 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search description, MP, ID, Agency, State..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(0);
              }}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:bg-white focus:ring-1 focus:ring-blue-600 transition-all"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* State Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedState}
              onChange={(e) => {
                setSelectedState(e.target.value);
                setPage(0);
              }}
              className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs sm:text-sm text-slate-700 focus:outline-none focus:border-blue-600 focus:bg-white transition-all font-medium"
            >
              <option value="ALL">All States ({filterOptions.states.length})</option>
              {filterOptions.states.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setPage(0);
              }}
              className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs sm:text-sm text-slate-700 focus:outline-none focus:border-blue-600 focus:bg-white transition-all font-medium"
            >
              <option value="ALL">All Statuses ({filterOptions.statuses.length})</option>
              {filterOptions.statuses.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          {/* Year Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedYear}
              onChange={(e) => {
                setSelectedYear(e.target.value);
                setPage(0);
              }}
              className="w-full px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs sm:text-sm text-slate-700 focus:outline-none focus:border-blue-600 focus:bg-white transition-all font-medium"
            >
              <option value="ALL">All Financial Years</option>
              {filterOptions.years.map((yr) => (
                <option key={yr} value={yr}>
                  {yr}
                </option>
              ))}
            </select>
          </div>

          {/* Clear Filters Button */}
          <div className="md:col-span-1 flex items-center justify-end">
            <button
              onClick={clearFilters}
              className="w-full md:w-auto p-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 border border-slate-200 flex items-center justify-center transition-colors text-xs font-medium"
              title="Reset all search & filters"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Financial Summary & Filter count bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs pt-3 border-t border-slate-100 text-slate-600">
          <div className="flex flex-wrap items-center gap-3">
            <span>
              Matching: <strong className="text-slate-900">{filteredSummary.count}</strong> of{' '}
              <strong className="text-slate-900">{works.length}</strong> works
            </span>
            <span className="text-slate-300">•</span>
            <span>
              Sanctioned Total: <strong className="text-emerald-700 font-semibold">{formatCurrencyShort(filteredSummary.sanctioned)}</strong>
            </span>
            <span className="text-slate-300">•</span>
            <span>
              Expenditure Total: <strong className="text-blue-700 font-semibold">{formatCurrencyShort(filteredSummary.expenditure)}</strong>
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-slate-500 font-mono text-[11px]">
            <span>Sort:</span>
            <span className="text-blue-700 font-semibold">{String(sortField)}</span>
            <span>({sortOrder.toUpperCase()})</span>
          </div>
        </div>
      </div>

      {/* Main Data Table in Crisp White */}
      <div className="rounded-2xl bg-white border border-slate-200 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 uppercase tracking-wider font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th
                  onClick={() => handleSort('work_id')}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 select-none whitespace-nowrap"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Work ID</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('work_description')}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 select-none min-w-[200px]"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Work Description</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('mp_name')}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 select-none whitespace-nowrap"
                >
                  <div className="flex items-center gap-1.5">
                    <span>MP & Constituency</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('state')}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 select-none whitespace-nowrap"
                >
                  <div className="flex items-center gap-1.5">
                    <span>State / District</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('sanctioned_amount')}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 select-none whitespace-nowrap text-right"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>Sanctioned</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('actual_expenditure')}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 select-none whitespace-nowrap text-right"
                >
                  <div className="flex items-center justify-end gap-1.5">
                    <span>Expenditure</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('status')}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 select-none whitespace-nowrap text-center"
                >
                  <div className="flex items-center justify-center gap-1.5">
                    <span>Status</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th className="py-3.5 px-4 text-right whitespace-nowrap">Audit Dossier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {paginatedWorks.map((work) => (
                <tr
                  key={work.work_id}
                  className="hover:bg-slate-50/80 transition-colors group"
                >
                  {/* Work ID */}
                  <td className="py-3.5 px-4 font-mono font-bold text-blue-700 whitespace-nowrap">
                    <Link
                      to={`/works/${encodeURIComponent(work.work_id)}`}
                      className="hover:underline flex items-center gap-1"
                    >
                      {work.work_id}
                    </Link>
                  </td>

                  {/* Work Description */}
                  <td className="py-3.5 px-4">
                    <div className="font-medium text-slate-900 max-w-md line-clamp-2 leading-snug">
                      {work.work_description || <AuditBadge value={null} />}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5">
                      Agency: {work.implementing_agency || <AuditBadge value={null} />}
                    </div>
                  </td>

                  {/* MP & Constituency */}
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    <div className="font-semibold text-slate-900">
                      {work.mp_name || <AuditBadge value={null} />}
                    </div>
                    <div className="text-[11px] text-slate-500 flex items-center gap-1">
                      <span>{work.constituency || 'Unspecified'}</span>
                      {work.financial_year && (
                        <span className="text-blue-700 font-mono">({work.financial_year})</span>
                      )}
                    </div>
                  </td>

                  {/* State / District */}
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    <div className="text-slate-800 font-medium">
                      {work.state || <AuditBadge value={null} />}
                    </div>
                    <div className="text-[11px] text-slate-500">
                      {work.district || <AuditBadge value={null} />}
                    </div>
                  </td>

                  {/* Sanctioned */}
                  <td className="py-3.5 px-4 font-mono text-right whitespace-nowrap font-bold text-emerald-700">
                    {formatCurrency(work.sanctioned_amount)}
                  </td>

                  {/* Actual Expenditure */}
                  <td className="py-3.5 px-4 font-mono text-right whitespace-nowrap font-bold text-blue-700">
                    {formatCurrency(work.actual_expenditure)}
                  </td>

                  {/* Status Badge */}
                  <td className="py-3.5 px-4 text-center whitespace-nowrap">
                    <StatusBadge status={work.status} size="sm" />
                  </td>

                  {/* Action Link */}
                  <td className="py-3.5 px-4 text-right whitespace-nowrap">
                    <Link
                      to={`/works/${encodeURIComponent(work.work_id)}`}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-700 text-blue-700 hover:text-white border border-blue-200 hover:border-blue-700 transition-all text-xs font-semibold"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect</span>
                    </Link>
                  </td>
                </tr>
              ))}

              {paginatedWorks.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    <div className="max-w-md mx-auto space-y-2">
                      <p className="font-semibold text-slate-900">No matching works found</p>
                      <p className="text-xs text-slate-500">
                        Try adjusting your search query or resetting filters.
                      </p>
                      <button
                        onClick={clearFilters}
                        className="mt-2 px-4 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium"
                      >
                        Reset Filters
                      </button>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer Controls */}
        <div className="bg-slate-50 px-4 py-3.5 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-600">
          <div className="flex items-center gap-4">
            <span>
              Page <strong className="text-slate-900">{page + 1}</strong> of{' '}
              <strong className="text-slate-900">{Math.max(1, totalPages)}</strong>
            </span>
            <div className="flex items-center gap-1.5">
              <span>Rows per page:</span>
              <select
                value={limit}
                onChange={(e) => {
                  setLimit(Number(e.target.value));
                  setPage(0);
                }}
                className="bg-white border border-slate-300 rounded px-2 py-1 text-slate-800 text-xs focus:outline-none"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-xs"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page + 1 >= totalPages || totalPages === 0}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-xs"
            >
              <span>Next</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorksPage;
