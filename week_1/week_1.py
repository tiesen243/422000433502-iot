import sys
import time

from grove.gpio import GPIO

from week_1.pins import LEDS


class Led(GPIO):
    def __init__(self, pin: int):
        super().__init__(pin=pin, direction=GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(1)

    def toggle(self):
        self.write(not self.read())


leds = []


def setup():
    global leds
    leds = [Led(pin) for pin in LEDS]


def loop():
    for led in leds:
        led.on()
        time.sleep(0.2)
        led.off()


def main():
    try:
        setup()

        while True:
            loop()

    except KeyboardInterrupt:
        for led in leds:
            led.off()

        print("Exiting program")
        sys.exit(0)


if __name__ == "__main__":
    main()
