from django.template.defaultfilters import title
from django.utils import timezone
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from calendars.models import Calendar
from memos.models import MemoSet
from tests.auth_base_test import TestAuthBase
from todos.models import SubTodo, Todo, TodoSet


class TestTodoListView(TestAuthBase):

    URL = "/api/v1/todos/"

    def setUp(self):
        super().setUp()

        self.memo_set = MemoSet.objects.create(user=self.user, title="test_memo_set")
        self.todo_set = TodoSet.objects.create(user=self.user, title="test_todo_set")
        self.calendar = Calendar.objects.create(user=self.user, title="test_calendar")

    def test_create_todo(self):
        response = self.client.post(
            self.URL,
            data={
                "todo_set": 1,
                "memo": {"title": "test_memo", "text": "test", "memo_set": 1},
                "title": "test_todo",
                "start_date": timezone.localtime(),
            },
            format="json",
        )
        data = response.json()

        todo_set = 1
        memo_title = "test_memo"
        memo_text = "test"
        memo_set = 1

        title = "test_todo"

        response_title = data.pop("title")
        response_memo = data.pop("memo")
        response_todo_set = data.pop("todo_set")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_title, title)
        self.assertEqual(response_memo.pop("title"), memo_title)
        self.assertEqual(response_memo.pop("text"), memo_text)
        self.assertEqual(response_memo.pop("memo_set"), memo_set)
        self.assertEqual(response_todo_set, todo_set)

    def test_data_invalid(self):
        response = self.client.post(
            self.URL,
            data={
                "todo_set": 1,
                "memo": {"title": 1, "text": 1, "memo_set": "1"},
                "title": "test_todo",
            },
            format="json",
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"start_date": ["필수 항목입니다."]})

    def test_get_todo_list(self):
        self.client.post(
            self.URL,
            data={
                "todo_set": 1,
                "memo": {"title": "test_memo", "text": "test", "memo_set": 1},
                "title": "test_todo",
                "start_date": timezone.localtime(),
            },
            format="json",
        )

        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTodoDetailView(TestAuthBase):

    URL = "/api/v1/todos/1/"

    def setUp(self):
        super().setUp()

        TodoSet.objects.create(user=self.user, title="test_todo_set")
        MemoSet.objects.create(user=self.user, title="test_memo_set")
        Calendar.objects.create(user=self.user, title="test_calendar")

        self.todo = Todo.objects.create(
            title="test_todo", start_date=timezone.localtime()
        )

    def test_get_todo(self):
        response = self.client.get(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.pop("id"), 1)
        self.assertEqual(data.pop("todo_set"), 1)

    def test_todo_not_found(self):
        self.URL = "/api/v1/todos/2/"
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_todo(self):
        TodoSet.objects.create(user=self.user, title="test_todo_set2")

        response = self.client.put(
            self.URL,
            data={
                "todo_set": 2,
                "title": "update_title",
                "start_date": timezone.localtime(),
            },
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(data.pop("id"), 1)
        self.assertEqual(data.pop("todo_set"), 2)
        self.assertEqual(data.pop("title"), "update_title")

    def test_update_data_invalid(self):
        response = self.client.put(self.URL, data={"start_date": 1})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            data,
            {
                "start_date": [
                    "Datetime has wrong format. Use one of these formats instead: "
                    "YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
                ]
            },
        )

    def test_delete_todo(self):
        response = self.client.delete(self.URL)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestTodoStatusUpdateView(TestAuthBase):

    URL = "/api/v1/todos/1/status/"

    def setUp(self):
        super().setUp()
        self.todo_set = TodoSet.objects.create(user=self.user, title="test_todo_set")
        self.todo = Todo.objects.create(
            title="test_todo", start_date=timezone.localtime()
        )

    def test_update_todo_status(self):
        response = self.client.patch(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertNotEqual(data.pop("complete_date"), None)

        response = self.client.patch(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(data.pop("complete_date"), None)

    def test_todo_not_found(self):
        self.URL = "/api/v1/todos/2/status/"
        now = timezone.localtime()
        response = self.client.patch(self.URL, data={"complete_date": now})
        data = response.json()

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(data, {"detail": "Not found."})


class TestSubTodoView(TestAuthBase):

    URL = "/api/v1/todos/1/sub_todo/"

    def setUp(self):
        super().setUp()

        self.todo_set = TodoSet.objects.create(user=self.user, title="test_todo_set")
        self.todo = Todo.objects.create(
            title="test_todo", start_date=timezone.localtime()
        )

    def test_sub_todo_create(self):
        response = self.client.post(
            self.URL,
            data={"title": "test_sub_todo", "start_date": timezone.localtime()},
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data.pop("todo"), 1)
        self.assertEqual(data.pop("id"), 1)

    def test_todo_not_exist(self):
        self.URL = "/api/v1/todos/2/sub_todo/"
        response = self.client.post(
            self.URL,
            data={"title": "test_sub_todo", "start_date": timezone.localtime()},
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data, {"detail": "Not found."})

    def test_data_invalid(self):
        response = self.client.post(self.URL, data={"title": 1, "start_date": 1})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            data,
            {
                "start_date": [
                    "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
                ]
            },
        )


class TestSubTodoStatusView(TestAuthBase):

    URL = "/api/v1/todos/sub_todo/1/status/"

    def setUp(self):
        super().setUp()

        self.now = timezone.localtime()

        self.todo_set = TodoSet.objects.create(user=self.user, title="test_todo_set")
        self.todo = Todo.objects.create(
            title="test_todo", start_date=timezone.localtime()
        )
        self.sub_todo = SubTodo.objects.create(
            todo=self.todo, title="test_sub_todo", start_date=self.now
        )

    def test_sub_todo_update(self):
        response = self.client.put(self.URL)
        data = response.json()
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertNotEqual(data.pop("complete_date"), None)

        response = self.client.put(self.URL)
        data = response.json()
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(data.pop("complete_date"), None)

    def test_sub_todo_not_found(self):
        self.URL = "/api/v1/todos/sub_todo/2/status/"
        response = self.client.put(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data, {"detail": "Not found."})


class TestTodoSetListView(TestAuthBase):

    URL = "/api/v1/todos/set/"

    def setUp(self):
        super().setUp()

        self.todo_set = TodoSet.objects.create(user=self.user, title="test_sub_todo")

    def test_get_todo_set(self):
        response = self.client.get(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0].pop("id"), 1)

    def test_create_todo_set(self):
        response = self.client.post(self.URL, data={"title": "test_todo_set_2"})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data.pop("id"), 2)

    def test_data_invalid(self):
        response = self.client.post(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"title": ["필수 항목입니다."]})


class TestTodoSetDetailView(TestAuthBase):

    URL = "/api/v1/todos/set/1/"

    def setUp(self):
        super().setUp()

        self.todo_set = TodoSet.objects.create(user=self.user, title="test_todo_set")

    def test_update_todo_set(self):
        response = self.client.put(self.URL, data={"title": "update_test_todo_set"})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.pop("title"), "update_test_todo_set")

    def test_todo_set_not_found(self):
        self.URL = "/api/v1/todos/set/2/"

        response = self.client.put(self.URL)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data, {"detail": "Not found."})

    def test_delete_todo_set(self):
        response = self.client.delete(self.URL)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
