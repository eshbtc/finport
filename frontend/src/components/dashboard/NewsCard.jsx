import React from 'react';
import { Newspaper, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatDate } from '@/lib/utils';

// Mock news data
const mockNewsData = [
  {
    id: 1,
    title: 'Federal Reserve Holds Interest Rates Steady, Signals Potential Cuts Later This Year',
    source: 'Financial Times',
    date: '2023-07-15T14:30:00Z',
    url: 'https://example.com/news/1',
  },
  {
    id: 2,
    title: 'Tech Stocks Rally as Earnings Beat Expectations',
    source: 'Wall Street Journal',
    date: '2023-07-14T10:15:00Z',
    url: 'https://example.com/news/2',
  },
  {
    id: 3,
    title: 'Inflation Data Shows Cooling Trend, Consumer Prices Rise Less Than Expected',
    source: 'Bloomberg',
    date: '2023-07-13T16:45:00Z',
    url: 'https://example.com/news/3',
  },
  {
    id: 4,
    title: 'Market Volatility Increases Amid Geopolitical Tensions',
    source: 'Reuters',
    date: '2023-07-12T09:20:00Z',
    url: 'https://example.com/news/4',
  },
  {
    id: 5,
    title: 'Retail Sales Data Exceeds Forecasts, Consumer Spending Remains Strong',
    source: 'CNBC',
    date: '2023-07-11T13:10:00Z',
    url: 'https://example.com/news/5',
  },
];

const NewsCard = () => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Newspaper className="h-5 w-5" />
          Market News
        </CardTitle>
        <Button variant="outline" size="sm">
          More News
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockNewsData.map((news) => (
            <div key={news.id} className="border-b pb-4 last:border-0 last:pb-0">
              <a 
                href={news.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="group"
              >
                <h3 className="font-medium group-hover:underline">
                  {news.title}
                </h3>
                <div className="mt-1 flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {news.source}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {formatDate(news.date)}
                    </span>
                    <ExternalLink className="h-3 w-3 text-muted-foreground" />
                  </div>
                </div>
              </a>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default NewsCard;

