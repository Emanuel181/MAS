# agents/supervisor_agent.py
import uuid

from slixmpp import jid
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from collections import defaultdict
from datetime import datetime
from settings import DATABASE_JID, GIS_JID, WAREHOUSE_LOCATION


class SupervisorAgent(Agent):
    """
    Monitors all courier agents, performs intelligent load balancing,
    and handles queries about parcel statuses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.courier_stats = {}  # Live status of each courier

        # FIX 1: The CSV header is now written here, only once on startup.
        # This creates/clears the file and writes the column names.
        with open("courier_status.csv", "w") as f:
            f.write("jid,location,battery,load,is_busy,last_updated\n")

    class MonitorAndQueryHandler(CyclicBehaviour):
        """
        Listens for courier status updates, delivery reports, and
        customer parcel status queries.
        """

        async def run(self):
            msg = await self.receive(timeout=5)
            if not msg:
                return

            msg_type = msg.metadata.get("type")

            if msg_type == "courier_status":
                jid, loc, bat, load, busy = msg.body.split('|')
                self.agent.courier_stats[jid] = {
                    "location": loc, "battery": float(bat),
                    "load": load, "is_busy": busy == 'True',
                    "last_updated": datetime.now()
                }

                # FIX 2: The code to write a data row is moved here.
                # It now runs correctly because jid, loc, bat, etc. exist in this scope.
                with open("courier_status.csv", "a") as f:
                    f.write(f"{jid},{loc},{bat},{load},{busy},{datetime.now().isoformat()}\n")


            elif msg_type == "delivery_report":
                parcel_id, status, timestamp = msg.body.split('|')
                print(f"📈 Supervisor: Received delivery report for {parcel_id}. Status: {status}")
                db_msg = Message(to=DATABASE_JID)
                db_msg.set_metadata("performative", "update")
                db_msg.set_metadata("type", "delivery_log")
                db_msg.body = f"{parcel_id}|{status}|{timestamp}"
                await self.send(db_msg)

            elif msg_type == "parcel_status_query":
                parcel_id = msg.body
                print(f"❓ Supervisor: Customer {msg.sender.user} asks about parcel {parcel_id}.")
                # Query DB for parcel status
                db_query = Message(to=DATABASE_JID)
                db_query.set_metadata("performative", "query")
                db_query.set_metadata("type", "parcel_info")
                db_query.thread = str(uuid.uuid4())
                db_query.body = parcel_id
                await self.send(db_query)

                # Wait for DB response
                db_res = await self.receive(timeout=5)
                if db_res and db_res.thread == db_query.thread:
                    response_msg = Message(to=str(msg.sender))
                    response_msg.set_metadata("performative", "inform")
                    response_msg.set_metadata("type", "status_update")
                    response_msg.body = db_res.body  # Forward the DB response
                    await self.send(response_msg)

    class LoadBalancer(CyclicBehaviour):
        """
        Responds to requests from the Warehouse for the best courier
        for a new assignment.
        """

        async def run(self):
            msg = await self.receive(timeout=5)
            if msg and msg.metadata.get("type") == "best_courier_request":
                print("⚖️ Supervisor: Load balancing request received from Warehouse.")
                available_couriers = [
                    (jid, stats) for jid, stats in self.agent.courier_stats.items()
                    if not stats["is_busy"] and stats["battery"] > 25
                ]

                best_courier = None
                if available_couriers:
                    # Simple scoring: lower load and closer to warehouse is better
                    # A more complex scoring function could be used here
                    best_courier = min(available_couriers, key=lambda c: int(c[1]['load'].split('/')[0]))[0]

                response = Message(to=str(msg.sender))
                response.thread = msg.thread
                response.set_metadata("performative", "inform")
                response.set_metadata("type", "best_courier_response")
                response.body = best_courier if best_courier else "NONE"
                await self.send(response)
                if best_courier:
                    print(f"✅ Supervisor: Selected {best_courier} for the job.")
                else:
                    print("⚠️ Supervisor: No suitable couriers found.")

    async def setup(self):
        print(f"🟢 SupervisorAgent ({str(self.jid)}) started.")
        self.add_behaviour(self.MonitorAndQueryHandler())
        # Template for load balancing requests
        template_load = Template()
        template_load.set_metadata("performative", "request")
        template_load.set_metadata("type", "best_courier_request")
        self.add_behaviour(self.LoadBalancer(), template_load)