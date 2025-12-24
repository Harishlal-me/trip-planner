"""
Model Training Pipeline
Orchestrates the training of ranking and budget models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import logging
from pathlib import Path
from typing import Dict
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Orchestrates model training pipeline"""
    
    def __init__(self, output_dir: str = "trained_models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.training_history = []
    
    def train_ranking_model(self, places_df: pd.DataFrame, 
                           interactions_df: pd.DataFrame,
                           model_type: str = 'gbm',
                           test_size: float = 0.2) -> Dict:
        """
        Train the ranking model
        
        Args:
            places_df: Place features
            interactions_df: User-place interactions
                Required columns: user_id, place_id, interaction_type, rating
            model_type: 'gbm' or 'rf'
            test_size: Test set proportion
        
        Returns:
            Training results and metrics
        """
        logger.info("="*60)
        logger.info("Starting ranking model training...")
        logger.info("="*60)
        
        from models.recommender.ml_ranking_model import MLRankingModel
        from data.feature_engineering import FeatureEngineer
        
        # Create features
        engineer = FeatureEngineer()
        X, y = engineer.create_training_dataset(places_df, interactions_df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Train model
        model = MLRankingModel()
        model.train(X_train, y_train, model_type=model_type)
        
        # Evaluate
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        
        metrics = {
            "model_type": "ranking",
            "algorithm": model_type,
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "train_rmse": float(train_rmse),
            "test_rmse": float(test_rmse),
            "train_mae": float(train_mae),
            "test_mae": float(test_mae),
            "n_features": len(X.columns),
            "n_train_samples": len(X_train),
            "n_test_samples": len(X_test),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("\nRanking Model Performance:")
        logger.info(f"Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
        logger.info(f"Train RMSE: {train_rmse:.4f}, Test RMSE: {test_rmse:.4f}")
        
        # Save model using the correct method
        logger.info("\n" + "="*60)
        logger.info("Saving ranking model...")
        logger.info("="*60)
        try:
            success = model.save('ranking_model')
            if success:
                logger.info("✓ Ranking model saved successfully")
            else:
                logger.error("✗ Failed to save ranking model")
        except Exception as e:
            logger.error(f"✗ Error saving ranking model: {e}")
            raise
        
        # Save metrics
        metrics_path = self.output_dir / "ranking_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"✓ Metrics saved to {metrics_path}")
        
        self.training_history.append(metrics)
        
        return {
            "model": model,
            "metrics": metrics,
            "feature_importance": model.get_feature_importance()
        }
    
    def train_budget_model(self, trip_data_df: pd.DataFrame,
                          model_type: str = 'rf',
                          test_size: float = 0.2) -> Dict:
        """
        Train the budget prediction model
        
        Args:
            trip_data_df: Trip data with features and costs
                Required columns: num_days, num_people, accommodation_level,
                                 destination_cost_index, total_cost
            model_type: 'rf', 'gbm', or 'ridge'
            test_size: Test set proportion
        
        Returns:
            Training results and metrics
        """
        logger.info("="*60)
        logger.info("Starting budget model training...")
        logger.info("="*60)
        
        from models.budget_prediction.ml_budget_model import MLBudgetModel
        
        # Separate features and target
        feature_cols = [col for col in trip_data_df.columns if col != 'total_cost']
        X = trip_data_df[feature_cols]
        y = trip_data_df['total_cost']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Train model
        model = MLBudgetModel()
        model.train(X_train, y_train, model_type=model_type)
        
        # Evaluate
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        
        # MAPE
        train_mape = np.mean(np.abs((y_train - train_pred) / y_train)) * 100
        test_mape = np.mean(np.abs((y_test - test_pred) / y_test)) * 100
        
        metrics = {
            "model_type": "budget",
            "algorithm": model_type,
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "train_rmse": float(train_rmse),
            "test_rmse": float(test_rmse),
            "train_mae": float(train_mae),
            "test_mae": float(test_mae),
            "train_mape": float(train_mape),
            "test_mape": float(test_mape),
            "n_features": len(X.columns),
            "n_train_samples": len(X_train),
            "n_test_samples": len(X_test),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("\nBudget Model Performance:")
        logger.info(f"Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
        logger.info(f"Test MAPE: {test_mape:.2f}%")
        
        # Save model using the correct method
        logger.info("\n" + "="*60)
        logger.info("Saving budget model...")
        logger.info("="*60)
        try:
            success = model.save('budget_model')
            if success:
                logger.info("✓ Budget model saved successfully")
            else:
                logger.error("✗ Failed to save budget model")
        except Exception as e:
            logger.error(f"✗ Error saving budget model: {e}")
            raise
        
        # Save metrics
        metrics_path = self.output_dir / "budget_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"✓ Metrics saved to {metrics_path}")
        
        self.training_history.append(metrics)
        
        return {
            "model": model,
            "metrics": metrics
        }
    
    def create_synthetic_training_data(self) -> Dict:
        """
        Create synthetic training data for demonstration
        (Use real Kaggle data in production)
        """
        logger.info("Creating synthetic training data...")
        
        # Synthetic place data
        n_places = 1000
        places_df = pd.DataFrame({
            'place_id': range(n_places),
            'name': [f'Place_{i}' for i in range(n_places)],
            'category': np.random.choice(['museum', 'restaurant', 'park', 'beach', 'shopping'], n_places),
            'rating': np.random.uniform(3.5, 5.0, n_places),
            'reviews_count': np.random.randint(10, 5000, n_places),
            'price_level': np.random.randint(1, 5, n_places),
            'latitude': np.random.uniform(40.0, 41.0, n_places),
            'longitude': np.random.uniform(-74.0, -73.0, n_places),
            'city': ['New York'] * n_places,
            'country': ['USA'] * n_places
        })
        
        # Synthetic interaction data
        n_interactions = 5000
        interactions_df = pd.DataFrame({
            'user_id': np.random.randint(1, 200, n_interactions),
            'place_id': np.random.randint(0, n_places, n_interactions),
            'interaction_type': np.random.choice(['view', 'save', 'visit'], n_interactions, p=[0.6, 0.3, 0.1]),
            'rating': np.random.uniform(3.0, 5.0, n_interactions),
            'timestamp': pd.date_range('2023-01-01', periods=n_interactions, freq='h')
        })
        
        # Synthetic trip data for budget model
        n_trips = 2000
        trip_data_df = pd.DataFrame({
            'num_days': np.random.randint(2, 15, n_trips),
            'num_people': np.random.randint(1, 6, n_trips),
            'accommodation_level': np.random.randint(1, 6, n_trips),
            'destination_cost_index': np.random.uniform(0.5, 2.0, n_trips),
            'season_multiplier': np.random.uniform(0.8, 1.4, n_trips)
        })
        
        # Calculate synthetic total cost
        trip_data_df['total_cost'] = (
            trip_data_df['num_days'] * 
            trip_data_df['num_people'] * 
            (50 + trip_data_df['accommodation_level'] * 30) * 
            trip_data_df['destination_cost_index'] * 
            trip_data_df['season_multiplier']
        ) + np.random.normal(0, 100, n_trips)
        
        logger.info(f"Created {len(places_df)} places, {len(interactions_df)} interactions, {len(trip_data_df)} trips")
        
        return {
            'places_df': places_df,
            'interactions_df': interactions_df,
            'trip_data_df': trip_data_df
        }
    
    def train_all_models(self):
        """Train both ranking and budget models"""
        logger.info("="*60)
        logger.info("TRAINING ALL MODELS")
        logger.info("="*60)
        
        # Create synthetic data
        data = self.create_synthetic_training_data()
        
        # Train ranking model
        logger.info("\n")
        ranking_results = self.train_ranking_model(
            data['places_df'],
            data['interactions_df'],
            model_type='gbm'
        )
        
        # Train budget model
        logger.info("\n")
        budget_results = self.train_budget_model(
            data['trip_data_df'],
            model_type='rf'
        )
        
        logger.info("\n" + "="*60)
        logger.info("TRAINING COMPLETE!")
        logger.info("="*60)
        logger.info(f"\nModels saved in: {self.output_dir}")
        logger.info("\nModel Performance Summary:")
        logger.info(f"Ranking Model Test R²: {ranking_results['metrics']['test_r2']:.4f}")
        logger.info(f"Budget Model Test R²: {budget_results['metrics']['test_r2']:.4f}")
        logger.info(f"Budget Model Test MAPE: {budget_results['metrics']['test_mape']:.2f}%")
        
        return {
            'ranking': ranking_results,
            'budget': budget_results
        }


if __name__ == "__main__":
    # Train models
    trainer = ModelTrainer()
    results = trainer.train_all_models()
    
    print("\n✅ Training completed successfully!")
    print(f"📁 Models saved in: trained_models/")
    print("\nYou can now use these models in your API!")