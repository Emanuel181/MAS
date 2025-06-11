# main.py

import asyncio
from settings import *

# Import the new, updated agent classes
from agents.customer_agent import CustomerAgent
from agents.warehouse_agent import WarehouseAgent
from agents.courier_agent import CourierAgent
from agents.supervisor_agent import SupervisorAgent
from agents.gis_agent import GISAgent
from agents.database_agent import DatabaseAgent


async def main():
    """
    Sets up and runs the entire multi-agent system.
    """
    print("🟢 Starting the Multi-Agent Courier System...")

    # --- Agent Initialization ---
    # The order is important: start services (DB, GIS, Supervisor) first.

    # 1. Core Service Agents
    database = DatabaseAgent(DATABASE_JID, DATABASE_PASS)
    gis = GISAgent(GIS_JID, GIS_PASS)
    supervisor = SupervisorAgent(SUPERVISOR_JID, SUPERVISOR_PASS)

    # 2. Operational Agents
    warehouse = WarehouseAgent(WAREHOUSE_JID, WAREHOUSE_PASS)
    customer = CustomerAgent(CUSTOMER_JID, CUSTOMER_PASS)  # Using the single customer from settings

    # --- Start Agents ---
    await database.start(auto_register=True)
    await gis.start(auto_register=True)
    await supervisor.start(auto_register=True)
    await warehouse.start(auto_register=True)
    await customer.start(auto_register=True)

    # Start all courier agents defined in the COURIERS dictionary
    courier_agents = []
    for jid, password in COURIERS.items():
        courier_agent = CourierAgent(jid, password)
        await courier_agent.start(auto_register=True)
        courier_agents.append(courier_agent)
        print(f"🚚 Courier {jid} has started.")

    print("\n✅ All agents are running. Simulation will run for 60 seconds.")

    # Let the simulation run for a while
    await asyncio.sleep(60)

    # --- Shutdown Sequence ---
    print("\n🛑 Shutting down all agents...")

    # Stop agents in a logical order
    await customer.stop()
    await warehouse.stop()
    for agent in courier_agents:
        await agent.stop()
    await supervisor.stop()
    await gis.stop()
    await database.stop()

    print("\n🏁 Simulation complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down.")