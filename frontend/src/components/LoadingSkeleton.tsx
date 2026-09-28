import React from 'react';

export const LoadingSkeleton: React.FC<{ rows?: number }> = ({ rows = 4 }) => {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-8 bg-slate-200 rounded-lg w-1/4"></div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-28 bg-white rounded-xl border border-slate-200 shadow-xs"></div>
        ))}
      </div>
      <div className="h-64 bg-white rounded-xl border border-slate-200 shadow-xs"></div>
      <div className="space-y-2">
        {[...Array(rows)].map((_, i) => (
          <div key={i} className="h-12 bg-white rounded-lg border border-slate-200 shadow-xs"></div>
        ))}
      </div>
    </div>
  );
};

export default LoadingSkeleton;
