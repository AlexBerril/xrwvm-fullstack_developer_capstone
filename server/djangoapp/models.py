# Uncomment the following imports before adding the Model code

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
# Car Make
class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  # можно оставить пустым

    def __str__(self):
        return self.name


# Car Model
class CarModel(models.Model):
    # связь многие-к-одному: одна марка -> много моделей
    car_make = models.ForeignKey(
        CarMake,
        on_delete=models.CASCADE, 
        related_name="models"
    )
    # ID дилера (из Cloudant). Чётко по заданию — IntegerField
    dealer_id = models.IntegerField()

    name = models.CharField(max_length=100)

    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default='SUV')

    # строго как в задании: min=2015, max=2023
    year = models.IntegerField(
        validators=[
            MinValueValidator(2015),
            MaxValueValidator(2023),
        ]
    )

    def __str__(self):
        return f"{self.car_make.name} {self.name}"
