from django.template.context_processors import request
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from tags.models import Tag
from tags.serializers import TagDetailSerializer
from users.models import User


class TestTagListView(APITestCase):

    URL = "/api/v1/tags/"

    def setUp(self):
        self.user = User.objects.create(email="test@tester.com", birthday="1995-08-17")
        self.user.set_password("123123")
        self.user.is_active = True
        self.user.save()

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_get_tag_list(self):
        self.client.post(self.URL, data={"title": "test"})

        response = self.client.get(self.URL)
        data = response.json()

        tag = Tag.objects.filter(user=self.user)

        serializer = TagDetailSerializer(tag, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, serializer.data)
