import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.LazyAttribute(lambda obj: "%s@example.com" % obj.username)
