"""
Onboarding Agent - Phase 7 Implementation

Handles:
- New hire onboarding workflows
- Account creation and setup
- Document collection
- Training assignment
- Integration with company systems
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class OnboardingStatus(str, Enum):
    """Onboarding status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"


class TaskStatus(str, Enum):
    """Individual task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class TaskCategory(str, Enum):
    """Task categories"""
    DOCUMENTATION = "documentation"
    ACCOUNT_SETUP = "account_setup"
    SYSTEM_ACCESS = "system_access"
    TRAINING = "training"
    BENEFITS = "benefits"
    COMPLIANCE = "compliance"
    ORIENTATION = "orientation"


@dataclass
class OnboardingTask:
    """Individual onboarding task"""
    task_id: str
    task_name: str
    description: str
    category: TaskCategory
    status: TaskStatus = TaskStatus.PENDING
    
    assigned_to: str = ""  # HR, Manager, Employee, System
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    required: bool = True
    dependencies: List[str] = field(default_factory=list)
    
    notes: str = ""
    completion_proof: Optional[str] = None


@dataclass
class OnboardingChecklist:
    """Complete onboarding checklist"""
    checklist_id: str
    hire_id: str
    hire_name: str
    job_title: str
    department: str
    
    start_date: datetime
    expected_completion: datetime
    
    status: OnboardingStatus = OnboardingStatus.NOT_STARTED
    progress_percentage: float = 0.0
    
    tasks: List[OnboardingTask] = field(default_factory=list)
    
    assigned_buddy: Optional[str] = None
    assigned_manager: str = ""
    assigned_hr: str = ""
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class EmployeeAccount:
    """New employee account setup"""
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    
    username: Optional[str] = None
    password_reset_token: Optional[str] = None
    
    # System accounts
    email_account_created: bool = False
    vpn_access_granted: bool = False
    network_access_granted: bool = False
    
    # Equipment
    laptop_assigned: bool = False
    laptop_serial: Optional[str] = None
    phone_assigned: bool = False
    phone_number: Optional[str] = None
    
    # Accounts
    github_username: Optional[str] = None
    slack_username: Optional[str] = None
    
    status: str = "pending_setup"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OnboardingMetrics:
    """Onboarding performance metrics"""
    total_hires_onboarded: int
    average_onboarding_days: float
    task_completion_rate: float  # 0-1
    early_departures: int
    satisfaction_score: float  # 0-10
    
    top_bottlenecks: List[str] = field(default_factory=list)
    time_to_productivity: float = 0.0  # days


class OnboardingAgent:
    """
    AI-powered onboarding coordinator.
    Manages workflows, tracks tasks, and ensures smooth employee integration.
    """
    
    def __init__(self):
        """Initialize onboarding agent"""
        self.task_templates = self._initialize_task_templates()
    
    def _initialize_task_templates(self) -> Dict[str, List[OnboardingTask]]:
        """Initialize standard onboarding task templates"""
        return {
            "standard": [
                # Documentation
                OnboardingTask(
                    task_id="doc_001",
                    task_name="Complete I-9 Verification",
                    description="Verify identity and work authorization documents",
                    category=TaskCategory.DOCUMENTATION,
                    assigned_to="HR",
                    required=True,
                    due_date=datetime.now() + timedelta(days=3)
                ),
                OnboardingTask(
                    task_id="doc_002",
                    task_name="Sign Employee Handbook",
                    description="Review and sign employee handbook acknowledgment",
                    category=TaskCategory.DOCUMENTATION,
                    assigned_to="Employee",
                    required=True,
                    due_date=datetime.now() + timedelta(days=2)
                ),
                OnboardingTask(
                    task_id="doc_003",
                    task_name="Complete Tax Forms (W-4/State)",
                    description="Complete federal and state tax withholding forms",
                    category=TaskCategory.DOCUMENTATION,
                    assigned_to="HR",
                    required=True,
                    due_date=datetime.now() + timedelta(days=1)
                ),
                
                # Account Setup
                OnboardingTask(
                    task_id="acct_001",
                    task_name="Create Email Account",
                    description="Set up corporate email account",
                    category=TaskCategory.ACCOUNT_SETUP,
                    assigned_to="System",
                    required=True,
                    due_date=datetime.now() + timedelta(days=1)
                ),
                OnboardingTask(
                    task_id="acct_002",
                    task_name="Setup VPN Access",
                    description="Configure VPN client and credentials",
                    category=TaskCategory.ACCOUNT_SETUP,
                    assigned_to="System",
                    required=True,
                    due_date=datetime.now() + timedelta(days=2)
                ),
                OnboardingTask(
                    task_id="acct_003",
                    task_name="Create Slack Account",
                    description="Add employee to Slack workspace",
                    category=TaskCategory.ACCOUNT_SETUP,
                    assigned_to="System",
                    required=True,
                    due_date=datetime.now() + timedelta(days=1)
                ),
                
                # System Access
                OnboardingTask(
                    task_id="sys_001",
                    task_name="Grant System Permissions",
                    description="Configure role-based access control",
                    category=TaskCategory.SYSTEM_ACCESS,
                    assigned_to="System",
                    required=True,
                    dependencies=["acct_001"],
                    due_date=datetime.now() + timedelta(days=2)
                ),
                OnboardingTask(
                    task_id="sys_002",
                    task_name="Assign Work Equipment",
                    description="Assign laptop, monitor, peripherals",
                    category=TaskCategory.SYSTEM_ACCESS,
                    assigned_to="Manager",
                    required=True,
                    due_date=datetime.now() + timedelta(days=1)
                ),
                
                # Training
                OnboardingTask(
                    task_id="train_001",
                    task_name="Company Orientation",
                    description="1-hour orientation on company culture and values",
                    category=TaskCategory.TRAINING,
                    assigned_to="HR",
                    required=True,
                    due_date=datetime.now() + timedelta(days=1)
                ),
                OnboardingTask(
                    task_id="train_002",
                    task_name="Department Orientation",
                    description="Meet team and learn about department",
                    category=TaskCategory.TRAINING,
                    assigned_to="Manager",
                    required=True,
                    due_date=datetime.now() + timedelta(days=2)
                ),
                OnboardingTask(
                    task_id="train_003",
                    task_name="Role-Specific Training",
                    description="Complete role-specific training programs",
                    category=TaskCategory.TRAINING,
                    assigned_to="Manager",
                    required=True,
                    due_date=datetime.now() + timedelta(days=14)
                ),
                
                # Benefits
                OnboardingTask(
                    task_id="ben_001",
                    task_name="Enroll in Health Insurance",
                    description="Choose health, dental, vision plans",
                    category=TaskCategory.BENEFITS,
                    assigned_to="HR",
                    required=True,
                    due_date=datetime.now() + timedelta(days=7)
                ),
                OnboardingTask(
                    task_id="ben_002",
                    task_name="Setup 401(k)",
                    description="Enroll in 401(k) retirement plan",
                    category=TaskCategory.BENEFITS,
                    assigned_to="HR",
                    required=False,
                    due_date=datetime.now() + timedelta(days=30)
                ),
                
                # Compliance
                OnboardingTask(
                    task_id="comp_001",
                    task_name="Security Training",
                    description="Complete information security training",
                    category=TaskCategory.COMPLIANCE,
                    assigned_to="System",
                    required=True,
                    due_date=datetime.now() + timedelta(days=7)
                ),
                OnboardingTask(
                    task_id="comp_002",
                    task_name="Sign NDA",
                    description="Sign non-disclosure agreement",
                    category=TaskCategory.COMPLIANCE,
                    assigned_to="Legal",
                    required=True,
                    due_date=datetime.now() + timedelta(days=1)
                ),
            ],
            "technical": [
                # Include standard tasks plus technical-specific ones
                OnboardingTask(
                    task_id="tech_001",
                    task_name="GitHub Repository Access",
                    description="Grant GitHub repository access",
                    category=TaskCategory.SYSTEM_ACCESS,
                    assigned_to="System",
                    required=True,
                    due_date=datetime.now() + timedelta(days=1)
                ),
                OnboardingTask(
                    task_id="tech_002",
                    task_name="Development Environment Setup",
                    description="Configure development environment",
                    category=TaskCategory.TRAINING,
                    assigned_to="Manager",
                    required=True,
                    due_date=datetime.now() + timedelta(days=2)
                ),
                OnboardingTask(
                    task_id="tech_003",
                    task_name="Code Review Guidelines",
                    description="Learn team code review process",
                    category=TaskCategory.TRAINING,
                    assigned_to="Manager",
                    required=True,
                    due_date=datetime.now() + timedelta(days=3)
                ),
            ]
        }
    
    def create_onboarding_checklist(
        self,
        hire_id: str,
        hire_name: str,
        job_title: str,
        department: str,
        start_date: datetime,
        role_type: str = "standard"
    ) -> OnboardingChecklist:
        """
        Create onboarding checklist for a new hire.
        
        Args:
            hire_id: Unique identifier for hire
            hire_name: New hire name
            job_title: Job title
            department: Department name
            start_date: First day of work
            role_type: Type of role (standard, technical, etc.)
            
        Returns:
            OnboardingChecklist ready to use
        """
        import uuid
        
        checklist = OnboardingChecklist(
            checklist_id=str(uuid.uuid4()),
            hire_id=hire_id,
            hire_name=hire_name,
            job_title=job_title,
            department=department,
            start_date=start_date,
            expected_completion=start_date + timedelta(days=30)
        )
        
        # Get task templates
        base_tasks = self.task_templates.get("standard", [])
        role_specific = self.task_templates.get(role_type, [])
        
        # Combine tasks (avoid duplicates)
        task_ids = set()
        all_tasks = []
        
        for task in base_tasks + role_specific:
            if task.task_id not in task_ids:
                all_tasks.append(task)
                task_ids.add(task.task_id)
        
        checklist.tasks = all_tasks
        return checklist
    
    def start_onboarding(self, checklist: OnboardingChecklist) -> OnboardingChecklist:
        """Start onboarding process"""
        checklist.status = OnboardingStatus.IN_PROGRESS
        checklist.updated_at = datetime.now()
        
        # Mark appropriate tasks as in-progress
        for task in checklist.tasks:
            if not task.dependencies:
                task.status = TaskStatus.IN_PROGRESS
        
        return checklist
    
    def complete_task(
        self,
        checklist: OnboardingChecklist,
        task_id: str,
        completion_proof: Optional[str] = None
    ) -> tuple[OnboardingChecklist, Optional[OnboardingTask]]:
        """
        Mark a task as completed.
        
        Args:
            checklist: Onboarding checklist
            task_id: Task to complete
            completion_proof: Proof of completion
            
        Returns:
            Updated checklist and completed task
        """
        completed_task = None
        
        for task in checklist.tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_date = datetime.now()
                task.completion_proof = completion_proof
                completed_task = task
                break
        
        if completed_task:
            # Unblock dependent tasks
            for task in checklist.tasks:
                if completed_task.task_id in task.dependencies:
                    if task.status == TaskStatus.BLOCKED:
                        task.status = TaskStatus.PENDING
        
        # Update progress
        self._update_progress(checklist)
        
        # Check if onboarding is complete
        if self._is_onboarding_complete(checklist):
            checklist.status = OnboardingStatus.COMPLETED
        
        checklist.updated_at = datetime.now()
        return checklist, completed_task
    
    def _update_progress(self, checklist: OnboardingChecklist) -> None:
        """Calculate and update onboarding progress"""
        if not checklist.tasks:
            checklist.progress_percentage = 0.0
            return
        
        required_tasks = [t for t in checklist.tasks if t.required]
        completed = sum(1 for t in required_tasks if t.status == TaskStatus.COMPLETED)
        
        if required_tasks:
            checklist.progress_percentage = (completed / len(required_tasks)) * 100
        else:
            checklist.progress_percentage = 0.0
    
    def _is_onboarding_complete(self, checklist: OnboardingChecklist) -> bool:
        """Check if all required tasks are completed"""
        required_tasks = [t for t in checklist.tasks if t.required]
        
        return all(
            t.status == TaskStatus.COMPLETED
            for t in required_tasks
        )
    
    def create_employee_account(
        self,
        hire_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str
    ) -> EmployeeAccount:
        """
        Create employee account.
        
        Args:
            hire_id: Hire identifier
            first_name: First name
            last_name: Last name
            email: Corporate email
            phone: Phone number
            
        Returns:
            EmployeeAccount
        """
        import uuid
        import random
        import string
        
        # Generate employee ID
        employee_id = f"EMP{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        # Generate temporary password reset token
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        account = EmployeeAccount(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_reset_token=reset_token,
            status="pending_setup"
        )
        
        return account
    
    def setup_account_systems(self, account: EmployeeAccount) -> EmployeeAccount:
        """
        Setup various account systems.
        
        Args:
            account: EmployeeAccount to setup
            
        Returns:
            Updated account with system setups
        """
        # Simulate system setups
        account.email_account_created = True
        account.vpn_access_granted = True
        account.network_access_granted = True
        
        # Generate usernames
        account.username = f"{account.first_name.lower()}.{account.last_name.lower()}"
        account.github_username = account.username
        account.slack_username = account.username
        
        account.status = "systems_configured"
        
        return account
    
    def assign_equipment(
        self,
        account: EmployeeAccount,
        laptop_serial: str,
        phone_number: str
    ) -> EmployeeAccount:
        """
        Assign equipment to employee.
        
        Args:
            account: EmployeeAccount
            laptop_serial: Laptop serial number
            phone_number: Corporate phone number
            
        Returns:
            Updated account
        """
        account.laptop_assigned = True
        account.laptop_serial = laptop_serial
        account.phone_assigned = True
        account.phone_number = phone_number
        
        account.status = "equipment_assigned"
        
        return account
    
    def get_onboarding_metrics(
        self,
        checklists: List[OnboardingChecklist]
    ) -> OnboardingMetrics:
        """
        Calculate onboarding metrics.
        
        Args:
            checklists: List of completed onboarding checklists
            
        Returns:
            OnboardingMetrics
        """
        if not checklists:
            return OnboardingMetrics(
                total_hires_onboarded=0,
                average_onboarding_days=0.0,
                task_completion_rate=0.0,
                early_departures=0,
                satisfaction_score=0.0
            )
        
        # Calculate metrics
        total_hires = len(checklists)
        
        durations = []
        for checklist in checklists:
            if checklist.expected_completion and checklist.created_at:
                duration = (checklist.expected_completion - checklist.created_at).days
                durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Task completion rate
        total_tasks = 0
        completed_tasks = 0
        for checklist in checklists:
            for task in checklist.tasks:
                if task.required:
                    total_tasks += 1
                    if task.status == TaskStatus.COMPLETED:
                        completed_tasks += 1
        
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        # Identify bottlenecks
        task_completion_rates = {}
        for checklist in checklists:
            for task in checklist.tasks:
                if task.task_id not in task_completion_rates:
                    task_completion_rates[task.task_id] = {"completed": 0, "total": 0}
                task_completion_rates[task.task_id]["total"] += 1
                if task.status == TaskStatus.COMPLETED:
                    task_completion_rates[task.task_id]["completed"] += 1
        
        bottlenecks = [
            task_id for task_id, counts in task_completion_rates.items()
            if counts["total"] > 0 and counts["completed"] / counts["total"] < 0.5
        ]
        
        return OnboardingMetrics(
            total_hires_onboarded=total_hires,
            average_onboarding_days=avg_duration,
            task_completion_rate=completion_rate,
            early_departures=0,  # Would be tracked separately
            satisfaction_score=0.0,  # Would come from surveys
            top_bottlenecks=bottlenecks[:5]
        )
