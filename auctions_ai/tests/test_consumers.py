import pytest
from channels.testing import WebsocketCommunicator
from unittest.mock import AsyncMock, patch

from auctions_ai.consumers import ChatConsumer


@pytest.mark.asyncio
async def test_receive_echoes_messages():
    with patch(
        "auctions_ai.consumers.AssistedUserChat.create", new_callable=AsyncMock
    ) as mock_chat:
        mock_chat.return_value = AsyncMock(call=AsyncMock(return_value="bar"))

        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/testws/")
        communicator.scope["user"] = AsyncMock(id=1, is_authenticated=True)

        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({"message": "foo"})

        response_user = await communicator.receive_json_from()
        assert response_user == {"message": "foo", "sender": "Du", "avatar": "gray-300"}

        response_assistant = await communicator.receive_json_from()
        assert response_assistant == {
            "message": "bar",
            "sender": "Immobyte-GPT",
            "avatar": "sky-500",
        }

        await communicator.disconnect()
