from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TagDetailSerializer, TagLabelSerializer, TagTitleSerializer


class TagLabelView(APIView):
    @extend_schema(
        summary="태그 라벨링",
        description="태그를 라벨링합니다. 라벨링이란, 메모, 투두, 캘린더 아이디를 참조하는 것을 의미합니다.",
        request=TagLabelSerializer,
        responses={200: TagDetailSerializer},
        tags=["Tags"],
    )
    def post(self, request, tag_id):
        # Placeholder implementation
        return Response({"message": f"Tag {tag_id} labeled"}, status=status.HTTP_200_OK)


class TagListView(ListAPIView):
    @extend_schema(
        summary="태그 조회",
        description="유저가 생성한 모든 태그를 조회합니다.",
        responses={200: TagDetailSerializer(many=True)},
        tags=["Tags"],
    )
    def get(self, request):
        # Placeholder implementation
        return Response({"message": "List of tags"}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="태그 삭제",
        description="특정 태그를 삭제합니다.",
        responses={204: TagDetailSerializer},
        tags=["Tags"],
    )
    def delete(self, request, tag_id):
        # Placeholder implementation
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="태그 이름 변경",
        description="태그 이름을 변경합니다.",
        request=TagTitleSerializer,
        responses={200: TagDetailSerializer},
        tags=["Tags"],
    )
    def put(self, request, tag_id):
        # Placeholder implementation
        return Response({"message": f"Tag {tag_id} updated"}, status=status.HTTP_200_OK)


class TagDetailView(APIView):
    @extend_schema(
        summary="태그 디테일 조회",
        description="유저가 생성한 태그의 detail을 조회합니다.",
        responses={200: TagDetailSerializer},
        tags=["Tags"],
    )
    def get(self, request, tag_id):
        # Placeholder implementation
        return Response(
            {"message": f"Details of tag {tag_id}"}, status=status.HTTP_200_OK
        )

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
        # Placeholder implementation
        return Response({"message": "Tag created"}, status=status.HTTP_201_CREATED)
