import time
import os
from datetime import datetime
from src.application.state_observer import StateObserver

class WorkflowObserver(StateObserver):

    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.events = []  # historial


        #per cada workflow, un fitxer de logs de l'observer ->traçabilitat persistent dels canvis d'estat.
        os.makedirs("logs", exist_ok=True)
        self.log_file = f"logs/workflow_{workflow_id}.txt"
    
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== Workflow {workflow_id} iniciat ===\n")

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

        #pels logs:
        timestamp = datetime.fromtimestamp(event["time"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        line = (f"[{timestamp}] "
        f"{agent_name} → {new_state.name} | {reason}"
        )
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

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
