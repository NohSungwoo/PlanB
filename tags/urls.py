from django.urls import path

from .views import (
    TagCreateView,
    TagDeleteView,
    TagDetailView,
    TagLabelView,
    TagListView,
    TagUpdateView,
)

urlpatterns = [
    path("", TagCreateView.as_view(), name="tag-create"),
    path("<int:tag_id>/label", TagLabelView.as_view(), name="tag-label"),
    path("<int:tag_id>", TagDeleteView.as_view(), name="tag-delete"),
    path("<int:tag_id>", TagUpdateView.as_view(), name="tag-update"),
    path("", TagListView.as_view(), name="tag-list"),
    path("<int:tag_id>", TagDetailView.as_view(), name="tag-detail"),
]
