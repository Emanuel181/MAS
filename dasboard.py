import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import time
import numpy as np

st.set_page_config(layout="wide")
st.title("Parcel Delivery Dashboard")

# -- Read Data --
@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(
            "delivery_log.csv",
            names=[
                "time", "courier", "parcel_id", "version", "parcel_info",
                "route", "count", "lat", "lon", "start_time", "end_time"
            ],
            parse_dates=["time", "start_time", "end_time"]
        )
        return df
    except Exception as e:
        st.warning(f"Waiting for data or error: {e}")
        return pd.DataFrame()

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
courier_opt = st.sidebar.selectbox("Courier", ["All"] + sorted(df["courier"].dropna().unique().tolist()))
route_opt = st.sidebar.selectbox("Route", ["All"] + sorted(df["route"].dropna().unique().tolist()))
date_opt = st.sidebar.date_input("Date", [])
if courier_opt != "All":
    df = df[df["courier"] == courier_opt]
if route_opt != "All":
    df = df[df["route"] == route_opt]
if date_opt and not df.empty:
    df = df[df["time"].dt.date.isin(date_opt if isinstance(date_opt, list) else [date_opt])]

# --- Tabs Layout ---
tabs = st.tabs([
    "Overview", "Map", "Heatmap", "Timelines", "Network", "Animation"
])

# ========== OVERVIEW ==========
with tabs[0]:
    st.subheader("Raw Delivery Log")
    st.dataframe(df)

    # Deliveries per minute (time series)
    st.subheader("Deliveries per Minute")
    fig1, ax1 = plt.subplots()
    if not df.empty:
        df.set_index('time')['courier'].resample('1T').count().plot(ax=ax1)
    ax1.set_ylabel("Number of Deliveries")
    ax1.set_xlabel("Time")
    st.pyplot(fig1)

    # Deliveries per courier (bar chart)
    st.subheader("Deliveries per Courier")
    fig2, ax2 = plt.subplots()
    if not df.empty:
        df['courier'].value_counts().plot(kind='bar', ax=ax2)
    ax2.set_ylabel("Number of Deliveries")
    ax2.set_xlabel("Courier")
    st.pyplot(fig2)

    # Deliveries per route (bar chart)
    st.subheader("Most Used Routes")
    fig3, ax3 = plt.subplots()
    if not df.empty:
        df['route'].value_counts().plot(kind='bar', ax=ax3)
    ax3.set_ylabel("Number of Deliveries")
    ax3.set_xlabel("Route")
    st.pyplot(fig3)

# ========== MAP ==========
with tabs[1]:
    st.subheader("Delivery Destinations Map")
    if "lat" in df and "lon" in df and not df.empty:
        st.map(df[["lat", "lon"]].dropna())
    else:
        st.info("No coordinates in data.")

# ========== HEATMAP ==========
with tabs[2]:
    st.subheader("Delivery Density Heatmap")
    if "lat" in df and "lon" in df and not df.empty:
        fig = px.density_mapbox(
            df, lat="lat", lon="lon",
            radius=10,
            center=dict(lat=45.753, lon=21.225),
            zoom=12,
            mapbox_style="open-street-map",
            title="Delivery Density"
        )
        st.plotly_chart(fig)
    else:
        st.info("No coordinates in data.")

# ========== TIMELINES ==========
with tabs[3]:
    st.subheader("Delivery Timeline (Gantt Chart)")
    # You must log start_time and end_time for this to work!
    if "start_time" in df and "end_time" in df and not df.empty and df['start_time'].notnull().any():
        gantt_df = df.dropna(subset=["start_time", "end_time"])
        fig = px.timeline(
            gantt_df, x_start="start_time", x_end="end_time",
            y="courier", color="parcel_id", hover_data=["parcel_info", "route"]
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig)
    else:
        st.info("No start/end time data for Gantt chart.")

# ========== NETWORK ==========
with tabs[4]:
    st.subheader("Agent Communication Network")
    # You need to log a separate file: agent_comm_log.csv
    try:
        comm_df = pd.read_csv("agent_comm_log.csv", names=["time", "sender", "receiver", "msg_type"])
        G = nx.DiGraph()
        for _, row in comm_df.iterrows():
            G.add_edge(row["sender"], row["receiver"])
        plt.figure(figsize=(8, 6))
        nx.draw_networkx(G, with_labels=True, node_color='lightblue', edge_color='gray')
        st.pyplot(plt)
    except Exception as e:
        st.info("No agent communication log found or error loading.")

# ========== ANIMATION ==========
with tabs[5]:
    st.subheader("Animated Delivery Replay")
    # For a true animation, you'll need to save stepwise delivery events (lat, lon, time)
    if "lat" in df and "lon" in df and not df.empty:
        coords = df[["lat", "lon"]].dropna().to_numpy()
        fig = go.Figure()
        for i in range(1, len(coords)+1):
            fig.add_trace(go.Scattermapbox(
                mode="lines+markers",
                lon=coords[:i,1], lat=coords[:i,0], marker={'size': 10},
                line=dict(width=2, color='blue'),
            ))
        fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=12, mapbox_center={"lat":45.753, "lon":21.225})
        st.plotly_chart(fig)
    else:
        st.info("No coordinates in data.")

# --- Auto-refresh ---
st.caption("Auto-refreshing every 10 seconds...")
time.sleep(10)
st.rerun()
