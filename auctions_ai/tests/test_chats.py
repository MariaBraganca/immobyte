import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from auctions_ai.chats import AssistedUserChat

# TODO's:
# The suite would benefit from:
# additional tests for edge cases or error handling
# separation between testing the functionality of the chat system and the integration with the OpenAI API

# Fixtures
# -----------------------------------------------------------------------------------------------
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

@pytest_asyncio.fixture
async def assisted_user_chat():
    return await AssistedUserChat.create(100)


# Assisted User Chat Functionality
# -----------------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_assisted_user_chat(patched_openai, assisted_user_chat):
    """Tests the initialization of an assisted user chat object."""
    assert isinstance(assisted_user_chat, AssistedUserChat)
    assert assisted_user_chat.user_id == 100

    patched_openai.beta.assistants.create.assert_awaited_once()
    patched_openai.beta.threads.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_call_assister_user_chat(patched_openai, assisted_user_chat):
    """Tests the assistant's response to a user message."""
    response = await assisted_user_chat.call('foo')

    assert response == 'bar'

    patched_openai.beta.threads.messages.create.assert_awaited_once()
    patched_openai.beta.threads.runs.create.assert_awaited_once()
    patched_openai.beta.threads.runs.retrieve.assert_awaited_once()
    patched_openai.beta.threads.messages.list.assert_awaited_once()

@pytest.mark.asyncio
async def test_process_assistant_response(patched_openai, assisted_user_chat):
    """Tests if the assistant's reponse has been processed."""
    processed_response = await assisted_user_chat.process_assistant_response()

    assert processed_response == True

    patched_openai.beta.threads.runs.create.assert_awaited_once()
    patched_openai.beta.threads.runs.retrieve.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_status_completed(patched_openai, assisted_user_chat):
    "Tests if the run went into completed status."
    status_completed = await assisted_user_chat.check_status_completed(3)

    assert status_completed == True

    patched_openai.beta.threads.runs.retrieve.assert_awaited_once()

@pytest.mark.asyncio
async def test_parse_assistant_response(patched_openai, assisted_user_chat):
    "Tests if the response is parsed as expected."
    parsed_response = await assisted_user_chat.parse_assistant_response()

    assert parsed_response == 'bar'

    patched_openai.beta.threads.messages.list.assert_awaited_once()


# OpenAI API Interactions
# -----------------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_add_user_message(patched_openai, assisted_user_chat):
    """Tests how to add messages to a thread."""
    content = 'test_user_message'

    await assisted_user_chat.add_user_message(content)

    patched_openai.beta.threads.messages.create.assert_awaited_once_with(
        thread_id = 2,
        role ='user',
        content = content
    )

@pytest.mark.asyncio
async def test_run_assistant(patched_openai, assisted_user_chat):
    """Tests how to create a run in a thread."""
    await assisted_user_chat.run_assistant()

    patched_openai.beta.threads.runs.create.assert_awaited_once_with(
        thread_id = 2,
        assistant_id = 1
    )

@pytest.mark.asyncio
async def test_retrieve_assistant(patched_openai, assisted_user_chat):
    """Tests how to get a run from a thread."""
    run = await assisted_user_chat.run_assistant()
    run_id = run.id

    await assisted_user_chat.retrieve_assistant(run_id)

    patched_openai.beta.threads.runs.retrieve.assert_awaited_once_with(
        thread_id = 2,
        run_id = 3
    )

@pytest.mark.asyncio
async def test_read_thread_messages(patched_openai, assisted_user_chat):
    """Tests how to get all messages in a thread."""
    await assisted_user_chat.read_thread_messages()

    patched_openai.beta.threads.messages.list.assert_awaited_once_with(
        thread_id = 2
    )
