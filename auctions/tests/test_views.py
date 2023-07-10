import pytest
from bs4 import BeautifulSoup

from auctions.models import Auction

pytestmark = pytest.mark.django_db

def test_auction_list_view(client):
    response = client.get(path='/auctions')
    
    assert response.status_code == 200
    assert response.template_name == ['auctions/auction_list.html']
    assert response.is_rendered == True
    
    soup = BeautifulSoup(response.rendered_content, 'html.parser')
    subheaders = [h3.string for h3 in soup.find_all('h3')]
    numbers = list(Auction.objects.values_list('number', flat=True))
    
    assert subheaders == numbers
    
def test_auction_detail_view(client):   
    auction = Auction.objects.first()
    response = client.get(path=f'/auctions/{auction.pk}')
    
    assert response.status_code == 200
    assert response.template_name == ['auctions/auction_detail.html']
    assert response.is_rendered == True
    
    soup = BeautifulSoup(response.rendered_content, 'html.parser')
    assert soup.h2.text == auction.number
