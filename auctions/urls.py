from django.urls import path

from auctions.views import list
from auctions.views import details

urlpatterns = [
  path('auctions', list),
  path('auctions/<int:pk>', details)
]
