import React from 'react';
import { EyeOff, ShieldCheck } from 'lucide-react';

interface AuditBadgeProps {
  value: string | number | null | undefined;
  fallbackText?: string;
  type?: 'inline' | 'card' | 'badge';
}

export const AuditBadge: React.FC<AuditBadgeProps> = ({
  value,
  fallbackText = 'Not publicly observed',
  type = 'inline',
}) => {
  const isNull = value === null || value === undefined || value === '';

  if (isNull) {
    if (type === 'badge') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono bg-slate-100 text-slate-500 border border-slate-200" title="Field is NULL in source government records">
          <EyeOff className="w-3 h-3 text-slate-400" />
          {fallbackText}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 text-slate-400 italic text-xs font-normal" title="Not observed in source eSAKSHI data">
        <span className="w-1.5 h-1.5 rounded-full bg-slate-300 inline-block"></span>
        {fallbackText}
      </span>
    );
  }

  if (type === 'badge') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
        <ShieldCheck className="w-3 h-3 text-emerald-600" />
        {value}
      </span>
    );
  }

  return <span>{value}</span>;
};

export default AuditBadge;
