from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from collections import defaultdict
import csv
from datetime import datetime

def log_agent_comm(sender, receiver, msg_type):
    with open("agent_comm_log.csv", "a") as f:
        f.write(f"{datetime.now().isoformat()},{sender},{receiver},{msg_type}\n")

class SupervisorAgent(Agent):
    class MonitorDeliveries(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                sender = str(msg.sender).split("/")[0]
                # Log receiving the delivery report
                log_agent_comm(sender, str(self.agent.jid), "delivery_report")

                if sender in self.agent.courier_stats:
                    self.agent.courier_stats[sender] += 1
                else:
                    print(f"⚠️ Warning: Unknown courier {sender} reported delivery, ignoring")

                count = self.agent.courier_stats[sender]

                # Check overload
                if count >= self.agent.overload_threshold:
                    print(f"⚠️ Courier {sender} is overloaded! ({count} deliveries)")

                # --- Advanced CSV Logging ---
                with open("delivery_log.csv", "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    body_parts = msg.body.split('|')
                    parcel_id      = body_parts[0] if len(body_parts) > 0 else ''
                    version        = body_parts[1] if len(body_parts) > 1 else ''
                    parcel_info    = body_parts[2] if len(body_parts) > 2 else ''
                    route          = body_parts[3] if len(body_parts) > 3 else ''
                    lat            = body_parts[4] if len(body_parts) > 4 else ''
                    lon            = body_parts[5] if len(body_parts) > 5 else ''
                    start_time     = body_parts[6] if len(body_parts) > 6 else ''
                    end_time       = body_parts[7] if len(body_parts) > 7 else ''
                    writer.writerow([
                        datetime.now().isoformat(),
                        sender,
                        parcel_id,
                        version,
                        parcel_info,
                        route,
                        count,      # total delivered by this courier
                        lat,
                        lon,
                        start_time,
                        end_time
                    ])
            else:
                print("⌛ Supervisor waiting for delivery reports...")

    class LoadBalancer(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("type") == "load_balance":
                print("📊 Load balance request received.")

                overloaded = [
                    c for c, cnt in self.agent.courier_stats.items()
                    if cnt >= self.agent.overload_threshold
                ]
                valid_couriers = [
                    c for c in self.agent.courier_stats
                    if c not in overloaded
                ]
                if valid_couriers:
                    least_loaded = min(valid_couriers, key=lambda c: self.agent.courier_stats[c])
                    print(f"📤 Load balancer chose courier: {least_loaded}")
                else:
                    least_loaded = "NONE"  # special string: all overloaded!
                    print("⚠️ All couriers are overloaded. Cannot assign right now.")

                response = Message(to=str(msg.sender))
                response.thread = msg.thread
                response.set_metadata("performative", "inform")
                response.set_metadata("type", "load_response")
                response.body = least_loaded
                await self.send(response)
                # Log sending load_balance response
                log_agent_comm(str(self.agent.jid), str(msg.sender), "load_response")

    async def setup(self):
        print(f"🟢 SupervisorAgent ({str(self.jid)}) started.")
        self.overload_threshold = 3
        self.courier_stats = defaultdict(int)
        known_couriers = ["courier1@localhost", "courier2@localhost"]  # Expand as needed
        for courier in known_couriers:
            self.courier_stats[courier] = 0

        template_delivery = Template()
        template_delivery.set_metadata("performative", "inform")
        template_delivery.set_metadata("type", "delivery_report")
        self.add_behaviour(self.MonitorDeliveries(), template_delivery)

        template_load = Template()
        template_load.set_metadata("performative", "request")
        template_load.set_metadata("type", "load_balance")
        self.add_behaviour(self.LoadBalancer(), template_load)
