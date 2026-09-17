import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  User,
  ShoppingBag,
  Sparkles,
  PieChart,
  Calendar,
  CreditCard,
  Truck,
  ExternalLink
} from 'lucide-react';
import { apiService } from '../services/api';
import { Loading } from '../components/Loading';
import { ErrorMessage } from '../components/ErrorMessage';
import { Badge } from '../components/Badge';
import { StatCard } from '../components/StatCard';
import { formatCurrency, formatPercent, formatDate } from '../utils/formatters';

export const CustomerDetails = () => {
  const { customerId } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiService.getCustomerProfile(customerId);
      setProfile(res);
    } catch (err) {
      setError(err?.message || 'Failed to load customer profile.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (customerId) {
      fetchProfile();
    }
  }, [customerId]);

  if (loading) {
    return <Loading message={`Loading full profile for customer ${customerId}...`} />;
  }

  if (error || !profile) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate('/customers')}
          className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Customers
        </button>
        <ErrorMessage
          title="Customer Not Found"
          message={error || `Could not find records for ${customerId}`}
          onRetry={fetchProfile}
        />
      </div>
    );
  }

  const { customer, cluster_profile, order_history, recommendations } = profile;

  return (
    <div className="space-y-6">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <button
          onClick={() => navigate('/customers')}
          className="inline-flex items-center gap-2 text-sm font-medium text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Customers List
        </button>
      </div>

      {/* Customer Header Badge Card */}
      <div className="glass-card rounded-xl p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="p-3.5 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <User className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold text-white tracking-tight font-mono">
                  {customer.customer_unique_id}
                </h2>
                {customer.cluster !== null && (
                  <Badge variant={`cluster${customer.cluster}`}>
                    Cluster {customer.cluster}
                  </Badge>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-1">
                E-Commerce Consumer Profile · Brazilian Olist Dataset
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Row 1: Customer Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Spending"
          value={formatCurrency(customer.total_spending)}
          subtitle={`${customer.total_products} items purchased`}
          icon={CreditCard}
          color="emerald"
        />
        <StatCard
          title="Total Orders"
          value={customer.total_orders}
          subtitle={`Avg ${formatCurrency(customer.average_order_value)} / order`}
          icon={ShoppingBag}
          color="indigo"
        />
        <StatCard
          title="Average Order Value"
          value={formatCurrency(customer.average_order_value)}
          subtitle="Net transaction value"
          icon={PieChart}
          color="purple"
        />
        <StatCard
          title="Total Freight Paid"
          value={formatCurrency(customer.total_freight)}
          subtitle="Logistics & shipping"
          icon={Truck}
          color="amber"
        />
      </div>

      {/* Row 2: Cluster Profile & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Assigned Cluster Analysis */}
        <div className="glass-card rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <PieChart className="w-4 h-4 text-purple-400" />
              K-Means Cluster Profile
            </h3>
            <span className="text-xs font-mono text-purple-400">Cluster {customer.cluster}</span>
          </div>

          {cluster_profile ? (
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-400">Cluster Population:</span>
                <span className="font-semibold text-slate-200">{cluster_profile.cluster_size?.toLocaleString()} customers</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-400">Cluster Average Spending:</span>
                <span className="font-semibold text-emerald-400">{formatCurrency(cluster_profile.avg_spending)}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-400">Cluster Average AOV:</span>
                <span className="font-semibold text-slate-200">{formatCurrency(cluster_profile.avg_order_value)}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                <span className="text-slate-400">Cluster Average Orders:</span>
                <span className="font-semibold text-slate-200">{cluster_profile.avg_orders?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-400">Spending Range:</span>
                <span className="font-semibold text-slate-300">
                  {formatCurrency(cluster_profile.min_spending)} – {formatCurrency(cluster_profile.max_spending)}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500">No cluster profile metrics available.</p>
          )}
        </div>

        {/* Right Columns: Personalized Recommendations */}
        <div className="glass-card rounded-xl p-5 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                Personalized Recommendations
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Generated from Hybrid Recommendation Engine (Apriori + Cosine Similarity + Popularity)
              </p>
            </div>
          </div>

          {recommendations && recommendations.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {recommendations.map((rec) => (
                <div
                  key={rec.rank}
                  className="rounded-xl p-3.5 bg-slate-950/60 border border-slate-800 hover:border-indigo-500/50 transition-all space-y-2"
                >
                  <div className="flex items-start justify-between">
                    <span className="text-[11px] font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                      Rank #{rec.rank}
                    </span>
                    <span className="text-xs font-semibold text-emerald-400">
                      Score: {(rec.score * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-slate-200 capitalize">
                      {rec.category ? rec.category.replace(/_/g, ' ') : 'General Merchandise'}
                    </h4>
                    <p className="text-[11px] font-mono text-slate-400 truncate" title={rec.product_id}>
                      {rec.product_id}
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-900">
                    <span>Source: {rec.source}</span>
                    {rec.weight_g && <span>{rec.weight_g}g</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500 text-xs">
              No recommendations generated for this customer ID yet.
            </div>
          )}
        </div>
      </div>

      {/* Row 3: Order History Table */}
      <div className="glass-card rounded-xl p-5 space-y-4">
        <h3 className="text-base font-semibold text-white flex items-center gap-2">
          <Calendar className="w-4 h-4 text-emerald-400" />
          Recent Order History
        </h3>
        {order_history && order_history.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Order ID</th>
                  <th className="py-2.5 px-3">Date</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {order_history.map((ord, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 text-indigo-300 font-semibold">{ord.order_id}</td>
                    <td className="py-2.5 px-3 text-slate-300 font-sans">{formatDate(ord.purchase_timestamp)}</td>
                    <td className="py-2.5 px-3 text-slate-300 font-sans">
                      {ord.category ? ord.category.replace(/_/g, ' ') : '—'}
                    </td>
                    <td className="py-2.5 px-3 font-sans">
                      <Badge variant={ord.status === 'delivered' ? 'success' : 'warning'}>
                        {ord.status}
                      </Badge>
                    </td>
                    <td className="py-2.5 px-3 text-right text-emerald-400 font-semibold">
                      {formatCurrency(ord.value)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-slate-500">No order history line items available.</p>
        )}
      </div>
    </div>
  );
};

export default CustomerDetails;
