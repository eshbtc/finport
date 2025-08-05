import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Calendar, ChevronDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CHART_PERIODS, MOCK_PRICE_DATA } from '@/lib/constants';
import { formatCurrency, formatDate } from '@/lib/utils';

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
  
  // Format data for chart
  const chartData = MOCK_PRICE_DATA.map(item => ({
    ...item,
    date: new Date(item.date),
  }));
  
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
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
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
      </CardContent>
    </Card>
  );
};

export default PriceChart;

