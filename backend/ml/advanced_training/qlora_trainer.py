"""
Advanced QLoRA/LoRA Training System for HR Models
Uses cutting-edge parameter-efficient fine-tuning techniques
"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training,
    PeftModel, PeftConfig
)
from datasets import Dataset, load_dataset
import bitsandbytes as bnb
from accelerate import Accelerator
import wandb
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report
import logging
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedQLoRATrainer:
    def __init__(self, model_name: str = "microsoft/DialoGPT-large", task_type: str = "CAUSAL_LM"):
        self.model_name = model_name
        self.task_type = TaskType[task_type]
        self.tokenizer = None
        self.model = None
        self.peft_model = None
        self.accelerator = Accelerator()
        
        # Advanced LoRA configurations
        self.lora_configs = {
            "resume_classifier": LoraConfig(
                task_type=TaskType.SEQ_CLS,
                inference_mode=False,
                r=16,  # Rank
                lora_alpha=32,  # Scaling parameter
                lora_dropout=0.1,
                target_modules=["query", "value", "key", "dense"],
                bias="none",
                modules_to_save=["classifier"]
            ),
            "interview_agent": LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=32,
                lora_alpha=64,
                lora_dropout=0.05,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                bias="none"
            ),
            "sentiment_analyzer": LoraConfig(
                task_type=TaskType.SEQ_CLS,
                inference_mode=False,
                r=8,
                lora_alpha=16,
                lora_dropout=0.1,
                target_modules=["query", "value"],
                bias="lora_only"
            ),
            "performance_predictor": LoraConfig(
                task_type=TaskType.SEQ_CLS,
                inference_mode=False,
                r=24,
                lora_alpha=48,
                lora_dropout=0.08,
                target_modules=["query", "value", "key", "dense", "intermediate"],
                bias="none"
            )
        }

    async def setup_model_and_tokenizer(self, model_config: str):
        """Setup model and tokenizer with QLoRA configuration"""
        try:
            logger.info(f"Setting up model: {self.model_name} for {model_config}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side="left"
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # QLoRA configuration for 4-bit quantization
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            
            # Load model with quantization
            if model_config in ["resume_classifier", "sentiment_analyzer", "performance_predictor"]:
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True,
                    num_labels=self._get_num_labels(model_config)
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True
                )
            
            # Prepare model for k-bit training
            self.model = prepare_model_for_kbit_training(self.model)
            
            # Apply LoRA
            lora_config = self.lora_configs[model_config]
            self.peft_model = get_peft_model(self.model, lora_config)
            
            # Print trainable parameters
            self.peft_model.print_trainable_parameters()
            
            logger.info(f"Model setup complete for {model_config}")
            
        except Exception as e:
            logger.error(f"Model setup error: {str(e)}")
            raise

    def _get_num_labels(self, model_config: str) -> int:
        """Get number of labels for classification tasks"""
        label_counts = {
            "resume_classifier": 16,  # Job categories
            "sentiment_analyzer": 7,   # Emotions + sentiment
            "performance_predictor": 5  # Performance levels
        }
        return label_counts.get(model_config, 2)

    async def generate_advanced_datasets(self) -> Dict[str, Dataset]:
        """Generate comprehensive datasets using multiple AI models"""
        try:
            logger.info("Generating advanced HR datasets...")
            
            datasets = {}
            
            # Resume Classification Dataset
            datasets["resume_classifier"] = await self._generate_resume_dataset()
            
            # Interview Conversation Dataset
            datasets["interview_agent"] = await self._generate_interview_dataset()
            
            # Sentiment Analysis Dataset
            datasets["sentiment_analyzer"] = await self._generate_sentiment_dataset()
            
            # Performance Prediction Dataset
            datasets["performance_predictor"] = await self._generate_performance_dataset()
            
            # Conflict Resolution Dataset
            datasets["conflict_resolver"] = await self._generate_conflict_dataset()
            
            # Training Recommendation Dataset
            datasets["training_recommender"] = await self._generate_training_dataset()
            
            logger.info("Dataset generation complete")
            return datasets
            
        except Exception as e:
            logger.error(f"Dataset generation error: {str(e)}")
            raise

    async def _generate_resume_dataset(self) -> Dataset:
        """Generate comprehensive resume classification dataset"""
        try:
            logger.info("Generating resume classification dataset...")
            
            job_categories = [
                "Software Engineer", "Data Scientist", "Product Manager", "UX Designer",
                "DevOps Engineer", "Marketing Manager", "Sales Representative", "HR Manager",
                "Financial Analyst", "Business Analyst", "Project Manager", "Quality Assurance",
                "Customer Success", "Operations Manager", "Research Scientist", "Consultant"
            ]
            
            skill_sets = {
                "Software Engineer": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Git"],
                "Data Scientist": ["Python", "R", "SQL", "Machine Learning", "TensorFlow", "Pandas", "Jupyter"],
                "Product Manager": ["Agile", "Scrum", "Analytics", "Roadmapping", "Stakeholder Management"],
                "UX Designer": ["Figma", "Sketch", "User Research", "Prototyping", "Wireframing"],
                "DevOps Engineer": ["Kubernetes", "Docker", "CI/CD", "AWS", "Terraform", "Monitoring"],
                "Marketing Manager": ["Digital Marketing", "SEO", "Content Strategy", "Analytics", "CRM"],
                "Sales Representative": ["CRM", "Lead Generation", "Negotiation", "Customer Relations"],
                "HR Manager": ["Recruitment", "Performance Management", "Employee Relations", "HRIS"],
                "Financial Analyst": ["Excel", "Financial Modeling", "SQL", "Tableau", "Bloomberg"],
                "Business Analyst": ["SQL", "Tableau", "Process Mapping", "Requirements Gathering"],
                "Project Manager": ["PMP", "Agile", "Scrum", "Risk Management", "Stakeholder Management"],
                "Quality Assurance": ["Test Automation", "Selenium", "JIRA", "API Testing", "Performance Testing"],
                "Customer Success": ["CRM", "Customer Onboarding", "Retention Strategies", "Analytics"],
                "Operations Manager": ["Process Optimization", "Supply Chain", "Lean Six Sigma", "Analytics"],
                "Research Scientist": ["Research Methodology", "Statistical Analysis", "Publications", "Grants"],
                "Consultant": ["Problem Solving", "Client Management", "Industry Expertise", "Presentation Skills"]
            }
            
            resumes_data = []
            
            for category in job_categories:
                for i in range(625):  # 10,000 total resumes
                    # Generate realistic resume content
                    experience_years = np.random.randint(0, 20)
                    education_level = np.random.choice(["Bachelor's", "Master's", "PhD", "Associate", "High School"])
                    skills = np.random.choice(skill_sets[category], size=np.random.randint(3, 8), replace=False).tolist()
                    
                    resume_text = await self._generate_resume_text(
                        category, experience_years, education_level, skills
                    )
                    
                    resumes_data.append({
                        "text": resume_text,
                        "label": job_categories.index(category),
                        "category": category,
                        "experience_years": experience_years,
                        "education_level": education_level,
                        "skills": skills
                    })
            
            return Dataset.from_pandas(pd.DataFrame(resumes_data))
            
        except Exception as e:
            logger.error(f"Resume dataset generation error: {str(e)}")
            raise

    async def _generate_interview_dataset(self) -> Dataset:
        """Generate comprehensive interview conversation dataset"""
        try:
            logger.info("Generating interview conversation dataset...")
            
            interview_types = ["technical", "behavioral", "cultural", "case_study", "system_design"]
            difficulty_levels = ["junior", "mid", "senior", "principal"]
            
            conversations_data = []
            
            for interview_type in interview_types:
                for difficulty in difficulty_levels:
                    for i in range(400):  # 8,000 total conversations
                        conversation = await self._generate_interview_conversation(
                            interview_type, difficulty
                        )
                        
                        conversations_data.append({
                            "conversation": conversation["text"],
                            "interview_type": interview_type,
                            "difficulty": difficulty,
                            "score": conversation["score"],
                            "feedback": conversation["feedback"],
                            "recommendation": conversation["recommendation"]
                        })
            
            return Dataset.from_pandas(pd.DataFrame(conversations_data))
            
        except Exception as e:
            logger.error(f"Interview dataset generation error: {str(e)}")
            raise

    async def _generate_sentiment_dataset(self) -> Dataset:
        """Generate workplace sentiment analysis dataset"""
        try:
            logger.info("Generating sentiment analysis dataset...")
            
            sentiment_categories = [
                "positive", "negative", "neutral", "frustrated", "excited", "concerned", "satisfied"
            ]
            
            communication_types = [
                "email", "slack_message", "meeting_notes", "feedback", "review", "complaint", "praise"
            ]
            
            sentiment_data = []
            
            for sentiment in sentiment_categories:
                for comm_type in communication_types:
                    for i in range(310):  # 15,000+ total samples
                        text = await self._generate_workplace_communication(sentiment, comm_type)
                        
                        sentiment_data.append({
                            "text": text,
                            "sentiment": sentiment,
                            "communication_type": comm_type,
                            "label": sentiment_categories.index(sentiment),
                            "intensity": np.random.uniform(0.3, 1.0)
                        })
            
            return Dataset.from_pandas(pd.DataFrame(sentiment_data))
            
        except Exception as e:
            logger.error(f"Sentiment dataset generation error: {str(e)}")
            raise

    async def _generate_performance_dataset(self) -> Dataset:
        """Generate performance prediction dataset"""
        try:
            logger.info("Generating performance prediction dataset...")
            
            performance_levels = ["exceptional", "exceeds", "meets", "below", "unsatisfactory"]
            
            performance_data = []
            
            for level in performance_levels:
                for i in range(1200):  # 6,000 total samples
                    review_text = await self._generate_performance_review(level)
                    
                    performance_data.append({
                        "review_text": review_text,
                        "performance_level": level,
                        "label": performance_levels.index(level),
                        "score": self._level_to_score(level),
                        "improvement_areas": await self._extract_improvement_areas(review_text),
                        "strengths": await self._extract_strengths(review_text)
                    })
            
            return Dataset.from_pandas(pd.DataFrame(performance_data))
            
        except Exception as e:
            logger.error(f"Performance dataset generation error: {str(e)}")
            raise

    async def train_all_models(self, datasets: Dict[str, Dataset]):
        """Train all HR models using advanced techniques"""
        try:
            logger.info("Starting comprehensive model training...")
            
            # Initialize Weights & Biases for experiment tracking
            wandb.init(project="hr-ai-system", name=f"training-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            
            training_results = {}
            
            # Train Resume Classifier
            logger.info("Training Resume Classifier...")
            training_results["resume_classifier"] = await self._train_classification_model(
                datasets["resume_classifier"], "resume_classifier"
            )
            
            # Train Interview Agent
            logger.info("Training Interview Agent...")
            training_results["interview_agent"] = await self._train_generative_model(
                datasets["interview_agent"], "interview_agent"
            )
            
            # Train Sentiment Analyzer
            logger.info("Training Sentiment Analyzer...")
            training_results["sentiment_analyzer"] = await self._train_classification_model(
                datasets["sentiment_analyzer"], "sentiment_analyzer"
            )
            
            # Train Performance Predictor
            logger.info("Training Performance Predictor...")
            training_results["performance_predictor"] = await self._train_classification_model(
                datasets["performance_predictor"], "performance_predictor"
            )
            
            # Save all models
            await self._save_all_models(training_results)
            
            wandb.finish()
            
            logger.info("All model training completed successfully")
            return training_results
            
        except Exception as e:
            logger.error(f"Model training error: {str(e)}")
            raise

    async def _train_classification_model(self, dataset: Dataset, model_config: str):
        """Train classification model with QLoRA"""
        try:
            # Setup model for this specific task
            await self.setup_model_and_tokenizer(model_config)
            
            # Tokenize dataset
            def tokenize_function(examples):
                return self.tokenizer(
                    examples["text"],
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                    return_tensors="pt"
                )
            
            tokenized_dataset = dataset.map(tokenize_function, batched=True)
            
            # Split dataset
            train_dataset = tokenized_dataset.select(range(int(0.8 * len(tokenized_dataset))))
            eval_dataset = tokenized_dataset.select(range(int(0.8 * len(tokenized_dataset)), len(tokenized_dataset)))
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=f"./models/{model_config}",
                num_train_epochs=3,
                per_device_train_batch_size=4,
                per_device_eval_batch_size=4,
                gradient_accumulation_steps=4,
                warmup_steps=100,
                learning_rate=2e-4,
                fp16=True,
                logging_steps=10,
                evaluation_strategy="steps",
                eval_steps=100,
                save_steps=500,
                save_total_limit=2,
                load_best_model_at_end=True,
                metric_for_best_model="eval_accuracy",
                greater_is_better=True,
                report_to="wandb",
                dataloader_pin_memory=False,
                gradient_checkpointing=True,
                optim="paged_adamw_8bit"
            )
            
            # Custom trainer with metrics
            trainer = Trainer(
                model=self.peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=self.tokenizer,
                compute_metrics=self._compute_classification_metrics
            )
            
            # Train model
            trainer.train()
            
            # Evaluate model
            eval_results = trainer.evaluate()
            
            # Save model
            trainer.save_model()
            
            return {
                "model_path": f"./models/{model_config}",
                "eval_results": eval_results,
                "training_completed": True
            }
            
        except Exception as e:
            logger.error(f"Classification model training error: {str(e)}")
            raise

    async def _train_generative_model(self, dataset: Dataset, model_config: str):
        """Train generative model for interview conversations"""
        try:
            # Setup model for generative task
            await self.setup_model_and_tokenizer(model_config)
            
            # Prepare dataset for causal language modeling
            def tokenize_function(examples):
                return self.tokenizer(
                    examples["conversation"],
                    truncation=True,
                    padding="max_length",
                    max_length=1024,
                    return_tensors="pt"
                )
            
            tokenized_dataset = dataset.map(tokenize_function, batched=True)
            
            # Data collator for language modeling
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
            
            # Split dataset
            train_dataset = tokenized_dataset.select(range(int(0.8 * len(tokenized_dataset))))
            eval_dataset = tokenized_dataset.select(range(int(0.8 * len(tokenized_dataset)), len(tokenized_dataset)))
            
            # Training arguments for generative model
            training_args = TrainingArguments(
                output_dir=f"./models/{model_config}",
                num_train_epochs=2,
                per_device_train_batch_size=2,
                per_device_eval_batch_size=2,
                gradient_accumulation_steps=8,
                warmup_steps=200,
                learning_rate=1e-4,
                fp16=True,
                logging_steps=20,
                evaluation_strategy="steps",
                eval_steps=200,
                save_steps=1000,
                save_total_limit=2,
                report_to="wandb",
                dataloader_pin_memory=False,
                gradient_checkpointing=True,
                optim="paged_adamw_8bit"
            )
            
            # Trainer for generative model
            trainer = Trainer(
                model=self.peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer
            )
            
            # Train model
            trainer.train()
            
            # Save model
            trainer.save_model()
            
            return {
                "model_path": f"./models/{model_config}",
                "training_completed": True
            }
            
        except Exception as e:
            logger.error(f"Generative model training error: {str(e)}")
            raise

    def _compute_classification_metrics(self, eval_pred):
        """Compute metrics for classification tasks"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        accuracy = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='weighted')
        
        return {
            "accuracy": accuracy,
            "f1": f1
        }

    async def _generate_resume_text(self, category: str, experience: int, education: str, skills: List[str]) -> str:
        """Generate realistic resume text using AI"""
        try:
            import openai
            
            prompt = f"""
            Generate a realistic resume for a {category} position with:
            - {experience} years of experience
            - {education} degree
            - Skills: {', '.join(skills)}
            
            Include: Professional summary, work experience, education, skills, and achievements.
            Make it realistic and detailed (300-500 words).
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume writer creating realistic professional resumes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Resume text generation error: {str(e)}")
            return f"Sample resume for {category} with {experience} years experience and {education} education."

    async def _generate_interview_conversation(self, interview_type: str, difficulty: str) -> Dict[str, Any]:
        """Generate realistic interview conversation"""
        try:
            import openai
            
            prompt = f"""
            Generate a realistic {interview_type} interview conversation for a {difficulty} level position.
            Include:
            - 5-8 questions and detailed answers
            - Natural conversation flow
            - Realistic candidate responses
            - Technical depth appropriate for {difficulty} level
            
            Format as a conversation between Interviewer and Candidate.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are creating realistic interview conversations for HR training."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.8
            )
            
            conversation_text = response.choices[0].message.content.strip()
            
            # Generate score and feedback
            score = np.random.randint(60, 95) if difficulty in ["senior", "principal"] else np.random.randint(50, 85)
            
            return {
                "text": conversation_text,
                "score": score,
                "feedback": f"Candidate demonstrated {difficulty}-level competency in {interview_type} skills.",
                "recommendation": "hire" if score > 75 else "maybe" if score > 60 else "no_hire"
            }
            
        except Exception as e:
            logger.error(f"Interview conversation generation error: {str(e)}")
            return {
                "text": f"Sample {interview_type} interview for {difficulty} level.",
                "score": 70,
                "feedback": "Standard interview performance.",
                "recommendation": "maybe"
            }

    async def _generate_workplace_communication(self, sentiment: str, comm_type: str) -> str:
        """Generate workplace communication with specific sentiment"""
        try:
            import openai
            
            sentiment_prompts = {
                "positive": "enthusiastic, optimistic, and encouraging",
                "negative": "frustrated, disappointed, or critical",
                "neutral": "factual, professional, and balanced",
                "frustrated": "showing clear frustration or annoyance",
                "excited": "showing enthusiasm and energy",
                "concerned": "expressing worry or concern",
                "satisfied": "showing contentment and approval"
            }
            
            prompt = f"""
            Write a realistic workplace {comm_type} that is {sentiment_prompts[sentiment]}.
            Make it authentic and professional, 50-150 words.
            Include specific workplace context and realistic details.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are writing realistic workplace communications."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Workplace communication generation error: {str(e)}")
            return f"Sample {comm_type} with {sentiment} sentiment."

    async def _generate_performance_review(self, level: str) -> str:
        """Generate performance review text"""
        try:
            import openai
            
            level_descriptions = {
                "exceptional": "outstanding performance, exceeds all expectations",
                "exceeds": "consistently exceeds expectations and goals",
                "meets": "meets expectations and performs well",
                "below": "below expectations, needs improvement",
                "unsatisfactory": "unsatisfactory performance, significant issues"
            }
            
            prompt = f"""
            Write a realistic performance review for an employee with {level_descriptions[level]}.
            Include specific examples, achievements, areas for improvement, and goals.
            Make it detailed and professional (200-300 words).
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an HR manager writing detailed performance reviews."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Performance review generation error: {str(e)}")
            return f"Sample performance review for {level} performance level."

    def _level_to_score(self, level: str) -> float:
        """Convert performance level to numeric score"""
        level_scores = {
            "exceptional": 95,
            "exceeds": 85,
            "meets": 75,
            "below": 60,
            "unsatisfactory": 40
        }
        return level_scores.get(level, 75)

    async def _extract_improvement_areas(self, review_text: str) -> List[str]:
        """Extract improvement areas from review text"""
        # Simple keyword-based extraction (could be enhanced with NLP)
        improvement_keywords = [
            "improve", "develop", "enhance", "strengthen", "focus on", "work on"
        ]
        
        areas = []
        for keyword in improvement_keywords:
            if keyword in review_text.lower():
                areas.append(f"Area requiring {keyword}")
        
        return areas[:3]  # Return top 3

    async def _extract_strengths(self, review_text: str) -> List[str]:
        """Extract strengths from review text"""
        # Simple keyword-based extraction
        strength_keywords = [
            "excellent", "outstanding", "strong", "exceptional", "skilled", "proficient"
        ]
        
        strengths = []
        for keyword in strength_keywords:
            if keyword in review_text.lower():
                strengths.append(f"Strength in {keyword} performance")
        
        return strengths[:3]  # Return top 3

    async def _save_all_models(self, training_results: Dict[str, Any]):
        """Save all trained models"""
        try:
            logger.info("Saving all trained models...")
            
            for model_name, results in training_results.items():
                if results.get("training_completed"):
                    model_path = results["model_path"]
                    
                    # Save additional metadata
                    metadata = {
                        "model_name": model_name,
                        "training_date": datetime.now().isoformat(),
                        "eval_results": results.get("eval_results", {}),
                        "model_path": model_path
                    }
                    
                    with open(f"{model_path}/metadata.json", "w") as f:
                        json.dump(metadata, f, indent=2)
            
            logger.info("All models saved successfully")
            
        except Exception as e:
            logger.error(f"Model saving error: {str(e)}")
            raise

# Additional imports for QLoRA
from transformers import BitsAndBytesConfig
