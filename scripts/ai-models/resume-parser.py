"""
Advanced Resume Parser with NLP and ML
Extracts comprehensive information from resumes using AI
"""

import spacy
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import re
import json
import logging
from datetime import datetime
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedResumeParser:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.error("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize ML models
        self.skill_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.experience_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Skill categories and keywords
        self.skill_categories = {
            'programming': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 
                'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r'
            ],
            'web_development': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 
                'django', 'flask', 'spring', 'laravel', 'rails'
            ],
            'databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 
                'oracle', 'sqlite', 'cassandra', 'dynamodb'
            ],
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 
                'jenkins', 'gitlab', 'ansible', 'chef'
            ],
            'data_science': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 
                'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop'
            ],
            'mobile': [
                'android', 'ios', 'react native', 'flutter', 'xamarin', 
                'swift', 'kotlin', 'objective-c'
            ],
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem-solving', 
                'analytical', 'creative', 'adaptable', 'organized'
            ]
        }
        
        # Experience level indicators
        self.experience_indicators = {
            'junior': ['junior', 'entry', 'associate', 'trainee', '0-2 years'],
            'mid': ['mid', 'intermediate', 'developer', '2-5 years', '3-6 years'],
            'senior': ['senior', 'lead', 'principal', '5+ years', '7+ years'],
            'executive': ['director', 'manager', 'head', 'vp', 'cto', 'ceo']
        }

    def extract_contact_info(self, text):
        """Extract contact information from resume"""
        contact_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['email'] = emails[0] if emails else None
        
        # Extract phone number
        phone_patterns = [
            r'(\+\d{1,3}[-.\s]?)?($$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4})',
            r'(\+\d{1,3}[-.\s]?)?\d{10}',
            r'(\+\d{1,3}[-.\s]?)?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
                break
        
        # Extract name (usually first line or first few words)
        lines = text.split('\n')
        potential_name = lines[0].strip() if lines else ""
        
        # Clean and validate name
        name_words = potential_name.split()
        if len(name_words) <= 4 and all(word.replace('-', '').isalpha() for word in name_words):
            contact_info['name'] = potential_name
        else:
            contact_info['name'] = None
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        contact_info['linkedin'] = linkedin_matches[0] if linkedin_matches else None
        
        # Extract GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        contact_info['github'] = github_matches[0] if github_matches else None
        
        return contact_info

    def extract_skills(self, text):
        """Extract and categorize skills from resume"""
        text_lower = text.lower()
        extracted_skills = {}
        
        for category, skills in self.skill_categories.items():
            found_skills = []
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
            
            extracted_skills[category] = found_skills
        
        # Calculate skill scores
        skill_scores = {}
        for category, skills in extracted_skills.items():
            skill_scores[category] = len(skills)
        
        return {
            'skills_by_category': extracted_skills,
            'skill_scores': skill_scores,
            'total_skills': sum(len(skills) for skills in extracted_skills.values())
        }

    def extract_experience(self, text):
        """Extract work experience information"""
        experience_data = {
            'positions': [],
            'total_years': 0,
            'level': 'entry',
            'companies': []
        }
        
        # Extract years of experience
        year_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience'
        ]
        
        years_found = []
        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years_found.extend([int(match) for match in matches])
        
        if years_found:
            experience_data['total_years'] = max(years_found)
        
        # Determine experience level
        if experience_data['total_years'] >= 10:
            experience_data['level'] = 'senior'
        elif experience_data['total_years'] >= 5:
            experience_data['level'] = 'mid'
        elif experience_data['total_years'] >= 2:
            experience_data['level'] = 'junior'
        else:
            experience_data['level'] = 'entry'
        
        # Extract job titles and companies
        lines = text.split('\n')
        
        job_title_indicators = [
            'engineer', 'developer', 'manager', 'analyst', 'specialist',
            'coordinator', 'director', 'lead', 'architect', 'consultant'
        ]
        
        company_indicators = [
            'inc', 'corp', 'llc', 'ltd', 'company', 'technologies',
            'solutions', 'systems', 'group', 'enterprises'
        ]
        
        for i, line in enumerate(lines):
            line_clean = line.strip().lower()
            
            # Check for job titles
            if any(indicator in line_clean for indicator in job_title_indicators):
                # Look for company in surrounding lines
                context_lines = lines[max(0, i-2):min(len(lines), i+3)]
                
                for context_line in context_lines:
                    if any(indicator in context_line.lower() for indicator in company_indicators):
                        experience_data['companies'].append(context_line.strip())
                        break
                
                experience_data['positions'].append({
                    'title': line.strip(),
                    'context': ' '.join(context_lines)[:200]
                })
        
        return experience_data

    def extract_education(self, text):
        """Extract education information"""
        education_data = {
            'degrees': [],
            'institutions': [],
            'level': 'none'
        }
        
        # Degree patterns
        degree_patterns = [
            r'\b(bachelor|master|phd|doctorate|associate)\s+(?:of\s+)?(?:science|arts|engineering|business|computer science)\b',
            r'\b(ba|bs|ms|ma|mba|phd|btech|mtech)\b',
            r'\b(degree|diploma|certificate)\s+in\s+[\w\s]+',
            r'\b(graduation|graduated)\s+(?:in|with)\s+[\
