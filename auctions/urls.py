from django.urls import path

from auctions.views import AuctionListView, AuctionDetailView

urlpatterns = [
    path('auctions', AuctionListView.as_view()),
    path('auctions/<int:pk>', AuctionDetailView.as_view())
]
