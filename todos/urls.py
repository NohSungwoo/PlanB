from django.urls import path

from .views import (
    SubTodoCreateView,
    SubTodoStatusUpdateView,
    TodoDetailView,
    TodoListView,
    TodoSetDetailView,
    TodoSetListView,
    TodoStatusUpdateView,
)

todo_urls = [
    path("", TodoListView.as_view(), name="todo-list"),
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
]

todoset_urls = [
    path("set", TodoSetListView.as_view(), name="todo-set-list"),
    path("set/<int:set_id>", TodoSetDetailView.as_view(), name="todo-set-detail"),
]

urlpatterns = todo_urls + todoset_urls
