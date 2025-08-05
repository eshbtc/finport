import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { List, Plus, ArrowUpRight, ArrowDownRight, MoreHorizontal } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DEFAULT_WATCHLIST } from '@/lib/constants';
import { formatCurrency, formatPercent } from '@/lib/utils';

// Mock data for watchlist items
const mockWatchlistData = {
  'AAPL': { price: 178.72, change: 0.0215, volume: 65432100 },
  'MSFT': { price: 389.56, change: 0.0175, volume: 35678200 },
  'GOOGL': { price: 142.15, change: 0.0125, volume: 25678900 },
  'AMZN': { price: 175.35, change: 0.0085, volume: 45678100 },
  'TSLA': { price: 215.65, change: -0.0325, volume: 85678300 },
  'META': { price: 465.25, change: 0.0275, volume: 35678200 },
  'NVDA': { price: 789.45, change: 0.0425, volume: 95678100 },
  'GME': { price: 25.75, change: -0.0185, volume: 15678300 },
  'AMD': { price: 156.85, change: 0.0155, volume: 35678200 },
  'INTC': { price: 42.35, change: -0.0075, volume: 25678900 },
};

const WatchlistCard = () => {
  const [sortBy, setSortBy] = useState('symbol');
  const [sortDirection, setSortDirection] = useState('asc');
  
  // Sort watchlist items
  const sortedWatchlist = [...DEFAULT_WATCHLIST].sort((a, b) => {
    const aValue = sortBy === 'symbol' ? a : mockWatchlistData[a][sortBy];
    const bValue = sortBy === 'symbol' ? b : mockWatchlistData[b][sortBy];
    
    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  // Handle sort
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortDirection('asc');
    }
  };
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <List className="h-5 w-5" />
          Watchlist
        </CardTitle>
        <Button variant="outline" size="sm">
          <Plus className="mr-2 h-4 w-4" />
          Add
        </Button>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-sm font-medium text-muted-foreground">
                <th 
                  className="pb-2 pl-2 pr-4 cursor-pointer"
                  onClick={() => handleSort('symbol')}
                >
                  Symbol
                </th>
                <th 
                  className="pb-2 px-4 cursor-pointer"
                  onClick={() => handleSort('price')}
                >
                  Price
                </th>
                <th 
                  className="pb-2 px-4 cursor-pointer"
                  onClick={() => handleSort('change')}
                >
                  Change
                </th>
                <th 
                  className="pb-2 px-4 cursor-pointer"
                  onClick={() => handleSort('volume')}
                >
                  Volume
                </th>
                <th className="pb-2 px-4"></th>
              </tr>
            </thead>
            <tbody>
              {sortedWatchlist.map((symbol) => {
                const data = mockWatchlistData[symbol];
                const isPositive = data.change > 0;
                
                return (
                  <tr key={symbol} className="border-b last:border-0">
                    <td className="py-3 pl-2 pr-4">
                      <Link 
                        to={`/securities/${symbol}`}
                        className="font-medium hover:underline"
                      >
                        {symbol}
                      </Link>
                    </td>
                    <td className="py-3 px-4">
                      {formatCurrency(data.price)}
                    </td>
                    <td className={`py-3 px-4 ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                      <div className="flex items-center">
                        {isPositive ? (
                          <ArrowUpRight className="mr-1 h-4 w-4" />
                        ) : (
                          <ArrowDownRight className="mr-1 h-4 w-4" />
                        )}
                        <span>{formatPercent(Math.abs(data.change))}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-muted-foreground">
                      {(data.volume / 1000000).toFixed(1)}M
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default WatchlistCard;

