# agents/warehouse_agent.py

import asyncio
import uuid
from collections import deque
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from settings import SUPERVISOR_JID, DATABASE_JID

def log_agent_comm(sender, receiver, msg_type, content=""):
    """Logs communication between agents."""
    # Implementation of logging function

STATE_IDLE = "STATE_IDLE"
STATE_REQUEST_COURIER = "STATE_REQUEST_COURIER"
STATE_AWAIT_ASSIGNMENT = "STATE_AWAIT_ASSIGNMENT"

class WarehouseAgent(Agent):
    """
    Manages incoming parcel requests, prioritizes them, and works with the
    Supervisor to get them assigned to the best available courier.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parcel_queue = []
        self.parcel_being_assigned = None

    class ParcelManagementFSM(FSMBehaviour):
        async def on_start(self):
            print("📦 Warehouse FSM starting.")

    class IdleState(State):
        """
        Waits for new parcel requests from customers or checks the internal
        queue for parcels that need assignment.
        """
        async def run(self):
            # Check for incoming parcels from customers
            msg = await self.receive(timeout=5)
            if msg and msg.metadata.get("type") == "parcel_creation":
                parcel_id, urgency, info = msg.body.split('|', 2)
                print(f"🏢 Warehouse: Received new parcel request {parcel_id}.")
                log_agent_comm(str(msg.sender), str(self.agent.jid), "parcel_creation", f"ID: {parcel_id}")

                # Store parcel in DB
                db_msg = Message(to=DATABASE_JID)
                db_msg.set_metadata("performative", "update")
                db_msg.set_metadata("type", "parcel_log")
                db_msg.body = f"{parcel_id}|{urgency}|PENDING|{info}"
                await self.send(db_msg)
                self.agent.parcel_queue.append(msg.body)

            # If there are parcels to be assigned, move to the next state
            if self.agent.parcel_queue:
                self.set_next_state(STATE_REQUEST_COURIER)
            else:
                self.set_next_state(STATE_IDLE)

    class RequestCourierState(State):
        """
        Prioritizes a parcel and requests a suitable courier from the Supervisor.
        """
        async def run(self):
            # Prioritization logic (urgency and age)
            self.agent.parcel_queue.sort(key=lambda p: ({"high": 0, "medium": 1, "low": 2}[p.split('|')[1]], p.split('|')[0]))
            self.agent.parcel_being_assigned = self.agent.parcel_queue.pop(0)
            parcel_id = self.agent.parcel_being_assigned.split('|')[0]

            print(f"🛠️ Warehouse: Processing parcel {parcel_id}. Requesting best courier.")
            req = Message(to=SUPERVISOR_JID)
            req.set_metadata("performative", "request")
            req.set_metadata("type", "best_courier_request")
            req.thread = str(uuid.uuid4())
            await self.send(req)
            log_agent_comm(str(self.agent.jid), SUPERVISOR_JID, "best_courier_request", f"Parcel ID: {parcel_id}")

            self.set_next_state(STATE_AWAIT_ASSIGNMENT)

    class AwaitAssignmentState(State):
        """
        Waits for the Supervisor's courier choice and assigns the parcel.
        """
        async def run(self):
            res = await self.receive(timeout=10)
            parcel_to_assign = self.agent.parcel_being_assigned

            if res and res.metadata.get("type") == "best_courier_response":
                courier_jid = res.body
                if courier_jid != "NONE":
                    print(f"✅ Warehouse: Supervisor assigned {courier_jid} to parcel {parcel_to_assign.split('|')[0]}")
                    assign_msg = Message(to=courier_jid)
                    assign_msg.set_metadata("performative", "inform")
                    assign_msg.set_metadata("type", "parcel_assignment")
                    assign_msg.body = parcel_to_assign
                    await self.send(assign_msg)
                    log_agent_comm(str(self.agent.jid), courier_jid, "parcel_assignment", f"Parcel: {parcel_to_assign.split('|')[0]}")
                else:
                    print(f"⚠️ Warehouse: No couriers available. Re-queuing parcel.")
                    self.agent.parcel_queue.append(parcel_to_assign) # Re-queue
            else:
                print(f"⚠️ Warehouse: No response from Supervisor. Re-queueing parcel.")
                self.agent.parcel_queue.append(parcel_to_assign) # Re-queue

            self.agent.parcel_being_assigned = None
            self.set_next_state(STATE_IDLE)

    async def setup(self):
        print(f"🟢 WarehouseAgent ({self.jid}) started.")
        fsm = self.ParcelManagementFSM()
        fsm.add_state(name=STATE_IDLE, state=self.IdleState(), initial=True)
        fsm.add_state(name=STATE_REQUEST_COURIER, state=self.RequestCourierState())
        fsm.add_state(name=STATE_AWAIT_ASSIGNMENT, state=self.AwaitAssignmentState())
        fsm.add_transition(source=STATE_IDLE, dest=STATE_IDLE)
        fsm.add_transition(source=STATE_IDLE, dest=STATE_REQUEST_COURIER)
        fsm.add_transition(source=STATE_REQUEST_COURIER, dest=STATE_AWAIT_ASSIGNMENT)
        fsm.add_transition(source=STATE_AWAIT_ASSIGNMENT, dest=STATE_IDLE)
        self.add_behaviour(fsm)