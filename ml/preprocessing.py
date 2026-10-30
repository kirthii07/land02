import pandas as pd
import numpy as np


FEATURE_COLUMNS = [
    "rain_24h",
    "rain_48h",
    "rain_72h",
    "rain_96h",
    "soil_moisture",
    "tilt"
]


def clean_sensor_data(data):

    cleaned = {}

    for column in FEATURE_COLUMNS:

        value = data.get(column, 0)

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0

        if not np.isfinite(value):
            value = 0.0

        cleaned[column] = value

    return cleaned


def prepare_features(data):

    cleaned = clean_sensor_data(data)

    return pd.DataFrame(
        [cleaned],
        columns=FEATURE_COLUMNS
    )


def calculate_rainfall_windows(
    rainfall_values
):

    values = [
        float(v)
        for v in rainfall_values
    ]

    if not values:
        return {
            "rain_24h": 0,
            "rain_48h": 0,
            "rain_72h": 0,
            "rain_96h": 0
        }

    return {

        "rain_24h":
            sum(values[-24:]),

        "rain_48h":
            sum(values[-48:]),

        "rain_72h":
            sum(values[-72:]),

        "rain_96h":
            sum(values[-96:])
    }