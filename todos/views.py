from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SubTodo, Todo, TodoSet
from .serializers import (
    SubTodoDetailSerializer,
    TodoDetailSerializer,
    TodoSetDetailSerializer,
)


class TodoListView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TodoDetailSerializer

    @extend_schema(
        summary="Todo 조회",
        description="사용자의 Todo 항목을 조회합니다. 이때 todo_set_id와 complete_date, tag를 통해 필터링 할 수 있습니다.",
        parameters=[
            OpenApiParameter(
                name="todo_set_id",
                description="필터링 할 Todo Set ID",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="complete_date", description="완료 날짜", required=False, type=str
            ),
            OpenApiParameter(
                name="tag", description="태그 필터", required=False, type=str
            ),
        ],
        responses={200: TodoDetailSerializer(many=True)},
        tags=["Todos"],
    )
    def get(self, request):
        todo_set_pk = request.GET.get("todo_set_id", None)
        complete_date = request.GET.get("todo_set_id", None)
        tag = request.GET.get("tag", None)

        if todo_set_pk:
            todo = Todo.objects.filter(todo_set_pk=todo_set_pk)
        else:
            todo = Todo.objects.all()

        if complete_date:
            todo = todo.filter(complete_date=complete_date)

        if tag:
            todo = todo.filter(tag=tag)

        serializer = self.serializer_class(todo, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Todo 등록",
        description="새로운 Todo 항목을 생성합니다. 이때 todo_set을 지정해야합니다. 지정하지 않으면 default TodoSet으로 할당됩니다.",
        request=TodoDetailSerializer,
        responses={201: TodoDetailSerializer},
        tags=["Todos"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        todo = serializer.save(user=request.user)

        serializer = self.serializer_class(todo)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TodoDetailView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TodoDetailSerializer

    def get_object(self, todo_id):
        try:
            todo = Todo.objects.get(pk=todo_id)

        except Todo.DoesNotExist:
            raise NotFound

        return todo

    @extend_schema(
        summary="Todo Detail 조회",
        description="사용자의 Todo Detail 항목을 조회합니다.",
        responses={200: TodoDetailSerializer},
        tags=["Todos"],
    )
    def get(self, request, todo_id):
        todo = self.get_object(todo_id)

        serializer = self.serializer_class(todo)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Todo 삭제",
        description="todoId를 기준으로 Todo를 삭제합니다.",
        responses={204: TodoDetailSerializer},
        tags=["Todos"],
    )
    def delete(self, request, todo_id):
        todo = self.get_object(todo_id)

        todo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Todo 수정",
        description="todoId를 기준으로 세부 내용을 수정합니다.",
        request=TodoDetailSerializer,
        responses={200: TodoDetailSerializer},
        tags=["Todos"],
    )
    def put(self, request, todo_id):
        todo = self.get_object(todo_id)
        serializer = self.serializer_class(todo, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        todo = serializer.save()

        serializer = self.serializer_class(todo)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TodoStatusUpdateView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TodoDetailSerializer

    @extend_schema(
        summary="Todo 상태 변경",
        description="특정 Todo항목의 상태를 변경합니다. \
            PATCH 메서드이기 때문에 멱등성이 성립하지 않습니다. \
            같은 요청을 보낼 때마다 status가 on-off 사이를 왔다갔다 합니다. \
            하위 태스크 영향 관련 결정은 노션 문서를 참고하세요.",
        responses={200: TodoDetailSerializer},
        tags=["Todos"],
    )
    def patch(self, request, todo_id):
        try:
            todo = Todo.objects.get(pk=todo_id)

        except Todo.DoesNotExist:
            raise NotFound

        if todo.complete_date:
            todo.complete_date = None
            todo.save()
        else:
            todo.complete_date = timezone.localtime()
            todo.save()

        serializer = self.serializer_class(todo)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SubTodoView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = SubTodoDetailSerializer

    @extend_schema(
        summary="Todo 하위 태스크 등록",
        description="특정 Todo항목에 하위 태스크를 추가합니다.",
        request=SubTodoDetailSerializer,
        responses={201: SubTodoDetailSerializer},
        tags=["Todos"],
    )
    def post(self, request, todo_id):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sub_todo = serializer.save(todo_id=todo_id)

        serializer = self.serializer_class(sub_todo)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class SubTodoStatusView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = SubTodoDetailSerializer

    @extend_schema(
        summary="Todo 하위 태스크 상태 변경",
        description="특정 Todo항목의 상태를 변경합니다. \
            PATCH 메서드이기 때문에 멱등성이 성립하지 않습니다. \
            같은 요청을 보낼 때마다 status가 on-off 사이를 왔다갔다 합니다. \
            하위 태스크 영향 관련 결정은 노션 문서를 참고하세요.",
        responses={200: SubTodoDetailSerializer},
        tags=["Todos"],
    )
    def put(self, request, sub_todo_id):
        try:
            sub_todo = SubTodo.objects.get(pk=sub_todo_id)

        except SubTodo.DoesNotExist:
            raise NotFound

        if sub_todo.complete_date:
            sub_todo.complete_date = None
            sub_todo.save()
        else:
            sub_todo.complete_date = timezone.localtime()
            sub_todo.save()

        serializer = self.serializer_class(sub_todo)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class TodoSetListView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TodoSetDetailSerializer

    @extend_schema(
        summary="투두셋 조회",
        description="투두셋을 조회합니다.",
        responses={200: TodoSetDetailSerializer(many=True)},
        tags=["TodoSets"],
    )
    def get(self, request):
        todo_set = TodoSet.objects.all()

        serializer = self.serializer_class(todo_set, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="투두셋 추가",
        description="새로운 투두셋을 생성합니다.",
        request=TodoSetDetailSerializer,
        responses={201: TodoSetDetailSerializer},
        tags=["TodoSets"],
    )
    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        todo_set = serializer.save(user=user)

        serializer = self.serializer_class(todo_set)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TodoSetDetailView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TodoSetDetailSerializer

    def get_object(self, set_id):
        try:
            todo_set = TodoSet.objects.get(pk=set_id)

        except TodoSet.DoesNotExist:
            raise NotFound

        return todo_set

    @extend_schema(
        summary="투두셋 디테일 조회",
        description="특정 투두셋의 세부 정보를 조회합니다.",
        responses={200: TodoSetDetailSerializer},
        tags=["TodoSets"],
    )
    def get(self, request, set_id):
        todo_set = self.get_object(set_id)

        serializer = self.serializer_class(todo_set)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="투두셋 수정",
        description="투두셋을 수정합니다.",
        request=TodoSetDetailSerializer,
        responses={200: TodoSetDetailSerializer},
        tags=["TodoSets"],
    )
    def put(self, request, set_id):
        todo_set = self.get_object(set_id)

        serializer = self.serializer_class(todo_set, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        todo_set = serializer.save()

        serializer = self.serializer_class(todo_set)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="투두셋 삭제",
        description="투두셋을 삭제합니다. Set 삭제시 하위 원소처리 관련 정책 적용",
        responses={204: None},
        tags=["TodoSets"],
    )
    def delete(self, request, set_id):
        todo_set = self.get_object(set_id)

        todo_set.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
