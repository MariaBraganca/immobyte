from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class ChatView(LoginRequiredMixin, TemplateView):
    template_name = "auctions_ai/auction_chat.html"
