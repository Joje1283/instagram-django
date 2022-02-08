import logging
import re

from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from .models import Post, Comment, Tag
from .serializers import PostSerializer, CommentSerializer

logger = logging.getLogger('django')


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().select_related('author').prefetch_related('tag_set', 'like_user_set')
    serializer_class = PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(
            Q(author=self.request.user) |
            Q(author__in=self.request.user.following_set.all())
        )
        return qs

    @staticmethod
    def extract_tag_list(caption):
        captured_tag_list = []

        for tag_name in re.findall(r'#([a-zA-Z\dㄱ-힣]+)', caption):
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            captured_tag_list.append(tag)
        return captured_tag_list

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, tag_set=self.extract_tag_list(serializer.validated_data['caption']))

    @action(detail=True, methods=['POST'])
    def like(self, request, pk):
        post = self.get_object()
        post.like_user_set.add(self.request.user)
        return Response(status=status.HTTP_201_CREATED)

    @like.mapping.delete
    def unlike(self, request, pk):
        post = self.get_object()
        post.like_user_set.remove(self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(post__pk=self.kwargs['post_pk'])
        return qs

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        serializer.save(author=self.request.user, post=post)
        return super().perform_create(serializer)