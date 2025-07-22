"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  DollarSign,
  Users,
  Calendar,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  Download,
  Send,
  Calculator,
  PieChart,
} from "lucide-react"

interface PayrollRun {
  id: string
  pay_period_start: string
  pay_period_end: string
  processed_at: string
  status: string
  employee_payrolls: EmployeePayroll[]
  totals: {
    gross_pay: number
    net_pay: number
    total_taxes: number
    total_deductions: number
    employer_costs: number
  }
}

interface EmployeePayroll {
  employee_id: string
  employee_name: string
  gross_pay: number
  total_taxes: number
  total_deductions: number
  net_pay: number
  time_data: {
    regular_hours: number
    overtime_hours: number
    total_hours: number
  }
}

export function PayrollDashboard() {
  const [currentPayrollRun, setCurrentPayrollRun] = useState<PayrollRun | null>(null)
  const [payrollHistory, setPayrollHistory] = useState<PayrollRun[]>([])
  const [loading, setLoading] = useState(false)
  const [processingPayroll, setProcessingPayroll] = useState(false)

  useEffect(() => {
    fetchPayrollData()
  }, [])

  const fetchPayrollData = async () => {
    try {
      setLoading(true)
      // Mock data - in real app, fetch from API
      const mockPayrollRun: PayrollRun = {
        id: "payroll-2024-01",
        pay_period_start: "2024-01-01",
        pay_period_end: "2024-01-15",
        processed_at: "2024-01-16T10:00:00Z",
        status: "completed",
        employee_payrolls: [
          {
            employee_id: "emp-1",
            employee_name: "John Doe",
            gross_pay: 5000.0,
            total_taxes: 1200.0,
            total_deductions: 300.0,
            net_pay: 3500.0,
            time_data: {
              regular_hours: 80,
              overtime_hours: 0,
              total_hours: 80,
            },
          },
          {
            employee_id: "emp-2",
            employee_name: "Jane Smith",
            gross_pay: 4500.0,
            total_taxes: 1080.0,
            total_deductions: 270.0,
            net_pay: 3150.0,
            time_data: {
              regular_hours: 80,
              overtime_hours: 0,
              total_hours: 80,
            },
          },
        ],
        totals: {
          gross_pay: 9500.0,
          net_pay: 6650.0,
          total_taxes: 2280.0,
          total_deductions: 570.0,
          employer_costs: 1425.0,
        },
      }

      setCurrentPayrollRun(mockPayrollRun)
      setPayrollHistory([mockPayrollRun])
    } catch (error) {
      console.error("Failed to fetch payroll data:", error)
    } finally {
      setLoading(false)
    }
  }

  const processPayroll = async () => {
    try {
      setProcessingPayroll(true)

      const response = await fetch("/api/payroll/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pay_period_start: "2024-01-16",
          pay_period_end: "2024-01-31",
        }),
      })

      const payrollRun = await response.json()
      setCurrentPayrollRun(payrollRun)
    } catch (error) {
      console.error("Failed to process payroll:", error)
    } finally {
      setProcessingPayroll(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600"
      case "processing":
        return "text-yellow-600"
      case "failed":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4" />
      case "processing":
        return <Clock className="h-4 w-4" />
      case "failed":
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Payroll Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Gross Pay</p>
                <p className="text-2xl font-bold">${currentPayrollRun?.totals.gross_pay.toLocaleString() || "0"}</p>
              </div>
              <DollarSign className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Net Pay</p>
                <p className="text-2xl font-bold">${currentPayrollRun?.totals.net_pay.toLocaleString() || "0"}</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Taxes</p>
                <p className="text-2xl font-bold">${currentPayrollRun?.totals.total_taxes.toLocaleString() || "0"}</p>
              </div>
              <Calculator className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Employer Costs</p>
                <p className="text-2xl font-bold">
                  ${currentPayrollRun?.totals.employer_costs.toLocaleString() || "0"}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Current Payroll Run */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Current Pay Period
            </CardTitle>
            <div className="flex gap-2">
              <Button onClick={processPayroll} disabled={processingPayroll} className="flex items-center gap-2">
                <Calculator className="h-4 w-4" />
                {processingPayroll ? "Processing..." : "Process Payroll"}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {currentPayrollRun ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h3 className="font-semibold">
                    Pay Period: {new Date(currentPayrollRun.pay_period_start).toLocaleDateString()} -{" "}
                    {new Date(currentPayrollRun.pay_period_end).toLocaleDateString()}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Processed: {new Date(currentPayrollRun.processed_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(currentPayrollRun.status)}
                  <Badge variant={currentPayrollRun.status === "completed" ? "default" : "secondary"}>
                    {currentPayrollRun.status}
                  </Badge>
                </div>
              </div>

              <Tabs defaultValue="summary" className="w-full">
                <TabsList>
                  <TabsTrigger value="summary">Summary</TabsTrigger>
                  <TabsTrigger value="employees">Employees</TabsTrigger>
                  <TabsTrigger value="taxes">Tax Breakdown</TabsTrigger>
                  <TabsTrigger value="reports">Reports</TabsTrigger>
                </TabsList>

                <TabsContent value="summary" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Payroll Breakdown</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>Gross Pay:</span>
                          <span className="font-semibold">${currentPayrollRun.totals.gross_pay.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-red-600">
                          <span>Total Taxes:</span>
                          <span className="font-semibold">
                            -${currentPayrollRun.totals.total_taxes.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex justify-between text-red-600">
                          <span>Total Deductions:</span>
                          <span className="font-semibold">
                            -${currentPayrollRun.totals.total_deductions.toLocaleString()}
                          </span>
                        </div>
                        <div className="border-t pt-2">
                          <div className="flex justify-between text-lg font-bold">
                            <span>Net Pay:</span>
                            <span className="text-green-600">${currentPayrollRun.totals.net_pay.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-3">Employer Costs</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>Payroll Taxes:</span>
                          <span className="font-semibold">$850.00</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Benefits Contributions:</span>
                          <span className="font-semibold">$425.00</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Workers' Comp:</span>
                          <span className="font-semibold">$150.00</span>
                        </div>
                        <div className="border-t pt-2">
                          <div className="flex justify-between text-lg font-bold">
                            <span>Total Employer Cost:</span>
                            <span>${currentPayrollRun.totals.employer_costs.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="employees" className="space-y-4">
                  <div className="space-y-4">
                    {currentPayrollRun.employee_payrolls.map((emp) => (
                      <Card key={emp.employee_id}>
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-4">
                            <h4 className="font-semibold">{emp.employee_name}</h4>
                            <Badge variant="outline">{emp.time_data.total_hours} hours</Badge>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Gross Pay:</span>
                              <div className="font-semibold">${emp.gross_pay.toLocaleString()}</div>
                            </div>
                            <div>
                              <span className="text-gray-600">Taxes:</span>
                              <div className="font-semibold text-red-600">-${emp.total_taxes.toLocaleString()}</div>
                            </div>
                            <div>
                              <span className="text-gray-600">Deductions:</span>
                              <div className="font-semibold text-red-600">
                                -${emp.total_deductions.toLocaleString()}
                              </div>
                            </div>
                            <div>
                              <span className="text-gray-600">Net Pay:</span>
                              <div className="font-semibold text-green-600">${emp.net_pay.toLocaleString()}</div>
                            </div>
                          </div>

                          <div className="mt-3">
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                              <span>Take-home percentage</span>
                              <span>{((emp.net_pay / emp.gross_pay) * 100).toFixed(1)}%</span>
                            </div>
                            <Progress value={(emp.net_pay / emp.gross_pay) * 100} className="h-2" />
                          </div>

                          <div className="mt-3 flex gap-2">
                            <Button size="sm" variant="outline" className="flex items-center gap-1 bg-transparent">
                              <FileText className="h-3 w-3" />
                              Pay Stub
                            </Button>
                            <Button size="sm" variant="outline" className="flex items-center gap-1 bg-transparent">
                              <Send className="h-3 w-3" />
                              Send
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="taxes" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Federal Taxes</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span>Federal Income Tax:</span>
                            <span className="font-semibold">$1,520.00</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Social Security:</span>
                            <span className="font-semibold">$589.00</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Medicare:</span>
                            <span className="font-semibold">$137.75</span>
                          </div>
                          <div className="border-t pt-2">
                            <div className="flex justify-between font-bold">
                              <span>Total Federal:</span>
                              <span>$2,246.75</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">State & Local Taxes</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span>State Income Tax:</span>
                            <span className="font-semibold">$475.00</span>
                          </div>
                          <div className="flex justify-between">
                            <span>State Disability:</span>
                            <span className="font-semibold">$85.50</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Local Taxes:</span>
                            <span className="font-semibold">$0.00</span>
                          </div>
                          <div className="border-t pt-2">
                            <div className="flex justify-between font-bold">
                              <span>Total State/Local:</span>
                              <span>$560.50</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>

                <TabsContent value="reports" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <Card className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardContent className="p-4 text-center">
                        <FileText className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                        <h4 className="font-semibold">Payroll Register</h4>
                        <p className="text-sm text-gray-600">Detailed payroll breakdown</p>
                        <Button size="sm" className="mt-2 bg-transparent" variant="outline">
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </CardContent>
                    </Card>

                    <Card className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardContent className="p-4 text-center">
                        <PieChart className="h-8 w-8 mx-auto mb-2 text-green-500" />
                        <h4 className="font-semibold">Tax Summary</h4>
                        <p className="text-sm text-gray-600">Tax withholdings report</p>
                        <Button size="sm" className="mt-2 bg-transparent" variant="outline">
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </CardContent>
                    </Card>

                    <Card className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardContent className="p-4 text-center">
                        <Calculator className="h-8 w-8 mx-auto mb-2 text-purple-500" />
                        <h4 className="font-semibold">Employer Costs</h4>
                        <p className="text-sm text-gray-600">Total employer expenses</p>
                        <Button size="sm" className="mt-2 bg-transparent" variant="outline">
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          ) : (
            <div className="text-center py-8">
              <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-600">No payroll data available</p>
              <Button onClick={processPayroll} className="mt-4">
                Process Current Payroll
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
