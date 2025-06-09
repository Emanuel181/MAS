from agents.customer_agent import CustomerAgent
from agents.warehouse_agent import WarehouseAgent
from agents.courier_agent import CourierAgent
from config import *
import asyncio
from agents.traffic_agent import TrafficAgent
from agents.supervisor_agent import SupervisorAgent

NUM_CUSTOMERS = 11  # Set this to however many customers you want

async def main():
    print("🟢 Starting main()...")

    warehouse = WarehouseAgent(WAREHOUSE_JID, WAREHOUSE_PASS)
    traffic = TrafficAgent(TRAFFIC_JID, TRAFFIC_PASS)
    supervisor = SupervisorAgent(SUPERVISOR_JID, SUPERVISOR_PASS)

    # Start warehouse, traffic, supervisor first
    await warehouse.start(auto_register=True)
    await traffic.start(auto_register=True)
    await supervisor.start(auto_register=True)

    # Start all courier agents from COURIERS dict
    courier_agents = []
    for jid, password in COURIERS.items():
        courier_agent = CourierAgent(jid, password)
        await courier_agent.start(auto_register=True)
        courier_agents.append(courier_agent)

    # --- START MULTIPLE CUSTOMER AGENTS ---
    customer_agents = []
    for i in range(NUM_CUSTOMERS):
        jid = f"customer{i+1}@localhost"
        password = "customerpass"  # Or make unique, if needed
        customer = CustomerAgent(jid, password)
        await customer.start(auto_register=True)
        customer_agents.append(customer)

    print("✅ All agents are running...")

    await asyncio.sleep(30)

    # Shutdown: stop customers
    for customer in customer_agents:
        await customer.stop()
    await warehouse.stop()
    for agent in courier_agents:
        await agent.stop()
    await traffic.stop()
    await supervisor.stop()

    print("🛑 Simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
