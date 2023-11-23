from django.urls import path

from auctions_ai.views import ChatFormView

urlpatterns = [
    path('chat', ChatFormView.as_view(), name='auctions_ai.chat')
]
