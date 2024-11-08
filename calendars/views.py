from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CalendarCreateSerializer,
    CalendarDetailSerializer,
    CalendarListSerializer,
)


class CalendarListView(ListAPIView):
    @extend_schema(
        summary="캘린더 목록 조회",
        description="유저가 등록한 모든 캘린더를 불러옵니다.",
        responses={200: CalendarListSerializer},
        tags=["Calendars"],
    )
    def get(self, request):
        pass


class CalendarDetailView(APIView):
    @extend_schema(
        summary="캘린더 속성 조회",
        description="스케줄들을 포함하는 캘린더의 속성들을 조회합니다. Calendar: calendar_name, description, timezone, subscription_url",
        responses={200: CalendarDetailSerializer},
        tags=["Calendars"],
    )
    def get(self, request, calendar_name):
        # Placeholder implementation
        return Response(
            {"message": f"Details for calendar {calendar_name}"},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="캘린더 속성 수정",
        description="캘린더의 속성을 수정합니다.",
        request=CalendarDetailSerializer,
        responses={200: CalendarDetailSerializer},
        tags=["Calendars"],
    )
    def put(self, request, calendar_name):
        # Placeholder implementation
        return Response(
            {"message": f"Updated properties for calendar {calendar_name}"},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="캘린더 삭제",
        description="캘린더를 삭제합니다. 삭제된 캘린더의 스케줄 처리 정책은 별도의 문서에 따릅니다.",
        responses={204: None},
        tags=["Calendars"],
    )
    def delete(self, request, calendar_name):
        # Placeholder implementation
        return Response(status=status.HTTP_204_NO_CONTENT)


class CalendarCreateView(APIView):
    @extend_schema(
        summary="캘린더 생성",
        description="새 캘린더를 생성합니다.",
        request=CalendarCreateSerializer,
        responses={201: CalendarDetailSerializer},
        tags=["Calendars"],
    )
    def post(self, request):
        # Placeholder implementation
        return Response({"message": "Calendar created"}, status=status.HTTP_201_CREATED)
