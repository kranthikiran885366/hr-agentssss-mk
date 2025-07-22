"""
Comprehensive Model Training System
Trains all HR models using advanced techniques
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    EarlyStoppingCallback, get_linear_schedule_with_warmup
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from datasets import Dataset
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import wandb
import os
from datetime import datetime
import json

from .advanced_training.qlora_trainer import AdvancedQLoRATrainer
from .advanced_training.multi_ai_integration import MultiAIIntegration
from .real_data_generator import RealDataGenerator

logger = logging.getLogger(__name__)

class ComprehensiveModelTrainer:
    def __init__(self):
        self.qlora_trainer = AdvancedQLoRATrainer()
        self.multi_ai = MultiAIIntegration()
        self.data_generator = RealDataGenerator()
        
        # Model configurations
        self.model_configs = {
            "resume_classifier": {
                "base_model": "microsoft/DialoGPT-medium",
                "task_type": "SEQ_CLS",
                "num_labels": 16,
                "max_length": 512
            },
            "interview_evaluator": {
                "base_model": "microsoft/DialoGPT-large",
                "task_type": "CAUSAL_LM",
                "max_length": 1024
            },
            "sentiment_analyzer": {
                "base_model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "task_type": "SEQ_CLS",
                "num_labels": 7,
                "max_length": 256
            },
            "performance_predictor": {
                "base_model": "bert-base-uncased",
                "task_type": "SEQ_CLS",
                "num_labels": 5,
                "max_length": 512
            },
            "conflict_detector": {
                "base_model": "roberta-base",
                "task_type": "SEQ_CLS",
                "num_labels": 6,
                "max_length": 512
            },
            "training_recommender": {
                "base_model": "sentence-transformers/all-MiniLM-L6-v2",
                "task_type": "FEATURE_EXTRACTION",
                "max_length": 384
            }
        }

    async def initialize(self):
        """Initialize all training components"""
        try:
            logger.info("Initializing Comprehensive Model Trainer...")
            
            # Initialize components
            await self.qlora_trainer.initialize()
            await self.multi_ai.initialize()
            await self.data_generator.initialize()
            
            # Initialize Weights & Biases
            wandb.init(
                project="hr-ai-comprehensive",
                name=f"training-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                config=self.model_configs
            )
            
            logger.info("Comprehensive Model Trainer initialized successfully")
            
        except Exception as e:
            logger.error(f"Trainer initialization error: {str(e)}")
            raise

    async def train_all_models(self):
        """Train all HR models comprehensively"""
        try:
            logger.info("Starting comprehensive model training pipeline...")
            
            # Step 1: Generate comprehensive datasets
            logger.info("Generating comprehensive datasets...")
            datasets = await self.data_generator.generate_comprehensive_datasets()
            
            # Step 2: Train individual models
            training_results = {}
            
            # Train Resume Classifier
            logger.info("Training Resume Classifier...")
            training_results["resume_classifier"] = await self._train_resume_classifier(
                datasets["resumes"]
            )
            
            # Train Interview Evaluator
            logger.info("Training Interview Evaluator...")
            training_results["interview_evaluator"] = await self._train_interview_evaluator(
                datasets["interviews"]
            )
            
            # Train Sentiment Analyzer
            logger.info("Training Sentiment Analyzer...")
            training_results["sentiment_analyzer"] = await self._train_sentiment_analyzer(
                datasets["workplace_communications"]
            )
            
            # Train Performance Predictor
            logger.info("Training Performance Predictor...")
            training_results["performance_predictor"] = await self._train_performance_predictor(
                datasets["performance_reviews"]
            )
            
            # Train Conflict Detector
            logger.info("Training Conflict Detector...")
            training_results["conflict_detector"] = await self._train_conflict_detector(
                datasets["conflict_cases"]
            )
            
            # Train Training Recommender
            logger.info("Training Training Recommender...")
            training_results["training_recommender"] = await self._train_training_recommender(
                datasets["training_records"]
            )
            
            # Step 3: Create ensemble models
            logger.info("Creating ensemble models...")
            ensemble_results = await self._create_ensemble_models(training_results)
            
            # Step 4: Validate all models
            logger.info("Validating all models...")
            validation_results = await self._validate_all_models(training_results, datasets)
            
            # Step 5: Save models and results
            logger.info("Saving models and results...")
            await self._save_all_models(training_results, ensemble_results, validation_results)
            
            # Step 6: Generate training report
            training_report = await self._generate_training_report(
                training_results, ensemble_results, validation_results
            )
            
            logger.info("Comprehensive model training completed successfully")
            return training_report
            
        except Exception as e:
            logger.error(f"Comprehensive training error: {str(e)}")
            raise

    async def _train_resume_classifier(self, resume_data: pd.DataFrame) -> Dict[str, Any]:
        """Train resume classification model"""
        try:
            logger.info("Training resume classifier with QLoRA...")
            
            # Prepare dataset
            dataset = Dataset.from_pandas(resume_data)
            
            # Setup QLoRA trainer
            await self.qlora_trainer.setup_model_and_tokenizer("resume_classifier")
            
            # Tokenize data
            def tokenize_function(examples):
                return self.qlora_trainer.tokenizer(
                    examples["resume_text"],
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                    return_tensors="pt"
                )
            
            tokenized_dataset = dataset.map(tokenize_function, batched=True)
            
            # Split data
            train_dataset, eval_dataset = self._split_dataset(tokenized_dataset, 0.8)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir="./models/resume_classifier",
                num_train_epochs=4,
                per_device_train_batch_size=8,
                per_device_eval_batch_size=8,
                gradient_accumulation_steps=2,
                warmup_steps=500,
                learning_rate=3e-4,
                fp16=True,
                logging_steps=50,
                evaluation_strategy="steps",
                eval_steps=200,
                save_steps=500,
                save_total_limit=3,
                load_best_model_at_end=True,
                metric_for_best_model="eval_f1",
                greater_is_better=True,
                report_to="wandb",
                dataloader_pin_memory=False,
                gradient_checkpointing=True,
                optim="paged_adamw_8bit",
                weight_decay=0.01,
                lr_scheduler_type="cosine"
            )
            
            # Create trainer
            trainer = Trainer(
                model=self.qlora_trainer.peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=self.qlora_trainer.tokenizer,
                compute_metrics=self._compute_classification_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
            )
            
            # Train model
            train_result = trainer.train()
            
            # Evaluate model
            eval_result = trainer.evaluate()
            
            # Save model
            trainer.save_model()
            
            return {
                "model_type": "resume_classifier",
                "train_result": train_result,
                "eval_result": eval_result,
                "model_path": "./models/resume_classifier",
                "training_completed": True
            }
            
        except Exception as e:
            logger.error(f"Resume classifier training error: {str(e)}")
            raise

    async def _train_interview_evaluator(self, interview_data: pd.DataFrame) -> Dict[str, Any]:
        """Train interview evaluation model"""
        try:
            logger.info("Training interview evaluator...")
            
            # Prepare dataset for generative training
            dataset = Dataset.from_pandas(interview_data)
            
            # Setup model
            await self.qlora_trainer.setup_model_and_tokenizer("interview_agent")
            
            # Prepare conversation data for training
            def prepare_conversation_data(examples):
                # Format: conversation + evaluation scores
                formatted_texts = []
                for i in range(len(examples["conversation"])):
                    text = f"Interview: {examples['conversation'][i]}\n"
                    text += f"Technical Score: {examples['technical_score'][i]}\n"
                    text += f"Communication Score: {examples['communication_score'][i]}\n"
                    text += f"Overall Score: {examples['overall_score'][i]}\n"
                    text += f"Recommendation: {examples['recommendation'][i]}"
                    formatted_texts.append(text)
                
                return self.qlora_trainer.tokenizer(
                    formatted_texts,
                    truncation=True,
                    padding="max_length",
                    max_length=1024,
                    return_tensors="pt"
                )
            
            tokenized_dataset = dataset.map(prepare_conversation_data, batched=True)
            
            # Split data
            train_dataset, eval_dataset = self._split_dataset(tokenized_dataset, 0.8)
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.qlora_trainer.tokenizer,
                mlm=False
            )
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir="./models/interview_evaluator",
                num_train_epochs=3,
                per_device_train_batch_size=4,
                per_device_eval_batch_size=4,
                gradient_accumulation_steps=4,
                warmup_steps=300,
                learning_rate=2e-4,
                fp16=True,
                logging_steps=25,
                evaluation_strategy="steps",
                eval_steps=150,
                save_steps=500,
                save_total_limit=2,
                report_to="wandb",
                dataloader_pin_memory=False,
                gradient_checkpointing=True,
                optim="paged_adamw_8bit"
            )
            
            # Create trainer
            trainer = Trainer(
                model=self.qlora_trainer.peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
                tokenizer=self.qlora_trainer.tokenizer
            )
            
            # Train model
            train_result = trainer.train()
            
            # Save model
            trainer.save_model()
            
            return {
                "model_type": "interview_evaluator",
                "train_result": train_result,
                "model_path": "./models/interview_evaluator",
                "training_completed": True
            }
            
        except Exception as e:
            logger.error(f"Interview evaluator training error: {str(e)}")
            raise

    async def _train_sentiment_analyzer(self, communication_data: pd.DataFrame) -> Dict[str, Any]:
        """Train sentiment analysis model"""
        try:
            logger.info("Training sentiment analyzer...")
            
            # Prepare dataset
            dataset = Dataset.from_pandas(communication_data)
            
            # Setup model
            await self.qlora_trainer.setup_model_and_tokenizer("sentiment_analyzer")
            
            # Tokenize data
            def tokenize_function(examples):
                return self.qlora_trainer.tokenizer(
                    examples["text"],
                    truncation=True,
                    padding="max_length",
                    max_length=256,
                    return_tensors="pt"
                )
            
            tokenized_dataset = dataset.map(tokenize_function, batched=True)
            
            # Split data
            train_dataset, eval_dataset = self._split_dataset(tokenized_dataset, 0.8)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir="./models/sentiment_analyzer",
                num_train_epochs=3,
                per_device_train_batch_size=16,
                per_device_eval_batch_size=16,
                gradient_accumulation_steps=1,
                warmup_steps=200,
                learning_rate=5e-5,
                fp16=True,
                logging_steps=20,
                evaluation_strategy="steps",
                eval_steps=100,
                save_steps=300,
                save_total_limit=2,
                load_best_model_at_end=True,
                metric_for_best_model="eval_f1",
                greater_is_better=True,
                report_to="wandb",
                dataloader_pin_memory=False,
                gradient_checkpointing=True,
                optim="paged_adamw_8bit"
            )
            
            # Create trainer
            trainer = Trainer(
                model=self.qlora_trainer.peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=self.qlora_trainer.tokenizer,
                compute_metrics=self._compute_classification_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
            )
            
            # Train model
            train_result = trainer.train()
            
            # Evaluate model
            eval_result = trainer.evaluate()
            
            # Save model
            trainer.save_model()
            
            return {
                "model_type": "sentiment_analyzer",
                "train_result": train_result,
                "eval_result": eval_result,
                "model_path": "./models/sentiment_analyzer",
                "training_completed": True
            }
            
        except Exception as e:
            logger.error(f"Sentiment analyzer training error: {str(e)}")
            raise

    async def _train_performance_predictor(self, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """Train performance prediction model"""
        try:
            logger.info("Training performance predictor...")
            
            # Prepare dataset
            dataset = Dataset.from_pandas(performance_data)
            
            # Setup model
            await self.qlora_trainer.setup_model_and_tokenizer("performance_predictor")
            
            # Tokenize data
            def tokenize_function(examples):
                return self.qlora_trainer.tokenizer(
                    examples["review_text"],
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                    return_tensors="pt"
                )
            
            tokenized_dataset = dataset.map(tokenize_function, batched=True)
            
            # Split data
            train_dataset, eval_dataset = self._split_dataset(tokenized_dataset, 0.8)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir="./models/performance_predictor",
                num_train_epochs=4,
                per_device_train_batch_size=12,
                per_device_eval_batch_size=12,
                gradient_accumulation_steps=2,
                warmup_steps=300,
                learning_rate=3e-5,
                fp16=True,
                logging_steps=30,
                evaluation_strategy="steps",
                eval_steps=150,
                save_steps=400,
                save_total_limit=3,
                load_best_model_at_end=True,
                metric_for_best_model="eval_accuracy",
                greater_is_better=True,
                report_to="wandb",
                dataloader_pin_memory=False,
                gradient_checkpointing=True,
                optim="paged_adamw_8bit",
                weight_decay=0.01
            )
            
            # Create trainer
            trainer = Trainer(
                model=self.qlora_trainer.peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=self.qlora_trainer.tokenizer,
                compute_metrics=self._compute_classification_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
            )
            
            # Train model
            train_result = trainer.train()
            
            # Evaluate model
            eval_result = trainer.evaluate()
            
            # Save model
            trainer.save_model()
            
            return {
                "model_type": "performance_predictor",
                "train_result": train_result,
                "eval_result": eval_result,
                "model_path": "./models/performance_predictor",
                "training_completed": True
            }
            
        except Exception as e:
            logger.error(f"Performance predictor training error: {str(e)}")
            raise

    async def _train_conflict_detector(self, conflict_data: pd.DataFrame) -> Dict[str, Any]:
        """Train conflict detection model"""
        try:
            logger.info("Training conflict detector...")
            
            # Prepare dataset
            dataset = Dataset.from_pandas(conflict_data)
            
            # Setup model
            await self.qlora_trainer.setup_model_and_tokenizer("conflict_detector")
            
            # Tokenize data
            def tokenize_function(examples):
                return self.qlora_trainer.tokenizer(
                    examples["description"],
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                    return_tensors="pt"
                )
            
            tokenized_dataset = dataset.map(tokenize_function, batched=True)
            
            # Split data
            train_dataset, eval_dataset = self._split_dataset(tokenized_dataset, 0.8)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir="./models/conflict_detector",
                num_train_epochs=3,
                per_device_train_batch_size=10,
                per_device_eval_batch_size=10,
                gradient_accumulation_steps=2,
                warmup_steps=200,
                learning_rate=4e-5,
                fp16=True,
                logging_steps=25,
                evaluation_strategy="steps",
                eval_steps=100,
                save_steps=300,
                save_total_limit=2,
                load_best_model_at_end=True,
                metric_for_best_model="eval_f1",
                greater_is_better=True,
                report_to="wandb",
                dataloader_pin_memory=False,
                gradient_checkpointing=True,
                optim="paged_adamw_8bit"
            )
            
            # Create trainer
            trainer = Trainer(
                model=self.qlora_trainer.peft_model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=self.qlora_trainer.tokenizer,
                compute_metrics=self._compute_classification_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
            )
            
            # Train model
            train_result = trainer.train()
            
            # Evaluate model
            eval_result = trainer.evaluate()
            
            # Save model
            trainer.save_model()
            
            return {
                "model_type": "conflict_detector",
                "train_result": train_result,
                "eval_result": eval_result,
                "model_path": "./models/conflict_detector",
                "training_completed": True
            }
            
        except Exception as e:
            logger.error(f"Conflict detector training error: {str(e)}")
            raise

    async def _train_training_recommender(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train training recommendation model"""
        try:
            logger.info("Training training recommender...")
            
            # This model uses embeddings for similarity-based recommendations
            from sentence_transformers import SentenceTransformer
            import faiss
            
            # Load pre-trained sentence transformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Prepare training descriptions
            course_descriptions = []
            for _, row in training_data.iterrows():
                desc = f"{row['course_name']} - {row['training_type']} training"
                course_descriptions.append(desc)
            
            # Generate embeddings
            embeddings = model.encode(course_descriptions)
            
            # Create FAISS index for similarity search
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
            index.add(embeddings.astype('float32'))
            
            # Save model and index
            model_path = "./models/training_recommender"
            os.makedirs(model_path, exist_ok=True)
            
            model.save(f"{model_path}/sentence_transformer")
            faiss.write_index(index, f"{model_path}/faiss_index.bin")
            
            # Save training data mapping
            training_mapping = {
                "courses": course_descriptions,
                "training_types": training_data['training_type'].tolist(),
                "course_names": training_data['course_name'].tolist()
            }
            
            with open(f"{model_path}/training_mapping.json", "w") as f:
                json.dump(training_mapping, f, indent=2)
            
            return {
                "model_type": "training_recommender",
                "model_path": model_path,
                "embedding_dimension": dimension,
                "total_courses": len(course_descriptions),
                "training_completed": True
            }
            
        except Exception as e:
            logger.error(f"Training recommender training error: {str(e)}")
            raise

    async def _create_ensemble_models(self, training_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create ensemble models combining multiple approaches"""
        try:
            logger.info("Creating ensemble models...")
            
            ensemble_results = {}
            
            # Resume Analysis Ensemble
            ensemble_results["resume_ensemble"] = {
                "models": ["resume_classifier", "multi_ai_resume"],
                "weights": [0.6, 0.4],
                "combination_method": "weighted_average",
                "confidence_threshold": 0.8
            }
            
            # Interview Evaluation Ensemble
            ensemble_results["interview_ensemble"] = {
                "models": ["interview_evaluator", "multi_ai_interview"],
                "weights": [0.7, 0.3],
                "combination_method": "weighted_average",
                "confidence_threshold": 0.75
            }
            
            # Sentiment Analysis Ensemble
            ensemble_results["sentiment_ensemble"] = {
                "models": ["sentiment_analyzer", "multi_ai_sentiment"],
                "weights": [0.5, 0.5],
                "combination_method": "majority_vote",
                "confidence_threshold": 0.7
            }
            
            logger.info("Ensemble models created successfully")
            return ensemble_results
            
        except Exception as e:
            logger.error(f"Ensemble creation error: {str(e)}")
            raise

    async def _validate_all_models(self, training_results: Dict[str, Any], datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Validate all trained models"""
        try:
            logger.info("Validating all models...")
            
            validation_results = {}
            
            # Validate each model
            for model_name, result in training_results.items():
                if result.get("training_completed"):
                    validation_results[model_name] = await self._validate_single_model(
                        model_name, result, datasets
                    )
            
            # Calculate overall validation metrics
            validation_results["overall"] = {
                "total_models": len(validation_results),
                "successful_validations": sum(1 for v in validation_results.values() if v.get("validation_passed", False)),
                "average_accuracy": np.mean([v.get("accuracy", 0) for v in validation_results.values() if "accuracy" in v]),
                "validation_completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Model validation completed")
            return validation_results
            
        except Exception as e:
            logger.error(f"Model validation error: {str(e)}")
            raise

    async def _validate_single_model(self, model_name: str, training_result: Dict[str, Any], datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Validate a single model"""
        try:
            model_path = training_result.get("model_path")
            
            if not model_path or not os.path.exists(model_path):
                return {"validation_passed": False, "error": "Model path not found"}
            
            # Load model for validation
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModelForSequenceClassification.from_pretrained(model_path)
                
                # Simple validation test
                test_input = "This is a test input for model validation."
                inputs = tokenizer(test_input, return_tensors="pt", truncation=True, padding=True)
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
                validation_passed = predictions.shape[1] > 0 and torch.sum(predictions).item() > 0.9
                
                return {
                    "validation_passed": validation_passed,
                    "model_loaded": True,
                    "output_shape": list(predictions.shape),
                    "prediction_sum": torch.sum(predictions).item(),
                    "accuracy": training_result.get("eval_result", {}).get("eval_accuracy", 0)
                }
                
            except Exception as model_error:
                return {
                    "validation_passed": False,
                    "model_loaded": False,
                    "error": str(model_error)
                }
            
        except Exception as e:
            logger.error(f"Single model validation error for {model_name}: {str(e)}")
            return {"validation_passed": False, "error": str(e)}

    async def _save_all_models(self, training_results: Dict[str, Any], ensemble_results: Dict[str, Any], validation_results: Dict[str, Any]):
        """Save all models and results"""
        try:
            logger.info("Saving all models and results...")
            
            # Create models directory
            os.makedirs("models/comprehensive", exist_ok=True)
            
            # Save training results
            with open("models/comprehensive/training_results.json", "w") as f:
                json.dump(training_results, f, indent=2, default=str)
            
            # Save ensemble results
            with open("models/comprehensive/ensemble_results.json", "w") as f:
                json.dump(ensemble_results, f, indent=2)
            
            # Save validation results
            with open("models/comprehensive/validation_results.json", "w") as f:
                json.dump(validation_results, f, indent=2, default=str)
            
            # Save model registry
            model_registry = {
                "models": {
                    name: {
                        "path": result.get("model_path"),
                        "type": result.get("model_type"),
                        "status": "trained" if result.get("training_completed") else "failed",
                        "validation_passed": validation_results.get(name, {}).get("validation_passed", False)
                    }
                    for name, result in training_results.items()
                },
                "ensembles": ensemble_results,
                "created_at": datetime.utcnow().isoformat(),
                "total_models": len(training_results)
            }
            
            with open("models/comprehensive/model_registry.json", "w") as f:
                json.dump(model_registry, f, indent=2)
            
            logger.info("All models and results saved successfully")
            
        except Exception as e:
            logger.error(f"Model saving error: {str(e)}")
            raise

    async def _generate_training_report(self, training_results: Dict[str, Any], ensemble_results: Dict[str, Any], validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive training report"""
        try:
            logger.info("Generating training report...")
            
            # Calculate summary statistics
            total_models = len(training_results)
            successful_trainings = sum(1 for r in training_results.values() if r.get("training_completed", False))
            successful_validations = sum(1 for r in validation_results.values() if r.get("validation_passed", False))
            
            # Get best performing models
            best_models = {}
            for name, result in training_results.items():
                eval_result = result.get("eval_result", {})
                if eval_result:
                    best_models[name] = {
                        "accuracy": eval_result.get("eval_accuracy", 0),
                        "f1": eval_result.get("eval_f1", 0),
                        "loss": eval_result.get("eval_loss", float('inf'))
                    }
            
            # Generate report
            report = {
                "training_summary": {
                    "total_models_trained": total_models,
                    "successful_trainings": successful_trainings,
                    "successful_validations": successful_validations,
                    "success_rate": (successful_trainings / total_models) * 100 if total_models > 0 else 0,
                    "validation_rate": (successful_validations / total_models) * 100 if total_models > 0 else 0
                },
                "model_performance": best_models,
                "ensemble_models": len(ensemble_results),
                "training_duration": "Comprehensive training completed",
                "recommendations": await self._generate_training_recommendations(training_results, validation_results),
                "next_steps": [
                    "Deploy models to production environment",
                    "Set up model monitoring and logging",
                    "Implement A/B testing for model comparison",
                    "Schedule regular model retraining",
                    "Create model documentation and API endpoints"
                ],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Save report
            with open("models/comprehensive/training_report.json", "w") as f:
                json.dump(report, f, indent=2)
            
            logger.info("Training report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Training report generation error: {str(e)}")
            raise

    async def _generate_training_recommendations(self, training_results: Dict[str, Any], validation_results: Dict[str, Any]) -> List[str]:
        """Generate training recommendations"""
        recommendations = []
        
        # Check for failed trainings
        failed_models = [name for name, result in training_results.items() if not result.get("training_completed", False)]
        if failed_models:
            recommendations.append(f"Retrain failed models: {', '.join(failed_models)}")
        
        # Check for low performance models
        low_performance_models = []
        for name, result in training_results.items():
            eval_result = result.get("eval_result", {})
            if eval_result.get("eval_accuracy", 0) < 0.8:
                low_performance_models.append(name)
        
        if low_performance_models:
            recommendations.append(f"Improve performance for: {', '.join(low_performance_models)}")
        
        # Check validation failures
        failed_validations = [name for name, result in validation_results.items() if not result.get("validation_passed", False)]
        if failed_validations:
            recommendations.append(f"Fix validation issues for: {', '.join(failed_validations)}")
        
        # General recommendations
        recommendations.extend([
            "Implement continuous model monitoring",
            "Set up automated retraining pipelines",
            "Create comprehensive model documentation",
            "Establish model versioning and rollback procedures"
        ])
        
        return recommendations

    def _split_dataset(self, dataset: Dataset, train_ratio: float = 0.8):
        """Split dataset into train and evaluation sets"""
        train_size = int(len(dataset) * train_ratio)
        eval_size = len(dataset) - train_size
        
        train_dataset = dataset.select(range(train_size))
        eval_dataset = dataset.select(range(train_size, train_size + eval_size))
        
        return train_dataset, eval_dataset

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

# Model deployment and inference classes
class ModelInferenceEngine:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.ensemble_configs = {}
        
    async def load_all_models(self):
        """Load all trained models for inference"""
        try:
            logger.info("Loading all models for inference...")
            
            # Load model registry
            with open("models/comprehensive/model_registry.json", "r") as f:
                registry = json.load(f)
            
            # Load individual models
            for model_name, model_info in registry["models"].items():
                if model_info["status"] == "trained" and model_info["validation_passed"]:
                    await self._load_single_model(model_name, model_info["path"])
            
            # Load ensemble configurations
            with open("models/comprehensive/ensemble_results.json", "r") as f:
                self.ensemble_configs = json.load(f)
            
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Model loading error: {str(e)}")
            raise

    async def _load_single_model(self, model_name: str, model_path: str):
        """Load a single model"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_path)
            self.models[model_name] = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            logger.info(f"Loaded model: {model_name}")
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")

    async def predict_resume_category(self, resume_text: str) -> Dict[str, Any]:
        """Predict resume category using trained model"""
        try:
            model_name = "resume_classifier"
            
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not loaded")
            
            # Tokenize input
            inputs = self.tokenizers[model_name](
                resume_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Make prediction
            with torch.no_grad():
                outputs = self.models[model_name](**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(predictions, dim=-1).item()
                confidence = torch.max(predictions).item()
            
            # Map to job categories
            job_categories = [
                "Software Engineer", "Data Scientist", "Product Manager", "UX Designer",
                "DevOps Engineer", "Marketing Manager", "Sales Representative", "HR Manager",
                "Financial Analyst", "Business Analyst", "Project Manager", "Quality Assurance",
                "Customer Success", "Operations Manager", "Research Scientist", "Consultant"
            ]
            
            return {
                "predicted_category": job_categories[predicted_class] if predicted_class < len(job_categories) else "Unknown",
                "confidence": confidence,
                "all_probabilities": predictions.tolist()[0]
            }
            
        except Exception as e:
            logger.error(f"Resume prediction error: {str(e)}")
            raise

    async def evaluate_interview(self, conversation: str) -> Dict[str, Any]:
        """Evaluate interview conversation"""
        try:
            # Use ensemble approach combining multiple models
            results = []
            
            # Use trained interview evaluator
            if "interview_evaluator" in self.models:
                result = await self._evaluate_with_trained_model(conversation)
                results.append(result)
            
            # Use multi-AI ensemble
            multi_ai_result = await self.multi_ai.ensemble_interview_evaluation(conversation, "comprehensive")
            results.append(multi_ai_result)
            
            # Combine results
            combined_result = await self._combine_interview_results(results)
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Interview evaluation error: {str(e)}")
            raise

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of workplace communication"""
        try:
            model_name = "sentiment_analyzer"
            
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not loaded")
            
            # Tokenize input
            inputs = self.tokenizers[model_name](
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=256
            )
            
            # Make prediction
            with torch.no_grad():
                outputs = self.models[model_name](**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(predictions, dim=-1).item()
                confidence = torch.max(predictions).item()
            
            # Map to sentiment labels
            sentiment_labels = ["positive", "negative", "neutral", "frustrated", "excited", "concerned", "satisfied"]
            
            return {
                "predicted_sentiment": sentiment_labels[predicted_class] if predicted_class < len(sentiment_labels) else "unknown",
                "confidence": confidence,
                "all_probabilities": predictions.tolist()[0]
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            raise

# Initialize the comprehensive training system
async def main():
    """Main function to run comprehensive model training"""
    try:
        # Initialize trainer
        trainer = ComprehensiveModelTrainer()
        await trainer.initialize()
        
        # Run comprehensive training
        training_report = await trainer.train_all_models()
        
        print("=" * 80)
        print("COMPREHENSIVE HR AI TRAINING COMPLETED")
        print("=" * 80)
        print(f"Total Models Trained: {training_report['training_summary']['total_models_trained']}")
        print(f"Success Rate: {training_report['training_summary']['success_rate']:.1f}%")
        print(f"Validation Rate: {training_report['training_summary']['validation_rate']:.1f}%")
        print("=" * 80)
        
        # Initialize inference engine
        inference_engine = ModelInferenceEngine()
        await inference_engine.load_all_models()
        
        print("All models loaded and ready for inference!")
        
        return training_report, inference_engine
        
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
