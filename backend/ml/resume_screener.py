"""
Resume Screening Engine - Phase 4 Implementation

Handles comprehensive resume analysis, candidate ranking, and automated screening.
Uses LLM-based and NLP-based techniques for intelligent candidate evaluation.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime
import asyncio

# Will be imported from core modules
# from backend.core.llm_client import LLMClient
# from backend.ml.resume_parser import ResumeParser


class MatchLevel(str, Enum):
    """Candidate match quality levels"""
    EXCELLENT = "excellent"  # 90-100%
    STRONG = "strong"  # 75-89%
    GOOD = "good"  # 60-74%
    MODERATE = "moderate"  # 45-59%
    WEAK = "weak"  # 30-44%
    POOR = "poor"  # 0-29%


class ScreeningCriteria(str, Enum):
    """Key screening dimensions"""
    SKILLS_MATCH = "skills_match"
    EXPERIENCE_LEVEL = "experience_level"
    EDUCATION_MATCH = "education_match"
    CULTURAL_FIT = "cultural_fit"
    AVAILABILITY = "availability"
    SALARY_EXPECTATIONS = "salary_expectations"
    LOCATION_FIT = "location_fit"
    GROWTH_POTENTIAL = "growth_potential"


@dataclass
class SkillMatch:
    """Represents a skill match between candidate and job"""
    skill_name: str
    candidate_level: str  # junior, mid, senior, expert
    required_level: str
    match_score: float  # 0-1
    confidence: float  # 0-1
    years_of_experience: Optional[float] = None


@dataclass
class ExperienceMatch:
    """Represents experience requirement matching"""
    required_years: float
    actual_years: float
    match_score: float  # 0-1
    roles_aligned: List[str] = field(default_factory=list)
    industry_match: float = 0.5


@dataclass
class EducationMatch:
    """Represents education requirement matching"""
    required_degree: str
    candidate_degree: str
    required_field: Optional[str]
    candidate_field: Optional[str]
    match_score: float  # 0-1
    certifications: List[str] = field(default_factory=list)


@dataclass
class CandidateScreening:
    """Complete screening results for a candidate"""
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    
    # Core scoring
    overall_score: float  # 0-100
    match_level: MatchLevel
    recommendation: str  # "Hire", "Review", "Reject", "Waitlist"
    
    # Detailed matches
    skills_match: List[SkillMatch] = field(default_factory=list)
    experience_match: Optional[ExperienceMatch] = None
    education_match: Optional[EducationMatch] = None
    
    # Scoring breakdown
    criteria_scores: Dict[ScreeningCriteria, float] = field(default_factory=dict)
    
    # Analysis
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    
    # Metadata
    screening_timestamp: datetime = field(default_factory=datetime.now)
    screened_by: str = "ai_agent"
    confidence: float = 0.85
    screening_duration_ms: int = 0


@dataclass
class RankingResult:
    """Ranking results for multiple candidates"""
    job_id: str
    job_title: str
    total_candidates: int
    ranked_candidates: List[Tuple[str, str, float, MatchLevel]] = field(default_factory=list)
    top_candidates: List[CandidateScreening] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    ranking_timestamp: datetime = field(default_factory=datetime.now)


class ResumeScreener:
    """
    Advanced resume screening engine with LLM and NLP capabilities.
    Performs intelligent candidate evaluation against job requirements.
    """
    
    def __init__(self, llm_client=None, resume_parser=None):
        """
        Initialize the resume screener.
        
        Args:
            llm_client: LLM client for intelligent analysis
            resume_parser: Resume parser for extraction
        """
        self.llm_client = llm_client
        self.resume_parser = resume_parser
        self.screening_prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, str]:
        """Initialize screening prompts for LLM"""
        return {
            "skills_analysis": """Analyze the candidate's skills against the job requirements.
Provide a detailed match analysis with:
1. Exact skill matches
2. Transferable skills
3. Skill gaps
4. Learning potential for missing skills
Score each skill match from 0-1.""",
            
            "experience_evaluation": """Evaluate the candidate's experience level.
Consider:
1. Years of relevant experience
2. Role progression and growth
3. Industry experience
4. Project complexity and scale
5. Leadership experience
Provide overall experience match score 0-1.""",
            
            "cultural_fit": """Assess cultural fit based on resume indicators.
Look for:
1. Values alignment
2. Team collaboration indicators
3. Growth mindset signals
4. Communication style
5. Leadership style indicators
Provide cultural fit score 0-1.""",
            
            "growth_potential": """Evaluate candidate's growth potential.
