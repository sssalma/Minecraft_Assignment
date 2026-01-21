import time
from src.application.state_observer import StateObserver

class WorkflowObserver(StateObserver):

    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.events = []  # historial

    def on_state_change(self, agent_name, new_state, reason):
        event = {
            "time": time.time(),
            "agent": agent_name,
            "state": new_state.name,
            "reason": reason
        }
        self.events.append(event)

        print(
            f"[Workflow {self.workflow_id}] "
            f"{agent_name} → {new_state.name} | {reason}"
        )

    def get_status(self):
        latest = {}
        for e in self.events:
            latest[e["agent"]] = e["state"]
        return latest

    def get_range(self, seconds):
        now = time.time()
        return [
            e for e in self.events
            if now - e["time"] <= seconds
        ]
