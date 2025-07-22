'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { BarChart, LineChart, PieChart, Users, Target, Award, Clock, Calendar, Filter, Download } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { format } from 'date-fns';

// Mock data - in a real app, this would come from an API
const performanceData = {
  overview: {
    totalEmployees: 124,
    onTrack: 84,
    atRisk: 22,
    needsAttention: 18,
    averageRating: 4.2,
    ratingChange: 0.3,
    completedGoals: 456,
    totalGoals: 620,
    pendingReviews: 28,
    overdueReviews: 5,
  },
  metrics: [
    { name: 'Q1', value: 3.8 },
    { name: 'Q2', value: 4.1 },
    { name: 'Q3', value: 4.2 },
    { name: 'Q4', value: 4.5 },
  ],
  departments: [
    { name: 'Engineering', value: 4.3, change: 0.2 },
    { name: 'Marketing', value: 4.1, change: 0.1 },
    { name: 'Sales', value: 4.4, change: 0.4 },
    { name: 'HR', value: 4.2, change: 0.0 },
    { name: 'Operations', value: 4.0, change: -0.1 },
  ],
  recentActivities: [
    { id: 1, employee: 'John Doe', action: 'completed', target: 'Q4 Performance Review', time: '2 hours ago' },
    { id: 2, employee: 'Jane Smith', action: 'submitted', target: 'Q4 Goals', time: '4 hours ago' },
    { id: 3, employee: 'Mike Johnson', action: 'requested feedback', target: 'Project Alpha', time: '1 day ago' },
    { id: 4, employee: 'Sarah Williams', action: 'achieved', target: 'Sales Target Q4', time: '2 days ago' },
    { id: 5, employee: 'David Brown', action: 'completed', target: 'Training: Leadership 101', time: '3 days ago' },
  ],
};

export default function PerformanceDashboard() {
  const [dateRange, setDateRange] = useState({
    from: new Date(2023, 0, 1),
    to: new Date(2023, 11, 31),
  });
  const [timeframe, setTimeframe] = useState('quarterly');
  const [department, setDepartment] = useState('all');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Performance Dashboard</h1>
          <p className="text-muted-foreground">
            Track and manage employee performance metrics and goals
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-[180px]">
              <Calendar className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Select timeframe" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="weekly">This Week</SelectItem>
              <SelectItem value="monthly">This Month</SelectItem>
              <SelectItem value="quarterly">This Quarter</SelectItem>
              <SelectItem value="yearly">This Year</SelectItem>
              <SelectItem value="custom">Custom Range</SelectItem>
            </SelectContent>
          </Select>
          
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="w-[240px] justify-start text-left font-normal">
                <Calendar className="mr-2 h-4 w-4" />
                {dateRange?.from ? (
                  dateRange.to ? (
                    <>
                      {format(dateRange.from, 'MMM dd, yyyy')} -{' '}
                      {format(dateRange.to, 'MMM dd, yyyy')}
                    </>
                  ) : (
                    format(dateRange.from, 'MMM dd, yyyy')
                  )
                ) : (
                  <span>Pick a date range</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <CalendarComponent
                initialFocus
                mode="range"
                defaultMonth={dateRange?.from}
                selected={dateRange}
                onSelect={(range) => setDateRange(range || { from: new Date(), to: new Date() })}
                numberOfMonths={2}
              />
            </PopoverContent>
          </Popover>
          
          <Select value={department} onValueChange={setDepartment}>
            <SelectTrigger className="w-[180px]">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="All Departments" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Departments</SelectItem>
              <SelectItem value="engineering">Engineering</SelectItem>
              <SelectItem value="marketing">Marketing</SelectItem>
              <SelectItem value="sales">Sales</SelectItem>
              <SelectItem value="hr">Human Resources</SelectItem>
              <SelectItem value="operations">Operations</SelectItem>
            </SelectContent>
          </Select>
          
          <Button variant="outline" size="icon">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{performanceData.overview.averageRating.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              {performanceData.overview.ratingChange >= 0 ? '+' : ''}
              {performanceData.overview.ratingChange} from last period
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Employees On Track</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{performanceData.overview.onTrack}</div>
            <div className="mt-2">
              <Progress value={(performanceData.overview.onTrack / performanceData.overview.totalEmployees) * 100} className="h-2" />
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {Math.round((performanceData.overview.onTrack / performanceData.overview.totalEmployees) * 100)}% of total
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Goals Completion</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {performanceData.overview.completedGoals} / {performanceData.overview.totalGoals}
            </div>
            <div className="mt-2">
              <Progress 
                value={(performanceData.overview.completedGoals / performanceData.overview.totalGoals) * 100} 
                className="h-2" 
              />
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {Math.round((performanceData.overview.completedGoals / performanceData.overview.totalGoals) * 100)}% completed
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Reviews</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{performanceData.overview.pendingReviews}</div>
            <div className="flex items-center mt-1">
              <Badge variant="destructive" className="mr-2">
                {performanceData.overview.overdueReviews} Overdue
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Due soon: {performanceData.overview.pendingReviews - performanceData.overview.overdueReviews}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Performance Trend */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Performance Trend</CardTitle>
            <CardDescription>
              Average performance rating over time
            </CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-[300px] flex items-center justify-center bg-muted/20 rounded-md">
              <LineChart className="h-8 w-8 text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Performance trend chart</span>
            </div>
          </CardContent>
        </Card>
        
        {/* Department Performance */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Department Performance</CardTitle>
            <CardDescription>
              Average ratings by department
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {performanceData.departments.map((dept) => (
                <div key={dept.name} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{dept.name}</span>
                    <div className="flex items-center">
                      <span className="font-medium mr-2">{dept.value.toFixed(1)}</span>
                      <span className={`text-xs ${dept.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {dept.change >= 0 ? '+' : ''}{dept.change}
                      </span>
                    </div>
                  </div>
                  <Progress value={(dept.value / 5) * 100} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        {/* Recent Activities */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activities</CardTitle>
            <CardDescription>
              Latest performance-related activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {performanceData.recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start pb-4 last:pb-0 last:border-0 border-b">
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center mr-3 mt-1">
                    <span className="text-sm font-medium text-primary">
                      {activity.employee.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{activity.employee}</h4>
                      <span className="text-xs text-muted-foreground">{activity.time}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {activity.action} {activity.target}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        {/* Performance Distribution */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Performance Distribution</CardTitle>
            <CardDescription>
              Employee performance ratings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center bg-muted/20 rounded-md">
              <PieChart className="h-8 w-8 text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Performance distribution chart</span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Quick Actions */}
      <div className="flex flex-wrap gap-2">
        <Button variant="outline">
          <Target className="mr-2 h-4 w-4" />
          Set Team Goals
        </Button>
        <Button variant="outline">
          <Users className="mr-2 h-4 w-4" />
          Schedule 1:1s
        </Button>
        <Button variant="outline">
          <Award className="mr-2 h-4 w-4" />
          Recognize Achievement
        </Button>
        <Button variant="outline">
          <BarChart className="mr-2 h-4 w-4" />
          Generate Report
        </Button>
      </div>
    </div>
  );
}
