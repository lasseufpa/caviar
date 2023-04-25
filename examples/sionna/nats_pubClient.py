from pynats import NATSClient

x1 = 10
y1 = 20
z1 = 30

x2 = 20
y2 = 20
z2 = 30

with NATSClient() as client:
    # Connect
    client.connect()

    # Subscribe
    def callback(msg):
        print(f"Received a message with subject {msg.subject}: {msg}")

    client.subscribe(subject="caviar.ue.mobility.positions", callback=callback)

    for i in range(1):
        client.publish(
            subject="caviar.ue.mobility.positions",
            payload=b"{'UE_type':'UAV','UE_Id':'UAV1','position': {'x':"
            + str(x1 + i).encode()
            + b",'y':"
            + str(y1).encode()
            + b",'z':"
            + str(z1).encode()
            + b"}}",
        )

        client.publish(
            subject="caviar.ue.mobility.positions",
            payload=b"{'UE_type':'UAV','UE_Id':'UAV2','position': {'x':"
            + str(x2 + i).encode()
            + b",'y':"
            + str(y2).encode()
            + b",'z':"
            + str(z2).encode()
            + b"}}",
        )

        client.wait(count=500)
