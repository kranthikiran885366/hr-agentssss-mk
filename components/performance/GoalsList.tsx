'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { MoreHorizontal, ArrowUpDown, Plus } from 'lucide-react';
import { format } from 'date-fns';
import { useRouter } from 'next/navigation';
import { Skeleton } from '@/components/ui/skeleton';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Goal {
  id: string;
  title: string;
  description: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'AT_RISK';
  progress: number;
  startDate: string;
  endDate: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  employee: {
    name: string;
    email: string;
  };
}

export default function GoalsList() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortConfig, setSortConfig] = useState<{ key: keyof Goal; direction: 'asc' | 'desc' } | null>(null);
  const [filter, setFilter] = useState<'all' | 'my' | 'team'>('all');

  useEffect(() => {
    if (status === 'authenticated') {
      fetchGoals();
    }
  }, [status, filter]);

  const fetchGoals = async () => {
    try {
      setIsLoading(true);
      const params = new URLSearchParams();
      if (filter === 'my') params.set('employeeId', session?.user?.id || '');
      if (filter === 'team') params.set('team', 'true');
      
      const response = await fetch(`/api/performance/goals?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch goals');
      }
      const data = await response.json();
      setGoals(data.data || []);
    } catch (error) {
      console.error('Error fetching goals:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSort = (key: keyof Goal) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedGoals = [...goals].sort((a, b) => {
    if (!sortConfig) return 0;
    
    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];
    
    if (aValue === bValue) return 0;
    
    if (aValue < bValue) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }
    return sortConfig.direction === 'asc' ? 1 : -1;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <Badge variant="success">Completed</Badge>;
      case 'IN_PROGRESS':
        return <Badge variant="default">In Progress</Badge>;
      case 'AT_RISK':
        return <Badge variant="destructive">At Risk</Badge>;
      default:
        return <Badge variant="outline">Not Started</Badge>;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'HIGH':
        return <Badge variant="destructive">High</Badge>;
      case 'MEDIUM':
        return <Badge variant="warning">Medium</Badge>;
      default:
        return <Badge variant="outline">Low</Badge>;
    }
  };

  const handleGoalClick = (goalId: string) => {
    router.push(`/dashboard/performance/goals/${goalId}`);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-36" />
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-64" />
                    <Skeleton className="h-4 w-48" />
                  </div>
                  <div className="flex items-center space-x-4">
                    <Skeleton className="h-6 w-24" />
                    <Skeleton className="h-8 w-8 rounded-full" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center space-x-2">
          <Button 
            variant={filter === 'all' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setFilter('all')}
          >
            All Goals
          </Button>
          <Button 
            variant={filter === 'my' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setFilter('my')}
          >
            My Goals
          </Button>
          {session?.user?.role !== 'USER' && (
            <Button 
              variant={filter === 'team' ? 'default' : 'outline'} 
              size="sm"
              onClick={() => setFilter('team')}
            >
              Team Goals
            </Button>
          )}
        </div>
        <Button 
          size="sm" 
          className="w-full sm:w-auto"
          onClick={() => router.push('/dashboard/performance/goals/new')}
        >
          <Plus className="mr-2 h-4 w-4" /> New Goal
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Performance Goals</CardTitle>
        </CardHeader>
        <CardContent>
          {sortedGoals.length === 0 ? (
            <div className="text-center py-12">
              <h3 className="text-lg font-medium">No goals found</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {filter === 'my' 
                  ? "You don't have any goals yet." 
                  : filter === 'team'
                    ? "Your team doesn't have any goals yet."
                    : "No goals have been created yet."}
              </p>
              <Button 
                className="mt-4" 
                onClick={() => router.push('/dashboard/performance/goals/new')}
              >
                <Plus className="mr-2 h-4 w-4" /> Create Goal
              </Button>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[300px]">
                      <button 
                        className="flex items-center"
                        onClick={() => handleSort('title')}
                      >
                        Title
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                      </button>
                    </TableHead>
                    {filter === 'all' && (
                      <TableHead>
                        <button 
                          className="flex items-center"
                          onClick={() => handleSort('employee')}
                        >
                          Employee
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </button>
                      </TableHead>
                    )}
                    <TableHead>
                      <div className="flex items-center">
                        Progress
                        <ArrowUpDown 
                          className="ml-2 h-4 w-4 cursor-pointer"
                          onClick={() => handleSort('progress')}
                        />
                      </div>
                    </TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>
                      <div className="flex items-center">
                        Due Date
                        <ArrowUpDown 
                          className="ml-2 h-4 w-4 cursor-pointer"
                          onClick={() => handleSort('endDate')}
                        />
                      </div>
                    </TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedGoals.map((goal) => (
                    <TableRow 
                      key={goal.id} 
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => handleGoalClick(goal.id)}
                    >
                      <TableCell className="font-medium">
                        <div className="font-medium">{goal.title}</div>
                        <div className="text-sm text-muted-foreground line-clamp-1">
                          {goal.description}
                        </div>
                      </TableCell>
                      {filter === 'all' && (
                        <TableCell>
                          <div className="font-medium">{goal.employee.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {goal.employee.email}
                          </div>
                        </TableCell>
                      )}
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Progress value={goal.progress} className="h-2 w-24" />
                          <span className="text-sm font-medium">{goal.progress}%</span>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(goal.status)}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {format(new Date(goal.endDate), 'MMM d, yyyy')}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(goal.endDate) > new Date() 
                            ? `Due in ${Math.ceil((new Date(goal.endDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days`
                            : 'Past due'}
                        </div>
                      </TableCell>
                      <TableCell>{getPriorityBadge(goal.priority)}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Open menu</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleGoalClick(goal.id)}>
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive">
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
