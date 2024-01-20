import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from auctions_ai.chats import AssistedUserChat

# TODO's:
# The suite would benefit from:
# additional tests for edge cases or error handling
# separation between testing the functionality of the chat system and the integration with the OpenAI API

@pytest.fixture
def patched_openai():
    with patch('auctions_ai.chats.AsyncOpenAI', AsyncMock) as mock_openai:
        mock_openai.beta = MagicMock(
            assistants = MagicMock(
                create = AsyncMock(return_value = MagicMock(id = 1))
            ),
            threads = MagicMock(
                create = AsyncMock(return_value = MagicMock(id = 2)),
                messages = MagicMock(
                    create = AsyncMock(),
                    list = AsyncMock(
                        return_value = MagicMock(data = [
                            MagicMock(content = [
                                MagicMock(text = MagicMock(value = 'bar'))
                            ])
                        ])
                    )
                ),
                runs = MagicMock(
                    create = AsyncMock(return_value = MagicMock(id = 3)),
                    retrieve = AsyncMock(return_value = MagicMock(status = 'completed'))
                )
            )
        )

        yield mock_openai

# Assisted User Chat Functionality
# -----------------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_assisted_user_chat(patched_openai):
    """Tests the initialization of an assisted user chat object."""
    assisted_user_chat = await AssistedUserChat.create(100)

    assert isinstance(assisted_user_chat, AssistedUserChat)
    assert assisted_user_chat.user_id == 100

    patched_openai.beta.assistants.create.assert_awaited_once()
    patched_openai.beta.threads.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_call_assister_user_chat(patched_openai):
    """Tests the assistant's response to a user message."""
    assisted_user_chat = await AssistedUserChat.create(100)
    response = await assisted_user_chat.call('foo')

    assert response == 'bar'

    patched_openai.beta.threads.messages.create.assert_awaited_once()
    patched_openai.beta.threads.runs.create.assert_awaited_once()
    patched_openai.beta.threads.runs.retrieve.assert_awaited_once()
    patched_openai.beta.threads.messages.list.assert_awaited_once()

# TODO's:
# add test for check_status_completed()
# add test for parse_assistant_response()
# add test for error handling


# OpenAI API Interactions
# -----------------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_add_user_message(patched_openai):
    """Tests how to add messages to a thread."""
    assisted_user_chat = await AssistedUserChat.create(100)
    content = 'test_user_message'

    await assisted_user_chat.add_user_message(content)

    patched_openai.beta.threads.messages.create.assert_awaited_once_with(
        thread_id = 2,
        role ='user',
        content = content
    )

@pytest.mark.asyncio
async def test_run_assistant(patched_openai):
    """Tests how to create a run in a thread."""
    assisted_user_chat = await AssistedUserChat.create(100)

    await assisted_user_chat.run_assistant()

    patched_openai.beta.threads.runs.create.assert_awaited_once_with(
        thread_id = 2,
        assistant_id = 1
    )

@pytest.mark.asyncio
async def test_retrieve_assistant(patched_openai):
    """Tests how to get a run from a thread."""
    assisted_user_chat = await AssistedUserChat.create(100)
    run = await assisted_user_chat.run_assistant()
    run_id = run.id

    await assisted_user_chat.retrieve_assistant(run_id)

    patched_openai.beta.threads.runs.retrieve.assert_awaited_once_with(
        thread_id = 2,
        run_id = 3
    )

@pytest.mark.asyncio
async def test_read_thread_messages(patched_openai):
    """Tests how to get all messages in a thread."""
    assisted_user_chat = await AssistedUserChat.create(1)

    await assisted_user_chat.read_thread_messages()

    patched_openai.beta.threads.messages.list.assert_awaited_once_with(
        thread_id = 2
    )

# TODO's:
# add test for API error handling
