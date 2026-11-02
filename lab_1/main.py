import sys

from grove.gpio import GPIO
from time import sleep

class Led(GPIO):
    def __init__(self, pin: int):
        super().__init__(pin=pin, direction=GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(0)

    def toggle(self):
        self.write(not self.read())

led_pins = [21, 26, 20, 19, 16, 13, 6, 12, 5, 7, 11, 8, 9, 25, 10, 24, 22, 23, 27, 17, 18, 15, 4, 14]
leds = [Led(pin) for pin in led_pins]

try:
    while True:
        for led, led_pin in zip(leds, led_pins):
            led.on()
            print(f"Led {led_pin}: ON")
            sleep(0.2)
            print(f"Led {led_pin}: OFF")
            led.off()

except KeyboardInterrupt:
    for led in leds:
        led.off()

    sys.exit(1)
