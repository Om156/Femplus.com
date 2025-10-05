# ThingSpeak Gas Sensor Integration Setup

This guide explains how to set up the ThingSpeak integration for gas sensor data in your FemPlus application.

## Prerequisites

1. A ThingSpeak account (free at https://thingspeak.com/)
2. A gas sensor device that can send data to ThingSpeak
3. Your ThingSpeak API key and Channel ID

## Setup Steps

### 1. Create a ThingSpeak Channel

1. Go to https://thingspeak.com/ and sign in
2. Click "New Channel"
3. Fill in the channel details:
   - Name: "Gas Sensor Data" (or any name you prefer)
   - Description: "Air quality monitoring for FemPlus"
4. Configure the fields (these are the default mappings):
   - Field 1: CO2 (ppm)
   - Field 2: CO (ppm)
   - Field 3: NO2 (ppb)
   - Field 4: O3 (ppb)
   - Field 5: PM2.5 (μg/m³)
   - Field 6: PM10 (μg/m³)
   - Field 7: Temperature (°C)
   - Field 8: Humidity (%)
5. Save the channel

### 2. Get Your API Credentials

1. Go to your channel page
2. Click on "API Keys" tab
3. Copy your "Write API Key" and "Channel ID"

### 3. Configure Environment Variables

Create a `.env` file in your project root with:

```env
# ThingSpeak Configuration
THINGSPEAK_API_KEY=your_write_api_key_here
THINGSPEAK_CHANNEL_ID=your_channel_id_here
```

### 4. Install Dependencies

Make sure you have the required Python packages:

```bash
pip install -r requirements.txt
```

### 5. Test the Integration

1. Start your FastAPI server:

   ```bash
   uvicorn app.main:app --reload
   ```

2. Open the frontend and go to the "Add Reading" section
3. Click on the "Gas Sensor (ThingSpeak)" tab
4. Click "Fetch Latest Gas Data" to test the connection

## Field Mappings

The application expects the following field mappings in your ThingSpeak channel:

| Field   | Parameter   | Description            | Unit  |
| ------- | ----------- | ---------------------- | ----- |
| Field 1 | CO2         | Carbon Dioxide         | ppm   |
| Field 2 | CO          | Carbon Monoxide        | ppm   |
| Field 3 | NO2         | Nitrogen Dioxide       | ppb   |
| Field 4 | O3          | Ozone                  | ppb   |
| Field 5 | PM2.5       | Particulate Matter 2.5 | μg/m³ |
| Field 6 | PM10        | Particulate Matter 10  | μg/m³ |
| Field 7 | Temperature | Air Temperature        | °C    |
| Field 8 | Humidity    | Relative Humidity      | %     |

## Air Quality Index (AQI) Calculation

The application automatically calculates an Air Quality Index based on the sensor readings:

- **Good (0-50)**: Air quality is satisfactory
- **Moderate (51-100)**: Air quality is acceptable for most people
- **Unhealthy for Sensitive Groups (101-150)**: Sensitive groups may experience health effects
- **Unhealthy (151+)**: Everyone may experience health effects

## Troubleshooting

### Common Issues

1. **"Failed to fetch gas sensor data"**

   - Check your API key and Channel ID
   - Ensure your ThingSpeak channel is public or you have the correct permissions
   - Verify that data has been sent to the channel recently

2. **"No data available"**

   - Make sure your gas sensor is actively sending data to ThingSpeak
   - Check that the field mappings match your sensor configuration

3. **CORS errors in browser**
   - This is normal when testing locally. The production setup should handle CORS properly.

### Testing with Mock Data

If you don't have a physical gas sensor, you can test the integration by manually sending data to your ThingSpeak channel using the ThingSpeak API or web interface.

## API Endpoints

The integration provides these new endpoints:

- `GET /data/gas-sensor/latest` - Fetch latest gas sensor data
- `GET /data/gas-sensor/historical?results=10` - Fetch historical data
- `POST /data/gas-sensor/add-reading` - Add gas sensor data as a reading

## Security Notes

- Keep your API keys secure and never commit them to version control
- Use environment variables for all sensitive configuration
- Consider using read-only API keys if possible
- Regularly rotate your API keys

## Support

For issues with the ThingSpeak integration, check:

1. ThingSpeak documentation: https://www.mathworks.com/help/thingspeak/
2. Your gas sensor device documentation
3. The application logs for detailed error messages
