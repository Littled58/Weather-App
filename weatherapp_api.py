import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Load API key from file
with open("apikey.txt") as f:
    API_KEY = f.read().strip()

# Get current weather + AQI
def get_current_data(city_name):
    url = f"http://api.weatherapi.com/v1/current.json?q={city_name}&key={API_KEY}&aqi=yes"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Get 5-day forecast
def get_forecast(city_name):
    url = f"http://api.weatherapi.com/v1/forecast.json?q={city_name}&key={API_KEY}&days=5&aqi=yes"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Prepare DataFrame
def forecast_to_df(data):
    records = []
    for day in data["forecast"]["forecastday"]:
        date = day["date"]
        min_temp = day["day"]["mintemp_c"]
        max_temp = day["day"]["maxtemp_c"]
        avg_temp = day["day"]["avgtemp_c"]
        humidity = day["day"]["avghumidity"]
        desc = day["day"]["condition"]["text"]
        sunrise = day["astro"]["sunrise"]
        sunset = day["astro"]["sunset"]
        will_rain = "🌧️ Rain expected!" if day["day"]["daily_will_it_rain"] else "☀️ No rain expected"
        records.append([date, min_temp, max_temp, avg_temp, humidity, desc, sunrise, sunset, will_rain])
    columns = ["Date", "Min Temp (°C)", "Max Temp (°C)", "Avg Temp (°C)", "Humidity (%)", 
               "Description", "Sunrise", "Sunset", "Rain Alert"]
    return pd.DataFrame(records, columns=columns)

# Plot temperature trend
def plot_forecast(df, city):
    df["Date"] = pd.to_datetime(df["Date"])
    plt.figure(figsize=(10, 4))
    plt.plot(df["Date"], df["Avg Temp (°C)"], marker='o', linestyle='-', color='skyblue')
    plt.title(f"Temperature Trend - {city}")
    plt.xlabel("Date")
    plt.ylabel("Avg Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

# Streamlit App
def main():
    st.set_page_config(page_title="Weather Forecast App", page_icon="🌦️")
    st.title("🌤️ Weather Forecast App")
    st.markdown("Get 5-day forecast, temperature trends, air quality, sunrise/sunset, and rain alerts!")

    city = st.text_input("Enter city name")

    if city and st.button("Get Weather"):
        with st.spinner("Fetching weather data..."):
            current = get_current_data(city)
            forecast = get_forecast(city)

        if not current or not forecast:
            st.error("Could not retrieve data. Check city name or API.")
            return

        df = forecast_to_df(forecast)
        st.success(f"Weather forecast for {city}")
        st.dataframe(df)

        # Temperature Trend
        plot_forecast(df, city)

        # AQI & Air Quality
        aqi = current["current"]["air_quality"]
        co = aqi["co"]
        no2 = aqi["no2"]
        pm2_5 = aqi["pm2_5"]
        pm10 = aqi["pm10"]

        st.subheader("🌬️ Air Quality (current)")
        st.markdown(f"- CO: `{co:.2f}` µg/m³")
        st.markdown(f"- NO2: `{no2:.2f}` µg/m³")
        st.markdown(f"- PM2.5: `{pm2_5:.2f}` µg/m³")
        st.markdown(f"- PM10: `{pm10:.2f}` µg/m³")

        # Suggestion Message
        st.subheader("✅ Recommendation")

        # Define good weather & air quality criteria
        good_weather = (
            df["Rain Alert"].iloc[0] == "☀️ No rain expected"
            and 18 <= df["Avg Temp (°C)"].iloc[0] <= 30
        )
        good_air = all([
            co < 400,
            no2 < 40,
            pm2_5 < 25,
            pm10 < 50
        ])

        if good_weather and good_air:
            st.success("✅ It's a great day to go out! The weather and air quality are favorable. 🌿")
        elif not good_weather and good_air:
            st.info("🌧️ Air quality is fine, but you might want to carry an umbrella just in case.")
        elif good_weather and not good_air:
            st.warning("😷 The weather is nice, but air quality isn't ideal. Consider wearing a mask.")
        else:
            st.error("🚫 Not the best day to go out due to poor weather and air quality.")

if __name__ == "__main__":
    main()
