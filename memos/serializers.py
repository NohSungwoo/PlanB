from django.contrib.auth import get_user_model
from rest_framework import serializers as s

from memos.models import Memo, MemoSet

User = get_user_model()


class MemoDetailSerializer(s.ModelSerializer):
    memo_set = s.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Memo
        fields = "__all__"


class MemoSetDetailSerializer(s.ModelSerializer):
    user = s.StringRelatedField()

    class Meta:
        model = MemoSet
        fields = "__all__"
