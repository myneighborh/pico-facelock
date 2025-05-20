from machine import Pin
import time


LED_RED = Pin(2, Pin.OUT)
LED_BLUE = Pin(3, Pin.OUT)
TIME_DELAY = 0.2


def main():
    try:
        while True:
            turn_on_led(LED_RED)
            turn_on_led(LED_BLUE)
            time.sleep(TIME_DELAY * 3)

            turn_off_led(LED_RED)
            turn_off_led(LED_BLUE)
            time.sleep(TIME_DELAY)

    except KeyboardInterrupt:
        print("Turn off")


# High signal function
def turn_on_led(led):
    led.on()


# Low signal function
def turn_off_led(led):
    led.off()
    
    
if __name__ == "__main__":
    main()