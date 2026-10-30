"""
Landslide Risk Assessment Service

Combines environmental sensor values and temporal information
to generate:
    - Slope Health Index (SHI)
    - Risk level
    - Contributing factors
    - Preventive recommendations
"""


def clamp(value, minimum=0, maximum=100):
    """Keep a value inside the given range."""
    return max(minimum, min(maximum, value))


def normalize(value, minimum, maximum):
    """
    Convert a value into a 0-100 scale.

    0   = lower risk
    100 = higher risk
    """
    if maximum == minimum:
        return 0

    score = ((value - minimum) / (maximum - minimum)) * 100

    return clamp(score)


def calculate_risk_score(
    rainfall,
    soil_moisture,
    tilt,
    humidity
):
    """
    Calculate environmental risk score.

    Prototype weighting:
        Rainfall       -> 30%
        Soil Moisture  -> 30%
        Tilt            -> 25%
        Humidity        -> 15%
    """

    rainfall_score = normalize(
        rainfall,
        0,
        200
    )

    soil_score = normalize(
        soil_moisture,
        20,
        100
    )

    tilt_score = normalize(
        tilt,
        0,
        10
    )

    humidity_score = normalize(
        humidity,
        40,
        100
    )

    shi = (
        rainfall_score * 0.30 +
        soil_score * 0.30 +
        tilt_score * 0.25 +
        humidity_score * 0.15
    )

    return round(clamp(shi), 2)


def get_risk_level(shi):
    """
    Convert Slope Health Index into risk category.

    Prototype thresholds:
        0-30   LOW
        31-55  MODERATE
        56-75  HIGH
        76-100 CRITICAL
    """

    if shi <= 30:
        return "LOW"

    elif shi <= 55:
        return "MODERATE"

    elif shi <= 75:
        return "HIGH"

    else:
        return "CRITICAL"


def identify_risk_factors(
    rainfall,
    soil_moisture,
    tilt,
    humidity
):
    """Identify environmental factors contributing to risk."""

    factors = []

    if rainfall >= 100:
        factors.append({
            "factor": "High rainfall",
            "severity": "HIGH",
            "value": rainfall
        })

    elif rainfall >= 50:
        factors.append({
            "factor": "Elevated rainfall",
            "severity": "MODERATE",
            "value": rainfall
        })

    if soil_moisture >= 75:
        factors.append({
            "factor": "High soil moisture",
            "severity": "HIGH",
            "value": soil_moisture
        })

    elif soil_moisture >= 60:
        factors.append({
            "factor": "Elevated soil moisture",
            "severity": "MODERATE",
            "value": soil_moisture
        })

    if tilt >= 5:
        factors.append({
            "factor": "Abnormal slope tilt",
            "severity": "HIGH",
            "value": tilt
        })

    elif tilt >= 2:
        factors.append({
            "factor": "Increasing slope tilt",
            "severity": "MODERATE",
            "value": tilt
        })

    if humidity >= 85:
        factors.append({
            "factor": "High humidity",
            "severity": "MODERATE",
            "value": humidity
        })

    return factors


def generate_recommendations(
    risk_level,
    factors
):
    """Generate preventive recommendations."""

    recommendations = []

    factor_names = [
        factor["factor"].lower()
        for factor in factors
    ]

    # Rainfall / water related
    if any(
        "rainfall" in factor
        for factor in factor_names
    ):
        recommendations.append(
            "Inspect drainage pathways and remove water blockages."
        )

    # Soil moisture
    if any(
        "soil moisture" in factor
        for factor in factor_names
    ):
        recommendations.append(
            "Check for water accumulation or seepage near the slope."
        )

    # Tilt
    if any(
        "tilt" in factor
        for factor in factor_names
    ):
        recommendations.append(
            "Inspect the slope for visible cracks or movement."
        )

    # General recommendations
    if risk_level == "LOW":

        recommendations.append(
            "Continue routine monitoring of the slope."
        )

    elif risk_level == "MODERATE":

        recommendations.append(
            "Increase monitoring frequency and observe changes."
        )

    elif risk_level == "HIGH":

        recommendations.append(
            "Notify the responsible monitoring team and inspect the slope."
        )

        recommendations.append(
            "Avoid unnecessary construction or excavation near the slope."
        )

    elif risk_level == "CRITICAL":

        recommendations.append(
            "Follow verified local emergency procedures."
        )

        recommendations.append(
            "Inform responsible local authorities immediately."
        )

        recommendations.append(
            "Move only according to official or predefined safe-zone guidance."
        )

    return recommendations


def assess_risk(
    rainfall,
    soil_moisture=None,
    tilt=None,
    humidity=None
):
    """
    Main risk assessment function.

    Returns a complete risk assessment dictionary.
    """

    if isinstance(rainfall, dict):
        rf = float(rainfall.get("rainfall", 0) or 0)
        sm = float(rainfall.get("soil_moisture", 0) or 0)
        t = float(rainfall.get("tilt", 0) or 0)
        h = float(rainfall.get("humidity", 0) or 0)
    else:
        rf = float(rainfall or 0)
        sm = float(soil_moisture or 0)
        t = float(tilt or 0)
        h = float(humidity or 0)

    shi = calculate_risk_score(
        rf,
        sm,
        t,
        h
    )

    risk_level = get_risk_level(shi)

    factors = identify_risk_factors(
        rf,
        sm,
        t,
        h
    )

    recommendations = generate_recommendations(
        risk_level,
        factors
    )

    return {
        "shi": shi,
        "risk_level": risk_level,
        "risk_factors": factors,
        "recommendations": recommendations
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    result = assess_risk(
        rainfall=120,
        soil_moisture=75,
        tilt=3.5,
        humidity=85
    )

    print("\n========== LANDSLIDE RISK TEST ==========")

    print(
        f"SHI          : {result['shi']}"
    )

    print(
        f"Risk Level   : {result['risk_level']}"
    )

    print("\nRisk Factors:")

    for factor in result["risk_factors"]:
        print(
            f"- {factor['factor']} "
            f"({factor['severity']})"
        )

    print("\nRecommendations:")

    for recommendation in result["recommendations"]:
        print(
            f"- {recommendation}"
        )

    print("==========================================\n")