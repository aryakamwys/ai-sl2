# AQI Forecast API

REST API to serve 48-hour AQI (ISPU) forecasts using the trained XGBoost model (`aqi_pipeline.pkl`).

## Quick start
1) Install deps:
```bash
pip install -r api/requirements.txt
```
2) Run the service:
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```
3) Open docs: http://localhost:8000/docs

## Endpoints
- `GET /health` — service health and model metadata.
- `POST /predict` — returns 48h AQI forecast.

### Request body (`/predict`)
Array of historical points (ISO timestamps are required). Provide **>= 25** hourly records (because `max(lags, rolls)+1 = 25`). Example:
```json
[
  {"timestamp": "2024-05-01T00:00:00", "pm25_density": 22.5},
  {"timestamp": "2024-05-01T01:00:00", "pm25_density": 24.1},
  ...
]
```
Fields:
- `timestamp` (string, ISO 8601)
- `pm25_density` (float, µg/m³)
- `aqi_ispu` (float, optional) — if omitted, the API derives it from PM2.5 using ISPU breakpoints.

### Response (`/predict`)
```json
{
  "forecast": [
    {"timestamp": "2024-05-02T01:00:00", "pred_aqi": 87.4},
    {"timestamp": "2024-05-02T02:00:00", "pred_aqi": 90.1}
  ],
  "metadata": {
    "horizon_hours": 48,
    "required_history_hours": 25,
    "features_used": ["hour", "dayofweek", ...]
  }
}
```

## Data requirements
- At least 25 consecutive hourly data points.
- Required signals: `timestamp`, `pm25_density`. Optional: `aqi_ispu` (else derived).
- The API resamples to hourly mean and forward-fills small gaps before feature building.

## Prediction pipeline (server-side)
1) Validate and sort historical records by timestamp.
2) Derive `aqi_ispu` from PM2.5 (ISPU interpolation) if missing.
3) Resample to hourly means, forward-fill gaps, keep the latest 25 hours.
4) Add time features (`hour`, `dayofweek`, `month`), lags, and rolling stats.
5) For each of the 48 steps: create a new row, reuse last PM2.5 (persistence), rebuild features, predict AQI, append to history, repeat.
6) Return the 48 predicted AQI values with timestamps.

## Deployment notes
- Keep `aqi_pipeline.pkl` in the project root (one level above `api/`).
- Use a process manager or container to run `uvicorn`. Example Docker command:
  ```bash
  uvicorn api.app:app --host 0.0.0.0 --port 8000
  ```
- Monitor memory: XGBoost model is light; API uses pandas for feature prep.

## CI/CD checklist for the dev team
- Install deps and run a short contract test (e.g., POST `/predict` with a 25-point fixture and assert 48 outputs).
- Version the model artifact (`aqi_pipeline.pkl`) and pin package versions from `api/requirements.txt`.
- Expose `/health` for liveness probes; add `/predict` latency/error logging.
- If deploying behind TLS/ingress, ensure body size limits allow at least ~10 KB payloads.
