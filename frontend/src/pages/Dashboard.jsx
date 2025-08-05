import React from 'react';
import MarketOverview from '@/components/dashboard/MarketOverview';
import WatchlistCard from '@/components/dashboard/WatchlistCard';
import PriceChart from '@/components/dashboard/PriceChart';
import NewsCard from '@/components/dashboard/NewsCard';

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Last updated: {new Date().toLocaleString()}
        </p>
      </div>
      
      <MarketOverview />
      
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <PriceChart symbol="SPY" />
        <WatchlistCard />
        <NewsCard />
      </div>
    </div>
  );
};

export default Dashboard;

