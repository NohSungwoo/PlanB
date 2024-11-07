from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserSerializer


class SignUp(APIView):
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
