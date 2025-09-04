
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
            list: Predicted class names
        """
        predicted_classes = []
        
        for segment in segments:
            inputs = self.image_processor(images=segment, return_tensors="pt")
            
            # Move inputs to GPU if available
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():  # Optimize GPU memory
                outputs = self.class_model(**inputs)
                logits = outputs.logits
                predicted_class_idx = logits.argmax(-1).item()
                predicted_class = self.class_model.config.id2label[predicted_class_idx]
                predicted_classes.append(predicted_class)
        
        # Clean up GPU memory after classification
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        return predicted_classes
    
    def map_to_categories(self, predicted_classes):
        """
        Step 3: Map ResNet predictions to predefined categories using zero-shot classification
        
        Args:
            predicted_classes (list): ResNet predicted class names
            
        Returns:
            list: Mapped category labels
        """
        labels = []
        
        for predicted_class in predicted_classes:
            result = self.label_classifier(predicted_class, candidate_labels=self.candidate_labels)
            label = result['labels'][0]  # Get the most confident label
            labels.append(label)
        
        return labels
    
    def count_objects(self, image_file, target_object_type):
        """
        Main pipeline: Count objects of specified type in image
        
        Args:
            image_file: Image file from Flask request
            target_object_type (str): Type of object to count
            
        Returns:
            dict: Results including count and processing info
        """
        start_time = time.time()
        
        # Load image
        image = Image.open(image_file).convert('RGB')
        
        # Step 1: Segment image
        segmentation_map, segments = self.segment_image(image)
        
        # Step 2: Classify segments
        predicted_classes = self.classify_segments(segments)
        
        # Step 3: Map to categories
        final_labels = self.map_to_categories(predicted_classes)
        
        # Count target objects
        target_count = final_labels.count(target_object_type)
        
        processing_time = time.time() - start_time
        
        return {
            "count": target_count,
            "total_segments": len(segments),
            "all_detected_objects": final_labels,
            "processing_time": round(processing_time, 2)
        }
    
    def count_all_objects(self, image_file):
        """
        Main pipeline: Detect and count ALL objects in image
        
        Args:
            image_file: Image file from Flask request
            
        Returns:
            dict: Results including counts for all detected object types
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
        
        # Step 2: Classify segments
        if monitor and monitor.is_monitoring:
            monitor.update_stage("classifying")
        predicted_classes = self.classify_segments(segments)
        
        # Step 3: Map to categories
        if monitor and monitor.is_monitoring:
            monitor.update_stage("mapping_categories")
        final_labels = self.map_to_categories(predicted_classes)
        
        # Count all object types
        if monitor and monitor.is_monitoring:
            monitor.update_stage("counting_objects")
        
        object_counts = {}
        for label in final_labels:
            object_counts[label] = object_counts.get(label, 0) + 1
        
        # Convert to list format for frontend
        objects_list = [
            {"type": obj_type, "count": count} 
            for obj_type, count in object_counts.items()
        ]
        
        # Calculate total objects
        total_objects = sum(object_counts.values())
        
        # Final stage
        if monitor and monitor.is_monitoring:
            monitor.update_stage("finalizing")
        
        processing_time = time.time() - start_time
        
        return {
            "objects": objects_list,
            "total_objects": total_objects,
            "total_segments": len(segments),
            "all_detected_objects": final_labels,
            "processing_time": round(processing_time, 2)
        }



