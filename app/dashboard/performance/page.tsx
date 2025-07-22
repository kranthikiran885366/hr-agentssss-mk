'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { BarChart, Target, Users, FileText, Plus } from 'lucide-react';

// Performance Components
import PerformanceDashboard from '@/components/performance/PerformanceDashboard';
import PerformanceReviews from '@/components/performance/PerformanceReviews';
import TeamPerformance from '@/components/performance/TeamPerformance';
import GoalsList from '@/components/performance/GoalsList';
import PerformanceChart from '@/components/performance/PerformanceChart';

export default function PerformancePage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('dashboard');

  // Redirect if not authenticated
  if (status === 'unauthenticated') {
    router.push('/auth/signin');
    return null;
  }

  // Show loading state
  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading performance data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 px-4">
      <div className="flex flex-col space-y-6">
        {/* Header */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold tracking-tight">Performance Management</h1>
            <div className="flex items-center space-x-2">
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Goal
              </Button>
            </div>
          </div>
          <p className="text-muted-foreground">
            Track and manage employee performance, goals, and reviews
          </p>
        </div>

        {/* Main Content */}
        <Tabs 
          defaultValue="dashboard" 
          className="space-y-6"
          onValueChange={setActiveTab}
        >
          <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 lg:w-auto lg:grid-cols-5">
            <TabsTrigger value="dashboard">
              <BarChart className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="goals">
              <Target className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Goals</span>
            </TabsTrigger>
            <TabsTrigger value="reviews">
              <FileText className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Reviews</span>
            </TabsTrigger>
            <TabsTrigger value="team">
              <Users className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Team</span>
            </TabsTrigger>
            <TabsTrigger value="reports" className="hidden lg:flex">
              <BarChart className="h-4 w-4 mr-2" />
              <span>Reports</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <PerformanceDashboard />
          </TabsContent>

          <TabsContent value="goals" className="space-y-6">
            <GoalsList />
          </TabsContent>

          <TabsContent value="reviews" className="space-y-6">
            <PerformanceReviews />
          </TabsContent>

          <TabsContent value="team" className="space-y-6">
            <TeamPerformance />
          </TabsContent>

          <TabsContent value="reports" className="space-y-6">
            <PerformanceChart />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
