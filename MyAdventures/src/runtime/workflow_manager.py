# src/runtime/workflow_manager.py
import logging
from src.runtime.workflow import Workflow


class WorkflowManager:
    """
    Gestiona múltiples workflows simultanis.

    Decisió  de disseny:
    - Aplicar les comandes del chat sobre l'ultim workflow creat
      atrib last_workflow_id.
    """

    def __init__(self):
        self.workflows = {}
        self.last_workflow_id = None   # Ultim workflow creat per aplicar comandes del chat!!
        self.contador = 0

    def start_workflow(self):
        self.contador += 1
        wf_id = self.contador

        wf = Workflow(workflow_id=wf_id)
        self.workflows[wf.id] = wf
        self.last_workflow_id = wf.id

        wf.start()
        return wf.id

    def get_workflow(self, workflow_id=None):
        if workflow_id:
            return self.workflows.get(workflow_id)
        if self.last_workflow_id:
            return self.workflows.get(self.last_workflow_id)
        return None

    def stop_workflow(self, workflow_id=None):
        wf = self.get_workflow(workflow_id)
        if wf:
            wf.stop()
            
    def list_workflows(self):
        return list(self.workflows.keys())
