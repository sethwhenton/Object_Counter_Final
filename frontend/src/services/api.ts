// API service for backend communication
const API_BASE_URL = 'http://127.0.0.1:5000';

export interface ApiObjectCount {
  type: string;
  count: number;
}

export interface ApiCountResponse {
  success: boolean;
  result_id: string;
  object_type: string;
  predicted_count: number;
  total_segments: number;
  processing_time: number;
  image_path: string;
  created_at: string;
}

export interface ApiMultiObjectResponse {
  success: boolean;
  result_id: string;
  objects: ApiObjectCount[];
  total_objects: number;
  total_segments: number;
  processing_time: number;
  image_path: string;
  created_at: string;
}

export interface ApiSingleObjectResponse {
  success: boolean;
  result_id: string;
  object_type: string;
  predicted_count: number;
  total_segments: number;
  processing_time: number;
  image_path: string;
  created_at: string;
}

export interface ApiObjectType {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface ApiCorrectionResponse {
  success: boolean;
  result_id: string;
  predicted_count: number;
  corrected_count: number;
  updated_at: string;
  message: string;
}

export interface ApiHealthResponse {
  status: string;
  message: string;
  database?: string;
  object_types?: number;
  pipeline_available?: boolean;
}

class ObjectCountingAPI {
  
  /**
   * Check API health and database status
   */
  async healthCheck(): Promise<ApiHealthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Get all available object types from backend
   */
  async getObjectTypes(): Promise<ApiObjectType[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/object-types`);
      if (!response.ok) {
        throw new Error(`Failed to get object types: ${response.status}`);
      }
      const data = await response.json();
      return data.object_types;
    } catch (error) {
      console.error('Failed to get object types:', error);
      throw error;
    }
  }

  /**
   * Get object type names as a simple array for dropdown options
   */
  async getObjectTypeNames(): Promise<string[]> {
    try {
      const objectTypes = await this.getObjectTypes();
      return objectTypes.map(obj => obj.name);
    } catch (error) {
      console.error('Failed to get object type names:', error);
      // Return fallback options if API fails
      return ['car', 'person', 'dog', 'cat', 'tree', 'building'];
    }
  }

  /**
   * Upload image and get object count prediction
   * @param imageFile - The image file to upload
   * @param objectType - The type of object to count
   * @param description - Optional description
   */
  async countObjects(imageFile: File, objectType: string, description = ''): Promise<ApiCountResponse> {
    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('object_type', objectType);
      if (description) {
        formData.append('description', description);
      }

      const response = await fetch(`${API_BASE_URL}/api/count`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to process image: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Object counting failed:', error);
      throw error;
    }
  }

  /**
   * Upload image and get object detection and counting for a specific object type
   * @param imageFile - The image file to upload
   * @param objectType - The specific object type to detect and count
   * @param description - Optional description
   */
  async countAllObjects(imageFile: File, objectType: string, description = ''): Promise<ApiSingleObjectResponse> {
    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('object_type', objectType);
      if (description) {
        formData.append('description', description);
      }

      const response = await fetch(`${API_BASE_URL}/api/count-all`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to analyze image: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Object detection failed:', error);
      throw error;
    }
  }

  /**
   * Submit a correction for a prediction
   * @param resultId - The ID of the result to correct
   * @param correctedCount - The corrected count
   */
  async correctPrediction(resultId: string, correctedCount: number): Promise<ApiCorrectionResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/correct`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          result_id: resultId,
          corrected_count: correctedCount,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to submit correction: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Correction submission failed:', error);
      throw error;
    }
  }

  /**
   * Get results with pagination and filtering
   */
  async getResults(page = 1, perPage = 10, objectType: string | null = null) {
    try {
      let url = `${API_BASE_URL}/api/results?page=${page}&per_page=${perPage}`;
      if (objectType) {
        url += `&object_type=${objectType}`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to get results: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to get results:', error);
      throw error;
    }
  }

  /**
   * Performance monitoring methods
   */
  async startPerformanceMonitoring(totalImages: number = 1) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          total_images: totalImages,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start performance monitoring: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Performance monitoring start failed:', error);
      throw error;
    }
  }

  async stopPerformanceMonitoring() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to stop performance monitoring: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Performance monitoring stop failed:', error);
      throw error;
    }
  }

  async getPerformanceMetrics() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance/metrics`);
      
      if (!response.ok) {
        throw new Error(`Failed to get performance metrics: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Performance metrics failed:', error);
      throw error;
    }
  }

  async updatePerformanceStage(stage: string, imageIndex?: number) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance/update-stage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stage,
          image_index: imageIndex,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update performance stage: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Performance stage update failed:', error);
      throw error;
    }
  }

  async getPerformanceSummary() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance/summary`);
      
      if (!response.ok) {
        throw new Error(`Failed to get performance summary: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Performance summary failed:', error);
      throw error;
    }
  }

  /**
   * Get detailed information for a specific result
   */
  async getResultDetails(resultId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/${resultId}`);
      if (!response.ok) {
        throw new Error(`Failed to get result details: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to get result details:', error);
      throw error;
    }
  }

  /**
   * Delete a result and its associated data
   */
  async deleteResult(resultId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/${resultId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`Failed to delete result: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to delete result:', error);
      throw error;
    }
  }

  /**
   * Update feedback for a specific result
   */
  async updateResultFeedback(resultId: string, correctedCount: number, objectType?: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/${resultId}/feedback`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          corrected_count: correctedCount,
          object_type: objectType
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update feedback: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to update feedback:', error);
      throw error;
    }
  }

  /**
   * Delete multiple results in bulk
   */
  async bulkDeleteResults(resultIds: string[]) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/bulk-delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          result_ids: resultIds
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to bulk delete results: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to bulk delete results:', error);
      throw error;
    }
  }
}

// Export a singleton instance
export default new ObjectCountingAPI();



