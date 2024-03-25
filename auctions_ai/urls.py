from django.urls import path

from auctions_ai.views import ChatView

urlpatterns = [path("chat", ChatView.as_view(), name="auctions_ai.chat")]
