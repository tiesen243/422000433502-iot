import csv
import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from gpiozero import LED
from paho.mqtt.enums import CallbackAPIVersion

load_dotenv()

MQTT_HOST = os.getenv("THING_SPEAK_MQTT_HOST", "mqtt3.thingspeak.com")
MQTT_PORT = int(os.getenv("THING_SPEAK_MQTT_PORT", "8883"))
MQTT_CHANNEL = os.getenv("THING_SPEAK_MQTT_CHANNEL")
MQTT_CLIENT = os.getenv("THING_SPEAK_MQTT_CLIENT")
MQTT_USERNAME = os.getenv("THING_SPEAK_MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("THING_SPEAK_MQTT_PASSWORD")

MQTT_TOPIC = f"channels/{MQTT_CHANNEL}/subscribe"
CSV_FILE = "/tmp/lab_4.csv"

red = LED(17, active_high=False)
yellow = LED(27, active_high=False)
blue = LED(22, active_high=False)


def set_led(led: LED, value: float, min_value: float, max_value: float):
    if value > max_value:
        led.on()
    elif value < min_value:
        led.off()


def write_csv(data: dict):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "temperature",
                    "humidity",
                    "light",
                    "distance",
                    "rotary",
                ]
            )

        writer.writerow(
            [
                data.get("created_at", ""),
                data.get("field1", ""),
                data.get("field2", ""),
                data.get("field3", ""),
                data.get("field4", ""),
                data.get("field5", ""),
            ]
        )


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(">> MQTT connected")
        client.subscribe(MQTT_TOPIC, qos=0)
        print(f">> Subscribed: {MQTT_TOPIC}")
    else:
        print(f">> MQTT connection failed: {reason_code}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))

        temperature = float(data["field1"])
        humidity = float(data["field2"])
        rotary = float(data["field5"])

        # Temperature
        set_led(red, temperature, 30, 40)

        # Humidity
        set_led(yellow, humidity, 40, 70)

        # Rotary
        set_led(blue, rotary, 1, 2)

        # CSV
        write_csv(data)

        os.system("clear")

        print("\n" + "=" * 55)
        print(f"{'Timestamp':<14}: {data.get('created_at', '-')}")
        print(f"{'Channel':<14}: {data.get('channel_id', '-')}")
        print(f"{'Entry ID':<14}: {data.get('entry_id', '-')}")
        print("-" * 55)

        print(
            f"{'Temperature':<14}: {temperature:>6.1f} °C | Red: {'ON' if red.is_active else 'OFF'}"
        )
        print(
            f"{'Humidity':<14}: {humidity:>6.1f} %  | Yellow: {'ON' if yellow.is_active else 'OFF'}"
        )
        print(f"{'Light':<14}: {float(data.get('field3', 0)):>7.1f}")
        print(f"{'Distance':<14}: {float(data.get('field4', 0)):>7.1f} cm")
        print(
            f"{'Rotary':<14}: {rotary:>6.2f} V  | Blue: {'ON' if blue.is_active else 'OFF'}"
        )
        print("=" * 55, flush=True)

    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as e:
        print(f">> Message processing error: {e}")


def main():
    client = mqtt.Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id=MQTT_CLIENT,
        protocol=mqtt.MQTTv311,
    )

    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message

    print(">> Starting MQTT subscriber")

    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n>> Subscriber stopped")
    finally:
        client.disconnect()
        red.off()
        yellow.off()
        blue.off()
        red.close()
        yellow.close()
        blue.close()


if __name__ == "__main__":
    main()
