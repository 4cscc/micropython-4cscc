import sys
from time import sleep

from picozero import pico_led
from machine import I2C, Pin
import bme280

from wifi import connect
from inst import request_inst_url, dict_to_payload
from util import f_to_c_conversion, hpa_to_atm_conversion, get_version

# frequency at which to report data to Initial State (in seconds)
reporting_frequency_s = 60

pico_led.off()

wlan, ip_address = connect()

i2c = I2C(id=0, scl=Pin(21), sda=Pin(20))
sleep(1)

print('Scanning I2C bus.')
devices = i2c.scan()

if len(devices) == 0:
    print("No I2C device detected.")
    sys.exit(-1)

print(f"{len(devices)} I2C devices found")
for device in devices:
    print(f"Decimal address {device}; Hex address: {hex(device)}.")

try:
    tph_sensor = bme280.BME280(i2c=i2c, address=0x77)
except OSError:
    print('BME280 not detected. Confirm connection and address.')
    sys.exit(-1)

version = get_version()

while True:
    if not wlan.isconnected():
        wlan, ip_address = connect()

    sleep(reporting_frequency_s)

    try:
        temp_c, pa, rh = tph_sensor.values
    except OSError:
        print(f'BME280 not detected. Will try again in {reporting_frequency_s} seconds.')
        continue

    temp_c = float(temp_c.replace('C', ''))
    temp_f = f_to_c_conversion(temp_c)
    atm = hpa_to_atm_conversion(float(pa.replace('hPa', '')))
    rh = float(rh.replace('%', ''))

    # Send the most recent reading of each sensor to Initial State
    data = {'temp-f': '%.2f' % temp_f,
            'pressure-atm': '%.2f' % atm,
            'relative-humidity': '%.2f' % rh,
            # TODO: don't pass version everytime (it's just overkill)
            'micropython-4cscc-version':version}
    payload = dict_to_payload(data)
    request_inst_url(payload)
