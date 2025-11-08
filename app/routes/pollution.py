"""
Pollution analysis and recommendation endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.pollution_schemas import (
    PollutionAnalysisResponse,
    RecommendationRequest,
    RecommendationResponse,
    SmartRecommendationRequest,
    SmartRecommendationResponse
)
from app.services.pollution_analyzer import pollution_analyzer
from app.services.sheets_reader import sheets_reader
from app.services.gemini_client import gemini_client
from app.services.rag_engine import rag_engine
from app.core.logger import logger

router = APIRouter()


@router.get("/analyze")
async def analyze_pollution(
    limit: int = Query(100, description="Number of recent records to analyze")
):
    """
    Analyze pollution data from Google Sheets
    Returns statistical analysis and insights
    """
    try:
        logger.info(f"Analyzing pollution data (limit: {limit})")
        
        # Get data from sheets
        data = sheets_reader.get_all_data()
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found in Google Sheets")
        
        # Limit to recent records
        recent_data = data[-limit:] if len(data) > limit else data
        
        # Analyze
        analysis = pollution_analyzer.analyze_data(recent_data)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing pollution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get recommendations based on pollution data
    
    For industrial users:
    - Warnings when reaching max pollutant levels
    - Critical alerts for immediate action
    
    For general users:
    - Health recommendations
    - Activity suggestions based on pollution levels
    """
    try:
        logger.info(f"Generating recommendations for {request.user_type} user")
        
        # Get data from sheets
        data = sheets_reader.get_all_data()
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found in Google Sheets")
        
        # Limit to recent records
        recent_data = data[-request.limit:] if len(data) > request.limit else data
        
        # Generate recommendations
        recommendations = pollution_analyzer.generate_recommendations(
            recent_data,
            user_type=request.user_type
        )
        
        if "error" in recommendations:
            raise HTTPException(status_code=500, detail=recommendations["error"])
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-recommendations")
async def get_smart_recommendations(request: SmartRecommendationRequest):
    """
    Get AI-powered smart recommendations using Gemini
    Combines statistical analysis with AI insights
    """
    try:
        logger.info(f"Generating smart recommendations for {request.user_type}")
        
        # Get data from sheets
        data = sheets_reader.get_all_data()
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found in Google Sheets")
        
        # Limit to recent records
        recent_data = data[-request.limit:] if len(data) > request.limit else data
        
        # Get statistical analysis
        analysis = pollution_analyzer.analyze_data(recent_data)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        # Prepare context for AI
        context = f"""
Air Quality Monitoring Data Analysis:

Summary Statistics:
- Total Readings: {analysis['summary']['total_readings']}
- Current Gas Value: {analysis['summary']['current_gas_value']}
- Average Gas Value: {analysis['summary']['average_gas_value']}
- Maximum Gas Value: {analysis['summary']['max_gas_value']}
- Current Level: {analysis['summary']['current_level']}
- Trend: {analysis['summary']['trend']}

Level Distribution:
- Good: {analysis['level_distribution']['good']} readings
- Moderate: {analysis['level_distribution']['moderate']} readings
- Unhealthy: {analysis['level_distribution']['unhealthy']} readings
- Very Unhealthy: {analysis['level_distribution']['very_unhealthy']} readings
- Hazardous: {analysis['level_distribution']['hazardous']} readings

Recent Readings: {[f"{row.get('Timestamp')}: {row.get('Gas Value')}" for row in recent_data[-5:]]}
"""
        
        # Generate AI recommendation
        if request.user_type == "industrial":
            prompt = f"""Based on this air quality data, provide specific recommendations for industrial operations:

{context}

Please provide:
1. Critical warnings if pollution levels are dangerous
2. Operational recommendations to reduce emissions
3. Compliance considerations
4. Action items for different pollution levels
"""
        else:
            prompt = f"""Based on this air quality data, provide health and safety recommendations for the general public:

{context}

Please provide:
1. Current health risk assessment
2. Recommended activities or restrictions
3. Health protection measures
4. When to seek medical attention
"""
        
        # Get AI response
        ai_response = gemini_client.generate_response(prompt)
        
        # Get relevant context from RAG (if initialized)
        retrieved_context = []
        if rag_engine.documents:
            retrieved = rag_engine.retrieve(
                f"pollution level {analysis['summary']['current_level']}",
                top_k=3
            )
            retrieved_context = [doc for doc, score in retrieved]
        
        return {
            "analysis": analysis,
            "ai_recommendation": ai_response,
            "retrieved_context": retrieved_context,
            "user_type": request.user_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating smart recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current-status")
async def get_current_status():
    """
    Get current pollution status (latest reading)
    Quick endpoint for real-time monitoring
    """
    try:
        logger.info("Getting current pollution status")
        
        # Get latest data
        data = sheets_reader.get_all_data()
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Get latest reading
        latest = data[-1]
        
        try:
            gas_value = float(latest.get("Gas Value", 0))
            level = pollution_analyzer._get_pollution_level(gas_value)
            
            return {
                "timestamp": latest.get("Timestamp"),
                "gas_value": gas_value,
                "air_quality": latest.get("Air Quality %"),
                "status": latest.get("Status"),
                "sensor_active": latest.get("Sensor Aktif"),
                "pollution_level": level,
                "is_safe": level in ["Good", "Moderate"]
            }
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=500, detail=f"Invalid data format: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_active_alerts(
    limit: int = Query(50, description="Number of recent records to check")
):
    """
    Get active alerts and warnings
    Quick endpoint to check if there are any pollution warnings
    """
    try:
        logger.info("Checking for active alerts")
        
        # Get data
        data = sheets_reader.get_all_data()
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Analyze recent data
        recent_data = data[-limit:] if len(data) > limit else data
        analysis = pollution_analyzer.analyze_data(recent_data)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return {
            "has_alerts": len(analysis["alerts"]) > 0,
            "alert_count": len(analysis["alerts"]),
            "alerts": analysis["alerts"],
            "current_level": analysis["summary"]["current_level"],
            "trend": analysis["summary"]["trend"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

