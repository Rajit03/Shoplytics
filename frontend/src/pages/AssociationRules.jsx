import React, { useState, useEffect } from 'react';
import { GitFork, Filter, ArrowRight, TrendingUp, Info } from 'lucide-react';
import { apiService } from '../services/api';
import { DataTable } from '../components/DataTable';
import { Badge } from '../components/Badge';
import { ErrorMessage } from '../components/ErrorMessage';
import { formatNumber } from '../utils/formatters';

export const AssociationRules = () => {
  const [rules, setRules] = useState([]);
  const [minLift, setMinLift] = useState('');
  const [minConfidence, setMinConfidence] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRules = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        limit: 50,
      };
      if (minLift) params.min_lift = Number(minLift);
      if (minConfidence) params.min_confidence = Number(minConfidence);

      const res = await apiService.getAssociationRules(params);
      setRules(res || []);
    } catch (err) {
      setError(err?.message || 'Failed to fetch association rules.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, [minLift, minConfidence]);

  const columns = [
    {
      header: 'Antecedent (Basket Product/Category)',
      accessor: 'antecedent',
      render: (val, row) => (
        <div className="space-y-1">
          <p className="font-mono text-indigo-300 font-semibold text-xs truncate max-w-[200px]" title={val}>
            {val}
          </p>
          {row.antecedent_categories && (
            <p className="font-sans text-[11px] text-slate-400 capitalize">
              {row.antecedent_categories.replace(/;/g, ', ').replace(/_/g, ' ')}
            </p>
          )}
        </div>
      ),
    },
    {
      header: 'Relationship',
      accessor: 'id',
      align: 'center',
      render: () => (
        <span className="text-slate-500 flex items-center justify-center">
          <ArrowRight className="w-4 h-4 text-indigo-400" />
        </span>
      ),
    },
    {
      header: 'Consequent (Associated Item)',
      accessor: 'consequent',
      render: (val, row) => (
        <div className="space-y-1">
          <p className="font-mono text-purple-300 font-semibold text-xs truncate max-w-[200px]" title={val}>
            {val}
          </p>
          {row.consequent_categories && (
            <p className="font-sans text-[11px] text-slate-400 capitalize">
              {row.consequent_categories.replace(/;/g, ', ').replace(/_/g, ' ')}
            </p>
          )}
        </div>
      ),
    },
    {
      header: 'Support',
      accessor: 'support',
      align: 'right',
      render: (val) => (
        <span className="font-sans text-slate-300">
          {Number(val).toFixed(6)}
        </span>
      ),
    },
    {
      header: 'Confidence',
      accessor: 'confidence',
      align: 'right',
      render: (val) => (
        <span className="font-sans font-semibold text-indigo-400">
          {(Number(val) * 100).toFixed(1)}%
        </span>
      ),
    },
    {
      header: 'Lift',
      accessor: 'lift',
      align: 'right',
      render: (val) => (
        <span className="font-sans font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          {Number(val).toFixed(2)}x
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <GitFork className="w-6 h-6 text-indigo-400" />
            Market Basket Association Rules (Apriori Algorithm)
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Cross-selling and co-purchasing affinity rules mined from distributed transaction baskets.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-card rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">Min Lift:</span>
            <select
              value={minLift}
              onChange={(e) => setMinLift(e.target.value)}
              className="bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Lift Values</option>
              <option value="1000">Lift &gt; 1,000x</option>
              <option value="5000">Lift &gt; 5,000x</option>
              <option value="10000">Lift &gt; 10,000x</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">Min Confidence:</span>
            <select
              value={minConfidence}
              onChange={(e) => setMinConfidence(e.target.value)}
              className="bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Confidence</option>
              <option value="0.25">Confidence &gt; 25%</option>
              <option value="0.50">Confidence &gt; 50%</option>
              <option value="0.75">Confidence &gt; 75%</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-slate-400 flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-indigo-400" />
          Sorted by <span className="font-semibold text-emerald-400">Lift (Impact Ratio)</span>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <ErrorMessage
          title="Error loading association rules"
          message={error}
          onRetry={fetchRules}
        />
      )}

      {/* Table */}
      <DataTable
        columns={columns}
        data={rules}
        loading={loading}
        pageSize={rules.length || 20}
        total={rules.length}
      />
    </div>
  );
};

export default AssociationRules;
