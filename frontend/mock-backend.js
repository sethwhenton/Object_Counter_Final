// Simple Node.js mock backend for demo purposes
// This replaces the Python Flask server temporarily

const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

// Enable CORS
app.use(cors());
app.use(express.json());

// Mock data
const mockObjectTypes = [
  { id: 1, name: 'person', description: 'People and humans' },
  { id: 2, name: 'car', description: 'Automobiles and vehicles' },
  { id: 3, name: 'bus', description: 'Buses and public transport vehicles' },
  { id: 4, name: 'bicycle', description: 'Bicycles and bikes' },
  { id: 5, name: 'motorcycle', description: 'Motorcycles and motorbikes' },
  { id: 6, name: 'dog', description: 'Dogs and canines' },
  { id: 7, name: 'cat', description: 'Domestic cats' },
  { id: 8, name: 'bird', description: 'Birds and flying animals' },
  { id: 9, name: 'tree', description: 'Trees and large plants' },
  { id: 10, name: 'building', description: 'Buildings and structures' },
  { id: 11, name: 'road', description: 'Roads and pathways' },
  { id: 12, name: 'sky', description: 'Sky and atmospheric elements' }
];

let mockResults = [];
let nextResultId = 1;

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    message: 'Mock AI Backend is running',
    database: 'connected',
    object_types: mockObjectTypes.length,
    pipeline_available: true,
    note: 'This is a mock backend for demo purposes'
  });
});

// Get object types
app.get('/api/object-types', (req, res) => {
  res.json({
    success: true,
    object_types: mockObjectTypes
  });
});

// Mock image processing
app.post('/api/count', upload.single('image'), (req, res) => {
  const { object_type, description } = req.body;
  
  if (!req.file) {
    return res.status(400).json({ error: 'No image uploaded' });
  }

  if (!object_type) {
    return res.status(400).json({ error: 'Object type is required' });
  }

  // Simulate processing time
  setTimeout(() => {
    // Mock prediction based on object type
    const mockCounts = {
      'person': Math.floor(Math.random() * 6) + 1,
      'car': Math.floor(Math.random() * 5) + 1,
      'bus': Math.floor(Math.random() * 3) + 1,
      'bicycle': Math.floor(Math.random() * 4) + 1,
      'motorcycle': Math.floor(Math.random() * 3) + 1,
      'dog': Math.floor(Math.random() * 3) + 1,
      'cat': Math.floor(Math.random() * 3) + 1,
      'bird': Math.floor(Math.random() * 8) + 1,
      'tree': Math.floor(Math.random() * 8) + 2,
      'building': Math.floor(Math.random() * 4) + 1,
      'road': 1,
      'sky': 1
    };

    const result = {
      success: true,
      result_id: nextResultId++,
      object_type: object_type,
      predicted_count: mockCounts[object_type] || Math.floor(Math.random() * 3) + 1,
      total_segments: Math.floor(Math.random() * 15) + 5,
      processing_time: Math.random() * 5 + 2, // 2-7 seconds
      image_path: `uploads/${req.file.filename}`,
      created_at: new Date().toISOString(),
      note: 'Mock AI prediction for demo'
    };

    mockResults.push(result);
    res.json(result);
  }, 2000); // 2 second delay to simulate AI processing
});

// Submit correction
app.put('/api/correct', (req, res) => {
  const { result_id, corrected_count } = req.body;

  if (!result_id || corrected_count === undefined) {
    return res.status(400).json({ error: 'Result ID and corrected count are required' });
  }

  const result = mockResults.find(r => r.result_id === result_id);
  if (!result) {
    return res.status(404).json({ error: 'Result not found' });
  }

  result.corrected_count = corrected_count;
  result.updated_at = new Date().toISOString();

  res.json({
    success: true,
    result_id: result_id,
    predicted_count: result.predicted_count,
    corrected_count: corrected_count,
    updated_at: result.updated_at,
    message: 'Correction saved successfully (mock backend)'
  });
});

// Get results
app.get('/api/results', (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const perPage = parseInt(req.query.per_page) || 10;
  const objectType = req.query.object_type;

  let filteredResults = mockResults;
  if (objectType) {
    filteredResults = mockResults.filter(r => r.object_type === objectType);
  }

  const startIndex = (page - 1) * perPage;
  const endIndex = startIndex + perPage;
  const paginatedResults = filteredResults.slice(startIndex, endIndex);

  res.json({
    success: true,
    results: paginatedResults,
    pagination: {
      page: page,
      per_page: perPage,
      total: filteredResults.length,
      pages: Math.ceil(filteredResults.length / perPage)
    }
  });
});

const PORT = 5000;
app.listen(PORT, '127.0.0.1', () => {
  console.log('🎭 Mock AI Backend Server running on http://127.0.0.1:5000');
  console.log('📍 Health check: http://127.0.0.1:5000/health');
  console.log('📍 Object types: http://127.0.0.1:5000/api/object-types');
  console.log('');
  console.log('✨ This is a MOCK backend for demo purposes');
  console.log('🔄 It simulates AI processing with random results');
  console.log('⚡ Processing time: 2 seconds (vs 30+ for real AI)');
});

