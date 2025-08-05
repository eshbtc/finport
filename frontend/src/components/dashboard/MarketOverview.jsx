import React from 'react';
import { ArrowUpRight, ArrowDownRight, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MARKET_INDICES } from '@/lib/constants';
import { formatPercent } from '@/lib/utils';

// Mock data for market indices
const mockMarketData = {
  'SPY': { price: 478.25, change: 0.0125, volume: 75432100 },
  'QQQ': { price: 389.76, change: 0.0215, volume: 45678200 },
  'DIA': { price: 385.12, change: 0.0075, volume: 25678900 },
  'IWM': { price: 201.45, change: -0.0085, volume: 35678100 },
  'VIX': { price: 15.75, change: -0.0325, volume: 15678300 },
};

const MarketOverview = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Market Overview
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {MARKET_INDICES.map((index) => {
            const data = mockMarketData[index.symbol];
            const isPositive = data.change > 0;
            
            return (
              <div 
                key={index.symbol}
                className="flex flex-col rounded-lg border p-3"
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium">{index.name}</div>
                  <div 
                    className="flex items-center text-xs font-medium"
                    style={{ color: index.color }}
                  >
                    {index.symbol}
                  </div>
                </div>
                
                <div className="mt-2 flex items-baseline justify-between">
                  <div className="text-2xl font-bold">{data.price.toFixed(2)}</div>
                  <div className={`flex items-center ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                    {isPositive ? (
                      <ArrowUpRight className="mr-1 h-4 w-4" />
                    ) : (
                      <ArrowDownRight className="mr-1 h-4 w-4" />
                    )}
                    <span>{formatPercent(Math.abs(data.change))}</span>
                  </div>
                </div>
                
                <div className="mt-2 text-xs text-muted-foreground">
                  Volume: {(data.volume / 1000000).toFixed(1)}M
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default MarketOverview;

