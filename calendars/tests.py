from rest_framework import reverse, status
from rest_framework.authentication import get_user_model

from calendars.models import Calendar
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
        payload = {"title": "Calendar1"} # sample calendar와 동일한 이름
        response = self.client.post(self.URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calendar.objects.count(), 1)


class TestCalendarDetail(TestAuthBase):
    URL = "/api/v1/calendars/"

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
