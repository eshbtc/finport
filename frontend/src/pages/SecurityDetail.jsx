import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area,
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from 'recharts';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  ArrowUpRight, 
  ArrowDownRight, 
  Star, 
  Info, 
  BarChart2,
  Activity,
  PieChart,
  Calendar,
  FileText,
  Users
} from 'lucide-react';
import { CHART_PERIODS, MOCK_PRICE_DATA } from '@/lib/constants';
import { formatCurrency, formatNumber, formatPercent, formatDate } from '@/lib/utils';

// Mock security data
const mockSecurityData = {
  'AAPL': {
    name: 'Apple Inc.',
    price: 178.72,
    change: 0.0215,
    volume: 65432100,
    marketCap: 2850000000000,
    peRatio: 29.5,
    dividend: 0.0092,
    beta: 1.28,
    avgVolume: 58900000,
    high52w: 182.94,
    low52w: 124.17,
    open: 175.50,
    previousClose: 175.01,
  },
  'MSFT': {
    name: 'Microsoft Corporation',
    price: 389.56,
    change: 0.0175,
    volume: 35678200,
    marketCap: 2900000000000,
    peRatio: 33.8,
    dividend: 0.0082,
    beta: 0.95,
    avgVolume: 28700000,
    high52w: 395.82,
    low52w: 275.37,
    open: 385.20,
    previousClose: 382.87,
  },
  'GOOGL': {
    name: 'Alphabet Inc.',
    price: 142.15,
    change: 0.0125,
    volume: 25678900,
    marketCap: 1800000000000,
    peRatio: 25.2,
    dividend: 0,
    beta: 1.06,
    avgVolume: 31500000,
    high52w: 153.78,
    low52w: 102.21,
    open: 140.50,
    previousClose: 140.37,
  },
  'AMZN': {
    name: 'Amazon.com, Inc.',
    price: 175.35,
    change: 0.0085,
    volume: 45678100,
    marketCap: 1820000000000,
    peRatio: 60.5,
    dividend: 0,
    beta: 1.22,
    avgVolume: 48900000,
    high52w: 180.14,
    low52w: 118.35,
    open: 174.20,
    previousClose: 173.86,
  },
  'TSLA': {
    name: 'Tesla, Inc.',
    price: 215.65,
    change: -0.0325,
    volume: 85678300,
    marketCap: 685000000000,
    peRatio: 55.3,
    dividend: 0,
    beta: 2.04,
    avgVolume: 92500000,
    high52w: 278.98,
    low52w: 152.37,
    open: 220.50,
    previousClose: 222.86,
  },
  'META': {
    name: 'Meta Platforms, Inc.',
    price: 465.25,
    change: 0.0275,
    volume: 35678200,
    marketCap: 1190000000000,
    peRatio: 26.8,
    dividend: 0,
    beta: 1.32,
    avgVolume: 25700000,
    high52w: 485.96,
    low52w: 258.75,
    open: 455.20,
    previousClose: 452.75,
  },
  'NVDA': {
    name: 'NVIDIA Corporation',
    price: 789.45,
    change: 0.0425,
    volume: 95678100,
    marketCap: 1950000000000,
    peRatio: 72.5,
    dividend: 0.0008,
    beta: 1.75,
    avgVolume: 42500000,
    high52w: 825.27,
    low52w: 373.55,
    open: 770.20,
    previousClose: 757.25,
  },
  'GME': {
    name: 'GameStop Corp.',
    price: 25.75,
    change: -0.0185,
    volume: 15678300,
    marketCap: 7850000000,
    peRatio: null,
    dividend: 0,
    beta: -0.25,
    avgVolume: 12500000,
    high52w: 42.97,
    low52w: 15.41,
    open: 26.20,
    previousClose: 26.22,
  },
  'AMD': {
    name: 'Advanced Micro Devices, Inc.',
    price: 156.85,
    change: 0.0155,
    volume: 35678200,
    marketCap: 253000000000,
    peRatio: 92.3,
    dividend: 0,
    beta: 1.68,
    avgVolume: 45700000,
    high52w: 227.30,
    low52w: 93.12,
    open: 155.20,
    previousClose: 154.45,
  },
  'INTC': {
    name: 'Intel Corporation',
    price: 42.35,
    change: -0.0075,
    volume: 25678900,
    marketCap: 178000000000,
    peRatio: null,
    dividend: 0.0125,
    beta: 0.89,
    avgVolume: 35700000,
    high52w: 51.28,
    low52w: 24.59,
    open: 42.70,
    previousClose: 42.67,
  },
};

