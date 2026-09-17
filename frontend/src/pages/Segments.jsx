import React, { useState, useEffect } from 'react';
import { PieChart as PieIcon, Users, DollarSign, ShoppingBag, Layers, Activity } from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { apiService } from '../services/api';
import { ChartCard } from '../components/ChartCard';
import { DataTable } from '../components/DataTable';
import { Badge } from '../components/Badge';
import { Loading } from '../components/Loading';
import { ErrorMessage } from '../components/ErrorMessage';
import { formatCurrency, formatNumber, formatPercent } from '../utils/formatters';

const CLUSTER_COLORS = ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'];

const CLUSTER_NAMES = [
  'Cluster 0: Mainstream Single-Order',
  'Cluster 1: Multi-Order Repeat Customers',
  'Cluster 2: VIP High-Spending Segment',
  'Cluster 3: Bulk / High-Volume Buyers',
];

const CLUSTER_DESCRIPTIONS = [
  'Largest group characterized by single purchases, moderate spending (~R$ 102), and low order counts.',
  'Repeat consumers with ~2.1 orders, higher average spending (~R$ 248), and substantial freight investment.',
  'High-value customers with very high spending (~R$ 1,033+ per order) and luxury transaction values.',
  'Consumers buying multiple product units with higher average freight and multi-item baskets.',
];

export const Segments = () => {
  const [profiles, setProfiles] = useState([]);
  const [summaryList, setSummaryList] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(2);
  const [clusterCustomers, setClusterCustomers] = useState(null);
  const [customerPage, setCustomerPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [custLoading, setCustLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProfiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const [pRes, sRes] = await Promise.all([
        apiService.getSegmentProfiles(),
        apiService.getSegments(),
      ]);
      setProfiles(pRes || []);
      setSummaryList(sRes || []);
    } catch (err) {
      setError(err?.message || 'Failed to load customer segmentation data.');
    } finally {
      setLoading(false);
    }
  };

  const fetchClusterCustomers = async () => {
    setCustLoading(true);
    try {
      const res = await apiService.getSegmentCustomers(selectedCluster, {
        page: customerPage,
        page_size: 10,
      });
      setClusterCustomers(res);
    } catch (err) {
      console.error('Failed to load cluster customers:', err);
    } finally {
      setCustLoading(false);
    }
  };

  useEffect(() => {
    fetchProfiles();
  }, []);

  useEffect(() => {
    fetchClusterCustomers();
  }, [selectedCluster, customerPage]);

  if (loading) {
    return <Loading message="Loading Spark K-Means customer segmentation profiles..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Error loading customer segments"
        message={error}
        onRetry={fetchProfiles}
      />
    );
  }

  // Distribution chart data
  const pieData = (profiles || []).map((p) => ({
    name: `Cluster ${p.cluster}`,
    value: Number(p.customers),
    label: CLUSTER_NAMES[p.cluster] || `Cluster ${p.cluster}`,
  }));

  // Average spending chart data
  const spendingBarData = (profiles || []).map((p) => ({
    name: `Cluster ${p.cluster}`,
    avgSpending: Number(p.avg_spending),
    avgAOV: Number(p.avg_order_value),
  }));

  const customerColumns = [
    {
      header: 'Customer ID',
      accessor: 'customer_unique_id',
      render: (val) => (
        <span className="text-indigo-400 font-semibold font-mono" title={val}>
          {val}
        </span>
      ),
    },
    {
      header: 'Total Orders',
      accessor: 'total_orders',
      align: 'center',
      render: (val) => <span className="font-sans text-slate-200">{val}</span>,
    },
    {
      header: 'Total Spending',
      accessor: 'total_spending',
      align: 'right',
      render: (val) => (
        <span className="font-sans font-semibold text-emerald-400">{formatCurrency(val)}</span>
      ),
    },
    {
      header: 'Average Order Value',
      accessor: 'average_order_value',
      align: 'right',
      render: (val) => <span className="font-sans text-slate-300">{formatCurrency(val)}</span>,
    },
    {
      header: 'Total Products',
      accessor: 'total_products',
      align: 'center',
      render: (val) => <span className="font-sans text-slate-300">{val}</span>,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <PieIcon className="w-6 h-6 text-indigo-400" />
            Customer Segmentation (K-Means Clustering)
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            4-Cluster customer segmentation trained on Spark ML and served through PostgreSQL.
          </p>
        </div>
      </div>

      {/* Row 1: 4 Cluster Detail Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {profiles.map((p) => {
          const isSelected = selectedCluster === p.cluster;
          return (
            <div
              key={p.cluster}
              onClick={() => {
                setSelectedCluster(p.cluster);
                setCustomerPage(1);
              }}
              className={`glass-card rounded-xl p-5 cursor-pointer transition-all border ${
                isSelected
                  ? 'border-indigo-500 bg-slate-900/90 shadow-indigo-500/10 ring-1 ring-indigo-500'
                  : 'hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <Badge variant={`cluster${p.cluster}`}>
                  Cluster {p.cluster}
                </Badge>
                <span className="text-xs text-slate-400 font-medium">
                  {formatNumber(p.customers)} customers
                </span>
              </div>

              <h3 className="text-sm font-bold text-white mt-2.5">
                {CLUSTER_NAMES[p.cluster]}
              </h3>

              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed line-clamp-2">
                {CLUSTER_DESCRIPTIONS[p.cluster]}
              </p>

              <div className="mt-4 pt-3 border-t border-slate-800 space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Avg Spending:</span>
                  <span className="font-semibold text-emerald-400">{formatCurrency(p.avg_spending)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Avg AOV:</span>
                  <span className="font-semibold text-slate-200">{formatCurrency(p.avg_order_value)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Avg Orders:</span>
                  <span className="font-semibold text-slate-300">{Number(p.avg_orders).toFixed(2)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Row 2: Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Customer Population Distribution */}
        <ChartCard
          title="Customer Segment Population Share"
          subtitle="Proportion of total 95,420 unique customers across clusters"
        >
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={95}
                paddingAngle={4}
                dataKey="value"
              >
                {pieData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={CLUSTER_COLORS[index % CLUSTER_COLORS.length]}
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
                  `${formatNumber(val)} customers (${formatPercent((val / 95420) * 100)})`,
                  props.payload.label,
                ]}
              />
              <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Average Spending Comparison */}
        <ChartCard
          title="Average Spending & AOV Comparison (R$)"
          subtitle="Mean spending profile per cluster segment"
        >
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={spendingBarData} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                tickFormatter={(v) => `R$ ${v}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
                formatter={(v, name) => [
                  formatCurrency(v),
                  name === 'avgSpending' ? 'Average Spending' : 'Average Order Value',
                ]}
              />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
              <Bar dataKey="avgSpending" name="Average Spending" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="avgAOV" name="Average AOV" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Row 3: Cluster Customer Explorer */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Users className="w-4 h-4 text-indigo-400" />
            Customers in {CLUSTER_NAMES[selectedCluster]}
          </h3>
          <span className="text-xs text-slate-400 font-mono">
            {formatNumber(clusterCustomers?.total || 0)} Total Members
          </span>
        </div>

        <DataTable
          columns={customerColumns}
          data={clusterCustomers?.data || []}
          loading={custLoading}
          page={clusterCustomers?.page || 1}
          pageSize={10}
          total={clusterCustomers?.total || 0}
          onPageChange={(p) => setCustomerPage(p)}
        />
      </div>
    </div>
  );
};

export default Segments;
