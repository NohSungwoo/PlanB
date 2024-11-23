from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TestAuthBase(APITestCase):
    """
    유저 생성, 활성화, 인증 토큰 발급 및 HTTP 헤더에 Bearer 토큰을 추가하는 setUp을 수행합니다.
    """

    def setUp(self):
        self.user = User.objects.create(
            email="tester@test.com",
            birthday="1997-09-26",
        )
        self.user.set_password("testtest")
        self.user.is_active = True
        self.user.save()

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")