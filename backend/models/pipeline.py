
from PIL import Image
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
from transformers import AutoImageProcessor, AutoModelForImageClassification, pipeline
import numpy as np
import os
import time
import torch
import torch.nn.functional as F
import torchvision.transforms as tf
import urllib.request
# Import performance monitor for stage tracking
try:
    from performance_monitor import get_performance_monitor
    PERFORMANCE_MONITORING = True
except ImportError:
    PERFORMANCE_MONITORING = False
    print("⚠️  Performance monitoring not available")

class ObjectCountingPipeline:
    """
    AI Pipeline for counting objects in images using:
    1. SAM (Segment Anything Model) for segmentation
    2. ResNet-50 for classification
    3. DistilBERT for zero-shot label mapping
    """
    
    def __init__(self):
        """Initialize all models and components"""
        print("Initializing Object Counting Pipeline...")
        
        # Configuration
        self.TOP_N = 10  # Number of top segments to process
        self.CONFIDENCE_THRESHOLD = 0.7  # Default confidence threshold for filtering
        self.MIN_SEGMENTS_FOR_QUALITY = 5  # Minimum segments for quality assessment
        
        # GPU setup with memory management
        self._setup_device()
        
        # Predefined object categories
        self.candidate_labels = [
            "person", "car", "bus", "bicycle", "motorcycle",
            "dog", "cat", "bird", "tree", "building", 
            "road", "sky"
        ]
        
        # Initialize models with error handling
        try:
            self._setup_sam_model()
            self._setup_classification_model()
            self._setup_label_classifier()
            print("✅ Pipeline initialization complete!")
        except Exception as e:
            print(f"❌ Pipeline initialization failed: {e}")
            # Fallback to CPU if GPU fails
            if self.device == "cuda":
                print("🔄 Falling back to CPU...")
                self.device = "cpu"
                self._setup_sam_model()
                self._setup_classification_model()
                self._setup_label_classifier()
                print("✅ Pipeline initialized on CPU!")
            else:
                raise e
    
    def _setup_device(self):
        """Setup device with GPU memory management"""
        if torch.cuda.is_available():
            self.device = "cuda"
            # Clear GPU cache
            torch.cuda.empty_cache()
            # Get GPU info
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"🚀 GPU detected: {gpu_name} ({gpu_memory:.1f}GB)")
            print(f"   Using device: {self.device}")
        else:
            self.device = "cpu"
            print(f"💻 No GPU available, using CPU")
    
    def _setup_sam_model(self):
        """Setup Segment Anything Model"""
        print("Setting up SAM model...")
        
        checkpoint_path = "sam_vit_b_01ec64.pth"
        if not os.path.exists(checkpoint_path):
            print("Downloading SAM checkpoint...")
            url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
            urllib.request.urlretrieve(url, checkpoint_path)
        
        self.sam = sam_model_registry["vit_b"](checkpoint=checkpoint_path)
        self.sam.to(self.device)
        
        self.mask_generator = SamAutomaticMaskGenerator(
            model=self.sam,
            points_per_side=16,
            pred_iou_thresh=0.7,
            stability_score_thresh=0.85,
            min_mask_region_area=500,
        )
        print("SAM model ready!")
    
    def _setup_classification_model(self):
        """Setup ResNet-50 classification model"""
        print("Setting up ResNet-50 model...")
        
        self.image_processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
        self.class_model = AutoModelForImageClassification.from_pretrained("microsoft/resnet-50")
        
        # Move ResNet model to GPU
        self.class_model.to(self.device)
        print(f"ResNet-50 model ready on {self.device}!")
    
    def _setup_label_classifier(self):
        """Setup zero-shot label classifier"""
        print("Setting up zero-shot classifier...")
        
        # Setup with GPU device if available
        device_id = 0 if self.device == "cuda" else -1
        self.label_classifier = pipeline(
            "zero-shot-classification", 
            model="typeform/distilbert-base-uncased-mnli",
            device=device_id
        )
        
        print(f"Zero-shot classifier ready on {self.device}!")
    
    def segment_image(self, image):
        """
        Step 1: Segment image using SAM
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            tuple: (segmented_map, segments_list)
        """
        height, width = image.size[1], image.size[0]
        
        # Generate masks using SAM
        masks = self.mask_generator.generate(np.array(image))
        masks_sorted = sorted(masks, key=lambda x: x['area'], reverse=True)
        
        # Create panoptic segmentation map
        predicted_panoptic_map = np.zeros((height, width), dtype=np.int32)
        for idx, mask_data in enumerate(masks_sorted[:self.TOP_N]):
            predicted_panoptic_map[mask_data['segmentation']] = idx + 1
        
        predicted_panoptic_map = torch.from_numpy(predicted_panoptic_map)
        
        # Extract individual segments
        transform = tf.Compose([tf.PILToTensor()])
        img_tensor = transform(image)
        
        segments = []
        for label in predicted_panoptic_map.unique():
            if label == 0:  # Skip background
                continue
                
            y_start, y_end = self._get_mask_box(predicted_panoptic_map == label)
            x_start, x_end = self._get_mask_box((predicted_panoptic_map == label).T)
            
            if y_start is None or x_start is None:
                continue
            
            cropped_tensor = img_tensor[:, y_start:y_end+1, x_start:x_end+1]
            cropped_mask = predicted_panoptic_map[y_start:y_end+1, x_start:x_end+1] == label
            
            segment = cropped_tensor * cropped_mask.unsqueeze(0)
            segment[:, ~cropped_mask] = 188  # Set background to gray
            
            segments.append(segment)
        
        return predicted_panoptic_map, segments
    
    def _get_mask_box(self, tensor):
        """
        Get bounding box of non-zero elements in tensor
        
        Args:
            tensor (torch.Tensor): Input tensor
            
        Returns:
            tuple: (first_index, last_index)
        """
        non_zero_indices = torch.nonzero(tensor, as_tuple=True)[0]
        if non_zero_indices.shape[0] == 0:
            return None, None
        
        first_n = non_zero_indices[:1].item()
        last_n = non_zero_indices[-1:].item()
        
        return first_n, last_n
    
    def classify_segments(self, segments):
        """
        Step 2: Classify each segment using ResNet-50
        
        Args:
            segments (list): List of image segments
            
        Returns:
            tuple: (predicted_classes, confidence_scores)
        """
        predicted_classes = []
        confidence_scores = []
        
        for segment in segments:
            inputs = self.image_processor(images=segment, return_tensors="pt")
            
            # Move inputs to GPU if available
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():  # Optimize GPU memory
                outputs = self.class_model(**inputs)
                logits = outputs.logits
                
                # Apply softmax to get probabilities
                probabilities = F.softmax(logits, dim=-1)
                max_prob, predicted_class_idx = torch.max(probabilities, dim=-1)
                
                predicted_class = self.class_model.config.id2label[predicted_class_idx.item()]
                confidence = max_prob.item()
                
                predicted_classes.append(predicted_class)
                confidence_scores.append(confidence)
        
        # Clean up GPU memory after classification
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        return predicted_classes, confidence_scores
    
    def map_to_categories(self, predicted_classes, classification_confidences):
        """
        Step 3: Map ResNet predictions to predefined categories using zero-shot classification
        
        Args:
            predicted_classes (list): ResNet predicted class names
            classification_confidences (list): Confidence scores from classification
            
        Returns:
            tuple: (mapped_labels, final_confidences)
        """
        labels = []
        final_confidences = []
        
        for predicted_class, class_confidence in zip(predicted_classes, classification_confidences):
            result = self.label_classifier(predicted_class, candidate_labels=self.candidate_labels)
            label = result['labels'][0]  # Get the most confident label
            mapping_confidence = result['scores'][0]  # Get confidence of mapping
            
            # Combine classification and mapping confidences
            combined_confidence = (class_confidence + mapping_confidence) / 2
            
            labels.append(label)
            final_confidences.append(combined_confidence)
        
        return labels, final_confidences
    
    def apply_confidence_threshold(self, segments, labels, confidences, threshold=None):
        """
        Filter segments by confidence threshold
        
        Args:
            segments (list): List of image segments
            labels (list): Predicted labels
            confidences (list): Confidence scores
            threshold (float): Confidence threshold (uses default if None)
            
        Returns:
            tuple: (filtered_segments, filtered_labels, filtered_confidences)
        """
        if threshold is None:
            threshold = self.CONFIDENCE_THRESHOLD
        
        filtered_segments = []
        filtered_labels = []
        filtered_confidences = []
        
        for segment, label, confidence in zip(segments, labels, confidences):
            if confidence > threshold:
                filtered_segments.append(segment)
                filtered_labels.append(label)
                filtered_confidences.append(confidence)
        
        return filtered_segments, filtered_labels, filtered_confidences
    
    def aggregate_confidences(self, confidences):
        """
        Calculate aggregated confidence metrics
        
        Args:
            confidences (list): List of confidence scores
            
        Returns:
            dict: Aggregated confidence metrics
        """
        if not confidences:
            return {
                "average_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "median_confidence": 0.0,
                "confidence_std": 0.0
            }
        
        import statistics
        
        return {
            "average_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "median_confidence": statistics.median(confidences),
            "confidence_std": statistics.stdev(confidences) if len(confidences) > 1 else 0.0
        }
    
    def generate_quality_flags(self, avg_confidence, total_segments, filtered_segments):
        """
        Generate quality assessment flags
        
        Args:
            avg_confidence (float): Average confidence score
            total_segments (int): Total number of segments processed
            filtered_segments (int): Number of segments after confidence filtering
            
        Returns:
            dict: Quality assessment flags and scores
        """
        # Calculate quality metrics
        confidence_quality = "high" if avg_confidence > 0.8 else "medium" if avg_confidence > 0.6 else "low"
        segment_quality = "sufficient" if total_segments >= self.MIN_SEGMENTS_FOR_QUALITY else "insufficient"
        filtering_ratio = filtered_segments / total_segments if total_segments > 0 else 0
        filtering_quality = "good" if filtering_ratio > 0.7 else "moderate" if filtering_ratio > 0.4 else "poor"
        
        # Overall quality score (0-1)
        quality_score = (avg_confidence * 0.4 + 
                        (1 if segment_quality == "sufficient" else 0.5) * 0.3 + 
                        filtering_ratio * 0.3)
        
        return {
            "high_confidence": avg_confidence > 0.8,
            "sufficient_segments": total_segments >= self.MIN_SEGMENTS_FOR_QUALITY,
            "good_filtering": filtering_ratio > 0.7,
            "confidence_quality": confidence_quality,
            "segment_quality": segment_quality,
            "filtering_quality": filtering_quality,
            "quality_score": quality_score,
            "filtering_ratio": filtering_ratio,
            "recommendations": self._get_quality_recommendations(confidence_quality, segment_quality, filtering_quality)
        }
    
    def _get_quality_recommendations(self, confidence_quality, segment_quality, filtering_quality):
        """
        Generate recommendations based on quality assessment
        
        Args:
            confidence_quality (str): Confidence quality level
            segment_quality (str): Segment quality level
            filtering_quality (str): Filtering quality level
            
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        if confidence_quality == "low":
            recommendations.append("Consider using higher resolution images or different lighting conditions")
        
        if segment_quality == "insufficient":
            recommendations.append("Image may have too few distinct objects for reliable counting")
        
        if filtering_quality == "poor":
            recommendations.append("Many segments were filtered out - consider adjusting confidence threshold")
        
        if not recommendations:
            recommendations.append("Quality assessment indicates good results")
        
        return recommendations
    
    def count_objects(self, image_file, target_object_type, confidence_threshold=None):
        """
        Main pipeline: Count objects of specified type in image with enhanced confidence processing
        
        Args:
            image_file: Image file from Flask request
            target_object_type (str): Type of object to count
            confidence_threshold (float): Optional confidence threshold override
            
        Returns:
            dict: Results including count, confidence metrics, and quality assessment
        """
        start_time = time.time()
        
        # Load image
        image = Image.open(image_file).convert('RGB')
        
        # Step 1: Segment image
        segmentation_map, segments = self.segment_image(image)
        total_segments = len(segments)
        
        # Step 2: Classify segments with confidence scores
        predicted_classes, classification_confidences = self.classify_segments(segments)
        
        # Step 3: Map to categories with combined confidence scores
        final_labels, final_confidences = self.map_to_categories(predicted_classes, classification_confidences)
        
        # Step 4: Apply confidence threshold filtering
        filtered_segments, filtered_labels, filtered_confidences = self.apply_confidence_threshold(
            segments, final_labels, final_confidences, confidence_threshold
        )
        
        # Step 5: Count target objects (using filtered results)
        target_count = filtered_labels.count(target_object_type)
        
        # Step 6: Calculate confidence aggregation
        confidence_metrics = self.aggregate_confidences(filtered_confidences)
        
        # Step 7: Generate quality assessment
        quality_flags = self.generate_quality_flags(
            confidence_metrics["average_confidence"], 
            total_segments, 
            len(filtered_segments)
        )
        
        processing_time = time.time() - start_time
        
        return {
            "count": target_count,
            "total_segments": total_segments,
            "filtered_segments": len(filtered_segments),
            "all_detected_objects": filtered_labels,  # Use filtered results
            "processing_time": round(processing_time, 2),
            "confidence_metrics": confidence_metrics,
            "quality_assessment": quality_flags,
            "confidence_threshold_used": confidence_threshold or self.CONFIDENCE_THRESHOLD
        }
    
    def count_all_objects(self, image_file, confidence_threshold=None):
        """
        Main pipeline: Detect and count ALL objects in image with enhanced confidence processing
        
        Args:
            image_file: Image file from Flask request
            confidence_threshold (float): Optional confidence threshold override
            
        Returns:
            dict: Results including counts for all detected object types with confidence metrics
        """
        start_time = time.time()
        
        # Update performance monitor if available
        monitor = None
        if PERFORMANCE_MONITORING:
            try:
                monitor = get_performance_monitor()
                if monitor.is_monitoring:
                    monitor.update_stage("loading_image")
            except:
                pass
        
        # Load image
        image = Image.open(image_file).convert('RGB')
        
        # Step 1: Segment image
        if monitor and monitor.is_monitoring:
            monitor.update_stage("segmenting")
        segmentation_map, segments = self.segment_image(image)
        total_segments = len(segments)
        
        # Step 2: Classify segments with confidence scores
        if monitor and monitor.is_monitoring:
            monitor.update_stage("classifying")
        predicted_classes, classification_confidences = self.classify_segments(segments)
        
        # Step 3: Map to categories with combined confidence scores
        if monitor and monitor.is_monitoring:
            monitor.update_stage("mapping_categories")
        final_labels, final_confidences = self.map_to_categories(predicted_classes, classification_confidences)
        
        # Step 4: Apply confidence threshold filtering
        if monitor and monitor.is_monitoring:
            monitor.update_stage("filtering_confidence")
        filtered_segments, filtered_labels, filtered_confidences = self.apply_confidence_threshold(
            segments, final_labels, final_confidences, confidence_threshold
        )
        
        # Count all object types (using filtered results)
        if monitor and monitor.is_monitoring:
            monitor.update_stage("counting_objects")
        
        object_counts = {}
        for label in filtered_labels:
            object_counts[label] = object_counts.get(label, 0) + 1
        
        # Convert to list format for frontend
        objects_list = [
            {"type": obj_type, "count": count} 
            for obj_type, count in object_counts.items()
        ]
        
        # Calculate total objects
        total_objects = sum(object_counts.values())
        
        # Step 5: Calculate confidence aggregation
        confidence_metrics = self.aggregate_confidences(filtered_confidences)
        
        # Step 6: Generate quality assessment
        quality_flags = self.generate_quality_flags(
            confidence_metrics["average_confidence"], 
            total_segments, 
            len(filtered_segments)
        )
        
        # Final stage
        if monitor and monitor.is_monitoring:
            monitor.update_stage("finalizing")
        
        processing_time = time.time() - start_time
        
        return {
            "objects": objects_list,
            "total_objects": total_objects,
            "total_segments": total_segments,
            "filtered_segments": len(filtered_segments),
            "all_detected_objects": filtered_labels,  # Use filtered results
            "processing_time": round(processing_time, 2),
            "confidence_metrics": confidence_metrics,
            "quality_assessment": quality_flags,
            "confidence_threshold_used": confidence_threshold or self.CONFIDENCE_THRESHOLD
        }



