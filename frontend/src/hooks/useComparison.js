import { useQuery } from 'react-query';
import stockApi from '../api/stockApi';

export function useCompareOverTime(ticker, periods, dataType, options = {}) {
  return useQuery(
    ['compareOverTime', ticker, periods, dataType],
    () => stockApi.compareOverTime(ticker, periods, dataType),
    {
      enabled: !!ticker && !!periods,
      staleTime: 5 * 60 * 1000,
      ...options
    }
  );
}

export function useCompareTickers(tickers, period, dataType, options = {}) {
  const tickersArray = Array.isArray(tickers) ? tickers : [tickers];
  const tickersString = tickersArray.join(',');
  
  return useQuery(
    ['compareTickers', tickersString, period, dataType],
    () => stockApi.compareTickers(tickersString, period, dataType),
    {
      enabled: tickersArray.length >= 2,
      staleTime: 5 * 60 * 1000,
      ...options
    }
  );
}

export function useComparisonData(mode, params) {
  const {
    tickers = [],
    ticker = '',
    periods = '1h,4h,1d,1w',
    period = '1d',
    dataType = 'analyst_ratings'
  } = params;

  const tickersQuery = useCompareTickers(tickers, period, dataType, {
    enabled: mode === 'tickers' && tickers.length >= 2
  });

  const periodsQuery = useCompareOverTime(ticker, periods, dataType, {
    enabled: mode === 'periods' && !!ticker
  });

  return mode === 'tickers' ? tickersQuery : periodsQuery;
}

export default {
  useCompareOverTime,
  useCompareTickers,
  useComparisonData
};
