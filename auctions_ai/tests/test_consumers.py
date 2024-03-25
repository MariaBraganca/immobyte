import pytest
import pytest_asyncio

from channels.testing import WebsocketCommunicator
from unittest.mock import AsyncMock, patch

from auctions_ai.consumers import ChatConsumer


@pytest_asyncio.fixture
async def chat_communicator():
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/testws/")
    communicator.scope["user"] = AsyncMock(id=1, is_authenticated=True)

    await communicator.connect()

    yield communicator

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_receive_echoes_messages(chat_communicator):
    with patch(
        "auctions_ai.consumers.AssistedUserChat.create", new_callable=AsyncMock
    ) as mock_chat:
        mock_chat.return_value = AsyncMock(call=AsyncMock(return_value="bar"))

        await chat_communicator.send_json_to({"message": "foo"})

        response_user = await chat_communicator.receive_json_from()
        assert response_user == {"message": "foo", "sender": "Du"}

        response_assistant = await chat_communicator.receive_json_from()
        assert response_assistant == {"message": "bar", "sender": "Immobyte-GPT"}


# TODO's:
# add Test class
# add parametrize()
# add tests for other methods
