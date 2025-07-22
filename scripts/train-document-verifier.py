"""
Document Verification ML Model Training Script
This script trains a machine learning model to verify document authenticity
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib
import cv2
import os
from PIL import Image
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentVerifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def extract_features(self, image_path):
        """Extract features from document image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not load image: {image_path}")
                return None
                
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract features
            features = []
            
            # Image quality metrics
            features.append(cv2.Laplacian(gray, cv2.CV_64F).var())  # Sharpness
            features.append(np.mean(gray))  # Brightness
            features.append(np.std(gray))   # Contrast
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            features.append(np.sum(edges > 0))  # Edge density
            
            # Texture analysis using Local Binary Pattern
            features.extend(self._calculate_lbp_features(gray))
            
            # Document structure features
            features.extend(self._analyze_document_structure(gray))
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Error extracting features from {image_path}: {e}")
            return None
    
    def _calculate_lbp_features(self, gray_image):
        """Calculate Local Binary Pattern features"""
        # Simplified LBP implementation
        h, w = gray_image.shape
        lbp_features = []
        
        # Calculate LBP for center region
        center_region = gray_image[h//4:3*h//4, w//4:3*w//4]
        lbp_features.append(np.mean(center_region))
        lbp_features.append(np.std(center_region))
        
        return lbp_features
    
    def _analyze_document_structure(self, gray_image):
        """Analyze document structure and layout"""
        features = []
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        horizontal_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, vertical_kernel)
        
        features.append(np.sum(horizontal_lines > 0))
        features.append(np.sum(vertical_lines > 0))
        
        # Text region detection (simplified)
        text_regions = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        features.append(np.sum(text_regions == 0) / text_regions.size)  # Text density
        
        return features
    
    def prepare_training_data(self, data_dir):
        """Prepare training data from document images"""
        features_list = []
        labels_list = []
        
        # Process authentic documents
        authentic_dir = os.path.join(data_dir, 'authentic')
        if os.path.exists(authentic_dir):
            for filename in os.listdir(authentic_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                    image_path = os.path.join(authentic_dir, filename)
                    features = self.extract_features(image_path)
                    if features is not None:
                        features_list.append(features)
                        labels_list.append(1)  # Authentic
        
        # Process fake documents
        fake_dir = os.path.join(data_dir, 'fake')
        if os.path.exists(fake_dir):
            for filename in os.listdir(fake_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                    image_path = os.path.join(fake_dir, filename)
                    features = self.extract_features(image_path)
                    if features is not None:
                        features_list.append(features)
                        labels_list.append(0)  # Fake
        
        if not features_list:
            logger.error("No training data found!")
            return None, None
            
        return np.array(features_list), np.array(labels_list)
    
    def train(self, data_dir):
        """Train the document verification model"""
        logger.info("Preparing training data...")
        X, y = self.prepare_training_data(data_dir)
        
        if X is None or len(X) == 0:
            logger.error("No training data available!")
            return False
        
        logger.info(f"Training with {len(X)} samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        logger.info("Training model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        return True
    
    def verify_document(self, image_path):
        """Verify a single document"""
        features = self.extract_features(image_path)
        if features is None:
            return None, 0.0
        
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict(features_scaled)[0]
        confidence = self.model.predict_proba(features_scaled)[0].max()
        
        return bool(prediction), confidence
    
    def save_model(self, model_path):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }
        joblib.dump(model_data, model_path)
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path):
        """Load a trained model"""
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        logger.info(f"Model loaded from {model_path}")

def main():
    """Main training function"""
    # Initialize verifier
    verifier = DocumentVerifier()
    
    # Training data directory structure:
    # ml/datasets/documents/
    #   ├── authentic/
    #   │   ├── passport1.jpg
    #   │   ├── license1.jpg
    #   │   └── ...
    #   └── fake/
    #       ├── fake_passport1.jpg
    #       ├── fake_license1.jpg
    #       └── ...
    
    data_dir = "ml/datasets/documents"
    
    # Create sample data directories if they don't exist
    os.makedirs(os.path.join(data_dir, "authentic"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "fake"), exist_ok=True)
    
    # Train the model
    if verifier.train(data_dir):
        # Save the model
        model_path = "ml/models/document_verifier.pkl"
        os.makedirs("ml/models", exist_ok=True)
        verifier.save_model(model_path)
        
        logger.info("Document verification model training completed successfully!")
    else:
        logger.error("Model training failed!")

if __name__ == "__main__":
    main()
