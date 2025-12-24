"""
ML-Based Budget Prediction Model
Predicts trip costs based on features
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from typing import Dict
import joblib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLBudgetModel:
    """Machine Learning model for budget prediction"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        
        if model_path and Path(model_path).exists():
            self.load(model_path)
    
    def train(self, X: pd.DataFrame, y: pd.Series, model_type: str = 'rf'):
        """
        Train the budget prediction model
        
        Args:
            X: Feature matrix
            y: Target costs
            model_type: 'rf', 'gbm', or 'ridge'
        """
        logger.info(f"Training {model_type} budget model...")
        
        # Store feature names
        self.feature_names = list(X.columns)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        if model_type == 'gbm':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
                subsample=0.8
            )
        elif model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        else:  # random forest (default)
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        logger.info("Model training complete")
        
        # Feature importance (if available)
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            logger.info("\nTop 10 Important Features:")
            logger.info(feature_importance.head(10))
        
        return self.model
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict budget for trips"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load a trained model.")
        
        # Ensure same features
        X = X[self.feature_names]
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def predict_trip_budget(self, trip_features: Dict) -> float:
        """
        Predict budget for a specific trip
        
        Args:
            trip_features: Dictionary with trip features
        
        Returns:
            Predicted budget
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        # Create DataFrame from features
        df = pd.DataFrame([trip_features])
        
        # Ensure all required features are present
        for feat in self.feature_names:
            if feat not in df.columns:
                df[feat] = 0
        
        # Select only required features
        df = df[self.feature_names]
        
        # Predict
        prediction = self.predict(df)[0]
        
        return float(prediction)
    
    def save(self, model_name: str = "budget_model"):
        """
        Save trained model using joblib
        
        Args:
            model_name: Name for the saved model files
        """
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        save_dir = Path("trained_models")
        save_dir.mkdir(exist_ok=True, parents=True)
        
        # Save model and scaler separately using joblib
        model_path = save_dir / f"{model_name}.joblib"
        scaler_path = save_dir / f"{model_name}_scaler.joblib"
        features_path = save_dir / f"{model_name}_features.joblib"
        
        try:
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            joblib.dump(self.feature_names, features_path)
            
            logger.info(f"✓ Model saved to {model_path}")
            logger.info(f"✓ Scaler saved to {scaler_path}")
            logger.info(f"✓ Features saved to {features_path}")
            
            # Verify files exist
            if model_path.exists() and scaler_path.exists() and features_path.exists():
                logger.info("✓ All files verified to exist!")
                return True
            else:
                logger.error("✗ Files were not saved properly")
                return False
        except Exception as e:
            logger.error(f"✗ Error saving model: {e}")
            return False
    
    def load(self, model_name: str = "budget_model"):
        """
        Load trained model using joblib
        
        Args:
            model_name: Name of the saved model files
        """
        save_dir = Path("trained_models")
        
        model_path = save_dir / f"{model_name}.joblib"
        scaler_path = save_dir / f"{model_name}_scaler.joblib"
        features_path = save_dir / f"{model_name}_features.joblib"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_names = joblib.load(features_path)
            self.is_trained = True
            
            logger.info(f"✓ Model loaded from {model_path}")
            logger.info(f"✓ Scaler loaded from {scaler_path}")
            logger.info(f"✓ Features loaded from {features_path}")
        except Exception as e:
            logger.error(f"✗ Error loading model: {e}")
            raise
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores"""
        if not self.is_trained:
            return pd.DataFrame()
        
        if not hasattr(self.model, 'feature_importances_'):
            logger.warning("This model type does not have feature importances")
            return pd.DataFrame()
        
        importances = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return feature_importance


def example_usage():
    """Example usage of MLBudgetModel"""
    
    logger.info("="*60)
    logger.info("TRAINING ML BUDGET MODEL")
    logger.info("="*60)
    
    # Create sample training data
    n_samples = 500
    X = pd.DataFrame({
        'num_days': np.random.randint(2, 15, n_samples),
        'num_people': np.random.randint(1, 6, n_samples),
        'accommodation_level': np.random.randint(1, 6, n_samples),
        'destination_cost_index': np.random.uniform(0.5, 2.0, n_samples),
        'season_multiplier': np.random.uniform(0.8, 1.4, n_samples)
    })
    
    # Create target
    y = (
        X['num_days'] * 
        X['num_people'] * 
        (50 + X['accommodation_level'] * 30) * 
        X['destination_cost_index'] * 
        X['season_multiplier']
    ) + np.random.normal(0, 100, n_samples)
    
    # Train model
    model = MLBudgetModel()
    model.train(X, y, model_type='rf')
    
    logger.info("\n" + "="*60)
    logger.info("SAVING MODEL")
    logger.info("="*60)
    
    # Save model
    success = model.save('budget_model')
    
    if success:
        logger.info("\n" + "="*60)
        logger.info("LOADING AND TESTING SAVED MODEL")
        logger.info("="*60)
        
        # Create a new model instance and load the saved model
        loaded_model = MLBudgetModel()
        loaded_model.load('budget_model')
        
        # Make predictions with loaded model
        predictions = loaded_model.predict(X.head(5))
        logger.info(f"Predictions from loaded model: {predictions}")
        
        # Feature importance
        importance = loaded_model.get_feature_importance()
        logger.info("\nTop 5 Feature Importance:")
        logger.info(importance.head(5))
        
        # Predict specific trip
        trip = {
            'num_days': 7,
            'num_people': 2,
            'accommodation_level': 4,
            'destination_cost_index': 1.2,
            'season_multiplier': 1.1
        }
        budget = loaded_model.predict_trip_budget(trip)
        logger.info(f"\nPredicted budget for trip: ${budget:.2f}")
    else:
        logger.error("Failed to save model!")


if __name__ == "__main__":
    example_usage()