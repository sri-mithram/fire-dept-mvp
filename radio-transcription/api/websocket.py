"""
WebSocket handlers for real-time streaming to frontend

"""



from fastapi import WebSocket, WebSocketDisconnect

from typing import Set, Dict

import asyncio

import json

from datetime import datetime



from utils.logger import log

from api.models import WebSocketMessage





class ConnectionManager:

    """Manages WebSocket connections"""

    

    def __init__(self):

        self.active_connections: Set[WebSocket] = set()

        self.connection_metadata: Dict[WebSocket, Dict] = {}

    

    async def connect(self, websocket: WebSocket, client_id: str = None):

        """Accept new WebSocket connection"""

        await websocket.accept()

        self.active_connections.add(websocket)

        

        self.connection_metadata[websocket] = {

            "client_id": client_id,

            "connected_at": datetime.now(),

            "messages_sent": 0

        }

        

        log.info(f"WebSocket client connected: {client_id or 'unknown'} (total: {len(self.active_connections)})")

        

        # Send welcome message

        await self.send_personal_message({

            "type": "connected",

            "data": {"message": "Connected to radio transcription backend"},

            "timestamp": datetime.now().isoformat()

        }, websocket)

    

    def disconnect(self, websocket: WebSocket):

        """Remove WebSocket connection"""

        if websocket in self.active_connections:

            self.active_connections.remove(websocket)

            

            client_id = self.connection_metadata.get(websocket, {}).get("client_id", "unknown")

            log.info(f"WebSocket client disconnected: {client_id} (remaining: {len(self.active_connections)})")

            

            if websocket in self.connection_metadata:

                del self.connection_metadata[websocket]

    

    async def send_personal_message(self, message: dict, websocket: WebSocket):

        """Send message to specific client"""

        try:

            await websocket.send_json(message)

            

            if websocket in self.connection_metadata:

                self.connection_metadata[websocket]["messages_sent"] += 1

                

        except Exception as e:

            log.error(f"Error sending message to client: {str(e)}")

            self.disconnect(websocket)

    

    async def broadcast(self, message: dict):

        """Broadcast message to all connected clients"""

        

        if not self.active_connections:

            return

        

        # Add timestamp if not present

        if "timestamp" not in message:

            message["timestamp"] = datetime.now().isoformat()

        

        # Send to all clients

        disconnected = []

        for websocket in self.active_connections:

            try:

                await websocket.send_json(message)

                

                if websocket in self.connection_metadata:

                    self.connection_metadata[websocket]["messages_sent"] += 1

                    

            except Exception as e:

                log.error(f"Error broadcasting to client: {str(e)}")

                disconnected.append(websocket)

        

        # Clean up disconnected clients

        for websocket in disconnected:

            self.disconnect(websocket)

    

    async def broadcast_transcript(self, transcript: dict):

        """Broadcast new transcript to all clients"""

        message = {

            "type": "transcript",

            "data": transcript

        }

        await self.broadcast(message)

    

    async def broadcast_alert(self, alert: dict):

        """Broadcast alert to all clients"""

        message = {

            "type": "alert",

            "data": alert

        }

        await self.broadcast(message)

        

        log.warning(f"Alert broadcasted: {alert.get('text', '')}")

    

    async def broadcast_status(self, status: dict):

        """Broadcast system status to all clients"""

        message = {

            "type": "status",

            "data": status

        }

        await self.broadcast(message)

    

    def get_connection_count(self) -> int:

        """Get number of active connections"""

        return len(self.active_connections)

    

    def get_connection_stats(self) -> Dict:

        """Get statistics about connections"""

        return {

            "active_connections": len(self.active_connections),

            "total_messages_sent": sum(

                meta["messages_sent"] 

                for meta in self.connection_metadata.values()

            )

        }





# Global connection manager instance

manager = ConnectionManager()





async def websocket_endpoint(websocket: WebSocket):

    """WebSocket endpoint handler"""

    

    client_id = websocket.query_params.get("client_id", "unknown")

    

    try:

        await manager.connect(websocket, client_id)

        

        # Keep connection alive and handle incoming messages

        while True:

            try:

                # Receive message from client

                data = await websocket.receive_json()

                

                # Handle different message types

                msg_type = data.get("type")

                

                if msg_type == "ping":

                    # Respond to ping

                    await manager.send_personal_message({

                        "type": "pong",

                        "timestamp": datetime.now().isoformat()

                    }, websocket)

                

                elif msg_type == "get_status":

                    # Client requesting status (implement in routes)

                    pass

                

                else:

                    log.debug(f"Received message from {client_id}: {msg_type}")

                    

            except WebSocketDisconnect:

                break

            except Exception as e:

                log.error(f"Error handling WebSocket message: {str(e)}")

                break

    

    except Exception as e:

        log.error(f"WebSocket error: {str(e)}")

    

    finally:

        manager.disconnect(websocket)

