import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
import time  # <-- ADDED IMPORT

st.set_page_config(layout="wide")
st.title("📦 Real-Time Delivery System Dashboard")


# --- Data Loading Functions ---

@st.cache_data(ttl=5)
def load_data_from_db():
    """Connects to the SQLite DB and loads parcel data."""
    try:
        conn = sqlite3.connect('courier_system.db')
        # Join parcels with their latest delivery status/timestamp
        query = """
                SELECT p.id, \
                       p.urgency, \
                       p.status, \
                       p.info, \
                       p.created_at, \
                       p.updated_at
                FROM parcels p \
                """
        df = pd.read_sql_query(query, conn, parse_dates=['created_at', 'updated_at'])
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=5)
def load_live_courier_status():
    """Loads the live status of all couriers."""
    try:
        return pd.read_csv("courier_status.csv").drop_duplicates(subset='jid', keep='last')
    except Exception:
        return pd.DataFrame(columns=["jid", "location", "battery", "load", "is_busy", "last_updated"])


@st.cache_data(ttl=5)
def load_comm_log():
    """Loads the agent communication log."""
    try:
        return pd.read_csv("agent_comm_log.csv", names=["time", "sender", "receiver", "msg_type", "content"])
    except Exception:
        return pd.DataFrame()


# Load all data
parcels_df = load_data_from_db()
couriers_df = load_live_courier_status()
comm_df = load_comm_log()

# --- Main Layout ---
if parcels_df.empty and couriers_df.empty:
    st.warning("Waiting for agent data... Please start the multi-agent system.")
    st.stop()

tabs = st.tabs([
    "📈 Overview",
    "🚚 Live Courier Status",
    "📄 Parcel Details",
    "🌐 Network Analysis"
])

# =======================
#      OVERVIEW TAB
# =======================
with tabs[0]:
    st.header("System-Wide Overview")

    # KPIs
    total_parcels = len(parcels_df)
    delivered_count = parcels_df['status'].eq('DELIVERED').sum()
    pending_count = parcels_df['status'].eq('PENDING').sum()

    # Calculate delivery time for delivered parcels
    if delivered_count > 0 and 'updated_at' in parcels_df.columns and 'created_at' in parcels_df.columns:
        parcels_df['delivery_duration'] = (pd.to_datetime(parcels_df['updated_at']) - pd.to_datetime(parcels_df['created_at'])).dt.total_seconds()
        avg_delivery_time = parcels_df[parcels_df['status'] == 'DELIVERED']['delivery_duration'].mean()
    else:
        avg_delivery_time = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Parcels Created", f"{total_parcels}")
    col2.metric("Parcels Delivered", f"{delivered_count}")
    col3.metric("Parcels Pending", f"{pending_count}")
    col4.metric("Avg. Delivery Time (s)", f"{avg_delivery_time:.2f}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Parcel Status Distribution")
        if not parcels_df.empty:
            status_counts = parcels_df['status'].value_counts()
            fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, hole=.3)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Parcels by Urgency")
        if not parcels_df.empty:
            urgency_counts = parcels_df['urgency'].value_counts()
            fig = px.bar(urgency_counts, x=urgency_counts.index, y=urgency_counts.values,
                         labels={'x': 'Urgency Level', 'y': 'Number of Parcels'}, color=urgency_counts.index)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Raw Parcel Data from Database")
    st.dataframe(parcels_df)

# =======================
#  LIVE COURIER STATUS TAB
# =======================
with tabs[1]:
    st.header("Live Courier Status")

    # This dictionary maps the location names from your GIS agent to coordinates
    location_coords = {
        "Warehouse": (45.7489, 21.2087),
        "Piata Unirii": (45.7573, 21.2291),
        "Piata Victoriei": (45.7533, 21.2255),
        "Iulius Town": (45.7651, 21.2384),
    }

    # Prepare data for map
    if not couriers_df.empty:
        couriers_df['lat'] = couriers_df['location'].map(lambda x: location_coords.get(x, (None, None))[0])
        couriers_df['lon'] = couriers_df['location'].map(lambda x: location_coords.get(x, (None, None))[1])
        st.map(couriers_df.dropna(subset=['lat', 'lon']))

    st.divider()

    if not couriers_df.empty:
        for index, row in couriers_df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.subheader(f"Courier: `{row['jid'].split('@')[0]}`")
                col1.write(f"**Location:** {row['location']}")
                col1.write(f"**Status:** {'Busy' if row['is_busy'] else 'Idle'}")
                col1.caption(f"Last updated: {row['last_updated']}")

                col2.metric("Battery", f"{row['battery']}%")
                st.progress(int(row['battery']))

                load_val, load_max = map(int, row['load'].split('/'))
                col3.metric("Load", f"{load_val}/{load_max}")
                st.progress(load_val / load_max)
    else:
        st.info("No live courier status data available yet.")

# =======================
#    PARCEL DETAILS TAB
# =======================
with tabs[2]:
    st.header("Individual Parcel Details")

    if not parcels_df.empty:
        parcel_id_list = parcels_df['id'].unique().tolist()
        selected_parcel = st.selectbox("Select a Parcel ID", parcel_id_list)

        if selected_parcel:
            parcel_data = parcels_df[parcels_df['id'] == selected_parcel].iloc[0]
            st.subheader(f"Details for Parcel `{selected_parcel}`")
            st.json(parcel_data.to_dict())

            st.subheader("Parcel Timeline (Gantt Chart)")
            gantt_df = parcels_df.dropna(subset=["created_at", "updated_at"])
            gantt_df = gantt_df[gantt_df['status'] == 'DELIVERED']

            if not gantt_df.empty:
                fig = px.timeline(
                    gantt_df,
                    x_start="created_at",
                    x_end="updated_at",
                    y="id",
                    color="urgency",
                    hover_data=["info"]
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No delivered parcels with start/end times to display.")
    else:
        st.info("No parcel data available.")

# =======================
#   NETWORK ANALYSIS TAB
# =======================
with tabs[3]:
    st.header("Agent Communication Network")

    if not comm_df.empty:
        G = nx.from_pandas_edgelist(comm_df, 'sender', 'receiver', create_using=nx.DiGraph())

        # Calculate node sizes based on activity (in-degree + out-degree)
        degrees = {node: val for node, val in G.degree()}
        nx.set_node_attributes(G, degrees, 'size')
        node_sizes = [d * 100 + 500 for d in degrees.values()]  # Scale sizes for visibility

        fig, ax = plt.subplots(figsize=(10, 8))
        pos = nx.spring_layout(G, k=0.9, iterations=50)
        nx.draw_networkx(
            G,
            pos,
            ax=ax,
            with_labels=True,
            node_size=node_sizes,
            node_color='skyblue',
            edge_color='gray',
            font_size=10,
            width=1.5,
            arrowsize=20
        )
        ax.set_title("Agent Communication Flow")
        st.pyplot(fig)

        st.subheader("Raw Communication Log")
        st.dataframe(comm_df)
    else:
        st.info("No agent communication log found.")

# --- Auto-refresh logic ---
# FIX: Replaced st.experimental_rerun() with the modern st.rerun()
st.caption("Auto-refreshing in 10 seconds...")
time.sleep(10)
st.rerun()