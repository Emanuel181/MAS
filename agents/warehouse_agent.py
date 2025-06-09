# agents/warehouse_agent.py

import asyncio
from collections import deque
import uuid
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from config import SUPERVISOR_JID
from datetime import datetime

def log_agent_comm(sender, receiver, msg_type):
    with open("agent_comm_log.csv", "a") as f:
        f.write(f"{datetime.now().isoformat()},{sender},{receiver},{msg_type}\n")

STATE_WAIT_PARCEL = "STATE_WAIT_PARCEL"
STATE_ASSIGN_COURIER = "STATE_ASSIGN_COURIER"

class WarehouseAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parcel_queue = deque()
        self.parcel_to_assign = None

    class ParcelFSM(FSMBehaviour):
        async def on_start(self):
            print("📦 Parcel FSM starting at state WAIT_PARCEL")

        async def on_end(self):
            print("📦 Parcel FSM finished")

    class WaitParcelState(State):
        async def run(self):
            print("⌛ Warehouse waiting for parcel requests...")
            # If a parcel is already queued, dequeue and assign
            if self.agent.parcel_queue:
                self.agent.parcel_to_assign = self.agent.parcel_queue.popleft()
                self.set_next_state(STATE_ASSIGN_COURIER)
                return

            # Otherwise, wait for new incoming parcels
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 10:
                msg = await self.receive(timeout=1)
                if msg and msg.metadata.get("performative") == "request" and msg.metadata.get("type") == "parcel":
                    print(f"🏢 Warehouse received a parcel request: {msg.body}")
                    self.agent.parcel_queue.append(msg.body)
                    # Log receiving parcel from CustomerAgent
                    log_agent_comm(str(msg.sender), str(self.agent.jid), "parcel")
                    if len(self.agent.parcel_queue) == 1 and self.agent.parcel_to_assign is None:
                        self.agent.parcel_to_assign = self.agent.parcel_queue.popleft()
                        self.set_next_state(STATE_ASSIGN_COURIER)
                        return
            self.set_next_state(STATE_WAIT_PARCEL)

    class AssignCourierState(State):
        async def run(self):
            parcel = self.agent.parcel_to_assign
            print(f"🛠️ Processing parcel: {parcel}")

            thread_id = str(uuid.uuid4())
            load_request = Message(to=SUPERVISOR_JID)
            load_request.thread = thread_id
            load_request.set_metadata("performative", "request")
            load_request.set_metadata("type", "load_balance")
            await self.send(load_request)
            log_agent_comm(str(self.agent.jid), SUPERVISOR_JID, "load_balance")

            print("📊 Requesting least loaded courier from Supervisor.")

            # Wait for Supervisor's response (with correct thread)
            response = None
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 5:
                msg = await self.receive(timeout=1)
                if msg and msg.thread == thread_id:
                    response = msg
                    # Log receiving load_balance response
                    log_agent_comm(str(msg.sender), str(self.agent.jid), "load_response")
                    break
                elif msg:
                    print(f"⚠️ Warehouse FSM received unexpected message: {msg.body}")

            if response:
                chosen_courier_jid = response.body.strip()
                if chosen_courier_jid == "NONE":
                    print(f"⚠️ All couriers overloaded. Parcel will be re-queued: {parcel}")
                    self.agent.parcel_queue.appendleft(parcel)
                else:
                    print(f"✅ Supervisor selected courier: '{chosen_courier_jid}'")
                    forward = Message(to=chosen_courier_jid)
                    forward.set_metadata("performative", "inform")
                    forward.set_metadata("type", "parcel_assignment")
                    forward.body = parcel
                    await self.send(forward)
                    log_agent_comm(str(self.agent.jid), chosen_courier_jid, "parcel_assignment")
                    print(f"🚚 Assigned parcel to courier {chosen_courier_jid}.")
            else:
                print(f"⚠️ No response from Supervisor for parcel: {parcel}. Re-queueing parcel.")
                self.agent.parcel_queue.appendleft(parcel)

            self.agent.parcel_to_assign = None
            self.set_next_state(STATE_WAIT_PARCEL)

    async def setup(self):
        print(f"🟢 WarehouseAgent ({self.jid}) started.")
        fsm = self.ParcelFSM()
        fsm.add_state(name=STATE_WAIT_PARCEL, state=self.WaitParcelState(), initial=True)
        fsm.add_state(name=STATE_ASSIGN_COURIER, state=self.AssignCourierState())
        fsm.add_transition(source=STATE_WAIT_PARCEL, dest=STATE_ASSIGN_COURIER)
        fsm.add_transition(source=STATE_WAIT_PARCEL, dest=STATE_WAIT_PARCEL)
        fsm.add_transition(source=STATE_ASSIGN_COURIER, dest=STATE_WAIT_PARCEL)
        self.add_behaviour(fsm)
