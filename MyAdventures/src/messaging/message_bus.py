from queue import Queue
from messaging.validator import MessageValidator


class MessageBus:
    """
    Patró Mediator.
    Gestiona l'intercanvi asíncron de missatges entre agents.
    """

    def __init__(self):
        self.channels = {}

    def register(self, agent_name):
        if agent_name not in self.channels:
            self.channels[agent_name] = Queue()
            print(f"[BUS] Canal registrat per: {agent_name}")

    def send(self, message):
        MessageValidator.validate(message)

        target = message.target

        if target == "ALL":
            for name, queue in self.channels.items():
                if name != message.source:
                    queue.put(message)
            return

        if target in self.channels:
            self.channels[target].put(message)
        else:
            print(f"[BUS] Error: agent destinatari desconegut: {target}")

    def receive(self, agent_name):
        messages = []
        if agent_name in self.channels:
            queue = self.channels[agent_name]
            while not queue.empty():
                messages.append(queue.get())
        return messages
