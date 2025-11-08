## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Google Cloud service account with Sheets API enabled
- Google Gemini API key

### Installation

1. Clone and setup:
```bash
cd ai-Bojongsantozzz
cp .env.example .env
```

2. Configure environment variables in `.env`:


3. Share your Google Sheet with the service account email:
```
api-gspreadsheet@gen-lang-client-0297593898.iam.gserviceaccount.com
```

4. Enable Google Sheets API in your Google Cloud project.

### Running the Application

#### Using Docker (Recommended)

```bash
./run.sh docker
```

Or manually:
```bash
docker-compose up --build
```

#### Running Locally

```bash
./run.sh local
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Access the API

- API Base URL: http://localhost:8000
- Interactive Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## API Endpoints

### Pollution Monitoring

#### GET /api/pollution/current-status
Get current pollution status in real-time.

```bash
curl http://localhost:8000/api/pollution/current-status
```

Response:
```json
{
  "timestamp": "2025-11-06 22:34:13",
  "gas_value": 50.0,
  "pollution_level": "Moderate",
  "is_safe": true
}
```

#### GET /api/pollution/analyze
Get statistical analysis of pollution data.

Parameters:
- `limit` (optional): Number of records to analyze (default: 100)

```bash
curl "http://localhost:8000/api/pollution/analyze?limit=50"
```

Response:
```json
{
  "summary": {
    "total_readings": 50,
    "average_gas_value": 68.12,
    "max_gas_value": 123.0,
    "current_level": "Moderate",
    "trend": "decreasing"
  },
  "level_distribution": {
    "good": 6,
    "moderate": 41,
    "unhealthy_sensitive": 3
  }
}
```

#### POST /api/pollution/recommendations
Get recommendations based on pollution data.

Request:
```json
{
  "user_type": "general",
  "limit": 50
}
```

User types: `general` (public) or `industrial` (factory/industry)

```bash
curl -X POST "http://localhost:8000/api/pollution/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_type": "general", "limit": 50}'
```

Response:
```json
{
  "pollution_status": "Moderate",
  "current_reading": 50.0,
  "recommendations": [
    "Air quality is acceptable for most people",
    "Sensitive people should limit prolonged outdoor exertion"
  ],
  "health_advice": [
    "Monitor symptoms if you have respiratory conditions",
    "Stay hydrated"
  ]
}
```

For industrial users:
```bash
curl -X POST "http://localhost:8000/api/pollution/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_type": "industrial", "limit": 100}'
```

Response includes `industrial_alerts` when pollution exceeds thresholds:
```json
{
  "industrial_alerts": [
    {
      "level": "CRITICAL",
      "message": "Maximum pollutant level reached",
      "action": "Stop operations immediately"
    }
  ]
}
```

#### POST /api/pollution/smart-recommendations
Get AI-powered recommendations using Google Gemini.

Request:
```json
{
  "user_type": "general",
  "include_context": true,
  "limit": 50
}
```

```bash
curl -X POST "http://localhost:8000/api/pollution/smart-recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_type": "general", "limit": 50}'
```

#### GET /api/pollution/alerts
Check for active pollution alerts.

```bash
curl "http://localhost:8000/api/pollution/alerts?limit=50"
```

Response:
```json
{
  "has_alerts": false,
  "alert_count": 0,
  "current_level": "Moderate",
  "trend": "decreasing"
}
```

### Data Management

#### GET /api/data/sheets/info
Get information about the connected Google Sheet.

```bash
curl http://localhost:8000/api/data/sheets/info
```

#### GET /api/data/sheets
Retrieve data from Google Sheets.

Parameters:
- `sheet_name` (optional): Specific worksheet name
- `limit` (optional): Maximum records (default: 100)

```bash
curl "http://localhost:8000/api/data/sheets?limit=10"
```

#### POST /api/data/sheets/query
Query sheets with filters.

```bash
curl -X POST "http://localhost:8000/api/data/sheets/query" \
  -H "Content-Type: application/json" \
  -d '{"filters": {"Status": "Good"}, "limit": 20}'
```

### AI Features

#### POST /api/ai/query
Query using RAG (Retrieval-Augmented Generation).

```bash
curl -X POST "http://localhost:8000/api/ai/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the air quality trend?", "top_k": 5}'
```

#### POST /api/ai/reindex
Reindex documents from Google Sheets for RAG.

```bash
curl -X POST "http://localhost:8000/api/ai/reindex"
```

#### GET /api/ai/stats
Get RAG engine statistics.

```bash
curl http://localhost:8000/api/ai/stats
```

## Pollution Levels

| Gas Value | Level | Description |
|-----------|-------|-------------|
| 0-49 | Good | Safe for everyone |
| 50-99 | Moderate | Acceptable for most people |
| 100-149 | Unhealthy for Sensitive Groups | Sensitive people should limit outdoor activity |
| 150-199 | Unhealthy | Everyone should reduce outdoor activity |
| 200-299 | Very Unhealthy | Everyone should avoid outdoor activity |
| 300+ | Hazardous | Health alert - everyone should stay indoors |

## Testing

### Test All Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Current status
curl http://localhost:8000/api/pollution/current-status

# Analysis
curl "http://localhost:8000/api/pollution/analyze?limit=50"

# Recommendations
curl -X POST "http://localhost:8000/api/pollution/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_type": "general", "limit": 50}'
```

### Google Sheets Setup

1. Create Google Cloud Project
2. Enable Google Sheets API
3. Create service account and download credentials
4. Share your Google Sheet with service account email
5. Add credentials JSON to `.env` as single-line string


## Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up --build

# Restart
docker-compose restart
```

## Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Style

```bash
black app/
isort app/
```

## Troubleshooting

### Google Sheets not connected

1. Verify service account credentials are correct
2. Ensure Google Sheet is shared with service account email
3. Check Sheet ID in `.env`
4. Verify Google Sheets API is enabled
5. Restart API: `docker-compose restart`

### Gemini API errors

1. Check API key is valid
2. Verify API key has not expired
3. Ensure you have available quota
4. Check model name is correct

### No data found

1. Verify Sheet ID is correct
2. Check sheet has data in expected format
3. Ensure headers are in row 3
4. Verify data starts from row 4

### Docker issues

```bash
# Clean everything
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up
```

## Technology Stack

- FastAPI: Web framework
- Pydantic: Data validation
- Google Sheets API: Data source
- Google Gemini: AI model
- Sentence Transformers: Text embeddings
- FAISS: Vector similarity search
- Docker: Containerization
- Uvicorn: ASGI server
