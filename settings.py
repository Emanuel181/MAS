# settings.py

# --- XMPP Server Configuration ---
XMPP_DOMAIN = "localhost"
# The address of your XMPP server. "127.0.0.1" is usually correct for a local server.
XMPP_SERVER = "127.0.0.1" 

# --- Agent Credentials ---

# Customer Agent
CUSTOMER_JID = f"customer@{XMPP_DOMAIN}"
CUSTOMER_PASS = "customerpass"

# Warehouse Agent
WAREHOUSE_JID = f"warehouse@{XMPP_DOMAIN}"
WAREHOUSE_PASS = "warehousepass"

# Supervisor Agent
SUPERVISOR_JID = f"supervisor@{XMPP_DOMAIN}"
SUPERVISOR_PASS = "supervisorpass"

# (NEW) GIS Agent - Replaces the old TrafficAgent
GIS_JID = f"gis@{XMPP_DOMAIN}"
GIS_PASS = "gispass"

# (NEW) Database Agent
DATABASE_JID = f"database@{XMPP_DOMAIN}"
DATABASE_PASS = "databasepass"

# Courier Agents - A dictionary to hold all courier credentials
COURIERS = {
    f"courier1@{XMPP_DOMAIN}": "courierpass1",
    f"courier2@{XMPP_DOMAIN}": "courierpass2",
    f"courier3@{XMPP_DOMAIN}": "courierpass3",
}

# --- Simulation Settings ---

# A fixed location name for the central depot/warehouse.
# This must match one of the keys in the LOCATIONS dictionary in gis_agent.py
WAREHOUSE_LOCATION = "Warehouse"