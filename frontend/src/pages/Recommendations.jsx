import React, { useState, useEffect } from 'react';
import { Sparkles, Search, Filter, Star, Info, ShieldCheck } from 'lucide-react';
import { apiService } from '../services/api';
import { Loading } from '../components/Loading';
import { ErrorMessage } from '../components/ErrorMessage';
import { Badge } from '../components/Badge';
import { formatPercent } from '../utils/formatters';

const SAMPLE_CUSTOMERS = [
  { id: '0f8758e5b1c6c6b2156a9dddce128558', label: 'Customer A (0f8758...)' },
  { id: '0000366f3b9a7992bf8c76cfdf3221e2', label: 'Customer B (000036...)' },
  { id: '0000b849f77a49e4a4ce2b2a4ca5be3f', label: 'Customer C (0000b8...)' },
];

export const Recommendations = () => {
  const [customerId, setCustomerId] = useState('0f8758e5b1c6c6b2156a9dddce128558');
  const [inputCustomer, setInputCustomer] = useState('0f8758e5b1c6c6b2156a9dddce128558');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async (cid) => {
    if (!cid) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiService.getCustomerRecommendations(cid.trim(), 10);
      setRecommendations(res || []);
    } catch (err) {
      setError(err?.message || 'Failed to fetch recommendations for this customer.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations(customerId);
  }, [customerId]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (inputCustomer.trim()) {
      setCustomerId(inputCustomer.trim());
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-indigo-400" />
            Personalized Recommendation Engine
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Hybrid Recommendation Engine combining Apriori Association Mining, Cosine/Jaccard Similarity, and Popularity Fallbacks.
          </p>
        </div>
      </div>

      {/* Customer Selector & Search Bar */}
      <div className="glass-card rounded-xl p-5 space-y-4">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Enter customer_id (e.g. 0f8758e5b1c6c6b2156a9dddce128558)..."
              value={inputCustomer}
              onChange={(e) => setInputCustomer(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 bg-slate-950/80 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono text-xs"
            />
          </div>
          <button
            type="submit"
            className="w-full sm:w-auto px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-indigo-600/20"
          >
            Find Recommendations
          </button>
        </form>

        {/* Quick Sample Selector */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 flex items-center gap-1">
            <Info className="w-3.5 h-3.5 text-indigo-400" /> Quick Samples:
          </span>
          {SAMPLE_CUSTOMERS.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setInputCustomer(s.id);
                setCustomerId(s.id);
              }}
              className={`px-2.5 py-1 rounded-md border font-mono text-[11px] transition-all ${
                customerId === s.id
                  ? 'bg-indigo-600 text-white border-indigo-500 shadow-sm'
                  : 'bg-slate-900 text-slate-300 border-slate-800 hover:border-slate-700'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <ErrorMessage
          title="Recommendation Retrieval Notice"
          message={error}
          onRetry={() => fetchRecommendations(customerId)}
        />
      )}

      {/* Content Area */}
      {loading ? (
        <Loading message={`Generating recommendations for customer ${customerId.slice(0, 12)}...`} />
      ) : recommendations.length === 0 ? (
        <div className="glass-card rounded-xl p-12 text-center text-slate-500 space-y-2">
          <p className="text-sm font-semibold text-slate-400">No recommendation records found.</p>
          <p className="text-xs">
            Please select a valid customer ID or choose one of the preset quick samples above.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>
              Showing top <span className="font-semibold text-white">{recommendations.length}</span> recommendations for customer{' '}
              <span className="font-mono text-indigo-400">{customerId}</span>
            </span>
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <ShieldCheck className="w-3.5 h-3.5" /> Direct PostgreSQL Output
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((rec) => (
              <div
                key={rec.rank}
                className="glass-card rounded-xl p-5 border border-slate-800 hover:border-indigo-500/50 transition-all flex flex-col justify-between space-y-3 group"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono">
                        #{rec.rank}
                      </span>
                      <Badge variant={rec.recommendation_source?.includes('Apriori') ? 'purple' : 'default'}>
                        {rec.recommendation_source || 'Algorithm'}
                      </Badge>
                    </div>

                    <div className="text-right">
                      <span className="text-sm font-bold text-emerald-400">
                        {(Number(rec.recommendation_score) * 100).toFixed(1)}%
                      </span>
                      <p className="text-[10px] text-slate-500">Confidence Score</p>
                    </div>
                  </div>

                  <h3 className="text-base font-semibold text-white capitalize mt-3 group-hover:text-indigo-300 transition-colors">
                    {rec.product_category ? rec.product_category.replace(/_/g, ' ') : 'General Merchandise'}
                  </h3>

                  <p className="text-xs font-mono text-slate-400 mt-1 truncate" title={rec.product_id}>
                    Product: {rec.product_id}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800/80 space-y-1.5 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Apriori Association Score:</span>
                    <span className="font-semibold text-slate-300">
                      {(Number(rec.apriori_score || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Cosine/Jaccard Similarity:</span>
                    <span className="font-semibold text-slate-300">
                      {(Number(rec.similarity_score || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Popularity Prior:</span>
                    <span className="font-semibold text-slate-300">
                      {(Number(rec.popularity_score || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
