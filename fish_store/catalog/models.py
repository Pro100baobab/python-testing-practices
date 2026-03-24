from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError

MAX_TOTAL_PRICE = 1_000_000


class FishProduct(models.Model):
    KIND_CHOICES = [
        ('salmon', 'Salmon'),
        ('cod', 'Cod'),
        ('carp', 'Carp'),
        ('perch', 'Perch'),
        ('other', 'Other'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Название',
        validators=[
            RegexValidator(
                regex=r'^[\w\s\-]+$',
                message='Только буквы, цифры, пробелы и дефисы'
            )
        ]
    )
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, verbose_name='Вид')
    is_fresh = models.BooleanField(verbose_name='Свежая')
    weight_grams = models.FloatField(
        verbose_name='Вес (граммы)',
        validators=[
            MinValueValidator(0, message='Вес должен быть больше 0'),
            MaxValueValidator(500000, message='Вес не может превышать 500 кг')
        ]
    )
    price_per_kg = models.FloatField(
        verbose_name='Цена за кг',
        validators=[
            MinValueValidator(0, message='Цена должна быть больше 0'),
            MaxValueValidator(10000, message='Цена не может превышать 10000 руб/кг')
        ]
    )
    country = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name='Страна происхождения',
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zА-Яа-я\s\-]+$',
                message='Только буквы, пробелы и дефисы'
            )
        ]
    )
    quality_rating = models.IntegerField(
        blank=True, null=True,
        verbose_name='Оценка качества',
        validators=[
            MinValueValidator(1, message='Оценка от 1 до 5'),
            MaxValueValidator(5, message='Оценка от 1 до 5')
        ]
    )

    class Meta:
        verbose_name = 'Рыбный товар'
        verbose_name_plural = 'Рыбные товары'

    def __str__(self):
        return self.name

    @property
    def total_price(self):
        """Общая стоимость = (вес в кг) * цена за кг"""
        return (self.weight_grams / 1000.0) * self.price_per_kg

    def clean(self):
        # Дополнительная валидация общей стоимости
        if self.total_price <= 0:
            raise ValidationError('Общая стоимость должна быть положительной')
        if self.total_price > MAX_TOTAL_PRICE:
            raise ValidationError(f'Общая стоимость не может превышать {MAX_TOTAL_PRICE} руб.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
