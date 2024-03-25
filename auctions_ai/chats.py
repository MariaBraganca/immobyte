import logging
import asyncio

from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from openai import AsyncOpenAI
from auctions_ai.decorators import log_openai_error

logger = logging.getLogger(__name__)


class AssistedUserChat:
    """Attempt to model assisted user chats."""

    @classmethod
    async def create(cls, user_id):
        """Initializes an instance of AssistedUserChat asynchronously."""
        self = cls()
        self.user = await database_sync_to_async(User.objects.get)(pk=user_id)
        self.client = AsyncOpenAI(max_retries=2, timeout=300.0)
        self.assistant = await self.client.beta.assistants.create(
            name="Immobyte-GPT",
            instructions=f"""You are a real estate agent. Your job is to help and guide users to buy real estate property.
                You are polite and have excellent communication skills. The current user is called {self.user.username}.
                Always greet and address users by their name.""",
            tools=[{"type": "retrieval"}],
            model="gpt-4-1106-preview",
        )
        self.thread = await self.client.beta.threads.create()
        return self

    async def call(self, content):
        """Handles chat interaction in order to return a response."""
        await self.add_user_message(content)

        if not await self.process_assistant_response():
            return "Immobyte's Assistant failed to process a response. Please try again later."

        response = await self.parse_assistant_response()

        return (
            response
            if response
            else "Immobyte's Assistant failed to parse a response. Please try again later."
        )

    async def process_assistant_response(self):
        run_assistant = await self.run_assistant()
        if run_assistant:
            return await self.check_status_completed(run_assistant.id)
        else:
            logger.warning("Unable to process assistant's response.")

        return None

    async def parse_assistant_response(self):
        thread_messages = await self.read_thread_messages()
        if thread_messages:
            try:
                # TODO's:
                # Add parser to read thread message.
                return thread_messages.data[0].content[0].text.value
            except (IndexError, AttributeError):
                logger.exception("Unexpected thread message structure.")
        else:
            logger.warning("Unable to read thread messages.")

        return None

    @log_openai_error
    async def add_user_message(self, content):
        await self.client.beta.threads.messages.create(
            thread_id=self.thread.id, role="user", content=content
        )

    @log_openai_error
    async def run_assistant(self):
        return await self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )

    @log_openai_error
    async def retrieve_assistant(self, run_id):
        return await self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id, run_id=run_id
        )

    async def check_status_completed(
        self,
        run_id,
        max_retries=10,
        base_interval=1,
        backoff_interval=2,
    ):
        retries = 0
        interval = base_interval
        while retries <= max_retries:
            run = await self.retrieve_assistant(run_id)
            try:
                if run.status == "completed":
                    return True
            except (NameError, AttributeError):
                logger.exception("Unable to check run status.")

            await asyncio.sleep(interval)
            interval = min(base_interval * (backoff_interval**retries), 60)
            retries += 1

        logger.warning("Reached maximum retries to check run status.")
        return False

    @log_openai_error
    async def read_thread_messages(self):
        return await self.client.beta.threads.messages.list(thread_id=self.thread.id)
