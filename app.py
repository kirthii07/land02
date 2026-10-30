import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from database import (
    init_db,
    insert_sensor_data,
    get_recent_data,
    get_latest_data,
    insert_alert,
    get_recent_alerts
)

from services.risk_service import assess_risk

from services.sensor_service import (
    prepare_sensor_payload
)

from services.temporal_service import (
    temporal_analysis
)

from services.weather_service import (
    get_weather
)

from services.recommendation_service import (
    generate_preventive_recommendations
)

from ml.predict import (
    predict_landslide
)

from services.gis_service import get_gis_layers_geojson, lookup_coordinates
from ml.explain import (
    explain_prediction
)


# ============================================================
# FLASK APPLICATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)

CORS(app)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

init_db()


# ============================================================
# WEB PAGES
# ============================================================

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/prediction")
def prediction():
    return render_template("prediction.html")


@app.route("/map")
def map_page():
    return render_template("map.html")


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/alerts")
def alerts():
    return render_template("alerts.html")


# ============================================================
# API HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "status": "online",
        "message": "Landslide monitoring API is running"
    })


# ============================================================
# RECEIVE SENSOR DATA
# ============================================================

@app.route("/api/sensor-data", methods=["POST"])
def receive_sensor_data():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON data received"
            }), 400


        # ----------------------------------------------------
        # Normalize + Validate Sensor Data
        # ----------------------------------------------------

        sensor_payload = prepare_sensor_payload(data)

        validation = sensor_payload["validation"]

        if not validation["valid"]:

            return jsonify({

                "success": False,

                "message":
                    "Invalid sensor data",

                "errors":
                    validation["errors"]

            }), 400


        sensor_data = sensor_payload["data"]


        # ----------------------------------------------------
        # Extract Sensor Values
        # ----------------------------------------------------

        rainfall = sensor_data["rainfall"]

        soil_moisture = (
            sensor_data["soil_moisture"]
        )

        tilt = sensor_data["tilt"]

        temperature = (
            sensor_data["temperature"]
        )

        humidity = sensor_data["humidity"]

        location = sensor_data["location"]


        # ----------------------------------------------------
        # Risk Assessment
        # ----------------------------------------------------

        risk_result = assess_risk({

            "rainfall":
                rainfall,

            "soil_moisture":
                soil_moisture,

            "tilt":
                tilt,

            "humidity":
                humidity

        })


        shi = risk_result["shi"]

        risk_level = (
            risk_result["risk_level"]
        )


        # ----------------------------------------------------
        # Save Sensor Data
        # ----------------------------------------------------

        sensor_id = insert_sensor_data(

            location=location,

            rainfall=rainfall,

            soil_moisture=soil_moisture,

            tilt=tilt,

            temperature=temperature,

            humidity=humidity,

            risk_level=risk_level,

            shi=shi

        )


        # ----------------------------------------------------
        # Generate Alert
        # ----------------------------------------------------

        if risk_level in [
            "HIGH",
            "CRITICAL"
        ]:

            message = (

                f"{risk_level} landslide risk detected "
                f"at {location}. "
                f"Slope Health Index: {shi:.1f}"

            )

            insert_alert(

                location=location,

                risk_level=risk_level,

                message=message,

                acknowledged=0

            )


        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "message":
                "Sensor data processed successfully",

            "sensor_id":
                sensor_id,

            "data": {

                "location":
                    location,

                "rainfall":
                    rainfall,

                "soil_moisture":
                    soil_moisture,

                "tilt":
                    tilt,

                "temperature":
                    temperature,

                "humidity":
                    humidity,

                "shi":
                    shi,

                "risk_level":
                    risk_level

            },

            "risk":
                risk_result

        })


    except Exception as e:

        print(
            "Sensor data error:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Failed to process sensor data",

            "error":
                str(e)

        }), 500


# ============================================================
# LATEST SENSOR DATA
# ============================================================

@app.route("/api/latest", methods=["GET"])
def latest():

    try:

        data = get_latest_data()


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No sensor data available"

            }), 404


        return jsonify({

            "success": True,

            "data":
                data

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Failed to fetch latest data",

            "error":
                str(e)

        }), 500


# ============================================================
# SENSOR HISTORY
# ============================================================

@app.route("/api/history", methods=["GET"])
def history_api():

    try:

        limit = request.args.get(
            "limit",
            default=50,
            type=int
        )


        if limit <= 0:
            limit = 50


        if limit > 500:
            limit = 500


        data = get_recent_data(limit)


        return jsonify({

            "success": True,

            "count":
                len(data),

            "data":
                data

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Failed to fetch history",

            "error":
                str(e)

        }), 500


# ============================================================
# ALERT HISTORY
# ============================================================

@app.route("/api/alerts", methods=["GET"])
def alerts_api():

    try:

        limit = request.args.get(
            "limit",
            default=20,
            type=int
        )


        if limit <= 0:
            limit = 20


        if limit > 200:
            limit = 200


        data = get_recent_alerts(limit)


        return jsonify({

            "success": True,

            "count":
                len(data),

            "data":
                data

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Failed to fetch alerts",

            "error":
                str(e)

        }), 500


