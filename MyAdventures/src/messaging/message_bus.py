import asyncio
import src.messaging.validator as MessageValidator

class MessageBus:
    """
    Patró Mediator (asíncron).
    Gestiona la comunicació entre agents mitjançant missatges.
    """

    def __init__(self):
        # handlers registrats per agent
        self.subscribers = {}   # agent_name -> handler(message)
        self.message_queue = asyncio.Queue()
        self.running = False

    # ========= REGISTRE =========

    def subscribe(self, agent_name, handler):
        """
        Registra el handler d’un agent.
        """
        self.subscribers[agent_name] = handler
        print(f"[MessageBus] Subscriptor registrat: {agent_name}")

    def unsubscribe(self, agent_name):
        if agent_name in self.subscribers:
            del self.subscribers[agent_name]

    # ========= ENVIAMENT =========

    async def publish(self, message):
        """
        Valida i envia un missatge al bus (asíncron).
        """
        MessageValidator.validate(message)
        await self.message_queue.put(message)

    # ========= LOOP PRINCIPAL =========

    async def run(self):
        """
        Loop asíncron del bus.
        """
        self.running = True
        print("[MessageBus] Iniciada...")

        try:
            while self.running:
                message = await self.message_queue.get()
                self._dispatch(message)

        except asyncio.CancelledError:
            print("[MessageBus] Cancel·lada")

    def _dispatch(self, message):
        """
        Enruta el missatge al destinatari.
        """
        target = message.target

        if target == "ALL":
            for name, handler in self.subscribers.items():
                if name != message.source:
                    handler(message)
            return

        handler = self.subscribers.get(target)
        if handler:
            handler(message)
        else:
            print(f"[MessageBus] Destinatari desconegut: {target}")

    # ========= ATURADA =========

    async def stop(self):
        """
        Atura el loop del bus.
        """
        self.running = False
        print("[MessageBus] Aturant...")
