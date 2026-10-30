from datetime import datetime


def calculate_rainfall_windows(history):

    if not history:
        return {
            "rain_24h": 0,
            "rain_48h": 0,
            "rain_72h": 0,
            "rain_96h": 0
        }

    rainfall = []

    for item in history:

        try:
            value = float(
                item.get("rainfall", 0)
            )
        except (TypeError, ValueError):
            value = 0

        rainfall.append(value)

    return {

        "rain_24h":
            sum(rainfall[-24:]),

        "rain_48h":
            sum(rainfall[-48:]),

        "rain_72h":
            sum(rainfall[-72:]),

        "rain_96h":
            sum(rainfall[-96:])
    }


def calculate_trend(history, field):

    if len(history) < 2:
        return {
            "trend": "STABLE",
            "change": 0
        }

    values = []

    for item in history:

        try:
            values.append(
                float(item.get(field, 0))
            )
        except (TypeError, ValueError):
            values.append(0)

    previous = values[-2]
    current = values[-1]

    change = current - previous

    if change > 0:
        trend = "INCREASING"

    elif change < 0:
        trend = "DECREASING"

    else:
        trend = "STABLE"

    return {
        "trend": trend,
        "change": round(change, 3)
    }


def temporal_analysis(history):

    return {

        "rainfall":
            calculate_trend(
                history,
                "rainfall"
            ),

        "soil_moisture":
            calculate_trend(
                history,
                "soil_moisture"
            ),

        "tilt":
            calculate_trend(
                history,
                "tilt"
            ),

        "rainfall_windows":
            calculate_rainfall_windows(
                history
            )
    }