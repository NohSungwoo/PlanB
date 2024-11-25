from drf_spectacular.utils import OpenApiParameter as P
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Tag
from .serializers import TagDetailSerializer, TagLabelSerializer, TagTitleSerializer


class TagLabelView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TagLabelSerializer

    def get_objcet(self, tag_id):
        try:
            tag = Tag.objects.get(pk=tag_id)

        except Tag.DoesNotExist:
            raise NotFound

        return tag

    @extend_schema(
        summary="태그 라벨 추가",
        description="태그를 라벨링을 합니다. 라벨링이란, 메모, 투두, 캘린더 아이디를 참조하는 것을 의미합니다.",
        request=TagLabelSerializer,
        responses={200: TagDetailSerializer},
        tags=["Tags"],
    )
    def post(self, request, tag_id):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tag = self.get_objcet(tag_id)

        schedule_pk = request.data.get("schedule_id")
        todo_pk = request.data.get("todo_id")
        memo_pk = request.data.get("memo_id")

        if schedule_pk:
            tag.schedule.add(schedule_pk)

        elif todo_pk:
            tag.todo.add(todo_pk)

        else:
            tag.memo.add(memo_pk)

        tag.save()

        serializer = TagDetailSerializer(tag)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="태그 라벨 제거",
        description="태그 라벨을 제거합니다. 이때 Query Param으로 제거할 엔티티 ID를 명시해야 합니다.\
            만일 제시한 ID가 현재 태그 라벨에 연관되지 않는다면 404 Not found를 반환합니다.",
        parameters=[
            P("schedule", type=OpenApiTypes.INT, location=P.QUERY),
            P("memo", type=OpenApiTypes.INT, location=P.QUERY),
            P("todo", type=OpenApiTypes.INT, location=P.QUERY),
        ],
        responses={204: TagDetailSerializer},
        tags=["Tags"],
    )
    def delete(self, request, tag_id):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tag = self.get_objcet(tag_id)

        schedule_pk = request.data.get("schedule_id")
        todo_pk = request.data.get("todo_id")
        memo_pk = request.data.get("memo_id")

        if schedule_pk:
            tag.schedule.remove(schedule_pk)

        elif todo_pk:
            tag.todo.remove(todo_pk)

        else:
            tag.memo.remove(memo_pk)

        serializer = TagDetailSerializer(tag)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TagListView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TagDetailSerializer

    @extend_schema(
        summary="태그 조회",
        description="유저가 생성한 모든 태그를 조회합니다.",
        responses={200: TagDetailSerializer(many=True)},
        tags=["Tags"],
    )
    def get(self, request):
        user = request.user

        tags = Tag.objects.filter(user=user)

        serializer = self.serializer_class(tags, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="태그 추가",
        description="새로운 태그를 생성하여 메모, 투두, 캘린더 항목에 사용할 수 있도록 합니다.\
                태그 생성은 단순히 title을 사용하여 생성이 가능하며, 다른 엔티티와 연결하기 \
                위해서 **태그 라벨링**을 요청해야 합니다.",
        request=TagTitleSerializer,
        responses={201: TagDetailSerializer},
        tags=["Tags"],
    )
    def post(self, request):
        try:
            user_pk = request.user.pk
            title = request.data["title"]

        except KeyError:
            raise ParseError("Need title data")

        serializer = self.serializer_class(data={"user": user_pk, "title": title})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tag = serializer.save()

        serializer = self.serializer_class(tag)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagDetailView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TagDetailSerializer

    def get_object(self, tag_id):
        try:
            tag = Tag.objects.get(pk=tag_id)

        except Tag.DoesNotExist:
            raise NotFound

        return tag

    @extend_schema(
        summary="태그 디테일 조회",
        description="유저가 생성한 태그의 detail을 조회합니다.",
        responses={200: TagDetailSerializer},
        tags=["Tags"],
    )
    def get(self, request, tag_id):
        tag = self.get_object(tag_id)

        serializer = self.serializer_class(tag)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="태그 이름 변경",
        description="태그 이름을 변경합니다.",
        request=TagTitleSerializer,
        responses={200: TagDetailSerializer},
        tags=["Tags"],
    )
    def put(self, request, tag_id):
        tag = self.get_object(tag_id)

        serializer = self.serializer_class(tag, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tag = serializer.save()

        serializer = self.serializer_class(tag)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="태그 삭제",
        description="특정 태그를 삭제합니다.",
        responses={204: TagDetailSerializer},
        tags=["Tags"],
    )
    def delete(self, request, tag_id):
        tag = self.get_object(tag_id)

        tag.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
