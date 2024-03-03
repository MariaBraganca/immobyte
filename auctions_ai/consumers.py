# chat/consumers.py
import json
import logging

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from channels.generic.websocket import AsyncWebsocketConsumer
from auctions_ai.chats import AssistedUserChat

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """Simple websocket echo server."""

    USER = "Du"
    USER_COLOR = "gray-300"
    IMMOBYTE = "Immobyte-GPT"
    IMMOBYTE_COLOR = "sky-500"
    SYSTEM = "System"
    SYSTEM_COLOR = "black"

    INCOMING_MESSAGE_SCHEMA = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"],
    }

    async def connect(self):
        """Accepts and closes a connection depending on user authentication."""
        if self.scope["user"].is_authenticated:
            self.assisted_chat = await AssistedUserChat.create(self.scope["user"].id)
            await self.accept()
        else:
            await self.close(code=403)  # Forbidden

    async def receive(self, text_data):
        """Processes incoming messages and responds appropriately.

        Validates the incoming JSON, extracts the message, processes it,
        and sends a response. Notifies the sender of errors at each step.
        """
        # validates incoming json
        text_data_json = self.validate_json(text_data)
        if text_data_json is None:
            await self.notify_error("Unable to validate message. Please check format.")
            return

        # extracts and echoes user message
        user_message = text_data_json.get("message")
        await self.send_json(
            {"message": user_message, "sender": self.USER, "avatar": self.USER_COLOR}
        )

        # processes and validates assistant's response
        assistant_message = await self.process_message(user_message)
        if assistant_message is None:
            await self.notify_error(
                "Unable to process the message. Please try again later."
            )
            return

        # echoes assistant's message
        await self.send_json(
            {
                "message": assistant_message,
                "sender": self.IMMOBYTE,
                "avatar": self.IMMOBYTE_COLOR,
            }
        )

    def validate_json(self, text_data):
        """Performs basic JSON Validation"""
        try:
            data = json.loads(text_data)
            validate(instance=data, schema=self.INCOMING_MESSAGE_SCHEMA)
            return data
        except json.JSONDecodeError as error:
            logger.error(
                f"JSONDecode Error: {error}. Failed to decode JSON from incoming message: {text_data}"
            )
            return None
        except ValidationError as error:
            logger.error(
                f"ValidationError: {error}. Incoming message does not match schema: {text_data}"
            )
            return None

    # TODO's:
    # add retry logic
    # handle certain types of errors more gracefully.
    async def send_json(self, message_data):
        """Sends a JSON response with the given message, user, and color."""
        try:
            await self.send(text_data=json.dumps(message_data))
        except Exception as error:
            logger.exception(
                f"Unexpected {error=}, {type(error)=}. Failed to send message data: {message_data}.",
                exc_info=True,
            )
            self.close(
                code=1011
            )  # terminating the connection because of unexpected condition

    # TODO's:
    # Distinguish between different error types
    # OR provide more information about the failure to the caller
    async def process_message(self, message):
        """Process the message through AssistedUserChat."""
        try:
            return await self.assisted_chat.call(message)
        except Exception as error:
            logger.exception(
                f"Unexpected {error=}, {type(error)=}. Failed to process message: {message}",
                exc_info=True,
            )
            return None

    async def notify_error(self, error_message):
        """Echos back a user-friendly error message."""
        await self.send_json(
            {
                "message": f"Error: {error_message}.",
                "sender": self.SYSTEM,
                "avatar": self.SYSTEM_COLOR,
            }
        )
