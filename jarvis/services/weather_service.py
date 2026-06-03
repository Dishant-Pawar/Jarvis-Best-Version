import requests
from typing import Dict, Any, Optional
from jarvis.utils.logger import logger
from jarvis.config.settings import DEFAULT_CITY

class WeatherService:
    @staticmethod
    def get_weather(city: Optional[str] = None) -> str:
        """Fetch current weather for a city. If no city is specified, uses the default city."""
        if not city or not city.strip():
            city = DEFAULT_CITY

        logger.info(f"Fetching weather for: {city}")
        city_encoded = requests.utils.quote(city)
        url = f"https://wttr.in/{city_encoded}?format=j1"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current_condition = data['current_condition'][0]
                temp_c = current_condition['temp_C']
                desc = current_condition['weatherDesc'][0]['value']
                humidity = current_condition['humidity']
                wind_speed = current_condition['windspeedKmph']
                
                report = (
                    f"The weather in {city} is currently {desc}. "
                    f"The temperature is {temp_c} degrees Celsius. "
                    f"Humidity is at {humidity} percent, and the wind is blowing at {wind_speed} kilometers per hour."
                )
                logger.info(f"Weather fetched successfully: {report}")
                return report
            else:
                logger.warning(f"wttr.in JSON API returned status {response.status_code}. Trying text fallback.")
        except Exception as e:
            logger.error(f"Error fetching weather JSON: {e}. Trying text fallback.")

        # Fallback to plain text format
        try:
            # format=%C+and+%t -> "Light rain and +14°C"
            fallback_url = f"https://wttr.in/{city_encoded}?format=%C+and+%t"
            response = requests.get(fallback_url, timeout=5)
            if response.status_code == 200:
                report = f"The weather in {city} is {response.text.strip()}."
                logger.info(f"Fallback weather fetched successfully: {report}")
                return report
        except Exception as e:
            logger.error(f"Weather text fallback also failed: {e}")
            
        return f"Sorry, I was unable to retrieve the weather report for {city} right now."
