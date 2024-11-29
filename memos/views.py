from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from memos.models import Memo, MemoSet

from .serializers import MemoDetailSerializer, MemoSetDetailSerializer


class MemoListView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = MemoDetailSerializer
    queryset = Memo.objects.all()

    @extend_schema(
        summary="메모 조회",
        description="날짜와 분류 기준으로 메모를 조회합니다. 연도, 월, 일 단위로 조회할 수 있으며, \
            정렬옵션도 설정할 수 있습니다. View 옵션을 통해 타입, 조회기간, 메모셋을 필터링 할 수 있습니다.",
        parameters=[
            OpenApiParameter(
                name="year", description="조회 연도", required=False, type=int
            ),
            OpenApiParameter(
                name="month", description="조회 월", required=False, type=int
            ),
            OpenApiParameter(
                name="day", description="조회 일", required=False, type=int
            ),
            OpenApiParameter(
                name="sort", description="정렬 옵션", required=False, type=str
            ),
            OpenApiParameter(
                name="type", description="메모 타입", required=False, type=str
            ),
            OpenApiParameter(
                name="memo_set",
                description="메모셋 필터, CSV",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="tag", description="태그 필터, CSV", required=False, type=str
            ),
        ],
        responses={200: MemoDetailSerializer(many=True)},
        tags=["Memos"],
    )
    def get(self, request):
        user = request.user
        queryset = self.queryset.filter(memo_set__user_id=user.id)

        # Placeholder implementation
        return Response({"message": "List of memos"}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="메모 등록",
        description="새로운 메모를 등록합니다. \
                등록시 메모타입 (일반, 캘린더, Todo)를 지정할 수 있습니다. \
                등록시 MemoSet을 지정할 수 있습니다.",
        request=MemoDetailSerializer,
        responses={201: MemoDetailSerializer},
        tags=["Memos"],
    )
    def post(self, request):
        # TODO - schedule, todo 연결 테스트 필요
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MemoDetailView(APIView):
    @extend_schema(
        summary="메모 디테일 조회",
        description="특정 메모의 세부 정보를 조회합니다.",
        responses={200: MemoDetailSerializer},
        tags=["Memos"],
    )
    def get(self, request, memo_id):
        # Placeholder implementation
        return Response(
            {"message": f"Details of memo {memo_id}"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="메모 수정",
        description="기존 메모의 내용을 수정합니다. 메모의 내용과 타입, 메모셋의 위치를 변경할 수 있습니다.",
        request=MemoDetailSerializer,
        responses={200: MemoDetailSerializer},
        tags=["Memos"],
    )
    def put(self, request, memo_id):
        # Placeholder implementation
        return Response(
            {"message": f"Memo {memo_id} updated"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="메모 삭제",
        description="특정 메모를 삭제합니다.",
        responses={204: MemoDetailSerializer},
        tags=["Memos"],
    )
    def delete(self, request, memo_id):
        # Placeholder implementation
        return Response(status=status.HTTP_204_NO_CONTENT)


class MemoSetListView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = MemoSetDetailSerializer
    queryset = MemoSet.objects.all()

    @extend_schema(
        summary="메모셋 조회",
        description="메모셋을 조회합니다.",
        responses={200: MemoSetDetailSerializer(many=True)},
        tags=["MemoSets"],
    )
    def get(self, request):
        queryset = self.queryset.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="메모셋 추가",
        description="새로운 메모셋을 생성합니다.",
        request=MemoSetDetailSerializer,
        responses={201: MemoSetDetailSerializer},
        tags=["MemoSets"],
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MemoSetDetailView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = MemoSetDetailSerializer
    queryset = MemoSet.objects.all()

    @extend_schema(
        summary="메모셋 디테일 조회",
        description="메모셋의 세부 정보를 조회합니다.",
        responses={200: MemoSetDetailSerializer},
        tags=["MemoSets"],
    )
    def get(self, request, set_id):
        queryset = self.queryset.filter(user=request.user, id=set_id)
        if not queryset.exists():
            raise NotFound(detail="해당 메모셋이 존재하지 않습니다.")

        serializer = self.serializer_class(queryset.first())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="메모셋 삭제",
        description="메모셋을 삭제합니다. Set 삭제시 하위 원소처리 관련 정책 적용",
        responses={204: MemoSetDetailSerializer},
        tags=["MemoSets"],
    )
    def delete(self, request, set_id):
        queryset = self.queryset.filter(user=request.user, id=set_id)
        if not queryset.exists():
            raise NotFound(detail="해당 메모셋이 존재하지 않습니다.")

        found = queryset.first()
        found.delete()

        serializer = self.serializer_class(found)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="메모셋 수정",
        description="메모셋을 수정합니다.",
        request=MemoSetDetailSerializer,
        responses={200: MemoSetDetailSerializer},
        tags=["MemoSets"],
    )
    def put(self, request, set_id):
        instance = self.queryset.get(user=request.user, id=set_id)
        if not instance:
            raise NotFound(detail="해당 메모셋이 존재하지 않습니다.")

        serializer = self.serializer_class(
            instance, data=request.data, partial=True, context={"request": request}
        )

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        updated_instance = serializer.save()
        serializer = self.serializer_class(updated_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
