"""
Feature Engineering for Trip Planner ML Models
Creates features from raw data for training
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Creates ML features from raw travel data"""
    
    def __init__(self):
        self.feature_names = []
        
    def create_place_features(self, places_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for places/destinations
        
        Expected columns in places_df:
        - place_id, name, category, rating, reviews_count, price_level,
          latitude, longitude, city, country
        """
        logger.info("Creating place features...")
        
        df = places_df.copy()
        
        # 1. Rating features
        if 'rating' not in df.columns:
            df['rating'] = 4.0  # default neutral rating

        df['rating_normalized'] = df['rating'] / 5.0
        df['has_rating'] = (df['rating'] > 0).astype(int)

        # 🔧 FIX 1: Encode rating_quality numerically
        df['rating_quality'] = pd.cut(
            df['rating'],
            bins=[0, 3, 4, 5],
            labels=[0, 1, 2]   # low=0, medium=1, high=2
        ).astype(int)

        # 2. Popularity features
        df['log_reviews'] = np.log1p(df['reviews_count'])
        df['popularity_score'] = df['rating'] * np.log1p(df['reviews_count'])
        df['is_popular'] = (df['reviews_count'] > df['reviews_count'].median()).astype(int)
        
        # 3. Price features
        df['price_level_normalized'] = df['price_level'] / 4.0
        df['is_budget_friendly'] = (df['price_level'] <= 2).astype(int)
        df['is_luxury'] = (df['price_level'] >= 3).astype(int)
        
        # 4. Category features (one-hot encoding)
        category_dummies = pd.get_dummies(df['category'], prefix='cat')
        df = pd.concat([df, category_dummies], axis=1)
        
        # 5. Geographic features
        df['lat_rounded'] = df['latitude'].round(2)
        df['lon_rounded'] = df['longitude'].round(2)
        
        # 6. Composite score
        df['quality_score'] = (
            df['rating_normalized'] * 0.4 +
            df['log_reviews'] / df['log_reviews'].max() * 0.3 +
            (5 - df['price_level']) / 4 * 0.3
        )
        
        logger.info(f"Created {len(df.columns) - len(places_df.columns)} new features")
        return df
    
    def create_user_features(self, user_prefs: Dict) -> Dict:
        """Create features from user preferences"""
        features = {}
        
        budget_map = {'low': 1, 'medium': 2, 'high': 3, 'luxury': 4}
        features['budget_encoded'] = budget_map.get(user_prefs.get('budget_level', 'medium'), 2)
        features['budget_normalized'] = features['budget_encoded'] / 4.0
        
        all_interests = [
            'culture', 'nature', 'food', 'adventure',
            'shopping', 'history', 'beach', 'nightlife', 'relaxation'
        ]
        user_interests = user_prefs.get('interests', [])
        for interest in all_interests:
            features[f'interest_{interest}'] = 1 if interest in user_interests else 0
        
        style_map = {'relaxed': 1, 'moderate': 2, 'packed': 3}
        features['travel_pace'] = style_map.get(user_prefs.get('travel_style', 'moderate'), 2)
        
        features['group_size'] = user_prefs.get('group_size', 1)
        features['is_solo'] = 1 if features['group_size'] == 1 else 0
        features['is_group'] = 1 if features['group_size'] >= 4 else 0
        
        return features
    
    def create_interaction_features(self, 
                                   places_df: pd.DataFrame,
                                   user_features: Dict) -> pd.DataFrame:
        """Create interaction features between user and places"""
        df = places_df.copy()
        
        user_budget = user_features['budget_encoded']
        df['budget_match'] = 1 - abs(df['price_level'] - user_budget) / 4.0
        
        user_interests = [
            k.replace('interest_', '') for k, v in user_features.items()
            if k.startswith('interest_') and v == 1
        ]
        
        def calculate_interest_match(category):
            category_interest_map = {
                'museum': ['culture', 'history'],
                'restaurant': ['food'],
                'park': ['nature', 'relaxation'],
                'beach': ['beach', 'relaxation'],
                'shopping': ['shopping'],
                'nightlife': ['nightlife'],
                'attraction': ['culture', 'adventure']
            }
            category_interests = category_interest_map.get(category.lower(), [])
            matches = len(set(user_interests) & set(category_interests))
            return matches / max(len(user_interests), 1)
        
        df['interest_match'] = df['category'].apply(calculate_interest_match)
        
        pace = user_features['travel_pace']
        if pace == 1:
            df['pace_match'] = df['category'].isin(['beach', 'park', 'spa']).astype(int)
        elif pace == 3:
            df['pace_match'] = df['category'].isin(['attraction', 'museum', 'shopping']).astype(int)
        else:
            df['pace_match'] = 0.5
        
        df['compatibility_score'] = (
            df['budget_match'] * 0.3 +
            df['interest_match'] * 0.4 +
            df['quality_score'] * 0.3
        )
        
        return df
    
    def create_training_dataset(self,
                               places_df: pd.DataFrame,
                               user_interactions_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Create full training dataset"""
        logger.info("Creating training dataset...")
        
        df = user_interactions_df.merge(places_df, on='place_id', how='left')
        df = self.create_place_features(df)
        
        interaction_weights = {'view': 1, 'save': 3, 'visit': 5}
        df['interaction_weight'] = df['interaction_type'].map(interaction_weights)
        df['target'] = df['rating'] * df['interaction_weight']
        
        feature_cols = [
            col for col in df.columns
            if col not in [
                'user_id', 'place_id', 'interaction_type', 'rating',
                'timestamp', 'name', 'city', 'country', 'category', 'target'
            ]
        ]
        
        # 🔧 FIX 2: Ensure all features are numeric
        X = df[feature_cols].astype(float)
        y = df['target']
        
        self.feature_names = feature_cols
        logger.info(f"Created dataset with {len(X)} samples and {len(feature_cols)} features")
        
        return X, y
