"""Dynamic agent loader using reflection."""
import os
import sys
import importlib
import inspect
import logging
from pathlib import Path
from typing import List, Type, Any

log = logging.getLogger(__name__)


class AgentLoader:
    """
    Carrega agents dinàmicament des de directoris especificats.
    Utilitza reflection per descobrir i instanciar automàticament.
    """

    def __init__(self, agents_dir: str = "src/agents", strategies_dir: str = "src/strategies"):
        """
        Inicialitza el loader.
        
        Args:
            agents_dir: Directori on buscar agents
            strategies_dir: Directori on buscar estratègies (opcional)
        """
        self.agents_dir = agents_dir
        self.strategies_dir = strategies_dir
        self.base_agent_class = None

    def _get_base_agent_class(self):
        """Importa i retorna la classe BaseAgent."""
        if self.base_agent_class is None:
            try:
                from ..agents.base_agent import BaseAgent
                self.base_agent_class = BaseAgent
            except ImportError as e:
                log.error(f"No es pot importar BaseAgent: {e}")
                raise
        return self.base_agent_class

    def _scan_directory(self, directory: str) -> List[str]:
        """
        Escaneja un directori i retorna mòduls Python vàlids.
        
        Args:
            directory: Path al directori
            
        Returns:
            Llista de paths de mòduls (ex: "src.agents.miner_agent")
        """
        modules = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            log.warning(f"Directori no existeix: {directory}")
            return modules

        for file_path in dir_path.glob("*.py"):
            # Ignorar __init__.py i base_agent.py
            if file_path.name in ("__init__.py", "base_agent.py"):
                continue
            
            # Convertir path a module name: src/agents/miner_agent.py -> src.agents.miner_agent
            module_path = str(file_path.with_suffix("")).replace(os.sep, ".")
            modules.append(module_path)
            log.info(f"Trobat modul: {module_path}")

        return modules

    def _import_module(self, module_path: str):
        """
        Importa un mòdul dinàmicament.
        
        Args:
            module_path: Path del mòdul (ex: "src.agents.miner_agent")
            
        Returns:
            Mòdul importat o None si falla
        """
        try:
            module = importlib.import_module(module_path)
            log.debug(f"Importat: {module_path}")
            return module
        except Exception as e:
            log.error(f"Error important {module_path}: {e}")
            return None

    def _find_agent_classes(self, module) -> List[Type]:
        """
        Troba totes les classes que hereden de BaseAgent en un mòdul.
        
        Args:
            module: Mòdul importat
            
        Returns:
            Llista de classes agent trobades
        """
        BaseAgent = self._get_base_agent_class()
        agent_classes = []

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Comprovar que:
            # 1. És una subclasse de BaseAgent
            # 2. No és BaseAgent mateix
            # 3. Està definida en aquest mòdul (no importada d'un altre)
            if (issubclass(obj, BaseAgent) and 
                obj is not BaseAgent and 
                obj.__module__ == module.__name__):
                
                agent_classes.append(obj)
                log.info(f"  Classe agent trobada: {name}")

        return agent_classes

    def _instantiate_agent(self, agent_class: Type, mc_client) -> Any:
        """
        Instancia un agent amb el client de Minecraft.
        
        Args:
            agent_class: Classe de l'agent
            mc_client: Client de Minecraft
            
        Returns:
            Instància de l'agent o None si falla
        """
        try:
            agent = agent_class(mc_client)
            log.info(f"  Instanciat: {agent.name}")
            return agent
        except Exception as e:
            log.error(f"Error instanciant {agent_class.__name__}: {e}")
            return None

    def load(self, mc_client) -> List[Any]:
        """
        Carrega tots els agents dinàmicament.
        
        Args:
            mc_client: Client de Minecraft per passar als agents
            
        Returns:
            Llista d'instàncies d'agents carregats
        """
        log.info("=" * 60)
        log.info("Iniciant carrega dinamica d'agents...")
        log.info("=" * 60)

        agents = []

        # Escanejar directori d'agents
        module_paths = self._scan_directory(self.agents_dir)
        
        if not module_paths:
            log.warning(f"Cap modul trobat a {self.agents_dir}")
            return agents

        # Processar cada mòdul
        for module_path in module_paths:
            log.info(f"\n→ Processant: {module_path}")
            
            # Importar mòdul
            module = self._import_module(module_path)
            if module is None:
                continue

            # Trobar classes agent
            agent_classes = self._find_agent_classes(module)
            
            # Instanciar agents
            for agent_class in agent_classes:
                agent = self._instantiate_agent(agent_class, mc_client)
                if agent:
                    agents.append(agent)

        log.info("=" * 60)
        log.info(f"Carrega completada: {len(agents)} agent(s) carregat(s)")
        log.info("=" * 60)
        
        return agents

    def load_strategies(self, strategy_dir: str = None) -> List[Type]:
        """
        Carrega estratègies dinàmicament (per futures extensions).
        
        Args:
            strategy_dir: Directori opcional d'estratègies
            
        Returns:
            Llista de classes d'estratègia
        """
        target_dir = strategy_dir or self.strategies_dir
        log.info(f"Escanejant estrategies a {target_dir}...")
        
        strategies = []
        module_paths = self._scan_directory(target_dir)
        
        for module_path in module_paths:
            module = self._import_module(module_path)
            if module:
                # Buscar classes que acabin amb "Strategy"
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith("Strategy") and obj.__module__ == module.__name__:
                        strategies.append(obj)
                        log.info(f"  Estrategia trobada: {name}")
        
        return strategies
