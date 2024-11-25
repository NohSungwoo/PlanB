from django.contrib.auth import get_user_model
from rest_framework import status

from memos.models import Memo, MemoSet
from tests.auth_base_test import TestAuthBase

User = get_user_model()


class TestMemoList(TestAuthBase):

    URL = "/api/v1/memos/"

    def setUp(self):
        super().setUp()

        # create a test memoset

        self.memo_set = MemoSet.objects.create(user=self.user, title="TestMemoSet")

        # create a test Memo

        self.memo = Memo.objects.create(
            memo_set=self.memo_set,
            title="title",
            text="text",
        )

    def test_get_memos(self):
        response = self.client.get(self.URL)
        data = response.data
        print(data)
        expected_data = {"id": 1, "memo_set": 1, "title": "title", "content": "content"}

        for expected_key, expected_value in expected_data.items():
            self.assertEqual(expected_value, data[expected_key])


class TestMemoDetail(TestAuthBase):
    pass


class TestMemoSetList(TestAuthBase):

    URL = "/api/v1/memos/set"

    def setUp(self):
        super().setUp()
        # Create multiple MemoSets for testing
        self.memo_set1 = MemoSet.objects.create(user=self.user, title="MemoSet 1")
        self.memo_set2 = MemoSet.objects.create(user=self.user, title="MemoSet 2")

    def test_get_memosets(self):
        """Test fetching the list of MemoSets"""
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two MemoSets should be returned

    def test_create_memoset(self):
        """Test creating a new MemoSet"""
        payload = {"title": "New MemoSet"}
        response = self.client.post(self.URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertEqual(MemoSet.objects.count(), 3)  # Ensure a new MemoSet is created

    def test_create_memoset_invalid(self):
        """Test creating a MemoSet with invalid data"""
        payload = {}
        response = self.client.post(self.URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)  # Title field is required


class TestMemoSetDetail(TestAuthBase):

    URL = "/api/v1/memos/set"

    def setUp(self):
        super().setUp()
        self.memo_set = MemoSet.objects.create(user=self.user, title="Test MemoSet")
        self.url = f"{self.URL}/{self.memo_set.id}"

    def test_get_memoset_detail(self):
        """Test fetching the details of a MemoSet"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.memo_set.title)

    def test_get_memoset_not_found(self):
        """Test fetching a MemoSet that does not exist"""
        url = f"{self.URL}/999"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_memoset(self):
        """Test updating a MemoSet"""
        payload = {"title": "Updated Title"}
        response = self.client.put(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.memo_set.refresh_from_db()
        self.assertEqual(self.memo_set.title, payload["title"])

    def test_update_memoset_partial(self):
        """Test partial update of a MemoSet"""
        payload = {"title": "Partially Updated Title"}
        response = self.client.put(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.memo_set.refresh_from_db()
        self.assertEqual(self.memo_set.title, payload["title"])

    def test_delete_memoset(self):
        """Test deleting a MemoSet"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MemoSet.objects.filter(id=self.memo_set.id).exists())

    def test_delete_memoset_not_found(self):
        """Test deleting a MemoSet that does not exist"""
        url = f"{self.URL}/999"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
