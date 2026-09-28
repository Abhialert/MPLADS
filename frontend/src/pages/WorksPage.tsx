import React, { useEffect, useState, useCallback } from 'react';
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
  X,
  ChevronsLeft,
  ChevronsRight,
  Filter,
} from 'lucide-react';
import { fetchWorks, fetchFilterOptions } from '../services/api';
import type { Work, FilterOptions } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { formatCurrency } from '../utils/formatters';

export const WorksPage: React.FC = () => {
  const [works, setWorks] = useState<Work[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    states: [],
    statuses: [],
    financial_years: [],
  });

  // Filter States
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [activeSearch, setActiveSearch] = useState<string>('');
  const [selectedState, setSelectedState] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedYear, setSelectedYear] = useState<string>('ALL');
  const [sortField, setSortField] = useState<string>('sanctioned_amount');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Pagination
  const [page, setPage] = useState<number>(1);
  const [limit, setLimit] = useState<number>(25);

  // Load filter dropdown options once
  useEffect(() => {
    fetchFilterOptions().then(setFilterOptions).catch(console.error);
  }, []);

  // Fetch works with current server-side filters
  const loadWorks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetchWorks({
        page,
        limit,
        search: activeSearch || undefined,
        state: selectedState !== 'ALL' ? selectedState : undefined,
        status: selectedStatus !== 'ALL' ? selectedStatus : undefined,
        financial_year: selectedYear !== 'ALL' ? selectedYear : undefined,
        sort_by: sortField,
        sort_order: sortOrder,
      });

      setWorks(response.items || []);
      setTotal(response.total || 0);
      setTotalPages(response.total_pages || 1);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load works:', err);
      setLoading(false);
    }
  }, [page, limit, activeSearch, selectedState, selectedStatus, selectedYear, sortField, sortOrder]);

  useEffect(() => {
    loadWorks();
  }, [loadWorks]);

  // Handle Search Submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setActiveSearch(searchTerm);
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setActiveSearch('');
    setSelectedState('ALL');
    setSelectedStatus('ALL');
    setSelectedYear('ALL');
    setSortField('sanctioned_amount');
    setSortOrder('desc');
    setPage(1);
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
    setPage(1);
  };

  // Export current results as CSV
  const handleExportCSV = () => {
    if (!works.length) return;
    const headers = [
      'Work_ID',
      'Description',
      'MP_Name',
      'Constituency',
      'State',
      'Recommended_Amount',
      'Sanctioned_Amount',
      'Status',
      'Financial_Year',
    ];
    const rows = works.map((w) => [
      `"${w.work_id}"`,
      `"${(w.work_description || '').replace(/"/g, '""')}"`,
      `"${w.mp_name || ''}"`,
      `"${w.constituency || ''}"`,
      `"${w.state || ''}"`,
      w.recommended_amount ?? '',
      w.sanctioned_amount ?? '',
      `"${w.status || ''}"`,
      `"${w.financial_year || ''}"`,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `mplad_works_page_${page}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const startRecord = total === 0 ? 0 : (page - 1) * limit + 1;
  const endRecord = Math.min(page * limit, total);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16 px-4 sm:px-6 lg:px-8">
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <Database className="w-6 h-6 text-blue-700" />
            MPLAD Works Database
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Tracking <strong>{total.toLocaleString('en-IN')}</strong> verified project records across all States and Union Territories.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadWorks}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
            title="Refresh current page"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleExportCSV}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold shadow-xs transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Panel */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Work ID, description, MP name, constituency, or agency..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => {
                  setSearchTerm('');
                  setActiveSearch('');
                  setPage(1);
                }}
                className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <button
            type="submit"
            className="px-5 py-2 bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold rounded-xl transition-colors shadow-xs"
          >
            Search
          </button>
        </form>

        {/* Dropdown Filters Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">State / UT</label>
            <select
              value={selectedState}
              onChange={(e) => {
                setSelectedState(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-1 focus:ring-blue-600"
            >
              <option value="ALL">All States / UTs</option>
              {filterOptions.states.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Project Status</label>
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-1 focus:ring-blue-600"
            >
              <option value="ALL">All Statuses</option>
              {filterOptions.statuses.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Financial Year</label>
            <select
              value={selectedYear}
              onChange={(e) => {
                setSelectedYear(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-1 focus:ring-blue-600"
            >
              <option value="ALL">All Years</option>
              {filterOptions.financial_years.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end gap-2">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-600 mb-1">Rows Per Page</label>
              <select
                value={limit}
                onChange={(e) => {
                  setLimit(Number(e.target.value));
                  setPage(1);
                }}
                className="w-full px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-1 focus:ring-blue-600"
              >
                <option value={15}>15 per page</option>
                <option value={25}>25 per page</option>
                <option value={50}>50 per page</option>
                <option value={100}>100 per page</option>
              </select>
            </div>
            <button
              onClick={handleResetFilters}
              className="px-3 py-1.5 border border-slate-300 hover:bg-slate-100 text-slate-600 text-xs font-semibold rounded-lg transition-colors"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Results Count and Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50/50">
          <span className="text-xs font-semibold text-slate-600">
            Showing <strong className="text-slate-900">{startRecord.toLocaleString('en-IN')}</strong> to{' '}
            <strong className="text-slate-900">{endRecord.toLocaleString('en-IN')}</strong> of{' '}
            <strong className="text-slate-900">{total.toLocaleString('en-IN')}</strong> works
          </span>
          <span className="text-xs text-slate-500 font-medium">
            Page {page} of {totalPages}
          </span>
        </div>

        {loading ? (
          <div className="p-6">
            <LoadingSkeleton rows={10} />
          </div>
        ) : works.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <Filter className="w-8 h-8 text-slate-400 mx-auto" />
            <h3 className="text-base font-bold text-slate-900">No works match your filter criteria</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Try adjusting your search keywords, selecting 'All States', or resetting filters.
            </p>
            <button
              onClick={handleResetFilters}
              className="mt-2 px-4 py-2 bg-blue-700 text-white rounded-xl text-xs font-semibold"
            >
              Reset All Filters
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4 font-semibold">Work ID & Description</th>
                  <th
                    onClick={() => handleSort('mp_name')}
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-slate-900"
                  >
                    <div className="flex items-center gap-1">
                      <span>MP & Constituency</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('state')}
                    className="py-3 px-4 font-semibold cursor-pointer hover:text-slate-900"
                  >
                    <div className="flex items-center gap-1">
                      <span>State</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('recommended_amount')}
                    className="py-3 px-4 font-semibold text-right cursor-pointer hover:text-slate-900"
                  >
                    <div className="flex items-center justify-end gap-1">
                      <span>Recommended</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('sanctioned_amount')}
                    className="py-3 px-4 font-semibold text-right cursor-pointer hover:text-slate-900"
                  >
                    <div className="flex items-center justify-end gap-1">
                      <span>Sanctioned</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="py-3 px-4 font-semibold text-center">Status</th>
                  <th className="py-3 px-4 font-semibold text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {works.map((w) => (
                  <tr key={w.work_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 max-w-sm">
                      <span className="font-mono text-xs text-blue-700 block font-semibold">{w.work_id}</span>
                      <span className="text-slate-800 text-xs line-clamp-2 font-medium mt-0.5">
                        {w.work_description || 'No description provided'}
                      </span>
                      {w.implementing_agency && (
                        <span className="text-[11px] text-slate-400 block mt-0.5 truncate">
                          IA: {w.implementing_agency}
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="font-bold text-slate-900 block">{w.mp_name || 'N/A'}</span>
                      <span className="text-slate-500">{w.constituency || 'N/A'}</span>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600">{w.state || 'N/A'}</td>
                    <td className="py-3.5 px-4 text-xs font-medium text-slate-700 text-right">
                      {formatCurrency(w.recommended_amount)}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-bold text-right text-emerald-700">
                      {formatCurrency(w.sanctioned_amount)}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <StatusBadge status={w.status} />
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <Link
                        to={`/works/${encodeURIComponent(w.work_id)}`}
                        className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-semibold px-2 py-1 rounded hover:bg-blue-50 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        <div className="p-4 border-t border-slate-200 flex flex-col sm:flex-row justify-between items-center gap-3 bg-slate-50/50">
          <span className="text-xs text-slate-600">
            Page <strong>{page}</strong> of <strong>{totalPages}</strong> ({total.toLocaleString('en-IN')} total projects)
          </span>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setPage(1)}
              disabled={page <= 1}
              className="p-1.5 rounded-lg border border-slate-300 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed text-slate-600 transition-colors"
              title="First Page"
            >
              <ChevronsLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-lg border border-slate-300 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed text-slate-600 transition-colors"
              title="Previous Page"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <span className="px-3 py-1 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg">
              {page}
            </span>

            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg border border-slate-300 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed text-slate-600 transition-colors"
              title="Next Page"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(totalPages)}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg border border-slate-300 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed text-slate-600 transition-colors"
              title="Last Page"
            >
              <ChevronsRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorksPage;
