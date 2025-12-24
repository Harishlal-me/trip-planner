"""
data/data_preprocessor.py
Data Preprocessing for ML Training
Clean and prepare Kaggle datasets for model training
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import re
from sklearn.preprocessing import LabelEncoder, StandardScaler


class DataPreprocessor:
    """
    Preprocess tourism and travel datasets for ML training.
    Handles missing values, outliers, encoding, and normalization.
    """
    
    def __init__(self):
        """Initialize preprocessor."""
        self.label_encoders = {}
        self.scalers = {}
        self.feature_stats = {}
    
    def preprocess_destinations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess destination/places dataset.
        
        Args:
            df: Raw destinations DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        print("🧹 Preprocessing destinations data...")
        
        df_clean = df.copy()
        
        # 1. Handle missing values
        df_clean = self._handle_missing_values(df_clean)
        
        # 2. Clean text columns
        text_columns = df_clean.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(self._clean_text)
        
        # 3. Extract features from descriptions
        if 'description' in df_clean.columns or 'Description' in df_clean.columns:
            desc_col = 'description' if 'description' in df_clean.columns else 'Description'
            df_clean['description_length'] = df_clean[desc_col].str.len().fillna(0)
            df_clean['word_count'] = df_clean[desc_col].str.split().str.len().fillna(0)
        
        # 4. Standardize ratings
        df_clean = self._standardize_ratings(df_clean)
        
        # 5. Remove duplicates
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['name'] if 'name' in df_clean.columns else None)
        removed = initial_count - len(df_clean)
        if removed > 0:
            print(f"   🗑️  Removed {removed} duplicate records")
        
        print(f"   ✅ Processed {len(df_clean)} destination records")
        
        return df_clean
    
    def preprocess_budget(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess budget/pricing dataset.
        
        Args:
            df: Raw budget DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        print("🧹 Preprocessing budget data...")
        
        df_clean = df.copy()
        
        # 1. Handle missing values
        df_clean = self._handle_missing_values(df_clean)
        
        # 2. Detect and clean price columns
        price_columns = self._detect_price_columns(df_clean)
        
        for col in price_columns:
            # Remove currency symbols and convert to float
            df_clean[col] = df_clean[col].apply(self._extract_price)
            
            # Remove outliers
            df_clean = self._remove_outliers(df_clean, col)
        
        # 3. Standardize location names
        location_columns = ['location', 'city', 'state', 'country', 'destination']
        for col in location_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].apply(self._clean_text)
                df_clean[col] = df_clean[col].str.title()
        
        # 4. Create duration features if dates exist
        df_clean = self._extract_duration_features(df_clean)
        
        print(f"   ✅ Processed {len(df_clean)} budget records")
        
        return df_clean
    
    def preprocess_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess reviews/ratings dataset.
        
        Args:
            df: Raw reviews DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        print("🧹 Preprocessing reviews data...")
        
        df_clean = df.copy()
        
        # 1. Handle missing values
        df_clean = self._handle_missing_values(df_clean)
        
        # 2. Clean review text
        if 'review' in df_clean.columns or 'Review' in df_clean.columns:
            review_col = 'review' if 'review' in df_clean.columns else 'Review'
            df_clean[review_col] = df_clean[review_col].apply(self._clean_review_text)
            df_clean['review_length'] = df_clean[review_col].str.len()
        
        # 3. Standardize ratings (1-5 scale)
        df_clean = self._standardize_ratings(df_clean)
        
        # 4. Extract sentiment features
        if 'review' in df_clean.columns:
            df_clean['sentiment_score'] = df_clean['review'].apply(self._simple_sentiment)
        
        print(f"   ✅ Processed {len(df_clean)} review records")
        
        return df_clean
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values appropriately."""
        # Numeric columns: fill with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Categorical columns: fill with mode or 'Unknown'
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().sum() > 0:
                mode_value = df[col].mode()
                if len(mode_value) > 0:
                    df[col].fillna(mode_value[0], inplace=True)
                else:
                    df[col].fillna('Unknown', inplace=True)
        
        return df
    
    def _clean_text(self, text: str) -> str:
        """Clean text data."""
        if pd.isna(text):
            return ''
        
        text = str(text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s,.\-]', '', text)
        
        return text.strip()
    
    def _clean_review_text(self, text: str) -> str:
        """Clean review text more thoroughly."""
        if pd.isna(text):
            return ''
        
        text = str(text).lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove emails
        text = re.sub(r'\S+@\S+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _extract_price(self, value) -> float:
        """Extract numeric price from text."""
        if pd.isna(value):
            return 0.0
        
        # If already numeric
        if isinstance(value, (int, float)):
            return float(value)
        
        # Extract numbers from string
        value = str(value)
        numbers = re.findall(r'\d+\.?\d*', value)
        
        if numbers:
            return float(numbers[0])
        
        return 0.0
    
    def _detect_price_columns(self, df: pd.DataFrame) -> List[str]:
        """Detect columns containing price/cost data."""
        price_keywords = ['price', 'cost', 'budget', 'rate', 'fare', 'fee', 'amount']
        price_columns = []
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in price_keywords):
                price_columns.append(col)
        
        return price_columns
    
    def _standardize_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize rating columns to 0-5 scale."""
        rating_columns = [col for col in df.columns if 'rating' in col.lower() or 'score' in col.lower()]
        
        for col in rating_columns:
            if col in df.columns:
                # Check current scale
                max_val = df[col].max()
                
                if max_val > 5:
                    # Scale to 0-5
                    df[col] = (df[col] / max_val) * 5
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame, column: str, threshold: float = 3.0) -> pd.DataFrame:
        """Remove outliers using Z-score method."""
        if column not in df.columns:
            return df
        
        mean = df[column].mean()
        std = df[column].std()
        
        if std == 0:
            return df
        
        z_scores = np.abs((df[column] - mean) / std)
        
        initial_count = len(df)
        df = df[z_scores < threshold]
        removed = initial_count - len(df)
        
        if removed > 0:
            print(f"   🗑️  Removed {removed} outliers from {column}")
        
        return df
    
    def _extract_duration_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract duration features from date columns."""
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        
        if len(date_columns) >= 2:
            try:
                df[date_columns[0]] = pd.to_datetime(df[date_columns[0]], errors='coerce')
                df[date_columns[1]] = pd.to_datetime(df[date_columns[1]], errors='coerce')
                
                df['duration_days'] = (df[date_columns[1]] - df[date_columns[0]]).dt.days
                df['duration_days'] = df['duration_days'].clip(lower=1)
            except:
                pass
        
        return df
    
    def _simple_sentiment(self, text: str) -> float:
        """Simple sentiment scoring based on keywords."""
        if pd.isna(text) or text == '':
            return 0.5
        
        text = str(text).lower()
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'best', 'love', 'beautiful']
        negative_words = ['bad', 'poor', 'terrible', 'worst', 'horrible', 'awful', 'disappointing']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.5
        
        return pos_count / total
    
    def encode_categorical(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Encode categorical columns."""
        df_encoded = df.copy()
        
        for col in columns:
            if col in df_encoded.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_encoded[col] = self.label_encoders[col].fit_transform(df_encoded[col].astype(str))
                else:
                    df_encoded[col] = self.label_encoders[col].transform(df_encoded[col].astype(str))
        
        return df_encoded
    
    def scale_features(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Scale numeric features."""
        df_scaled = df.copy()
        
        for col in columns:
            if col in df_scaled.columns:
                if col not in self.scalers:
                    self.scalers[col] = StandardScaler()
                    df_scaled[col] = self.scalers[col].fit_transform(df_scaled[[col]])
                else:
                    df_scaled[col] = self.scalers[col].transform(df_scaled[[col]])
        
        return df_scaled
    
    def create_train_test_split(
        self,
        df: pd.DataFrame,
        target_column: str,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Create train-test split."""
        from sklearn.model_selection import train_test_split
        
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    print("✅ Data Preprocessor - Ready!")