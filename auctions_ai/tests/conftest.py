import pytest
import pytest_asyncio

from unittest.mock import AsyncMock, MagicMock, patch
from auctions_ai.chats import AssistedUserChat
from auctions_ai.tests.factories import UserFactory
from asgiref.sync import sync_to_async


# Fixtures
# -----------------------------------------------------------------------------------------------
@pytest.fixture
def patched_openai():
    with patch("auctions_ai.chats.AsyncOpenAI", AsyncMock) as mock_openai:
        mock_openai.beta = MagicMock(
            assistants=MagicMock(create=AsyncMock()),
            threads=MagicMock(
                create=AsyncMock(),
                messages=MagicMock(create=AsyncMock(), list=AsyncMock()),
                runs=MagicMock(create=AsyncMock(), retrieve=AsyncMock()),
            ),
        )

        yield mock_openai


@pytest_asyncio.fixture
async def assisted_user_chat(db, patched_openai):
    patched_openai.beta.assistants.create.return_value = MagicMock(id=1)
    patched_openai.beta.threads.create.return_value = MagicMock(id=2)

    test_user = await sync_to_async(UserFactory)()
    return await AssistedUserChat.create(test_user.id)
