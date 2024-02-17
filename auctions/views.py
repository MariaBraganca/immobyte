from django.views.generic import ListView, DetailView
from auctions.models import Auction
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class AuctionListView(LoginRequiredMixin, ListView):
    model = Auction
    context_object_name = "auctions"


class AuctionDetailView(LoginRequiredMixin, DetailView):
    model = Auction
    context_object_name = "auction"
