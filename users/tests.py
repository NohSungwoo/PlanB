from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .serializers import ProfileSerializer
from .tokens import account_activation_token


class TestSignUp(APITestCase):
    NAME = "SignUp Test"
    URL = "/api/v1/users/signup/"

    def test_sign_up(self):
        # 정상 회원 가입 요청
        response = self.client.post(
            self.URL,
            data={
                "email": "tester@test.com",
                "password": "123test",
                "nickname": "digimon",
                "gender": "male",
                "birthday": "1995-08-17",
            },
        )

        data = response.json()

        self.assertEqual(response.status_code, 201, "Status code isn't 201")
        self.assertEqual(data["email"], "tester@test.com")
        self.assertEqual(data["nickname"], "digimon")
        self.assertEqual(data["gender"], "male")
        self.assertEqual(data["birthday"], "1995-08-17")

    def test_need_password(self):
        # password 가 없는 경우
        response = self.client.post(
            self.URL,
            data={
                "email": "tester@test.com",
                "nickname": "digimon",
                "gender": "male",
                "birthday": "1995-08-17",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_serializer_data(self):
        # 데이터 형식이 정확한지 검사
        response = self.client.post(
            self.URL,
            data={
                "email": "invalid-email-format",  # 실패
                "password": "123",
                "nickname": "ash",
                "gender": "unknown",  # 실패
                "birthday": "invalid-date-format",  # 실패
            },
        )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data["email"], ["Enter a valid email address."])
        self.assertEqual(data["gender"], ['"unknown" is not a valid choice.'])
        self.assertEqual(
            data["birthday"],
            ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."],
        )

    def test_send_mail(self):
        # 메일 발송 여부 테스트
        response = self.client.post(
            self.URL,
            data={
                "email": "shtjddn0817@naver.com",
                "password": "123test",
                "nickname": "digimon",
                "gender": "male",
                "birthday": "1995-08-17",
            },
        )

        # 이메일 발송 확인
        self.assertEqual(len(mail.outbox), 1)  # 한 통의 이메일이 발송되었는지 확인
        self.assertIn(
            "shtjddn0817@naver.com", mail.outbox[0].to
        )  # 수신자가 올바른지 확인
        self.assertIn(
            "계정 활성화 링크 주소입니다.", mail.outbox[0].body
        )  # 이메일 본문 확인


class TestLogin(APITestCase):

    URL = "/api/v1/users/login/"

    def setUp(self):
        user = User.objects.create(email="tester@naver.com", birthday="1995-08-17")
        user.set_password("123123")
        user.save()

    def test_login(self):
        # 정상 로그인 요청
        response = self.client.post(
            self.URL, data={"email": "tester@naver.com", "password": "123123"}
        )
        print(response.status_code)
        data = response.json()

        self.assertEqual(
            response.status_code, status.HTTP_200_OK, {"login data invalid"}
        )
        self.assertEqual(data["email"], "tester@naver.com", "email value error")

    def test_missing_data(self):
        # 값이 누락된 경우
        response = self.client.post(self.URL, data={"email": "unknown"})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"detail": "Missing data"})

    def test_invalid_data(self):
        # 값이 잘못된 경우
        response = self.client.post(
            self.URL, data={"email": "tester", "password": "1212"}
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"detail": "It's not valid"})


class TestCertifiedEmail(APITestCase):

    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create(email="tester@naver.com", birthday="1995-08-17")
        self.user.set_password("123123")
        self.user.save()

    def test_certified_email(self):
        uid64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        url = f"/api/v1/users/certified/email/{uid64}/{token}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_is_none(self):
        # 유저가 존재하지 않는 경우
        uid64 = urlsafe_base64_encode(force_bytes(2))
        token = account_activation_token.make_token(self.user)
        url = f"/api/v1/users/certified/email/{uid64}/{token}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_token_is_invalid(self):
        # 토큰이 틀린 경우
        uid64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user).join("a")
        url = f"/api/v1/users/certified/email/{uid64}/{token}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestRequestResetPassword(APITestCase):

    URL = "/api/v1/users/request/reset/password/"

    def setUp(self):
        self.user = User.objects.create(email="tester@naver.com", birthday="1995-08-17")
        self.user.set_password("123123")
        self.user.save()

    def test_send_mail(self):
        response = self.client.post(
            self.URL,
            data={"email": self.user.email},
        )
        data = response.json()

        self.assertEqual(response.status_code, 201, "Status code isn't 201")
        self.assertEqual(data["email"], "tester@naver.com")

    def test_missing_email(self):
        # 이메일이 request data에서 누락된 경우
        response = self.client.post(self.URL, data={})
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {"detail": "Need email"})

    def test_user_not_found(self):
        # user가 존재하지 않는경우
        response = self.client.post(self.URL, data={"email": "nsw@test.com"})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data, {"detail": "Email not found"})


class TestResetPassword(APITestCase):

    URL = "/api/v1/users/reset/password/"

    def setUp(self):
        self.user = User.objects.create(email="tester@naver.com", birthday="1995-08-17")
        self.user.set_password("123123")
        self.user.save()

    def test_send_email(self):
        token = account_activation_token.make_token(self.user)
        uid64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.post(
            self.URL, data={"email": "tester@naver.com", "uid64": uid64, "token": token}
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, {"email": "tester@naver.com"})

    def test_missing_data(self):
        response = self.client.post(self.URL, data={"email": "tester@naver.com"})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"detail": "Missing request data"})

    def test_user_is_none(self):
        token = account_activation_token.make_token(self.user)
        uid64 = urlsafe_base64_encode(force_bytes(self.user.pk + 1))
        response = self.client.post(
            self.URL, data={"email": "tester@naver.com", "uid64": uid64, "token": token}
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data, {"detail": "Not found."})

    def test_link_is_valid(self):
        token = account_activation_token.make_token(self.user).join("a")
        uid64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.post(
            self.URL, data={"email": "tester@naver.com", "uid64": uid64, "token": token}
        )
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"error": "Invalid link"})


class TestProfile(APITestCase):

    URL = "/api/v1/users/profile/"

    def setUp(self):
        self.user = User.objects.create(email="tester@naver.com", birthday="1995-08-17")
        self.user.set_password("123123")
        self.user.save()

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.URL)
        data = response.json()
        serializer = ProfileSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, serializer.data, "Data is not equal")

    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            self.URL, data={"nickname": "digimon", "gender": "male"}
        )
        data = response.json()
        serializer = ProfileSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, serializer.data)

    def test_permission_denied(self):
        for method in (self.client.get, self.client.put, self.client.delete):
            response = method(self.URL)
            data = response.json()

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(
                data, {"detail": "Authentication credentials were not provided."}
            )

    def test_data_invalid(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.URL, data={"gender": 1})
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {"gender": ['"1" is not a valid choice.']})

    def test_delete_success(self):
        pk = self.user.pk
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.URL)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        user = User.objects.filter(pk=pk).first()

        self.assertIsNone(user)
