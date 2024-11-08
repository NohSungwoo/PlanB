from django.urls import path
from .views import (
    TodoCreateView,
    TodoDeleteView,
    TodoSetDeleteView,
    TodoSetDetailView,
    TodoSetListView,
    TodoSetUpdateView,
    TodoUpdateView,
    TodoListView,
    TodoDetailView,
    TodoStatusUpdateView,
    SubTodoCreateView,
    SubTodoStatusUpdateView,
    TodoSetCreateView,
)

urlpatterns = [
    path("", TodoCreateView.as_view(), name="todo-create"),
    path("", TodoListView.as_view(), name="todo-list"),
    path("<int:todo_id>", TodoDeleteView.as_view(), name="todo-delete"),
    path("<int:todo_id>", TodoUpdateView.as_view(), name="todo-update"),
    path("<int:todo_id>", TodoDetailView.as_view(), name="todo-detail"),
    path(
        "<int:todo_id>/status",
        TodoStatusUpdateView.as_view(),
        name="todo-status-update",
    ),
    path("<int:todo_id>/subtodo", SubTodoCreateView.as_view(), name="sub-todo-create"),
    path(
        "<int:todo_id>/sub_todo/<int:sub_todo_id>/status",
        SubTodoStatusUpdateView.as_view(),
        name="sub-todo-status-update",
    ),
    path("set", TodoSetCreateView.as_view(), name="todo-set-create"),
    path("set/<int:set_id>", TodoSetDeleteView.as_view(), name="todo-set-delete"),
    path("set/<int:set_id>", TodoSetUpdateView.as_view(), name="todo-set-update"),
    path("set", TodoSetListView.as_view(), name="todo-set-list"),
    path("set/<int:set_id>", TodoSetDetailView.as_view(), name="todo-set-detail"),
]
