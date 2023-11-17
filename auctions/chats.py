from django.contrib.auth.models import User
from openai import OpenAI
import os
import time

class AssistedUserChat:
    """Attempt to model assisted user chats."""
    
    def __init__(self, user_id):
        """Initalize user, client, assistant and thread."""
        self.user = User.objects.get(pk=user_id)
        self.client = OpenAI(api_key= os.getenv('OPENAI_API_KEY'))
        self.assistant = self.client.beta.assistants.create(
            name = 'Immobyte Assistant',
            instructions = 'You are a real estate agent. Write and run code to sell real estate property.',
            tools = [{'type': 'code_interpreter'}],
            model = 'gpt-4-1106-preview'
        )
        self.thread = self.client.beta.threads.create()
        
    def call(self, content):
        """Add message to thread."""
        self.add_message(content)
                
        """Run the assistant."""
        run = self.run_assistant()

        """Enqueue the assistant's response."""
        self.retrieve_assistant(run.id)

        time.sleep(3)

        """List all thread messages"""
        thread_messages = self.read_thread_messages()

        return [tm.content[0].text.value for tm in thread_messages.data]

    def add_message(self, content):
        self.client.beta.threads.messages.create(
            thread_id = self.thread.id,
            role = 'user',
            content = content
        )
        
    def run_assistant(self):
        object = self.client.beta.threads.runs.create(
            thread_id = self.thread.id,
            assistant_id = self.assistant.id,
            instructions = f"Please address the user as {self.user.username}."
        )
        return object
        
    def retrieve_assistant(self, run_id):
        object = self.client.beta.threads.runs.retrieve(
            thread_id = self.thread.id,
            run_id = run_id
        )
        return object
    
    def read_thread_messages(self):
        list = self.client.beta.threads.messages.list(thread_id = self.thread.id)
        
        return list
