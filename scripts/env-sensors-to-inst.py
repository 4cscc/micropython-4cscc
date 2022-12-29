from picozero import pico_led
from time import sleep
from machine import I2C, Pin
import bme280
import sgp40

from wifi import connect
from inst import request_inst_url, dict_to_payload
from util import f_to_c_conversion, hpa_to_atm_conversion


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
        
    temp_c, pa, rh = tph_sensor.values
    temp_f = f_to_c_conversion(float(temp_c.replace('C', '')))
    atm = hpa_to_atm_conversion(float(pa.replace('hPa', '')))
    rh = float(rh.replace('%', ''))
    
    # TODO: adjust for humidity and temperature with
    # parameters to measure_raw
    voc = voc_sensor.measure_raw()
    
    data = {'temp-f': '%.2f' % temp_f,
            'pressure-atm': '%.2f' % atm,
            'relative-humidity': '%.2f' % rh,
            'voc': str(voc)}
    payload = dict_to_payload(data)
    request_inst_url(payload)
    
    sleep(10)
    pico_led.toggle()