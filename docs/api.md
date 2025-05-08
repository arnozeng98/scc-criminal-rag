# SCC Criminal Cases RAG API Documentation

This document describes the API endpoints for the SCC Criminal Cases RAG system.

## Base URL

The API is available at the following base URL:

```bash
# When running locally
http://localhost:8000

# When running with reverse proxy
/api
```

### Reverse Proxy Configuration

The system now supports reverse proxy deployment. In such configurations, API endpoints are available at `/api` path prefix rather than a separate domain or port.

## Authentication

Currently, the API does not require authentication.

## Endpoints

### RAG Query

Query the RAG system with a question about Canadian Supreme Court criminal cases.

**URL**: `/rag/query`

**Method**: `POST`

**Request Body**:

```json
{
  "query": "What are the elements of self-defense in Canada?",
  "top_k": 5
}
```

Parameters:

- `query` (string, required): The question to ask the RAG system
- `top_k` (integer, optional, default: 5): Number of top chunks to retrieve

**Response**:

```json
{
  "answer": "Self-defense in Canada has several key elements...",
  "citations": [
    {
      "case_number": "35982",
      "title": "R. v. Smith",
      "date": "2015-04-20",
      "citation_text": "R. v. Smith (2015)",
      "score": 0.92,
      "mention": "R. v. Smith"
    }
  ],
  "context": [
    {
      "case_number": "35982",
      "title": "R. v. Smith",
      "date": "2015-04-20"
    }
  ],
  "retrieval_time": 0.35,
  "total_time": 2.75
}
```

Response fields:

- `answer` (string): Generated answer from the RAG system
- `citations` (array): List of citations used in the answer
  - `case_number` (string): Case number
  - `title` (string): Case title
  - `date` (string): Case date
  - `citation_text` (string): Formatted citation text
  - `score` (number): Relevance score
  - `mention` (string, optional): Case mention in the answer
- `context` (array): List of context chunks used to generate the answer
- `retrieval_time` (number): Time taken for retrieval (seconds)
- `total_time` (number): Total time taken (seconds)
- `error` (string, optional): Error message if any

**Status Codes**:

- `200 OK`: Successful query
- `400 Bad Request`: Invalid request (e.g., empty query)
- `500 Internal Server Error`: Server error

### Health Check

Check the health status of the RAG system.

**URL**: `/rag/health`

**Method**: `GET`

**Response**:

```json
{
  "status": "ok",
  "message": "RAG system is healthy"
}
```

**Status Codes**:

- `200 OK`: System is healthy
- `500 Internal Server Error`: System is not healthy

## Error Handling

Errors are returned with appropriate HTTP status codes and a JSON response containing an error message:

```json
{
  "detail": "Error message"
}
```

## Example Usage

### cURL

```bash
# Local development
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the elements of self-defense in Canada?",
    "top_k": 5
  }'

# With reverse proxy
curl -X POST "/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the elements of self-defense in Canada?",
    "top_k": 5
  }'
```

### Python

```python
import requests

# Configure API URL based on environment
API_URL = "http://localhost:8000"  # For local development
# API_URL = "/api"  # For reverse proxy deployment

response = requests.post(
    f"{API_URL}/rag/query",
    json={
        "query": "What are the elements of self-defense in Canada?",
        "top_k": 5
    }
)

result = response.json()
print(result["answer"])
```

### JavaScript

```javascript
// Configure API URL based on environment
const API_URL = process.env.REACT_APP_API_URL || '/api';

fetch(`${API_URL}/rag/query`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What are the elements of self-defense in Canada?",
    top_k: 5,
  }),
})
  .then((response) => response.json())
  .then((data) => {
    console.log(data.answer);
  });
```
