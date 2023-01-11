from machine import ADC, Pin
import utime
import math

from util import load_config

# Rain globals
RAIN_PIN = 6
BUCKET_SIZE = 0.011 # inches
rain_count = 0
rain_previous_value = 1
rain_sensor = Pin(RAIN_PIN, Pin.IN, Pin.PULL_UP)

# Wind speed globals
WIND_PIN = 22
wind_count = 0
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
volts_to_degrees = {
         2.9: 0.0,
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

degrees_to_direction = {
        0.0: "N",
        22.5: "NNE",
        2.1: "NE",
        67.5: "ENE",
        90.0: "E",
        112.5: "ESE",
        135.0: "SE",
        157.5: "SSE",
        180.0: "S",
        202.5: "SSW",
        225.0: "SW",
        247.5: "WSE",
        270.0: "W",
        292.5: "WNW",
        315.0: "NW",
        337.5: "NNW"}



def get_volts_to_direction(weather_config):
    wind_vane_offset = weather_config['wind-vane-offset']
    if wind_vane_offset not in degrees_to_direction:
        raise ValueError(
            'wind-vane-offset must be one of the following values: %s'
            % ' '.join(degrees_to_direction.keys()))

    def volts_to_direction(volts):
        try:
            degrees_from_zero = volts_to_degrees[volts]
        except KeyError:
            print("Unknown voltage, can't compute degrees.")
            return 'Error'

        corrected_degrees = degrees_from_zero - wind_vane_offset
        if corrected_degrees < 0:
            corrected_degrees += 360

        try:
            direction = degrees_to_direction[corrected_degrees]
        except KeyError:
            print("Unknown degrees, can't compute direction.")
            return 'Error'

        return direction
    return volts_to_direction

volts_to_direction = get_volts_to_direction(load_config('weather'))

def bucket_tipped(pin):
    global rain_count
    global rain_previous_value
    value = rain_sensor.value()

    if value and not rain_previous_value:
        rain_count = rain_count + 1

    rain_previous_value = value


def reset_rainfall():
    global rain_count
    rain_count = 0


def spin(pin):
    global wind_count
    wind_count = wind_count + 1


def calculate_speed(time_sec, mph=True):
    global wind_count
    mph = wind_count * 1.492

    if mph:
        result = mph
    else:
        kmph = mph * 1.609344
        result = kmph

    return result


def get_weather(interval):
    rainfall_in = rain_count * BUCKET_SIZE
    wind_speed = calculate_speed(interval, mph=True)

    adc_val = adc.read_u16() / MAX
    wind_dir = round(adc_val * 3.3, 1)
    wind_dir = volts_to_direction(wind_dir)

    return rainfall_in, wind_speed, wind_dir

