from django.contrib import admin
from auctions.models import Auction

# Register your models here.
class AuctionAdmin(admin.ModelAdmin):
    list_display = ['number']

admin.site.register(Auction, AuctionAdmin)