Consider:
1. Learning trajectory
2. Skill diversity
3. Challenge-seeking behavior
4. Mentorship received
5. Innovation indicators
Provide growth potential score 0-1."""
        }
    
    def screen_candidate(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        detailed: bool = True
    ) -> CandidateScreening:
        """
        Screen a single candidate against job requirements.
        
        Args:
            candidate_data: Parsed candidate resume data
            job_requirements: Job requirements specification
            detailed: Whether to include detailed analysis
            
        Returns:
            CandidateScreening with comprehensive results
        """
        screening = CandidateScreening(
            candidate_id=candidate_data.get("id", "unknown"),
            candidate_name=candidate_data.get("name", "Unknown"),
            job_id=job_requirements.get("id", "unknown"),
            job_title=job_requirements.get("title", "Unknown Position")
        )
        
        # Perform screening analysis
        skills_scores = self._score_skills_match(candidate_data, job_requirements)
        experience_match = self._score_experience_match(candidate_data, job_requirements)
        education_match = self._score_education_match(candidate_data, job_requirements)
        
        # Calculate criterion scores
        criteria_scores = {
            ScreeningCriteria.SKILLS_MATCH: skills_scores["overall"],
            ScreeningCriteria.EXPERIENCE_LEVEL: experience_match.match_score,
            ScreeningCriteria.EDUCATION_MATCH: education_match.match_score,
            ScreeningCriteria.CULTURAL_FIT: self._score_cultural_fit(candidate_data),
            ScreeningCriteria.AVAILABILITY: self._score_availability(candidate_data),
            ScreeningCriteria.SALARY_EXPECTATIONS: self._score_salary_fit(candidate_data, job_requirements),
            ScreeningCriteria.LOCATION_FIT: self._score_location_fit(candidate_data, job_requirements),
            ScreeningCriteria.GROWTH_POTENTIAL: self._score_growth_potential(candidate_data),
        }
        
        # Weighted calculation
        weights = {
            ScreeningCriteria.SKILLS_MATCH: 0.35,
            ScreeningCriteria.EXPERIENCE_LEVEL: 0.25,
            ScreeningCriteria.EDUCATION_MATCH: 0.15,
            ScreeningCriteria.CULTURAL_FIT: 0.10,
            ScreeningCriteria.AVAILABILITY: 0.05,
            ScreeningCriteria.SALARY_EXPECTATIONS: 0.05,
            ScreeningCriteria.LOCATION_FIT: 0.03,
            ScreeningCriteria.GROWTH_POTENTIAL: 0.02,
        }
        
        overall_score = sum(
            criteria_scores.get(criterion, 0) * weights.get(criterion, 0)
            for criterion in ScreeningCriteria
        ) * 100
        
        screening.overall_score = round(overall_score, 2)
        screening.criteria_scores = {k: round(v * 100, 2) for k, v in criteria_scores.items()}
        screening.experience_match = experience_match
        screening.education_match = education_match
        screening.skills_match = skills_scores["matches"]
        
        # Determine recommendation
        screening.match_level = self._get_match_level(overall_score)
        screening.recommendation = self._get_recommendation(overall_score, job_requirements)
        
        # Detailed analysis
        if detailed:
            screening.strengths = self._extract_strengths(candidate_data, job_requirements, criteria_scores)
            screening.gaps = self._extract_gaps(candidate_data, job_requirements, criteria_scores)
            screening.concerns = self._extract_concerns(candidate_data, criteria_scores)
            screening.opportunities = self._extract_opportunities(candidate_data, job_requirements)
        
        screening.confidence = min(0.95, 0.70 + (overall_score / 100) * 0.25)
        
        return screening
    
    def _score_skills_match(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Score skills matching between candidate and job"""
        required_skills = job_requirements.get("skills", [])
        candidate_skills = candidate_data.get("skills", [])
        
        matches: List[SkillMatch] = []
        total_score = 0
        
        for required_skill in required_skills:
            skill_name = required_skill.get("name", "")
            required_level = required_skill.get("level", "mid")
            required_years = required_skill.get("years", 3)
            weight = required_skill.get("weight", 1.0)
            
            # Find matching candidate skill
            match = None
            for cand_skill in candidate_skills:
                if self._skills_match(skill_name, cand_skill.get("name", "")):
                    match = cand_skill
                    break
            
            if match:
                score = self._calculate_skill_score(
                    match.get("level", "junior"),
                    required_level,
                    match.get("years", 0),
                    required_years
                )
                matches.append(SkillMatch(
                    skill_name=skill_name,
                    candidate_level=match.get("level", "unknown"),
                    required_level=required_level,
                    match_score=score,
                    confidence=0.9,
                    years_of_experience=match.get("years", 0)
                ))
                total_score += score * weight
            else:
                matches.append(SkillMatch(
                    skill_name=skill_name,
                    candidate_level="missing",
                    required_level=required_level,
                    match_score=0.0,
                    confidence=1.0
                ))
                total_score += 0.0 * weight
        
        overall_score = total_score / len(required_skills) if required_skills else 0
        
        return {
            "overall": overall_score,
            "matches": matches,
            "exact_matches": len([m for m in matches if m.match_score > 0.8]),
            "partial_matches": len([m for m in matches if 0.3 < m.match_score <= 0.8]),
            "missing_skills": len([m for m in matches if m.match_score <= 0.3])
        }
    
    def _score_experience_match(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> ExperienceMatch:
        """Score experience level match"""
        required_years = job_requirements.get("experience_years", 3)
        candidate_experience = candidate_data.get("experience", {})
        total_years = candidate_experience.get("total_years", 0)
        
        # Experience scoring
        if total_years >= required_years * 1.5:
            score = 1.0  # Over-qualified is acceptable
        elif total_years >= required_years:
            score = 1.0  # Perfect match
        elif total_years >= required_years * 0.75:
            score = 0.8  # Close match
        elif total_years >= required_years * 0.5:
            score = 0.6  # Below requirements
        else:
            score = max(0, total_years / required_years)  # Significant gap
        
        # Extract relevant roles
        roles = [exp.get("title", "") for exp in candidate_experience.get("positions", [])]
        
        return ExperienceMatch(
            required_years=required_years,
            actual_years=total_years,
            match_score=score,
            roles_aligned=roles[:3],  # Top 3 roles
            industry_match=self._score_industry_match(
                candidate_experience.get("industries", []),
                job_requirements.get("industries", [])
            )
        )
    
    def _score_education_match(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> EducationMatch:
        """Score education match"""
        required_degree = job_requirements.get("education_level", "bachelor")
        required_field = job_requirements.get("education_field")
        
        education = candidate_data.get("education", {})
        candidate_degree = education.get("highest_degree", "unknown")
        candidate_field = education.get("field_of_study")
        
        # Degree matching
        degree_levels = {"high_school": 1, "bachelor": 2, "master": 3, "phd": 4}
        req_level = degree_levels.get(required_degree, 2)
        cand_level = degree_levels.get(candidate_degree, 0)
        
        degree_score = min(1.0, cand_level / req_level) if req_level > 0 else 1.0
        
        # Field matching
        field_score = 1.0
        if required_field and candidate_field:
            if required_field.lower() == candidate_field.lower():
                field_score = 1.0
            elif self._field_similarity(required_field, candidate_field) > 0.6:
                field_score = 0.8
            else:
                field_score = 0.5
        elif required_field and not candidate_field:
            field_score = 0.3
        
        overall_score = (degree_score * 0.7) + (field_score * 0.3)
        
        return EducationMatch(
            required_degree=required_degree,
            candidate_degree=candidate_degree,
            required_field=required_field,
            candidate_field=candidate_field,
            match_score=overall_score,
            certifications=education.get("certifications", [])
        )
    
    def _score_cultural_fit(self, candidate_data: Dict[str, Any]) -> float:
        """Score cultural fit based on career indicators"""
        indicators = 0
        total_indicators = 0
        
        # Check for leadership roles
        positions = candidate_data.get("experience", {}).get("positions", [])
        for pos in positions:
            total_indicators += 1
            if any(word in pos.get("title", "").lower() for word in ["lead", "manager", "director", "head"]):
                indicators += 0.8
            elif any(word in pos.get("title", "").lower() for word in ["senior", "principal", "staff"]):
                indicators += 0.6
            else:
                indicators += 0.4
        
        # Check for diverse responsibilities
        total_indicators += 1
        skill_diversity = len(candidate_data.get("skills", []))
        indicators += min(1.0, skill_diversity / 15)  # 15+ skills = excellent diversity
        
        # Check for growth
        total_indicators += 1
        if positions and len(positions) >= 2:
            indicators += 0.7  # Job hopping or growth
        else:
            indicators += 0.3
        
        return indicators / total_indicators if total_indicators > 0 else 0.5
    
    def _score_availability(self, candidate_data: Dict[str, Any]) -> float:
        """Score candidate availability"""
        notice_period = candidate_data.get("notice_period_days", 30)
        
        if notice_period <= 7:
            return 1.0
        elif notice_period <= 14:
            return 0.95
        elif notice_period <= 30:
            return 0.85
        elif notice_period <= 60:
            return 0.7
        else:
            return 0.5
    
    def _score_salary_fit(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> float:
        """Score salary expectation fit"""
        candidate_salary = candidate_data.get("salary_expectations", {}).get("amount", 0)
        job_salary = job_requirements.get("salary_range", {})
        job_min = job_salary.get("min", 0)
        job_max = job_salary.get("max", float("inf"))
        
        if not candidate_salary:
            return 0.8  # Neutral if not specified
        
        if job_min <= candidate_salary <= job_max:
            return 1.0
        elif candidate_salary < job_min:
            return 0.9  # Below range is acceptable
        elif candidate_salary <= job_max * 1.1:
            return 0.7  # Slightly above range
        else:
            return 0.3  # Well above range
    
    def _score_location_fit(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> float:
        """Score location fit"""
        candidate_location = candidate_data.get("location", {})
        job_location = job_requirements.get("location", {})
        job_type = job_requirements.get("job_type", "on-site")
        
        if job_type == "remote":
            return 1.0  # Location irrelevant
        
        if candidate_location.get("city") == job_location.get("city"):
            return 1.0
        elif candidate_location.get("state") == job_location.get("state"):
            return 0.8
        else:
            return 0.5  # Relocation needed
    
    def _score_growth_potential(self, candidate_data: Dict[str, Any]) -> float:
        """Score candidate's growth potential"""
        indicators = 0
        
        # Career progression
        positions = candidate_data.get("experience", {}).get("positions", [])
        if positions and len(positions) >= 2:
            indicators += 0.3
        
        # Education progression
        education = candidate_data.get("education", [])
        if len(education) > 1:
            indicators += 0.2
        
        # Skill diversity and learning
        skill_diversity = len(candidate_data.get("skills", []))
        indicators += min(0.3, skill_diversity / 20)
        
        # Certifications and continuous learning
        certifications = candidate_data.get("education", {}).get("certifications", [])
        indicators += min(0.2, len(certifications) / 5)
        
        return min(1.0, indicators)
    
    def _skills_match(self, required: str, candidate: str) -> bool:
        """Check if skills match (fuzzy matching)"""
        required_normalized = required.lower().strip()
        candidate_normalized = candidate.lower().strip()
        return required_normalized == candidate_normalized or \
               required_normalized in candidate_normalized or \
               candidate_normalized in required_normalized
    
    def _calculate_skill_score(
        self,
        candidate_level: str,
        required_level: str,
        candidate_years: float,
        required_years: float
    ) -> float:
        """Calculate individual skill match score"""
        levels = {"junior": 1, "mid": 2, "senior": 3, "expert": 4}
        
        level_score = 0
        if candidate_level in levels and required_level in levels:
            cand_level = levels[candidate_level]
            req_level = levels[required_level]
            level_score = min(1.0, cand_level / req_level)
        
        experience_score = 0
        if required_years > 0:
            experience_score = min(1.0, candidate_years / required_years)
        else:
            experience_score = 1.0
        
        return (level_score * 0.6) + (experience_score * 0.4)
    
    def _score_industry_match(self, candidate_industries: List[str], required_industries: List[str]) -> float:
        """Score industry experience match"""
        if not required_industries:
            return 0.5
        
        matches = sum(1 for ind in candidate_industries if ind in required_industries)
        return min(1.0, matches / len(required_industries))
    
    def _field_similarity(self, field1: str, field2: str) -> float:
        """Calculate similarity between education fields"""
        f1_lower = field1.lower()
        f2_lower = field2.lower()
        
        if f1_lower == f2_lower:
            return 1.0
        
        # Related fields
        related_fields = {
            "computer science": ["software engineering", "it", "engineering", "mathematics"],
            "business": ["management", "economics", "finance", "accounting"],
            "engineering": ["computer science", "physics", "mathematics"],
        }
        
        for field, related in related_fields.items():
            if field in f1_lower or field in f2_lower:
                for rel in related:
                    if rel in f1_lower or rel in f2_lower:
                        return 0.7
        
        return 0.2
    
    def _get_match_level(self, score: float) -> MatchLevel:
        """Determine match level from score"""
        if score >= 90:
            return MatchLevel.EXCELLENT
        elif score >= 75:
            return MatchLevel.STRONG
        elif score >= 60:
            return MatchLevel.GOOD
        elif score >= 45:
            return MatchLevel.MODERATE
        elif score >= 30:
            return MatchLevel.WEAK
        else:
            return MatchLevel.POOR
    
    def _get_recommendation(self, score: float, job_requirements: Dict[str, Any]) -> str:
        """Get hiring recommendation"""
        if score >= 80:
            return "Hire"
        elif score >= 60:
            return "Review"
        elif score >= 40:
            return "Waitlist"
        else:
            return "Reject"
    
    def _extract_strengths(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        criteria_scores: Dict[ScreeningCriteria, float]
    ) -> List[str]:
        """Extract candidate strengths"""
        strengths = []
        
        if criteria_scores.get(ScreeningCriteria.SKILLS_MATCH, 0) > 0.75:
            strengths.append("Excellent skill match with job requirements")
        
        if criteria_scores.get(ScreeningCriteria.EXPERIENCE_LEVEL, 0) > 0.8:
            strengths.append("Strong relevant experience")
        
        if criteria_scores.get(ScreeningCriteria.GROWTH_POTENTIAL, 0) > 0.75:
            strengths.append("High growth potential")
        
        if len(candidate_data.get("skills", [])) > 12:
            strengths.append("Diverse skill set")
        
        return strengths[:5]
    
    def _extract_gaps(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        criteria_scores: Dict[ScreeningCriteria, float]
    ) -> List[str]:
        """Extract skill and experience gaps"""
        gaps = []
        
        if criteria_scores.get(ScreeningCriteria.SKILLS_MATCH, 0) < 0.7:
            gaps.append("Missing some key skills")
        
        if criteria_scores.get(ScreeningCriteria.EXPERIENCE_LEVEL, 0) < 0.65:
            gaps.append("Below required experience level")
        
        if criteria_scores.get(ScreeningCriteria.EDUCATION_MATCH, 0) < 0.6:
            gaps.append("Education below requirements")
        
        return gaps
    
    def _extract_concerns(
        self,
        candidate_data: Dict[str, Any],
        criteria_scores: Dict[ScreeningCriteria, float]
    ) -> List[str]:
        """Extract potential concerns"""
        concerns = []
        
        positions = candidate_data.get("experience", {}).get("positions", [])
        if positions and len(positions) > 4:
            concerns.append("Frequent job changes")
        
        if criteria_scores.get(ScreeningCriteria.AVAILABILITY, 0) < 0.6:
            concerns.append("Long notice period")
        
        return concerns
    
    def _extract_opportunities(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> List[str]:
        """Extract growth opportunities"""
        opportunities = []
        
        missing_skills = job_requirements.get("nice_to_have_skills", [])
        candidate_skills = {s.get("name", "").lower() for s in candidate_data.get("skills", [])}
        
        for skill in missing_skills[:3]:
            if skill.lower() not in candidate_skills:
                opportunities.append(f"Can learn {skill}")
        
        return opportunities
    
    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        job_requirements: Dict[str, Any],
        top_n: int = 10
    ) -> RankingResult:
        """
        Rank multiple candidates against a job.
        
        Args:
            candidates: List of candidate data
            job_requirements: Job requirements
            top_n: Number of top candidates to return
            
        Returns:
            RankingResult with ranked candidates
        """
        screenings = []
        
        for candidate in candidates:
            screening = self.screen_candidate(candidate, job_requirements)
            screenings.append(screening)
        
        # Sort by score
        screenings.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Prepare ranking result
        result = RankingResult(
            job_id=job_requirements.get("id", "unknown"),
            job_title=job_requirements.get("title", "Unknown"),
            total_candidates=len(candidates),
            top_candidates=screenings[:top_n]
        )
        
        # Create ranked list (candidate_id, name, score, match_level)
        result.ranked_candidates = [
            (s.candidate_id, s.candidate_name, s.overall_score, s.match_level)
            for s in screenings[:top_n]
        ]
        
        # Calculate statistics
        scores = [s.overall_score for s in screenings]
        result.statistics = {
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "max_score": round(max(scores), 2) if scores else 0,
            "min_score": round(min(scores), 2) if scores else 0,
            "excellent_count": len([s for s in screenings if s.match_level == MatchLevel.EXCELLENT]),
            "strong_count": len([s for s in screenings if s.match_level == MatchLevel.STRONG]),
            "good_count": len([s for s in screenings if s.match_level == MatchLevel.GOOD]),
            "weak_count": len([s for s in screenings if s.match_level == MatchLevel.WEAK]),
        }
        
        return result
