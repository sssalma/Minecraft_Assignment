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
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)

# Afegir directori src al path de Python
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from src.messaging.message_bus import MessageBus
from src.application.coordinator import Coordinator
from src.reflections.agent_loader import AgentLoader
from src.minecraft_adapter.chat_listerner import ChatListener
from mcpi.minecraft import Minecraft


async def async_main():
    """Funcio principal asincrona que gestiona el bus i el bucle de ticks."""
    
    # Canviar al directori del script per gestionar paths relatius
    os.chdir(script_dir)
    
    # Inicialitzar client de Minecraft
    mc = Minecraft.create()
    mc.postToChat("Sistema TAP inicialitzat. Esperant comandes...")
    print("[Main] Connectat a Minecraft")

    # Crear instàncies del bus i coordinador
    bus = MessageBus()
    coordinator = Coordinator(bus)

    # Carregar agents dinamicament amb reflection
    loader = AgentLoader(agents_dir="src/agents")
    agents = loader.load(mc, coordinator)
    
    # Registrar agents automàticament al coordinador
    i = 0
    while i < len(agents):
        agent = agents[i]
        coordinator.register_agent(agent)
        i = i + 1
    
    # Verificar si s'han carregat agents
    agent_count = len(agents)
    if agent_count == 0:
        print("[Main] ADVERTENCIA: Cap agent carregat. Comprova el directori src/agents/")

    # Iniciar el bus asincron en background
    await coordinator.start()
    print("[Main] Bus de missatges iniciat")

    # Crear ChatListener per escoltar comandes
    chat_listener = ChatListener(mc, coordinator)
    print("[Main] Sistema llest. Escriu comandes al xat de Minecraft.")

    # Bucle principal de ticks (Minecraft tick rate ~20 TPS = 0.05s, pero usem 0.5s)
    try:
        running = True
        while running == True:
            # Llegir comandes del chat (operacio sincronica)
            chat_listener.listen()
            
            # Executar cicle de tots els agents (operacio sincronica)
            coordinator.tick()
            
            # Esperar abans del seguent tick (operacio asincrona)
            await asyncio.sleep(0.5)
            
    except KeyboardInterrupt:
        # Interrupcio manual per l'usuari
        print("\n[Main] Aturant sistema...")
    finally:
        # Aturar el bus abans de sortir
        await coordinator.stop()
        mc.postToChat("Sistema TAP aturat.")
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
