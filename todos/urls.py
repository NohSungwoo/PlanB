from django.urls import path

from .views import (
    SubTodoStatusView,
    SubTodoView,
    TodoDetailView,
    TodoListView,
    TodoSetDetailView,
    TodoSetListView,
    TodoStatusUpdateView,
)

todo_urls = [
    path("", TodoListView.as_view(), name="todo-list"),
    path("<int:todo_id>/", TodoDetailView.as_view(), name="todo-detail"),
    path(
        "<int:todo_id>/status/",
        TodoStatusUpdateView.as_view(),
        name="todo-status-update",
    ),
    path("<int:todo_id>/sub_todo/", SubTodoView.as_view(), name="sub-todo-create"),
    path(
        "sub_todo/<int:sub_todo_id>/status/",
        SubTodoStatusView.as_view(),
        name="sub-todo-status-update",
    ),
]

todo_set_urls = [
    path("set/", TodoSetListView.as_view(), name="todo-set-list"),
    path("set/<int:set_id>/", TodoSetDetailView.as_view(), name="todo-set-detail"),
]

urlpatterns = todo_urls + todo_set_urls
