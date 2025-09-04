import React, { useState, useEffect, useRef } from 'react';
import { X, Zap, Cpu, HardDrive, Thermometer, Activity, Clock, Image as ImageIcon, CheckCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import api from '../services/api';

interface ProcessingDialogProps {
  isOpen: boolean;
  onClose: () => void;
  totalImages: number;
  onProcessingComplete: (results: any[]) => void;
  onProcessingError: (error: string) => void;
  imageFiles: File[];
  prompt: string;
}

interface PerformanceMetrics {
  monitoring: boolean;
  timestamp: string;
  elapsed_time: number;
  current_stage: string;
  progress: {
    total_images: number;
    processed_images: number;
    percentage: number;
  };
  cpu: {
    usage_percent: number;
    frequency_mhz: number;
    cores: number;
    per_core_usage: number[];
    temperature: number;
  };
  gpu: {
    available: boolean;
    name?: string;
    usage_percent: number;
    memory_used_mb: number;
    memory_total_mb: number;
    memory_percent: number;
    temperature: number;
    torch_memory?: {
      allocated_mb: number;
      reserved_mb: number;
      max_allocated_mb: number;
    };
  };
  memory: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
    swap_total_gb: number;
    swap_used_gb: number;
    swap_percent: number;
  };
  disk: {
    read_mb_per_s: number;
    write_mb_per_s: number;
    total_gb: number;
    used_gb: number;
    free_gb: number;
    usage_percent: number;
  };
}

const STAGE_DESCRIPTIONS = {
  'idle': 'System Ready',
  'initializing': 'Initializing AI Pipeline',
  'loading_image': 'Loading Image',
  'segmenting': 'Analyzing Segments',
  'classifying': 'Classifying Objects',
  'mapping_categories': 'Mapping Categories',
  'counting_objects': 'Counting Objects',
  'finalizing': 'Finalizing Results',
  'completed': 'Processing Complete'
};

