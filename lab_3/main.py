import os
import time

import requests
from dotenv import load_dotenv
from grove.adc import ADC
from grove.display.jhd1802 import JHD1802
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
from seeed_dht import DHT

load_dotenv()

API_KEY = os.getenv("THING_SPEAK_API_KEY")
API_URL = "https://api.thingspeak.com/update"

INTERVAL = 1
AVG_INTERVAL = 20
DURATION = 15 * 60

dht = DHT("11", 12)

ultrasonic = GroveUltrasonicRanger(22)
lcd = JHD1802()
adc = ADC()
LIGHT_PIN = 0
ROTARY_PIN = 2

LOG_FILE = "log.csv"


def send_data(temp: float, humi: float, light: float, distance: float) -> None:
    params = {
        "api_key": API_KEY,
        "field1": temp,
        "field2": humi,
        "field3": light,
        "field4": distance,
    }

    try:
        res = requests.get(API_URL, params=params, timeout=10)
        res.raise_for_status()

        if res.text.strip() != "0":
            print(
                f">> Sent: T={temp:.2f}C, H={humi:.2f}%, L={light:.2f}, D={distance:.2f}cm"
            )
        else:
            print(">> ThingSpeak update failed")

    except requests.RequestException as e:
        print(f">> Send failed: {e}")


def main():
    start_time = time.monotonic()
    last_avg_time = start_time

    temp_sum = humi_sum = light_sum = distance_sum = 0.0
    count = 0

    with open(LOG_FILE, "w") as f:
        f.write("timestamp,temp,humi,light,distance\n")
        f.close()

    while time.monotonic() - start_time < DURATION:
        humi, temp = dht.read()

        if humi is None or temp is None:
            print(">> DHT read failed")
            time.sleep(INTERVAL)
            continue

        temp, humi = float(temp), float(humi)
        light = adc.read(LIGHT_PIN)
        distance = ultrasonic.get_distance()

        lcd.setCursor(0, 0)
        lcd.write(f"T:{temp:.1f}C H:{humi:.1f}%")
        lcd.setCursor(1, 0)
        lcd.write(f"L:{light} D:{distance:.1f}cm")

        temp_sum += temp
        humi_sum += humi
        light_sum += light
        distance_sum += distance
        count += 1

        now = time.monotonic()

        if now - last_avg_time >= AVG_INTERVAL:
            avg_temp = temp_sum / count
            avg_humi = humi_sum / count
            avg_light = light_sum / count
            avg_distance = distance_sum / count

            send_data(avg_temp, avg_humi, avg_light, avg_distance)
            with open(LOG_FILE, "a") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                f.write(
                    f"{timestamp},{avg_temp:.2f},{avg_humi:.2f},{avg_light:.2f},{avg_distance:.2f}\n"
                )
                f.close()

            temp_sum = humi_sum = light_sum = distance_sum = 0.0
            count = 0
            last_avg_time = now

        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n>> Program interrupted")
    finally:
        lcd.clear()
