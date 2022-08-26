from multiprocessing import context
from rest_framework import permissions, response
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rating.serializers import ReviewSerializer
from . import serializers
from . models import *
from account.permissions import IsAuthor
from rest_framework.decorators import action
from .serializers import *
from . import serializers
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

class StandartResultsPagination(PageNumberPagination):
    page_size=5
    page_query_param='page'
    max_page_size=1000


class ProductViewSet(ModelViewSet):
    queryset=Recipe.objects.all()
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    filter_backends=(DjangoFilterBackend,SearchFilter)
    filterset_fields=('category',)
    search_fields=('title',)
    pagination_class=StandartResultsPagination



    def get_serializer_class(self):
        if self.action=='list':
            return serializers.RecipeListSerializer

        return serializers.RecipeDetailSerializer

    #api/v1/products/<id>/reviews/
    @action(['GET', 'POST'], detail=True)
    def reviews(self, request, pk=None):
        recipe=self.get_object()
        if request.method=='GET':
            reviews=recipe.reviews.all()
            serializer=ReviewSerializer(reviews, many=True).data
            return response.Response(serializer, status=200)
        data=request.data
        serializer=ReviewSerializer(data=data, context={'request':request, 'recipe':recipe})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=201)
        

    @action(['GET'],detail=True)
    def comments(self,request,pk):
        post=self.get_object()
        comments=post.comments.all()
        serializer=serializers.CommentSerilizer(comments,many=True)
        return Response(serializer.data,status=200)
    
    # api/v1/posts/<id>/add_to_liked/
    @action(['POST'],detail=True)
    def add_to_liked(self,request,pk):
        post=self.get_object()
        if request.user.liked.filter(post=post).exists():
            # request.user.liked.filter(post=post).delete()
            return Response('Вы уже лайкнули этот пост',status=400)
        Likes.objects.create(post=post,owner=request.user)
        return Response('Вы поставили лайк', status=201)

    #api/v1/posts/<id>/remove_from_liked
    @action(['POST'],detail=True)
    def remove_from_liked(self,request,pk):
        post=self.get_object()
        if not request.user.liked.filter(post=post).exists():
            return Response('Вы не лайкали этот пост!',status=400)
        request.user.liked.filter(post=post).delete()
        return Response('Вы убрали ваш лайк',status=204)

    #api/v1/posts/<id>/get_likes
    @action(['GET'],detail=True)
    def get_likes(self,request,pk):
        post=self.get_object()
        likes=post.likes.all()
        serializer=serializers.LikeSerializer(likes,many=True)
        return Response(serializer.data,status=200)


class CommentListCreateView(generics.ListCreateAPIView):
    queryset=Comments.objects.all()
    serializer_class=serializers.CommentSerilizer
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class  CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Comments.objects.all()
    serializer_class=CommentSerilizer
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,IsAuthor)
