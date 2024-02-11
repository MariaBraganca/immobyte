import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from auctions_ai.chats import AssistedUserChat

# Fixtures
# -----------------------------------------------------------------------------------------------
# NOTE:
# Setting fixture scope from function to module messes up with the await count assertions

@pytest.fixture
def patched_openai():
    with patch('auctions_ai.chats.AsyncOpenAI', AsyncMock) as mock_openai:
        mock_openai.beta = MagicMock(
            assistants = MagicMock(
                create = AsyncMock()
            ),
            threads = MagicMock(
                create = AsyncMock(),
                messages = MagicMock(
                    create = AsyncMock(),
                    list = AsyncMock()
                ),
                runs = MagicMock(
                    create = AsyncMock(),
                    retrieve = AsyncMock()
                )
            )
        )

        yield mock_openai

@pytest_asyncio.fixture
async def assisted_user_chat(patched_openai):
    patched_openai.beta.assistants.create.return_value = MagicMock(id = 1)
    patched_openai.beta.threads.create.return_value = MagicMock(id = 2)

    return await AssistedUserChat.create(100)

# Assisted User Chat Functionality
# -----------------------------------------------------------------------------------------------
class TestAssistedUserChatFunctionality:
    @pytest.mark.asyncio
    async def test_create_assisted_user_chat(self, patched_openai, assisted_user_chat):
        """Tests the initialization of an assisted user chat object."""
        assert isinstance(assisted_user_chat, AssistedUserChat)
        assert assisted_user_chat.user_id == 100
        assert assisted_user_chat.assistant.id == 1
        assert assisted_user_chat.thread.id == 2

        patched_openai.beta.assistants.create.assert_awaited_once()
        patched_openai.beta.threads.create.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("processed_response,parsed_response,expected", [
        (True, 'bar', 'bar'),
        (False, None, "Immobyte's Assistant failed to process a response. Please try again later."),
        (None, None, "Immobyte's Assistant failed to process a response. Please try again later."),
        (True, None, "Immobyte's Assistant failed to parse a response. Please try again later.")
    ])
    async def test_call_assister_user_chat(self, patched_openai, assisted_user_chat, processed_response, parsed_response, expected):
        """Tests the assistant's response to a user message."""
        with patch('auctions_ai.chats.AssistedUserChat.process_assistant_response', return_value = processed_response):
            with patch('auctions_ai.chats.AssistedUserChat.parse_assistant_response', return_value = parsed_response):
                response = await assisted_user_chat.call('foo')

                assert response == expected

                patched_openai.beta.threads.messages.create.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("run_object,run_status_completed,expected,log_message", [
        (MagicMock(id = 1), True, True, []),
        (MagicMock(id = 2), False, False, []),
        (None, None, None, ["Unable to process assistant's response."]),
    ])
    async def test_process_assistant_response(self, patched_openai, assisted_user_chat, run_object, run_status_completed, expected, log_message, caplog):
        """Tests if the assistant's reponse has been processed."""
        with patch('auctions_ai.chats.AssistedUserChat.check_status_completed', return_value = run_status_completed):
            patched_openai.beta.threads.runs.create.return_value = run_object
            processed_response = await assisted_user_chat.process_assistant_response()

            assert log_message == caplog.messages
            assert processed_response == expected

            patched_openai.beta.threads.runs.create.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("run_object,run_status,expected,await_count,log_messages", [
        (MagicMock(id = 1), MagicMock(status='completed'), True, 1, []),
        (MagicMock(id = 2), MagicMock(status='failed'), False, 2, ["Reached maximum retries to check run status."]),
        (MagicMock(id = 3), None, False, 2,["Unable to check run status.","Unable to check run status.","Reached maximum retries to check run status."])
    ])
    async def test_check_status_completed(self, patched_openai, assisted_user_chat, run_object, run_status, expected, await_count, log_messages, caplog):
        "Tests if the run went into completed status."
        patched_openai.beta.threads.runs.create.return_value = run_object
        patched_openai.beta.threads.runs.retrieve.return_value = run_status

        # Set arguments: max_retries = 1, interval = 0
        status_completed = await assisted_user_chat.check_status_completed(run_object.id, 1, 0)

        assert log_messages == caplog.messages
        assert status_completed == expected

        patched_openai.beta.threads.runs.retrieve.assert_awaited()
        assert patched_openai.beta.threads.runs.retrieve.await_count == await_count

    @pytest.mark.asyncio
    @pytest.mark.parametrize("thread_messages_object,expected,log_messages", [
        (MagicMock(data = [MagicMock(content = [MagicMock(text = MagicMock(value = 'bar'))])]), 'bar', []),
        (MagicMock(data = []), None, ['Unexpected thread message structure.']),
        (None, None, ['Unable to read thread messages.'])
    ])
    async def test_parse_assistant_response(self, patched_openai, assisted_user_chat, thread_messages_object, expected, log_messages, caplog):
        "Tests if the response is parsed as expected."
        patched_openai.beta.threads.messages.list.return_value = thread_messages_object

        parsed_response = await assisted_user_chat.parse_assistant_response()

        assert log_messages == caplog.messages
        assert parsed_response == expected

        patched_openai.beta.threads.messages.list.assert_awaited_once()


# OpenAI API Interactions
# -----------------------------------------------------------------------------------------------
# NOTE:
# Error handling of openai exceptions are covered on test_decorator.py
class TestOpenAiInteraction:
    @pytest.mark.asyncio
    async def test_add_user_message(self, patched_openai, assisted_user_chat):
        """Tests how to add messages to a thread."""
        await assisted_user_chat.add_user_message('foo')

        patched_openai.beta.threads.messages.create.assert_awaited_once_with(
            thread_id = 2,
            role ='user',
            content = 'foo'
        )

    @pytest.mark.asyncio
    async def test_run_assistant(self, patched_openai, assisted_user_chat):
        """Tests how to create a run in a thread."""
        await assisted_user_chat.run_assistant()

        patched_openai.beta.threads.runs.create.assert_awaited_once_with(
            thread_id = 2,
            assistant_id = 1
        )

    @pytest.mark.asyncio
    async def test_retrieve_assistant(self, patched_openai, assisted_user_chat):
        """Tests how to get a run from a thread."""
        await assisted_user_chat.retrieve_assistant(3)

        patched_openai.beta.threads.runs.retrieve.assert_awaited_once_with(
            thread_id = 2,
            run_id = 3
        )

    @pytest.mark.asyncio
    async def test_read_thread_messages(self, patched_openai, assisted_user_chat):
        """Tests how to get all messages in a thread."""
        await assisted_user_chat.read_thread_messages()

        patched_openai.beta.threads.messages.list.assert_awaited_once_with(
            thread_id = 2
        )
