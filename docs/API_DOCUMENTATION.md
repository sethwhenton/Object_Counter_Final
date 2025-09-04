# 📡 Object Counting API Documentation

## Base URL
```
http://127.0.0.1:5000
```

## Authentication
No authentication required for development version.

---

## Endpoints

### 🏥 Health Check

**GET** `/health`

Check API and database status.

**Response:**
```json
{
  "status": "healthy",
  "message": "Object Counting API is running",
  "database": "connected",
  "object_types": 9,
  "pipeline_available": true
}
```

---

### 🎯 Production Object Counting

**POST** `/api/count`

Upload an image and get object count prediction stored in database.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `image` (file): Image file (PNG, JPG, JPEG, GIF, BMP, TIFF)
  - `object_type` (string): Object type to count (car, cat, tree, dog, building, person, sky, ground, hardware)
  - `description` (string, optional): Description of the image

**Response:**
```json
{
  "success": true,
  "result_id": 1,
  "object_type": "car",
  "predicted_count": 3,
  "total_segments": 10,
  "processing_time": 27.5,
  "image_path": "uploads/unique_filename.jpg",
  "created_at": "2025-09-02T10:30:00"
}
```

**Error Response:**
```json
{
  "error": "Invalid object type: airplane",
  "available_types": ["car", "cat", "tree", "dog", "building", "person", "sky", "ground", "hardware"]
}
```

---

### ✏️ Correct Prediction

**PUT** `/api/correct`

Update a prediction with user-provided correction.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "result_id": 1,
  "corrected_count": 2
}
```

**Response:**
```json
{
  "success": true,
  "result_id": 1,
  "predicted_count": 3,
  "corrected_count": 2,
  "updated_at": "2025-09-02T10:35:00",
  "message": "Correction saved successfully"
}
```

---

### 📊 Get Results

**GET** `/api/results`

Retrieve all prediction results with pagination.

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Results per page (default: 10)
- `object_type` (string, optional): Filter by object type

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "created_at": "2025-09-02T10:30:00",
      "updated_at": "2025-09-02T10:35:00",
      "predicted_count": 3,
      "corrected_count": 2,
      "object_type_id": 1,
      "input_id": 1,
      "object_type_name": "car"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### 🏷️ Get Object Types

**GET** `/api/object-types`

Get all available object types.

**Response:**
```json
{
  "object_types": [
    {
      "id": 1,
      "created_at": "2025-09-02T10:00:00",
      "updated_at": "2025-09-02T10:00:00",
      "name": "car",
      "description": "Automobiles and vehicles"
    },
    {
      "id": 2,
      "name": "cat",
      "description": "Domestic cats"
    }
  ]
}
```

---

### 🧪 Test Pipeline (Development Only)

**POST** `/test-pipeline`

Test the AI pipeline without database storage.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `image` (file): Image file
  - `object_type` (string, optional): Object type (default: "car")

**Response:**
```json
{
  "success": true,
  "object_type": "car",
  "predicted_count": 3,
  "total_segments": 10,
  "processing_time": 27.5
}
```

---

## Database Schema

### object_types
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |
| name | VARCHAR(255) | Object type name |
| description | TEXT | Object type description |

### inputs
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |
| image_path | VARCHAR(500) | Path to uploaded image |
| description | TEXT | Image description |

### outputs
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |
| predicted_count | INTEGER | AI predicted count |
| corrected_count | INTEGER | User corrected count (nullable) |
| object_type_fk | INTEGER | Foreign key to object_types |
| input_fk | INTEGER | Foreign key to inputs |

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Not Found (invalid result_id) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (database issue) |

---

## Rate Limits
No rate limits in development version.

## File Upload Limits
- Maximum file size: 16MB
- Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF



