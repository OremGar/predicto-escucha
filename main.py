import random
from paho.mqtt import client as mqtt_client
import json
import tratamiento
import sys
import firebase_admin
from firebase_admin import credentials

broker = "nam1.cloud.thethings.network"
port = 1883
topic = "#"
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'
username = 'predicto-ttn@ttn'
password = 'NNSXS.MBJ6XGZ72KSZ3B2GUOSB62O6YLC3WS5736NYW7Q.K4MSYU7IVD5HDKPYQZNO4AWM5DVO234QXY7JKSDBX4YXW4KKO3UA'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        try:
            #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            messageJson = json.loads(msg.payload.decode())
            uplinkMessage = messageJson["uplink_message"]
            data = uplinkMessage["decoded_payload"]["data"]
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            pass

        try:
            tratamiento.TratamientoDatos(data, messageJson["end_device_ids"]["dev_eui"], messageJson["received_at"])
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            pass

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    cred = credentials.Certificate("predicto-f6a28-firebase-adminsdk-be1mn-4f5e3a53fe.json")
    firebase_admin.initialize_app(cred)
    run()