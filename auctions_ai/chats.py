import os
import asyncio

# from django.contrib.auth.models import User
from openai import AsyncOpenAI

class AssistedUserChat:
    """Attempt to model assisted user chats."""

    @classmethod
    async def create(cls, user_id):
        self = cls()
        # TODO's:
        # Move client's credentials out of this class.
        self.client = AsyncOpenAI(api_key= os.getenv('OPENAI_API_KEY'))
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
        await self.check_status(run_assistant.id)

        """Display the assistant's response."""
        thread_messages = await self.read_thread_messages()

        return thread_messages.data[0].content[0].text.value

    async def add_message(self, content):
        await self.client.beta.threads.messages.create(
            thread_id = self.thread.id,
            role = 'user',
            content = content
        )

    async def run_assistant(self):
        return await self.client.beta.threads.runs.create(
            thread_id = self.thread.id,
            assistant_id = self.assistant.id,
            instructions = f"Please address the user by Immobyte-User for now."
        )

    async def retrieve_assistant(self, run_id):
        return await self.client.beta.threads.runs.retrieve(
            thread_id = self.thread.id,
            run_id = run_id
        )

    async def check_status(self, run_id):
        while True:
            run = await self.retrieve_assistant(run_id)
            if run.status == 'completed':
                break
            await asyncio.sleep(1)

    async def read_thread_messages(self):
        return await self.client.beta.threads.messages.list(thread_id = self.thread.id)
