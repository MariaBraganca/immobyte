# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from auctions_ai.chats import AssistedUserChat

class ChatConsumer(AsyncWebsocketConsumer):
    """Attempt to structure code as a series of functions to be called whenever an event happens."""

    async def connect(self):
        """Accept connection call."""
        if self.scope["user"].is_authenticated:
            self.assisted_chat = await AssistedUserChat.create(self.scope['user'].id)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Close connection call."""
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        """Echo user's message."""
        await self.send(text_data=json.dumps({"message": message, "sender": 'user'}))

        """Echo assistant's message."""
        response = await self.process_message(message)
        await self.send(text_data=json.dumps({"message": response, "sender": 'assistant'}))

    async def process_message(self, message):
        """Process the message through AssistedUserChat."""
        return await self.assisted_chat.call(message)
