"""Template registry and loader."""
from .simple_house import SimpleHouse
from .pilar import Pilar
from .table import Table

# Registry of all available templates
_TEMPLATES = {
    "simple_house": SimpleHouse,
    "pilar": Pilar,
    "table": Table,
}


def list_templates():
    """Return list of available template names."""
    return list(_TEMPLATES.keys())


def get_template(name: str):
    """
    Get a template instance by name.
    
    Args:
        name: Template name (e.g., "simple_house")
        
    Returns:
        Template instance or None if not found
    """
    template_class = _TEMPLATES.get(name)
    if template_class:
        return template_class()
    return None


def get_all_templates():
    """Return list of all template instances."""
    return [cls() for cls in _TEMPLATES.values()]
