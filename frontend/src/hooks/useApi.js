import { useState, useEffect, useCallback } from 'react';

/**
 * Custom React hook for calling API functions with loading, error, and refetch states.
 */
export const useApi = (apiFunc, params = null, autoFetch = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(autoFetch);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (overrideParams = null) => {
    setLoading(true);
    setError(null);
    try {
      const p = overrideParams !== null ? overrideParams : params;
      const result = await (p !== null && p !== undefined ? apiFunc(p) : apiFunc());
      setData(result);
      return result;
    } catch (err) {
      setError(err?.message || 'Failed to fetch data from API.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunc, JSON.stringify(params)]);

  useEffect(() => {
    if (autoFetch) {
      fetchData().catch(() => {});
    }
  }, [fetchData, autoFetch]);

  return { data, loading, error, refetch: fetchData, setData };
};

export default useApi;
