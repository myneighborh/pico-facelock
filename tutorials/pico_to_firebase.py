import json
import time
import ntptime

import network
import urequests

from machine import ADC


def main():
    config = load_config()
    ssid = config["ssid"]
    password = config["password"]
    firebase_url = config["firebase_url"]

    try :
        sensor = ADC(4)    
        connect_to_wifi(ssid, password)

        while True:
            temperature = read_temp(sensor)
            print(f'Temperature: {temperature:.2f}°C')

            data = {
                'temp': temperature,
            }
            date = get_date()

            upload_to_firebase(firebase_url, data, date)

            time.sleep(5)

    except KeyboardInterrupt :
        print("Turn off")


def load_config(path="config.json"):
    with open(path, "r") as file:
        config = json.load(file)
    return config


def get_date():
    ntptime.settime()
    kst_offset = 9 * 60 * 60
    current_time = time.localtime(time.time() + kst_offset)
    date = f"{current_time[0] % 100:02d}-{current_time[1]:02d}-{current_time[2]:02d}"
    return date


def read_temp(sensorPin):
    reading = sensorPin.read_u16()
    voltage = reading * 3.3 / (65535)
    temperature_celsius = 27 - (voltage - 0.706) / 0.001721
    return temperature_celsius


def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)
    print('Network connected:', wlan.ifconfig())


def upload_to_firebase(FIREBASE_URL, data, date):
    headers = {'Content-Type': 'application/json'}
    url = f"{FIREBASE_URL}{date}.json"
    response = urequests.put(url, headers=headers, data=json.dumps(data))
    print('Response:', response.text)
    response.close()


if __name__ == "__main__":
    main()