from queue import Queue

class MessageBus:
    """
    Patró Mediator / Singleton.
    Gestiona l'intercanvi asíncron de missatges entre agents.
    """
    _instance = None

    # Singleton per assegurar que només hi ha un Bus!!
    def __new__(cls): 
        #cls és com self(instància) pero de classe.
        if cls._instance is None: #només el primer cop és None.
            cls._instance = super(MessageBus, cls).__new__(cls) #la creo
            cls._instance.channels = {} #Diccionari per les cues dels agents {agentA: Queue(), agentB:Queue()}
        return cls._instance

    def register(self, agent_name):
        """Crea una bústia per a un agent nou."""
        if agent_name not in self.channels:
            self.channels[agent_name] = Queue()
            print(f"[BUS] Canal registrat per: {agent_name}")

    def send(self, message):
        """
        Envia un missatge a la bústia del destinatari.
        Comunicació asíncrona: és com un observer ""indirecte"" -> Patró Pub/sub
        """
        target = message.target
        
        # Si és un missatge Broadcast; p.e. del builder, encuo en totes les cues menys la meva
        if target == "ALL":
            for name, queue in self.channels.items():
                if name != message.source:
                    queue.put(message)
            return

        # Missatge directe
        if target in self.channels:
            self.channels[target].put(message)
        else:
            print(f"[BUS] Error: agent destinatari desconegut: {target}")



    def receive(self, agent_name):
        """Retorna tots els missatges pendents de la bústia de l'agent."""
        messages = []
        if agent_name in self.channels:
            queue = self.channels[agent_name]
            # per cada receive , retorno tots els missatges acumulats a la cua de l'agent.
            while not queue.empty():
                messages.append(queue.get())
        return messages