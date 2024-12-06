import datetime
from django.core.exceptions import BadRequest, ObjectDoesNotExist
from django.db.models import F, Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from memos.models import Memo, MemoSet
from users.models import User

from .serializers import MemoDetailSerializer, MemoSetDetailSerializer


class MemoListView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = MemoDetailSerializer
    queryset = Memo.objects.select_related("memo_set")

    @extend_schema(
        summary="메모 조회",
        description="날짜와 다양한 분류,정렬 기준으로 사용자의 메모를 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="year", description="조회 연도", required=False, type=int
            ),
            OpenApiParameter(
                name="month",
                description="조회 월, year에 의존합니다.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="day",
                description="조회 일, month에 의존합니다.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="sort",
                description="정렬 옵션. created_at_asc, created_at_desc, updated_at_asc, updated_at_desc, title_asc, title_desc 중 하나를 허용합니다.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="type[]",
                description="메모 타입. 'schedule', 'todo', ''를 포함할 수 있습니다. ''는 아무 리소스에 연결되지 않은 메모임을 의미합니다. 다중인자를 허용합니다. null일 경우 필터링 없이 가져옵니다.",
                required=False,
                type=str,
                many=True,
            ),
            OpenApiParameter(
                name="memo_set[]",
                description="메모셋 id. 다중인자를 허용합니다.",
                required=False,
                type=int,
                many=True,
            ),
            OpenApiParameter(
                name="tag[]",
                description="태그 필터. 태그 이름은 고유하기 때문에 tag_title을 사용합니다. 다중인자를 허용합니다.",
                required=False,
                type=str,
                many=True,
            ),
        ],
        responses={200: MemoDetailSerializer(many=True)},
        tags=["Memos"],
    )
    def get(self, request):
        user = request.user
        queryset = self.queryset.filter(memo_set__user_id=user.id)

        param = request.query_params

        # year 없는 month는 존재하지 않고 month 없는 day는 존재하지 않는다.
        if param.get("year"):
            year = int(param.get("year"))

            if param.get("month"):
                month = int(param.get("month"))

                if param.get("day"):  # year + month + day
                    day = int(param.get("day"))
                    queryset = queryset.filter(
                        created_at__date=datetime.date(year, month, day)
                    )

                else:  # year + month
                    queryset = queryset.filter(
                        created_at__year=year, created_at__month=month
                    )

            else:  # year
                queryset = queryset.filter(created_at__year=year)

        # `type` filtering
        if param.get("type[]") is not None:
            types = set(param.getlist("type[]"))
            excluded_types = {"todo", "schedule", ""} - types

            q = Q()
            for e in excluded_types:
                # 여기서 e는 걸러질 타입을 의미한다!
                match e:
                    case "todo":
                        q &= Q(memo_todo__isnull=True)
                    case "schedule":
                        q &= Q(memo_schedule__isnull=True)
                    case "":
                        q &= Q(memo_todo__isnull=False) | Q(memo_schedule__isnull=False)

            queryset = queryset.filter(q)
            del q

        # `memo_set` filtering
        try:
            if param.get("memo_set[]"):
                memo_sets = map(int, param.getlist("memo_set[]"))
                q = Q()
                for i in memo_sets:
                    q |= Q(memo_set_id=i)

                queryset = queryset.filter(q)
                del q
        except ValueError:
            return Response(
                "memo_set[] query parameter가 유효하지 않습니다.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # `tag` filtering
        if param.get("tag[]"):
            tags = param.getlist("tag[]")
            q = Q()
            for tag_title in tags:
                q |= Q(memo_tags__title=tag_title)

            queryset = queryset.filter(q)
            del q

        # `sort` created_at_asc, created_at_desc, updated_at_asc, updated_at_desc, title_asc, title_desc
        match param.get("sort"):
            case "created_at_asc":
                queryset = queryset.order_by("created_at")
            case "created_at_desc":
                queryset = queryset.order_by("-created_at")
            case "updated_at_asc":
                queryset = queryset.order_by("updated_at")
            case "updated_at_desc":
                queryset = queryset.order_by("-updated_at")
            case "title_asc":
                queryset = queryset.order_by("title")
            case "title_desc":
                queryset = queryset.order_by("-title")

        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="메모 등록",
        description="새로운 메모를 등록합니다. \
                등록시 MemoSet을 지정할 수 있습니다.",
        request=MemoDetailSerializer,
        responses={201: MemoDetailSerializer},
        tags=["Memos"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MemoDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MemoDetailSerializer
    queryset = Memo.objects.select_related("memo_set")

    @extend_schema(
        summary="메모 디테일 조회",
        description="특정 메모의 세부 정보를 조회합니다.",
        responses={200: MemoDetailSerializer},
        tags=["Memos"],
    )
    def get(self, request, memo_id):
        memo: Memo = self.queryset.get(pk=memo_id)
        if not memo:
            return Response(
                {"message": "memo not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(instance=memo)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="메모 수정",
        description="기존 메모의 내용을 수정합니다. 메모의 내용과 타입, 메모셋의 위치를 변경할 수 있습니다. (Whole Update)",
        request=MemoDetailSerializer,
        responses={200: MemoDetailSerializer},
        tags=["Memos"],
    )
    def put(self, request, memo_id):
        try:
            memo: Memo = self.queryset.get(pk=memo_id)

            serializer = self.serializer_class(
                memo,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)

            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"message": "memo not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError:
            return Response(
                {"message": "request is not valid 💀"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="메모 삭제",
        description="특정 메모를 삭제합니다.",
        responses={204: MemoDetailSerializer},
        tags=["Memos"],
    )
    def delete(self, request, memo_id):
        memo: Memo = self.queryset.get(pk=memo_id)

        if not memo:
            return Response({"message": "memo not found"}, status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=memo)

        memo.delete()

        # Placeholder implementation
        return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)


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
