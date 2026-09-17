import React, { useState, useEffect } from 'react';
import { ShoppingCart, Filter, Calendar, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { DataTable } from '../components/DataTable';
import { Badge } from '../components/Badge';
import { ErrorMessage } from '../components/ErrorMessage';
import { formatDateTime, formatDate } from '../utils/formatters';

export const Orders = () => {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState('');
  const [ordersData, setOrdersData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (statusFilter) {
        params.status = statusFilter;
      }
      const res = await apiService.getOrders(params);
      setOrdersData(res);
    } catch (err) {
      setError(err?.message || 'Failed to fetch orders.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [page, statusFilter]);

  const columns = [
    {
      header: 'Order ID',
      accessor: 'order_id',
      render: (val) => (
        <span className="text-indigo-400 font-semibold font-mono" title={val}>
          {val.slice(0, 16)}...
        </span>
      ),
    },
    {
      header: 'Customer ID',
      accessor: 'customer_id',
      render: (val) => (
        <span className="text-slate-400 font-mono text-xs" title={val}>
          {val.slice(0, 14)}...
        </span>
      ),
    },
    {
      header: 'Purchase Date & Time',
      accessor: 'order_purchase_timestamp',
      render: (val) => (
        <span className="font-sans text-slate-300">{formatDateTime(val)}</span>
      ),
    },
    {
      header: 'Status',
      accessor: 'order_status',
      align: 'center',
      render: (val) => {
        const variantMap = {
          delivered: 'success',
          shipped: 'primary',
          canceled: 'danger',
          unavailable: 'warning',
          invoiced: 'default',
        };
        return <Badge variant={variantMap[val] || 'default'}>{val}</Badge>;
      },
    },
    {
      header: 'Delivered Date',
      accessor: 'order_delivered_customer_date',
      render: (val) => (
        <span className="font-sans text-slate-400">{formatDate(val)}</span>
      ),
    },
    {
      header: 'Delivery Time',
      accessor: 'delivery_days',
      align: 'right',
      render: (val) => (
        <span className="font-sans font-medium text-slate-300">
          {val !== null && val !== undefined ? `${Number(val).toFixed(1)} days` : '—'}
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
            <ShoppingCart className="w-6 h-6 text-indigo-400" />
            Order Lifecycle Management
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Real-time fulfillment tracking across 99,441 consumer order transactions.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-card rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="w-full sm:w-64 bg-slate-950/80 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Order Statuses</option>
            <option value="delivered">Delivered (96,478 orders)</option>
            <option value="shipped">Shipped (1,107 orders)</option>
            <option value="canceled">Canceled (625 orders)</option>
            <option value="unavailable">Unavailable (609 orders)</option>
            <option value="invoiced">Invoiced (314 orders)</option>
            <option value="processing">Processing (301 orders)</option>
          </select>
        </div>

        <div className="text-xs text-slate-400">
          Indexed on <span className="font-mono text-indigo-400">customer_id</span>, <span className="font-mono text-indigo-400">order_status</span>, <span className="font-mono text-indigo-400">order_purchase_timestamp</span>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <ErrorMessage
          title="Error loading orders"
          message={error}
          onRetry={fetchOrders}
        />
      )}

      {/* Table */}
      <DataTable
        columns={columns}
        data={ordersData?.data || []}
        loading={loading}
        page={ordersData?.page || 1}
        pageSize={pageSize}
        total={ordersData?.total || 0}
        onPageChange={(p) => setPage(p)}
      />
    </div>
  );
};

export default Orders;
