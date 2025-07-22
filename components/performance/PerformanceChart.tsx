'use client';

import { useEffect, useRef, useState } from 'react';
import { useTheme } from 'next-themes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartOptions,
  ChartData,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const timeRanges = [
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '90', label: 'Last 3 months' },
  { value: '365', label: 'Last year' },
];

const chartTypes = [
  { value: 'overall', label: 'Overall Performance' },
  { value: 'goals', label: 'Goal Completion' },
  { value: 'reviews', label: 'Review Ratings' },
];

export default function PerformanceChart() {
  const { theme } = useTheme();
  const [timeRange, setTimeRange] = useState('30');
  const [chartType, setChartType] = useState('overall');
  const [isLoading, setIsLoading] = useState(true);
  const [chartData, setChartData] = useState<ChartData<'line'>>({
    labels: [],
    datasets: [],
  });

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setIsLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Generate mock data based on time range and chart type
        const days = parseInt(timeRange);
        const labels = [];
        const today = new Date();
        
        for (let i = days; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }

        let datasets = [];
        
        if (chartType === 'overall') {
          datasets = [
            {
              label: 'Performance Score',
              data: labels.map((_, i) => {
                const base = Math.sin(i / 3) * 10 + 70;
                return Math.min(100, Math.max(0, base + (Math.random() * 10 - 5)));
              }),
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              tension: 0.4,
              fill: true,
            },
          ];
        } else if (chartType === 'goals') {
          datasets = [
            {
              label: 'Goal Completion %',
              data: labels.map((_, i) => {
                const base = Math.min(100, 30 + (i * (70 / days)) + (Math.random() * 15 - 7.5));
                return Math.round(base * 10) / 10;
              }),
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              tension: 0.4,
              fill: true,
            },
          ];
        } else {
          datasets = [
            {
              label: 'Technical Skills',
              data: labels.map(() => 3 + Math.random() * 2),
              borderColor: '#8b5cf6',
              backgroundColor: 'transparent',
              tension: 0.4,
            },
            {
              label: 'Communication',
              data: labels.map(() => 2.5 + Math.random() * 2.5),
              borderColor: '#ec4899',
              backgroundColor: 'transparent',
              tension: 0.4,
            },
            {
              label: 'Teamwork',
              data: labels.map(() => 3.5 + Math.random() * 1.5),
              borderColor: '#f59e0b',
              backgroundColor: 'transparent',
              tension: 0.4,
            },
          ];
        }

        setChartData({
          labels,
          datasets,
        });
      } catch (error) {
        console.error('Error fetching chart data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChartData();
  }, [timeRange, chartType]);

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: theme === 'dark' ? '#e2e8f0' : '#475569',
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
        titleColor: theme === 'dark' ? '#e2e8f0' : '#1e293b',
        bodyColor: theme === 'dark' ? '#cbd5e1' : '#475569',
        borderColor: theme === 'dark' ? '#334155' : '#e2e8f0',
        borderWidth: 1,
        padding: 12,
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
    },
    scales: {
      x: {
        grid: {
          color: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          color: theme === 'dark' ? '#94a3b8' : '#64748b',
          maxRotation: 0,
          autoSkip: true,
          maxTicksLimit: 7,
        },
        border: {
          display: false,
        },
      },
      y: {
        beginAtZero: chartType !== 'reviews',
        max: chartType === 'reviews' ? 5 : 100,
        grid: {
          color: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          color: theme === 'dark' ? '#94a3b8' : '#64748b',
          callback: (value) => {
            if (chartType === 'reviews') return value.toFixed(1);
            return `${value}${chartType === 'overall' ? '%' : ''}`;
          },
        },
        border: {
          display: false,
        },
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
    elements: {
      point: {
        radius: 0,
        hoverRadius: 6,
        hoverBorderWidth: 2,
      },
    },
  };

  if (isLoading) {
    return (
      <div className="h-[350px] w-full">
        <Skeleton className="h-full w-full" />
      </div>
    );
  }

  return (
    <div className="h-[350px] w-full">
      <div className="flex justify-between items-center mb-4">
        <Select value={chartType} onValueChange={setChartType}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select chart type" />
          </SelectTrigger>
          <SelectContent>
            {chartTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Select time range" />
          </SelectTrigger>
          <SelectContent>
            {timeRanges.map((range) => (
              <SelectItem key={range.value} value={range.value}>
                {range.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      <div className="h-[calc(100%-48px)]">
        <Line 
          data={chartData} 
          options={options} 
          className="w-full h-full"
        />
      </div>
    </div>
  );
}
