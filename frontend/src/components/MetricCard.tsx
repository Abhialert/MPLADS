import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    label: string;
    positive?: boolean;
    neutral?: boolean;
  };
  accentColor?: 'indigo' | 'emerald' | 'amber' | 'cyan' | 'rose' | 'blue' | 'slate';
  tooltip?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  accentColor = 'blue',
  tooltip,
}) => {
  const colorMap = {
    blue: {
      border: 'hover:border-blue-300',
      iconBg: 'bg-blue-50 text-blue-700',
      textAccent: 'text-blue-700',
      glow: 'hover:shadow-md hover:shadow-blue-500/5',
    },
    indigo: {
      border: 'hover:border-indigo-300',
      iconBg: 'bg-indigo-50 text-indigo-700',
      textAccent: 'text-indigo-700',
      glow: 'hover:shadow-md hover:shadow-indigo-500/5',
    },
    emerald: {
      border: 'hover:border-emerald-300',
      iconBg: 'bg-emerald-50 text-emerald-700',
      textAccent: 'text-emerald-700',
      glow: 'hover:shadow-md hover:shadow-emerald-500/5',
    },
    amber: {
      border: 'hover:border-amber-300',
      iconBg: 'bg-amber-50 text-amber-700',
      textAccent: 'text-amber-700',
      glow: 'hover:shadow-md hover:shadow-amber-500/5',
    },
    cyan: {
      border: 'hover:border-cyan-300',
      iconBg: 'bg-cyan-50 text-cyan-700',
      textAccent: 'text-cyan-700',
      glow: 'hover:shadow-md hover:shadow-cyan-500/5',
    },
    rose: {
      border: 'hover:border-rose-300',
      iconBg: 'bg-rose-50 text-rose-700',
      textAccent: 'text-rose-700',
      glow: 'hover:shadow-md hover:shadow-rose-500/5',
    },
    slate: {
      border: 'hover:border-slate-300',
      iconBg: 'bg-slate-100 text-slate-700',
      textAccent: 'text-slate-700',
      glow: '',
    },
  };

  const scheme = colorMap[accentColor];

  return (
    <div
      className={`group relative rounded-xl border border-slate-200 bg-white p-5 shadow-xs transition-all duration-200 ${scheme.border} ${scheme.glow}`}
      title={tooltip}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <div className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            {value}
          </div>
        </div>
        <div className={`rounded-xl p-2.5 ${scheme.iconBg}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>

      {(subtitle || trend) && (
        <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-2.5 text-xs">
          {subtitle && (
            <span className="text-slate-500 truncate">{subtitle}</span>
          )}
          {trend && (
            <span
              className={`inline-flex items-center font-medium ${
                trend.neutral
                  ? 'text-slate-500'
                  : trend.positive
                  ? 'text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full'
                  : 'text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full'
              }`}
            >
              {trend.label}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default MetricCard;
