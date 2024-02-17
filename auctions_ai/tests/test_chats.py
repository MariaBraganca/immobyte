import pytest
import pytest_asyncio
import openai
from unittest.mock import AsyncMock, MagicMock, patch
from auctions_ai.chats import AssistedUserChat


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
async def assisted_user_chat(patched_openai):
    patched_openai.beta.assistants.create.return_value = MagicMock(id=1)
    patched_openai.beta.threads.create.return_value = MagicMock(id=2)

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
    @pytest.mark.parametrize(
        "processed_response,parsed_response,expected",
        [
            (True, "bar", "bar"),
            (
                False,
                None,
                "Immobyte's Assistant failed to process a response. Please try again later.",
            ),
            (
                None,
                None,
                "Immobyte's Assistant failed to process a response. Please try again later.",
            ),
            (
                True,
                None,
                "Immobyte's Assistant failed to parse a response. Please try again later.",
            ),
        ],
    )
    async def test_call_assister_user_chat(
        self,
        patched_openai,
        assisted_user_chat,
        processed_response,
        parsed_response,
        expected,
    ):
        """Tests the assistant's response to a user message."""
        with patch(
            "auctions_ai.chats.AssistedUserChat.process_assistant_response",
            return_value=processed_response,
        ):
            with patch(
                "auctions_ai.chats.AssistedUserChat.parse_assistant_response",
                return_value=parsed_response,
            ):
                response = await assisted_user_chat.call("foo")

                assert response == expected

                patched_openai.beta.threads.messages.create.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "run_object,run_status_completed,expected,log_message",
        [
            (MagicMock(id=1), True, True, []),
            (MagicMock(id=2), False, False, []),
            (None, None, None, ["Unable to process assistant's response."]),
        ],
    )
    async def test_process_assistant_response(
        self,
        patched_openai,
        assisted_user_chat,
        run_object,
        run_status_completed,
        expected,
        log_message,
        caplog,
    ):
        """Tests if the assistant's reponse has been processed."""
        with patch(
            "auctions_ai.chats.AssistedUserChat.check_status_completed",
            return_value=run_status_completed,
        ):
            patched_openai.beta.threads.runs.create.return_value = run_object
            processed_response = await assisted_user_chat.process_assistant_response()

            assert log_message == caplog.messages
            assert processed_response == expected

            patched_openai.beta.threads.runs.create.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "run_object,run_status,expected,await_count,log_messages",
        [
            (MagicMock(id=1), MagicMock(status="completed"), True, 1, []),
            (
                MagicMock(id=2),
                MagicMock(status="failed"),
                False,
                2,
                ["Reached maximum retries to check run status."],
            ),
            (
                MagicMock(id=3),
                None,
                False,
                2,
                [
                    "Unable to check run status.",
                    "Unable to check run status.",
                    "Reached maximum retries to check run status.",
                ],
            ),
        ],
    )
    async def test_check_status_completed(
        self,
        patched_openai,
        assisted_user_chat,
        run_object,
        run_status,
        expected,
        await_count,
        log_messages,
        caplog,
    ):
        "Tests if the run went into completed status."
        patched_openai.beta.threads.runs.create.return_value = run_object
        patched_openai.beta.threads.runs.retrieve.return_value = run_status

        # Set arguments: max_retries = 1, interval = 0
        status_completed = await assisted_user_chat.check_status_completed(
            run_object.id, 1, 0
        )

        assert log_messages == caplog.messages
        assert status_completed == expected

        patched_openai.beta.threads.runs.retrieve.assert_awaited()
        assert patched_openai.beta.threads.runs.retrieve.await_count == await_count

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "thread_messages_object,expected,log_messages",
        [
            (
                MagicMock(
                    data=[MagicMock(content=[MagicMock(text=MagicMock(value="bar"))])]
                ),
                "bar",
                [],
            ),
            (MagicMock(data=[]), None, ["Unexpected thread message structure."]),
            (None, None, ["Unable to read thread messages."]),
        ],
    )
    async def test_parse_assistant_response(
        self,
        patched_openai,
        assisted_user_chat,
        thread_messages_object,
        expected,
        log_messages,
        caplog,
    ):
        "Tests if the response is parsed as expected."
        patched_openai.beta.threads.messages.list.return_value = thread_messages_object

        parsed_response = await assisted_user_chat.parse_assistant_response()

        assert log_messages == caplog.messages
        assert parsed_response == expected

        patched_openai.beta.threads.messages.list.assert_awaited_once()


