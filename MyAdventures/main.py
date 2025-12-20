import sys
import os
import time

# Añadimos src al path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from application.coordinator import Coordinator
from infrastructure.minecraft.mc_client import MinecraftClient
from infrastructure.minecraft.chat_listener import ChatListener
from messaging.message_bus import MessageBus
from reflection.agent_loader import AgentLoader


def main():
    mc_client = MinecraftClient()
    mc_client.post_chat("Sistema TAP inicialitzat. Esperant comandes...")

    bus = MessageBus()
    coordinator = Coordinator(bus)

    loader = AgentLoader(bus)
    agents = loader.load(mc_client)

    for agent in agents:
        coordinator.register_agent(agent)

    chat_listener = ChatListener(mc_client, coordinator)

    print("Sistema llest. Escriu comandes al xat.")

    while True:
        chat_listener.listen()
        coordinator.tick()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
