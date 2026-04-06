"""
Document Verification & Fraud Detection Engine - Phase 6

Handles:
- Resume authenticity verification
- Credential validation
- Background check integration
- Document integrity checking
- Fraud detection and red flags
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import re
import hashlib
import asyncio


class VerificationStatus(str, Enum):
    """Document verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    SUSPICIOUS = "suspicious"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"


class RiskLevel(str, Enum):
    """Risk level assessment"""
    LOW = "low"  # 0-20%
    MEDIUM = "medium"  # 21-50%
    HIGH = "high"  # 51-80%
    CRITICAL = "critical"  # 81-100%


class FraudIndicator(str, Enum):
    """Types of fraud indicators detected"""
    EDUCATION_MISMATCH = "education_mismatch"
    EXPERIENCE_GAP = "experience_gap"
    TIMELINE_INCONSISTENCY = "timeline_inconsistency"
    DUPLICATE_INFORMATION = "duplicate_information"
    UNVERIFIABLE_EMPLOYER = "unverifiable_employer"
    CREDENTIAL_FORGERY = "credential_forgery"
    INCONSISTENT_DATES = "inconsistent_dates"
    RED_FLAG_KEYWORDS = "red_flag_keywords"
    MISSING_VERIFICATION = "missing_verification"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


@dataclass
class DocumentMetadata:
    """Metadata about a document"""
    document_id: str
    document_type: str  # resume, degree, certificate, license
    file_name: str
    file_hash: str
    file_size_bytes: int
    upload_timestamp: datetime
    extracted_text: Optional[str] = None
    is_digital_original: bool = False
    has_digital_signature: bool = False


@dataclass
class CredentialVerification:
    """Verification result for a credential"""
    credential_type: str  # degree, certification, license
    institution_name: str
    credential_name: str
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_timestamp: Optional[datetime] = None
    verification_source: str = ""  # API, manual, database
    
    is_valid: bool = False
    is_expired: bool = False
    confidence_score: float = 0.0  # 0-1
    
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmploymentVerification:
    """Verification result for employment history"""
    company_name: str
    job_title: str
    start_date: datetime
    end_date: Optional[datetime] = None
    
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_timestamp: Optional[datetime] = None
    
    company_found: bool = False
    company_verified: bool = False
    employment_verified: bool = False
    confidence_score: float = 0.0  # 0-1
    
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FraudRiskAssessment:
    """Comprehensive fraud risk assessment"""
    candidate_id: str
    assessment_timestamp: datetime
    
    overall_risk_level: RiskLevel
    risk_score: float  # 0-100
    
    fraud_indicators: List[Tuple[FraudIndicator, float, str]] = field(default_factory=list)  # (indicator, severity 0-1, reason)
    
    red_flags: List[str] = field(default_factory=list)
    suspicious_patterns: List[str] = field(default_factory=list)
    
    verified_credentials: List[CredentialVerification] = field(default_factory=list)
    verified_employment: List[EmploymentVerification] = field(default_factory=list)
    
    recommendation: str = "review"  # proceed, review, reject
    requires_manual_review: bool = False
    review_reason: str = ""


@dataclass
class BackgroundCheckResult:
    """Background check result"""
    candidate_id: str
    check_timestamp: datetime
    check_status: VerificationStatus
    
    criminal_record_found: bool = False
    sanctions_found: bool = False
    credit_issues: bool = False
    
    details: Dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW


