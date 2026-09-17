import React from 'react';

export const Badge = ({ children, variant = 'default', size = 'md' }) => {
  const variants = {
    default: 'bg-slate-800 text-slate-300 border-slate-700',
    primary: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    danger: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    cluster0: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    cluster1: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    cluster2: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    cluster3: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-md border ${variants[variant] || variants.default} ${sizes[size] || sizes.md}`}
    >
      {children}
    </span>
  );
};

export default Badge;
