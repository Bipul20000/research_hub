

import paho.mqtt.client as mqtt

broker_ip = "broker.emqx.io"
topic = "bk/chat"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "laptopB_pub")
client.connect(broker_ip, 1883, 60)

print("Type your message and press Enter. Type 'exit' to quit.")
while True:
    msg = input("You: ")
    if msg.lower() == "exit":
        break
    client.publish(topic, msg)