export function ProcessingDialog({
  isOpen,
  onClose,
  totalImages,
  onProcessingComplete,
  onProcessingError,
  imageFiles,
  prompt
}: ProcessingDialogProps) {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedResults, setProcessedResults] = useState<any[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [processingStage, setProcessingStage] = useState('idle');
  const [startTime, setStartTime] = useState<number | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [error, setError] = useState<string>('');
  
  // Performance history for charts
  const [performanceHistory, setPerformanceHistory] = useState<{
    cpu: number[];
    gpu: number[];
    memory: number[];
    timestamps: number[];
  }>({
    cpu: [],
    gpu: [],
    memory: [],
    timestamps: []
  });
  
  const metricsIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const elapsedIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Start performance monitoring and processing
  useEffect(() => {
    if (isOpen && !isProcessing && imageFiles.length > 0) {
      startProcessing();
    }
  }, [isOpen, imageFiles]);

  // Clean up intervals on unmount
  useEffect(() => {
    return () => {
      if (metricsIntervalRef.current) {
        clearInterval(metricsIntervalRef.current);
      }
      if (elapsedIntervalRef.current) {
        clearInterval(elapsedIntervalRef.current);
      }
    };
  }, []);

  const startMetricsPolling = () => {
    // Poll performance metrics every 250ms for more responsive updates
    const pollMetrics = async () => {
      if (!isProcessing) return;
      
      try {
        const metricsData = await api.getPerformanceMetrics();
        setMetrics(metricsData);
        
        if (metricsData.current_stage) {
          setProcessingStage(metricsData.current_stage);
        }
        
        // Update performance history for charts
        if (metricsData.monitoring) {
          const now = Date.now();
          setPerformanceHistory(prev => {
            const maxPoints = 50; // Keep last 50 data points
            
            const newHistory = {
              cpu: [...prev.cpu, metricsData.cpu?.usage_percent || 0].slice(-maxPoints),
              gpu: [...prev.gpu, metricsData.gpu?.usage_percent || 0].slice(-maxPoints),
              memory: [...prev.memory, metricsData.memory?.usage_percent || 0].slice(-maxPoints),
              timestamps: [...prev.timestamps, now].slice(-maxPoints)
            };
            
            return newHistory;
          });
        }
      } catch (error) {
        console.error('Failed to get performance metrics:', error);
      }
    };
    
    // Initial metrics fetch
    pollMetrics();
    
    // Set up interval polling
    metricsIntervalRef.current = setInterval(pollMetrics, 250);
  };

  const stopMetricsPolling = () => {
    if (metricsIntervalRef.current) {
      clearInterval(metricsIntervalRef.current);
      metricsIntervalRef.current = null;
    }
  };

  const startElapsedTimer = () => {
    setStartTime(Date.now());
    elapsedIntervalRef.current = setInterval(() => {
      if (startTime) {
        setElapsedTime((Date.now() - startTime) / 1000);
      }
    }, 100);
  };

  const stopElapsedTimer = () => {
    if (elapsedIntervalRef.current) {
      clearInterval(elapsedIntervalRef.current);
      elapsedIntervalRef.current = null;
    }
  };

  const startProcessing = async () => {
    try {
      setIsProcessing(true);
      setError('');
      setProcessedResults([]);
      setCurrentImageIndex(0);
      setProcessingStage('initializing');
      
      // Start performance monitoring
      await api.startPerformanceMonitoring(totalImages);
      startMetricsPolling();
      startElapsedTimer();
      
      // Process images asynchronously with proper yielding
      const results: any[] = [];
      
      for (let i = 0; i < imageFiles.length; i++) {
        setCurrentImageIndex(i);
        
        try {
          console.log(`🔍 Processing image ${i + 1}/${imageFiles.length}: ${imageFiles[i].name}`);
          
          // Update stage in backend
          await api.updatePerformanceStage('processing_image', i);
          
          // Yield to allow UI updates and metrics polling
          await new Promise(resolve => setTimeout(resolve, 100));
          
          // Process image with timeout to prevent hanging
          const processImage = () => api.countAllObjects(
            imageFiles[i],
            prompt || 'Detect and count all objects in this image'
          );
          
          const result = await Promise.race([
            processImage(),
            new Promise((_, reject) => 
              setTimeout(() => reject(new Error('Processing timeout')), 120000) // 2 minute timeout
            )
          ]);
          
          console.log(`✅ Image ${i + 1} processed:`, result);
          
          const processedResult = {
            id: Math.random().toString(36).substr(2, 9),
            file: imageFiles[i],
            url: URL.createObjectURL(imageFiles[i]),
            objects: result.objects || [],
            resultId: result.result_id,
            processingTime: result.processing_time,
            totalSegments: result.total_segments
          };
          
          results.push(processedResult);
          
          // Update processed results incrementally for better UX
          setProcessedResults([...results]);
          
          // Another yield to update UI
          await new Promise(resolve => setTimeout(resolve, 50));
          
        } catch (error) {
          console.error(`❌ Error processing image ${i + 1}:`, error);
          
          // Continue with other images instead of failing completely
          const errorResult = {
            id: Math.random().toString(36).substr(2, 9),
            file: imageFiles[i],
            url: URL.createObjectURL(imageFiles[i]),
            objects: [],
            resultId: null,
            processingTime: 0,
            totalSegments: 0,
            error: error instanceof Error ? error.message : 'Processing failed'
          };
          
          results.push(errorResult);
          setProcessedResults([...results]);
        }
      }
      
      // Final stage update
      await api.updatePerformanceStage('completed');
      
      // Stop monitoring
      stopMetricsPolling();
      stopElapsedTimer();
      const summaryResponse = await api.stopPerformanceMonitoring();
      
      setProcessingStage('completed');
      
      console.log('📊 Processing summary:', summaryResponse.summary);
      
      // Wait a bit to show completion state
      setTimeout(() => {
        onProcessingComplete(results.filter(r => !r.error)); // Only pass successful results
        onClose();
      }, 2000);
      
    } catch (error) {
      console.error('Processing failed:', error);
      setError(error instanceof Error ? error.message : 'Processing failed');
      stopMetricsPolling();
      stopElapsedTimer();
      
      try {
        await api.stopPerformanceMonitoring();
      } catch (stopError) {
        console.error('Error stopping monitoring:', stopError);
      }
      
      onProcessingError(error instanceof Error ? error.message : 'Processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  };

  const getStageProgress = (): number => {
    if (!metrics) return 0;
    return metrics.progress.percentage;
  };

  const renderMetricCard = (title: string, value: string, icon: React.ReactNode, color: string = 'blue') => (
    <Card className="bg-white/5 border-white/10">
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-${color}-500/20`}>
            {icon}
          </div>
          <div>
            <p className="text-sm text-gray-400">{title}</p>
            <p className="text-lg font-semibold text-white">{value}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderPerformanceChart = (data: number[], color: string, title: string) => {
    if (data.length < 2) return null;
    
    const maxValue = Math.max(...data, 100);
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = 100 - (value / maxValue) * 100;
      return `${x},${y}`;
    }).join(' ');
    
    return (
      <div className="bg-white/5 border border-white/10 rounded-lg p-3">
        <h5 className="text-xs text-gray-400 mb-2">{title}</h5>
        <div className="h-16 relative">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <linearGradient id={`gradient-${title}`} x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.3 }} />
                <stop offset="100%" style={{ stopColor: color, stopOpacity: 0.1 }} />
              </linearGradient>
            </defs>
            {data.length > 1 && (
              <>
                <polygon
                  points={`0,100 ${points} 100,100`}
                  fill={`url(#gradient-${title})`}
                />
                <polyline
                  points={points}
                  fill="none"
                  stroke={color}
                  strokeWidth="1"
                  vectorEffect="non-scaling-stroke"
                />
              </>
            )}
          </svg>
          <div className="absolute top-1 right-1 text-xs text-white bg-black/50 px-1 rounded">
            {data[data.length - 1]?.toFixed(0)}%
          </div>
        </div>
      </div>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 border-blue-500/20 text-white">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              🚀 AI Processing Center
            </DialogTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              disabled={isProcessing}
              className="text-gray-400 hover:text-white"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Error Display */}
          {error && (
            <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
              <p className="text-red-200">{error}</p>
            </div>
          )}

          {/* Processing Progress */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Processing Status</h3>
                <p className="text-sm text-gray-400">
                  {STAGE_DESCRIPTIONS[processingStage as keyof typeof STAGE_DESCRIPTIONS] || processingStage}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">Progress</p>
                <p className="text-lg font-semibold">
                  {currentImageIndex + (isProcessing ? 1 : 0)}/{totalImages} images
                </p>
              </div>
            </div>
            
            <Progress 
              value={getStageProgress()} 
              className="h-3 bg-gray-700/50 border border-gray-600/50"
            />
            
            <div className="flex items-center justify-between text-sm text-gray-400">
              <span>
                <Clock className="h-4 w-4 inline mr-1" />
                {formatTime(elapsedTime)}
              </span>
              <span>
                {processingStage === 'completed' ? (
                  <span className="text-green-400 flex items-center gap-1">
                    <CheckCircle className="h-4 w-4" />
                    Complete
                  </span>
                ) : isProcessing ? (
                  <span className="text-blue-400 flex items-center gap-1">
                    <Activity className="h-4 w-4 animate-pulse" />
                    Processing...
                  </span>
                ) : (
                  'Ready'
                )}
              </span>
            </div>
          </div>

          {/* Performance Metrics */}
          {metrics && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold">Real-time Performance</h3>
              
              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {renderMetricCard(
                  'CPU Usage',
                  `${metrics.cpu.usage_percent.toFixed(1)}%`,
                  <Cpu className="h-5 w-5 text-blue-400" />,
                  'blue'
                )}
                
                {metrics.gpu.available && renderMetricCard(
                  'GPU Usage',
                  `${metrics.gpu.usage_percent.toFixed(1)}%`,
                  <Zap className="h-5 w-5 text-yellow-400" />,
                  'yellow'
                )}
                
                {renderMetricCard(
                  'Memory',
                  `${metrics.memory.usage_percent.toFixed(1)}%`,
                  <HardDrive className="h-5 w-5 text-green-400" />,
                  'green'
                )}
                
                {renderMetricCard(
                  'Temperature',
                  `${metrics.cpu.temperature.toFixed(0)}°C`,
                  <Thermometer className="h-5 w-5 text-red-400" />,
                  'red'
                )}
              </div>

              {/* Real-time Performance Charts */}
              {performanceHistory.cpu.length > 1 && (
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-gray-300">Real-time Performance Charts</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {renderPerformanceChart(performanceHistory.cpu, '#3b82f6', 'CPU Usage')}
                    {metrics?.gpu?.available && renderPerformanceChart(performanceHistory.gpu, '#eab308', 'GPU Usage')}
                    {renderPerformanceChart(performanceHistory.memory, '#10b981', 'Memory Usage')}
                  </div>
                </div>
              )}

              {/* Detailed Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* CPU Details */}
                <Card className="bg-white/5 border-white/10">
                  <CardContent className="p-4 space-y-3">
                    <h4 className="font-semibold text-blue-400">CPU Performance</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Cores:</span>
                        <span>{metrics.cpu.cores}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Frequency:</span>
                        <span>{metrics.cpu.frequency_mhz.toFixed(0)} MHz</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Usage:</span>
                        <span>{metrics.cpu.usage_percent.toFixed(1)}%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* GPU Details (if available) */}
                {metrics.gpu.available && (
                  <Card className="bg-white/5 border-white/10">
                    <CardContent className="p-4 space-y-3">
                      <h4 className="font-semibold text-yellow-400 flex items-center gap-2">
                        <Zap className="h-4 w-4" />
                        GPU Performance
                      </h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Model:</span>
                          <span className="text-xs font-mono">{metrics.gpu.name || 'Unknown'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Usage:</span>
                          <span className="font-semibold">{metrics.gpu.usage_percent.toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Memory:</span>
                          <span>{(metrics.gpu.memory_used_mb / 1024).toFixed(1)}GB / {(metrics.gpu.memory_total_mb / 1024).toFixed(1)}GB</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Temp:</span>
                          <span className={`font-semibold ${metrics.gpu.temperature > 80 ? 'text-red-400' : metrics.gpu.temperature > 70 ? 'text-yellow-400' : 'text-green-400'}`}>
                            {metrics.gpu.temperature.toFixed(0)}°C
                          </span>
                        </div>
                        
                        {/* Enhanced metrics if available */}
                        {metrics.gpu.enhanced && (
                          <>
                            {metrics.gpu.enhanced.power_watts && (
                              <div className="flex justify-between">
                                <span className="text-gray-400">Power:</span>
                                <span>{metrics.gpu.enhanced.power_watts.toFixed(0)}W / {metrics.gpu.enhanced.power_limit_watts?.toFixed(0) || '?'}W</span>
                              </div>
                            )}
                            {metrics.gpu.enhanced.graphics_clock_mhz && (
                              <div className="flex justify-between">
                                <span className="text-gray-400">GPU Clock:</span>
                                <span>{metrics.gpu.enhanced.graphics_clock_mhz} MHz</span>
                              </div>
                            )}
                            {metrics.gpu.enhanced.memory_clock_mhz && (
                              <div className="flex justify-between">
                                <span className="text-gray-400">Mem Clock:</span>
                                <span>{metrics.gpu.enhanced.memory_clock_mhz} MHz</span>
                              </div>
                            )}
                            {metrics.gpu.enhanced.fan_speed_percent > 0 && (
                              <div className="flex justify-between">
                                <span className="text-gray-400">Fan Speed:</span>
                                <span>{metrics.gpu.enhanced.fan_speed_percent}%</span>
                              </div>
                            )}
                          </>
                        )}
                        
                        {metrics.gpu.torch_memory && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">PyTorch:</span>
                            <span>{metrics.gpu.torch_memory.allocated_mb.toFixed(0)}MB</span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Memory Details */}
                <Card className="bg-white/5 border-white/10">
                  <CardContent className="p-4 space-y-3">
                    <h4 className="font-semibold text-green-400">Memory Usage</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Total:</span>
                        <span>{metrics.memory.total_gb.toFixed(1)} GB</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Used:</span>
                        <span>{metrics.memory.used_gb.toFixed(1)} GB</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Available:</span>
                        <span>{metrics.memory.available_gb.toFixed(1)} GB</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Processing Info */}
                <Card className="bg-white/5 border-white/10">
                  <CardContent className="p-4 space-y-3">
                    <h4 className="font-semibold text-purple-400">Processing Info</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Total Images:</span>
                        <span>{totalImages}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Processed:</span>
                        <span>{metrics.progress?.processed_images || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Current Stage:</span>
                        <Badge variant="outline" className="text-xs">
                          {STAGE_DESCRIPTIONS[processingStage as keyof typeof STAGE_DESCRIPTIONS] || processingStage}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* Completed Results Preview */}
          {processedResults.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Processing Results</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {processedResults.map((result, index) => (
                  <Card key={result.id} className="bg-white/5 border-white/10">
                    <CardContent className="p-3">
                      <div className="aspect-square rounded-lg overflow-hidden bg-gray-700/50 mb-2">
                        <img
                          src={result.url}
                          alt={`Processed ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-400">{result.file.name}</p>
                        <p className="text-sm font-semibold">
                          {result.objects.reduce((sum: number, obj: any) => sum + obj.count, 0)} objects
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
