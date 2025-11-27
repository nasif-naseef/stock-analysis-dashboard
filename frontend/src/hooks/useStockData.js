import { useQuery, useMutation, useQueryClient } from 'react-query';
import stockApi from '../api/stockApi';

export function useAnalystRatings(ticker, options = {}) {
  return useQuery(
    ['analystRatings', ticker],
    () => stockApi.getAnalystRatings(ticker),
    {
      enabled: !!ticker,
      staleTime: 5 * 60 * 1000, // 5 minutes
      ...options
    }
  );
}

export function useNewsSentiment(ticker, options = {}) {
  return useQuery(
    ['newsSentiment', ticker],
    () => stockApi.getNewsSentiment(ticker),
    {
      enabled: !!ticker,
      staleTime: 5 * 60 * 1000,
      ...options
    }
  );
}

export function useQuantamental(ticker, options = {}) {
  return useQuery(
    ['quantamental', ticker],
    () => stockApi.getQuantamental(ticker),
    {
      enabled: !!ticker,
      staleTime: 5 * 60 * 1000,
      ...options
    }
  );
}

export function useHedgeFund(ticker, options = {}) {
  return useQuery(
    ['hedgeFund', ticker],
    () => stockApi.getHedgeFund(ticker),
    {
      enabled: !!ticker,
      staleTime: 5 * 60 * 1000,
      ...options
    }
  );
}

export function useCrowd(ticker, options = {}) {
  return useQuery(
    ['crowd', ticker],
    () => stockApi.getCrowd(ticker),
    {
      enabled: !!ticker,
      staleTime: 5 * 60 * 1000,
      ...options
    }
  );
}

export function useTechnical(ticker, timeframe, options = {}) {
  return useQuery(
    ['technical', ticker, timeframe],
    () => stockApi.getTechnical(ticker, timeframe),
    {
      enabled: !!ticker,
      staleTime: 5 * 60 * 1000,
      ...options
    }
  );
}

export function useTargetPrice(ticker, options = {}) {
  return useQuery(
    ['targetPrice', ticker],
    () => stockApi.getTargetPrice(ticker),
    {
      enabled: !!ticker,
      staleTime: 5 * 60 * 1000,
      ...options
    }
  );
}

export function useDashboardOverview(options = {}) {
  return useQuery(
    'dashboardOverview',
    () => stockApi.getDashboardOverview(),
    {
      staleTime: 60 * 1000, // 1 minute
      refetchInterval: 60 * 1000,
      ...options
    }
  );
}

export function useDashboardAlerts(hours = 24, options = {}) {
  return useQuery(
    ['dashboardAlerts', hours],
    () => stockApi.getDashboardAlerts(hours),
    {
      staleTime: 60 * 1000,
      refetchInterval: 60 * 1000,
      ...options
    }
  );
}

export function useTickerOverview(ticker, options = {}) {
  return useQuery(
    ['tickerOverview', ticker],
    () => stockApi.getTickerOverview(ticker),
    {
      enabled: !!ticker,
      staleTime: 60 * 1000,
      ...options
    }
  );
}

export function useTriggerCollection() {
  const queryClient = useQueryClient();
  
  return useMutation(
    (ticker) => stockApi.triggerCollection(ticker),
    {
      onSuccess: () => {
        // Invalidate relevant queries after collection
        queryClient.invalidateQueries('dashboardOverview');
        queryClient.invalidateQueries('dashboardAlerts');
      }
    }
  );
}

export function useConfiguredTickers() {
  return useQuery(
    'configuredTickers',
    () => stockApi.getConfiguredTickers(),
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
    }
  );
}
