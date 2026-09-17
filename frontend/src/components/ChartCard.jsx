import React from 'react';

export const ChartCard = ({
  title,
  subtitle = null,
  children,
  action = null,
  className = '',
}) => {
  return (
    <div className={`glass-card rounded-xl p-5 flex flex-col justify-between ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100">{title}</h3>
          {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
        {action && <div>{action}</div>}
      </div>
      <div className="w-full flex-1 min-h-[260px] flex items-center justify-center">
        {children}
      </div>
    </div>
  );
};

export default ChartCard;
