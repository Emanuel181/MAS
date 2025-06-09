from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import random
from datetime import datetime

def log_agent_comm(sender, receiver, msg_type):
    with open("agent_comm_log.csv", "a") as f:
        f.write(f"{datetime.now().isoformat()},{sender},{receiver},{msg_type}\n")

class TrafficAgent(Agent):
    class RouteRequestHandler(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print(f"🚦 TrafficAgent received route request from {msg.sender}")

                # Simulate generating a traffic-aware route
                routes = [
                    "Route A → B → C",
                    "Route A → D → C (faster)",
                    "Route A → E → F → C",
                ]
                route = random.choice(routes)

                response = Message(to=str(msg.sender))
                response.thread = msg.thread
                response.set_metadata("performative", "inform")
                response.set_metadata("type", "route")
                response.body = route
                await self.send(response)
                # Log the response (TrafficAgent → courier)
                log_agent_comm(str(self.agent.jid), str(msg.sender), "route")

                print(f"🧭 Sent optimal route: {route}")
            else:
                print("⌛ TrafficAgent waiting for requests...")

    async def setup(self):
        print(f"🟢 TrafficAgent ({str(self.jid)}) started.")
        template = Template()
        template.set_metadata("performative", "request")
        template.set_metadata("type", "route")
        self.add_behaviour(self.RouteRequestHandler(), template)
