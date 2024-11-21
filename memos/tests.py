from django.contrib.auth import get_user_model

from tests.auth_base_test import TestAuthBase
from memos.models import Memo, MemoSet

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
    pass


class TestMemoSetDetail(TestAuthBase):
    pass
