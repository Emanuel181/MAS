import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
import random
import string
import json
import streamlit.components.v1 as components

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Real-Time Courier Dashboard",
    layout="wide",
    page_icon="📦"
)
st.title("📦 Real-Time Delivery System Dashboard")
st.caption(
    "Full monitoring & control for your SPADE-based multi-agent delivery system. | Advanced dashboard (Streamlit, Plotly, Mapbox)")

# ========== CONSTANTS AND TEMPLATES ==========
MAPBOX_API_TOKEN = "pk.eyJ1IjoiZW1hMTIxIiwiYSI6ImNtYmMycms1djE3azcybHF1d3pvMzM2NHQifQ.1kkI3Uwn4zAER6PYWpMknQ"
MAPBOX_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Real-Time Courier Map</title>
<meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no" />
<script src="https://api.mapbox.com/mapbox-gl-js/v3.4.0/mapbox-gl.js"></script>
<link href="https://api.mapbox.com/mapbox-gl-js/v3.4.0/mapbox-gl.css" rel="stylesheet" />
<style>
    body {{ margin: 0; padding: 0; }}
    #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
    .mapboxgl-popup-content {{
        background-color: #333;
        color: #fff;
        border-radius: 5px;
        padding: 10px;
        font-family: sans-serif;
    }}
</style>
</head>
<body>
<div id="map"></div>
<script>
    mapboxgl.accessToken = '{mapbox_token}';
    const courierData = {courier_json};
    const parcelData = {parcel_json};
    const viewState = {view_state_json};

    const map = new mapboxgl.Map({{
        container: 'map',
        style: 'mapbox://styles/mapbox/standard',
        center: [viewState.longitude, viewState.latitude],
        zoom: viewState.zoom,
        pitch: viewState.pitch,
        bearing: viewState.bearing,
        antialias: true
    }});

    map.on('load', () => {{
    
        map.setConfigProperty('basemap', 'lightPreset', 'day');
        map.addSource('couriers', {{'type': 'geojson', 'data': courierData}});
        
        map.addLayer({{
            'id': 'courier-layer-3d', 'type': 'fill-extrusion', 'source': 'couriers',
            'paint': {{
                'fill-extrusion-color': ['case', ['==', ['get', 'is_busy'], true], '#FF4136', '#2ECC40'],
                'fill-extrusion-height': ['*', ['get', 'battery'], 3],
                'fill-extrusion-base': 0, 'fill-extrusion-opacity': 0.85
            }}
        }});
        map.addSource('parcels', {{'type': 'geojson', 'data': parcelData}});
        map.addLayer({{
            'id': 'parcel-layer-3d', 'type': 'fill-extrusion', 'source': 'parcels',
            'paint': {{
                'fill-extrusion-color': '#0074D9', 'fill-extrusion-height': ['get', 'elevation'],
                'fill-extrusion-base': 0, 'fill-extrusion-opacity': 0.85
            }}
        }});

        const popup = new mapboxgl.Popup({{closeButton: false, closeOnClick: false}});
        const showPopup = (e) => {{
            map.getCanvas().style.cursor = 'pointer';
            const feature = e.features[0];
            const coordinates = feature.geometry.coordinates[0][0]; // Adjusted for polygon
            const props = feature.properties;
            let description = '';
            if (props.name) {{
                description = `<strong>Courier:</strong> ${{props.name}}<br><strong>Status:</strong> ${{props.is_busy ? 'Busy' : 'Idle'}}<br><strong>Battery:</strong> ${{props.battery}}%`;
            }} else {{
                description = `<strong>Parcel ID:</strong> ${{props.id}}<br><strong>Destination:</strong> ${{props.info}}<br><strong>Urgency:</strong> ${{props.urgency}}`;
            }}
            popup.setLngLat(coordinates).setHTML(description).addTo(map);
        }};
        const hidePopup = () => {{ map.getCanvas().style.cursor = ''; popup.remove(); }};
        map.on('mouseenter', 'courier-layer-3d', showPopup);
        map.on('mouseleave', 'courier-layer-3d', hidePopup);
        map.on('mouseenter', 'parcel-layer-3d', showPopup);
        map.on('mouseleave', 'parcel-layer-3d', hidePopup);
    }});
