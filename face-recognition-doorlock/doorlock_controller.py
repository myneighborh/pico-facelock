import json
import time

import network
import urequests
import neopixel

from machine import Pin, PWM


SERVO_PIN = 14
NEOPIXEL_PIN = 9
servo = PWM(Pin(SERVO_PIN))
servo.freq(50)

NUM_PIXELS = 4
pixel = neopixel.NeoPixel(Pin(NEOPIXEL_PIN), NUM_PIXELS)


def main():
    config = load_config()
    ssid = config["ssid"]
    password = config["password"]
    firebase_url = config["firebase_url"]

    door_close()
    connect_to_wifi(ssid, password)

    while True:
        door_open_status = get_doorlock_status(firebase_url)

        if door_open_status:  # True인 경우만
            print("Door is opened")
            set_color(0, 10, 0)
            door_open()
            time.sleep(3)

            door_close()
            set_color(10, 0, 0)
            print("Door is now locked again")
            update_doorlock_status(firebase_url, False)
        else:  # False 또는 None → 무조건 닫기
            door_close()
            set_color(10, 0, 0)

        time.sleep(1)


def load_config(path="config.json"):
    with open(path, "r") as file:
        config = json.load(file)
    return config


# Sets neopixel
def set_color(r, g, b):
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    for i in range(NUM_PIXELS):
        pixel[i] = (r, g, b)
    pixel.write()


def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Network connected:', wlan.ifconfig())


# Sets servo's angle
def set_angle(angle):
    # angle (0~180) → duty_u16 (1638 ~ 8192)
    min_duty = 1638  # 0.5ms
    max_duty = 8192   # 2.5ms
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty_u16(duty)


def door_open():
    set_angle(0)


def door_close():
    set_angle(90)


def update_doorlock_status(firebase_url, status: bool):
    url = f"{firebase_url}/door_open.json"
    urequests.put(url, json=status)


def get_doorlock_status(firebase_url):
    try:
        url = f"{firebase_url}/door_open.json"
        response = urequests.get(url)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, bool):
                print('door_open status from Firebase:', result)
                return result
            else:
                print('Unexpected value type', result)
        else:
            print('Failed to fetch door_open status, status code:', response.status_code)
            return None
    except Exception as e:
        print('Error fetching door_open status:', e)
        return None
    finally:
        if 'response' in locals():
            response.close()


if __name__ == "__main__":
    main()