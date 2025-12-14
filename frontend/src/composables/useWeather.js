import { ref } from "vue";
import axios from "@/apiConfig.js";
import { settings } from "@/settings";

export function useWeather() {
  const weatherData = ref(null);
  const rawWeatherTemp = ref(null);

  const getWeatherInterpretation = (code) => {
    const codes = {
      0: { description: "Clear sky", icon: "☀️" },
      1: { description: "Mainly clear", icon: "🌤️" },
      2: { description: "Partly cloudy", icon: "⛅️" },
      3: { description: "Overcast", icon: "☁️" },
      45: { description: "Fog", icon: "🌫️" },
      48: { description: "Depositing rime fog", icon: "🌫️" },
      51: { description: "Light drizzle", icon: "🌦️" },
      53: { description: "Moderate drizzle", icon: "🌦️" },
      55: { description: "Dense drizzle", icon: "🌦️" },
      56: { description: "Light freezing drizzle", icon: "🥶" },
      57: { description: "Dense freezing drizzle", icon: "🥶" },
      61: { description: "Slight rain", icon: "🌧️" },
      63: { description: "Moderate rain", icon: "🌧️" },
      65: { description: "Heavy rain", icon: "🌧️" },
      66: { description: "Light freezing rain", icon: "🥶" },
      67: { description: "Heavy freezing rain", icon: "🥶" },
      71: { description: "Slight snow fall", icon: "🌨️" },
      73: { description: "Moderate snow fall", icon: "🌨️" },
      75: { description: "Heavy snow fall", icon: "🌨️" },
      77: { description: "Snow grains", icon: "🌨️" },
      80: { description: "Slight rain showers", icon: "🌦️" },
      81: { description: "Moderate rain showers", icon: "🌧️" },
      82: { description: "Violent rain showers", icon: "🌧️" },
      85: { description: "Slight snow showers", icon: "🌨️" },
      86: { description: "Heavy snow showers", icon: "🌨️" },
      95: { description: "Thunderstorm", icon: "⛈️" },
      96: { description: "Thunderstorm with hail", icon: "⛈️" },
      99: { description: "Thunderstorm with heavy hail", icon: "⛈️" },
    };
    return codes[code] || { description: "Unknown", icon: "🤷" };
  };

  const updateWeatherDisplay = () => {
    if (rawWeatherTemp.value === null || !weatherData.value) return;
    if (settings.units === "imperial") {
      const fahrenheit = rawWeatherTemp.value * (9 / 5) + 32;
      weatherData.value.temp = Math.round(fahrenheit);
    } else {
      weatherData.value.temp = Math.round(rawWeatherTemp.value);
    }
  };

  const fetchWeather = async (activityDetails) => {
    if (!activityDetails?.start_latlng?.length) return;
    const [lat, lon] = activityDetails.start_latlng;
    const startDate = new Date(activityDetails.start_date);
    const dateString = startDate.toISOString().split("T")[0];
    const apiUrl = `https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lon}&start_date=${dateString}&end_date=${dateString}&hourly=temperature_2m,weathercode&timezone=auto`;
    try {
      const response = await axios.get(apiUrl);
      const hourlyData = response.data.hourly;
      let closestHourIndex = 0;
      let minDiff = Infinity;
      hourlyData.time.forEach((timeStr, index) => {
        const diff = Math.abs(new Date(timeStr) - startDate);
        if (diff < minDiff) {
          minDiff = diff;
          closestHourIndex = index;
        }
      });
      rawWeatherTemp.value =
        response.data.hourly.temperature_2m[closestHourIndex];
      const weatherCode = hourlyData.weathercode[closestHourIndex];
      const interpretation = getWeatherInterpretation(weatherCode);
      weatherData.value = {
        temp: 0,
        description: interpretation.description,
        icon: interpretation.icon,
      };
      updateWeatherDisplay();
    } catch (error) {
      console.error("Error fetching weather:", error);
      weatherData.value = null;
    }
  };

  return {
    weatherData,
    fetchWeather,
    updateWeatherDisplay,
  };
}
