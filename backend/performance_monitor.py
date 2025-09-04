#!/usr/bin/env python3
"""
Real-time performance monitoring for AI pipeline
Tracks CPU, GPU, memory, and processing metrics
"""

import psutil
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
import json

try:
    import GPUtil
    import torch
    import pynvml
    GPU_AVAILABLE = True
    # Initialize NVML for detailed GPU monitoring
    try:
        pynvml.nvmlInit()
        NVML_AVAILABLE = True
        print("🚀 Enhanced GPU monitoring with pynvml initialized")
    except:
        NVML_AVAILABLE = False
        print("⚠️  NVML not available, using basic GPU monitoring")
except ImportError as e:
    GPU_AVAILABLE = False
    NVML_AVAILABLE = False
    print(f"⚠️  GPU monitoring not available: {e}")

class PerformanceMonitor:
    """Real-time performance monitoring for AI processing"""
    
    def __init__(self):
        self.is_monitoring = False
        self.current_metrics = {}
        self.metrics_history = []
        self.max_history = 100  # Keep last 100 readings
        self.processing_start_time = None
        self.current_stage = "idle"
        self.total_images = 0
        self.processed_images = 0
        
        # Background monitoring
        self.monitoring_thread = None
        self.monitoring_interval = 0.5  # Update every 500ms
        self._stop_monitoring_flag = False
        
    def start_monitoring(self, total_images: int = 1):
        """Start monitoring for a processing session"""
        self.is_monitoring = True
        self.processing_start_time = time.time()
        self.current_stage = "initializing"
        self.total_images = total_images
        self.processed_images = 0
        self.metrics_history = []
        self._stop_monitoring_flag = False
        
        # Start background monitoring thread
        self.monitoring_thread = threading.Thread(target=self._background_monitor)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print(f"🔍 Performance monitoring started for {total_images} images with background thread")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self._stop_monitoring_flag = True
        self.is_monitoring = False
        self.current_stage = "completed"
        processing_time = time.time() - self.processing_start_time if self.processing_start_time else 0
        
        # Wait for background thread to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)
        
        print(f"✅ Performance monitoring stopped. Total time: {processing_time:.2f}s")
        
    def _background_monitor(self):
        """Background thread for continuous metrics collection"""
        print("🔄 Background performance monitoring started")
        
        while not self._stop_monitoring_flag and self.is_monitoring:
            try:
                # Collect current metrics
                self.get_current_metrics()
                
                # Sleep for the monitoring interval
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"❌ Background monitoring error: {e}")
                time.sleep(1.0)  # Longer sleep on error
        
        print("🛑 Background performance monitoring stopped")
        
    def update_stage(self, stage: str, image_index: int = None):
        """Update current processing stage"""
        self.current_stage = stage
        if image_index is not None:
            self.processed_images = image_index + 1
            
        print(f"📊 Stage: {stage} ({self.processed_images}/{self.total_images})")
        
    def get_cpu_metrics(self) -> Dict:
        """Get CPU usage metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            
            # Get per-core usage
            cpu_per_core = psutil.cpu_percent(percpu=True, interval=0.1)
            
            return {
                "usage_percent": cpu_percent,
                "frequency_mhz": cpu_freq.current if cpu_freq else 0,
                "cores": cpu_count,
                "per_core_usage": cpu_per_core,
                "temperature": self.get_cpu_temperature()
            }
        except Exception as e:
            print(f"❌ Error getting CPU metrics: {e}")
            return {"usage_percent": 0, "frequency_mhz": 0, "cores": 0, "per_core_usage": [], "temperature": 0}
    
    def get_gpu_metrics(self) -> Dict:
        """Get enhanced GPU usage metrics with detailed monitoring"""
        if not GPU_AVAILABLE:
            return {"available": False, "usage_percent": 0, "memory_used_mb": 0, "memory_total_mb": 0, "temperature": 0}
            
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return {"available": False, "usage_percent": 0, "memory_used_mb": 0, "memory_total_mb": 0, "temperature": 0}
                
            gpu = gpus[0]  # Use first GPU
            
            # Enhanced metrics with pynvml if available
            enhanced_metrics = {}
            if NVML_AVAILABLE:
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    
                    # Detailed temperature monitoring
                    gpu_temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    
                    # Power consumption
                    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                    power_limit = pynvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1] / 1000.0
                    
                    # Clock speeds
                    graphics_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                    memory_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
                    
                    # Fan speed (if available)
                    try:
                        fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
                    except:
                        fan_speed = 0
                    
                    # GPU utilization breakdown
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    
                    enhanced_metrics = {
                        "temperature_detailed": gpu_temp,
                        "power_watts": power_usage,
                        "power_limit_watts": power_limit,
                        "power_percent": (power_usage / power_limit) * 100 if power_limit > 0 else 0,
                        "graphics_clock_mhz": graphics_clock,
                        "memory_clock_mhz": memory_clock,
                        "fan_speed_percent": fan_speed,
                        "gpu_utilization": utilization.gpu,
                        "memory_utilization": utilization.memory
                    }
                except Exception as e:
                    print(f"⚠️  Enhanced GPU metrics error: {e}")
            
            # PyTorch GPU memory if available
            torch_memory = {}
            if torch.cuda.is_available():
                try:
                    torch_memory = {
                        "allocated_mb": torch.cuda.memory_allocated() / 1024 / 1024,
                        "reserved_mb": torch.cuda.memory_reserved() / 1024 / 1024,
                        "max_allocated_mb": torch.cuda.max_memory_allocated() / 1024 / 1024
                    }
                except:
                    torch_memory = {}
            
            return {
                "available": True,
                "name": gpu.name,
                "usage_percent": gpu.load * 100,
                "memory_used_mb": gpu.memoryUsed,
                "memory_total_mb": gpu.memoryTotal,
                "memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100,
                "temperature": gpu.temperature,
                "torch_memory": torch_memory,
                "enhanced": enhanced_metrics
            }
        except Exception as e:
            print(f"❌ Error getting GPU metrics: {e}")
            return {"available": False, "usage_percent": 0, "memory_used_mb": 0, "memory_total_mb": 0, "temperature": 0}
    
    def get_memory_metrics(self) -> Dict:
        """Get system memory metrics"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total_gb": memory.total / 1024 / 1024 / 1024,
                "used_gb": memory.used / 1024 / 1024 / 1024,
                "available_gb": memory.available / 1024 / 1024 / 1024,
                "usage_percent": memory.percent,
                "swap_total_gb": swap.total / 1024 / 1024 / 1024,
                "swap_used_gb": swap.used / 1024 / 1024 / 1024,
                "swap_percent": swap.percent
            }
        except Exception as e:
            print(f"❌ Error getting memory metrics: {e}")
            return {"total_gb": 0, "used_gb": 0, "available_gb": 0, "usage_percent": 0, "swap_total_gb": 0, "swap_used_gb": 0, "swap_percent": 0}
    
    def get_cpu_temperature(self) -> float:
        """Get CPU temperature (if available)"""
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
            elif 'cpu_thermal' in temps:
                return temps['cpu_thermal'][0].current
            else:
                return 0.0
        except:
            return 0.0
    
    def get_disk_metrics(self) -> Dict:
        """Get disk I/O metrics"""
        try:
            disk_io = psutil.disk_io_counters()
            disk_usage = psutil.disk_usage('/')
            
            return {
                "read_mb_per_s": disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
                "write_mb_per_s": disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
                "total_gb": disk_usage.total / 1024 / 1024 / 1024,
                "used_gb": disk_usage.used / 1024 / 1024 / 1024,
                "free_gb": disk_usage.free / 1024 / 1024 / 1024,
                "usage_percent": (disk_usage.used / disk_usage.total) * 100
            }
        except Exception as e:
            print(f"❌ Error getting disk metrics: {e}")
            return {"read_mb_per_s": 0, "write_mb_per_s": 0, "total_gb": 0, "used_gb": 0, "free_gb": 0, "usage_percent": 0}
    
    def get_current_metrics(self) -> Dict:
        """Get all current performance metrics"""
        if not self.is_monitoring:
            return {"monitoring": False}
            
        timestamp = datetime.now().isoformat()
        elapsed_time = time.time() - self.processing_start_time if self.processing_start_time else 0
        
        metrics = {
            "monitoring": True,
            "timestamp": timestamp,
            "elapsed_time": elapsed_time,
            "current_stage": self.current_stage,
            "progress": {
                "total_images": self.total_images,
                "processed_images": self.processed_images,
                "percentage": (self.processed_images / self.total_images * 100) if self.total_images > 0 else 0
            },
            "cpu": self.get_cpu_metrics(),
            "gpu": self.get_gpu_metrics(),
            "memory": self.get_memory_metrics(),
            "disk": self.get_disk_metrics()
        }
        
        # Store in history
        self.current_metrics = metrics
        self.metrics_history.append(metrics)
        
        # Keep only recent history
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
            
        return metrics
    
    def get_metrics_summary(self) -> Dict:
        """Get performance summary and statistics"""
        if not self.metrics_history:
            return {"available": False}
            
        # Calculate averages and peaks
        cpu_usage = [m["cpu"]["usage_percent"] for m in self.metrics_history if "cpu" in m]
        gpu_usage = [m["gpu"]["usage_percent"] for m in self.metrics_history if "gpu" in m and m["gpu"]["available"]]
        memory_usage = [m["memory"]["usage_percent"] for m in self.metrics_history if "memory" in m]
        
        return {
            "available": True,
            "total_readings": len(self.metrics_history),
            "cpu": {
                "avg_usage": sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                "peak_usage": max(cpu_usage) if cpu_usage else 0,
                "min_usage": min(cpu_usage) if cpu_usage else 0
            },
            "gpu": {
                "avg_usage": sum(gpu_usage) / len(gpu_usage) if gpu_usage else 0,
                "peak_usage": max(gpu_usage) if gpu_usage else 0,
                "min_usage": min(gpu_usage) if gpu_usage else 0,
                "available": len(gpu_usage) > 0
            },
            "memory": {
                "avg_usage": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                "peak_usage": max(memory_usage) if memory_usage else 0,
                "min_usage": min(memory_usage) if memory_usage else 0
            },
            "processing_time": self.current_metrics.get("elapsed_time", 0)
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def get_performance_monitor():
    """Get the global performance monitor instance"""
    return performance_monitor
