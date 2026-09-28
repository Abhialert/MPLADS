import React from 'react';
import { CheckCircle2, Clock, AlertCircle, HelpCircle, FileText } from 'lucide-react';

interface StatusBadgeProps {
  status: string | null | undefined;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const normalized = (status || '').toUpperCase().trim();

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold',
  }[size];

  if (normalized === 'COMPLETED') {
    return (
      <span className={`inline-flex items-center rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-xs ${sizeClasses}`}>
        <CheckCircle2 className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5 text-emerald-600'} />
        <span>COMPLETED</span>
      </span>
    );
  }

  if (normalized === 'ONGOING' || normalized === 'IN_PROGRESS' || normalized === 'UNDER_EXECUTION') {
    return (
      <span className={`inline-flex items-center rounded-full bg-amber-50 text-amber-700 border border-amber-200 shadow-xs ${sizeClasses}`}>
        <Clock className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5 text-amber-600'} />
        <span>ONGOING</span>
      </span>
    );
  }

  if (normalized === 'SANCTIONED') {
    return (
      <span className={`inline-flex items-center rounded-full bg-blue-50 text-blue-700 border border-blue-200 shadow-xs ${sizeClasses}`}>
        <FileText className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5 text-blue-600'} />
        <span>SANCTIONED</span>
      </span>
    );
  }

  if (normalized === 'RECOMMENDED') {
    return (
      <span className={`inline-flex items-center rounded-full bg-sky-50 text-sky-700 border border-sky-200 shadow-xs ${sizeClasses}`}>
        <FileText className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5 text-sky-600'} />
        <span>RECOMMENDED</span>
      </span>
    );
  }

  if (normalized === 'CANCELLED' || normalized === 'REJECTED') {
    return (
      <span className={`inline-flex items-center rounded-full bg-rose-50 text-rose-700 border border-rose-200 shadow-xs ${sizeClasses}`}>
        <AlertCircle className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5 text-rose-600'} />
        <span>{normalized}</span>
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center rounded-full bg-slate-100 text-slate-600 border border-slate-200 ${sizeClasses}`}>
      <HelpCircle className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5 text-slate-400'} />
      <span>{status || 'Not publicly observed'}</span>
    </span>
  );
};

export default StatusBadge;
