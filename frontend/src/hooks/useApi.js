import { useState, useCallback } from 'react';
import apiService from '@/lib/api';

/**
 * Custom hook for API calls with loading and error states
 */
export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callApi = useCallback(async (apiCall, ...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall(...args);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    callApi,
  };
};

/**
 * Hook for securities data
 */
export const useSecurities = () => {
  const { loading, error, callApi } = useApi();

  const getSecurities = useCallback(() => {
    return callApi(apiService.getSecurities.bind(apiService));
  }, [callApi]);

  const getSecurity = useCallback((ticker) => {
    return callApi(apiService.getSecurity.bind(apiService), ticker);
  }, [callApi]);

  const searchSecurities = useCallback((query) => {
    return callApi(apiService.searchSecurities.bind(apiService), query);
  }, [callApi]);

  return {
    loading,
    error,
    getSecurities,
    getSecurity,
    searchSecurities,
  };
};

/**
 * Hook for price data
 */
export const usePriceData = () => {
  const { loading, error, callApi } = useApi();

  const getPriceData = useCallback((ticker, options = {}) => {
    return callApi(apiService.getPriceData.bind(apiService), ticker, options);
  }, [callApi]);

  return {
    loading,
    error,
    getPriceData,
  };
};

/**
 * Hook for FTD data
 */
export const useFTDData = () => {
  const { loading, error, callApi } = useApi();

  const getFTDData = useCallback((ticker, options = {}) => {
    return callApi(apiService.getFTDData.bind(apiService), ticker, options);
  }, [callApi]);

  return {
    loading,
    error,
    getFTDData,
  };
};

/**
 * Hook for technical indicators
 */
export const useTechnicalIndicators = () => {
  const { loading, error, callApi } = useApi();

  const getTechnicalIndicators = useCallback((ticker, options = {}) => {
    return callApi(apiService.getTechnicalIndicators.bind(apiService), ticker, options);
  }, [callApi]);

  return {
    loading,
    error,
    getTechnicalIndicators,
  };
};

/**
 * Hook for market analysis
 */
export const useMarketAnalysis = () => {
  const { loading, error, callApi } = useApi();

  const getSwapCycles = useCallback((ticker, options = {}) => {
    return callApi(apiService.getSwapCycles.bind(apiService), ticker, options);
  }, [callApi]);

  const getVolatilityCycles = useCallback((ticker, options = {}) => {
    return callApi(apiService.getVolatilityCycles.bind(apiService), ticker, options);
  }, [callApi]);

  const getMarketCorrelations = useCallback((ticker, options = {}) => {
    return callApi(apiService.getMarketCorrelations.bind(apiService), ticker, options);
  }, [callApi]);

  return {
    loading,
    error,
    getSwapCycles,
    getVolatilityCycles,
    getMarketCorrelations,
  };
};

/**
 * Hook for user management
 */
export const useUsers = () => {
  const { loading, error, callApi } = useApi();

  const getUsers = useCallback(() => {
    return callApi(apiService.getUsers.bind(apiService));
  }, [callApi]);

  const createUser = useCallback((userData) => {
    return callApi(apiService.createUser.bind(apiService), userData);
  }, [callApi]);

  const getUser = useCallback((userId) => {
    return callApi(apiService.getUser.bind(apiService), userId);
  }, [callApi]);

  const updateUser = useCallback((userId, userData) => {
    return callApi(apiService.updateUser.bind(apiService), userId, userData);
  }, [callApi]);

  const deleteUser = useCallback((userId) => {
    return callApi(apiService.deleteUser.bind(apiService), userId);
  }, [callApi]);

  return {
    loading,
    error,
    getUsers,
    createUser,
    getUser,
    updateUser,
    deleteUser,
  };
};

/**
 * Hook for watchlists
 */
export const useWatchlists = () => {
  const { loading, error, callApi } = useApi();

  const getUserWatchlists = useCallback((userId) => {
    return callApi(apiService.getUserWatchlists.bind(apiService), userId);
  }, [callApi]);

  const createWatchlist = useCallback((userId, watchlistData) => {
    return callApi(apiService.createWatchlist.bind(apiService), userId, watchlistData);
  }, [callApi]);

  const addWatchlistItem = useCallback((userId, watchlistId, itemData) => {
    return callApi(apiService.addWatchlistItem.bind(apiService), userId, watchlistId, itemData);
  }, [callApi]);

  return {
    loading,
    error,
    getUserWatchlists,
    createWatchlist,
    addWatchlistItem,
  };
}; 