class DocumentVerifier:
    """
    Advanced document verification and fraud detection system.
    Validates credentials, detects inconsistencies, and identifies fraud.
    """
    
    def __init__(self):
        """Initialize the document verifier"""
        self.red_flag_keywords = self._initialize_red_flags()
        self.education_database = self._initialize_education_db()
        self.company_database = self._initialize_company_db()
    
    def _initialize_red_flags(self) -> Dict[str, List[str]]:
        """Initialize red flag keywords and patterns"""
        return {
            "common_fraud": [
                "willing to relocate immediately",
                "available for work immediately",
                "no background check required",
                "cash payment",
                "no references needed",
                "confidential position",
            ],
            "education_fraud": [
                "degree mill",
                "diploma mill",
                "unaccredited",
                "correspondence university",
                "purchased degree",
            ],
            "timeline_issues": [
                "overlapping dates",
                "impossible timeline",
                "gap not explained",
            ],
        }
    
    def _initialize_education_db(self) -> Dict[str, List[str]]:
        """Initialize database of known educational institutions"""
        # Simplified - would connect to real database
        return {
            "valid_institutions": [
                "harvard university",
                "mit",
                "stanford university",
                "university of california",
                "carnegie mellon university",
            ],
            "known_diploma_mills": [
                "online university diploma",
                "internet degree",
                "fake diploma",
            ],
        }
    
    def _initialize_company_db(self) -> Dict[str, List[str]]:
        """Initialize database of known companies"""
        return {
            "major_tech": [
                "google",
                "microsoft",
                "apple",
                "amazon",
                "facebook",
                "tesla",
            ],
            "startup_patterns": [
                "startup",
                "inc",
                "llc",
                "corp",
            ],
        }
    
    def verify_document(
        self,
        file_path: str,
        file_content: bytes,
        document_type: str
    ) -> DocumentMetadata:
        """
        Verify a document's integrity and metadata.
        
        Args:
            file_path: Path to document
            file_content: Document content
            document_type: Type of document
            
        Returns:
            DocumentMetadata with verification info
        """
        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        metadata = DocumentMetadata(
            document_id=file_hash[:16],
            document_type=document_type,
            file_name=file_path.split('/')[-1],
            file_hash=file_hash,
            file_size_bytes=len(file_content),
            upload_timestamp=datetime.now()
        )
        
        # Extract text (simplified)
        metadata.extracted_text = self._extract_text(file_content)
        
        return metadata
    
    def _extract_text(self, file_content: bytes) -> str:
        """Extract text from document"""
        # Simplified - would use PyPDF2 or similar for real PDFs
        try:
            return file_content.decode('utf-8', errors='ignore')[:1000]
        except:
            return ""
    
    def assess_fraud_risk(
        self,
        candidate_data: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> FraudRiskAssessment:
        """
        Assess overall fraud risk for a candidate.
        
        Args:
            candidate_data: Candidate information
            resume_data: Parsed resume data
            
        Returns:
            FraudRiskAssessment with indicators and recommendations
        """
        assessment = FraudRiskAssessment(
            candidate_id=candidate_data.get("id", "unknown"),
            assessment_timestamp=datetime.now(),
            overall_risk_level=RiskLevel.LOW,
            risk_score=0.0
        )
        
        # Check for fraud indicators
        indicators = self._detect_fraud_indicators(candidate_data, resume_data)
        assessment.fraud_indicators = indicators
        
        # Check for red flags
        red_flags = self._check_red_flags(resume_data)
        assessment.red_flags = red_flags
        
        # Detect suspicious patterns
        patterns = self._detect_suspicious_patterns(resume_data)
        assessment.suspicious_patterns = patterns
        
        # Calculate overall risk
        total_severity = sum(severity for _, severity, _ in indicators)
        assessment.risk_score = min(100, (total_severity / len(indicators) * 100) if indicators else 0)
        
        # Determine risk level
        if assessment.risk_score >= 80:
            assessment.overall_risk_level = RiskLevel.CRITICAL
            assessment.requires_manual_review = True
        elif assessment.risk_score >= 50:
            assessment.overall_risk_level = RiskLevel.HIGH
            assessment.requires_manual_review = True
        elif assessment.risk_score >= 20:
            assessment.overall_risk_level = RiskLevel.MEDIUM
        else:
            assessment.overall_risk_level = RiskLevel.LOW
        
        # Make recommendation
        assessment.recommendation = self._make_recommendation(assessment)
        
        return assessment
    
    def _detect_fraud_indicators(
        self,
        candidate_data: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> List[Tuple[FraudIndicator, float, str]]:
        """Detect specific fraud indicators"""
        indicators: List[Tuple[FraudIndicator, float, str]] = []
        
        # Check education consistency
        education_issue = self._check_education_consistency(resume_data)
        if education_issue:
            indicators.append((FraudIndicator.EDUCATION_MISMATCH, education_issue[1], education_issue[2]))
        
        # Check experience gaps
        experience_gaps = self._check_experience_gaps(resume_data)
        if experience_gaps:
            for gap_severity, gap_reason in experience_gaps:
                indicators.append((FraudIndicator.EXPERIENCE_GAP, gap_severity, gap_reason))
        
        # Check timeline consistency
        timeline_issues = self._check_timeline_consistency(resume_data)
        if timeline_issues:
            for issue_severity, issue_reason in timeline_issues:
                indicators.append((FraudIndicator.TIMELINE_INCONSISTENCY, issue_severity, issue_reason))
        
        # Check for duplicate information
        if self._has_duplicate_info(resume_data):
            indicators.append((FraudIndicator.DUPLICATE_INFORMATION, 0.4, "Duplicate information found"))
        
        # Check for unverifiable employers
        unverifiable = self._check_unverifiable_employers(resume_data)
        if unverifiable:
            for company, severity in unverifiable:
                indicators.append((FraudIndicator.UNVERIFIABLE_EMPLOYER, severity, f"Cannot verify {company}"))
        
        return indicators
    
    def _check_education_consistency(self, resume_data: Dict[str, Any]) -> Optional[Tuple[str, float, str]]:
        """Check education information consistency"""
        education = resume_data.get("education", {})
        
        if not education:
            return None
        
        degree = education.get("highest_degree", "").lower()
        field = education.get("field_of_study", "").lower()
        
        # Check against diploma mills
        for mill in self.education_database.get("known_diploma_mills", []):
            if mill in degree or mill in field:
                return (FraudIndicator.EDUCATION_MISMATCH, 0.9, f"Possible diploma mill: {degree}")
        
        # Check graduation date consistency
        grad_date = education.get("graduation_date")
        if grad_date:
            grad_datetime = self._parse_date(grad_date)
            if grad_datetime and grad_datetime > datetime.now():
                return (FraudIndicator.INCONSISTENT_DATES, 0.8, "Future graduation date")
        
        return None
    
    def _check_experience_gaps(self, resume_data: Dict[str, Any]) -> List[Tuple[float, str]]:
        """Check for unexplained experience gaps"""
        gaps = []
        positions = resume_data.get("experience", {}).get("positions", [])
        
        if len(positions) < 2:
            return gaps
        
        # Sort positions by date
        sorted_positions = self._sort_positions_by_date(positions)
        
        for i in range(len(sorted_positions) - 1):
            current = sorted_positions[i]
            next_pos = sorted_positions[i + 1]
            
            current_end = self._parse_date(current.get("end_date"))
            next_start = self._parse_date(next_pos.get("start_date"))
            
            if current_end and next_start:
                gap_days = (next_start - current_end).days
                
                # Flag gaps longer than 3 months
                if gap_days > 90:
                    severity = min(0.8, gap_days / 365)  # Max 0.8
                    gaps.append((severity, f"Gap of {gap_days} days between positions"))
        
        return gaps
    
    def _check_timeline_consistency(self, resume_data: Dict[str, Any]) -> List[Tuple[float, str]]:
        """Check timeline consistency"""
        issues = []
        positions = resume_data.get("experience", {}).get("positions", [])
        
        for pos in positions:
            start_date = self._parse_date(pos.get("start_date"))
            end_date = self._parse_date(pos.get("end_date"))
            
            if start_date and end_date and start_date > end_date:
                issues.append((0.9, "Start date after end date"))
            
            if start_date and start_date > datetime.now():
                issues.append((0.8, "Future start date"))
        
        return issues
    
    def _has_duplicate_info(self, resume_data: Dict[str, Any]) -> bool:
        """Check for duplicate information"""
        positions = resume_data.get("experience", {}).get("positions", [])
        position_titles = [p.get("title", "").lower() for p in positions]
        
        return len(position_titles) != len(set(position_titles))
    
    def _check_unverifiable_employers(self, resume_data: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Check for unverifiable employers"""
        unverifiable = []
        positions = resume_data.get("experience", {}).get("positions", [])
        
        for pos in positions:
            company = pos.get("company", "").lower()
            
            # Simple check - in production would verify against business database
            if len(company) < 3 or company in ["company", "startup", "unknown"]:
                unverifiable.append((company, 0.5))
        
        return unverifiable
    
    def _check_red_flags(self, resume_data: Dict[str, Any]) -> List[str]:
        """Check for red flag keywords and phrases"""
        red_flags = []
        resume_text = str(resume_data).lower()
        
        for category, keywords in self.red_flag_keywords.items():
            for keyword in keywords:
                if keyword.lower() in resume_text:
                    red_flags.append(f"Red flag: {keyword}")
        
        return red_flags[:5]
    
    def _detect_suspicious_patterns(self, resume_data: Dict[str, Any]) -> List[str]:
        """Detect suspicious patterns in resume"""
        patterns = []
        
        # Check for too many jobs in short time
        positions = resume_data.get("experience", {}).get("positions", [])
        if len(positions) > 5:
            duration_per_job = 0
            if positions:
                earliest = min(self._parse_date(p.get("start_date")) for p in positions if self._parse_date(p.get("start_date")))
                latest = max(self._parse_date(p.get("end_date")) or datetime.now() for p in positions if self._parse_date(p.get("end_date")))
                if earliest and latest:
                    duration_per_job = (latest - earliest).days / len(positions)
            
            if duration_per_job < 365:  # Less than 1 year per job
                patterns.append("Frequent job changes - less than 1 year per position")
        
        # Check for unclear job titles
        for pos in positions:
            title = pos.get("title", "").lower()
            if len(title) > 50 or "and" in title or "/" in title:
                patterns.append(f"Unclear job title: {title}")
        
        return patterns[:5]
    
    def _make_recommendation(self, assessment: FraudRiskAssessment) -> str:
        """Make recommendation based on assessment"""
        if assessment.risk_score >= 70:
            return "reject"
        elif assessment.risk_score >= 40:
            assessment.requires_manual_review = True
            return "review"
        else:
            return "proceed"
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse date string to datetime"""
        if isinstance(date_str, datetime):
            return date_str
        
        if not date_str or not isinstance(date_str, str):
            return None
        
        # Try common formats
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%B %Y", "%b %Y", "%Y"]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def _sort_positions_by_date(self, positions: List[Dict]) -> List[Dict]:
        """Sort positions by start date"""
        def get_start_date(pos):
            date = self._parse_date(pos.get("start_date"))
            return date if date else datetime.min
        
        return sorted(positions, key=get_start_date)
    
    async def verify_credential(
        self,
        credential_type: str,
        institution: str,
        credential_name: str,
        issue_date: Optional[str] = None,
        credential_id: Optional[str] = None
    ) -> CredentialVerification:
        """
        Verify a credential (degree, certification, license).
        
        Args:
            credential_type: Type of credential
            institution: Issuing institution
            credential_name: Name of credential
            issue_date: Issue date
            credential_id: Credential ID for verification
            
        Returns:
            CredentialVerification result
        """
        verification = CredentialVerification(
            credential_type=credential_type,
            institution_name=institution,
            credential_name=credential_name,
            verification_timestamp=datetime.now()
        )
        
        if issue_date:
            verification.issue_date = self._parse_date(issue_date)
        
        # Simulate verification (in production would call actual verification APIs)
        verification.status = VerificationStatus.PENDING
        
        # Check against known institutions
        if institution.lower() in self.education_database.get("valid_institutions", []):
            verification.company_found = True
            verification.confidence_score = 0.85
            verification.status = VerificationStatus.VERIFIED
            verification.is_valid = True
        else:
            verification.company_found = False
            verification.confidence_score = 0.3
            verification.status = VerificationStatus.REQUIRES_MANUAL_REVIEW
        
        # Check expiration
        if verification.expiry_date and verification.expiry_date < datetime.now():
            verification.is_expired = True
            verification.is_valid = False
        
        return verification
    
    async def verify_employment(
        self,
        company_name: str,
        job_title: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> EmploymentVerification:
        """
        Verify employment history.
        
        Args:
            company_name: Company name
            job_title: Job title
            start_date: Start date
            end_date: End date
            
        Returns:
            EmploymentVerification result
        """
        verification = EmploymentVerification(
            company_name=company_name,
            job_title=job_title,
            start_date=self._parse_date(start_date) or datetime.now(),
            verification_timestamp=datetime.now()
        )
        
        if end_date:
            verification.end_date = self._parse_date(end_date)
        
        # Simulate verification (in production would call HR verification services)
        verification.status = VerificationStatus.PENDING
        
        # Check against known companies
        company_lower = company_name.lower()
        if any(major in company_lower for major in self.company_database.get("major_tech", [])):
            verification.company_found = True
            verification.company_verified = True
            verification.confidence_score = 0.9
            verification.status = VerificationStatus.VERIFIED
            verification.employment_verified = True
        else:
            verification.company_found = False
            verification.confidence_score = 0.4
            verification.status = VerificationStatus.REQUIRES_MANUAL_REVIEW
        
        return verification
    
    async def conduct_background_check(
        self,
        candidate_id: str,
        candidate_name: str,
        ssn: Optional[str] = None
    ) -> BackgroundCheckResult:
        """
        Conduct background check.
        
        Args:
            candidate_id: Candidate ID
            candidate_name: Candidate name
            ssn: Social Security Number (if available)
            
        Returns:
            BackgroundCheckResult
        """
        result = BackgroundCheckResult(
            candidate_id=candidate_id,
            check_timestamp=datetime.now(),
            check_status=VerificationStatus.PENDING
        )
        
        # Simulate background check (in production would integrate with background check services)
        result.criminal_record_found = False
        result.sanctions_found = False
        result.credit_issues = False
        result.risk_level = RiskLevel.LOW
        result.check_status = VerificationStatus.VERIFIED
        
        return result
