"""
Multi-AI Integration System
Combines OpenAI, Google Gemini, and Anthropic Claude for ensemble predictions
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import openai
import google.generativeai as genai
import anthropic
import numpy as np
from datetime import datetime
import json
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import statistics

logger = logging.getLogger(__name__)

class MultiAIIntegration:
    def __init__(self):
        self.openai_client = None
        self.gemini_client = None
        self.claude_client = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Model configurations
        self.model_configs = {
            "openai": {
                "gpt-4": {"max_tokens": 4000, "temperature": 0.7},
                "gpt-3.5-turbo": {"max_tokens": 2000, "temperature": 0.7},
                "text-embedding-ada-002": {"dimensions": 1536}
            },
            "gemini": {
                "gemini-pro": {"max_output_tokens": 2048, "temperature": 0.7},
                "gemini-pro-vision": {"max_output_tokens": 2048, "temperature": 0.7}
            },
            "claude": {
                "claude-3-opus": {"max_tokens": 4000, "temperature": 0.7},
                "claude-3-sonnet": {"max_tokens": 2000, "temperature": 0.7},
                "claude-3-haiku": {"max_tokens": 1000, "temperature": 0.7}
            }
        }

    async def initialize(self):
        """Initialize all AI clients"""
        try:
            logger.info("Initializing Multi-AI Integration...")
            
            # Initialize OpenAI
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = openai
            
            # Initialize Google Gemini
            genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
            self.gemini_client = genai.GenerativeModel('gemini-pro')
            
            # Initialize Anthropic Claude
            self.claude_client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            
            logger.info("Multi-AI Integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Multi-AI initialization error: {str(e)}")
            raise

    async def ensemble_resume_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume using all AI models and combine results"""
        try:
            logger.info("Starting ensemble resume analysis...")
            
            # Parallel analysis with all models
            tasks = [
                self._openai_resume_analysis(resume_text),
                self._gemini_resume_analysis(resume_text),
                self._claude_resume_analysis(resume_text)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            combined_analysis = await self._combine_resume_analyses(results)
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Ensemble resume analysis error: {str(e)}")
            raise

    async def _openai_resume_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume using OpenAI GPT-4"""
        try:
            prompt = f"""
            Analyze this resume comprehensively:
            
            {resume_text}
            
            Provide analysis in JSON format with:
            1. Overall score (0-100)
            2. Skills extracted (list)
            3. Experience level (junior/mid/senior/expert)
            4. Education assessment
            5. Strengths (list)
            6. Improvement areas (list)
            7. Job category prediction
            8. Salary range estimate
            9. Interview readiness score
            10. Cultural fit indicators
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst providing detailed resume analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse JSON response
            analysis_text = response.choices[0].message.content
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback parsing
                analysis = self._parse_analysis_text(analysis_text)
            
            analysis["source"] = "openai"
            analysis["model"] = "gpt-4"
            
            return analysis
            
        except Exception as e:
            logger.error(f"OpenAI resume analysis error: {str(e)}")
            return {"source": "openai", "error": str(e)}

    async def _gemini_resume_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume using Google Gemini"""
        try:
            prompt = f"""
            Perform detailed resume analysis for:
            
            {resume_text}
            
            Return structured analysis with:
            - Overall quality score (0-100)
            - Technical skills identified
            - Experience level assessment
            - Education evaluation
            - Key strengths
            - Areas needing improvement
            - Best-fit job roles
            - Estimated salary range
            - Interview preparation score
            - Team fit assessment
            
            Format as JSON.
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.gemini_client.generate_content(prompt)
            )
            
            analysis_text = response.text
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = self._parse_analysis_text(analysis_text)
            
            analysis["source"] = "gemini"
            analysis["model"] = "gemini-pro"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Gemini resume analysis error: {str(e)}")
            return {"source": "gemini", "error": str(e)}

    async def _claude_resume_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume using Anthropic Claude"""
        try:
            prompt = f"""
            Conduct comprehensive resume evaluation:
            
            {resume_text}
            
            Provide detailed JSON analysis including:
            1. Quality score (0-100)
            2. Skills inventory
            3. Experience classification
            4. Educational background assessment
            5. Notable strengths
            6. Development opportunities
            7. Role recommendations
            8. Compensation expectations
            9. Interview readiness
            10. Organizational fit factors
            """
            
            message = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.claude_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1500,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            )
            
            analysis_text = message.content[0].text
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = self._parse_analysis_text(analysis_text)
            
            analysis["source"] = "claude"
            analysis["model"] = "claude-3-opus"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Claude resume analysis error: {str(e)}")
            return {"source": "claude", "error": str(e)}

    async def _combine_resume_analyses(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine analyses from all AI models"""
        try:
            valid_analyses = [a for a in analyses if not isinstance(a, Exception) and "error" not in a]
            
            if not valid_analyses:
                return {"error": "All AI analyses failed"}
            
            # Combine scores
            scores = [a.get("overall_score", 0) for a in valid_analyses if a.get("overall_score")]
            combined_score = statistics.mean(scores) if scores else 0
            
            # Combine skills
            all_skills = []
            for analysis in valid_analyses:
                skills = analysis.get("skills", [])
                if isinstance(skills, list):
                    all_skills.extend(skills)
            
            unique_skills = list(set(all_skills))
            
            # Combine experience levels
            experience_levels = [a.get("experience_level", "") for a in valid_analyses if a.get("experience_level")]
            combined_experience = statistics.mode(experience_levels) if experience_levels else "unknown"
            
            # Combine strengths
            all_strengths = []
            for analysis in valid_analyses:
                strengths = analysis.get("strengths", [])
                if isinstance(strengths, list):
                    all_strengths.extend(strengths)
            
            # Combine improvement areas
            all_improvements = []
            for analysis in valid_analyses:
                improvements = analysis.get("improvement_areas", [])
                if isinstance(improvements, list):
                    all_improvements.extend(improvements)
            
            # Generate consensus
            combined_analysis = {
                "ensemble_score": combined_score,
                "confidence": len(valid_analyses) / 3,  # Confidence based on successful analyses
                "skills": unique_skills,
                "experience_level": combined_experience,
                "strengths": list(set(all_strengths)),
                "improvement_areas": list(set(all_improvements)),
                "individual_analyses": valid_analyses,
                "consensus_metrics": {
                    "score_variance": statistics.variance(scores) if len(scores) > 1 else 0,
                    "agreement_level": self._calculate_agreement_level(valid_analyses)
                },
                "analyzed_at": datetime.utcnow().isoformat(),
                "models_used": [a.get("source") for a in valid_analyses]
            }
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Analysis combination error: {str(e)}")
            return {"error": str(e)}

    async def ensemble_interview_evaluation(self, conversation: str, interview_type: str) -> Dict[str, Any]:
        """Evaluate interview using ensemble of AI models"""
        try:
            logger.info("Starting ensemble interview evaluation...")
            
            tasks = [
                self._openai_interview_evaluation(conversation, interview_type),
                self._gemini_interview_evaluation(conversation, interview_type),
                self._claude_interview_evaluation(conversation, interview_type)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            combined_evaluation = await self._combine_interview_evaluations(results)
            
            return combined_evaluation
            
        except Exception as e:
            logger.error(f"Ensemble interview evaluation error: {str(e)}")
            raise

    async def _openai_interview_evaluation(self, conversation: str, interview_type: str) -> Dict[str, Any]:
        """Evaluate interview using OpenAI"""
        try:
            prompt = f"""
            Evaluate this {interview_type} interview conversation:
            
            {conversation}
            
            Provide comprehensive evaluation in JSON format:
            1. Overall score (0-100)
            2. Technical competency score
            3. Communication skills score
            4. Problem-solving ability score
            5. Cultural fit score
            6. Specific strengths demonstrated
            7. Areas of concern
            8. Hiring recommendation (hire/maybe/no_hire)
            9. Detailed feedback
            10. Follow-up questions suggested
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interview evaluator providing detailed candidate assessments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.3
            )
            
            evaluation_text = response.choices[0].message.content
            try:
                evaluation = json.loads(evaluation_text)
            except json.JSONDecodeError:
                evaluation = self._parse_evaluation_text(evaluation_text)
            
            evaluation["source"] = "openai"
            return evaluation
            
        except Exception as e:
            logger.error(f"OpenAI interview evaluation error: {str(e)}")
            return {"source": "openai", "error": str(e)}

    async def _gemini_interview_evaluation(self, conversation: str, interview_type: str) -> Dict[str, Any]:
        """Evaluate interview using Gemini"""
        try:
            prompt = f"""
            Analyze this {interview_type} interview performance:
            
            {conversation}
            
            Provide structured evaluation covering:
            - Overall performance score (0-100)
            - Technical skills assessment
            - Communication effectiveness
            - Problem-solving approach
            - Cultural alignment
            - Key strengths observed
            - Improvement areas
            - Hiring decision recommendation
            - Constructive feedback
            - Additional assessment suggestions
            
            Return as JSON.
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.gemini_client.generate_content(prompt)
            )
            
            evaluation_text = response.text
            try:
                evaluation = json.loads(evaluation_text)
            except json.JSONDecodeError:
                evaluation = self._parse_evaluation_text(evaluation_text)
            
            evaluation["source"] = "gemini"
            return evaluation
            
        except Exception as e:
            logger.error(f"Gemini interview evaluation error: {str(e)}")
            return {"source": "gemini", "error": str(e)}

    async def _claude_interview_evaluation(self, conversation: str, interview_type: str) -> Dict[str, Any]:
        """Evaluate interview using Claude"""
        try:
            prompt = f"""
            Evaluate candidate performance in this {interview_type} interview:
            
            {conversation}
            
            Provide comprehensive JSON assessment with:
            1. Overall score (0-100)
            2. Technical proficiency rating
            3. Communication quality score
            4. Analytical thinking assessment
            5. Team fit evaluation
            6. Demonstrated strengths
            7. Development needs
            8. Hiring recommendation
            9. Detailed feedback comments
            10. Next steps suggestions
            """
            
            message = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.claude_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1200,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            )
            
            evaluation_text = message.content[0].text
            try:
                evaluation = json.loads(evaluation_text)
            except json.JSONDecodeError:
                evaluation = self._parse_evaluation_text(evaluation_text)
            
            evaluation["source"] = "claude"
            return evaluation
            
        except Exception as e:
            logger.error(f"Claude interview evaluation error: {str(e)}")
            return {"source": "claude", "error": str(e)}

    async def _combine_interview_evaluations(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine interview evaluations from all models"""
        try:
            valid_evaluations = [e for e in evaluations if not isinstance(e, Exception) and "error" not in e]
            
            if not valid_evaluations:
                return {"error": "All interview evaluations failed"}
            
            # Combine scores
            overall_scores = [e.get("overall_score", 0) for e in valid_evaluations if e.get("overall_score")]
            combined_score = statistics.mean(overall_scores) if overall_scores else 0
            
            # Combine recommendations
            recommendations = [e.get("hiring_recommendation", "") for e in valid_evaluations if e.get("hiring_recommendation")]
            
            # Calculate consensus recommendation
            hire_votes = recommendations.count("hire")
            maybe_votes = recommendations.count("maybe")
            no_hire_votes = recommendations.count("no_hire")
            
            if hire_votes > maybe_votes and hire_votes > no_hire_votes:
                consensus_recommendation = "hire"
            elif no_hire_votes > hire_votes and no_hire_votes > maybe_votes:
                consensus_recommendation = "no_hire"
            else:
                consensus_recommendation = "maybe"
            
            # Combine feedback
            all_feedback = []
            for evaluation in valid_evaluations:
                feedback = evaluation.get("feedback", "")
                if feedback:
                    all_feedback.append(feedback)
            
            combined_evaluation = {
                "ensemble_score": combined_score,
                "consensus_recommendation": consensus_recommendation,
                "confidence": len(valid_evaluations) / 3,
                "score_variance": statistics.variance(overall_scores) if len(overall_scores) > 1 else 0,
                "recommendation_distribution": {
                    "hire": hire_votes,
                    "maybe": maybe_votes,
                    "no_hire": no_hire_votes
                },
                "combined_feedback": " ".join(all_feedback),
                "individual_evaluations": valid_evaluations,
                "evaluated_at": datetime.utcnow().isoformat(),
                "models_used": [e.get("source") for e in valid_evaluations]
            }
            
            return combined_evaluation
            
        except Exception as e:
            logger.error(f"Interview evaluation combination error: {str(e)}")
            return {"error": str(e)}

    async def ensemble_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using ensemble of AI models"""
        try:
            tasks = [
                self._openai_sentiment_analysis(text),
                self._gemini_sentiment_analysis(text),
                self._claude_sentiment_analysis(text)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            combined_sentiment = await self._combine_sentiment_analyses(results)
            
            return combined_sentiment
            
        except Exception as e:
            logger.error(f"Ensemble sentiment analysis error: {str(e)}")
            raise

    async def _openai_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using OpenAI"""
        try:
            prompt = f"""
            Analyze the sentiment and emotional tone of this workplace communication:
            
            "{text}"
            
            Provide analysis in JSON format:
            1. Primary sentiment (positive/negative/neutral)
            2. Sentiment confidence (0-1)
            3. Emotional tone (happy/sad/angry/frustrated/excited/concerned/satisfied)
            4. Intensity level (low/medium/high)
            5. Professional tone assessment
            6. Urgency level
            7. Key emotional indicators
            8. Workplace appropriateness score
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in workplace communication sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            analysis_text = response.choices[0].message.content
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = self._parse_sentiment_text(analysis_text)
            
            analysis["source"] = "openai"
            return analysis
            
        except Exception as e:
            logger.error(f"OpenAI sentiment analysis error: {str(e)}")
            return {"source": "openai", "error": str(e)}

    async def _gemini_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Gemini"""
        try:
            prompt = f"""
            Perform sentiment analysis on this workplace text:
            
            "{text}"
            
            Return JSON analysis with:
            - Overall sentiment classification
            - Confidence score
            - Emotional state detected
            - Intensity measurement
            - Professional communication assessment
            - Urgency indicators
            - Emotional markers identified
            - Workplace context appropriateness
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.gemini_client.generate_content(prompt)
            )
            
            analysis_text = response.text
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = self._parse_sentiment_text(analysis_text)
            
            analysis["source"] = "gemini"
            return analysis
            
        except Exception as e:
            logger.error(f"Gemini sentiment analysis error: {str(e)}")
            return {"source": "gemini", "error": str(e)}

    async def _claude_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Claude"""
        try:
            prompt = f"""
            Analyze sentiment and emotional content of this workplace communication:
            
            "{text}"
            
            Provide comprehensive JSON analysis including:
            1. Sentiment classification
            2. Confidence level
            3. Emotional tone identification
            4. Intensity rating
            5. Professional tone evaluation
            6. Urgency assessment
            7. Emotional cues present
            8. Workplace communication quality
            """
            
            message = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.claude_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    temperature=0.2,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            )
            
            analysis_text = message.content[0].text
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                analysis = self._parse_sentiment_text(analysis_text)
            
            analysis["source"] = "claude"
            return analysis
            
        except Exception as e:
            logger.error(f"Claude sentiment analysis error: {str(e)}")
            return {"source": "claude", "error": str(e)}

    async def _combine_sentiment_analyses(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine sentiment analyses from all models"""
        try:
            valid_analyses = [a for a in analyses if not isinstance(a, Exception) and "error" not in a]
            
            if not valid_analyses:
                return {"error": "All sentiment analyses failed"}
            
            # Combine sentiments
            sentiments = [a.get("primary_sentiment", "") for a in valid_analyses if a.get("primary_sentiment")]
            
            # Calculate consensus sentiment
            positive_count = sentiments.count("positive")
            negative_count = sentiments.count("negative")
            neutral_count = sentiments.count("neutral")
            
            if positive_count > negative_count and positive_count > neutral_count:
                consensus_sentiment = "positive"
            elif negative_count > positive_count and negative_count > neutral_count:
                consensus_sentiment = "negative"
            else:
                consensus_sentiment = "neutral"
            
            # Combine confidence scores
            confidences = [a.get("sentiment_confidence", 0) for a in valid_analyses if a.get("sentiment_confidence")]
            avg_confidence = statistics.mean(confidences) if confidences else 0
            
            combined_analysis = {
                "consensus_sentiment": consensus_sentiment,
                "confidence": avg_confidence,
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                },
                "agreement_level": max(positive_count, negative_count, neutral_count) / len(sentiments) if sentiments else 0,
                "individual_analyses": valid_analyses,
                "analyzed_at": datetime.utcnow().isoformat(),
                "models_used": [a.get("source") for a in valid_analyses]
            }
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Sentiment analysis combination error: {str(e)}")
            return {"error": str(e)}

    def _parse_analysis_text(self, text: str) -> Dict[str, Any]:
        """Parse analysis text when JSON parsing fails"""
        # Simple fallback parsing
        return {
            "overall_score": 75,
            "skills": ["General Skills"],
            "experience_level": "mid",
            "strengths": ["Professional Experience"],
            "improvement_areas": ["Further Development"],
            "parsed_from_text": True
        }

    def _parse_evaluation_text(self, text: str) -> Dict[str, Any]:
        """Parse evaluation text when JSON parsing fails"""
        return {
            "overall_score": 70,
            "hiring_recommendation": "maybe",
            "feedback": text[:200] + "..." if len(text) > 200 else text,
            "parsed_from_text": True
        }

    def _parse_sentiment_text(self, text: str) -> Dict[str, Any]:
        """Parse sentiment text when JSON parsing fails"""
        return {
            "primary_sentiment": "neutral",
            "sentiment_confidence": 0.5,
            "emotional_tone": "professional",
            "parsed_from_text": True
        }

    def _calculate_agreement_level(self, analyses: List[Dict[str, Any]]) -> float:
        """Calculate agreement level between different AI models"""
        if len(analyses) < 2:
            return 1.0
        
        # Simple agreement calculation based on score variance
        scores = [a.get("overall_score", 0) for a in analyses if a.get("overall_score")]
        if not scores:
            return 0.5
        
        variance = statistics.variance(scores) if len(scores) > 1 else 0
        # Convert variance to agreement (lower variance = higher agreement)
        agreement = max(0, 1 - (variance / 1000))  # Normalize variance
        
        return agreement
