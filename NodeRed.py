from machine import Pin, PWM
import network
import time
from umqtt.simple import MQTTClient
import machine
import math

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('TskoliVESM', 'Fallegurhestur')  # Replace with your WiFi credentials
    while not wlan.isconnected():
        time.sleep(1)
    print('Connected to WiFi:', wlan.ifconfig())

# MQTT setup
def setup_mqtt():
    client = MQTTClient("esp32", "10.201.48.85")  # Replace with Raspberry Pi's IP address
    try:
        print("Attempting to connect to MQTT broker...")
        client.connect()
        print("Connected to MQTT Broker")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        time.sleep(5)  # Retry after 5 seconds
        setup_mqtt()  # Retry connection
    client.set_callback(sub_cb)
    client.subscribe("animatronic/UpDown")
    client.subscribe("animatronic/LeftRight")
    client.subscribe("animatronic/jaw")
    client.subscribe("animatronic/lefthand")
    client.subscribe("animatronic/righthand")
    client.subscribe("animatronic/Eyes")

    print("Subscribed to topics")
    return client

# Servo class definition
class Servo:
    def __init__(self, pin, freq=50, min_us=600, max_us=2400, angle=180):
        self.min_us = min_us
        self.max_us = max_us
        self.us = 0
        self.freq = freq
        self.angle = angle
        self.pwm = machine.PWM(machine.Pin(pin), freq=freq, duty=0)  # Correcting the Pin definition

    def write_us(self, us):
        if us == 0:
            self.pwm.duty(0)
            return
        us = min(self.max_us, max(self.min_us, us))
        duty = us * 1024 * self.freq // 1000000
        self.pwm.duty(duty)

    def write_angle(self, degrees=None, radians=None):
        if degrees is None:
            degrees = math.degrees(radians)
        degrees = degrees % 360
        total_range = self.max_us - self.min_us
        us = self.min_us + total_range * degrees // self.angle
        self.write_us(us)

# Initialize servos on the pins
neck1 = Servo(11)  # Pin 11 for neck1
neck2 = Servo(13)  # Pin 13 for neck2
lefthand = Servo(14)  # Pin 14 for left hand
righthand = Servo(10)  # Pin 10 for right hand
led1_green = Pin(5, Pin.OUT)  # Green for LED 1
led2_green = Pin(2, Pin.OUT)


def sub_cb(topic, msg):
    try:
        print(f"Message received: Topic={topic}, Message={msg}")
        if topic == b"animatronic/UpDown":
            angle = int(msg)
            if 0 <= angle <= 180:
                neck2.write_angle(angle)
                print(f"Moving neck2 to angle: {angle}")
            else:
                print(f"Invalid angle: {angle}. Must be between 0 and 180.")
                
        elif topic == b"animatronic/LeftRight":
            angle = int(msg)
            if 0 <= angle <= 180:
                neck1.write_angle(angle)
                print(f"Moving neck1 to angle: {angle}")
            else:
                print(f"Invalid angle: {angle}. Must be between 0 and 180.")
                
        elif topic == b"animatronic/lefthand":
            angle = int(msg)
            if 0 <= angle <= 180:
                lefthand.write_angle(angle)
                print(f"Moving left hand to angle: {angle}")
            else:
                print(f"Invalid angle: {angle}. Must be between 0 and 180.")
                
        elif topic == b"animatronic/righthand":
            angle = int(msg)
            if 0 <= angle <= 180:
                righthand.write_angle(angle)
                print(f"Moving right hand to angle: {angle}")
            else:
                print(f"Invalid angle: {angle}. Must be between 0 and 180.")
        elif topic == b"animatronic/Eyes":
            if msg == b"ON":
                led1_green.value(1)
                led2_green.value(1)
                print("Lights turned ON")
            elif msg == b"OFF":
                led1_green.value(0)
                led2_green.value(0)
                print("Lights turned OFF")
            else:
                print(f"Invalid lights command: {msg}")

        else:
            print(f"Unknown topic: {topic}")
    except ValueError:
        print(f"Invalid message: {msg}. Could not convert to integer.")






# Main loop
connect_wifi()
mqtt_client = setup_mqtt()

while True:
    mqtt_client.check_msg()  # Listen for incoming messages
    time.sleep(1)
