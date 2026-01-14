"""Coordinador per gestionar comunicació global i cicle de vida dels agents."""
import asyncio
from typing import Dict, Any
from ..messaging.message_bus import MessageBus
from ..messaging.message import Message


class Coordinator:
    """
    Coordinador central del sistema d'agents.
    Patró: Facade - proporciona una interfície simplificada per interactuar amb el bus.
    """

    def __init__(self, message_bus):
        """
        Inicialitza el coordinador.
        
        Args:
            message_bus: Instància del bus de missatges
        """
        self.bus = message_bus
        # Registre d'agents actius
        self.agents = dict()
        # Tasca asincrònica del bus
        self.bus_task = None

    def register_agent(self, agent):
        """
        Registra un agent al coordinador i subscriu el seu handler al bus.
        
        Args:
            agent: Instància de BaseAgent amb atribut 'name' i mètode 'handle_message'
        """
        # Verificar que l'agent té mètode handle_message
        has_handler = hasattr(agent, 'handle_message')
        if not has_handler:
            raise ValueError(f"Agent no té mètode 'handle_message'")
        
        # Verificar que l'agent té atribut name
        has_name = hasattr(agent, 'name')
        if not has_name:
            raise ValueError(f"Agent no té atribut 'name'")
        
        # Obtenir nom de l'agent
        name = agent.name
        
        # Emmagatzemar agent al registre
        self.agents[name] = agent
        
        # Subscriure handler al bus
        self.bus.subscribe(name, agent.handle_message)
        
        print(f"[Coordinator] Agent '{name}' registrat")

    async def start(self):
        """Inicia el bus de missatges en background."""
        # Verificar si ja hi ha una tasca activa
        task_exists = False
        if self.bus_task is not None:
            task_exists = True
        
        if not task_exists:
            # Crear tasca asincrònica per executar el bus
            self.bus_task = asyncio.create_task(self.bus.run())
            print("[Coordinator] Sistema iniciat")

    async def stop(self):
        """Atura el bus i tots els agents."""
        # Aturar el bus
        await self.bus.stop()
        
        # Verificar si hi ha tasca per cancel·lar
        task_exists = False
        if self.bus_task is not None:
            task_exists = True
        
        if task_exists:
            # Cancel·lar tasca del bus
            self.bus_task.cancel()
            
            try:
                # Esperar que la tasca es cancel·li
                await self.bus_task
            except asyncio.CancelledError:
                # Ignorar excepció de cancel·lació
                pass
        
        print("[Coordinator] Sistema aturat")

    # ======== API per enviar missatges ========

    async def send_message(self, source, target, message_type, payload=None, context=None):
        """
        Envia un missatge a un agent específic.
        
        Args:
            source: Origen del missatge
            target: Destinatari
            message_type: Tipus de missatge
            payload: Dades del missatge
            context: Context addicional
        """
        # Crear objecte missatge
        message = Message(
            source=source,
            target=target,
            message_type=message_type,
            payload=payload,
            context=context
        )
        
        # Publicar al bus
        await self.bus.publish(message)

    async def send_to_miner(self, source, message_type, payload=None):
        """Mètode de conveniència per enviar a miner."""
        await self.send_message(source, "miner", message_type, payload)

    async def send_to_builder(self, source, message_type, payload=None):
        """Mètode de conveniència per enviar a builder."""
        await self.send_message(source, "builder", message_type, payload)

    async def send_to_explorer(self, source, message_type, payload=None):
        """Mètode de conveniència per enviar a explorer."""
        await self.send_message(source, "explorer", message_type, payload)

    async def broadcast(self, source, message_type, payload=None):
        """
        Envia un missatge a tots els agents registrats.
        
        Args:
            source: Origen del missatge
            message_type: Tipus de missatge
            payload: Dades del missatge
        """
        # Obtenir llista de noms d'agents
        agent_names = list(self.agents.keys())
        
        # Iterar sobre cada agent
        i = 0
        while i < len(agent_names):
            agent_name = agent_names[i]
            await self.send_message(source, agent_name, message_type, payload)
            i = i + 1

    # ======== Cicle de tick (sync loop) ========

    def tick(self):
        """
        Executa un cicle de tots els agents (cridat des del main loop).
        Cada agent executa el seu run_step() que processa missatges i fa P-D-A.
        """
        # Obtenir llista d'agents
        agent_list = list(self.agents.values())
        
        # Iterar sobre cada agent
        i = 0
        while i < len(agent_list):
            agent = agent_list[i]
            
            # Verificar si l'agent té mètode run_step
            has_run_step = hasattr(agent, 'run_step')
            if has_run_step:
                # Executar cicle de l'agent
                agent.run_step()
            
            i = i + 1

    # ======== API sincrònica per ChatListener ========

    def send_control(self, target, message_type, payload=None):
        """
        Envia un missatge de manera sincrònica des del ChatListener.
        Crea una tasca asíncrona al bus que es processarà al següent tick.
        
        Args:
            target: Nom de l'agent o "ALL" per broadcast
            message_type: Tipus de missatge
            payload: Dades opcionals
        """
        # Normalitzar target a majúscules per comparació
        target_upper = target.upper()
        
        # Verificar si és broadcast
        is_broadcast = False
        if target_upper == "ALL":
            is_broadcast = True
        
        if is_broadcast:
            # Broadcast a tots els agents
            agent_names = list(self.agents.keys())
            
            i = 0
            while i < len(agent_names):
                agent_name = agent_names[i]
                
                # Crear missatge per aquest agent
                message = Message(
                    source="chat_listener",
                    target=agent_name,
                    message_type=message_type,
                    payload=payload
                )
                
                # Publicar directament a la cua del bus (sync-safe)
                try:
                    self.bus.message_queue.put_nowait(message)
                except Exception as e:
                    print(f"[Coordinator] Error enviant a {agent_name}: {e}")
                
                i = i + 1
        else:
            # Normalitzar nom: ExplorerBot -> explorer
            target_lower = target.lower()
            target_normalized = target_lower.replace("bot", "")
            
            # Crear missatge
            message = Message(
                source="chat_listener",
                target=target_normalized,
                message_type=message_type,
                payload=payload
            )
            
            # Publicar directament a la cua del bus (sync-safe)
            try:
                self.bus.message_queue.put_nowait(message)
            except Exception as e:
                print(f"[Coordinator] Error enviant missatge: {e}")
