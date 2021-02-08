import os

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitlesFilter
from .models import Category, Genre, Title, User
from .permissions import (IsAdminOrReadOnly, IsAuthOnlyCreateOnceOrReadOnly,
                          IsAuthorOrAdmin, IsAuthorOrModerAdminCrOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleSerializerCreate, TitleSerializerList,
                          UserSerializer)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_yamdb.settings")


@api_view(["POST"])
@permission_classes([AllowAny])
def mail_code(request):
    token = PasswordResetTokenGenerator()
    email = request.POST["email"]
    new_username = "".join(email.split("@")[0])
    User.objects.get_or_create(email=email,
                               password=email,
                               username=new_username)
    user = get_object_or_404(User, email=email)
    confirmation_code = token.make_token(user)
    send_mail(
        "Тема письма",
        f"Текст письма: {confirmation_code}",
        "settings.EMAIL_HOST_USER",
        [email],
        fail_silently=False,
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def get_tokens_for_user(request):
    token = PasswordResetTokenGenerator()
    email = request.POST["email"]
    confirmation_code = request.POST["confirmation_code"]
    user = get_object_or_404(User, email=email)
    if token.check_token(user, confirmation_code) is True:
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

    return Response(status=status.HTTP_404_NOT_FOUND)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ["sername", ]
    authentication_classes = [JWTAuthentication]
    pagination_class = PageNumberPagination
    lookup_field = "username"
    permission_classes = [IsAuthorOrAdmin]

    @action(methods=["GET", "PATCH"],
            detail=False,
            permission_classes=[IsAuthenticated], )
    def me(self, request, pk=None):
        user = get_object_or_404(
            User,
            username=request.user.username
        )
        serializer = UserSerializer(user)
        if request.method == "PATCH":
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
        return Response(serializer.data)


class CatalogViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin,
                     GenericViewSet):
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    lookup_field = "slug"


class CategoryViewSet(CatalogViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer


class GenreViewSet(CatalogViewSet):
    queryset = Genre.objects.all().order_by("id")
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TitleSerializerCreate
        return TitleSerializerList

    def get_queryset(self):
        queryset = Title.objects.all()
        Title.objects.update(
            rating=Subquery(
                Title.objects.filter(
                    id=OuterRef("id")
                ).annotate(
                    avg_rating=Avg("reviews__score")
                 ).values("avg_rating")[:1]
            )
        )
        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for operations with review.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthOnlyCreateOnceOrReadOnly,)

    def perform_create(self, serializer):
        titles = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        #if Review.objects.filter(author=self.request.user, title_id=title).exists() raise ////#
        serializer.save(author=self.request.user, title_id=titles.id)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        queryset = title.reviews.all()
        return queryset

    def perform_update(self, serializer):
        titles = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title_id=titles.id)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for operations with comments.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModerAdminCrOrReadOnly, )

    def get_queryset(self):
        titles = get_object_or_404(Title,
                                   pk=self.kwargs.get("title_id"))
        reviews = get_object_or_404(titles.reviews.all(),
                                    pk=self.kwargs.get("review_id"))
        queryset = reviews.comments.all()
        return queryset

    def perform_create(self, serializer):
        titles = get_object_or_404(Title,
                                   pk=self.kwargs.get("title_id"))
        reviews = get_object_or_404(titles.reviews.all(),
                                    pk=self.kwargs.get("review_id"))
        serializer.save(author_id=self.request.user.id,
                        review_id=reviews.id)
