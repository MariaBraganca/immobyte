import logging
import asyncio

# from django.contrib.auth.models import User
from openai import AsyncOpenAI
from auctions_ai.decorators import log_openai_error

logger = logging.getLogger(__name__)


class AssistedUserChat:
    """Attempt to model assisted user chats."""

    @classmethod
    async def create(cls, user_id):
        """Initializes an instance of AssistedUserChat asynchronously."""
        self = cls()
        self.client = AsyncOpenAI(max_retries=2, timeout=300.0)
        self.assistant = await self.client.beta.assistants.create(
            name="Immobyte Assistant",
            instructions="You are a real estate agent. Help and guide users to buy real estate property.",
            tools=[{"type": "retrieval"}],
            model="gpt-4-1106-preview",
        )
        self.thread = await self.client.beta.threads.create()
        # TODO's:
        # Asyncronous call to the database is causing a load error. Find out why.
        # self.user = await User.objects.aget(pk=user_id)
        self.user_id = user_id
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

    # TODO's:
    # Add an exponential backoff instead of a fixed interval for retries.
    async def check_status_completed(self, run_id, max_retries=10, interval=5):
        retries = 0
        while retries <= max_retries:
            run = await self.retrieve_assistant(run_id)
            try:
                if run.status == "completed":
                    return True
            except AttributeError:
                logger.exception("Unable to check run status.")

            await asyncio.sleep(interval)
            retries += 1

        logger.warning("Reached maximum retries to check run status.")
        return False

    @log_openai_error
    async def read_thread_messages(self):
        return await self.client.beta.threads.messages.list(thread_id=self.thread.id)
