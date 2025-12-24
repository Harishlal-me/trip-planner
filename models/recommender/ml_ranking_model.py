"""
ML-Based Ranking Model for Travel Recommendations
Uses trained models to rank destinations
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple
import pickle
import joblib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLRankingModel:
    """Machine Learning model for ranking travel destinations"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def train(self, X: pd.DataFrame, y: pd.Series, model_type: str = 'gbm'):
        """
        Train the ranking model
        
        Args:
            X: Feature matrix
            y: Target scores (higher = better)
            model_type: 'gbm' or 'rf'
        """
        logger.info(f"Training {model_type} ranking model...")
        
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
        else:  # random forest
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        logger.info("Model training complete")
        
        # Feature importance
        importances = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        logger.info("\nTop 10 Important Features:")
        logger.info(feature_importance.head(10))
        
        return self.model
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict scores for places"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load a trained model.")
        
        # Ensure same features
        X = X[self.feature_names]
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def rank_places(self, 
                    places_df: pd.DataFrame,
                    user_features: Dict,
                    top_k: int = 10) -> List[Dict]:
        """
        Rank places for a user
        
        Args:
            places_df: DataFrame with place features
            user_features: User preference features
            top_k: Number of top places to return
        
        Returns:
            List of ranked places with scores
        """
        if not self.is_trained:
            logger.warning("Model not trained, using fallback scoring")
            return self._fallback_ranking(places_df, user_features, top_k)
        
        # Add user features to each place
        for key, value in user_features.items():
            places_df[key] = value
        
        # Predict scores
        try:
            scores = self.predict(places_df)
            places_df['ml_score'] = scores
        except Exception as e:
            logger.error(f"Prediction error: {e}, using fallback")
            return self._fallback_ranking(places_df, user_features, top_k)
        
        # Sort by score
        ranked_df = places_df.sort_values('ml_score', ascending=False).head(top_k)
        
        # Convert to list of dicts
        results = []
        for _, row in ranked_df.iterrows():
            results.append({
                'place_id': row.get('place_id', row.name),
                'name': row.get('name', 'Unknown'),
                'score': float(row['ml_score']),
                'rating': row.get('rating', 0),
                'category': row.get('category', 'Unknown'),
                'price_level': row.get('price_level', 2)
            })
        
        return results
    
    def _fallback_ranking(self, 
                         places_df: pd.DataFrame,
                         user_features: Dict,
                         top_k: int) -> List[Dict]:
        """Fallback ranking when model is not available"""
        
        # Simple scoring based on available features
        df = places_df.copy()
        
        # Base quality score
        df['score'] = df.get('rating', 4.0) / 5.0
        
        # Boost by popularity
        if 'reviews_count' in df.columns:
            df['score'] += np.log1p(df['reviews_count']) / 10
        
        # Budget compatibility
        user_budget = user_features.get('budget_encoded', 2)
        if 'price_level' in df.columns:
            df['budget_penalty'] = abs(df['price_level'] - user_budget) * 0.1
            df['score'] -= df['budget_penalty']
        
        # Interest matching
        user_interests = [k.replace('interest_', '') for k, v in user_features.items() 
                         if k.startswith('interest_') and v == 1]
        
        if 'category' in df.columns and user_interests:
            category_interest_map = {
                'museum': ['culture', 'history'],
                'restaurant': ['food'],
                'park': ['nature', 'relaxation'],
                'beach': ['beach', 'relaxation'],
                'shopping': ['shopping'],
                'nightlife': ['nightlife'],
                'attraction': ['culture', 'adventure']
            }
            
            def interest_boost(category):
                cat_interests = category_interest_map.get(category.lower(), [])
                matches = len(set(user_interests) & set(cat_interests))
                return matches * 0.2
            
            df['score'] += df['category'].apply(interest_boost)
        
        # Sort and return top k
        ranked_df = df.sort_values('score', ascending=False).head(top_k)
        
        results = []
        for _, row in ranked_df.iterrows():
            results.append({
                'place_id': row.get('place_id', row.name),
                'name': row.get('name', 'Unknown'),
                'score': float(row['score']),
                'rating': row.get('rating', 0),
                'category': row.get('category', 'Unknown'),
                'price_level': row.get('price_level', 2)
            })
        
        return results
    
    def save(self, model_name: str = "ranking_model"):
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
    
    def load(self, model_name: str = "ranking_model"):
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
        
        importances = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return feature_importance
    
    def explain_prediction(self, place_features: pd.Series) -> Dict:
        """
        Explain why a place was ranked the way it was
        
        Args:
            place_features: Features for a single place
        
        Returns:
            Dictionary with explanation
        """
        if not self.is_trained:
            return {'error': 'Model not trained'}
        
        # Get feature contributions
        X = place_features[self.feature_names].values.reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        score = self.model.predict(X_scaled)[0]
        
        # Get feature importance
        feature_importance = self.get_feature_importance()
        top_features = feature_importance.head(5)
        
        explanation = {
            'predicted_score': float(score),
            'top_contributing_features': []
        }
        
        for _, row in top_features.iterrows():
            feat_name = row['feature']
            feat_value = place_features.get(feat_name, 0)
            explanation['top_contributing_features'].append({
                'feature': feat_name,
                'value': float(feat_value),
                'importance': float(row['importance'])
            })
        
        return explanation