// Mock institutional ownership data
const mockInstitutionalData = [
  { name: 'Vanguard Group', shares: 25678900, value: 4589000000, change: 0.0125 },
  { name: 'BlackRock', shares: 19876500, value: 3556000000, change: 0.0075 },
  { name: 'State Street', shares: 15432100, value: 2761000000, change: -0.0025 },
  { name: 'Fidelity', shares: 12345600, value: 2208000000, change: 0.0185 },
  { name: 'T. Rowe Price', shares: 9876500, value: 1766000000, change: -0.0095 },
];

// Mock FTD data
const mockFTDData = [
  { date: '2023-01-15', quantity: 125000, price: 165.75, value: 20718750 },
  { date: '2023-01-30', quantity: 98000, price: 170.25, value: 16684500 },
  { date: '2023-02-15', quantity: 145000, price: 168.50, value: 24432500 },
  { date: '2023-02-28', quantity: 87000, price: 172.75, value: 15029250 },
  { date: '2023-03-15', quantity: 165000, price: 175.25, value: 28916250 },
  { date: '2023-03-30', quantity: 112000, price: 178.50, value: 19992000 },
  { date: '2023-04-15', quantity: 135000, price: 176.75, value: 23861250 },
  { date: '2023-04-30', quantity: 95000, price: 173.25, value: 16458750 },
  { date: '2023-05-15', quantity: 155000, price: 177.50, value: 27512500 },
  { date: '2023-05-30', quantity: 105000, price: 180.25, value: 18926250 },
];

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

