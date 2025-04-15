import paho.mqtt.client as mqtt

broker_ip = "broker.emqx.io"
topic = "bk/chat"

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected with result code " + str(reason_code))
    client.subscribe(topic)

def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "sub")
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_ip, 1883, 60)
client.loop_forever()