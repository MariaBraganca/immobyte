import pytest
import openai

from unittest.mock import MagicMock


# OpenAI API Interactions
# -----------------------------------------------------------------------------------------------
class TestOpenAiInteractionForSuccess:
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
class TestOpenAiInteractionForFailure:
    @pytest.mark.asyncio
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
