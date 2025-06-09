import asyncio
import random
import uuid
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from config import WAREHOUSE_JID
from datetime import datetime

def log_agent_comm(sender, receiver, msg_type):
    with open("agent_comm_log.csv", "a") as f:
        f.write(f"{datetime.now().isoformat()},{sender},{receiver},{msg_type}\n")

class CustomerAgent(Agent):
    class SendParcelRequest(OneShotBehaviour):
        async def run(self):
            for i in range(3):  # Send 3 parcels
                await asyncio.sleep(random.randint(1, 3))  # simulate delay between orders
                parcel_id = str(uuid.uuid4())
                version = 1  # Always 1 unless you handle retries elsewhere
                parcel_info = (
                    f"Parcel {i + 1}: Deliver to Piata {random.choice(['700', 'Victoriei', 'Libertatii'])}, "
                    f"Weight: {random.randint(1, 5)}kg, Urgency: {random.choice(['low', 'medium', 'high'])}"
                )
                msg = Message(to=WAREHOUSE_JID)
                msg.set_metadata("performative", "request")
                msg.set_metadata("type", "parcel")
                msg.body = f"{parcel_id}|{version}|{parcel_info}"
                await self.send(msg)
                log_agent_comm(str(self.agent.jid), WAREHOUSE_JID, "parcel")
                print(f"📦 Customer: Sent parcel request {i + 1} with id={parcel_id} and version={version}")

    async def setup(self):
        print(f"🟢 CustomerAgent ({str(self.jid)}) started.")
        self.add_behaviour(self.SendParcelRequest())
