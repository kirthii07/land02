def generate_preventive_recommendations(
    risk_level,
    risk_factors=None
):

    recommendations = []

    risk_factors = risk_factors or []


    if risk_level == "LOW":

        recommendations.extend([

            "Continue routine slope monitoring.",

            "Keep drainage paths clear.",

            "Protect existing vegetation on the slope."

        ])


    elif risk_level == "MODERATE":

        recommendations.extend([

            "Inspect nearby drainage channels.",

            "Check for visible seepage or water accumulation.",

            "Increase monitoring frequency.",

            "Inspect the slope for new cracks or surface changes."

        ])


    elif risk_level == "HIGH":

        recommendations.extend([

            "Inspect slope and drainage conditions immediately.",

            "Check for new cracks, seepage, or soil movement.",

            "Avoid unnecessary construction or disturbance near the slope.",

            "Notify the responsible monitoring team."

        ])


    elif risk_level == "CRITICAL":

        recommendations.extend([

            "Treat the location as requiring immediate attention.",

            "Inspect slope and drainage conditions immediately.",

            "Avoid unnecessary access or construction near the affected slope.",

            "Notify the responsible authorities or monitoring team.",

            "Follow official local safety and evacuation procedures if issued."

        ])


    return recommendations