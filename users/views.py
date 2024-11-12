from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import LoginSerializer, UserSerializer

from .tokens import account_activation_token


class SignUp(APIView):

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        try:
            password = request.data["password"]

        except KeyError:
            raise ParseError("Need Password")

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        user.set_password(password)
        user.save()

        # Send Email Link
        email = user.email
        domain = request.get_host()
        subject = "PLANA 계정 활성화 이메일 발송 안내"
        link = f"http://{domain}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_activation_token.make_token(user)}"
        message = (
            "계정 활성화 링크 주소입니다. \n"
            "아래 링크를 클릭하여 계정을 활성화 하세요. \n"
            f"{link}\n"
            "감사합니다."
        )

        send_mail(subject, message, "shtjddn0817@naver.com", [email])

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Login(APIView):

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]

        except KeyError:
            raise ParseError("Missing data")

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"detail": "It's not valid"}, status=status.HTTP_400_BAD_REQUEST
            )

        login(request, user)

        serializer = self.serializer_class(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class Logout(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Logout success"}, status=status.HTTP_200_OK)


class CertifiedEmail(APIView):

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get(self, request, uid64, token):
        pk = force_str(urlsafe_base64_decode(uid64))  # id값을 반환
        user = User.objects.filter(pk=pk).first()

        if user is None:
            raise NotFound

        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            return Response(
                {"detail": f"{user.email} is activated"}, status=status.HTTP_200_OK
            )

        return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)
