from datetime import date, datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from calendars.models import Calendar, Schedule

from .serializers import (
    CalendarDetailSerializer,
    ScheduleDetailSerializer,
    ScheduleViewChoices,
    ScheduleUpdateSerializer,
)


class CalendarListView(APIView):
    """
    캘린더들에 대한 작업을 처리합니다. 모든 캘린더를 조회하거나 새 캘린더를 추가합니다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CalendarDetailSerializer
    queryset = Calendar.objects.all()

    @extend_schema(
        summary="캘린더 목록 조회",
        description="유저가 등록한 모든 캘린더를 불러옵니다.",
        responses={200: CalendarDetailSerializer(many=True)},
        tags=["Calendars"],
    )
    def get(self, request):
        queryset = self.queryset.filter(user=request.user)
        serializer = self.serializer_class(instance=queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="캘린더 생성",
        description="새 캘린더를 생성합니다.",
        request=CalendarDetailSerializer,
        responses={201: CalendarDetailSerializer},
        tags=["Calendars"],
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CalendarDetailView(APIView):
    """
    캘린더 하나에 대한 작업을 처리합니다. 속성을 조회할 수 있으며, 업데이트, 삭제가 가능합니다.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CalendarDetailSerializer
    queryset = Calendar.objects.all()

    @extend_schema(
        summary="캘린더 속성 조회",
        description="스케줄들을 포함하는 캘린더의 속성들을 조회합니다. \
            Calendar: calendar_name, description, timezone, subscription_url",
        responses={200: CalendarDetailSerializer},
        tags=["Calendars"],
    )
    def get(self, request, calendar_name):
        try:
            instance = self.queryset.get(user=request.user, title=calendar_name)

            serializer = self.serializer_class(instance=instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise NotFound(detail={"message": "해당 캘린더가 존재하지 않습니다."})

    @extend_schema(
        summary="캘린더 속성 수정",
        description="캘린더의 속성을 수정합니다. Whole update",
        request=CalendarDetailSerializer,
        responses={200: CalendarDetailSerializer},
        tags=["Calendars"],
    )
    def put(self, request, calendar_name):
        try:
            instance = self.queryset.get(user=request.user, title=calendar_name)

            serializer = self.serializer_class(
                instance=instance,
                data=request.data,
                partial=False,
                context={"request": request},
            )

            if not serializer.is_valid():
                raise ValidationError(serializer.errors)

            updated_instance = serializer.save()
            serializer = self.serializer_class(updated_instance)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            raise NotFound(detail={"message": "캘린더가 존재하지 않습니다."})

    @extend_schema(
        summary="캘린더 삭제",
        description="캘린더를 삭제합니다. 삭제된 캘린더의 스케줄 처리 정책은 별도의 문서에 따릅니다.",
        responses={204: None},
        tags=["Calendars"],
    )
    def delete(self, request, calendar_name):
        try:
            instance = self.queryset.get(user=request.user, title=calendar_name)

            serializer = self.serializer_class(instance=instance)
            instance.delete()

            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            raise NotFound(detail={"message": "캘린더가 존재하지 않습니다."})


class ScheduleCopyView(APIView):
    @extend_schema(
        summary="일정 복사",
        description="schedule_id의 일정을 복사하여 새로운 일정으로 생성합니다. 이때 메모가 존재하면 메모도 함께 복사합니다.",
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
    permission_classes = [IsAuthenticated]
    serializer_class = ScheduleDetailSerializer
    queryset = Schedule.objects.select_related("calendar")
    pagination_class = PageNumberPagination

    @extend_schema(
        summary="일정 조회",
        description="기간 내의 일정을 조회합니다. 일간 보기, 주간 보기, 월간 보기 기능이 있으며, 날짜를 기준으로 Pagination을 지원합니다. 원하는 캘린더들을 선택하여 요청을 보낼 수 있습니다.",
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="조회 시작 날짜",
                required=True,
                type=date,
            ),
            OpenApiParameter(
                name="view",
                description="뷰 타입으로, 일간(daily), 주간(weekly) 혹은 월간(monthly)으로 세팅합니다. 기본값은 월간입니다.",
                required=False,
                type=ScheduleViewChoices,
            ),
            OpenApiParameter(
                name="page",
                description="페이지 번호를 입력합니다. 1부터 세며, 기본값은 1입니다. 0보다 큰 정수를 허용합니다.",
                required=False,
                type=int,
                default=1,
            ),
            OpenApiParameter(
                name="calendar[]",
                description="캘린더 필터링, 다중인자를 허용합니다.",
                required=False,
                type=str,
            ),
        ],
        responses={200: ScheduleDetailSerializer(many=True)},
        tags=["Schedules"],
    )
    def get(self, request):
        user = request.user
        queryset = self.queryset.filter(calendar__user_id=user.id)

        param = request.query_params

        # `start_date` 필터링
        if not param.get("start_date"):
            raise ValidationError("start_date is required")
        start_date = datetime.fromisoformat(param["start_date"])
        queryset = queryset.filter(start_date__gte=start_date)

        # `calendar[]` 필터링
        if param.get("calendar[]") is not None:
            calendars = set(param.getlist("calendar[]"))
            queryset = queryset.filter(calendar__title__in=calendars)

        # `view` 필터링
        if param.get("view"):
            match param.get("view"):
                case "monthly":
                    queryset = queryset.filter(
                        start_date__month__lt=start_date.month + 1
                    )
                case "weekly":
                    queryset = queryset.filter(
                        start_date__lt=start_date + timedelta(days=7)
                    )
                case "daily":
                    queryset = queryset.filter(
                        start_date__lt=start_date + timedelta(days=1)
                    )

        # `page` 필터링
        queryset = self.pagination_class().paginate_queryset(
            queryset, request, view=self
        )

        serializer = self.serializer_class(instance=queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="일정 등록",
        description="새로운 일정을 등록합니다. 이때 새 메모를 동시에 추가할 수도 있습니다.",
        request=ScheduleDetailSerializer,
        responses={201: ScheduleDetailSerializer},
        tags=["Schedules"],
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ScheduleSearchView(APIView):
    @extend_schema(
        summary="일정 검색",
        description="문자열 기반 검색을 수행합니다. \
            Calendar 필터링 옵션을 할 수 있습니다. Tag 옵션을 \
            사용하여 지정된 태그만을 필터링 할 수 있습니다.",
        parameters=[
            OpenApiParameter(
                name="query", description="검색 문자열", required=True, type=str
            ),
            OpenApiParameter(
                name="tag",
                description="포함할 태그, ','로 구분",
                required=False,
                type=str,
            ),
        ],
        responses={200: ScheduleDetailSerializer(many=True)},
        tags=["Schedules"],
    )
    def get(self, request):
        # Placeholder implementation
        return Response(
            {"message": "Schedule search results"}, status=status.HTTP_200_OK
        )


class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScheduleDetailSerializer
    queryset = Schedule.objects.select_related("calendar")

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

    @extend_schema(
        summary="일정 삭제",
        description="schedule_id path param을 기준으로 일정을 삭제합니다.",
        responses={204: ScheduleDetailSerializer},
        tags=["Schedules"],
    )
    def delete(self, request, schedule_id):
        instance = self.queryset.get(pk=schedule_id)
        serializer = self.serializer_class(instance=instance)
        instance.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="일정 수정",
        description="schedule_id path param을 기준으로 일정을 수정합니다. 함께 있는 Memo는 메모 수정 API를 호출해야 합니다.",
        request=ScheduleUpdateSerializer,
        responses={200: ScheduleDetailSerializer},
        tags=["Schedules"],
    )
    def put(self, request, schedule_id):
        instance = self.queryset.get(pk=schedule_id)
        serializer = self.serializer_class(instance, data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)
