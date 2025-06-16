import asyncio
import json
from nats.aio.client import Client as NATS
from main import main

nc = NATS()  # Instancia o cliente NATS

async def callback(msg):
    try:
        payload = json.loads(msg.data.decode())  # Decodifica a mensagem JSON

        # Extrai a posição
        position = [
            float(payload["position"]["x"]),
            float(payload["position"]["y"]),
            float(payload["position"]["z"])
        ]

        run = payload["run"]

        # Define a rotação fixa como (0,0,0)
        rotation = (0, 0, 0)

        # Chama a função main com os valores extraídos
        await main(position, rotation,run)

    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")
    
    
    await nc.publish(subject="communications.state", payload=b'{"Message":"Finish"}')
    print("Mensagem de finalização enviada para 'communications.state'.")

async def run():

    await nc.connect("nats://200.239.93.221:4222")  # Conecta ao servidor NATS

    print("Escutando mensagens no tópico '3D.mobility.positions'...")

    # Inscreve-se no tópico e chama `callback` quando uma mensagem é recebida
    await nc.subscribe("3D.mobility.positions", cb=callback)

    # Mantém o programa rodando
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())