class EnsembleRankingModel:
    """Ensemble of multiple ranking models"""
    
    def __init__(self):
        self.models = []
        self.weights = []
    
    def add_model(self, model: MLRankingModel, weight: float = 1.0):
        """Add a model to the ensemble"""
        self.models.append(model)
        self.weights.append(weight)
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict using ensemble"""
        if not self.models:
            raise ValueError("No models in ensemble")
        
        # Normalize weights
        weights = np.array(self.weights)
        weights = weights / weights.sum()
        
        # Get predictions from all models
        predictions = []
        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Weighted average
        ensemble_pred = np.average(predictions, axis=0, weights=weights)
        
        return ensemble_pred
    
    def rank_places(self,
                   places_df: pd.DataFrame,
                   user_features: Dict,
                   top_k: int = 10) -> List[Dict]:
        """Rank places using ensemble"""
        
        # Get predictions from all models
        scores_list = []
        for model in self.models:
            if model.is_trained:
                scores = model.predict(places_df)
                scores_list.append(scores)
        
        if not scores_list:
            # Fallback to first model
            return self.models[0].rank_places(places_df, user_features, top_k)
        
        # Weighted average
        weights = np.array(self.weights[:len(scores_list)])
        weights = weights / weights.sum()
        
        ensemble_scores = np.average(scores_list, axis=0, weights=weights)
        places_df['ensemble_score'] = ensemble_scores
        
        # Sort and return
        ranked_df = places_df.sort_values('ensemble_score', ascending=False).head(top_k)
        
        results = []
        for _, row in ranked_df.iterrows():
            results.append({
                'place_id': row.get('place_id', row.name),
                'name': row.get('name', 'Unknown'),
                'score': float(row['ensemble_score']),
                'rating': row.get('rating', 0),
                'category': row.get('category', 'Unknown'),
                'price_level': row.get('price_level', 2)
            })
        
        return results


def example_usage():
    """Example usage of MLRankingModel with proper saving"""
    
    logger.info("=" * 60)
    logger.info("TRAINING ML RANKING MODEL")
    logger.info("=" * 60)
    
    # Create sample training data
    n_samples = 1000
    n_features = 10
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    # Create target (places with higher feature_0 are better)
    y = X['feature_0'] * 2 + X['feature_1'] + np.random.randn(n_samples) * 0.1
    
    # Train model
    model = MLRankingModel()
    model.train(X, y, model_type='gbm')
    
    logger.info("\n" + "=" * 60)
    logger.info("SAVING MODEL")
    logger.info("=" * 60)
    
    # Save model - this is the key step!
    success = model.save('gbm_model')
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("LOADING AND TESTING SAVED MODEL")
        logger.info("=" * 60)
        
        # Create a new model instance and load the saved model
        loaded_model = MLRankingModel()
        loaded_model.load('gbm_model')
        
        # Make predictions with loaded model
        predictions = loaded_model.predict(X.head(10))
        logger.info(f"Predictions from loaded model: {predictions[:5]}")
        
        # Feature importance
        importance = loaded_model.get_feature_importance()
        logger.info("\nTop 5 Feature Importance:")
        logger.info(importance.head(5))
    else:
        logger.error("Failed to save model!")


if __name__ == "__main__":
    example_usage()