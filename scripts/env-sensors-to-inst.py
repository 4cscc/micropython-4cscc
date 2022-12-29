from picozero import pico_led
from time import sleep
from machine import I2C, Pin
import bme280
import sgp40

from wifi import connect
from inst import request_inst_url, dict_to_payload
from util import f_to_c_conversion, hpa_to_atm_conversion

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
    exit()

print(f"{len(devices)} I2C devices found")
for device in devices:
    print(f"Decimal address {device}; Hex address: {hex(device)}.")

pico_led.on()

tph_sensor = bme280.BME280(i2c=i2c, address=0x77)
voc_sensor = sgp40.SGP40(i2c=i2c, addr=0x59)

while True:
    if not wlan.isconnected():
        wlan, ip_address = connect()
    
    for i in range(reporting_frequency_s):
        temp_c, pa, rh = tph_sensor.values
        temp_c = float(temp_c.replace('C', ''))
        temp_f = f_to_c_conversion(temp_c)
        atm = hpa_to_atm_conversion(float(pa.replace('hPa', '')))
        rh = float(rh.replace('%', ''))

        # TODO: adjust for humidity and temperature with
        # parameters to measure_raw
        # TODO: figure out unit conversion for VOC
        voc = voc_sensor.measure_raw(temperature=temp_c, humidity=rh)

        # SGP40 requires once per second readings.
        sleep(1)
    
    # Send the most recent reading of each sensor to Initial State
    data = {'temp-f': '%.2f' % temp_f,
            'pressure-atm': '%.2f' % atm,
            'relative-humidity': '%.2f' % rh,
            'voc': str(voc)}
    payload = dict_to_payload(data)
    request_inst_url(payload)
    
    pico_led.toggle()