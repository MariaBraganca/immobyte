from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from auctions.models import Auction

# Create your views here.
class AuctionListView(LoginRequiredMixin, ListView):
    model = Auction
    context_object_name = 'auctions'

class AuctionDetailView(LoginRequiredMixin, DetailView):
    model = Auction
    context_object_name = 'auction'
