from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from .models import Category, Comment, Genre, Review, Title, User


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Invalid input.")
    default_code = "invalid"
    default_field = "Error"

    def __init__(self, detail=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {self.default_field: force_text(detail)}
        else:
            self.detail = {"detail": force_text(self.default_detail)}


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username",
                  "bio", "email", "role")
        lookup_field = "username"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug",)
        lookup_field = "slug"
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug",)
        lookup_field = "slug"
        model = Genre


class CategoryField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class GenreField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class TitleSerializerList(serializers.ModelSerializer):
    """
    Сериализатор на чтение
    """
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = "__all__"
        model = Title


class TitleSerializerCreate(serializers.ModelSerializer):
    """
    Сериализатор на запись
    """
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field="slug",
        queryset=Genre.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    text = serializers.CharField(required=True)
    score = serializers.IntegerField(required=True)

    def validate(self, data):
        author_id = self.context["request"].user.id
        method = self.context["request"].method
        title_id = self.context["view"].kwargs.get("title_id")
        author_has_rev = Review.objects.filter(author_id=author_id,
                                               title_id=title_id)
        if author_has_rev and method == "POST":
            raise ValidationError(
                "You have review on this Title1")
        return data

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review
        extra_kwargs = {"score": {"required": True},
                        "author": {"validators": [], },
                        }
        read_only_fields = ("author",)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    text = serializers.CharField(required=True)

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
