import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { pay_period_start, pay_period_end, employee_ids } = await request.json()

    // Mock payroll processing
    const payrollRun = {
      id: `payroll-${Date.now()}`,
      pay_period_start,
      pay_period_end,
      processed_at: new Date().toISOString(),
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
          tax_breakdown: {
            federal_income_tax: 800.0,
            state_income_tax: 250.0,
            social_security_tax: 310.0,
            medicare_tax: 72.5,
            total_taxes: 1432.5,
          },
          deduction_breakdown: {
            health_insurance: 150.0,
            retirement_401k: 200.0,
            dental_insurance: 25.0,
            total_deductions: 375.0,
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
          tax_breakdown: {
            federal_income_tax: 720.0,
            state_income_tax: 225.0,
            social_security_tax: 279.0,
            medicare_tax: 65.25,
            total_taxes: 1289.25,
          },
          deduction_breakdown: {
            health_insurance: 150.0,
            retirement_401k: 180.0,
            dental_insurance: 25.0,
            total_deductions: 355.0,
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

    return NextResponse.json(payrollRun)
  } catch (error) {
    return NextResponse.json({ error: "Failed to process payroll" }, { status: 500 })
  }
}
