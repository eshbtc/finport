import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Calendar, ChevronDown, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CHART_PERIODS } from '@/lib/constants';
import { formatCurrency, formatDate } from '@/lib/utils';
import { usePriceData } from '@/hooks/useApi';

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-background p-3 shadow-md">
        <p className="font-medium">{formatDate(label)}</p>
        <p className="text-sm text-muted-foreground">
          Open: <span className="font-medium text-foreground">{formatCurrency(payload[0].payload.open)}</span>
        </p>
        <p className="text-sm text-muted-foreground">
          Close: <span className="font-medium text-foreground">{formatCurrency(payload[0].payload.close)}</span>
        </p>
        <p className="text-sm text-muted-foreground">
          High: <span className="font-medium text-foreground">{formatCurrency(payload[0].payload.high)}</span>
        </p>
        <p className="text-sm text-muted-foreground">
          Low: <span className="font-medium text-foreground">{formatCurrency(payload[0].payload.low)}</span>
        </p>
        <p className="text-sm text-muted-foreground">
          Volume: <span className="font-medium text-foreground">{payload[0].payload.volume.toLocaleString()}</span>
        </p>
      </div>
    );
  }

  return null;
};

const PriceChart = ({ symbol = 'SPY' }) => {
  const [period, setPeriod] = useState('1m');
  const [showPeriodDropdown, setShowPeriodDropdown] = useState(false);
  const [priceData, setPriceData] = useState([]);
  
  const { loading, error, getPriceData } = usePriceData();
  
  useEffect(() => {
    const fetchPriceData = async () => {
      try {
        const result = await getPriceData(symbol, { timespan: 'day' });
        if (result.success && result.data?.price_data) {
          const formattedData = result.data.price_data.map(item => ({
            ...item,
            date: new Date(item.date),
          }));
          setPriceData(formattedData);
        }
      } catch (err) {
        console.error('Failed to fetch price data:', err);
      }
    };
    
    fetchPriceData();
  }, [symbol, getPriceData]);
  
  return (
    <Card className="col-span-2">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          {symbol} Price Chart
        </CardTitle>
        
        <div className="relative">
          <Button
            variant="outline"
            size="sm"
            className="flex items-center gap-1"
            onClick={() => setShowPeriodDropdown(!showPeriodDropdown)}
          >
            {CHART_PERIODS.find(p => p.value === period)?.label || '1M'}
            <ChevronDown className="h-4 w-4" />
          </Button>
          
          {showPeriodDropdown && (
            <div className="absolute right-0 top-full z-10 mt-1 w-24 rounded-md border bg-background shadow-md">
              {CHART_PERIODS.map((p) => (
                <button
                  key={p.value}
                  className="w-full px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground"
                  onClick={() => {
                    setPeriod(p.value);
                    setShowPeriodDropdown(false);
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex h-[300px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : error ? (
          <div className="flex h-[300px] items-center justify-center text-destructive">
            <p>Failed to load price data</p>
          </div>
        ) : (
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={priceData}
                margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
              >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(date) => formatDate(date, 'short')}
                stroke="var(--muted-foreground)"
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                domain={['auto', 'auto']}
                tickFormatter={(value) => formatCurrency(value, 'USD', 0)}
                stroke="var(--muted-foreground)"
                tick={{ fontSize: 12 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="close" 
                stroke="var(--chart-1)" 
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6 }}
                name="Close Price"
              />
                          </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PriceChart;

