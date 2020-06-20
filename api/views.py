from rest_framework  import viewsets, permissions, generics, filters, exceptions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import models

from .models import Post, Comment, Group, Follow, User
from .serializers import PostSerializer, CommentSerializer, GroupSerializer, FollowSerializer
from .permissions import AuthorRightPermission

  
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AuthorRightPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group',]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AuthorRightPermission]
    
    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(post=self.kwargs['post_id'])
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AuthorRightPermission]


class FollowList(generics.ListCreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [AuthorRightPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=user__username', '=following__username']
   
    def perform_create(self, serializer):
        try:
            following = User.objects.get(username=self.request.data.get('following'))
        except models.User.DoesNotExist:
            raise exceptions.ValidationError('not validation')
        if Follow.objects.filter(user=self.request.user, following=following).exists():
            raise exceptions.ValidationError('not validation')
        serializer.save(user=self.request.user, following=following)
