"""
Pollution Analysis Service
Analyzes air quality data and generates recommendations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.logger import logger


class PollutionAnalyzer:
    """Service for analyzing pollution data and generating recommendations"""
    
    # Threshold definitions (dapat disesuaikan)
    THRESHOLDS = {
        "gas_value": {
            "good": 0,
            "moderate": 50,
            "unhealthy_sensitive": 100,
            "unhealthy": 150,
            "very_unhealthy": 200,
            "hazardous": 300
        },
        "daily_max": 150,  # Maximum acceptable daily average
        "critical_level": 200,  # Critical warning level
    }
    
    def __init__(self):
        self.logger = logger
    
    def analyze_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze pollution data and generate insights
        
        Args:
            data: List of pollution readings from Google Sheets
            
        Returns:
            Analysis results with statistics and insights
        """
        try:
            if not data:
                return {"error": "No data to analyze"}
            
            # Extract gas values
            gas_values = []
            timestamps = []
            
            for row in data:
                try:
                    gas_val = float(row.get("Gas Value", 0))
                    gas_values.append(gas_val)
                    timestamps.append(row.get("Timestamp", ""))
                except (ValueError, TypeError):
                    continue
            
            if not gas_values:
                return {"error": "No valid gas values found"}
            
            # Calculate statistics
            avg_gas = sum(gas_values) / len(gas_values)
            max_gas = max(gas_values)
            min_gas = min(gas_values)
            
            # Count readings by level
            level_counts = self._categorize_readings(gas_values)
            
            # Get current status
            current_gas = gas_values[-1] if gas_values else 0
            current_level = self._get_pollution_level(current_gas)
            
            # Get trend
            trend = self._calculate_trend(gas_values[-10:] if len(gas_values) > 10 else gas_values)
            
            # Ensure all keys exist in level_counts (sometimes missing if no data in that category)
            default_level_counts = {
                "good": 0,
                "moderate": 0,
                "unhealthy_sensitive": 0,
                "unhealthy": 0,
                "very_unhealthy": 0,
                "hazardous": 0
            }
            # Merge with actual counts
            for key in level_counts:
                default_level_counts[key] = level_counts.get(key, 0)
            
            analysis = {
                "summary": {
                    "total_readings": len(gas_values),
                    "average_gas_value": round(avg_gas, 2),
                    "max_gas_value": round(max_gas, 2),
                    "min_gas_value": round(min_gas, 2),
                    "current_gas_value": round(current_gas, 2),
                    "current_level": current_level,
                    "trend": trend
                },
                "level_distribution": default_level_counts,
                "alerts": self._generate_alerts(avg_gas, max_gas, current_gas),
                "timestamp_range": {
                    "first": timestamps[0] if timestamps else None,
                    "last": timestamps[-1] if timestamps else None
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            return {"error": str(e)}
    
    def generate_recommendations(
        self,
        data: List[Dict[str, Any]],
        user_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on pollution data
        
        Args:
            data: Pollution data
            user_type: 'industrial' or 'general' user
            
        Returns:
            Recommendations and warnings
        """
        try:
            analysis = self.analyze_data(data)
            
            if "error" in analysis:
                return analysis
            
            summary = analysis["summary"]
            current_gas = summary["current_gas_value"]
            avg_gas = summary["average_gas_value"]
            max_gas = summary["max_gas_value"]
            current_level = summary["current_level"]
            
            recommendations = {
                "user_type": user_type,
                "pollution_status": current_level,
                "current_reading": current_gas,
                "warnings": [],
                "recommendations": [],
                "industrial_alerts": [],
                "health_advice": []
            }
            
            # Industrial warnings
            if user_type == "industrial":
                if max_gas >= self.THRESHOLDS["critical_level"]:
                    recommendations["industrial_alerts"].append({
                        "level": "CRITICAL",
                        "message": f"⚠️ CRITICAL: Maximum pollutant level reached ({max_gas})! Immediate action required.",
                        "action": "Stop operations immediately and investigate source of pollution"
                    })
                
                if avg_gas >= self.THRESHOLDS["daily_max"]:
                    recommendations["industrial_alerts"].append({
                        "level": "HIGH",
                        "message": f"⚠️ WARNING: Daily average ({avg_gas}) exceeds acceptable limit ({self.THRESHOLDS['daily_max']})",
                        "action": "Reduce emissions and implement pollution control measures"
                    })
            
            # General warnings for high pollution
            if current_gas >= self.THRESHOLDS["gas_value"]["hazardous"]:
                recommendations["warnings"].append({
                    "level": "HAZARDOUS",
                    "message": "🔴 HAZARDOUS air quality detected!",
                    "severity": "critical"
                })
            elif current_gas >= self.THRESHOLDS["gas_value"]["very_unhealthy"]:
                recommendations["warnings"].append({
                    "level": "VERY UNHEALTHY",
                    "message": "🟠 Very unhealthy air quality!",
                    "severity": "high"
                })
            elif current_gas >= self.THRESHOLDS["gas_value"]["unhealthy"]:
                recommendations["warnings"].append({
                    "level": "UNHEALTHY",
                    "message": "🟡 Unhealthy air quality detected",
                    "severity": "moderate"
                })
            
            # Generate specific recommendations
            recommendations["recommendations"] = self._get_recommendations_by_level(
                current_level,
                current_gas
            )
            
            # Health advice
            recommendations["health_advice"] = self._get_health_advice(current_level)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def _get_pollution_level(self, gas_value: float) -> str:
        """Determine pollution level based on gas value"""
        if gas_value >= self.THRESHOLDS["gas_value"]["hazardous"]:
            return "Hazardous"
        elif gas_value >= self.THRESHOLDS["gas_value"]["very_unhealthy"]:
            return "Very Unhealthy"
        elif gas_value >= self.THRESHOLDS["gas_value"]["unhealthy"]:
            return "Unhealthy"
        elif gas_value >= self.THRESHOLDS["gas_value"]["unhealthy_sensitive"]:
            return "Unhealthy for Sensitive Groups"
        elif gas_value >= self.THRESHOLDS["gas_value"]["moderate"]:
            return "Moderate"
        else:
            return "Good"
    
    def _categorize_readings(self, gas_values: List[float]) -> Dict[str, int]:
        """Categorize all readings by pollution level"""
        counts = {
            "good": 0,
            "moderate": 0,
            "unhealthy_sensitive": 0,
            "unhealthy": 0,
            "very_unhealthy": 0,
            "hazardous": 0
        }
        
        for val in gas_values:
            level = self._get_pollution_level(val)
            if level == "Good":
                counts["good"] += 1
            elif level == "Moderate":
                counts["moderate"] += 1
            elif level == "Unhealthy for Sensitive Groups":
                counts["unhealthy_sensitive"] += 1
            elif level == "Unhealthy":
                counts["unhealthy"] += 1
            elif level == "Very Unhealthy":
                counts["very_unhealthy"] += 1
            else:
                counts["hazardous"] += 1
        
        return counts
    
    def _calculate_trend(self, recent_values: List[float]) -> str:
        """Calculate trend from recent values"""
        if len(recent_values) < 2:
            return "stable"
        
        # Simple linear trend
        mid_point = len(recent_values) // 2
        first_half_avg = sum(recent_values[:mid_point]) / mid_point
        second_half_avg = sum(recent_values[mid_point:]) / (len(recent_values) - mid_point)
        
        diff = second_half_avg - first_half_avg
        
        if diff > 10:
            return "increasing"
        elif diff < -10:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_alerts(
        self,
        avg_gas: float,
        max_gas: float,
        current_gas: float
    ) -> List[Dict[str, str]]:
        """Generate alerts based on thresholds"""
        alerts = []
        
        if max_gas >= self.THRESHOLDS["critical_level"]:
            alerts.append({
                "type": "critical",
                "message": f"Maximum pollution level ({max_gas}) reached critical threshold!"
            })
        
        if avg_gas >= self.THRESHOLDS["daily_max"]:
            alerts.append({
                "type": "warning",
                "message": f"Daily average ({avg_gas}) exceeds recommended limit!"
            })
        
        if current_gas >= self.THRESHOLDS["gas_value"]["unhealthy"]:
            alerts.append({
                "type": "current",
                "message": f"Current pollution level ({current_gas}) is unhealthy!"
            })
        
        return alerts
    
    def _get_recommendations_by_level(
        self,
        level: str,
        gas_value: float
    ) -> List[str]:
        """Get recommendations based on pollution level"""
        recommendations = []
        
        if level == "Good":
            recommendations = [
                "✅ Air quality is good. Safe for outdoor activities.",
                "Continue normal activities",
                "Good time for exercise outdoors"
            ]
        elif level == "Moderate":
            recommendations = [
                "⚠️ Air quality is acceptable for most people",
                "Unusually sensitive people should limit prolonged outdoor exertion",
                "Consider reducing intensive outdoor activities if you're sensitive"
            ]
        elif level in ["Unhealthy for Sensitive Groups", "Unhealthy"]:
            recommendations = [
                "🟡 Reduce prolonged or heavy outdoor exertion",
                "People with respiratory conditions should limit outdoor activities",
                "Keep windows closed if possible",
                "Consider using air purifiers indoors",
                "Monitor air quality regularly"
            ]
        elif level == "Very Unhealthy":
            recommendations = [
                "🟠 Avoid prolonged outdoor exertion",
                "Keep outdoor activities short",
                "Stay indoors as much as possible",
                "Use air purifiers or masks if going outside",
                "People with heart or lung disease should remain indoors"
            ]
        else:  # Hazardous
            recommendations = [
                "🔴 URGENT: Avoid all outdoor activities",
                "Everyone should remain indoors",
                "Keep windows and doors closed",
                "Run air purifiers on high if available",
                "Consider evacuation if pollution persists",
                "Seek medical attention if experiencing symptoms"
            ]
        
        return recommendations
    
    def _get_health_advice(self, level: str) -> List[str]:
        """Get health advice based on pollution level"""
        advice = []
        
        if level in ["Unhealthy", "Very Unhealthy", "Hazardous"]:
            advice = [
                "💊 Take prescribed medications if you have respiratory conditions",
                "🏥 Seek medical help if you experience breathing difficulties",
                "😷 Wear N95 masks when going outside",
                "💧 Stay hydrated",
                "🚭 Avoid smoking or exposure to other pollutants"
            ]
        elif level in ["Moderate", "Unhealthy for Sensitive Groups"]:
            advice = [
                "Monitor symptoms if you have respiratory conditions",
                "Keep inhaler handy if prescribed",
                "Stay hydrated"
            ]
        else:
            advice = [
                "Maintain regular health checkups",
                "Stay informed about air quality"
            ]
        
        return advice


# Create global instance
pollution_analyzer = PollutionAnalyzer()

