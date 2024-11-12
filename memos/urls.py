from django.urls import path

from .views import (
    MemoCreateView,
    MemoDeleteView,
    MemoDetailView,
    MemoListView,
    MemoSetCreateView,
    MemoSetDeleteView,
    MemoSetDetailView,
    MemoSetListView,
    MemoSetUpdateView,
    MemoUpdateView,
)

urlpatterns = [
    ### Memo
    path("", MemoCreateView.as_view(), name="memo-create"),
    path("", MemoListView.as_view(), name="memo-list"),
    path("<int:memo_id>", MemoDetailView.as_view(), name="memo-detail"),
    path("<int:memo_id>", MemoUpdateView.as_view(), name="memo-update"),
    path("<int:memo_id>", MemoDeleteView.as_view(), name="memo-delete"),
    ### Memoset
    path("set", MemoSetCreateView.as_view(), name="memoset-create"),
    path("set", MemoSetListView.as_view(), name="memoset-list"),
    path("set/<int:set_id>", MemoSetDetailView.as_view(), name="memoset-detail"),
    path("set/<int:set_id>", MemoSetUpdateView.as_view(), name="memoset-update"),
    path("set/<int:set_id>", MemoSetDeleteView.as_view(), name="memoset-delete"),
]
