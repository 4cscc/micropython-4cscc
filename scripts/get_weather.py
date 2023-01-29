import sys
from time import sleep

import weather

# frequency at which to report data to Initial State (in seconds)
reporting_frequency_s = 1


weather.rain_sensor.irq(handler=weather.bucket_tipped)
weather.wind_speed_sensor.irq(handler=weather.spin)


while True:
    weather.rain_count = 0
    weather.wind_count = 0

    sleep(reporting_frequency_s)

    rainfall, wind_speed, wind_dir = weather.get_weather(reporting_frequency_s)

    print(rainfall, wind_speed, wind_dir)
