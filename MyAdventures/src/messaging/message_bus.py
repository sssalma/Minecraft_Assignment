"""Bus de missatges asíncron per comunicació entre agents."""
import asyncio
from typing import Callable, Any, Dict, List
from .message import Message


class MessageBus:
    """
    Bus de missatges asíncron que coordina la comunicació entre agents.
    Patró: Publisher-Subscriber amb enrutament per destinatari.
    """

    def __init__(self):
        """Inicialitza el bus de missatges."""
        # Taula d'enrutament: destinatari -> llista de callbacks
        self.subscribers = dict()
        # Cua FIFO per emmagatzemar missatges pendents  
        self.message_queue = asyncio.Queue()
        # Bandera de control del bucle d'events
        self.running = False

    def subscribe(self, target, handler):
        """
        Registra un callback per rebre missatges dirigits a un destinatari.
        
        Args:
            target: Identificador del destinatari
            handler: Funció callback que processa el missatge
        """
        # Inicialitzar llista si el destinatari no existeix
        target_exists = False
        for key in self.subscribers.keys():
            if key == target:
                target_exists = True
                break
        
        if not target_exists:
            self.subscribers[target] = list()
        
        # Afegir handler a la llista
        self.subscribers[target].append(handler)
        print(f"[MessageBus] Handler registrat per '{target}'")

    def unsubscribe(self, target, handler):
        """Elimina un callback d'un destinatari."""
        # Comprovar existència del destinatari
        target_exists = False
        for key in self.subscribers.keys():
            if key == target:
                target_exists = True
                break
        
        if not target_exists:
            return
        
        # Comprovar existència del handler i trobar índex
        handler_list = self.subscribers[target]
        handler_exists = False
        handler_index = -1
        
        i = 0
        while i < len(handler_list):
            if handler_list[i] == handler:
                handler_exists = True
                handler_index = i
                break
            i = i + 1
        
        if handler_exists:
            # Eliminar handler per índex
            del self.subscribers[target][handler_index]
            print(f"[MessageBus] Handler eliminat de '{target}'")

    async def publish(self, message):
        """
        Insereix un missatge a la cua per processar-lo.
        
        Args:
            message: Objecte Message a encuar
        """
        # Operació atòmica d'escriptura a la cua
        await self.message_queue.put(message)
        print(f"[MessageBus] Missatge publicat: {message}")

    async def _process_message(self, message):
        """
        Enruta un missatge als callbacks registrats per al destinatari.
        
        Args:
            message: Missatge a processar
        """
        # Extreure destinatari del missatge
        target = message.target
        
        # Buscar destinatari a la taula d'enrutament
        target_exists = False
        for key in self.subscribers.keys():
            if key == target:
                target_exists = True
                break
        
        if not target_exists:
            print(f"[MessageBus] Cap handler registrat per '{target}'")
            return

        # Obtenir llista de handlers
        handlers = self.subscribers[target]
        handler_count = len(handlers)
        print(f"[MessageBus] Enrutant a {handler_count} handler(s) de '{target}'")

        # Llista per emmagatzemar coroutines pendents
        async_tasks = list()
        
        # Iterar sobre cada handler
        i = 0
        while i < handler_count:
            handler = handlers[i]
            
            try:
                # Invocar handler
                result = handler(message)
                
                # Detectar si el resultat és una coroutine
                is_coroutine = asyncio.iscoroutine(result)
                
                if is_coroutine:
                    # Afegir coroutine a la llista de tasques
                    async_tasks.append(result)
            except Exception as e:
                print(f"[MessageBus] Error en handler de '{target}': {e}")
            
            i = i + 1

        # Executar totes les coroutines en paral·lel si n'hi ha
        task_count = len(async_tasks)
        if task_count > 0:
            await asyncio.gather(*async_tasks, return_exceptions=True)

    async def run(self):
        """
        Bucle d'events principal: extreu missatges de la cua i els processa.
        S'executa en background: asyncio.create_task(bus.run())
        """
        # Activar bandera de control
        self.running = True
        print("[MessageBus] Iniciada...")
        
        try:
            # Bucle infinit controlat per bandera
            while self.running == True:
                message = None
                timeout_occurred = False
                
                try:
                    # Operació de lectura bloquejant amb timeout d'1 segon
                    message = await asyncio.wait_for(
                        self.message_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    # Timeout expirat sense missatges - continuar bucle
                    timeout_occurred = True
                
                # Processar missatge si s'ha rebut
                if not timeout_occurred and message is not None:
                    await self._process_message(message)
                    
        except asyncio.CancelledError:
            # Tasca cancel.lada externament
            print("[MessageBus] Deturat per cancel.lacio")
            self.running = False
        except Exception as e:
            # Error no controlat
            print(f"[MessageBus] Error critic: {e}")
            self.running = False

    async def stop(self):
        """Desactiva el bucle d'events."""
        self.running = False
        print("[MessageBus] Aturant...")


# Variable global per instància singleton
_bus_instance = None


def get_bus():
    """Retorna la instància singleton del bus."""
    global _bus_instance
    
    # Inicialització lazy
    instance_exists = False
    if _bus_instance is not None:
        instance_exists = True
    
    if not instance_exists:
        _bus_instance = MessageBus()
    
    return _bus_instance