const SecurityDetail = () => {
  const { symbol } = useParams();
  const [period, setPeriod] = useState('1m');
  
  // Get security data
  const securityData = mockSecurityData[symbol] || mockSecurityData['AAPL'];
  const isPositive = securityData.change > 0;
  
  // Format data for chart
  const chartData = MOCK_PRICE_DATA.map(item => ({
    ...item,
    date: new Date(item.date),
  }));
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{symbol} - {securityData.name}</h1>
          <p className="text-sm text-muted-foreground">
            Last updated: {new Date().toLocaleString()}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Star className="mr-2 h-4 w-4" />
            Add to Watchlist
          </Button>
          <Button variant="outline" size="sm">
            <Info className="mr-2 h-4 w-4" />
            Company Info
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col gap-1">
              <span className="text-sm font-medium text-muted-foreground">Current Price</span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold">{formatCurrency(securityData.price)}</span>
                <span className={`flex items-center text-sm font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                  {isPositive ? (
                    <ArrowUpRight className="mr-1 h-4 w-4" />
                  ) : (
                    <ArrowDownRight className="mr-1 h-4 w-4" />
                  )}
                  <span>{formatPercent(Math.abs(securityData.change))}</span>
                </span>
              </div>
              <span className="text-xs text-muted-foreground">
                Volume: {formatNumber(securityData.volume, 0)}
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col gap-1">
              <span className="text-sm font-medium text-muted-foreground">Market Cap</span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold">{formatCurrency(securityData.marketCap / 1000000000, 'USD', 1)}B</span>
              </div>
              <span className="text-xs text-muted-foreground">
                P/E Ratio: {securityData.peRatio ? formatNumber(securityData.peRatio, 2) : 'N/A'}
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col gap-1">
              <span className="text-sm font-medium text-muted-foreground">52 Week Range</span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold">{formatCurrency(securityData.low52w)} - {formatCurrency(securityData.high52w)}</span>
              </div>
              <span className="text-xs text-muted-foreground">
                Beta: {formatNumber(securityData.beta, 2)}
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col gap-1">
              <span className="text-sm font-medium text-muted-foreground">Dividend Yield</span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold">{formatPercent(securityData.dividend)}</span>
              </div>
              <span className="text-xs text-muted-foreground">
                Avg Volume: {formatNumber(securityData.avgVolume / 1000000, 1)}M
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BarChart2 className="h-5 w-5" />
            Price Chart
          </CardTitle>
          
          <div className="flex items-center gap-2">
            {CHART_PERIODS.map((p) => (
              <Button
                key={p.value}
                variant={period === p.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPeriod(p.value)}
              >
                {p.label}
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
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
      
      <Tabs defaultValue="overview">
        <TabsList className="grid w-full grid-cols-4 lg:w-auto">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="institutional">Institutional Ownership</TabsTrigger>
          <TabsTrigger value="ftd">FTD Data</TabsTrigger>
          <TabsTrigger value="swap">Swap Theory</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="mt-4 space-y-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Key Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Open</p>
                    <p className="text-lg font-semibold">{formatCurrency(securityData.open)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Previous Close</p>
                    <p className="text-lg font-semibold">{formatCurrency(securityData.previousClose)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Day Range</p>
                    <p className="text-lg font-semibold">{formatCurrency(securityData.price * 0.98)} - {formatCurrency(securityData.price * 1.02)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">52 Week Range</p>
                    <p className="text-lg font-semibold">{formatCurrency(securityData.low52w)} - {formatCurrency(securityData.high52w)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Volume</p>
                    <p className="text-lg font-semibold">{formatNumber(securityData.volume, 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Avg. Volume</p>
                    <p className="text-lg font-semibold">{formatNumber(securityData.avgVolume, 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Market Cap</p>
                    <p className="text-lg font-semibold">{formatCurrency(securityData.marketCap / 1000000000, 'USD', 1)}B</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">P/E Ratio</p>
                    <p className="text-lg font-semibold">{securityData.peRatio ? formatNumber(securityData.peRatio, 2) : 'N/A'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  Volume Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
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
                        tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                        stroke="var(--muted-foreground)"
                        tick={{ fontSize: 12 }}
                      />
                      <Tooltip />
                      <Bar 
                        dataKey="volume" 
                        fill="var(--chart-2)" 
                        name="Volume" 
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="institutional" className="mt-4 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Institutional Ownership
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left text-sm font-medium text-muted-foreground">
                      <th className="pb-2 pl-2 pr-4">Institution</th>
                      <th className="pb-2 px-4">Shares</th>
                      <th className="pb-2 px-4">Value</th>
                      <th className="pb-2 px-4">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockInstitutionalData.map((institution, index) => (
                      <tr key={index} className="border-b last:border-0">
                        <td className="py-3 pl-2 pr-4 font-medium">
                          {institution.name}
                        </td>
                        <td className="py-3 px-4">
                          {formatNumber(institution.shares, 0)}
                        </td>
                        <td className="py-3 px-4">
                          {formatCurrency(institution.value / 1000000, 'USD', 1)}M
                        </td>
                        <td className={`py-3 px-4 ${institution.change > 0 ? 'text-green-500' : institution.change < 0 ? 'text-red-500' : 'text-muted-foreground'}`}>
                          <div className="flex items-center">
                            {institution.change > 0 ? (
                              <ArrowUpRight className="mr-1 h-4 w-4" />
                            ) : institution.change < 0 ? (
                              <ArrowDownRight className="mr-1 h-4 w-4" />
                            ) : null}
                            <span>{formatPercent(Math.abs(institution.change))}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="ftd" className="mt-4 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Failure-to-Deliver (FTD) Data
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b text-left text-sm font-medium text-muted-foreground">
                        <th className="pb-2 pl-2 pr-4">Date</th>
                        <th className="pb-2 px-4">Quantity</th>
                        <th className="pb-2 px-4">Price</th>
                        <th className="pb-2 px-4">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockFTDData.map((ftd, index) => (
                        <tr key={index} className="border-b last:border-0">
                          <td className="py-3 pl-2 pr-4 font-medium">
                            {formatDate(ftd.date)}
                          </td>
                          <td className="py-3 px-4">
                            {formatNumber(ftd.quantity, 0)}
                          </td>
                          <td className="py-3 px-4">
                            {formatCurrency(ftd.price)}
                          </td>
                          <td className="py-3 px-4">
                            {formatCurrency(ftd.value / 1000000, 'USD', 1)}M
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={mockFTDData.map(item => ({
                        ...item,
                        date: new Date(item.date),
                      }))}
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
                        yAxisId="left"
                        tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
                        stroke="var(--chart-3)"
                        tick={{ fontSize: 12 }}
                      />
                      <YAxis 
                        yAxisId="right"
                        orientation="right"
                        tickFormatter={(value) => formatCurrency(value, 'USD', 0)}
                        stroke="var(--chart-4)"
                        tick={{ fontSize: 12 }}
                      />
                      <Tooltip />
                      <Legend />
                      <Area 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="quantity" 
                        stroke="var(--chart-3)" 
                        fill="var(--chart-3)" 
                        fillOpacity={0.3}
                        name="FTD Quantity" 
                      />
                      <Line 
                        yAxisId="right"
                        type="monotone" 
                        dataKey="price" 
                        stroke="var(--chart-4)" 
                        name="Price" 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="swap" className="mt-4 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Swap Theory Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-muted-foreground">
                  Swap theory analysis examines the relationship between derivatives contracts, 
                  particularly total return swaps, and their impact on the underlying security's price movements.
                  This analysis helps identify potential cycle patterns in price action.
                </p>
                
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
                      <Tooltip />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="close" 
                        stroke="var(--chart-1)" 
                        strokeWidth={2}
                        name="Close Price"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="open" 
                        stroke="var(--chart-5)" 
                        strokeWidth={1}
                        strokeDasharray="5 5"
                        name="Cycle Prediction"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="rounded-lg border p-4">
                  <h3 className="mb-2 font-semibold">Cycle Analysis</h3>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Current Cycle</p>
                      <p className="text-lg font-semibold">Accumulation Phase</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Estimated Next Peak</p>
                      <p className="text-lg font-semibold">Aug 15, 2023</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Confidence Score</p>
                      <p className="text-lg font-semibold">72%</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SecurityDetail;

