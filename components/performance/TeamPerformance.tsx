'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, BarChart2, Filter, Download, MoreHorizontal, Search } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/components/ui/use-toast';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

interface TeamMember {
  id: string;
  name: string;
  avatar?: string;
  department: string;
  position: string;
  performance: {
    rating: number;
    trend: 'up' | 'down' | 'neutral';
    completedGoals: number;
    totalGoals: number;
    lastReviewDate: string;
  };
  status: 'on-track' | 'at-risk' | 'exceeding' | 'needs-improvement';
  lastActive: string;
}

export default function TeamPerformance() {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const { toast } = useToast();

  useEffect(() => {
    // Simulate API call
    const fetchTeamPerformance = async () => {
      try {
        setIsLoading(true);
        // In a real app, this would be an API call
        // const response = await fetch('/api/performance/team');
        // const data = await response.json();
        
        // Mock data
        const mockTeam: TeamMember[] = [
          {
            id: '1',
            name: 'John Doe',
            department: 'Engineering',
            position: 'Senior Developer',
            avatar: '/avatars/john-doe.jpg',
            performance: {
              rating: 4.5,
              trend: 'up',
              completedGoals: 8,
              totalGoals: 10,
              lastReviewDate: '2023-11-15',
            },
            status: 'exceeding',
            lastActive: '2023-12-20T14:30:00Z',
          },
          // Add more team members as needed
        ];
        
        setTeamMembers(mockTeam);
      } catch (error) {
        console.error('Error fetching team performance:', error);
        toast({
          title: 'Error',
          description: 'Failed to load team performance data',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchTeamPerformance();
  }, [toast]);

  const filteredMembers = teamMembers.filter(member => {
    const matchesSearch = 
      member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.position.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDepartment = departmentFilter === 'all' || member.department === departmentFilter;
    const matchesStatus = statusFilter === 'all' || member.status === statusFilter;
    
    return matchesSearch && matchesDepartment && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const statusMap = {
      'on-track': { label: 'On Track', variant: 'default' as const, color: 'bg-green-500' },
      'exceeding': { label: 'Exceeding', variant: 'success' as const, color: 'bg-emerald-500' },
      'at-risk': { label: 'At Risk', variant: 'destructive' as const, color: 'bg-red-500' },
      'needs-improvement': { label: 'Needs Improvement', variant: 'warning' as const, color: 'bg-yellow-500' },
    };

    const statusConfig = statusMap[status as keyof typeof statusMap] || { label: status, variant: 'outline' as const };
    
    return (
      <Badge variant={statusConfig.variant} className="capitalize">
        <span className={`w-2 h-2 rounded-full ${statusConfig.color} mr-2`}></span>
        {statusConfig.label}
      </Badge>
    );
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return <span className="text-green-500">↑</span>;
      case 'down':
        return <span className="text-red-500">↓</span>;
      default:
        return <span className="text-gray-500">→</span>;
    }
  };

  const departments = Array.from(new Set(teamMembers.map(member => member.department)));

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
        <CardTitle className="text-lg font-medium flex items-center">
          <Users className="h-5 w-5 mr-2" />
          Team Performance
        </CardTitle>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button size="sm">
            <BarChart2 className="mr-2 h-4 w-4" />
            View Analytics
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search team members..."
              className="pl-8 w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-9">
                  <Filter className="mr-2 h-4 w-4" />
                  Department: {departmentFilter === 'all' ? 'All' : departmentFilter}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setDepartmentFilter('all')}>
                  All Departments
                </DropdownMenuItem>
                {departments.map(dept => (
                  <DropdownMenuItem 
                    key={dept} 
                    onClick={() => setDepartmentFilter(dept)}
                  >
                    {dept}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-9">
                  <Filter className="mr-2 h-4 w-4" />
                  Status: {statusFilter === 'all' ? 'All' : statusFilter.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setStatusFilter('all')}>
                  All Statuses
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('on-track')}>
                  On Track
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('exceeding')}>
                  Exceeding
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('at-risk')}>
                  At Risk
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('needs-improvement')}>
                  Needs Improvement
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[300px]">Team Member</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Rating</TableHead>
                <TableHead>Goals</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Last Active</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredMembers.length > 0 ? (
                filteredMembers.map((member) => (
                  <TableRow key={member.id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">
                      <div className="flex items-center">
                        <Avatar className="h-9 w-9 mr-3">
                          <AvatarImage src={member.avatar} alt={member.name} />
                          <AvatarFallback>
                            {member.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">{member.name}</div>
                          <div className="text-sm text-muted-foreground">{member.position}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{member.department}</TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        {member.performance.rating.toFixed(1)}
                        <span className="ml-1">
                          {getTrendIcon(member.performance.trend)}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <Progress 
                          value={(member.performance.completedGoals / member.performance.totalGoals) * 100} 
                          className="h-2 w-24 mr-2" 
                        />
                        <span className="text-sm text-muted-foreground">
                          {member.performance.completedGoals}/{member.performance.totalGoals}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(member.status)}</TableCell>
                    <TableCell className="text-right text-sm text-muted-foreground">
                      {new Date(member.lastActive).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center">
                    No team members found matching your criteria.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
        
        <div className="flex items-center justify-between mt-4 text-sm text-muted-foreground">
          <div>Showing {filteredMembers.length} of {teamMembers.length} team members</div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" disabled>
              Previous
            </Button>
            <Button variant="outline" size="sm" disabled>
              Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