# ============================================================
# CURRENT RISK
# ============================================================

@app.route("/api/risk", methods=["GET"])
def current_risk():

    try:

        data = get_latest_data()


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No sensor data available"

            }), 404


        risk_result = assess_risk({

            "rainfall":
                float(
                    data.get(
                        "rainfall",
                        0
                    )
                ),

            "soil_moisture":
                float(
                    data.get(
                        "soil_moisture",
                        0
                    )
                ),

            "tilt":
                float(
                    data.get(
                        "tilt",
                        0
                    )
                ),

            "humidity":
                float(
                    data.get(
                        "humidity",
                        0
                    )
                )

        })


        return jsonify({

            "success": True,

            "risk":
                risk_result

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Failed to calculate risk",

            "error":
                str(e)

        }), 500


# ============================================================
# ML PREDICTION
# ============================================================

@app.route("/api/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No JSON data received"

            }), 400


        # ----------------------------------------------------
        # Extract ML Features
        # ----------------------------------------------------

        rain_24h = float(
            data.get(
                "rain_24h",
                0
            )
        )

        rain_48h = float(
            data.get(
                "rain_48h",
                0
            )
        )

        rain_72h = float(
            data.get(
                "rain_72h",
                0
            )
        )

        rain_96h = float(
            data.get(
                "rain_96h",
                0
            )
        )

        soil_moisture = float(
            data.get(
                "soil_moisture",
                0
            )
        )

        tilt = float(
            data.get(
                "tilt",
                0
            )
        )


        # ----------------------------------------------------
        # ML Prediction
        # ----------------------------------------------------

        prediction_result = predict_landslide(

            rain_24h,

            rain_48h,

            rain_72h,

            rain_96h,

            soil_moisture,

            tilt

        )


        # ----------------------------------------------------
        # Explain Prediction
        # ----------------------------------------------------

        explanation = explain_prediction(

            rain_24h,

            soil_moisture,

            tilt,

            prediction_result["prediction"]

        )


        return jsonify({

            "success": True,

            "prediction":
                prediction_result["prediction"],

            "prediction_label":
                prediction_result["label"],

            "probability":
                prediction_result["probability"],

            "explanation":
                explanation

        })


    except Exception as e:

        print(
            "Prediction error:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Prediction failed",

            "error":
                str(e)

        }), 500


# ============================================================
# TEMPORAL ANALYSIS
# ============================================================

@app.route("/api/temporal", methods=["GET"])
def temporal():

    try:

        history_data = get_recent_data(96)


        analysis = temporal_analysis(
            history_data
        )


        return jsonify({

            "success": True,

            "analysis":
                analysis

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Temporal analysis failed",

            "error":
                str(e)

        }), 500


# ============================================================
# WEATHER
# ============================================================

@app.route("/api/weather", methods=["GET"])
def weather():

    try:

        lat_param = request.args.get("lat") or request.args.get("latitude")
        lon_param = request.args.get("lon") or request.args.get("lng") or request.args.get("longitude")
        latitude = float(lat_param) if lat_param is not None else 11.685
        longitude = float(lon_param) if lon_param is not None else 76.132
        result = get_weather(

            latitude,

            longitude

        )


        return jsonify(result)


    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Weather request failed",

            "error":
                str(e)

        }), 500


# ============================================================
# COMBINED ANALYSIS
# ============================================================

@app.route("/api/gis/layers", methods=["GET"])
def gis_layers():
    try:
        layers = get_gis_layers_geojson()
        return jsonify({
            "success": True,
            "layers": layers
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to fetch GIS layers",
            "error": str(e)
        }), 500


@app.route("/api/gis/lookup", methods=["GET"])
def gis_lookup():
    try:
        lat_val = request.args.get("lat") or request.args.get("latitude") or 11.685
        lon_val = request.args.get("lon") or request.args.get("lng") or request.args.get("longitude") or 76.132
        lat = float(lat_val)
        lon = float(lon_val)

        info = lookup_coordinates(lat, lon)
        weather_res = get_weather(lat, lon)
        info["current_weather"] = weather_res

        return jsonify({
            "success": True,
            "data": info
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Coordinate lookup failed",
            "error": str(e)
        }), 500


