from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import LoginSerializer, UserSerializer


class SignUp(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            password = request.data["password"]

        except KeyError:
            raise ParseError("Need Password")

        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        user.set_password(password)
        user.save()

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
