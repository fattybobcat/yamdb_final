from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UsersViewSet)

v1_router = DefaultRouter()
v1_router.register(r"users", UsersViewSet),
v1_router.register("categories", CategoryViewSet)
v1_router.register("genres", GenreViewSet)
v1_router.register("titles", TitleViewSet, basename="titles")


v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet,
    basename="reviews",
)

v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

auth_urlpatterns = [
    path("email/", views.mail_code),
    path("token/", views.get_tokens_for_user),
    path("refresh/",
         TokenRefreshView.as_view(),
         name="token_refresh"),
]

urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("v1/auth/", include(auth_urlpatterns)),
]
