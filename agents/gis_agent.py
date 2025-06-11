# agents/gis_agent.py

import random
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

# In a real system, this would use a mapping API like Google Maps or OSM
LOCATIONS = {
    "Warehouse": (45.7489, 21.2087),
    "Piata Unirii": (45.7573, 21.2291),
    "Piata Victoriei": (45.7533, 21.2255),
    "Iulius Town": (45.7651, 21.2384),
}

class GISAgent(Agent):
    """
    Geographic Information System Agent.
    Provides routing and simulates traffic conditions.
    """

    class RouteRequestHandler(CyclicBehaviour):
        def haversine(self, coord1, coord2):
            # Simple distance calculation, not used for routing logic here
            # but good for realism.
            import math
            R = 6371  # Earth radius in kilometers
            lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
            lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c
            return distance

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("type") == "route_request":
                start_loc_name, end_loc_name = msg.body.split('|')
                print(f"🗺️ GIS Agent: Received route request from {start_loc_name} to {end_loc_name}.")

                # Simulate creating a route (list of coordinates/waypoints)
                # This is a simplified mock route. A real implementation would
                # return a list of GPS coordinates for the path.
                route = [start_loc_name, f"waypoint_{random.randint(1,3)}", end_loc_name]

                # Simulate traffic by adding a random delay factor
                traffic_factor = random.uniform(1.0, 1.5) # 1.0 = no traffic, 1.5 = heavy traffic

                response = Message(to=str(msg.sender))
                response.thread = msg.thread
                response.set_metadata("performative", "inform")
                response.set_metadata("type", "route_response")
                response.body = f"{route}" # Sending the list as a string
                await self.send(response)
                print(f"🧭 GIS Agent: Sent route for {start_loc_name} -> {end_loc_name}.")

    async def setup(self):
        print(f"🟢 GISAgent ({str(self.jid)}) started.")
        template = Template()
        template.set_metadata("performative", "request")
        template.set_metadata("type", "route_request")
        self.add_behaviour(self.RouteRequestHandler(), template)