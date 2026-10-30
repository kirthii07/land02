import random
from datetime import datetime, timedelta

from database import (
    init_db,
    insert_sensor_data
)

from services.risk_service import assess_risk


def seed_database():

    init_db()

    location = "Wayanad, Kerala"

    now = datetime.now()


    for i in range(100):

        timestamp = (
            now -
            timedelta(
                minutes=(99 - i) * 5
            )
        ).isoformat()


        rainfall = round(
            random.uniform(
                10,
                140
            ),
            2
        )

        soil_moisture = round(
            random.uniform(
                35,
                90
            ),
            2
        )

        tilt = round(
            random.uniform(
                0.2,
                5.5
            ),
            2
        )

        temperature = round(
            random.uniform(
                23,
                32
            ),
            2
        )

        humidity = round(
            random.uniform(
                55,
                95
            ),
            2
        )


        risk = assess_risk({

            "rainfall":
                rainfall,

            "soil_moisture":
                soil_moisture,

            "tilt":
                tilt,

            "humidity":
                humidity

        })


        insert_sensor_data(

            timestamp=timestamp,

            location=location,

            rainfall=rainfall,

            soil_moisture=
                soil_moisture,

            tilt=tilt,

            temperature=
                temperature,

            humidity=humidity,

            risk_level=
                risk["risk_level"],

            shi=risk["shi"]

        )


    print(
        "100 sample records inserted successfully."
    )


if __name__ == "__main__":
    seed_database()