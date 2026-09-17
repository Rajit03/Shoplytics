import React from 'react';
import {
  Users,
  ShoppingCart,
  Package,
  DollarSign,
  TrendingUp,
  CheckCircle2,
  XCircle,
  BarChart3,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

import { useApi } from '../hooks/useApi';
import { apiService } from '../services/api';
import { StatCard } from '../components/StatCard';
import { ChartCard } from '../components/ChartCard';
import { Loading } from '../components/Loading';
import { ErrorMessage } from '../components/ErrorMessage';
import { formatCurrency, formatNumber, formatCompactNumber, formatPercent } from '../utils/formatters';

const STATUS_COLORS = {
  delivered: '#10b981',
  shipped: '#6366f1',
  canceled: '#f43f5e',
  unavailable: '#f59e0b',
  invoiced: '#8b5cf6',
  processing: '#06b6d4',
  created: '#64748b',
  approved: '#3b82f6',
};

export const Dashboard = () => {
  const { data: summary, loading: l1, error: e1, refetch: r1 } = useApi(apiService.getDashboardSummary);
  const { data: monthly, loading: l2, error: e2, refetch: r2 } = useApi(apiService.getMonthlySales);
  const { data: categories, loading: l3, error: e3, refetch: r3 } = useApi(() => apiService.getCategorySales(8));
  const { data: topProducts, loading: l4, error: e4, refetch: r4 } = useApi(() => apiService.getProductSales(5));
  const { data: topSellers, loading: l5, error: e5, refetch: r5 } = useApi(() => apiService.getSellerSales(5));
  const { data: orderStatuses, loading: l6, error: e6, refetch: r6 } = useApi(apiService.getOrderStatus);

  const loading = l1 || l2 || l3 || l4 || l5 || l6;
  const error = e1 || e2 || e3 || e4 || e5 || e6;

  const handleRetryAll = () => {
    r1(); r2(); r3(); r4(); r5(); r6();
  };

  if (loading && !summary) {
    return <Loading message="Aggregating distributed analytics & dashboard KPIs..." />;
  }

  if (error && !summary) {
    return (
      <ErrorMessage
        title="Failed to load dashboard metrics"
        message={error}
        onRetry={handleRetryAll}
      />
    );
  }

  // Process monthly sales for chart
  const monthlyChartData = (monthly || []).map((m) => ({
    name: `${m.order_month_name.slice(0, 3)} ${m.order_year}`,
    revenue: m.revenue,
    orders: m.orders_count,
    net: m.net_sales,
  }));

  // Process category sales for chart
  const categoryChartData = (categories || []).map((c) => ({
    category: c.category.replace(/_/g, ' '),
    revenue: c.revenue,
    items: c.items_sold,
  }));

  // Process order status for pie chart
  const statusPieData = (orderStatuses || []).map((s) => ({
    name: s.order_status,
    value: s.count,
    percentage: s.percentage,
  }));

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Executive Analytics Dashboard</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Real-time e-commerce performance derived from Spark Analytics and PostgreSQL serving layer.
          </p>
        </div>
      </div>

      {/* Row 1: KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Sales (Gross)"
          value={formatCurrency(summary?.total_sales)}
          subtitle={`Freight: ${formatCurrency(summary?.total_freight)}`}
          icon={DollarSign}
          color="indigo"
        />
        <StatCard
          title="Total Orders"
          value={formatNumber(summary?.total_orders)}
          subtitle={`Delivered: ${formatNumber(summary?.delivered_orders)}`}
          icon={ShoppingCart}
          color="emerald"
        />
        <StatCard
          title="Total Customers"
          value={formatNumber(summary?.total_customers)}
          subtitle={`Segments: ${summary?.total_clusters} K-Means Clusters`}
          icon={Users}
          color="purple"
        />
        <StatCard
          title="Average Order Value"
          value={formatCurrency(summary?.average_order_value)}
          subtitle={`Catalog: ${formatNumber(summary?.total_products)} Products`}
          icon={TrendingUp}
          color="amber"
        />
      </div>

      {/* Row 1.5: Secondary KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card rounded-xl p-4 flex items-center justify-between border-l-4 border-emerald-500">
          <div>
            <p className="text-xs text-slate-400 font-medium">Delivered Orders</p>
            <p className="text-lg font-bold text-white mt-0.5">{formatNumber(summary?.delivered_orders)}</p>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              {formatPercent((summary?.delivered_orders / (summary?.total_orders || 1)) * 100)}
            </span>
            <p className="text-[10px] text-slate-500 mt-1">Fulfillment Rate</p>
          </div>
        </div>

        <div className="glass-card rounded-xl p-4 flex items-center justify-between border-l-4 border-rose-500">
          <div>
            <p className="text-xs text-slate-400 font-medium">Cancelled Orders</p>
            <p className="text-lg font-bold text-white mt-0.5">{formatNumber(summary?.cancelled_orders)}</p>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
              {formatPercent((summary?.cancelled_orders / (summary?.total_orders || 1)) * 100)}
            </span>
            <p className="text-[10px] text-slate-500 mt-1">Cancellation Rate</p>
          </div>
        </div>

        <div className="glass-card rounded-xl p-4 flex items-center justify-between border-l-4 border-indigo-500">
          <div>
            <p className="text-xs text-slate-400 font-medium">Active Categories</p>
            <p className="text-lg font-bold text-white mt-0.5">{summary?.active_categories} Categories</p>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
              {formatCompactNumber(summary?.total_products)} SKUs
            </span>
            <p className="text-[10px] text-slate-500 mt-1">Catalog Depth</p>
          </div>
        </div>
      </div>

      {/* Row 2: Monthly Sales & Revenue Trend (Area Chart) */}
      <ChartCard
        title="Revenue & Order Volume Growth Trend"
        subtitle="Chronological monthly revenue in Brazilian Real (R$) and total orders count"
        className="w-full"
      >
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={monthlyChartData} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => `R$ ${formatCompactNumber(v)}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '0.5rem',
                fontSize: '12px',
                color: '#f8fafc',
              }}
              formatter={(value, name) => [
                name === 'revenue' ? formatCurrency(value) : formatNumber(value),
                name === 'revenue' ? 'Gross Revenue' : 'Orders Count',
              ]}
            />
            <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
            <Area
              type="monotone"
              dataKey="revenue"
              name="Gross Revenue"
              stroke="#6366f1"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#revenueGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Row 3: Category Revenue + Order Status Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Sales Bar Chart */}
        <ChartCard
          title="Top Product Categories by Revenue"
          subtitle="Revenue generated per English category (R$)"
          className="lg:col-span-2"
        >
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={categoryChartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
              <XAxis
                type="number"
                stroke="#64748b"
                fontSize={11}
                tickFormatter={(v) => `R$ ${formatCompactNumber(v)}`}
              />
              <YAxis
                type="category"
                dataKey="category"
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                width={120}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
                formatter={(val) => [formatCurrency(val), 'Revenue']}
              />
              <Bar dataKey="revenue" fill="#818cf8" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Order Status Distribution Donut Chart */}
        <ChartCard
          title="Order Fulfillment Status"
          subtitle="Percentage distribution of order lifecycle"
        >
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={statusPieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={85}
                paddingAngle={4}
                dataKey="value"
              >
                {statusPieData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={STATUS_COLORS[entry.name] || '#94a3b8'}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
                formatter={(val, name, props) => [
                  `${formatNumber(val)} orders (${props.payload.percentage}%)`,
                  name,
                ]}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Row 4: Top Products & Top Sellers Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Products */}
        <div className="glass-card rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-base font-semibold text-white">Top 5 Best-Selling Products</h3>
              <p className="text-xs text-slate-400">Ranked by revenue contribution</p>
            </div>
            <Package className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 border-b border-slate-800 pb-2">
                <tr>
                  <th className="py-2">Product ID</th>
                  <th className="py-2">Category</th>
                  <th className="py-2 text-right">Units</th>
                  <th className="py-2 text-right">Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {(topProducts || []).map((p) => (
                  <tr key={p.product_id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 text-indigo-300 font-semibold truncate max-w-[120px]" title={p.product_id}>
                      {p.product_id.slice(0, 10)}...
                    </td>
                    <td className="py-2.5 text-slate-300 font-sans">{p.product_category_name_english.replace(/_/g, ' ')}</td>
                    <td className="py-2.5 text-right text-slate-300 font-sans">{p.units_sold}</td>
                    <td className="py-2.5 text-right text-emerald-400 font-semibold">{formatCurrency(p.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Sellers */}
        <div className="glass-card rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-base font-semibold text-white">Top 5 Merchant Sellers</h3>
              <p className="text-xs text-slate-400">Ranked by gross sales volume</p>
            </div>
            <TrendingUp className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 border-b border-slate-800 pb-2">
                <tr>
                  <th className="py-2">Seller ID</th>
                  <th className="py-2 text-right">Orders</th>
                  <th className="py-2 text-right">Items Sold</th>
                  <th className="py-2 text-right">Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {(topSellers || []).map((s) => (
                  <tr key={s.seller_id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 text-purple-300 font-semibold truncate max-w-[140px]" title={s.seller_id}>
                      {s.seller_id.slice(0, 12)}...
                    </td>
                    <td className="py-2.5 text-right text-slate-300 font-sans">{s.orders_count}</td>
                    <td className="py-2.5 text-right text-slate-300 font-sans">{s.items_sold}</td>
                    <td className="py-2.5 text-right text-emerald-400 font-semibold">{formatCurrency(s.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
