"""Carregador dinàmic d'agents alineat amb l'arquitectura actual."""
import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Any, List, Type

log = logging.getLogger(__name__)


class AgentLoader:
    """Carrega classes d'agents des de ``agents_dir`` i les instancia."""

    def __init__(self, agents_dir="src/agents"):
        self.agents_dir = Path(agents_dir)
        # Cache per la classe BaseAgent
        self._base_agent = None

    def _get_base_agent(self):
        """Obté la classe BaseAgent amb caché."""
        # Verificar si ja està en cache
        is_cached = False
        if self._base_agent is not None:
            is_cached = True
        
        if not is_cached:
            try:
                # Importar BaseAgent
                from src.agents.base_agent import BaseAgent

                # Emmagatzemar en cache
                self._base_agent = BaseAgent
            except Exception as exc:
                log.error(f"No es pot importar BaseAgent: {exc}")
                raise
        
        return self._base_agent

    def _discover_modules(self):
        """Descobreix mòduls Python al directori d'agents."""
        # Inicialitzar llista de mòduls
        modules = list()

        # Verificar si el directori existeix
        dir_exists = self.agents_dir.exists()
        if not dir_exists:
            log.warning(f"Directori no existeix: {self.agents_dir}")
            return modules

        # Obtenir llista de fitxers Python
        file_paths = list(self.agents_dir.glob("*.py"))
        
        # Iterar sobre cada fitxer
        i = 0
        while i < len(file_paths):
            file_path = file_paths[i]
            
            # Saltar fitxers especials
            file_name = file_path.name
            is_init = False
            is_base = False
            
            if file_name == "__init__.py":
                is_init = True
            if file_name == "base_agent.py":
                is_base = True
            
            if is_init or is_base:
                i = i + 1
                continue

            # Convertir path a import path (ex: src/agents/miner.py -> src.agents.miner)
            module_path = str(file_path.with_suffix(""))
            module_path = module_path.replace(os.sep, ".")
            
            # Afegir a la llista
            modules.append(module_path)
            log.debug(f"Trobat modul: {module_path}")
            
            i = i + 1

        return modules

    def _import_module(self, module_path):
        """Importa un mòdul pel seu path."""
        module = None
        
        try:
            # Intentar importar el mòdul
            module = importlib.import_module(module_path)
        except Exception as exc:
            log.error(f"Error important {module_path}: {exc}")
            module = None
        
        return module

    def _find_agent_classes(self, module):
        """Troba totes les classes d'agents dins d'un mòdul."""
        # Obtenir classe base
        BaseAgent = self._get_base_agent()
        
        # Inicialitzar llista de classes
        classes = list()

        # Obtenir tots els membres del mòdul que siguin classes
        members = inspect.getmembers(module, inspect.isclass)
        
        # Iterar sobre cada membre
        i = 0
        while i < len(members):
            name, obj = members[i]
            
            # Saltar si és la classe BaseAgent mateixa
            is_base_agent = False
            if obj is BaseAgent:
                is_base_agent = True
            
            if is_base_agent:
                i = i + 1
                continue
            
            # Verificar si és subclasse de BaseAgent
            is_subclass = False
            try:
                if issubclass(obj, BaseAgent):
                    is_subclass = True
            except TypeError:
                # No és una classe vàlida
                pass
            
            if not is_subclass:
                i = i + 1
                continue
            
            # Verificar que la classe està definida en aquest mòdul
            is_from_module = False
            if obj.__module__ == module.__name__:
                is_from_module = True
            
            if not is_from_module:
                i = i + 1
                continue
            
            # Afegir classe vàlida
            classes.append(obj)
            log.info(f"Classe agent trobada: {obj.__name__}")
            
            i = i + 1

        return classes

    def _instantiate(self, cls, mc_client, coordinator=None):
        """Instancia una classe d'agent amb els paràmetres donats."""
        agent = None
        
        try:
            # Crear instància de l'agent
            agent = cls(mc_client)
            
            # Verificar si cal injectar el coordinador
            has_coordinator = False
            if coordinator is not None:
                has_coordinator = True
            
            if has_coordinator:
                # Verificar si l'agent té mètode set_coordinator
                has_setter = hasattr(agent, "set_coordinator")
                
                if has_setter:
                    # Injectar coordinador
                    agent.set_coordinator(coordinator)
            
            log.info(f"Instanciat agent: {agent.name}")
            return agent
            
        except Exception as exc:
            log.error(f"Error instanciant {cls.__name__}: {exc}")
            return None

    def load(self, mc_client, coordinator=None):
        """Descobreix, importa i instancia tots els agents a ``agents_dir``."""

        # Assegurar que l'arrel del projecte està al sys.path per imports amb punts
        project_root = Path(__file__).resolve().parent.parent
        project_root_str = str(project_root)
        
        # Verificar si ja està al path
        is_in_path = False
        i = 0
        while i < len(sys.path):
            if sys.path[i] == project_root_str:
                is_in_path = True
                break
            i = i + 1
        
        if not is_in_path:
            sys.path.insert(0, project_root_str)

        # Descobrir mòduls
        modules = self._discover_modules()
        
        # Inicialitzar llista d'agents
        agents = list()

        # Processar cada mòdul
        i = 0
        while i < len(modules):
            module_path = modules[i]
            
            # Importar mòdul
            module = self._import_module(module_path)
            
            # Verificar si la importació va tenir èxit
            import_success = False
            if module is not None:
                import_success = True
            
            if not import_success:
                i = i + 1
                continue

            # Trobar classes d'agents al mòdul
            agent_classes = self._find_agent_classes(module)
            
            # Instanciar cada classe trobada
            j = 0
            while j < len(agent_classes):
                cls = agent_classes[j]
                
                # Instanciar agent
                agent = self._instantiate(cls, mc_client, coordinator)
                
                # Afegir a la llista si la instanciació va tenir èxit
                if agent is not None:
                    agents.append(agent)
                
                j = j + 1
            
            i = i + 1

        # Registrar resum de càrrega
        agent_count = len(agents)
        log.info(f"Carrega completada: {agent_count} agent(s) carregat(s)")
        
        return agents
