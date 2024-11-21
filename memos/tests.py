from django.contrib.auth import get_user_model

from common.tests import TestAuthBase
from memos.models import Memo, MemoSet

User = get_user_model()


class TestMemoList(TestAuthBase):

    URL = "/api/v1/memos/"

    def setUp(self):
        super().setUp()

        # create a test memoset

        self.memo_set = MemoSet.objects.create(user=self.user, name="TestMemoSet")

        # create a test Memo

        self.memo = Memo.objects.create(
            memo_set=self.memo_set,
            content="Test Memo Content",
        )


class TestMemoDetail(TestAuthBase):
    pass


class TestMemoSetList(TestAuthBase):
    pass


class TestMemoSetDetail(TestAuthBase):
    pass
