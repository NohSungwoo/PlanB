import datetime
import json
import pprint
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

from calendars.models import Calendar, Schedule
from tags.models import Tag
from memos.models import Memo, MemoSet
from tests.auth_base_test import TestAuthBase
from todos.models import Todo, TodoSet

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

    def test_get_memos_with_year_month_day(self):
        ### do create sample memos
        memo_9999_12_31 = Memo.objects.create(
            memo_set=self.memo_set,
            title="9999",
            text="9999",
        )
        Memo.objects.filter(pk=memo_9999_12_31.pk).update(created_at="9999-12-31")

        memo_9999_12_01 = Memo.objects.create(
            memo_set=self.memo_set,
            title="9999",
            text="9999",
        )
        Memo.objects.filter(pk=memo_9999_12_01.pk).update(created_at="9999-12-01")

        memo_9999_11_30 = Memo.objects.create(
            memo_set=self.memo_set,
            title="9999",
            text="9999",
        )
        Memo.objects.filter(pk=memo_9999_11_30.pk).update(created_at="9999-11-30")

        ### do filter

        response = self.client.get(
            self.URL,
            query_params={
                "year": 9999,
            },
        )
        self.assertEqual(len(response.data), 3)

        response = self.client.get(
            self.URL,
            query_params={
                "year": 9999,
                "month": 12,
            },
        )
        self.assertEqual(len(response.data), 2)

        response = self.client.get(
            self.URL,
            query_params={"year": 9999, "month": 12, "day": 1},
        )
        self.assertEqual(len(response.data), 1)

    def test_get_memos_with_memo_set(self):
        """
        query param의 `memo_set[]` 인자를 바탕으로 원하는
        메모셋과 연관된 메모만 필터링합니다.
        """
        other_memo_set = MemoSet.objects.create(user=self.user, title="other_memo_set")

        memo_in_default_set = Memo.objects.create(
            memo_set=self.memo_set,
            title="Test Memo in default memo set",
            text="This memo belongs to the default memo set.",
        )

        memo_in_other_set = Memo.objects.create(
            memo_set=other_memo_set,
            title="Test Memo in OtherMemoSet",
            text="This memo belongs to the other memo set.",
        )

        # default memo set 먼저
        response = self.client.get(
            self.URL, query_params={"memo_set[]": [self.memo_set.pk]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # other memo set
        response = self.client.get(
            self.URL, query_params={"memo_set[]": [other_memo_set.pk]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], memo_in_other_set.title)

        # 둘 다
        response = self.client.get(
            self.URL, query_params={"memo_set[]": [self.memo_set.pk, other_memo_set.pk]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # Error case: invalid query param
        response = self.client.get(
            self.URL, query_params={"memo_set[]": ["hello", "world"]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_memos_with_tag(self):
        """
        tag를 생성하고 그 태그에 연결된 메모를 쿼리합니다.
        """

        # 없는 태그를 쿼리할 경우
        response = self.client.get(self.URL, query_params={"tag[]": "sample_tag"})
        self.assertEqual(len(response.data), 0)

        # 새 태그 생성 및 연결
        tag = Tag.objects.create(user=self.user, title="sample_tag")
        tag.memo.add(self.memo)
        tag.save()

        # 존재하는 태그를 쿼리할 경우
        response = self.client.get(self.URL, query_params={"tag[]": "sample_tag"})
        self.assertEqual(len(response.data), 1)

    def __create_sample_memos_relates_to_schedule_and_todo(self):
        """하나의 테스트케이스 마다 한 번의 request만 가능하기에 따로 뽑아놨습니다."""
        # create schedule with related memos
        self.schedule_related_memo = Memo.objects.create(
            memo_set=self.memo_set, title="schedulememo1", text="schedulememo1"
        )
        calendar = Calendar.objects.create(user=self.user, title="calendar")
        Schedule.objects.create(
            calendar=calendar,
            title="schedule",
            start_date=datetime.date(2024, 12, 4),
            memo=self.schedule_related_memo,
        )

        # create todo with related memos
        self.todo_related_memo = Memo.objects.create(
            memo_set=self.memo_set, title="todomemo1", text="todomemo1"
        )
        todo_set = TodoSet.objects.create(user=self.user, title="todoset")
        Todo.objects.create(
            todo_set=todo_set,
            memo=self.todo_related_memo,
            title="todo",
            start_date=datetime.date(2024, 12, 4),
        )

    def test_get_memos_with_types1(self):
        """
        type[] 필터링의 결과가 올바르게 되는지 확인합니다.

        ## Example

        ```
        case ["schedule"]:
            query will contain only schedule-related memos
        ```
        """
        self.__create_sample_memos_relates_to_schedule_and_todo()

        # it should only give schedule_related_memo if `type[]=schedule` query param has entered
        response = self.client.get(self.URL, query_params={"type[]": "schedule"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(len(data), 1, str(data))
        self.assertEqual(self.schedule_related_memo.title, data[0].get("title"))

    def test_get_memos_with_types2(self):
        """
        type[] 필터링의 결과가 올바르게 되는지 확인합니다.

        ## Example

        ```
        case ["schedule", ""]:
            query will contain schedule-related memos and standalone memos.
        ```
        """
        self.__create_sample_memos_relates_to_schedule_and_todo()

        # it should give todo_related_memo and standalone memo
        # if `type[]=schedule&type[]=` query param has entered
        response = self.client.get(self.URL, query_params={"type[]": ["schedule", ""]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2, str(response.data))

    def test_get_memos_with_types3(self):
        """
        type[] 필터링의 결과가 올바르게 되는지 확인합니다.

        ## Example

        ```
        case [""]:
            query will contain only standalone memos.
        ```
        """
        self.__create_sample_memos_relates_to_schedule_and_todo()

        # it should give standalone memo if `type[]=schedule&type[]=todo` query param has entered
        response = self.client.get(self.URL, query_params={"type[]": [""]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1, str(response.data))
        self.assertEqual(response.data[0]["title"], self.memo.title)

    def test_create_memo(self):
        """Test creating a new Memo"""
        payload = {"title": "New Memo title", "text": "New Memo text", "memo_set": 1}
        response = self.client.post(self.URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for attr, value in payload.items():
            self.assertEqual(response.data[attr], value)

        self.assertEqual(Memo.objects.count(), 2)

    def test_get_memos_order_by_create_at_asc(self):
        """order_by("created_at")"""
        COUNT = 10
        FROM_YEAR = 9999

        # remove default memo
        self.memo.delete()

        memos = [
            Memo.objects.create(memo_set=self.memo_set, title=str(i), text=str(i))
            for i in range(1, COUNT + 1)
        ]

        # update each memos's created_at reversly
        for i, memo in enumerate(memos):
            year = FROM_YEAR - i
            memo.created_at = datetime.datetime(year, 1, 1)
            memo.save(force_update=True)

        # it should give reversed result when sort with "created_at_asc"
        response = self.client.get(self.URL, query_params={"sort": "created_at_asc"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), COUNT)

        for i, memo in enumerate(reversed(memos)):
            self.assertEqual(response.data[i]["id"], memo.id)

    def test_get_memos_order_by_created_at_desc(self):
        """order_by("-created_at")"""
        COUNT = 10

        # remove default memo
        self.memo.delete()

        memos = [
            Memo.objects.create(memo_set=self.memo_set, title=str(i), text=str(i))
            for i in range(1, COUNT + 1)
        ]

        # it should give reversed result when sort with "created_at_desc"
        response = self.client.get(self.URL, query_params={"sort": "created_at_desc"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), COUNT)

        for i, memo in enumerate(reversed(memos)):
            self.assertEqual(response.data[i]["id"], memo.id)


class TestMemoDetail(TestAuthBase):
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

        self.url = self.URL + str(self.memo.pk) + "/"

    def test_get_one_memo(self):
        response = self.client.get(self.url)
        data = response.data
        expected_data = {"id": 1, "memo_set": 1, "title": "title", "text": "text"}

        for expected_key, expected_value in expected_data.items():
            self.assertEqual(expected_value, data[expected_key])

    def test_update_memo_success(self):
        payload = {
            "title": "Updated Title",
            "text": "Updated Text",
            "memo_set": self.memo_set.pk,
        }
        response = self.client.put(self.url, payload)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK, response.data.get("message")
        )

        for attr, value in payload.items():
            self.assertEqual(response.data[attr], value)

    def test_update_memo_not_found(self):
        invalid_url = reverse("memo-detail", args=[999])
        response = self.client.put(invalid_url, {"title": "hello?"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_memo_invalid_data(self):
        payload = {"titlle": "Two L in attribute!!! 💀💀💀💀"}
        response = self.client.put(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestMemoSetList(TestAuthBase):

    URL = "/api/v1/memos/set/"

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

    URL = "/api/v1/memos/set/"

    def setUp(self):
        super().setUp()
        self.memo_set = MemoSet.objects.create(user=self.user, title="Test MemoSet")
        self.url = f"{self.URL}{self.memo_set.id}/"

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
