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
        self = cls()
        self.client = AsyncOpenAI(max_retries=2, timeout=300.0)
        self.assistant = await self.client.beta.assistants.create(
            name = 'Immobyte Assistant',
            instructions = 'You are a real estate agent. Help and guide users to buy real estate property.',
            tools = [{'type': 'retrieval'}],
            model = 'gpt-4-1106-preview'
        )
        self.thread = await self.client.beta.threads.create()
        # TODO's:
        # Asyncronous call to the database is causing a load error. Find out why.
        # self.user = await User.objects.aget(pk=user_id)
        self.user_id = user_id
        return self

    async def call(self, content):
        """Add message to thread."""
        await self.add_message(content)

        """Run the assistant."""
        run_assistant = await self.run_assistant()

        """Check the run status."""
        run_status_completed = await self.check_status_completed(run_assistant.id)

        """Display the assistant's response."""
        if run_status_completed:
            try:
                thread_messages = await self.read_thread_messages()
                return thread_messages.data[0].content[0].text.value
            except Exception as e:
                logger.warning("Could not return the assistant's message.", e)
        else:
            return "Immobyte's Assistant failed to return an answer. Please try again later."

    @log_openai_error
    async def add_message(self, content):
        await self.client.beta.threads.messages.create(
            thread_id = self.thread.id,
            role = 'user',
            content = content
        )

    @log_openai_error
    async def run_assistant(self):
        return await self.client.beta.threads.runs.create(
            thread_id = self.thread.id,
            assistant_id = self.assistant.id,
        )

    @log_openai_error
    async def retrieve_assistant(self, run_id):
        return await self.client.beta.threads.runs.retrieve(
            thread_id = self.thread.id,
            run_id = run_id
        )

    async def check_status_completed(self, run_id, max_retries=10):
        retries = 0
        while retries <= max_retries:
            try:
                run = await self.retrieve_assistant(run_id)
                if run.status == 'completed':
                    return True
            except Exception as e:
                logger.warning("Could not check run status.", e)

            await asyncio.sleep(5)
            retries += 1

        logger.warning("Maximum retries to check run status were reached.")
        return False

    @log_openai_error
    async def read_thread_messages(self):
        return await self.client.beta.threads.messages.list(thread_id = self.thread.id)
