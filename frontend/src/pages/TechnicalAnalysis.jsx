import React, { useState } from 'react';
import { 
  LineChart, 
  Line, 
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend,
  ReferenceLine
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Pencil, 
  MousePointer, 
  Maximize, 
  Minimize, 
  TrendingUp,
  BarChart2,
  Activity,
  Layers,
  ChevronDown,
  Search,
  Save,
  Share,
  Download
} from 'lucide-react';
import { CHART_PERIODS, CHART_TYPES, TECHNICAL_INDICATORS, MOCK_PRICE_DATA } from '@/lib/constants';
import { formatCurrency, formatDate, formatNumber } from '@/lib/utils';

// Mock data for technical indicators
const mockRSIData = MOCK_PRICE_DATA.map((item, index) => ({
  date: new Date(item.date),
  value: 30 + Math.sin(index * 0.5) * 20 + Math.random() * 10,
}));

const mockMACDData = MOCK_PRICE_DATA.map((item, index) => ({
  date: new Date(item.date),
  macd: Math.sin(index * 0.5) * 2 + Math.random() * 0.5,
  signal: Math.sin((index + 2) * 0.5) * 2 + Math.random() * 0.5,
  histogram: Math.sin(index * 0.5) * 2 - Math.sin((index + 2) * 0.5) * 2 + Math.random() * 0.3,
}));

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-background p-3 shadow-md">
        <p className="font-medium">{formatDate(label)}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm text-muted-foreground">
            {entry.name}: <span className="font-medium" style={{ color: entry.color }}>{entry.value.toFixed(2)}</span>
          </p>
        ))}
      </div>
    );
  }

  return null;
};

