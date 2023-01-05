from machine import ADC, Pin
import utime
import math

# Rain globals
RAIN_PIN = 6
BUCKET_SIZE = 0.2794
rain_count = 0
rain_previous_value = 1
rain_sensor = Pin(RAIN_PIN, Pin.IN, Pin.PULL_UP)

# Wind speed globals
WIND_PIN = 22
wind_count = 0
radius_cm = 9.0
CM_IN_A_KM = 10000.0
SECS_IN_AN_HOUR = 3600
ADJUSTMENT = 1.18
wind_speed_sensor = Pin(WIND_PIN, Pin.IN, Pin.PULL_UP)

# Wind direction globals
ADC_PIN = 28
adc = ADC(ADC_PIN)
MAX = 2 ** 16 - 1
# Setting this high makes the readings on
# the adc more consistent by forcing 3.3v
# on the power supply
smps = Pin(23, Pin.OUT)
smps.value(1)

# These voltages are for a 3.3v power supply and
# a 4.7kOhm r1
volts = {2.9: 0.0,
         1.9: 22.5,
         2.1: 45.0,
         .5: 67.5,
         .6: 90.0,
         .4: 112.5,
         1.1: 135.0,
         .8: 157.5,
         1.5: 180.0,
         1.3: 202.5,
         2.6: 225.0,
         2.5: 247.5,
         3.2: 270.0,
         3.0: 292.5,
         3.1: 315.0,
         2.7 : 337.5}


def bucket_tipped(pin):
    global rain_count
    global rain_previous_value
    value = rain_sensor.value()

    if value and not rain_previous_value:
        rain_count = rain_count + 1

    rain_previous_value = value


def reset_rainfall ():
    global rain_count
    rain_count = 0


def spin(pin):
    global wind_count
    wind_count = wind_count + 1


def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / 2.0

    dist_km = (circumference_cm * rotations) / CM_IN_A_KM

    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * SECS_IN_AN_HOUR

    return km_per_hour * ADJUSTMENT


def get_weather(interval):
    rainfall = rain_count * BUCKET_SIZE
    wind_speed = calculate_speed(interval)

    adc_val = adc.read_u16() / MAX
    wind_dir = round(adc_val * 3.3, 1)

    try:
        wind_dir = volts[wind_dir]
    except KeyError:
        wind_dir = 'error'

    return rainfall, wind_speed, wind_dir
