# agents/database_agent.py

import sqlite3
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class DatabaseAgent(Agent):
    """
    A centralized agent for managing the system's database (parcels, deliveries).
    This provides a more robust alternative to scattered CSV files.
    """

    def setup_db(self):
        self.conn = sqlite3.connect('courier_system.db')
        self.cursor = self.conn.cursor()
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parcels (
                id TEXT PRIMARY KEY,
                urgency TEXT,
                status TEXT,
                info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS delivery_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                parcel_id TEXT,
                status TEXT,
                timestamp TEXT,
                FOREIGN KEY(parcel_id) REFERENCES parcels(id)
            )
        ''')
        self.conn.commit()

    class DatabaseHandler(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if not msg:
                return

            performative = msg.metadata.get("performative")
            msg_type = msg.metadata.get("type")

            if performative == "update":
                if msg_type == "parcel_log":
                    # For creating a new parcel entry
                    parcel_id, urgency, status, info = msg.body.split('|', 3)
                    self.agent.cursor.execute(
                        "INSERT INTO parcels (id, urgency, status, info) VALUES (?, ?, ?, ?)",
                        (parcel_id, urgency, status, info)
                    )
                    self.agent.conn.commit()
                elif msg_type == "delivery_log":
                    # For updating an existing parcel's status
                    parcel_id, status, timestamp = msg.body.split('|')
                    self.agent.cursor.execute(
                        "UPDATE parcels SET status = ?, updated_at = ? WHERE id = ?",
                        (status, timestamp, parcel_id)
                    )
                    self.agent.cursor.execute(
                        "INSERT INTO delivery_log (parcel_id, status, timestamp) VALUES (?, ?, ?)",
                        (parcel_id, status, timestamp)
                    )
                    self.agent.conn.commit()

            elif performative == "query":
                if msg_type == "parcel_info":
                    parcel_id = msg.body
                    self.agent.cursor.execute("SELECT id, status, info FROM parcels WHERE id = ?", (parcel_id,))
                    result = self.agent.cursor.fetchone()
                    response_body = "|".join(result) if result else f"{parcel_id}|NOT_FOUND|-"

                    response_msg = Message(to=str(msg.sender))
                    response_msg.thread = msg.thread
                    response_msg.set_metadata("performative", "inform")
                    response_msg.body = response_body
                    await self.send(response_msg)

    async def setup(self):
        print(f"🟢 DatabaseAgent ({str(self.jid)}) started.")
        self.setup_db()
        self.add_behaviour(self.DatabaseHandler())

    def on_end(self):
        self.conn.close()
        print("Database connection closed.")