import React, { useState, useEffect } from 'react';
import { Package, Filter, Search, Tag, Layers, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';
import { DataTable } from '../components/DataTable';
import { ErrorMessage } from '../components/ErrorMessage';
import { formatNumber } from '../utils/formatters';

export const Products = () => {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [productsData, setProductsData] = useState(null);
  const [categoriesList, setCategoriesList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch top categories for dropdown filter
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const catRes = await apiService.getCategorySales(30);
        setCategoriesList(catRes || []);
      } catch (err) {
        console.error('Failed to load categories list:', err);
      }
    };
    loadCategories();
  }, []);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (categoryFilter) {
        params.category = categoryFilter;
      }
      const res = await apiService.getProducts(params);
      setProductsData(res);
    } catch (err) {
      setError(err?.message || 'Failed to fetch product catalog.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [page, categoryFilter]);

  const columns = [
    {
      header: 'Product ID',
      accessor: 'product_id',
      render: (val) => (
        <span className="text-indigo-400 font-semibold font-mono" title={val}>
          {val.slice(0, 16)}...
        </span>
      ),
    },
    {
      header: 'Category (English)',
      accessor: 'product_category_name_english',
      render: (val) => (
        <span className="font-sans font-medium text-slate-200 capitalize">
          {val ? val.replace(/_/g, ' ') : 'Uncategorized'}
        </span>
      ),
    },
    {
      header: 'Photos',
      accessor: 'product_photos_qty',
      align: 'center',
      render: (val) => <span className="font-sans text-slate-300">{val ?? '—'}</span>,
    },
    {
      header: 'Weight (g)',
      accessor: 'product_weight_g',
      align: 'right',
      render: (val) => (
        <span className="font-sans text-slate-300">
          {val !== null && val !== undefined ? `${Number(val).toLocaleString()} g` : '—'}
        </span>
      ),
    },
    {
      header: 'Dimensions (L x H x W cm)',
      accessor: 'product_length_cm',
      align: 'center',
      render: (_, row) => (
        <span className="font-sans text-slate-400 text-xs">
          {row.product_length_cm ?? '—'} × {row.product_height_cm ?? '—'} × {row.product_width_cm ?? '—'} cm
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
            <Package className="w-6 h-6 text-indigo-400" />
            Product Catalog
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Browse 32,951 cleaned e-commerce products with physical specifications and localized categories.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-card rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value);
              setPage(1);
            }}
            className="w-full sm:w-72 bg-slate-950/80 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 capitalize"
          >
            <option value="">All Categories (71 Categories)</option>
            {categoriesList.map((c) => (
              <option key={c.category} value={c.category}>
                {c.category.replace(/_/g, ' ')} ({c.items_sold} sold)
              </option>
            ))}
          </select>
        </div>

        <div className="text-xs text-slate-400">
          Showing catalog data from PostgreSQL serving table <span className="font-mono text-indigo-400">products</span>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <ErrorMessage
          title="Error loading product catalog"
          message={error}
          onRetry={fetchProducts}
        />
      )}

      {/* Table */}
      <DataTable
        columns={columns}
        data={productsData?.data || []}
        loading={loading}
        page={productsData?.page || 1}
        pageSize={pageSize}
        total={productsData?.total || 0}
        onPageChange={(p) => setPage(p)}
      />
    </div>
  );
};

export default Products;
