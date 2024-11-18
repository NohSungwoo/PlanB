from django.urls import path

from .views import MemoDetailView, MemoListView, MemoSetDetailView, MemoSetListView

memo_urls = [
    path("", MemoListView.as_view(), name="memo-list"),
    path("<int:memo_id>", MemoDetailView.as_view(), name="memo-detail"),
]

memoset_urls = [
    path("set", MemoSetListView.as_view(), name="memoset-list"),
    path("set/<int:set_id>", MemoSetDetailView.as_view(), name="memoset-detail"),
]

urlpatterns = memo_urls + memoset_urls
