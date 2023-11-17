from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import json
from auctions.models import Auction
from auctions.forms import ChatForm
from auctions.chats import AssistedUserChat


# Create your views here.
class AuctionListView(LoginRequiredMixin, ListView):
    model = Auction
    context_object_name = 'auctions'

class AuctionDetailView(LoginRequiredMixin, DetailView):
    model = Auction
    context_object_name = 'auction'

class ChatFormView(LoginRequiredMixin, FormView):
    template_name = "auctions/auction_chat.html"
    form_class = ChatForm

    def form_valid(self, form):
        # Get the parameter from the form
        message = form.cleaned_data['message']
        user_id = self.request.user.id

        # Instantiate and call another class based on the parameter
        if not message:
            response = {'error': 'Write a message'}
        else:
            response = AssistedUserChat(user_id).call(message)

        # Returning a JSON Response
        return JsonResponse({'data': json.dumps(response)})
