from django.urls import path

from .views import TagDetailView, TagLabelView, TagListView

urlpatterns = [
    path("<int:tag_id>/label", TagLabelView.as_view(), name="tag-label"),
    path("", TagListView.as_view(), name="tag-list"),
    path("<int:tag_id>", TagDetailView.as_view(), name="tag-detail"),
]
