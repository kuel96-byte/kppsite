from django.db import models
from django.utils import timezone


# Сначала определяем все константы
class Pass(models.Model):
    # Константы выносим на уровень класса (и обязательно до их использования!)
    PASS_TYPES = (
        ('employee', 'Сотрудник'),
        ('guest', 'Гость'),
        ('temporary', 'Временный'),
    )

    # Теперь поля модели - здесь уже можно использовать PASS_TYPES
    qr_code_data = models.CharField(max_length=100, unique=True, verbose_name="Данные QR-кода")
    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    pass_type = models.CharField(max_length=20, choices=PASS_TYPES, verbose_name="Тип пропуска")
    organization = models.CharField(max_length=100, blank=True, verbose_name="Организация")
    valid_from = models.DateTimeField(default=timezone.now, verbose_name="Действует с")
    valid_until = models.DateTimeField(verbose_name="Действует до")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    photo = models.ImageField(upload_to='pass_photos/', blank=True, null=True, verbose_name="Фото")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.get_pass_type_display()}"

    def is_valid(self):
        """Проверка действительности пропуска"""
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until


class AccessLog(models.Model):
    # Константы для этого класса
    ACCESS_RESULTS = (
        ('granted', 'Разрешен'),
        ('denied', 'Запрещен'),
        ('expired', 'Просрочен'),
    )

    pass_data = models.ForeignKey(Pass, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пропуск")
    qr_code_scanned = models.CharField(max_length=100, verbose_name="Сканированный QR-код")
    access_result = models.CharField(max_length=20, choices=ACCESS_RESULTS, verbose_name="Результат")
    access_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP-адрес")

    def __str__(self):
        return f"{self.access_time} - {self.access_result}"