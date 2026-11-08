import os
import time

import requests
from dotenv import load_dotenv
from grove.display.jhd1802 import JHD1802
from seeed_dht import DHT

load_dotenv()

API_KEY = os.getenv("THING_SPEAK_API_KEY")
API_URL = "https://api.thingspeak.com/update"

INTERVAL = 2
AVG_INTERVAL = 20
DURATION = 30 * 60

dht = DHT("11", 12)
lcd = JHD1802()


def send_data(temp: float, humi: float):
    params = {
        "api_key": API_KEY,
        "field1": temp,
        "field2": humi,
    }

    try:
        res = requests.get(API_URL, params=params, timeout=10)
        res.raise_for_status()

        if res.text.strip() != "0":
            print(f">> Sent: T={temp:.2f}C, H={humi:.2f}%")
        else:
            print(">> ThingSpeak update failed")

    except requests.RequestException as e:
        print(f">> Send failed: {e}")


def main():
    start_time = time.monotonic()
    last_avg_time = start_time

    temp_sum = humi_sum = 0.0
    count = 0

    while time.monotonic() - start_time < DURATION:
        humi, temp = dht.read()

        if humi is None or temp is None:
            print(">> DHT read failed")
            time.sleep(INTERVAL)
            continue

        temp, humi = float(temp), float(humi)

        lcd.setCursor(0, 0)
        lcd.write(f"T:{temp:.1f}C H:{humi:.1f}%")

        temp_sum += temp
        humi_sum += humi
        count += 1

        now = time.monotonic()

        if now - last_avg_time >= AVG_INTERVAL:
            avg_temp = temp_sum / count
            avg_humi = humi_sum / count

            lcd.setCursor(1, 0)
            lcd.write(f"AT:{avg_temp:.1f} AH:{avg_humi:.1f}")

            send_data(avg_temp, avg_humi)

            temp_sum = humi_sum = 0.0
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
