from http.client import responses

from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
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

    def test_create_and_search(self):
        self.client.post(self.URL, data={"title": "test"})

        response = self.client.get(self.URL)
        data = response.json()

        tag = Tag.objects.filter(user=self.user)

        serializer = TagDetailSerializer(tag, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, serializer.data)

    def test_no_data(self):
        response = self.client.post(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"detail": "Need title data"})

    def test_data_unique(self):
        self.client.post(self.URL, data={"title": 123})
        response = self.client.post(self.URL, data={"title": 123})
        data = response.json()

        self.assertEqual(data, {"title": ["tag with this title already exists."]})


class TestTagDetailView(APITestCase):

    URL = "/api/v1/tags/1"

    def setUp(self):
        self.user = User.objects.create(email="test@tester.com", birthday="1995-08-17")
        self.user.set_password("123123")
        self.user.is_active = True
        self.user.save()

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_get_tag_detail(self):
        tag = Tag.objects.create(title="test", user=self.user)

        response = self.client.get(self.URL)
        data = response.json()

        serializer = TagDetailSerializer(tag)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(data, serializer.data)

    def test_tag_not_found(self):
        response = self.client.get(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(data, {"detail": "Not found."})

    def test_tag_update(self):
        Tag.objects.create(user=self.user, title="title")
        response = self.client.put(self.URL, data={"title": "update_title"})
        data = response.json()

        tag = Tag.objects.get(title="update_title")
        serializer = TagDetailSerializer(tag)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(data, serializer.data)

    def test_tag_update_duplication_value(self):
        Tag.objects.create(user=self.user, title="title")
        Tag.objects.create(user=self.user, title="duplicate_title")
        response = self.client.put(self.URL, data={"title": "duplicate_title"})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"title": ["tag with this title already exists."]})

    def test_tag_delete(self):
        Tag.objects.create(user=self.user, title="title")
        response = self.client.delete(self.URL)

        try:
            Tag.objects.get(pk=1)

        except Tag.DoesNotExist:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
