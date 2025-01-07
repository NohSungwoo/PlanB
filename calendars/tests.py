from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.authentication import get_user_model
from rest_framework.reverse import reverse

from calendars.models import Calendar, Schedule
from memos.models import Memo, MemoSet
from tests.auth_base_test import TestAuthBase


User = get_user_model()


class TestCalendarList(TestAuthBase):
    URL = "/api/v1/calendars/"

    def setUp(self):
        super().setUp()

        # create a sample Calendar for testing
        self.calendar = Calendar.objects.create(user=self.user, title="Calendar1")

    def test_get_calendars(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Calendar1")

    def test_create_calendar(self):
        payload = {"title": "Calendar2"}
        response = self.client.post(self.URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Calendar.objects.count(), 2)
        self.assertEqual(Calendar.objects.last().title, "Calendar2")

    def test_create_calendar_invalid(self):
        payload = {}  # 타이틀 누락
        response = self.client.post(self.URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calendar.objects.count(), 1)

    def test_create_calendar_duplicated(self):
        payload = {"title": "Calendar1"}  # sample calendar와 동일한 이름
        response = self.client.post(self.URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calendar.objects.count(), 1)


class TestCalendarDetail(TestAuthBase):
    URL = "/api/v1/calendars/name/"

    def setUp(self):
        super().setUp()

        # create a sample Calendar for testing
        self.calendar = Calendar.objects.create(user=self.user, title="Calendar1")

        self.url = f"{self.URL}{self.calendar.title}/"

    def test_get_calendar_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Calendar1")

    def test_get_calendar_not_found(self):
        url = f"{self.URL}NonExistentCalendar/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("message", response.data)

    def test_update_calendar(self):
        payload = {"title": "UpdatedCalendar"}
        response = self.client.put(self.url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.calendar.refresh_from_db()
        self.assertEqual(self.calendar.title, "UpdatedCalendar")

    def test_update_calendar_bad_request(self):
        payload = {}  # 타이틀 누락
        response = self.client.put(self.url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_calendar(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Calendar.objects.filter(id=self.calendar.id).exists())


class TestScheduleList(TestAuthBase):
    URL = "/api/v1/calendars/schedule/"

    def setUp(self):
        super().setUp()

        self.calendar1 = Calendar.objects.create(user=self.user, title="Work")
        self.calendar2 = Calendar.objects.create(user=self.user, title="Personal")
        self.schedule1 = Schedule.objects.create(
            calendar=self.calendar1,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(hours=1),
            title="Meeting",
        )
        self.schedule2 = Schedule.objects.create(
            calendar=self.calendar2,
            start_date=datetime.now() + timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1, hours=1),
            title="Gym",
        )
        self.url = reverse("schedule-list")

    def test_get_sample_schedule(self):
        response = self.client.get(
            self.URL, query_params={"start_date": self.schedule1.start_date}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], self.schedule1.title)

    def test_create_schedule_without_memo(self):
        payload = {
            "calendar": self.calendar1.pk,
            "title": "schedule1",
            "start_date": "9999-12-31",
        }
        response = self.client.post(self.URL, data=payload)
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, response.content
        )
        for key in payload.keys():
            self.assertIn(key, response.data)

    def test_get_without_start_date(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_with_start_date(self):
        response = self.client.get(self.url, {"start_date": datetime.now().isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_with_start_date_and_calendar(self):
        response = self.client.get(
            self.url,
            {
                "start_date": datetime.now().isoformat(),
                "calendar[]": [self.calendar1.title],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_with_start_date_and_view_monthly(self):
        response = self.client.get(
            self.url, {"start_date": datetime.now().isoformat(), "view": "monthly"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_with_start_date_and_view_weekly(self):
        response = self.client.get(
            self.url, {"start_date": datetime.now().isoformat(), "view": "weekly"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_with_start_date_and_view_daily(self):
        response = self.client.get(
            self.url, {"start_date": datetime.now().isoformat(), "view": "daily"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class TestScheduleDetail(TestAuthBase):
    pass


class TestScheduleListPagination(TestAuthBase):
    URL = "/api/v1/calendars/schedule/"

    def setUp(self):
        super().setUp()

        self.calendar1 = Calendar.objects.create(user=self.user, title="Work")
        self.calendar2 = Calendar.objects.create(user=self.user, title="Personal")
        self.schedules = [
            Schedule.objects.create(
                calendar=self.calendar1,
                start_date=datetime.now() + timedelta(days=i),
                end_date=datetime.now() + timedelta(days=i, hours=1),
                title=f"Meeting {i}",
            )
            for i in range(15)
        ]
        self.url = reverse("schedule-list")

    def test_get_schedules_with_pagination(self):
        response = self.client.get(
            self.url, {"start_date": datetime.now().isoformat(), "page": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_get_schedules_with_pagination_second_page(self):
        response = self.client.get(
            self.url, {"start_date": datetime.now().isoformat(), "page": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_get_schedules_with_pagination_invalid_page(self):
        response = self.client.get(
            self.url, {"start_date": datetime.now().isoformat(), "page": 3}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestCopySchedule(TestAuthBase):
    URL = "/api/v1/calendars/schedule/"

    def setUp(self):
        super().setUp()

        self.memo_set = MemoSet.objects.create(user=self.user, title="MemoSet")
        self.memo = Memo.objects.create(memo_set=self.memo_set, text="Memo")
        self.calendar = Calendar.objects.create(user=self.user, title="Test Calendar")
        self.schedule = Schedule.objects.create(
            calendar=self.calendar,
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            title="Original Schedule",
            memo=self.memo,
        )
        self.copy_url = f"{self.URL}{self.schedule.pk}/copy/"

    def test_copy_schedule(self):
        response = self.client.post(self.copy_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Schedule.objects.count(), 2)

        copied_schedule = Schedule.objects.select_related("memo").latest("id")

        self.assertNotEqual(copied_schedule.id, self.schedule.id)
        self.assertEqual(copied_schedule.title, self.schedule.title)
        self.assertEqual(copied_schedule.start_date, self.schedule.start_date)
        self.assertEqual(copied_schedule.end_date, self.schedule.end_date)
        self.assertNotEqual(copied_schedule.memo.pk, self.schedule.memo.pk)

    def test_copy_nonexistent_schedule(self):
        non_existent_url = f"{self.URL}99999/copy/"
        response = self.client.post(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("message", response.data)
