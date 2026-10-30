import random
import time
import requests
from datetime import datetime


API_URL = "http://127.0.0.1:5000/api/sensor-data"

LOCATION = "Wayanad, Kerala"


def generate_sensor_data():

    # Simulated environmental conditions
    rainfall = round(
        random.uniform(10, 140),
        2
    )

    soil_moisture = round(
        random.uniform(35, 90),
        2
    )

    tilt = round(
        random.uniform(0.2, 5.5),
        2
    )

    temperature = round(
        random.uniform(23, 32),
        2
    )

    humidity = round(
        random.uniform(55, 95),
        2
    )

    return {
        "rainfall": rainfall,
        "soil_moisture": soil_moisture,
        "tilt": tilt,
        "temperature": temperature,
        "humidity": humidity,
        "location": LOCATION
    }


def send_sensor_data(data):

    try:

        response = requests.post(
            API_URL,
            json=data,
            timeout=5
        )

        if response.status_code == 201:

            result = response.json()

            risk = result["risk"]

            print("\n" + "=" * 55)

            print(
                f"⏰ {datetime.now().strftime('%H:%M:%S')}"
            )

            print(
                f"📍 Location      : {LOCATION}"
            )

            print(
                f"🌧️ Rainfall      : {data['rainfall']} mm"
            )

            print(
                f"💧 Soil Moisture : {data['soil_moisture']} %"
            )

            print(
                f"📐 Tilt          : {data['tilt']}°"
            )

            print(
                f"🌡️ Temperature   : {data['temperature']} °C"
            )

            print(
                f"💦 Humidity      : {data['humidity']} %"
            )

            print(
                f"❤️ SHI           : {risk['shi']}/100"
            )

            print(
                f"⚠️ Risk Level    : {risk['risk_level']}"
            )

            print("=" * 55)

        else:

            print(
                "❌ API Error:",
                response.status_code
            )

            print(response.text)

    except requests.exceptions.ConnectionError:

        print(
            "\n❌ Flask server is not running!"
        )

        print(
            "Start it using: python app.py"
        )

    except Exception as error:

        print(
            "❌ Error:",
            error
        )


def main():

    print("\n")
    print("=" * 55)
    print("🌧️ LANDSLIDE SENSOR SIMULATOR")
    print("=" * 55)
    print("📍 Location:", LOCATION)
    print("🔗 API:", API_URL)
    print("⏱️ Sending data every 5 seconds")
    print("🛑 Press CTRL+C to stop")
    print("=" * 55)

    while True:

        sensor_data = generate_sensor_data()

        send_sensor_data(
            sensor_data
        )

        time.sleep(5)


if __name__ == "__main__":
    main()