# OpenAI API Interactions
# -----------------------------------------------------------------------------------------------
class TestOpenAiInteraction:
    @pytest.mark.asyncio
    async def test_add_user_message_for_success(
        self, patched_openai, assisted_user_chat, caplog
    ):
        """Tests how to create a message in a thread."""
        response = await assisted_user_chat.add_user_message("foo")

        assert not caplog.messages
        assert response == None

        patched_openai.beta.threads.messages.create.assert_awaited_once_with(
            thread_id=2, role="user", content="foo"
        )

    @pytest.mark.asyncio
    async def test_run_assistant_for_success(
        self, patched_openai, assisted_user_chat, caplog
    ):
        """Tests how to create a run in a thread."""
        run = MagicMock()
        patched_openai.beta.threads.runs.create.return_value = run
        response = await assisted_user_chat.run_assistant()

        assert not caplog.messages
        assert response == run

        patched_openai.beta.threads.runs.create.assert_awaited_once_with(
            thread_id=2, assistant_id=1
        )

    @pytest.mark.asyncio
    async def test_retrieve_assistant_for_success(
        self, patched_openai, assisted_user_chat, caplog
    ):
        """Tests how to retrieve a run from a thread."""
        run = MagicMock()
        patched_openai.beta.threads.runs.retrieve.return_value = run
        response = await assisted_user_chat.retrieve_assistant(3)

        assert not caplog.messages
        assert response == run

        patched_openai.beta.threads.runs.retrieve.assert_awaited_once_with(
            thread_id=2, run_id=3
        )

    @pytest.mark.asyncio
    async def test_read_thread_messages_for_success(
        self, patched_openai, assisted_user_chat, caplog
    ):
        """Tests how to list all messages in a thread."""
        thread_messages = MagicMock()
        patched_openai.beta.threads.messages.list.return_value = thread_messages
        response = await assisted_user_chat.read_thread_messages()

        assert not caplog.messages
        assert response == thread_messages

        patched_openai.beta.threads.messages.list.assert_awaited_once_with(thread_id=2)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception,expected,log_message",
        [
            (
                openai.APIConnectionError(request=MagicMock()),
                None,
                "The server could not be reached",
            ),
            (
                openai.RateLimitError(message="", response=MagicMock(), body=None),
                None,
                "A 429 status code was received; we should back off a bit.",
            ),
            (
                openai.APIStatusError(message="", response=MagicMock(), body=None),
                None,
                "Another non-200-range status code was received",
            ),
        ],
    )
    async def test_add_user_message_for_failure(
        self,
        patched_openai,
        assisted_user_chat,
        exception,
        expected,
        log_message,
        caplog,
    ):
        """Tests error handling when creating a message in a thread."""
        patched_openai.beta.threads.messages.create.side_effect = exception
        response = await assisted_user_chat.add_user_message("foo")

        assert log_message in caplog.text
        assert response == expected

        patched_openai.beta.threads.messages.create.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception,expected,log_message",
        [
            (
                openai.APIConnectionError(request=MagicMock()),
                None,
                "The server could not be reached",
            ),
            (
                openai.RateLimitError(message="", response=MagicMock(), body=None),
                None,
                "A 429 status code was received; we should back off a bit.",
            ),
            (
                openai.APIStatusError(message="", response=MagicMock(), body=None),
                None,
                "Another non-200-range status code was received",
            ),
        ],
    )
    async def test_run_assistant_for_failure(
        self,
        patched_openai,
        assisted_user_chat,
        exception,
        expected,
        log_message,
        caplog,
    ):
        """Tests error handling when creating a run in a thread."""
        patched_openai.beta.threads.runs.create.side_effect = exception
        response = await assisted_user_chat.run_assistant()

        assert log_message in caplog.text
        assert response == expected

        patched_openai.beta.threads.runs.create.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception,expected,log_message",
        [
            (
                openai.APIConnectionError(request=MagicMock()),
                None,
                "The server could not be reached",
            ),
            (
                openai.RateLimitError(message="", response=MagicMock(), body=None),
                None,
                "A 429 status code was received; we should back off a bit.",
            ),
            (
                openai.APIStatusError(message="", response=MagicMock(), body=None),
                None,
                "Another non-200-range status code was received",
            ),
        ],
    )
    async def test_retrieve_assistant_for_failure(
        self,
        patched_openai,
        assisted_user_chat,
        exception,
        expected,
        log_message,
        caplog,
    ):
        """Tests error handling when retrieving a run from a thread."""
        patched_openai.beta.threads.runs.retrieve.side_effect = exception
        response = await assisted_user_chat.retrieve_assistant(3)

        assert log_message in caplog.text
        assert response == expected

        patched_openai.beta.threads.runs.retrieve.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception,expected,log_message",
        [
            (
                openai.APIConnectionError(request=MagicMock()),
                None,
                "The server could not be reached",
            ),
            (
                openai.RateLimitError(message="", response=MagicMock(), body=None),
                None,
                "A 429 status code was received; we should back off a bit.",
            ),
            (
                openai.APIStatusError(message="", response=MagicMock(), body=None),
                None,
                "Another non-200-range status code was received",
            ),
        ],
    )
    async def test_read_thread_messages_for_failure(
        self,
        patched_openai,
        assisted_user_chat,
        exception,
        expected,
        log_message,
        caplog,
    ):
        """Tests error handling when listing all messages from a thread."""
        patched_openai.beta.threads.messages.list.side_effect = exception
        response = await assisted_user_chat.read_thread_messages()

        assert log_message in caplog.text
        assert response == expected

        patched_openai.beta.threads.messages.list.assert_awaited_once()
