from django.views.generic import ListView, DetailView
from auctions.models import Auction

# Create your views here.
class AuctionListView(ListView):
    model = Auction
    context_object_name = 'auctions'

class AuctionDetailView(DetailView):
    model = Auction
    context_object_name = 'auction'
