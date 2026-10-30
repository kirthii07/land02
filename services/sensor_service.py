from datetime import datetime


def normalize_sensor_data(data):
    """
    Normalize incoming ESP32 / simulator sensor payload.
    """

    return {
        "rainfall": float(data.get("rainfall", 0)),
        "soil_moisture": float(data.get("soil_moisture", 0)),
        "tilt": float(data.get("tilt", 0)),
        "temperature": float(data.get("temperature", 0)),
        "humidity": float(data.get("humidity", 0)),
        "location": data.get(
            "location",
            "Unknown"
        )
    }


def validate_sensor_data(data):
    """
    Basic validation for sensor readings.
    """

    errors = []

    if data["rainfall"] < 0:
        errors.append("Rainfall cannot be negative.")

    if not 0 <= data["soil_moisture"] <= 100:
        errors.append(
            "Soil moisture must be between 0 and 100."
        )

    if data["tilt"] < 0:
        errors.append(
            "Tilt cannot be negative."
        )

    if not -50 <= data["temperature"] <= 80:
        errors.append(
            "Temperature value is outside expected range."
        )

    if not 0 <= data["humidity"] <= 100:
        errors.append(
            "Humidity must be between 0 and 100."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def prepare_sensor_payload(data):

    normalized = normalize_sensor_data(data)

    validation = validate_sensor_data(
        normalized
    )

    return {
        "data": normalized,
        "validation": validation,
        "timestamp": datetime.now().isoformat()
    }