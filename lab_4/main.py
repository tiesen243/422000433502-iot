import os
import time
from urllib.parse import parse_qs

import paho.mqtt.client as mqtt
import requests
from dotenv import load_dotenv
from grove.adc import ADC
from grove.display.jhd1802 import JHD1802
from grove.gpio import GPIO
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
from paho.mqtt.enums import CallbackAPIVersion
from seeed_dht import DHT

load_dotenv()

THING_SPEAK_API_KEY = os.getenv("THING_SPEAK_API_KEY")
THING_SPEAK_API_URL = os.getenv(
    "THING_SPEAK_API_URL", "https://api.thingspeak.com/update"
)

THING_SPEAK_MQTT_HOST = os.getenv("THING_SPEAK_MQTT_HOST", "mqtt3.thingspeak.com")
THING_SPEAK_MQTT_PORT = int(os.getenv("THING_SPEAK_MQTT_PORT", "8883"))
THING_SPEAK_MQTT_CHANNEL = os.getenv("THING_SPEAK_MQTT_CHANNEL")
THING_SPEAK_MQTT_CLIENT = os.getenv("THING_SPEAK_MQTT_CLIENT")
THING_SPEAK_MQTT_USERNAME = os.getenv("THING_SPEAK_MQTT_USERNAME")
THING_SPEAK_MQTT_PASSWORD = os.getenv("THING_SPEAK_MQTT_PASSWORD")

MQTT_PUBLISH_TOPIC = f"channels/{THING_SPEAK_MQTT_CHANNEL}/publish"
MQTT_SUBSCRIBE_TOPIC = f"channels/{THING_SPEAK_MQTT_CHANNEL}/subscribe"


INTERVAL = 1
AVG_INTERVAL = 20
DURATION = 45 * 60

red = GPIO(5, GPIO.OUT)  # D5
yellow = GPIO(16, GPIO.OUT)  # D16
blue = GPIO(18, GPIO.OUT)  # D18

dht = DHT("11", 12)  # PWM

ultrasonic = GroveUltrasonicRanger(22)  # D22
lcd = JHD1802()  # I2C

adc = ADC()
LIGHT_PIN = 0  # A0
ROTARY_PIN = 2  # A2

LOG_FILE = "/temp/lab_4.csv"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def set_led(led: GPIO, value: float, min: float, max: float):
    if value > max:
        led.write(1)
    elif value < min:
        led.write(0)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(">> MQTT connected")

        client.subscribe(MQTT_SUBSCRIBE_TOPIC, qos=0)
        print(f">> MQTT subscribed to {MQTT_SUBSCRIBE_TOPIC}")
    else:
        print(f">> MQTT connection failed: {reason_code}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        print(f"<< MQTT message received: {payload}")

        data = parse_qs(payload)
        temp = float(data["field1"][0])
        humi = float(data["field2"][0])
        light = float(data["field3"][0])
        distance = float(data["field4"][0])
        rotary = float(data["field5"][0])

        with open(LOG_FILE, "a") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            f.write(
                f"{timestamp},{temp:.2f},{humi:.2f},{light:.2f},{distance:.2f},{rotary:.2f}\n"
            )
            f.close()

    except (ValueError, KeyError, IndexError) as e:
        print(f"<< MQTT message processing error: {e}")


def create_mqtt_client():
    client = mqtt.Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id=THING_SPEAK_MQTT_CLIENT,
        protocol=mqtt.MQTTv311,
    )

    client.username_pw_set(THING_SPEAK_MQTT_USERNAME, THING_SPEAK_MQTT_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect

    client.connect(THING_SPEAK_MQTT_HOST, THING_SPEAK_MQTT_PORT, keepalive=60)
    client.loop_start()

    client.on_message = on_message

    return client


def send_data(
    temp: float, humi: float, light: float, distance: float, rotary: float
) -> None:
    params = {
        "api_key": THING_SPEAK_API_KEY,
        "field1": temp,
        "field2": humi,
        "field3": light,
        "field4": distance,
        "field5": rotary,
    }

    try:
        res = requests.get(THING_SPEAK_API_URL, params=params, timeout=10)
        res.raise_for_status()

        if res.text.strip() != "0":
            print(
                f">> Sent: T={temp:.2f}C, H={humi:.2f}%, L={light:.2f}, D={distance:.2f}cm, R={rotary:.2f}V"
            )
        else:
            print(">> ThingSpeak update failed")

    except requests.RequestException as e:
        print(f">> Send failed: {e}")


def send_data_mqtt(
    client: mqtt.Client,
    temp: float,
    humi: float,
    light: float,
    distance: float,
    rotary: float,
) -> None:
    payload = f"field1={temp:.2f}&field2={humi:.2f}&field3={light:.2f}&field4={distance:.2f}&field5={rotary:.2f}"

    if not client.is_connected():
        print(">> MQTT disconnected")
        return

    result = client.publish(MQTT_PUBLISH_TOPIC, payload, qos=0)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(
            f">> Published: T={temp:.2f}C, "
            f"H={humi:.2f}%, L={light:.2f}, "
            f"D={distance:.2f}cm, R={rotary:.2f}V"
        )
    else:
        print(f">> MQTT publish failed: {result.rc}")


def main():
    print(
        f">> Starting data collection at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
    )

    client = create_mqtt_client()

    start_time = time.monotonic()
    last_avg_time = start_time

    temp_sum = humi_sum = light_sum = distance_sum = rotary_sum = 0.0
    count = 0

    with open(LOG_FILE, "w") as f:
        f.write("timestamp,temp,humi,light,distance,rotary\n")
        f.close()

    while time.monotonic() - start_time < DURATION:
        humi, temp = dht.read()

        if humi is None or temp is None:
            print(">> DHT read failed")
            time.sleep(INTERVAL)
            continue

        temp, humi = float(temp), float(humi)
        light = adc.read(LIGHT_PIN)
        rotate = adc.read_voltage(ROTARY_PIN) / 1000
        distance = ultrasonic.get_distance()

        set_led(red, temp, 30, 40)
        set_led(yellow, humi, 40, 70)
        set_led(blue, rotate, 1, 2)

        lcd.setCursor(0, 0)
        lcd.write(f"T:{temp:.1f}C H:{humi:.1f}%")
        lcd.setCursor(1, 0)
        lcd.write(f"L:{light} D:{distance:.1f}cm")

        temp_sum += temp
        humi_sum += humi
        light_sum += light
        distance_sum += distance
        rotary_sum += rotate
        count += 1

        now = time.monotonic()

        if now - last_avg_time >= AVG_INTERVAL:
            avg_temp = temp_sum / count
            avg_humi = humi_sum / count
            avg_light = light_sum / count
            avg_distance = distance_sum / count
            avg_rotary = rotary_sum / count

            send_data(avg_temp, avg_humi, avg_light, avg_distance, avg_rotary)
            send_data_mqtt(
                client, avg_temp, avg_humi, avg_light, avg_distance, avg_rotary
            )

            temp_sum = humi_sum = light_sum = distance_sum = rotary_sum = 0.0
            count = 0
            last_avg_time = now

        time.sleep(INTERVAL)

    print(
        f">> Data collection finished at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n>> Program interrupted")
    finally:
        lcd.clear()
