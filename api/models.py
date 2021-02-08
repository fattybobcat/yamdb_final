from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import my_year_validator


class RoleUser(models.TextChoices):
    USER = "user", _("user")
    MODERATOR = "moderator", _("moderator")
    ADMIN = "admin", _("admin")


class User(AbstractUser):

    bio = models.TextField(null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=50, unique=True, blank=False)
    role = models.CharField(
        max_length=9,
        choices=RoleUser.choices,
        blank=False,
        default=RoleUser.USER,
    )

    @property
    def is_admin(self):
        if self.role == RoleUser.ADMIN or self.is_superuser:
            return True

    @property
    def is_moderator(self):
        if self.role == RoleUser.MODERATOR or self.is_staff:
            return True


class Category(models.Model):
    name = models.CharField(max_length=300,
                            verbose_name="Категория",
                            unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=300, verbose_name="Жанр", unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=300)
    year = models.IntegerField(null=True,
                               blank=True,
                               db_index=True,
                               validators=[my_year_validator])
    description = models.CharField(max_length=1000, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, verbose_name="Жанр")
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 blank=True,
                                 null=True,
                                 related_name="titles",
                                 verbose_name="Категория")

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return f"{self.name} ({self.year}г.)"


class Review(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="reviews",
                               verbose_name="Автор")
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name="reviews",
                              verbose_name="Произведение",)
    text = models.TextField()
    pub_date = models.DateTimeField("Дата добавления",
                                    auto_now_add=True,
                                    db_index=True)
    score = models.PositiveIntegerField(default=None,
                                        validators=[MinValueValidator(1),
                                                    MaxValueValidator(10)],
                                        null=True,
                                        blank=False,
                                        verbose_name="Оценка"
                                        )

    class Meta:
        verbose_name = "Обзор"
        verbose_name_plural = "Обзоры"


class Comment(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор",)
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Отзыв",)
    text = models.TextField()
    pub_date = models.DateTimeField("Дата добавления",
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
