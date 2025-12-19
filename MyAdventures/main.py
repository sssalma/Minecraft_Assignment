import time
import os
import importlib
import sys
from mcpi.minecraft import Minecraft

# Aseguramos que Python encuentre nuestros módulos
sys.path.append('.')

def load_agents(mc):
   #Reflexió: s'escaneja la carpeta agents i es carreguen les classes dinámicament.
    agents_loaded = []
    agents_dir = "agents"
    
    print("--- Començant test càrrega reflexiva ---")
     # 1. Llistar els fitxers a la carpeta agents
    for filename in os.listdir(agents_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Traiem el .py (ex: explorer)
            
            # 2. Importar el mòdul dinàmicament
            module = importlib.import_module(f"agents.{module_name}")
            
            # 3. Buscar la classe dins del mòdul
            # Només agafem classes que acaben amb 'Bot' (convenció simple)
            for attribute_name in dir(module):
                if attribute_name.endswith("Bot"):
                    agent_class = getattr(module, attribute_name)
                   
                    # 4. Instanciar l'agent
                    new_agent = agent_class(mc)
                    agents_loaded.append(new_agent)
                    print(f" -> Agent carregat: {new_agent.name}")
    
    return agents_loaded


def main():
    # 1. Connexió al servidor Minecraft
    mc = Minecraft.create()
    mc.postToChat("Sistema TAP Inicialitzat. Esperant comandes...")
    
    # 2. Carregar agents utilitzant reflexió
    my_agents = load_agents(mc)
    
    # 3. Bucle principal (Game Loop)
    print("--- Sistema llest. Escriu 'explorer start' al xat ---")
    
    while True:
        # A. ESCOLTADOR DE XAT
        # Llegim el xat per convertir missatges en accions
        chat_events = mc.events.pollChatPosts()
        for event in chat_events:
            message = event.message.lower()
            print(f"Xat rebut: {message}")  # Debug a consola
            
            # B. DESPATXADOR SIMPLE DE COMANDOS
            if "start" in message and "explorer" in message:
                # Busco l'explorer i el poso a RUNNING
                for agent in my_agents:
                    if agent.name == "ExplorerBot":
                        agent.set_state("RUNNING")  
                        mc.postToChat("ExplorerBot: A les ordres! Iniciant escaneig.")
            
            elif "stop" in message:
                # Aturo tots els agents
                for agent in my_agents:
                    agent.set_state("IDLE") 
                    mc.postToChat(f"{agent.name} detingut.")

        # B. ACTUALITZACIÓ DELS AGENTS (cicle run_step)
        for agent in my_agents:
            agent.run_step()
        
        # Descans 
        time.sleep(0.5)


if __name__ == "__main__":
    main()