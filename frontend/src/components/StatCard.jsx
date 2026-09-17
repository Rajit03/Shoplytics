import React from 'react';

export const StatCard = ({
  title,
  value,
  subtitle = null,
  icon: Icon = null,
  trend = null,
  color = 'indigo',
}) => {
  const colorMap = {
    indigo: 'from-indigo-500/20 to-indigo-500/5 text-indigo-400 border-indigo-500/20',
    emerald: 'from-emerald-500/20 to-emerald-500/5 text-emerald-400 border-emerald-500/20',
    amber: 'from-amber-500/20 to-amber-500/5 text-amber-400 border-amber-500/20',
    rose: 'from-rose-500/20 to-rose-500/5 text-rose-400 border-rose-500/20',
    blue: 'from-blue-500/20 to-blue-500/5 text-blue-400 border-blue-500/20',
    purple: 'from-purple-500/20 to-purple-500/5 text-purple-400 border-purple-500/20',
    cyan: 'from-cyan-500/20 to-cyan-500/5 text-cyan-400 border-cyan-500/20',
  };

  const selectedTheme = colorMap[color] || colorMap.indigo;

  return (
    <div className="glass-card rounded-xl p-5 relative overflow-hidden group">
      <div
        className={`absolute -right-6 -bottom-6 w-24 h-24 rounded-full bg-gradient-to-br ${selectedTheme} opacity-30 group-hover:scale-125 transition-transform duration-500`}
      />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1.5 tracking-tight">{value}</h3>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
          {trend && (
            <p className="text-xs mt-2 flex items-center space-x-1">
              <span className={trend.positive ? 'text-emerald-400' : 'text-rose-400'}>
                {trend.value}
              </span>
              <span className="text-slate-500">{trend.label}</span>
            </p>
          )}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg bg-gradient-to-br ${selectedTheme} border shadow-inner`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard;
