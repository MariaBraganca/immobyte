from django.shortcuts import render, get_object_or_404
from auctions.models import Auction

# Create your views here.
def list(request):
    auctions = Auction.objects.all()
    return render(request, 'auctions/list.html', {'auctions': auctions})

def details(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    return render(request, 'auctions/details.html', { 'auction': auction })
