from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from auctions_ai.forms import ChatForm
from auctions_ai.chats import AssistedUserChat

# Create your views here.
class ChatFormView(LoginRequiredMixin, FormView):
    template_name = "auctions_ai/auction_chat.html"
    form_class = ChatForm

    def form_valid(self, form):
        message = form.cleaned_data['message']
        user_id = self.request.user.id

        if not message:
            response = 'Write a message'
        else:
            response = AssistedUserChat(user_id).call(message)

        return response
