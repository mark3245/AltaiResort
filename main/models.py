from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class House(models.Model):
    """Модель домика для отдыха"""
    name = models.CharField(max_length=100, verbose_name="Название домика")
    description = models.TextField(verbose_name="Описание")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость (человек)")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за ночь")
    image = models.ImageField(upload_to='houses/', verbose_name="Фото домика")
    is_available = models.BooleanField(default=True, verbose_name="Доступен для бронирования")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Домик"
        verbose_name_plural = "Домики"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.capacity} мест)"


class Booking(models.Model):
    """Модель бронирования"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name="Домик")
    guest_name = models.CharField(max_length=100, verbose_name="Имя гостя")
    guest_phone = models.CharField(max_length=20, verbose_name="Телефон гостя")
    guest_email = models.EmailField(blank=True, verbose_name="Email гостя")
    check_in_date = models.DateField(verbose_name="Дата заезда")
    check_out_date = models.DateField(verbose_name="Дата выезда")
    guests_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Количество гостей"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    special_requests = models.TextField(blank=True, verbose_name="Особые пожелания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронирование {self.house.name} - {self.guest_name} ({self.check_in_date})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.check_in_date and self.check_out_date:
            if self.check_in_date < timezone.now().date():
                raise ValidationError("Дата заезда не может быть в прошлом")
            if self.check_out_date <= self.check_in_date:
                raise ValidationError("Дата выезда должна быть позже даты заезда")


class Review(models.Model):
    """Модель отзыва"""
    guest_name = models.CharField(max_length=100, verbose_name="Имя гостя")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name="Аватар")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен для публикации")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.guest_name} ({self.rating}/5)"


class GalleryImage(models.Model):
    """Модель изображения для галереи"""
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='gallery/', verbose_name="Изображение")
    alt_text = models.CharField(max_length=200, verbose_name="Alt текст")
    is_featured = models.BooleanField(default=False, verbose_name="Показать на главной")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Изображение галереи"
        verbose_name_plural = "Изображения галереи"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Contact(models.Model):
    """Модель контактной информации"""
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес")
    coordinates_lat = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    coordinates_lng = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")
    working_hours = models.CharField(max_length=100, verbose_name="Время работы")
    telegram = models.URLField(blank=True, verbose_name="Telegram")
    whatsapp = models.URLField(blank=True, verbose_name="WhatsApp")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"

    def __str__(self):
        return "Контактная информация"
