import pytest
import openai
from unittest.mock import AsyncMock, MagicMock
from auctions_ai.decorators import log_openai_error


class TestLogOpenAiDecorator:
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
    async def test_log_openai_error_for_failure(
        self, exception, expected, log_message, caplog
    ):
        """Tests error handling of openai exceptions."""
        async_function = AsyncMock(side_effect=exception)
        decorated_async_function = log_openai_error(async_function)

        response = await decorated_async_function()

        assert log_message in caplog.text
        assert response == expected

        async_function.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_log_openai_error_for_success(self):
        """Tests a successful asynchronous function."""
        async_function = AsyncMock(return_value=1)
        decorated_async_function = log_openai_error(async_function)

        response = await decorated_async_function()

        assert response == 1

        async_function.assert_awaited_once()
