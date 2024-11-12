from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CalendarCreateSerializer,
    CalendarDetailSerializer,
    CalendarListSerializer,
    ScheduleCopySerializer,
    ScheduleCreateSerializer,
    ScheduleDetailSerializer,
    ScheduleListQuerySerializer,
    ScheduleListSerializer,
    ScheduleSearchQuerySerializer,
    ScheduleSearchSerializer,
    ScheduleUpdateSerializer,
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


class ScheduleCreateView(APIView):
    @extend_schema(
        summary="일정 등록",
        description="새로운 일정을 등록합니다. 이때 새 메모를 동시에 추가할 수도 있습니다.",
        request=ScheduleCreateSerializer,
        responses={201: ScheduleDetailSerializer},
        tags=["Schedules"],
    )
    def post(self, request):
        # Placeholder implementation
        return Response({"message": "Schedule created"}, status=status.HTTP_201_CREATED)


class ScheduleCopyView(APIView):
    @extend_schema(
        summary="일정 복사",
        description="schedule_id의 일정을 복사하여 새로운 일정으로 생성합니다. 이때 메모가 존재하면 메모도 함께 복사합니다.",
        request=ScheduleCopySerializer,
        responses={201: ScheduleDetailSerializer},
        tags=["Schedules"],
    )
    def post(self, request, schedule_id):
        # Placeholder implementation
        return Response(
            {"message": f"Copied schedule {schedule_id}"},
            status=status.HTTP_201_CREATED,
        )


class ScheduleListView(ListAPIView):
    @extend_schema(
        summary="일정 조회",
        description="기간 내의 일정을 조회합니다. 일간 보기, 주간 보기, 월간 보기 기능이 있으며, 날짜를 기준으로 Pagination을 지원합니다. 원하는 캘린더들을 선택하여 요청을 보낼 수 있습니다.",
        parameters=[
            # ScheduleListQuerySerializer, # TODO - Query Param Serializer
            OpenApiParameter(
                name="start_date", description="조회 시작 날짜", required=True, type=str
            ),
            OpenApiParameter(
                name="end_date", description="조회 종료 날짜", required=True, type=str
            ),
            OpenApiParameter(
                name="calendar", description="캘린더 필터링", required=False, type=str
            ),
        ],
        responses={200: ScheduleListSerializer},
        tags=["Schedules"],
    )
    def get(self, request):
        # Placeholder implementation
        return Response({"message": "List of schedules"}, status=status.HTTP_200_OK)


class ScheduleSearchView(APIView):
    @extend_schema(
        summary="일정 검색",
        description="문자열 기반 검색을 수행합니다. Calendar 필터링 옵션을 할 수 있습니다. Tag 옵션을 사용하여 지정된 태그만을 필터링 할 수 있습니다.",
        parameters=[
            # ScheduleSearchQuerySerializer, # TODO - Query Param Serializer
            OpenApiParameter(
                name="query", description="검색 문자열", required=True, type=str
            ),
            OpenApiParameter(
                name="tag", description="필터링할 태그", required=False, type=str
            ),
        ],
        responses={200: ScheduleSearchSerializer},
        tags=["Schedules"],
    )
    def get(self, request):
        # Placeholder implementation
        return Response(
            {"message": "Schedule search results"}, status=status.HTTP_200_OK
        )


class ScheduleDetailView(APIView):
    @extend_schema(
        summary="일정 상세 조회",
        description="schedule_id path param을 기준으로 일정을 조회합니다.",
        responses={200: ScheduleDetailSerializer},
        tags=["Schedules"],
    )
    def get(self, request, schedule_id):
        # Placeholder implementation
        return Response(
            {"message": f"Details for schedule {schedule_id}"},
            status=status.HTTP_200_OK,
        )


class ScheduleDeleteView(APIView):
    @extend_schema(
        summary="일정 삭제",
        description="schedule_id path param을 기준으로 일정을 삭제합니다.",
        responses={204: ScheduleDetailSerializer},
        tags=["Schedules"],
    )
    def delete(self, request, schedule_id):
        # Placeholder implementation
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScheduleUpdateView(APIView):
    @extend_schema(
        summary="일정 수정",
        description="schedule_id path param을 기준으로 일정을 수정합니다. 함께 있는 Memo는 메모 수정 API를 호출해야 합니다.",
        request=ScheduleUpdateSerializer,
        responses={200: ScheduleDetailSerializer},
        tags=["Schedules"],
    )
    def put(self, request, schedule_id):
        # Placeholder implementation
        return Response(
            {"message": f"Updated schedule {schedule_id}"}, status=status.HTTP_200_OK
        )
