from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# from auctions_ai.forms import ChatForm
# from auctions_ai.chats import AssistedUserChat

# import json

# Create your views here.
class ChatView(LoginRequiredMixin, TemplateView):
    template_name = "auctions_ai/auction_chat.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         context['user_id'] = self.request.user.id
    #     return context
