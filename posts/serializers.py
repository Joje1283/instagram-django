import re
import logging

from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers

from .models import Post, Comment, Tag

logger = logging.getLogger('django')


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'username', 'name',
        ]


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    is_like = serializers.SerializerMethodField('is_like_field')

    def is_like_field(self, post):
        if 'request' in self.context:
            user = self.context['request'].user
            return post.like_user_set.filter(pk=user.pk).exists()
        return False

    class Meta:
        model = Post
        fields = ['id', 'author', 'created_at', 'photo', 'caption', 'location', 'tag_set', 'is_like']


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "message", "created_at"]