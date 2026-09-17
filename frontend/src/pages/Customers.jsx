import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Users, Sparkles } from 'lucide-react';
import { apiService } from '../services/api';
import { DataTable } from '../components/DataTable';
import { Badge } from '../components/Badge';
import { ErrorMessage } from '../components/ErrorMessage';
import { formatCurrency, formatNumber } from '../utils/formatters';

export const Customers = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [clusterFilter, setClusterFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [customersData, setCustomersData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      if (searchQuery.trim()) {
        const res = await apiService.searchCustomers(
          searchQuery.trim(),
          clusterFilter !== '' ? Number(clusterFilter) : null,
          20
        );
        setCustomersData({
          page: 1,
          page_size: 20,
          total: res.length,
          data: res,
        });
      } else {
        const params = {
          page,
          page_size: pageSize,
        };
        if (clusterFilter !== '') {
          params.cluster = Number(clusterFilter);
        }
        const res = await apiService.getCustomers(params);
        setCustomersData(res);
      }
    } catch (err) {
      setError(err?.message || 'Failed to fetch customer data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [page, clusterFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchCustomers();
  };

  const columns = [
    {
      header: 'Customer Unique ID',
      accessor: 'customer_unique_id',
      render: (val) => (
        <span className="text-indigo-400 font-semibold hover:underline flex items-center gap-1.5">
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
      header: 'Total Freight',
      accessor: 'total_freight',
      align: 'right',
      render: (val) => <span className="font-sans text-slate-400">{formatCurrency(val)}</span>,
    },
    {
      header: 'Cluster Segment',
      accessor: 'cluster',
      align: 'center',
      render: (val) => {
        if (val === null || val === undefined) return <Badge variant="default">Unassigned</Badge>;
        const variant = `cluster${val}`;
        const labels = ['Cluster 0 (Mainstream)', 'Cluster 1 (Repeat High Freight)', 'Cluster 2 (VIP High Spenders)', 'Cluster 3 (Bulk Buyers)'];
        return <Badge variant={variant}>{labels[val] || `Cluster ${val}`}</Badge>;
      },
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Users className="w-6 h-6 text-indigo-400" />
            Customer Analytics
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Browse 95,420 unique customer profiles segmented by Spark K-Means clustering.
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-card rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by customer_unique_id prefix (e.g. 00003)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={clusterFilter}
            onChange={(e) => {
              setClusterFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-950/80 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Customer Clusters</option>
            <option value="0">Cluster 0 (Mainstream Single-Order)</option>
            <option value="1">Cluster 1 (Repeat / Multi-Order)</option>
            <option value="2">Cluster 2 (VIP High Spenders)</option>
            <option value="3">Cluster 3 (Bulk Item Buyers)</option>
          </select>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <ErrorMessage
          title="Error loading customers"
          message={error}
          onRetry={fetchCustomers}
        />
      )}

      {/* Table */}
      <DataTable
        columns={columns}
        data={customersData?.data || []}
        loading={loading}
        page={customersData?.page || 1}
        pageSize={pageSize}
        total={customersData?.total || 0}
        onPageChange={(p) => setPage(p)}
        onRowClick={(row) => navigate(`/customers/${row.customer_unique_id}`)}
      />
    </div>
  );
};

export default Customers;
