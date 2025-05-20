from machine import ADC
import time


SENSOR_TEMP = ADC(4)
CONVERSION_FACTOR = 3.3 / 65535


def main():
    while True:
        raw_value = SENSOR_TEMP.read_u16()
        voltage = convert_raw_to_voltage(raw_value)
        temperature = convert_voltage_to_temp(voltage)    
        print(f"Temperature: {temperature:.2f} °C")
        time.sleep(1)
        

def convert_raw_to_voltage(raw_value):
    return raw_value * CONVERSION_FACTOR


def convert_voltage_to_temp(voltage):
    return 27 - (voltage - 0.706) / 0.001721


if __name__ == "__main__":
    main()
