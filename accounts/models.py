from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class GenderChoices(models.TextChoices):
        MALE = 'M', '남성'
        FEMALE = 'F', '여성'

    follower_set = models.ManyToManyField('self', blank=True)
    following_set = models.ManyToManyField('self', blank=True)

    website_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(validators=[RegexValidator(r'010-?[1-9]\d{3}-?\d{4}$')], max_length=13, blank=True)
    gender = models.CharField(choices=GenderChoices.choices, max_length=1, blank=True)

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'.strip()
