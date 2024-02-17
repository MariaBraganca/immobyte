import pytest
from bs4 import BeautifulSoup

from auctions.models import Auction

pytestmark = pytest.mark.django_db


def test_auction_list_view(client):
    response = client.get(path="/auctions")

    assert response.status_code == 200
    assert response.template_name == ["auctions/auction_list.html"]
    assert response.is_rendered == True

    soup = BeautifulSoup(response.rendered_content, "html.parser")
    identifiers = [i.text for i in soup.find_all("td", {"id": "auctionNumber"})]
    auction_numbers = list(Auction.objects.values_list("number", flat=True))

    assert identifiers == auction_numbers


def test_auction_detail_view(client):
    auction = Auction.objects.first()
    response = client.get(path=f"/auctions/{auction.pk}")

    assert response.status_code == 200
    assert response.template_name == ["auctions/auction_detail.html"]
    assert response.is_rendered == True

    soup = BeautifulSoup(response.rendered_content, "html.parser")
    identifier = soup.find("dd", {"id": "auctionNumber"})
    assert identifier.text == auction.number
