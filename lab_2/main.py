import os
import time

from grove.adc import ADC
from grove.display.jhd1802 import JHD1802
from grove.gpio import GPIO
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
from seeed_dht import DHT

# ------------
# Configuration
# ------------

INTERVAL = 1
EVENT_DURATION = 3

# ------------
# Devices
# ------------

dht = DHT("11", 12)

red = GPIO(5, GPIO.OUT)
yellow = GPIO(16, GPIO.OUT)
blue = GPIO(18, GPIO.OUT)

ultrasonic = GroveUltrasonicRanger(22)
lcd = JHD1802()
adc = ADC()
LIGHT_PIN = 0
ROTARY_PIN = 2

LEDS = [
    ("RED", red, 40, 30, "Temp", "C"),
    ("YELLOW", yellow, 70, 40, "Humi", "%"),
    ("BLUE", blue, 2, 1, "Rotary", "V"),
]

# Cache initial LED states
led_states = {name: bool(led.read()) for name, led, *_ in LEDS}


# ------------
# Utils
# ------------


def lcd_write(first: str, second: str) -> None:
    for row, text in enumerate((first, second)):
        lcd.setCursor(row, 0)
        lcd.write(str(text)[:16].ljust(16))


def get_timestamp() -> str:
    return time.strftime("%d/%m/%Y %H:%M:%S")


def show_led_event(name: str, state: bool, sensor: str, value: str) -> None:
    status = "ON" if state else "OFF"

    lcd_write(f"{name} LED: {status}", f"{sensor}: {value}")

    print(f"[LED CHANGED] {name}: {status}")
    print(f"{sensor}: {value}")

    time.sleep(EVENT_DURATION)


def update_leds(temperature: float, humidity: float, rotary: float):
    values = {
        "RED": temperature,
        "YELLOW": humidity,
        "BLUE": rotary,
    }

    events = []

    for name, led, upper, lower, sensor, unit in LEDS:
        value = values[name]
        previous = led_states[name]

        current = previous

        if value > upper:
            current = True
        elif value < lower:
            current = False

        if current != previous:
            led.write(int(current))
            led_states[name] = current

            events.append((name, current, sensor, f"{value:.2f}{unit}"))

    return events


def print_status(temperature, humidity, light, rotary, distance):
    states = "/".join("ON" if led_states[name] else "OFF" for name, *_ in LEDS)

    os.system("clear")
    print(f"""========== {get_timestamp()} ==========
Temperature: {temperature:.2f}C
Humidity   : {humidity:.2f}%
Light      : {light}
Rotary     : {rotary:.2f}V
Distance   : {distance:.2f}cm
Led R/Y/B  : {states}
=========================================
""")


# ------------
# Main
# ------------


def main():
    while True:
        humidity, temperature = dht.read()

        if humidity is None or temperature is None:
            print(">> DHT read failed")
            time.sleep(INTERVAL)
            continue

        temperature = float(temperature)
        humidity = float(humidity)

        light = adc.read(LIGHT_PIN)
        rotary = adc.read_voltage(ROTARY_PIN) / 1000
        distance = ultrasonic.get_distance()

        events = update_leds(temperature, humidity, rotary)

        print_status(
            temperature,
            humidity,
            light,
            rotary,
            distance,
        )

        for event in events:
            show_led_event(*event)

        lcd_write(
            f"T:{temperature:.2f}C H:{humidity:.2f}%",
            f"L:{light} D:{distance:.2f}cm",
        )

        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n>> Program interrupted")
    finally:
        for _, led, *_ in LEDS:
            led.write(0)

        lcd_write("Program Stopped", "")
