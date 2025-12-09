import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="AQI Forecast API",
    description="Serve 48-hour AQI forecasts using the trained XGBoost model.",
    version="1.0.0",
)

# Load trained artifacts
PIPELINE_PATH = Path(__file__).resolve().parent.parent / "aqi_pipeline.pkl"
pipeline_data = joblib.load(PIPELINE_PATH)
model = pipeline_data["model"]
FEATURES = pipeline_data["features"]
LAGS = pipeline_data["lags"]
ROLLS = pipeline_data["rolls"]
MAX_LOOKBACK = max(max(LAGS), max(ROLLS)) + 1

# AQI interpolation points (PM2.5 -> ISPU)
X_POINTS = np.array([0.0, 15.5, 55.4, 150.4, 250.4, 500.0])
Y_POINTS = np.array([0, 50, 100, 200, 300, 500])


class HistoryItem(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp in ISO 8601")
    pm25_density: float = Field(..., description="PM2.5 concentration (µg/m³)")
    aqi_ispu: Optional[float] = Field(
        None,
        description="Optional precomputed AQI/ISPU. If omitted, it will be derived from PM2.5.",
    )
    
    class Config:
        extra = "allow"  # Allow extra fields but ignore them


def compute_aqi_ispu(pm25: float) -> float:
    # Piecewise-linear interpolation based on Indonesian ISPU breakpoints
    return float(np.interp(pm25, X_POINTS, Y_POINTS))


def preprocess_history(items: List[HistoryItem]) -> pd.DataFrame:
    if not items:
        raise HTTPException(status_code=400, detail="History cannot be empty")

    df = pd.DataFrame([i.model_dump() for i in items])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=False)
    df = df.sort_values("timestamp").set_index("timestamp")
    
    # Keep only required columns: pm25_density and optionally aqi_ispu
    required_cols = ["pm25_density"]
    if "aqi_ispu" in df.columns:
        required_cols.append("aqi_ispu")
    df = df[required_cols]

    if "aqi_ispu" not in df or df["aqi_ispu"].isna().any():
        df["aqi_ispu"] = df["pm25_density"].apply(compute_aqi_ispu)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df = df[numeric_cols].resample("1H").mean().ffill()

    if len(df) < MAX_LOOKBACK:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least {MAX_LOOKBACK} hourly records to build features; got {len(df)}.",
        )

    return df.tail(MAX_LOOKBACK)


def add_time_features(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["hour"] = enriched.index.hour
    enriched["dayofweek"] = enriched.index.dayofweek
    enriched["month"] = enriched.index.month

    for l in LAGS:
        enriched[f"aqi_lag_{l}"] = enriched["aqi_ispu"].shift(l)
        enriched[f"pm25_lag_{l}"] = enriched["pm25_density"].shift(l)

    for r in ROLLS:
        enriched[f"aqi_roll_mean_{r}"] = enriched["aqi_ispu"].rolling(r).mean()
        enriched[f"aqi_roll_std_{r}"] = enriched["aqi_ispu"].rolling(r).std()

    return enriched


def forecast_48h(history: pd.DataFrame) -> pd.DataFrame:
    current = history.copy()
    future_predictions = []
    future_timestamps = []
    last_timestamp = current.index[-1]

    for i in range(1, 49):
        next_time = last_timestamp + timedelta(hours=i)
        next_row = pd.DataFrame(index=[next_time], columns=current.columns, dtype=float)
        next_row["pm25_density"] = current["pm25_density"].iloc[-1]
        next_row["aqi_ispu"] = np.nan  # Will be filled after prediction
        temp = pd.concat([current, next_row])

        df_feat = add_time_features(temp)
        df_feat = df_feat.dropna()

        if df_feat.empty:
            raise HTTPException(status_code=500, detail="Feature frame is empty during forecasting")

        X_next = df_feat.iloc[[-1]][FEATURES]
        pred_aqi = float(model.predict(X_next)[0])

        future_predictions.append(pred_aqi)
        future_timestamps.append(next_time)

        temp.loc[next_time, "aqi_ispu"] = pred_aqi
        current = temp

    return pd.DataFrame({"timestamp": future_timestamps, "pred_aqi": future_predictions}).set_index("timestamp")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True, "max_lookback_hours": MAX_LOOKBACK}


@app.post("/predict")
def predict(history: List[HistoryItem]):
    history_df = preprocess_history(history)
    forecast = forecast_48h(history_df)

    return {
        "forecast": [
            {"timestamp": ts.isoformat(), "pred_aqi": float(val)}
            for ts, val in forecast["pred_aqi"].items()
        ],
        "metadata": {
            "horizon_hours": 48,
            "required_history_hours": MAX_LOOKBACK,
            "features_used": FEATURES,
        },
    }
