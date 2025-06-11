# agents/customer_agent.py

import asyncio
import random
import uuid
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from settings import WAREHOUSE_JID, SUPERVISOR_JID
from datetime import datetime, timedelta

def log_agent_comm(sender, receiver, msg_type, content=""):
    """Logs communication between agents to a CSV file."""
    with open("agent_comm_log.csv", "a") as f:
        f.write(f"{datetime.now().isoformat()},{sender},{receiver},{msg_type},{content}\n")

class CustomerAgent(Agent):
    """
    The CustomerAgent simulates a customer who creates parcel orders
    and periodically requests status updates for their parcels.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sent_parcels = {}

    class OrderAndTrackBehaviour(PeriodicBehaviour):
        """
        A periodic behaviour to create new parcel orders and track existing ones.
        """
        async def run(self):
            # Chance to create a new parcel
            if random.random() < 0.5:
                parcel_id = str(uuid.uuid4())
                urgency = random.choice(['low', 'medium', 'high'])
                destination = random.choice(['Piata Unirii', 'Piata Victoriei', 'Iulius Town'])
                parcel_info = f"Books and electronics, deliver to {destination}"

                msg = Message(to=WAREHOUSE_JID)
                msg.set_metadata("performative", "request")
                msg.set_metadata("type", "parcel_creation")
                msg.body = f"{parcel_id}|{urgency}|{parcel_info}"

                await self.send(msg)
                self.agent.sent_parcels[parcel_id] = "PENDING"
                log_agent_comm(str(self.agent.jid), WAREHOUSE_JID, "parcel_creation", f"ID: {parcel_id}")
                print(f"📦 Customer ({self.agent.jid.user}): Sent parcel request with ID: {parcel_id}")

            # Track a random pending or in-transit parcel
            trackable_parcels = [pid for pid, status in self.agent.sent_parcels.items() if status not in ["DELIVERED", "FAILED"]]
            if trackable_parcels:
                parcel_to_track = random.choice(trackable_parcels)
                print(f"🕵️ Customer ({self.agent.jid.user}): Requesting status for parcel {parcel_to_track}")
                track_msg = Message(to=SUPERVISOR_JID)
                track_msg.set_metadata("performative", "query")
                track_msg.set_metadata("type", "parcel_status")
                track_msg.body = parcel_to_track
                await self.send(track_msg)
                log_agent_comm(str(self.agent.jid), SUPERVISOR_JID, "parcel_status_query", f"ID: {parcel_to_track}")

    class StatusUpdateListener(PeriodicBehaviour):
        """
        Listens for status updates from the supervisor.
        """
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg and msg.metadata.get("type") == "status_update":
                parcel_id, status, info = msg.body.split('|', 2)
                if parcel_id in self.agent.sent_parcels:
                    self.agent.sent_parcels[parcel_id] = status
                    print(f"🔔 Customer ({self.agent.jid.user}): Status update for {parcel_id} -> {status}. Info: {info}")
                    log_agent_comm(str(msg.sender), str(self.agent.jid), "status_update_received", f"ID: {parcel_id}, Status: {status}")


    async def setup(self):
        print(f"🟢 CustomerAgent ({str(self.jid)}) started.")
        # Start ordering and tracking parcels every 10 to 20 seconds
        self.add_behaviour(self.OrderAndTrackBehaviour(period=random.randint(10, 20)))
        # Start listening for updates
        self.add_behaviour(self.StatusUpdateListener(period=5))