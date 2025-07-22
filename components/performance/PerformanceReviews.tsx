'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Search, Filter, Download, MoreHorizontal } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/components/ui/use-toast';
import { format } from 'date-fns';

interface Review {
  id: string;
  employee: {
    id: string;
    name: string;
    avatar?: string;
    department: string;
  };
  reviewer: {
    id: string;
    name: string;
    role: string;
  };
  period: {
    start: string;
    end: string;
  };
  status: 'draft' | 'in-progress' | 'completed' | 'approved' | 'rejected';
  overallRating: number;
  lastUpdated: string;
  goalsCompleted: number;
  totalGoals: number;
  isSelfReview: boolean;
}

export default function PerformanceReviews() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const { toast } = useToast();

  useEffect(() => {
    // Simulate API call
    const fetchReviews = async () => {
      try {
        setIsLoading(true);
        // In a real app, this would be an API call
        // const response = await fetch('/api/performance/reviews');
        // const data = await response.json();
        
        // Mock data
        const mockReviews: Review[] = [
          {
            id: '1',
            employee: { id: '1', name: 'John Doe', department: 'Engineering' },
            reviewer: { id: '2', name: 'Jane Smith', role: 'Manager' },
            period: { 
              start: '2023-01-01', 
              end: '2023-12-31' 
            },
            status: 'completed',
            overallRating: 4.2,
            lastUpdated: '2023-12-15T10:30:00Z',
            goalsCompleted: 8,
            totalGoals: 10,
            isSelfReview: false,
          },
          // Add more mock reviews as needed
        ];
        
        setReviews(mockReviews);
      } catch (error) {
        console.error('Error fetching reviews:', error);
        toast({
          title: 'Error',
          description: 'Failed to load performance reviews',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchReviews();
  }, [toast]);

  const filteredReviews = reviews.filter(review => {
    const matchesSearch = 
      review.employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      review.reviewer.name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || review.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const statusMap = {
      draft: { label: 'Draft', variant: 'outline' as const },
      'in-progress': { label: 'In Progress', variant: 'secondary' as const },
      completed: { label: 'Completed', variant: 'default' as const },
      approved: { label: 'Approved', variant: 'success' as const },
      rejected: { label: 'Needs Revision', variant: 'destructive' as const },
    };

    const statusConfig = statusMap[status as keyof typeof statusMap] || { label: status, variant: 'outline' as const };
    
    return (
      <Badge variant={statusConfig.variant} className="capitalize">
        {statusConfig.label}
      </Badge>
    );
  };

  const handleStartReview = (reviewId: string) => {
    // Navigate to review form
    console.log('Starting review:', reviewId);
    // router.push(`/dashboard/performance/reviews/${reviewId}`);
  };

  if (isLoading) {
    return <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-20 bg-muted/20 animate-pulse rounded-md" />
      ))}
    </div>;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg font-medium">Performance Reviews</CardTitle>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button size="sm">
            <Plus className="mr-2 h-4 w-4" />
            New Review
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search reviews..."
                className="pl-8 w-[200px] lg:w-[300px]"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-9">
                  <Filter className="mr-2 h-4 w-4" />
                  Status: {statusFilter === 'all' ? 'All' : statusFilter.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem onClick={() => setStatusFilter('all')}>
                  All
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('draft')}>
                  Draft
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('in-progress')}>
                  In Progress
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('completed')}>
                  Completed
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('approved')}>
                  Approved
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('rejected')}>
                  Needs Revision
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="rounded-md border
```
