from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


class Employee(models.Model):
    class Genders(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        UNKNOWN = '', _('Unknown')

    first_name = models.CharField(max_length=128, blank=False, null=False)
    last_name = models.CharField(max_length=128, blank=False, null=False)
    email = models.EmailField(max_length=256, blank=True, null=False, default='')
    gender = models.CharField(max_length=1, choices=Genders.choices, blank=True, null=False, default=Genders.UNKNOWN)
    date_of_birth = models.DateField(default=None, null=True) # TODO add custom validation
    industry = models.CharField(max_length=256, default='', blank=True, null=False)
    salary = models.FloatField(default=None, null=True, blank=True,
                               validators=[MinValueValidator(0.0),
                                           MaxValueValidator(1e12)])
    years_of_experience = models.PositiveSmallIntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.last_name}, {self.first_name}' + (f' at {self.email}' if self.email else '')
