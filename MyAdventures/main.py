"""
Punt d'entrada principal del sistema TAP per Minecraft.
Inicialitza el bus de missatges asincron i el bucle de ticks sincronic.
"""
import sys
import os
import asyncio
import logging

# Configurar sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# Afegir directori src al path de Python
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from src.messaging.message_bus import MessageBus
from src.application.coordinator import Coordinator
from src.reflection.agent_loader import AgentLoader
from src.infrastructure.minecraft.chat_listener import ChatListener
from src.infrastructure.minecraft.mc_client import MinecraftClient

async def async_main():
    """Funcio principal asincrona que gestiona el bus i el bucle de ticks."""
    
    os.chdir(script_dir)
    
    mc = MinecraftClient()
    mc.post_chat("Sistema TAP inicialitzat. Esperant comandes...")
    print("[Main] Connectat a Minecraft")


    # Crear instàncies del bus i coordinador
    bus = MessageBus()
    coordinator = Coordinator(bus)

    # Carregar agents dinamicament amb reflection
    loader = AgentLoader(bus)
    agents = loader.load(mc)
    
    if len(agents) == 0:
        print("[Main] ADVERTÈNCIA: cap agent carregat")

    # Registrar agents
    for agent in agents:
        coordinator.register_agent(agent)


    # Iniciar el bus (passant per la capa del coordinador)
    await coordinator.start()
    print("[Main] Bus de missatges iniciat")
    await coordinator.start_agents()


    # Crear ChatListener per escoltar comandes
    chat_listener = ChatListener(mc, coordinator)
    print("[Main] Sistema llest. Escriu comandes al xat de Minecraft.")

    # Bucle principal
    try:
        running = True
        while running == True:
            # Llegir comandes del chat
            chat_listener.listen()
            await asyncio.sleep(0.5)
            
    except KeyboardInterrupt:
        # Interrupcio manual per l'usuari
        print("\n[Main] Aturant sistema...")
    finally:
        # Aturar el bus abans de sortir
        await coordinator.stop_agents()
        await coordinator.stop()
        mc.post_chat("Sistema TAP aturat.")
        print("[Main] Sistema aturat correctament")


def main():
    """Punt d'entrada sincronic que llança la funcio principal asincrona."""
    try:
        # Executar funcio async_main
        asyncio.run(async_main())
    except Exception as e:
        # Capturar qualsevol error critic
        print(f"[Main] Error critic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
