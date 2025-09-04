"""
Performance Metrics Utilities for Object Counting AI
Implements F1 Score, Precision, Recall, and other evaluation metrics
"""

def calculate_f1_metrics(predicted_count, corrected_count) -> None:
    """
    Calculate F1 Score, Precision, and Recall for object counting tasks.
    
    F1 Score is superior to simple accuracy for object counting because:
    1. Handles imbalanced data better (sparse vs dense object scenarios)
    2. Considers both precision (avoiding false positives) and recall (finding all objects)
    3. Provides more nuanced evaluation than simple accuracy
    4. Standard metric in machine learning evaluation
    
    For object counting interpretation:
    - True Positives (TP) = min(predicted, corrected) - correctly detected objects
    - False Positives (FP) = max(0, predicted - corrected) - over-detection errors
    - False Negatives (FN) = max(0, corrected - predicted) - missed objects
    
    Args:
        predicted_count (int): AI model's predicted object count
        corrected_count (int): User's corrected/actual object count
        
    Returns:
        dict: {
            'f1_score': float (0-100),
            'precision': float (0-100), 
            'recall': float (0-100),
            'true_positives': int,
            'false_positives': int,
            'false_negatives': int,
            'explanation': str
        }
    """
    
    # Calculate confusion matrix components for object counting
    true_positives = min(predicted_count, corrected_count)
    false_positives = max(0, predicted_count - corrected_count)
    false_negatives = max(0, corrected_count - predicted_count)
    
    # Calculate precision (what % of predictions were correct)
    if predicted_count > 0:
        precision = true_positives / predicted_count
    else:
        # No predictions made
        precision = 1.0 if corrected_count == 0 else 0.0
    
    # Calculate recall (what % of actual objects were found)
    if corrected_count > 0:
        recall = true_positives / corrected_count
    else:
        # No actual objects
        recall = 1.0 if predicted_count == 0 else 0.0
    
    # Calculate F1 Score (harmonic mean of precision and recall)
    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0
    
    # Convert to percentages
    f1_score_pct = f1_score * 100
    precision_pct = precision * 100
    recall_pct = recall * 100
    
    # Generate explanation
    explanation = generate_performance_explanation(
        f1_score_pct, precision_pct, recall_pct, 
        predicted_count, corrected_count,
        true_positives, false_positives, false_negatives
    )
    
    return {
        'f1_score': f1_score_pct,
        'precision': precision_pct,
        'recall': recall_pct,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'explanation': explanation
    }

def generate_performance_explanation(f1_score, precision, recall, predicted, corrected, tp, fp, fn) -> None:
    """Generate human-readable explanation of the F1 score metrics"""
    
    if f1_score >= 95:
        level = "Excellent"
        emoji = "🎯"
        insight = "Near-perfect object counting performance!"
    elif f1_score >= 85:
        level = "Very Good"
        emoji = "✅"
        insight = "Strong performance with minor counting variations."
    elif f1_score >= 70:
        level = "Good"
        emoji = "👍"
        insight = "Solid performance, some room for improvement."
    elif f1_score >= 50:
        level = "Fair"
        emoji = "⚠️"
        insight = "Moderate performance, significant counting differences detected."
    else:
        level = "Needs Improvement"
        emoji = "🔄"
        insight = "Large counting discrepancies, model may need retraining."
    
    # Specific insights based on precision vs recall
    if precision > recall + 15:
        balance_insight = "Model tends to be conservative (misses some objects)."
    elif recall > precision + 15:
        balance_insight = "Model tends to over-detect (finds extra objects)."
    else:
        balance_insight = "Good balance between precision and recall."
    
    # Detailed breakdown
    breakdown = f"Predicted: {predicted}, Actual: {corrected}"
    if tp > 0:
        breakdown += f" | Correctly detected: {tp}"
    if fp > 0:
        breakdown += f" | Over-detected: {fp}"
    if fn > 0:
        breakdown += f" | Missed: {fn}"
    
    return f"{emoji} {level} (F1: {f1_score:.1f}%) - {insight} {balance_insight} [{breakdown}]"

def calculate_legacy_accuracy(predicted_count, corrected_count) -> None:
    """
    Calculate legacy accuracy metric for backward compatibility.
    
    This is the old accuracy calculation that we're replacing with F1 Score.
    Kept for compatibility during transition period.
    """
    if corrected_count == 0:
        return 100 if predicted_count == 0 else 0
    else:
        return max(0, 100 - abs(predicted_count - corrected_count) / corrected_count * 100)

def get_performance_badge_info(f1_score) -> None:
    """
    Get badge styling information based on F1 score.
    
    Returns:
        dict: {'level': str, 'color': str, 'bg_color': str, 'border_color': str}
    """
    if f1_score is None:
        return {
            'level': 'No Feedback',
            'color': 'text-gray-600',
            'bg_color': 'bg-gray-100',
            'border_color': 'border-gray-300'
        }
    elif f1_score >= 90:
        return {
            'level': 'Excellent',
            'color': 'text-green-800',
            'bg_color': 'bg-green-100',
            'border_color': 'border-green-300'
        }
    elif f1_score >= 75:
        return {
            'level': 'Very Good',
            'color': 'text-blue-800',
            'bg_color': 'bg-blue-100', 
            'border_color': 'border-blue-300'
        }
    elif f1_score >= 60:
        return {
            'level': 'Good',
            'color': 'text-yellow-800',
            'bg_color': 'bg-yellow-100',
            'border_color': 'border-yellow-300'
        }
    else:
        return {
            'level': 'Needs Review',
            'color': 'text-red-800',
            'bg_color': 'bg-red-100',
            'border_color': 'border-red-300'
        }

def calculate_overall_f1_stats(results) -> None:
    """
    Calculate overall F1 statistics across multiple results.
    
    Args:
        results: List of dicts with 'predicted_count' and 'corrected_count'
        
    Returns:
        dict: Overall F1 statistics
    """
    if not results:
        return {
            'count': 0,
            'avg_f1_score': 0,
            'avg_precision': 0,
            'avg_recall': 0,
            'excellent_count': 0,
            'good_count': 0,
            'needs_review_count': 0
        }
    
    total_f1 = 0
    total_precision = 0
    total_recall = 0
    excellent_count = 0
    good_count = 0
    needs_review_count = 0
    
    for result in results:
        if result.get('corrected_count') is not None:
            metrics = calculate_f1_metrics(
                result['predicted_count'], 
                result['corrected_count']
            )
            
            total_f1 += metrics['f1_score']
            total_precision += metrics['precision']
            total_recall += metrics['recall']
            
            if metrics['f1_score'] >= 90:
                excellent_count += 1
            elif metrics['f1_score'] >= 70:
                good_count += 1
            else:
                needs_review_count += 1
    
    count = len([r for r in results if r.get('corrected_count') is not None])
    
    return {
        'count': count,
        'avg_f1_score': total_f1 / count if count > 0 else 0,
        'avg_precision': total_precision / count if count > 0 else 0,
        'avg_recall': total_recall / count if count > 0 else 0,
        'excellent_count': excellent_count,
        'good_count': good_count,
        'needs_review_count': needs_review_count
    }