const TechnicalAnalysis = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [period, setPeriod] = useState('1m');
  const [chartType, setChartType] = useState('candlestick');
  const [selectedIndicators, setSelectedIndicators] = useState(['sma', 'ema', 'rsi']);
  const [showIndicatorDropdown, setShowIndicatorDropdown] = useState(false);
  
  // Format data for chart
  const chartData = MOCK_PRICE_DATA.map(item => ({
    ...item,
    date: new Date(item.date),
    sma20: item.close * (1 + Math.sin(new Date(item.date).getDate() * 0.1) * 0.02),
    ema50: item.close * (1 + Math.cos(new Date(item.date).getDate() * 0.1) * 0.03),
  }));
  
  // Toggle indicator
  const toggleIndicator = (indicator) => {
    if (selectedIndicators.includes(indicator)) {
      setSelectedIndicators(selectedIndicators.filter(i => i !== indicator));
    } else {
      setSelectedIndicators([...selectedIndicators, indicator]);
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Technical Analysis</h1>
          <p className="text-sm text-muted-foreground">
            Advanced charting and technical indicators
          </p>
        </div>
        
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative w-full md:w-auto">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Enter symbol..."
              className="pl-8 w-full md:w-[180px]"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            />
          </div>
          
          <Select value={chartType} onValueChange={setChartType}>
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder="Chart Type" />
            </SelectTrigger>
            <SelectContent>
              {CHART_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <div className="flex items-center gap-1">
            {CHART_PERIODS.slice(0, 5).map((p) => (
              <Button
                key={p.value}
                variant={period === p.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPeriod(p.value)}
              >
                {p.label}
              </Button>
            ))}
            <Select value={period} onValueChange={setPeriod}>
              <SelectTrigger className="w-[80px]">
                <SelectValue placeholder="More" />
              </SelectTrigger>
              <SelectContent>
                {CHART_PERIODS.slice(5).map((p) => (
                  <SelectItem key={p.value} value={p.value}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-12 gap-6">
        {/* Left sidebar - Drawing tools */}
        <div className="col-span-12 md:col-span-1">
          <Card className="h-full">
            <CardContent className="p-2">
              <div className="flex flex-row md:flex-col gap-1">
                <Button variant="ghost" size="icon" title="Cursor">
                  <MousePointer className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" title="Draw Line">
                  <TrendingUp className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" title="Draw Rectangle">
                  <Maximize className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" title="Draw Fibonacci">
                  <Layers className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" title="Text">
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" title="Zoom">
                  <Minimize className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Main chart area */}
        <div className="col-span-12 md:col-span-8">
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between py-3">
              <CardTitle className="text-xl">{symbol} Chart</CardTitle>
              
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex items-center gap-1"
                    onClick={() => setShowIndicatorDropdown(!showIndicatorDropdown)}
                  >
                    <Activity className="h-4 w-4" />
                    Indicators
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                  
                  {showIndicatorDropdown && (
                    <div className="absolute right-0 top-full z-10 mt-1 w-[220px] rounded-md border bg-background shadow-md">
                      <div className="p-2">
                        {TECHNICAL_INDICATORS.map((indicator) => (
                          <div
                            key={indicator.value}
                            className="flex items-center gap-2 rounded-md px-2 py-1 hover:bg-accent hover:text-accent-foreground"
                          >
                            <input
                              type="checkbox"
                              id={`indicator-${indicator.value}`}
                              checked={selectedIndicators.includes(indicator.value)}
                              onChange={() => toggleIndicator(indicator.value)}
                            />
                            <label
                              htmlFor={`indicator-${indicator.value}`}
                              className="flex-1 cursor-pointer text-sm"
                            >
                              {indicator.label} - {indicator.description}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                <Button variant="outline" size="icon" title="Save Chart">
                  <Save className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" title="Share Chart">
                  <Share className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" title="Download Chart">
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[500px]">
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
                    {selectedIndicators.includes('sma') && (
                      <Line 
                        type="monotone" 
                        dataKey="sma20" 
                        stroke="var(--chart-2)" 
                        strokeWidth={1.5}
                        dot={false}
                        name="SMA (20)"
                      />
                    )}
                    {selectedIndicators.includes('ema') && (
                      <Line 
                        type="monotone" 
                        dataKey="ema50" 
                        stroke="var(--chart-3)" 
                        strokeWidth={1.5}
                        dot={false}
                        name="EMA (50)"
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </div>
              
              {/* Indicator panels */}
              {selectedIndicators.includes('rsi') && (
                <div className="mt-4 h-[150px]">
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-sm font-medium">RSI (14)</span>
                    <span className="text-xs text-muted-foreground">
                      Current: {mockRSIData[mockRSIData.length - 1].value.toFixed(2)}
                    </span>
                  </div>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={mockRSIData}
                      margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={(date) => formatDate(date, 'short')}
                        stroke="var(--muted-foreground)"
                        tick={{ fontSize: 10 }}
                      />
                      <YAxis 
                        domain={[0, 100]}
                        tickFormatter={(value) => value}
                        stroke="var(--muted-foreground)"
                        tick={{ fontSize: 10 }}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <ReferenceLine y={70} stroke="var(--destructive)" strokeDasharray="3 3" />
                      <ReferenceLine y={30} stroke="var(--chart-4)" strokeDasharray="3 3" />
                      <Line 
                        type="monotone" 
                        dataKey="value" 
                        stroke="var(--chart-5)" 
                        strokeWidth={1.5}
                        dot={false}
                        name="RSI"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
              
              {selectedIndicators.includes('macd') && (
                <div className="mt-4 h-[150px]">
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-sm font-medium">MACD (12,26,9)</span>
                    <span className="text-xs text-muted-foreground">
                      MACD: {mockMACDData[mockMACDData.length - 1].macd.toFixed(2)} | 
                      Signal: {mockMACDData[mockMACDData.length - 1].signal.toFixed(2)}
                    </span>
                  </div>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={mockMACDData}
                      margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={(date) => formatDate(date, 'short')}
                        stroke="var(--muted-foreground)"
                        tick={{ fontSize: 10 }}
                      />
                      <YAxis 
                        tickFormatter={(value) => value.toFixed(1)}
                        stroke="var(--muted-foreground)"
                        tick={{ fontSize: 10 }}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar 
                        dataKey="histogram" 
                        fill="var(--chart-2)" 
                        name="Histogram" 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="macd" 
                        stroke="var(--chart-1)" 
                        strokeWidth={1.5}
                        dot={false}
                        name="MACD"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="signal" 
                        stroke="var(--chart-3)" 
                        strokeWidth={1.5}
                        dot={false}
                        name="Signal"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        
        {/* Right sidebar - Watchlist */}
        <div className="col-span-12 md:col-span-3">
          <Card className="h-full">
            <CardHeader className="py-3">
              <CardTitle className="flex items-center gap-2">
                <BarChart2 className="h-5 w-5" />
                Watchlist
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y">
                {['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'].map((sym) => (
                  <div 
                    key={sym}
                    className={`flex items-center justify-between p-3 hover:bg-accent hover:text-accent-foreground cursor-pointer ${
                      sym === symbol ? 'bg-accent text-accent-foreground' : ''
                    }`}
                    onClick={() => setSymbol(sym)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center">
                        <span className="text-xs font-semibold">{sym}</span>
                      </div>
                      <div>
                        <div className="font-medium">{sym}</div>
                        <div className="text-xs text-muted-foreground">
                          {formatCurrency(Math.random() * 500 + 100)}
                        </div>
                      </div>
                    </div>
                    <div className="h-10 w-20">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                          data={[...Array(10)].map((_, i) => ({
                            x: i,
                            y: Math.random() * 10 + 90 + (sym === 'TSLA' ? Math.sin(i) * 5 : 0),
                          }))}
                          margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
                        >
                          <Line 
                            type="monotone" 
                            dataKey="y" 
                            stroke={sym === 'TSLA' ? 'var(--destructive)' : 'var(--chart-1)'} 
                            strokeWidth={1.5}
                            dot={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TechnicalAnalysis;

