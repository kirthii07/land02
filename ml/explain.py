def explain_prediction(
    rainfall,
    soil_moisture,
    tilt,
    prediction
):
    """
    Prototype rule-based explanation.

    This is an interpretable supporting layer,
    not a replacement for SHAP.
    """

    factors = []


    # Rainfall

    if rainfall >= 100:

        factors.append({
            "factor": "High rainfall",
            "value": rainfall,
            "severity": "HIGH"
        })

    elif rainfall >= 50:

        factors.append({
            "factor": "Elevated rainfall",
            "value": rainfall,
            "severity": "MODERATE"
        })


    # Soil moisture

    if soil_moisture >= 75:

        factors.append({
            "factor": "High soil moisture",
            "value": soil_moisture,
            "severity": "HIGH"
        })

    elif soil_moisture >= 60:

        factors.append({
            "factor": "Elevated soil moisture",
            "value": soil_moisture,
            "severity": "MODERATE"
        })


    # Tilt

    if tilt >= 5:

        factors.append({
            "factor": "High slope tilt",
            "value": tilt,
            "severity": "HIGH"
        })

    elif tilt >= 2:

        factors.append({
            "factor": "Elevated slope tilt",
            "value": tilt,
            "severity": "MODERATE"
        })


    # Overall explanation

    if prediction == 1:

        summary = (
            "The model indicates potential "
            "landslide risk based on the "
            "provided environmental conditions."
        )

    else:

        summary = (
            "The model does not indicate "
            "landslide risk for the provided "
            "conditions."
        )


    return {
        "summary": summary,
        "factors": factors
    }