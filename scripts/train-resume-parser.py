"""
Resume Parser ML Model Training Script
This script trains a model to extract information from resumes
"""

import pandas as pd
import numpy as np
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self):
        self.skill_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.experience_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Load spaCy model for NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_text_features(self, text):
        """Extract features from resume text"""
        features = {}
        
        # Basic text statistics
        features['word_count'] = len(text.split())
        features['char_count'] = len(text)
        features['sentence_count'] = len(text.split('.'))
        
        # Email detection
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        features['has_email'] = len(re.findall(email_pattern, text)) > 0
        
        # Phone number detection
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?$$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4}'
        features['has_phone'] = len(re.findall(phone_pattern, text)) > 0
        
        # Education keywords
        education_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'education']
        features['education_mentions'] = sum(1 for keyword in education_keywords if keyword.lower() in text.lower())
        
        # Experience keywords
        experience_keywords = ['experience', 'worked', 'employed', 'position', 'role', 'job', 'company']
        features['experience_mentions'] = sum(1 for keyword in experience_keywords if keyword.lower() in text.lower())
        
        # Technical skills keywords
        tech_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes']
        features['tech_skills_count'] = sum(1 for skill in tech_skills if skill.lower() in text.lower())
        
        return features
    
    def extract_contact_info(self, text):
        """Extract contact information from resume"""
        contact_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['email'] = emails[0] if emails else None
        
        # Extract phone number
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?$$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        contact_info['phone'] = phones[0] if phones else None
        
        # Extract name (first few words, typically)
        lines = text.split('\n')
        potential_name = lines[0].strip() if lines else ""
        # Simple name validation
        if len(potential_name.split()) <= 4 and potential_name.replace(' ', '').isalpha():
            contact_info['name'] = potential_name
        else:
            contact_info['name'] = None
        
        return contact_info
    
    def extract_skills(self, text):
        """Extract skills from resume text"""
        # Predefined skill categories
        skill_categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web_development': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'matplotlib', 'seaborn'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem-solving', 'analytical', 'creative']
        }
        
        extracted_skills = {}
        text_lower = text.lower()
        
        for category, skills in skill_categories.items():
            found_skills = [skill for skill in skills if skill in text_lower]
            extracted_skills[category] = found_skills
        
        return extracted_skills
    
    def extract_experience(self, text):
        """Extract work experience from resume"""
        experience = []
        
        # Look for date patterns (years)
        date_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(date_pattern, text)
        
        # Look for company/position patterns
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains potential job title or company
            job_indicators = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator', 'director']
            company_indicators = ['inc', 'corp', 'llc', 'ltd', 'company', 'technologies', 'solutions']
            
            if any(indicator in line.lower() for indicator in job_indicators + company_indicators):
                # Try to extract dates from surrounding lines
                context_lines = lines[max(0, i-2):min(len(lines), i+3)]
                context_text = ' '.join(context_lines)
                context_years = re.findall(date_pattern, context_text)
                
                experience.append({
                    'title_or_company': line,
                    'years': context_years,
                    'context': context_text[:200]  # First 200 chars for context
                })
        
        return experience
    
    def extract_education(self, text):
        """Extract education information from resume"""
        education = []
        
        # Education keywords and patterns
        degree_patterns = [
            r'\b(bachelor|master|phd|doctorate|associate)\s+(of\s+)?(arts|science|engineering|business|computer science)\b',
            r'\b(ba|bs|ms|ma|mba|phd)\b',
            r'\b(degree|diploma|certificate)\b'
        ]
        
        institution_indicators = ['university', 'college', 'institute', 'school']
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip().lower()
            if not line:
                continue
            
            # Check for degree patterns
            for pattern in degree_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Look for institution in surrounding lines
                    context_lines = lines[max(0, i-2):min(len(lines), i+3)]
                    
                    institution = None
                    for context_line in context_lines:
                        if any(indicator in context_line.lower() for indicator in institution_indicators):
                            institution = context_line.strip()
                            break
                    
                    education.append({
                        'degree': line,
                        'institution': institution,
                        'context': ' '.join(context_lines)[:200]
                    })
                    break
        
        return education
    
    def parse_resume(self, text):
        """Parse a complete resume and extract all information"""
        parsed_data = {
            'contact_info': self.extract_contact_info(text),
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text),
            'text_features': self.extract_text_features(text),
            'raw_text': text[:500]  # First 500 chars for reference
        }
        
        return parsed_data
    
    def prepare_training_data(self, data_dir):
        """Prepare training data from resume samples"""
        # This would typically load from a dataset of labeled resumes
        # For demo purposes, we'll create some synthetic training data
        
        sample_resumes = [
            {
                'text': """John Doe
                Software Engineer
                john.doe@email.com | (555) 123-4567
                
                Experience:
                Senior Software Engineer at Tech Corp (2020-2023)
                - Developed web applications using React and Node.js
                - Led team of 5 developers
                
                Software Engineer at StartupXYZ (2018-2020)
                - Built scalable backend systems with Python and AWS
                
                Education:
                Bachelor of Science in Computer Science
                University of Technology (2014-2018)
                
                Skills: Python, JavaScript, React, Node.js, AWS, Docker""",
                'labels': {
                    'has_contact': True,
                    'experience_level': 'senior',
                    'tech_skills_count': 6
                }
            },
            # Add more sample resumes here...
        ]
        
        return sample_resumes
    
    def train_models(self, training_data):
        """Train the resume parsing models"""
        logger.info("Training resume parsing models...")
        
        # Extract features and labels from training data
        features = []
        skill_labels = []
        experience_labels = []
        
        for resume in training_data:
            text_features = self.extract_text_features(resume['text'])
            features.append(list(text_features.values()))
            
            # Create labels for different classification tasks
            skill_labels.append(resume['labels']['tech_skills_count'])
            experience_
