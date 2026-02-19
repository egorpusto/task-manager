from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Идентична стандартной, но готова к расширению —
    можно добавить avatar, timezone, bio
    """

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
