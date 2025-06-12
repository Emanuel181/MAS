# 📦 MAS2: Real-Time Multi-Agent Courier Delivery System

A fully functional SPADE-based Multi-Agent System (MAS) that simulates parcel delivery using autonomous agents and visualizes courier activity and parcel analytics through a real-time dashboard.

---

## 🧠 System Overview

This system models a courier service with intelligent agents:

- 🧍 **CustomerAgent**: Creates parcel delivery requests and tracks them.
- 🏢 **WarehouseAgent**: Manages and prioritizes parcels, assigns couriers.
- 🚚 **CourierAgent**: Delivers parcels, manages battery and capacity.
- 🧠 **SupervisorAgent**: Monitors all couriers and optimizes assignments.
- 🗺️ **GISAgent**: Provides simulated routing and traffic responses.
- 🗃️ **DatabaseAgent**: Stores all parcel and delivery data using SQLite.
- 📊 **Dashboard**: Real-time web dashboard built with Streamlit + Plotly + Mapbox.
- 🛰️ **simulate_couriers.py**: Optional background script to feed live location updates.

---

## 📁 Project Structure

```bash
MAS2/
├── agents/                   # All SPADE agents
│   ├── courier_agent.py
│   ├── customer_agent.py
│   ├── database_agent.py
│   ├── gis_agent.py
│   ├── supervisor_agent.py
│   └── warehouse_agent.py
├── utils/
│   └── agent_comm_log.csv    # Communication logs (generated)
├── bike.png                  # Optional icon used in dashboard
├── courier_status.csv        # Courier status (generated or simulated)
├── courier_system.db         # SQLite DB (generated)
├── dasboard.py               # Streamlit dashboard
├── main.py                   # System launcher
├── settings.py               # Agent credentials and settings
├── simulate_couriers.py      # Optional courier movement simulation
├── .gitignore
└── README.md

⚙️ Requirements
Install the required packages:

pip install spade streamlit plotly pandas matplotlib
Also make sure a local XMPP server (e.g., ejabberd or Openfire) is running and agents are registered.

🚀 Getting Started
1. Configure settings.py
python
Copy
Edit
# settings.py
CUSTOMER_JID = "customer@localhost"
CUSTOMER_PASS = "customerpass"

WAREHOUSE_JID = "warehouse@localhost"
WAREHOUSE_PASS = "warehousepass"

SUPERVISOR_JID = "supervisor@localhost"
SUPERVISOR_PASS = "supervisorpass"

GIS_JID = "gis@localhost"
GIS_PASS = "gispass"

DATABASE_JID = "db@localhost"
DATABASE_PASS = "dbpass"

COURIERS = {
    "courier1@localhost": "courier1pass",
    "courier2@localhost": "courier2pass"
}

WAREHOUSE_LOCATION = "Warehouse"
2. Launch the Agent System
python main.py
This launches all agents: Database, GIS, Supervisor, Warehouse, Customer, and Couriers.

3. Start the Real-Time Dashboard
In a separate terminal:

streamlit run dasboard.py
Features:

📊 Parcel statistics & analytics

🗺️ 3D Mapbox courier tracking

🔗 Agent network graph & communication logs

4. (Optional) Simulate Courier Movement

Copy
Edit
python simulate_couriers.py
This script will update courier_status.csv to simulate GPS movement and battery changes in real time.

📸 Preview
A live 3D courier map, urgent delivery highlights, and message analytics dashboard.


📄 License
MIT License. Built for educational and research use.

✨ Acknowledgments
Developed using:

SPADE

Streamlit

Plotly

Mapbox