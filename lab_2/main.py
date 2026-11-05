import sys
import time

from grove.adc import ADC
from grove.display import JHD1802
from grove.gpio import GPIO
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
from seeed_dht import DHT

# ------------
# Devices
# ------------

dht = DHT("11", 12)


red = GPIO(16, GPIO.OUT)
yellow = GPIO(18, GPIO.OUT)
blue = GPIO(22, GPIO.OUT)

ultrasonic = GroveUltrasonicRanger(5)

adc = ADC()
LIGHT_PIN = 0
ROTARY_PIN = 2

lcd = JHD1802()

# ------------
# Utils
# ------------


def show_led_event(name, state, sensor_name, value):
    status = "ON" if state else "OFF"

    lcd_write(f"{name} LED: {status}", f"{sensor_name}: {value}")

    print(f"[LED CHANGED] {name}: {status}")
    print(f"{sensor_name}: {value}")

    time.sleep(3)


def lcd_write(frist: str, second: str) -> None:
    frist = str(frist)[:16].ljust(16)
    second = str(second)[:16].ljust(16)

    lcd.setCursor(0, 0)
    lcd.write(frist)

    lcd.setCursor(1, 0)
    lcd.write(second)


def get_timestamp():
    current = time.localtime()
    return time.strftime("%d/%m/%Y %H:%M:%S", current)


# ------------
# Main
# ------------


def main():
    while True:
        humidity, temperature = dht.read()
        if humidity is None or temperature is None:
            continue

        light = adc.read(LIGHT_PIN)
        rotary = adc.read_voltage(ROTARY_PIN) / 1000
        distance = ultrasonic.get_distance()

        leds = [
            ("RED", red, temperature, 40, 30, "Temp", "C"),
            ("YELLOW", yellow, humidity, 70, 40, "Humi", "%"),
            ("BLUE", blue, rotary, 2, 1, "Rotary", "V"),
        ]

        events = []
        for name, led, value, upper, lower, sensor, unit in leds:
            previous = bool(led.read())

            if value > upper:
                led.write(1)
            elif value < lower:
                led.write(0)

            current = bool(led.read())

            if previous != current:
                events.append((name, current, sensor, f"{value:.2f}{unit}"))

        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

        print(f"""========== {get_timestamp()} ==========
Temperature: {temperature:.2f}C
Humidity   : {humidity:.2f}%
Light      : {light}
Rotary     : {rotary:.2f}V
Distance   : {distance:.2f}cm
Led R/Y/B  : {"ON" if red.read() else "OFF"}/{"ON" if yellow.read() else "OFF"}/{"ON" if blue.read() else "OFF"}
=========================================\n""")
        for event in events:
            show_led_event(*event)

        lcd_write(
            f"T:{temperature:.2f}C H:{humidity:.2f}%",
            f"L:{light} D:{distance:.2f}cm",
        )

        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        red.write(0)
        yellow.write(0)
        blue.write(0)
        lcd_write("Program Stopped", "")

        sys.exit(0)
