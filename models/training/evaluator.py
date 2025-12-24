"""
Model Evaluator
Comprehensive evaluation of trained models
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import logging
from typing import Dict, List
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate and analyze model performance"""
    
    def __init__(self, output_dir: str = "evaluation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def evaluate_ranking_model(self, model, X_test: pd.DataFrame, 
                               y_test: pd.Series) -> Dict:
        """
        Comprehensive evaluation of ranking model
        
        Args:
            model: Trained ranking model
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Evaluation metrics and insights
        """
        logger.info("Evaluating ranking model...")
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        
        # Calculate additional metrics
        correlation = np.corrcoef(y_test, y_pred)[0, 1]
        
        # Prediction accuracy at different thresholds
        errors = np.abs(y_test - y_pred)
        within_10_percent = np.mean(errors / y_test <= 0.1) * 100
        within_20_percent = np.mean(errors / y_test <= 0.2) * 100
        
        metrics = {
            "r2_score": float(r2),
            "rmse": float(rmse),
            "mae": float(mae),
            "correlation": float(correlation),
            "within_10_percent": float(within_10_percent),
            "within_20_percent": float(within_20_percent),
            "mean_prediction": float(np.mean(y_pred)),
            "std_prediction": float(np.std(y_pred)),
            "mean_actual": float(np.mean(y_test)),
            "std_actual": float(np.std(y_test))
        }
        
        logger.info("\nRanking Model Evaluation:")
        logger.info(f"R² Score: {r2:.4f}")
        logger.info(f"RMSE: {rmse:.4f}")
        logger.info(f"MAE: {mae:.4f}")
        logger.info(f"Predictions within 10%: {within_10_percent:.2f}%")
        logger.info(f"Predictions within 20%: {within_20_percent:.2f}%")
        
        # Save metrics
        metrics_path = self.output_dir / "ranking_evaluation.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def evaluate_budget_model(self, model, X_test: pd.DataFrame,
                             y_test: pd.Series) -> Dict:
        """
        Comprehensive evaluation of budget model
        
        Args:
            model: Trained budget model
            X_test: Test features
            y_test: Test labels (actual costs)
        
        Returns:
            Evaluation metrics and insights
        """
        logger.info("Evaluating budget model...")
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        # Median Absolute Percentage Error
        medape = np.median(np.abs((y_test - y_pred) / y_test)) * 100
        
        # Accuracy at different thresholds
        errors_pct = np.abs((y_test - y_pred) / y_test) * 100
        within_10_percent = np.mean(errors_pct <= 10) * 100
        within_15_percent = np.mean(errors_pct <= 15) * 100
        within_20_percent = np.mean(errors_pct <= 20) * 100
        
        # Overestimation vs Underestimation
        overestimations = np.sum(y_pred > y_test)
        underestimations = np.sum(y_pred < y_test)
        
        metrics = {
            "r2_score": float(r2),
            "rmse": float(rmse),
            "mae": float(mae),
            "mape": float(mape),
            "medape": float(medape),
            "within_10_percent": float(within_10_percent),
            "within_15_percent": float(within_15_percent),
            "within_20_percent": float(within_20_percent),
            "overestimations": int(overestimations),
            "underestimations": int(underestimations),
            "total_predictions": len(y_test),
            "mean_predicted_budget": float(np.mean(y_pred)),
            "mean_actual_budget": float(np.mean(y_test)),
            "bias": float(np.mean(y_pred - y_test))
        }
        
        logger.info("\nBudget Model Evaluation:")
        logger.info(f"R² Score: {r2:.4f}")
        logger.info(f"MAPE: {mape:.2f}%")
        logger.info(f"Within 10% accuracy: {within_10_percent:.2f}%")
        logger.info(f"Within 15% accuracy: {within_15_percent:.2f}%")
        logger.info(f"Within 20% accuracy: {within_20_percent:.2f}%")
        logger.info(f"Overestimations: {overestimations} ({overestimations/len(y_test)*100:.1f}%)")
        logger.info(f"Underestimations: {underestimations} ({underestimations/len(y_test)*100:.1f}%)")
        
        # Save metrics
        metrics_path = self.output_dir / "budget_evaluation.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def analyze_feature_importance(self, model, top_n: int = 15) -> pd.DataFrame:
        """
        Analyze and visualize feature importance
        
        Args:
            model: Trained model with feature_importances_
            top_n: Number of top features to show
        
        Returns:
            DataFrame with feature importance
        """
        if not hasattr(model, 'get_feature_importance'):
            logger.warning("Model doesn't support feature importance")
            return pd.DataFrame()
        
        importance_df = model.get_feature_importance().head(top_n)
        
        logger.info(f"\nTop {top_n} Most Important Features:")
        for idx, row in importance_df.iterrows():
            logger.info(f"{row['feature']}: {row['importance']:.4f}")
        
        return importance_df
    
    def analyze_prediction_errors(self, y_true: pd.Series, 
                                 y_pred: np.ndarray) -> Dict:
        """
        Analyze patterns in prediction errors
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
        
        Returns:
            Error analysis results
        """
        errors = y_pred - y_true
        abs_errors = np.abs(errors)
        pct_errors = (errors / y_true) * 100
        
        analysis = {
            "mean_error": float(np.mean(errors)),
            "std_error": float(np.std(errors)),
            "mean_abs_error": float(np.mean(abs_errors)),
            "median_abs_error": float(np.median(abs_errors)),
            "max_overestimation": float(np.max(errors)),
            "max_underestimation": float(np.min(errors)),
            "error_quartiles": {
                "25th": float(np.percentile(abs_errors, 25)),
                "50th": float(np.percentile(abs_errors, 50)),
                "75th": float(np.percentile(abs_errors, 75)),
                "90th": float(np.percentile(abs_errors, 90))
            }
        }
        
        logger.info("\nError Analysis:")
        logger.info(f"Mean Error (Bias): ${analysis['mean_error']:.2f}")
        logger.info(f"Mean Absolute Error: ${analysis['mean_abs_error']:.2f}")
        logger.info(f"Median Absolute Error: ${analysis['median_abs_error']:.2f}")
        
        return analysis
    
    def compare_models(self, models: Dict, X_test: pd.DataFrame,
                      y_test: pd.Series) -> pd.DataFrame:
        """
        Compare multiple models
        
        Args:
            models: Dictionary of model_name: model
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Comparison DataFrame
        """
        results = []
        
        for model_name, model in models.items():
            try:
                y_pred = model.predict(X_test)
                
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)
                
                results.append({
                    'model': model_name,
                    'r2_score': r2,
                    'rmse': rmse,
                    'mae': mae
                })
            except Exception as e:
                logger.error(f"Error evaluating {model_name}: {e}")
        
        comparison_df = pd.DataFrame(results)
        comparison_df = comparison_df.sort_values('r2_score', ascending=False)
        
        logger.info("\nModel Comparison:")
        logger.info(comparison_df.to_string())
        
        # Save comparison
        comparison_path = self.output_dir / "model_comparison.csv"
        comparison_df.to_csv(comparison_path, index=False)
        
        return comparison_df
    
    def generate_evaluation_report(self, model, X_test: pd.DataFrame,
                                   y_test: pd.Series, model_type: str) -> Dict:
        """
        Generate comprehensive evaluation report
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            model_type: 'ranking' or 'budget'
        
        Returns:
            Complete evaluation report
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"GENERATING EVALUATION REPORT FOR {model_type.upper()} MODEL")
        logger.info(f"{'='*60}")
        
        # Main evaluation
        if model_type == 'ranking':
            metrics = self.evaluate_ranking_model(model, X_test, y_test)
        else:
            metrics = self.evaluate_budget_model(model, X_test, y_test)
        
        # Feature importance
        feature_importance = self.analyze_feature_importance(model)
        
        # Error analysis
        y_pred = model.predict(X_test)
        error_analysis = self.analyze_prediction_errors(y_test, y_pred)
        
        report = {
            "model_type": model_type,
            "metrics": metrics,
            "error_analysis": error_analysis,
            "feature_importance": feature_importance.to_dict('records') if not feature_importance.empty else []
        }
        
        # Save full report
        report_path = self.output_dir / f"{model_type}_evaluation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"\n✅ Evaluation report saved to: {report_path}")
        
        return report


if __name__ == "__main__":
    print("Model Evaluator - Ready for use")
    print("Load trained models and test data to evaluate")