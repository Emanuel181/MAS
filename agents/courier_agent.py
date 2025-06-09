# agents/courier_agent.py

from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template
import asyncio
import uuid
from datetime import datetime
from config import TRAFFIC_JID, SUPERVISOR_JID

def log_agent_comm(sender, receiver, msg_type):
    with open("agent_comm_log.csv", "a") as f:
        f.write(f"{datetime.now().isoformat()},{sender},{receiver},{msg_type}\n")

STATE_WAIT_ASSIGNMENT = "STATE_WAIT_ASSIGNMENT"
STATE_REQUEST_ROUTE = "STATE_REQUEST_ROUTE"
STATE_DELIVER_PARCEL = "STATE_DELIVER_PARCEL"

class CourierAgent(Agent):
    class DeliveryFSM(FSMBehaviour):
        async def on_start(self):
            print(f"🚚 Courier FSM ({self.agent.jid.user}) starting at WAIT_ASSIGNMENT")
            self.agent.current_parcel = None
            self.agent.current_route = None
            self.agent.current_parcel_id = None
            self.agent.current_parcel_version = None
            self.agent.current_parcel_info = None
            self.agent.current_parcel_lat = None
            self.agent.current_parcel_lon = None
            self.agent.current_parcel_start = None

    class WaitAssignmentState(State):
        async def run(self):
            print(f"⌛ Courier ({self.agent.jid.user}) waiting for parcel assignments...")
            msg = await self.receive(timeout=20)
            if msg:
                print(f"🚚 Courier ({self.agent.jid.user}) received parcel: {msg.body}")
                # Log receipt of parcel assignment (optional)
                log_agent_comm(str(self.agent.jid), str(msg.sender), "parcel_assignment")
                parts = msg.body.split('|')
                self.agent.current_parcel_id = parts[0] if len(parts) > 0 else ""
                self.agent.current_parcel_version = parts[1] if len(parts) > 1 else ""
                self.agent.current_parcel_info = parts[2] if len(parts) > 2 else msg.body
                self.agent.current_parcel_lat = parts[4] if len(parts) > 4 else ""
                self.agent.current_parcel_lon = parts[5] if len(parts) > 5 else ""
                self.agent.current_parcel = msg.body
                self.agent.current_parcel_start = datetime.now().isoformat()
                self.set_next_state(STATE_REQUEST_ROUTE)
            else:
                self.set_next_state(STATE_WAIT_ASSIGNMENT)

    class RequestRouteState(State):
        async def run(self):
            print("🧭 Requesting optimal route from TrafficAgent...")
            thread_id = str(uuid.uuid4())
            route_request = Message(to=TRAFFIC_JID)
            route_request.thread = thread_id
            route_request.set_metadata("performative", "request")
            route_request.set_metadata("type", "route")
            await self.send(route_request)
            log_agent_comm(str(self.agent.jid), TRAFFIC_JID, "route")

            response = None
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 5:
                msg = await self.receive(timeout=1)
                if msg and msg.thread == thread_id:
                    response = msg
                    # Log receipt of route (optional)
                    log_agent_comm(str(self.agent.jid), str(msg.sender), "route_response")
                    break
                elif msg:
                    print(f"⚠️ Courier FSM received unexpected message: {msg.body}")

            if response:
                print(f"✅ Route acquired: {response.body}")
                self.agent.current_route = response.body
            else:
                print("⚠️ Could not acquire route from TrafficAgent.")
                self.agent.current_route = "Route unavailable 🚫"

            self.set_next_state(STATE_DELIVER_PARCEL)

    class DeliverParcelState(State):
        async def run(self):
            print("🚚 Delivering parcel...")
            await asyncio.sleep(2)  # Simulate delivery time
            print("📦 Parcel delivered.")

            delivery_end = datetime.now().isoformat()
            report = Message(to=SUPERVISOR_JID)
            report.set_metadata("performative", "inform")
            report.set_metadata("type", "delivery_report")
            report.body = f"{self.agent.current_parcel_id}|{self.agent.current_parcel_version}|{self.agent.current_parcel_info}|{self.agent.current_route}|{self.agent.current_parcel_lat}|{self.agent.current_parcel_lon}|{self.agent.current_parcel_start}|{delivery_end}"
            await self.send(report)
            log_agent_comm(str(self.agent.jid), SUPERVISOR_JID, "delivery_report")
            print("📬 Report sent to SupervisorAgent.")

            self.set_next_state(STATE_WAIT_ASSIGNMENT)

    async def setup(self):
        print(f"🟢 CourierAgent ({str(self.jid)}) started.")
        fsm = self.DeliveryFSM()
        fsm.add_state(name=STATE_WAIT_ASSIGNMENT, state=self.WaitAssignmentState(), initial=True)
        fsm.add_state(name=STATE_REQUEST_ROUTE, state=self.RequestRouteState())
        fsm.add_state(name=STATE_DELIVER_PARCEL, state=self.DeliverParcelState())
        fsm.add_transition(source=STATE_WAIT_ASSIGNMENT, dest=STATE_WAIT_ASSIGNMENT)
        fsm.add_transition(source=STATE_WAIT_ASSIGNMENT, dest=STATE_REQUEST_ROUTE)
        fsm.add_transition(source=STATE_REQUEST_ROUTE, dest=STATE_DELIVER_PARCEL)
        fsm.add_transition(source=STATE_DELIVER_PARCEL, dest=STATE_WAIT_ASSIGNMENT)
        self.add_behaviour(fsm)
