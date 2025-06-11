# agents/courier_agent.py

import asyncio
import uuid
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour
from spade.message import Message
from settings import GIS_JID, SUPERVISOR_JID, DATABASE_JID, WAREHOUSE_LOCATION
from datetime import datetime

STATE_IDLE = "STATE_IDLE"
STATE_MOVING_TO_DESTINATION = "STATE_MOVING_TO_DESTINATION"
STATE_MOVING_TO_DEPOT = "STATE_MOVING_TO_DEPOT"
STATE_CHARGING = "STATE_CHARGING"

class CourierAgent(Agent):
    """
    Represents a courier who picks up parcels, delivers them, and manages
    its own battery and capacity.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_location = WAREHOUSE_LOCATION
        self.parcels_to_deliver = []
        self.route = []
        self.battery = 100.0
        self.capacity = 5 # Max 5 parcels
        self.is_busy = False

    class DeliveryFSM(FSMBehaviour):
        async def on_start(self):
            print(f"🚚 Courier FSM ({self.agent.jid.user}) starting at IDLE.")

    class IdleState(State):
        """
        The courier is at the warehouse, ready for assignments or charging.
        """
        async def run(self):
            # If battery is low, charge first
            if self.agent.battery < 20:
                self.set_next_state(STATE_CHARGING)
                return

            print(f"⌛ Courier ({self.agent.jid.user}) is idle at the depot. Battery: {self.agent.battery:.1f}%")
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("type") == "parcel_assignment":
                self.agent.is_busy = True
                parcel_id, urgency, info = msg.body.split('|', 2)
                destination = info.split("Deliver to ")[1].split(',')[0] # Basic parsing

                self.agent.parcels_to_deliver.append({"id": parcel_id, "info": info, "destination": destination})
                print(f"👍 Courier ({self.agent.jid.user}): Accepted parcel {parcel_id}.")

                # Request a route from the GIS agent
                route_req = Message(to=GIS_JID)
                route_req.set_metadata("performative", "request")
                route_req.set_metadata("type", "route_request")
                route_req.body = f"{self.agent.current_location}|{destination}"
                await self.send(route_req)

                # Wait for route
                route_res = await self.receive(timeout=5)
                if route_res and route_res.metadata.get("type") == "route_response":
                    self.agent.route = eval(route_res.body) # Route is a list of coordinates
                    self.set_next_state(STATE_MOVING_TO_DESTINATION)
                else:
                    print(f"⛔ Courier ({self.agent.jid.user}): Could not get route. Delivery failed.")
                    # Handle failure
            else:
                 self.set_next_state(STATE_IDLE)

    class MovingToDestinationState(State):
        """
        Simulates the courier moving along the route to deliver a parcel.
        """
        async def run(self):
            target_destination = self.agent.route[-1]
            print(f"🚚 Courier ({self.agent.jid.user}): Moving to {target_destination}. Parcels: {len(self.agent.parcels_to_deliver)}")
            # Simulate movement
            await asyncio.sleep(5) # Travel time
            self.agent.battery -= 2.5 # Battery consumption

            self.agent.current_location = target_destination
            delivered_parcel = self.agent.parcels_to_deliver.pop(0)
            print(f"✅ Courier ({self.agent.jid.user}): Delivered parcel {delivered_parcel['id']} at {self.agent.current_location}.")

            # Inform Supervisor
            report = Message(to=SUPERVISOR_JID)
            report.set_metadata("performative", "inform")
            report.set_metadata("type", "delivery_report")
            report.body = f"{delivered_parcel['id']}|DELIVERED|{datetime.now().isoformat()}"
            await self.send(report)

            # If more parcels to deliver, get next route or head back to depot
            if not self.agent.parcels_to_deliver:
                self.set_next_state(STATE_MOVING_TO_DEPOT)
            else:
                # In a more complex scenario, might chain deliveries
                self.set_next_state(STATE_MOVING_TO_DEPOT) # Simplified: return after each delivery


    class MovingToDepotState(State):
        """
        Courier is returning to the main depot.
        """
        async def run(self):
            print(f"↩️ Courier ({self.agent.jid.user}): Returning to depot. Battery: {self.agent.battery:.1f}%")
            # Simulate movement
            await asyncio.sleep(5)
            self.agent.battery -= 2.5
            self.agent.current_location = WAREHOUSE_LOCATION
            self.agent.is_busy = False
            print(f"🏠 Courier ({self.agent.jid.user}): Arrived at depot.")
            self.set_next_state(STATE_IDLE)

    class ChargingState(State):
        """
        Courier is charging its battery at the depot.
        """
        async def run(self):
            print(f"🔋 Courier ({self.agent.jid.user}): Battery low ({self.agent.battery:.1f}%). Charging...")
            while self.agent.battery < 99:
                await asyncio.sleep(2)
                self.agent.battery += 10
                print(f"⚡ Courier ({self.agent.jid.user}): Charging... {self.agent.battery:.1f}%")
            self.agent.battery = 100.0
            print(f"💯 Courier ({self.agent.jid.user}): Fully charged.")
            self.set_next_state(STATE_IDLE)

    class StatusUpdateBehaviour(PeriodicBehaviour):
        """
        Periodically sends its status (location, battery) to the Supervisor.
        """
        async def run(self):
            status_msg = Message(to=SUPERVISOR_JID)
            status_msg.set_metadata("performative", "inform")
            status_msg.set_metadata("type", "courier_status")
            status_msg.body = f"{self.agent.jid.user}|{self.agent.current_location}|{self.agent.battery:.1f}|{len(self.agent.parcels_to_deliver)}/{self.agent.capacity}|{self.agent.is_busy}"
            await self.send(status_msg)

    async def setup(self):
        print(f"🟢 CourierAgent ({str(self.jid)}) started.")
        fsm = self.DeliveryFSM()
        fsm.add_state(name=STATE_IDLE, state=self.IdleState(), initial=True)
        fsm.add_state(name=STATE_MOVING_TO_DESTINATION, state=self.MovingToDestinationState())
        fsm.add_state(name=STATE_MOVING_TO_DEPOT, state=self.MovingToDepotState())
        fsm.add_state(name=STATE_CHARGING, state=self.ChargingState())

        fsm.add_transition(source=STATE_IDLE, dest=STATE_IDLE)
        fsm.add_transition(source=STATE_IDLE, dest=STATE_MOVING_TO_DESTINATION)
        fsm.add_transition(source=STATE_IDLE, dest=STATE_CHARGING)
        fsm.add_transition(source=STATE_MOVING_TO_DESTINATION, dest=STATE_MOVING_TO_DEPOT)
        fsm.add_transition(source=STATE_MOVING_TO_DEPOT, dest=STATE_IDLE)
        fsm.add_transition(source=STATE_CHARGING, dest=STATE_IDLE)
        self.add_behaviour(fsm)
        self.add_behaviour(self.StatusUpdateBehaviour(period=10))