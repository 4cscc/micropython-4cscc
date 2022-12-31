import network
from picozero import pico_led
from time import sleep
from util import load_config


def _connect(wlan, wifi_config, retry_delay):
    ssid = wifi_config['ssid']
    password = wifi_config['password']
    wlan.disconnect()
    if not wlan.isconnected():
        print(f'Trying connection to {ssid} ...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pico_led.toggle()
            sleep(retry_delay)

    pico_led.on()
    ip_address = wlan.ifconfig()[0]
    print(f'Connected to {ssid} with IP address {ip_address}')
    return wlan, ip_address
 

def connect(retry_delay=5):
    wifi_config = load_config('wifi')

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    return _connect(wlan, wifi_config, retry_delay)
