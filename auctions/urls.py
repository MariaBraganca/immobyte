from django.urls import path

from auctions.views import AuctionListView, AuctionDetailView

urlpatterns = [
    path('auctions', AuctionListView.as_view(), name="auction.list"),
    path('auctions/<int:pk>', AuctionDetailView.as_view(), name="auction.detail")
]