</script>
</body>
</html>
"""

# ========== LOCATION COORDINATES MAP ==========
location_coords = {
    "Warehouse": (45.7489, 21.2087),
    "Piata Unirii": (45.7573, 21.2291),
    "Piata Victoriei": (45.7533, 21.2255),
    "Iulius Town": (45.7651, 21.2384),
    "Circumvalatiunii": (45.7711, 21.2172),
    "Gara Nord": (45.7542, 21.2080),
    "Modern": (45.7591, 21.2411),
    "Soarelui": (45.7354, 21.2465)
}

# ========== SIDEBAR: NAVIGATION, FILTERS, DEMO ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/891/891462.png", width=70)
    st.markdown("## Dashboard Navigation")
    selected_tab = st.selectbox(
        "Choose Section",
        [
            "📊 Overview & Insights",
            "🚚 Courier Map & Insights",
            "📦 Parcel Analytics",
            "🔗 Agent Network"
        ]
    )

    st.divider()
    st.markdown("## Filters & Controls")


    # -- Demo action: generate and insert random parcel into DB --
    def insert_random_parcel():
        urgency_choices = ["low", "medium", "high"]
        status_choices = ["PENDING", "DELIVERED", "IN_TRANSIT"]
        dest_choices = list(location_coords.keys())
        pid = "P" + ''.join(random.choices(string.digits, k=5))
        urgency = random.choice(urgency_choices)
        status = random.choice(status_choices)
        info = random.choice(dest_choices)
        now = datetime.now()
        created_at = now - timedelta(minutes=random.randint(0, 180))
        updated_at = created_at + timedelta(minutes=random.randint(0, 120))
        if status == "PENDING":
            updated_at = created_at
        try:
            conn = sqlite3.connect('courier_system.db')
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO parcels (id, urgency, status, info, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (pid, urgency, status, info, created_at, updated_at)
            )
            conn.commit()
            conn.close()
            return True, pid
        except Exception as e:
            return False, str(e)


    if st.button("🎲 Generate Random Parcel (DEMO)"):
        ok, msg = insert_random_parcel()
        if ok:
            st.success(f"Random parcel `{msg}` inserted in DB! Refreshing...")
            st.cache_data.clear()  # Clear all caches
            time.sleep(1)
            st.rerun()
        else:
            st.error("Failed to insert parcel: " + msg)

    if st.button("🔄 Refresh All Data"):
        st.cache_data.clear()  # Clear all caches
        st.rerun()


    # --- Load and cache data (live) ---
    @st.cache_data(ttl=10)  # Cache parcel data for 10 seconds
    def load_data_from_db():
        try:
            conn = sqlite3.connect('courier_system.db')
            df = pd.read_sql_query("SELECT * FROM parcels", conn, parse_dates=['created_at', 'updated_at'])
            conn.close()
            return df
        except Exception:
            return pd.DataFrame()


    parcels_df = load_data_from_db()

    status_options = sorted(parcels_df["status"].unique()) if not parcels_df.empty else []
    urgency_options = sorted(parcels_df["urgency"].unique()) if not parcels_df.empty else []
    dest_options = sorted(parcels_df["info"].unique()) if not parcels_df.empty else []
    status_filter = st.multiselect("Parcel Status", status_options, default=status_options)
    urgency_filter = st.multiselect("Urgency Level", urgency_options, default=urgency_options)
    dest_filter = st.selectbox("Destination", ["All"] + dest_options)
    search_id = st.text_input("Search by Parcel ID or keyword").strip()

    st.caption("All filters above apply to all dashboard sections.")


# ========== DATA LOADING ==========

@st.cache_data(ttl=5)  # Cache courier data for 5 seconds for live updates
def load_live_courier_status():
    """Reads live courier data from the CSV file."""
    try:
        # Keep only the last reported status for each courier
        return pd.read_csv("courier_status.csv").drop_duplicates(subset='jid', keep='last')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Return an empty dataframe if the file doesn't exist yet
        return pd.DataFrame(columns=["jid", "lat", "lon", "battery", "load", "is_busy", "last_updated"])


@st.cache_data(ttl=10)  # Cache communication log for 10 seconds
def load_comm_log():
    try:
        return pd.read_csv("agent_comm_log.csv", names=["time", "sender", "receiver", "msg_type", "content"])
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()


# --- Call the data loading functions ---
couriers_df = load_live_courier_status()
comm_df = load_comm_log()

# ===== FIX: convert lat/lon to numeric (drop all bad/corrupt rows) =====
if not couriers_df.empty:
    couriers_df["lat"] = pd.to_numeric(couriers_df["lat"], errors="coerce")
    couriers_df["lon"] = pd.to_numeric(couriers_df["lon"], errors="coerce")
    couriers_df = couriers_df.dropna(subset=["lat", "lon"])

# ========== GLOBAL FILTERED PARCEL DATA ==========
filtered_df = parcels_df.copy()
if status_filter:
    filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
if urgency_filter:
    filtered_df = filtered_df[filtered_df["urgency"].isin(urgency_filter)]
if dest_filter != "All":
    filtered_df = filtered_df[filtered_df["info"] == dest_filter]
if search_id:
    search_lc = search_id.lower()
    filtered_df = filtered_df[
        filtered_df["id"].astype(str).str.lower().str.contains(search_lc) |
        filtered_df["info"].astype(str).str.lower().str.contains(search_lc)
        ]

# ========== DASHBOARD SECTIONS ==========
# 1. OVERVIEW TAB
if selected_tab == "📊 Overview & Insights":
    st.header("📊 System Overview & Advanced Insights")

    # KPIs
    total = len(filtered_df)
    delivered_count = filtered_df['status'].eq('DELIVERED').sum()
    pending = filtered_df['status'].eq('PENDING').sum()
    urgent_delivered = filtered_df.query('urgency == "high" and status == "DELIVERED"').shape[0]
    parcels_per_day = filtered_df.groupby(
        filtered_df['created_at'].dt.date).size().mean() if not filtered_df.empty else 0

    if "delivery_duration" not in filtered_df and "updated_at" in filtered_df and "created_at" in filtered_df:
        filtered_df["delivery_duration"] = (pd.to_datetime(filtered_df['updated_at']) - pd.to_datetime(
            filtered_df['created_at'])).dt.total_seconds()
    avg_time = filtered_df[filtered_df['status'] == 'DELIVERED'][
        'delivery_duration'].mean() if delivered_count > 0 and "delivery_duration" in filtered_df else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Parcels", total)
    col2.metric("Delivered", delivered_count)
    col3.metric("Pending", pending)
    col4.metric("Urgent Delivered", urgent_delivered)
    col5.metric("Parcels/day (avg)", f"{parcels_per_day:.2f}")

    st.divider()

    st.subheader("Parcel Status Distribution")
    if not filtered_df.empty:
        pie_data = filtered_df["status"].value_counts()
        fig = px.pie(values=pie_data.values, names=pie_data.index, hole=.4,
                     color_discrete_sequence=px.colors.qualitative.G10)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Animated Parcel Delivery Timeline")
    if not filtered_df.empty:
        time_data = filtered_df.copy()
        time_data['created_day'] = pd.to_datetime(time_data['created_at']).dt.strftime("%Y-%m-%d")
        time_agg = time_data.groupby(['created_day', 'status']).size().reset_index(name="count")
        if not time_agg.empty:
            fig = px.bar(
                time_agg, x="created_day", y="count", color="status",
                animation_frame="created_day", barmode="stack",
                range_y=[0, time_agg["count"].max() + 2]
            )
            fig.update_layout(xaxis_title="Date", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data to display in the timeline.")

    st.divider()
    st.subheader("Filtered Raw Parcel Data")
    st.dataframe(filtered_df)

# 2. COURIER MAP TAB - Real-time positions with Mapbox
elif selected_tab == "🚚 Courier Map & Insights":
    st.header("🗺️ Courier Map, Destinations & Real-Time Tracking (3D)")

    # The page will automatically rerun every 5s due to the cache on load_live_courier_status
    # This creates a soft auto-refresh effect for the map
    st.caption("ℹ️ Map and courier data auto-refreshes every 5 seconds.")


    def create_geojson_feature(lon, lat, properties):
        """Creates a GeoJSON feature (a small square polygon) for 3D extrusion."""
        size = 0.0001
        return {
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [[
                [lon - size, lat - size], [lon + size, lat - size],
                [lon + size, lat + size], [lon - size, lat + size],
                [lon - size, lat - size],
            ]]},
            "properties": properties
        }


    # --- Prepare Courier GeoJSON ---
    courier_features = []
    if not couriers_df.empty:
        for _, row in couriers_df.iterrows():
            props = {
                "name": row['jid'].split('@')[0],
                "is_busy": bool(row['is_busy']),
                "battery": int(row['battery'])
            }
            feature = create_geojson_feature(row['lon'], row['lat'], props)
            courier_features.append(feature)
    courier_geojson = {"type": "FeatureCollection", "features": courier_features}

    # --- Prepare Parcel GeoJSON ---
    parcel_features = []
    undelivered_parcels = filtered_df[filtered_df["status"] != "DELIVERED"]
    for _, row in undelivered_parcels.iterrows():
        coords = location_coords.get(row["info"])
        if coords:
            lat, lon = coords
            props = {"id": row['id'], "info": row['info'], "urgency": row['urgency'], "elevation": 100}
            feature = create_geojson_feature(lon, lat, props)
            parcel_features.append(feature)
    parcel_geojson = {"type": "FeatureCollection", "features": parcel_features}

    # --- Center map ---
    if not couriers_df.empty:
        center_lat, center_lon = couriers_df["lat"].mean(), couriers_df["lon"].mean()
    else:
        center_lat, center_lon = 45.7533, 21.2255  # Fallback to Timișoara center

    view_state = {"latitude": center_lat, "longitude": center_lon, "zoom": 13, "pitch": 50, "bearing": 0}

    # --- Render Map ---
    if MAPBOX_API_TOKEN and "pk." in MAPBOX_API_TOKEN:
        final_html = MAPBOX_HTML_TEMPLATE.format(
            mapbox_token=MAPBOX_API_TOKEN,
            courier_json=json.dumps(courier_geojson),
            parcel_json=json.dumps(parcel_geojson),
            view_state_json=json.dumps(view_state)
        )
        components.html(final_html, height=500)
    else:
        st.error("Mapbox API token is missing or invalid. Please add it to the script.")

    st.divider()
    st.subheader("Live Courier Cards")
    if not couriers_df.empty:
        for _, row in couriers_df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.markdown(f"### :truck: `{row['jid'].split('@')[0]}`")
                c1.markdown(
                    f"**Coords:** {row['lat']:.5f}, {row['lon']:.5f} | **Status:** {'Busy' if row['is_busy'] else 'Idle'}")
                c1.caption(f"Last updated: {row['last_updated']}")
                c2.metric("Battery", f"{row['battery']}%")
                st.progress(int(row['battery']))

                try:
                    load_val, load_max = map(int, str(row['load']).split('/'))
                    c3.metric("Load", f"{load_val}/{load_max}")
                    st.progress(load_val / load_max if load_max > 0 else 0)
                except (ValueError, ZeroDivisionError):
                    c3.metric("Load", str(row.get('load', 'N/A')))
                    st.progress(0)
    else:
        st.info("No courier status data available. Is `simulate_couriers.py` running?")

    st.divider()
    st.subheader("Leaderboard (by Battery, then Busy status)")
    if not couriers_df.empty:
        lb = couriers_df.sort_values(["battery", "is_busy"], ascending=[False, False])
        st.dataframe(
            lb[["jid", "battery", "load", "is_busy"]],
            use_container_width=True,
            column_config={
                "jid": st.column_config.TextColumn("Courier ID"),
                "battery": st.column_config.ProgressColumn("Battery (%)", min_value=0, max_value=100, format="%d%%"),
                "load": st.column_config.TextColumn("Load"),
                "is_busy": st.column_config.CheckboxColumn("Busy")
            }
        )

# 3. PARCEL ANALYTICS
elif selected_tab == "📦 Parcel Analytics":
    st.header("📦 Parcel Analytics & Timeline")
    if not filtered_df.empty:
        sel_id = st.selectbox("Select a Parcel", filtered_df['id'].unique())
        if sel_id:
            sel_row = filtered_df[filtered_df['id'] == sel_id].iloc[0]
            st.json(json.loads(sel_row.to_json(date_format='iso')))

        delivered = filtered_df.dropna(subset=["created_at", "updated_at"])
        delivered = delivered[delivered["status"] == "DELIVERED"].copy()
        if "delivery_duration" not in delivered:
            delivered["delivery_duration"] = (pd.to_datetime(delivered['updated_at']) - pd.to_datetime(
                delivered['created_at'])).dt.total_seconds()

        st.divider()
        st.subheader("Animated Delivery Timeline (Gantt)")
        if not delivered.empty:
            delivered_sorted = delivered.sort_values("created_at")
            fig = px.timeline(
                delivered_sorted, x_start="created_at", x_end="updated_at",
                y="id", color="urgency", hover_data=["info"]
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Delivery Duration by Urgency (Boxplot)")
            fig2 = px.box(delivered, x="urgency", y="delivery_duration", color="urgency", points="all")
            st.plotly_chart(fig2, use_container_width=True)

            if not delivered["delivery_duration"].empty:
                med = delivered["delivery_duration"].median()
                if med > 0:
                    outliers = delivered[delivered["delivery_duration"] > 3 * med]
                    if not outliers.empty:
                        st.warning(f"⚠️ Outlier deliveries detected: {len(outliers)}")
                        st.dataframe(outliers)
        else:
            st.info("No delivered parcels with complete timeline data.")
    else:
        st.warning("No parcel data available for analysis.")

# 4. AGENT NETWORK
elif selected_tab == "🔗 Agent Network":
    st.header("🔗 Agent Network, Centrality, and Communication Patterns")
    if not comm_df.empty:
        G = nx.from_pandas_edgelist(comm_df, 'sender', 'receiver', create_using=nx.DiGraph())
        if G.nodes():
            centrality = nx.degree_centrality(G)
            node_sizes = [centrality.get(n, 0) * 2500 + 500 for n in G.nodes()]
            fig, ax = plt.subplots(figsize=(12, 10))
            pos = nx.spring_layout(G, k=0.95, seed=42)
            nx.draw(
                G, pos, ax=ax, with_labels=True, node_size=node_sizes,
                node_color='deepskyblue', edge_color='gray', width=1.5,
                arrowsize=20, font_size=10,
                labels={node: node.split('@')[0] for node in G.nodes()}
            )
            ax.set_title("Agent Communication Flow (Node Size = Centrality)", size=16)
            st.pyplot(fig)

            st.subheader("Heatmap: Message Volume (Sender/Receiver)")
            pivot = comm_df.pivot_table(index="sender", columns="receiver", values="msg_type", aggfunc="count",
                                        fill_value=0)
            st.dataframe(pivot)

            st.subheader("Top Message Routes")
            route_stats = comm_df.groupby(['sender', 'receiver']).size().reset_index(name='count').sort_values("count",
                                                                                                               ascending=False)
            st.dataframe(route_stats.head(10))

            st.subheader("Raw Communication Log")
            st.dataframe(comm_df)
    else:
        st.warning("No agent communication log found (agent_comm_log.csv).")

# Trigger a rerun to refresh the data from cache
time.sleep(5)
try:
    st.rerun()
except st.errors.StreamlitAPIException as e:
    # This will happen if the user navigates away or closes the tab
    pass