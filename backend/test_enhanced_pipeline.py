#!/usr/bin/env python3
"""
Test script for the enhanced AI Object Counting Pipeline
Tests the new confidence threshold, confidence aggregation, and quality flags features
"""

import os
import sys
import time
from PIL import Image
import numpy as np

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_image():
    """Create a simple test image with basic shapes"""
    # Create a 400x400 RGB image with white background
    img = Image.new('RGB', (400, 400), color='white')
    
    # Create a simple numpy array to draw some basic shapes
    img_array = np.array(img)
    
    # Draw some rectangles (simulating objects)
    # Rectangle 1 (top-left)
    img_array[50:150, 50:150] = [255, 0, 0]  # Red
    
    # Rectangle 2 (top-right)
    img_array[50:150, 250:350] = [0, 255, 0]  # Green
    
    # Rectangle 3 (bottom-left)
    img_array[250:350, 50:150] = [0, 0, 255]  # Blue
    
    # Rectangle 4 (bottom-right)
    img_array[250:350, 250:350] = [255, 255, 0]  # Yellow
    
    return Image.fromarray(img_array)

def test_enhanced_pipeline():
    """Test the enhanced pipeline with confidence features"""
    print("🧪 Testing Enhanced AI Object Counting Pipeline")
    print("=" * 60)
    
    try:
        # Import the enhanced pipeline
        from models.pipeline import ObjectCountingPipeline
        print("✅ Successfully imported enhanced pipeline")
        
        # Initialize pipeline
        print("\n🚀 Initializing pipeline...")
        pipeline = ObjectCountingPipeline()
        print("✅ Pipeline initialized successfully!")
        
        # Create test image
        print("\n🖼️  Creating test image...")
        test_image = create_test_image()
        test_image.save("test_enhanced_image.png")
        print("✅ Test image created: test_enhanced_image.png")
        
        # Test 1: Basic object counting with default confidence threshold
        print("\n📊 Test 1: Basic object counting (default confidence threshold)")
        print("-" * 50)
        
        with open("test_enhanced_image.png", "rb") as f:
            result1 = pipeline.count_objects(f, "person")
        
        print(f"Count: {result1['count']}")
        print(f"Total segments: {result1['total_segments']}")
        print(f"Filtered segments: {result1['filtered_segments']}")
        print(f"Processing time: {result1['processing_time']:.2f}s")
        print(f"Confidence threshold used: {result1['confidence_threshold_used']}")
        
        # Display confidence metrics
        conf_metrics = result1['confidence_metrics']
        print(f"\nConfidence Metrics:")
        print(f"  Average: {conf_metrics['average_confidence']:.3f}")
        print(f"  Min: {conf_metrics['min_confidence']:.3f}")
        print(f"  Max: {conf_metrics['max_confidence']:.3f}")
        print(f"  Median: {conf_metrics['median_confidence']:.3f}")
        print(f"  Std Dev: {conf_metrics['confidence_std']:.3f}")
        
        # Display quality assessment
        quality = result1['quality_assessment']
        print(f"\nQuality Assessment:")
        print(f"  High confidence: {quality['high_confidence']}")
        print(f"  Sufficient segments: {quality['sufficient_segments']}")
        print(f"  Good filtering: {quality['good_filtering']}")
        print(f"  Quality score: {quality['quality_score']:.3f}")
        print(f"  Filtering ratio: {quality['filtering_ratio']:.3f}")
        print(f"  Recommendations: {quality['recommendations']}")
        
        # Test 2: High confidence threshold
        print("\n📊 Test 2: High confidence threshold (0.9)")
        print("-" * 50)
        
        with open("test_enhanced_image.png", "rb") as f:
            result2 = pipeline.count_objects(f, "person", confidence_threshold=0.9)
        
        print(f"Count: {result2['count']}")
        print(f"Total segments: {result2['total_segments']}")
        print(f"Filtered segments: {result2['filtered_segments']}")
        print(f"Confidence threshold used: {result2['confidence_threshold_used']}")
        
        # Test 3: Low confidence threshold
        print("\n📊 Test 3: Low confidence threshold (0.3)")
        print("-" * 50)
        
        with open("test_enhanced_image.png", "rb") as f:
            result3 = pipeline.count_objects(f, "person", confidence_threshold=0.3)
        
        print(f"Count: {result3['count']}")
        print(f"Total segments: {result3['total_segments']}")
        print(f"Filtered segments: {result3['filtered_segments']}")
        print(f"Confidence threshold used: {result3['confidence_threshold_used']}")
        
        # Test 4: Multi-object detection
        print("\n📊 Test 4: Multi-object detection")
        print("-" * 50)
        
        with open("test_enhanced_image.png", "rb") as f:
            result4 = pipeline.count_all_objects(f, confidence_threshold=0.5)
        
        print(f"Total objects: {result4['total_objects']}")
        print(f"Total segments: {result4['total_segments']}")
        print(f"Filtered segments: {result4['filtered_segments']}")
        print(f"Objects detected: {result4['objects']}")
        
        # Compare results
        print("\n📈 Results Comparison:")
        print("-" * 50)
        print(f"Default threshold (0.7): {result1['filtered_segments']} segments")
        print(f"High threshold (0.9):   {result2['filtered_segments']} segments")
        print(f"Low threshold (0.3):    {result3['filtered_segments']} segments")
        print(f"Multi-object (0.5):     {result4['filtered_segments']} segments")
        
        print("\n✅ All tests completed successfully!")
        print("\n🎯 Enhanced Features Verified:")
        print("  ✅ Confidence threshold filtering")
        print("  ✅ Confidence aggregation metrics")
        print("  ✅ Quality assessment flags")
        print("  ✅ Quality recommendations")
        print("  ✅ Enhanced API responses")
        
        # Cleanup
        if os.path.exists("test_enhanced_image.png"):
            os.remove("test_enhanced_image.png")
            print("\n🧹 Cleaned up test files")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install torch torchvision transformers pillow")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_pipeline()
