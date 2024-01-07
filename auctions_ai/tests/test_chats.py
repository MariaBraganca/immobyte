import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from auctions_ai.chats import AssistedUserChat

@pytest.mark.asyncio
async def test_create_assisted_user_chat():
    user_id = 1

    with patch('auctions_ai.chats.AsyncOpenAI', new = AsyncMock) as mock_openai:
        # Attaching Mocks as Attributes
        mock_beta = MagicMock()
        mock_assistants = MagicMock()
        mock_threads = MagicMock()

        mock_openai.beta = mock_beta
        mock_beta.assistants = mock_assistants
        mock_beta.threads = mock_threads

        mock_assistants.create = AsyncMock(return_value = 'mocked_assistant')
        mock_threads.create = AsyncMock(return_value = 'mocked_thread')

         # Create assisted user chat instance
        assisted_user_chat = await AssistedUserChat.create(user_id)

        assert isinstance(assisted_user_chat, AssistedUserChat)

        # Test returned values
        assert assisted_user_chat.assistant == 'mocked_assistant'
        assert assisted_user_chat.thread == 'mocked_thread'
        assert assisted_user_chat.user_id == user_id

        # Test async behaviour
        mock_openai.beta.assistants.create.assert_awaited_once()
        mock_openai.beta.threads.create.assert_awaited_once()
