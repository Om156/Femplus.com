import aiohttp
import asyncio
from typing import Dict, Any, Optional
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ThingSpeakService:
    def __init__(self):
        # Hardcoded credentials for now
        self.api_key = "NUUB6AC1A2WIE4YG"
        self.channel_id = "3073236"
        self.base_url = "https://api.thingspeak.com"
        
        logger.info(f"ThingSpeak service initialized with Channel ID: {self.channel_id}")
    
    async def fetch_latest_sensor_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the latest sensor data from ThingSpeak channel.
        Returns both gas sensor and TCS230 color sensor readings.
        """
        if not self.api_key or not self.channel_id:
            logger.error("ThingSpeak credentials not configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch latest data from the channel
                url = f"{self.base_url}/channels/{self.channel_id}/feeds/last.json"
                params = {
                    "api_key": self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        sensor_data = self._parse_sensor_data(data)
                        
                        # Add color analysis if color data is available
                        if sensor_data and any(key.startswith('color_') for key in sensor_data.keys()):
                            color_analysis = self.analyze_color_data(sensor_data)
                            sensor_data.update(color_analysis)
                        
                        return sensor_data
                    else:
                        logger.error(f"Failed to fetch data from ThingSpeak: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching data from ThingSpeak: {str(e)}")
            return None
    
    # Keep the old method for backward compatibility
    async def fetch_latest_gas_data(self) -> Optional[Dict[str, Any]]:
        """Backward compatibility method - calls fetch_latest_sensor_data"""
        return await self.fetch_latest_sensor_data()
    
    async def fetch_historical_gas_data(self, results: int = 10) -> Optional[list]:
        """
        Fetch historical gas sensor data from ThingSpeak channel.
        """
        if not self.api_key or not self.channel_id:
            logger.error("ThingSpeak credentials not configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/channels/{self.channel_id}/feeds.json"
                params = {
                    "api_key": self.api_key,
                    "results": results
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_historical_data(data)
                    else:
                        logger.error(f"Failed to fetch historical data from ThingSpeak: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching historical data from ThingSpeak: {str(e)}")
            return None
    
    def _parse_sensor_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the gas sensor data from ThingSpeak response.
        Maps field names to meaningful gas sensor parameters.
        """
        try:
            # Common sensor field mappings
            # Gas sensor fields
            field_mapping = {
                "field1": "co2_ppm",      # CO2 in parts per million
                "field2": "co_ppm",        # CO in parts per million  
                "field3": "no2_ppb",       # NO2 in parts per billion
                "field4": "o3_ppb",        # O3 in parts per billion
                "field5": "pm25_ugm3",     # PM2.5 in μg/m³
                "field6": "pm10_ugm3",     # PM10 in μg/m³
                "field7": "temperature_c", # Temperature in Celsius
                "field8": "humidity_pct",  # Humidity percentage
                # TCS230 Color sensor fields (if using additional fields)
                "field9": "color_red",     # Red color intensity
                "field10": "color_green",  # Green color intensity
                "field11": "color_blue",   # Blue color intensity
                "field12": "color_clear",  # Clear/white light intensity
                "field13": "color_hue",    # Calculated hue value
                "field14": "color_saturation", # Color saturation
                "field15": "color_brightness", # Overall brightness
                "field16": "color_temperature" # Color temperature in Kelvin
            }
            
            parsed_data = {
                "timestamp": data.get("created_at", datetime.utcnow().isoformat()),
                "sensor_id": data.get("entry_id", "unknown"),
                "raw_data": data
            }
            
            # Map the fields to gas sensor parameters
            for field, param_name in field_mapping.items():
                if field in data and data[field] is not None:
                    try:
                        value = data[field]
                        # Handle 'nan' string values
                        if str(value).lower() == 'nan':
                            parsed_data[param_name] = None
                        else:
                            parsed_data[param_name] = float(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not parse {field} value: {data[field]}")
                        parsed_data[param_name] = None
                else:
                    parsed_data[param_name] = None
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing gas sensor data: {str(e)}")
            return None
    
    def _parse_historical_data(self, data: Dict[str, Any]) -> list:
        """
        Parse historical gas sensor data from ThingSpeak response.
        """
        try:
            feeds = data.get("feeds", [])
            parsed_feeds = []
            
            for feed in feeds:
                parsed_feed = self._parse_gas_sensor_data(feed)
                if parsed_feed:
                    parsed_feeds.append(parsed_feed)
            
            return parsed_feeds
            
        except Exception as e:
            logger.error(f"Error parsing historical data: {str(e)}")
            return []
    
    def analyze_color_data(self, color_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze TCS230 color sensor data and provide health insights.
        """
        if not color_data:
            return {"color_analysis": "No color data available"}
        
        red = color_data.get("color_red", 0)
        green = color_data.get("color_green", 0)
        blue = color_data.get("color_blue", 0)
        clear = color_data.get("color_clear", 0)
        
        # Calculate color ratios for analysis
        # Handle None values
        red = red or 0
        green = green or 0
        blue = blue or 0
        clear = clear or 0
        
        total_rgb = red + green + blue
        if total_rgb > 0:
            red_ratio = red / total_rgb
            green_ratio = green / total_rgb
            blue_ratio = blue / total_rgb
        else:
            red_ratio = green_ratio = blue_ratio = 0
        
        # Calculate hue (0-360 degrees)
        max_val = max(red, green, blue)
        min_val = min(red, green, blue)
        diff = max_val - min_val
        
        if red > 0 or green > 0 or blue > 0:
            if diff == 0:
                hue = 0
            elif max_val == red:
                hue = (60 * ((green - blue) / diff) + 360) % 360
            elif max_val == green:
                hue = (60 * ((blue - red) / diff) + 120) % 360
            else:
                hue = (60 * ((red - green) / diff) + 240) % 360
        else:
            hue = 0
        
        # Calculate saturation (0-100%)
        if max_val > 0:
            saturation = (diff / max_val) * 100
        else:
            saturation = 0
        
        # Calculate brightness (0-100%)
        brightness = (total_rgb / 1023) * 100  # Assuming 10-bit ADC
        
        # Health analysis based on color
        health_indicators = []
        color_category = "Unknown"
        
        # Red dominance analysis (could indicate blood)
        if red_ratio > 0.6:
            health_indicators.append("High red content detected")
            color_category = "Red Dominant"
        elif red_ratio > 0.4:
            health_indicators.append("Moderate red content")
            color_category = "Reddish"
        
        # Green analysis (could indicate infection or unusual content)
        if green_ratio > 0.5:
            health_indicators.append("High green content - may indicate unusual composition")
            color_category = "Greenish"
        
        # Blue analysis (unusual for menstrual flow)
        if blue_ratio > 0.4:
            health_indicators.append("High blue content - unusual for normal flow")
            color_category = "Bluish"
        
        # Brightness analysis
        if brightness > 80:
            health_indicators.append("Very bright - may indicate high fluid content")
        elif brightness < 20:
            health_indicators.append("Very dark - may indicate concentrated content")
        
        # Overall color health assessment
        if not health_indicators:
            health_indicators.append("Color appears within normal range")
            color_category = "Normal"
        
        return {
            "color_analysis": {
                "hue": round(hue, 1),
                "saturation": round(saturation, 1),
                "brightness": round(brightness, 1),
                "red_ratio": round(red_ratio, 3),
                "green_ratio": round(green_ratio, 3),
                "blue_ratio": round(blue_ratio, 3),
                "color_category": color_category,
                "health_indicators": health_indicators,
                "raw_values": {
                    "red": red,
                    "green": green,
                    "blue": blue,
                    "clear": clear
                }
            }
        }
    
    def get_air_quality_index(self, gas_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Air Quality Index (AQI) based on gas sensor readings.
        This is a simplified AQI calculation - you may want to use more sophisticated algorithms.
        """
        if not gas_data:
            return {"aqi": 0, "category": "Unknown", "health_concern": "No data available"}
        
        # Simplified AQI calculation (you may want to implement proper AQI standards)
        aqi_components = []
        
        # CO2 AQI component (simplified)
        co2 = gas_data.get("co2_ppm")
        if co2 is not None:
            if co2 <= 400:
                aqi_components.append(0)  # Good
            elif co2 <= 1000:
                aqi_components.append(50)  # Moderate
            elif co2 <= 2000:
                aqi_components.append(100)  # Unhealthy for sensitive groups
            else:
                aqi_components.append(150)  # Unhealthy
        
        # PM2.5 AQI component
        pm25 = gas_data.get("pm25_ugm3")
        if pm25 is not None:
            if pm25 <= 12:
                aqi_components.append(0)
            elif pm25 <= 35.4:
                aqi_components.append(50)
            elif pm25 <= 55.4:
                aqi_components.append(100)
            else:
                aqi_components.append(150)
        
        # CO AQI component
        co = gas_data.get("co_ppm")
        if co is not None:
            if co <= 4.4:
                aqi_components.append(0)
            elif co <= 9.4:
                aqi_components.append(50)
            elif co <= 12.4:
                aqi_components.append(100)
            else:
                aqi_components.append(150)
        
        # Calculate overall AQI
        if aqi_components:
            max_aqi = max(aqi_components)
        else:
            max_aqi = 0
        
        # Determine category and health concern
        if max_aqi <= 50:
            category = "Good"
            health_concern = "Air quality is satisfactory"
        elif max_aqi <= 100:
            category = "Moderate"
            health_concern = "Air quality is acceptable for most people"
        elif max_aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
            health_concern = "Sensitive groups may experience health effects"
        else:
            category = "Unhealthy"
            health_concern = "Everyone may experience health effects"
        
        return {
            "aqi": max_aqi,
            "category": category,
            "health_concern": health_concern,
            "components": {
                "co2_ppm": co2,
                "pm25_ugm3": pm25,
                "co_ppm": co
            }
        }

# Global instance
thingspeak_service = ThingSpeakService()