@app.route("/api/analysis", methods=["GET"])
def combined_analysis():

    try:

        latest_data = get_latest_data()

        history_data = get_recent_data(96)


        if not latest_data:

            return jsonify({

                "success": False,

                "message":
                    "No monitoring data available"

            }), 404


        # ----------------------------------------------------
        # Current Risk
        # ----------------------------------------------------

        risk_result = assess_risk({

            "rainfall":
                float(
                    latest_data.get(
                        "rainfall",
                        0
                    )
                ),

            "soil_moisture":
                float(
                    latest_data.get(
                        "soil_moisture",
                        0
                    )
                ),

            "tilt":
                float(
                    latest_data.get(
                        "tilt",
                        0
                    )
                ),

            "humidity":
                float(
                    latest_data.get(
                        "humidity",
                        0
                    )
                )

        })


        # ----------------------------------------------------
        # Temporal Analysis
        # ----------------------------------------------------

        temporal_result = temporal_analysis(
            history_data
        )


        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        recommendations = (
            generate_preventive_recommendations(

                risk_result[
                    "risk_level"
                ],

                risk_result.get(
                    "risk_factors",
                    []
                )

            )
        )


        return jsonify({

            "success": True,

            "latest":
                latest_data,

            "risk":
                risk_result,

            "temporal":
                temporal_result,

            "recommendations":
                recommendations

        })


    except Exception as e:

        print(
            "Combined analysis error:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Combined analysis failed",

            "error":
                str(e)

        }), 500


# ============================================================
# GIS LOCATION DATA
# ============================================================

@app.route("/api/location", methods=["GET"])
def location():

    try:

        data = get_latest_data()


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No monitoring location available"

            }), 404


        return jsonify({

            "success": True,

            "location": {

                "name":
                    data.get(
                        "location",
                        "Unknown"
                    ),

                "latitude":
                    11.685,

                "longitude":
                    76.132,

                "risk_level":
                    data.get(
                        "risk_level",
                        "UNKNOWN"
                    ),

                "shi":
                    data.get(
                        "shi",
                        0
                    )

            }

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Location request failed",

            "error":
                str(e)

        }), 500


# ============================================================
# TEST SENSOR DATA
# ============================================================

@app.route("/api/test", methods=["POST"])
def test_sensor():

    try:

        test_data = {

            "rainfall": 120,

            "soil_moisture": 82,

            "tilt": 5.5,

            "temperature": 27,

            "humidity": 90,

            "location":
                "Wayanad, Kerala"

        }


        # ----------------------------------------------------
        # Risk
        # ----------------------------------------------------

        risk_result = assess_risk({

            "rainfall":
                test_data["rainfall"],

            "soil_moisture":
                test_data["soil_moisture"],

            "tilt":
                test_data["tilt"],

            "humidity":
                test_data["humidity"]

        })


        shi = risk_result["shi"]

        risk_level = (
            risk_result["risk_level"]
        )


        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        sensor_id = insert_sensor_data(

            timestamp=None,

            location=
                test_data["location"],

            rainfall=
                test_data["rainfall"],

            soil_moisture=
                test_data["soil_moisture"],

            tilt=
                test_data["tilt"],

            temperature=
                test_data["temperature"],

            humidity=
                test_data["humidity"],

            risk_level=
                risk_level,

            shi=shi

        )


        # ----------------------------------------------------
        # Alert
        # ----------------------------------------------------

        if risk_level in [
            "HIGH",
            "CRITICAL"
        ]:

            message = (

                f"{risk_level} landslide risk detected "
                f"at {test_data['location']}. "
                f"Slope Health Index: {shi:.1f}"

            )


            insert_alert(

                location=
                    test_data["location"],

                risk_level=
                    risk_level,

                message=
                    message,

                acknowledged=0

            )


        return jsonify({

            "success": True,

            "message":
                "Test sensor data inserted",

            "sensor_id":
                sensor_id,

            "data":
                test_data,

            "risk":
                risk_result

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Test failed",

            "error":
                str(e)

        }), 500


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "message":
            "Endpoint not found"

    }), 404


@app.errorhandler(500)
def internal_error(error):

    return jsonify({

        "success": False,

        "message":
            "Internal server error"

    }), 500


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)

    print(
        "🌧️  LOCALIZED LANDSLIDE "
        "RISK MONITORING SYSTEM"
    )

    print("=" * 65)

    print()

    print(
        "Dashboard  : "
        "http://127.0.0.1:5000/dashboard"
    )

    print(
        "Prediction : "
        "http://127.0.0.1:5000/prediction"
    )

    print(
        "Risk Map   : "
        "http://127.0.0.1:5000/map"
    )

    print(
        "History    : "
        "http://127.0.0.1:5000/history"
    )

    print(
        "Alerts     : "
        "http://127.0.0.1:5000/alerts"
    )

    print()

    print(
        "API Health : "
        "http://127.0.0.1:5000/api/health"
    )

    print(
        "API Latest : "
        "http://127.0.0.1:5000/api/latest"
    )

    print(
        "API Risk   : "
        "http://127.0.0.1:5000/api/risk"
    )

    print(
        "API Analysis : "
        "http://127.0.0.1:5000/api/analysis"
    )

    print()

    print("=" * 65)
    print()


    import os
    port = int(os.environ.get("PORT", 5000))
    try:
        app.run(
            host="127.0.0.1",
            port=port,
            debug=True
        )
    except OSError as e:
        alt_port = 5001 if port == 5000 else port + 1
        print(f"\n[!] Port {port} is already in use by another application.")
        print(f"--> Automatically starting on http://127.0.0.1:{alt_port} instead...\n")
        app.run(
            host="127.0.0.1",
            port=alt_port,
            debug=True
        )