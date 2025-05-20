from machine import Pin, PWM
import time


LED_RED = PWM(Pin(2))
LED_BLUE = PWM(Pin(3))

LED_RED.freq(1000)
LED_BLUE.freq(1000)


def main():
    try:
        while True:
            fade_cross(LED_RED, LED_BLUE)
            fade_cross(LED_BLUE, LED_RED)

    except KeyboardInterrupt:
        LED_RED.duty_u16(0)
        LED_RED.deinit()
        LED_BLUE.duty_u16(0)
        LED_BLUE.deinit()
        print("Turn off")


def fade_in(*leds, step=10, delay=0.01):
    for duty in range(0, 1024, step):
        for led in leds:
            led.duty_u16(duty * 64)
        time.sleep(delay)


def fade_out(*leds, step=10, delay=0.01):
    for duty in range(1023, -1, -step):
        for led in leds:
            led.duty_u16(duty * 64)
        time.sleep(delay)


def fade_cross(led_in, led_out, step=10, delay=0.01):
    for duty in range(0, 1024, step):
        led_in.duty_u16(duty * 64)
        led_out.duty_u16((1023 - duty) * 64)
        time.sleep(delay)


if __name__ == "__main__":
    main()
