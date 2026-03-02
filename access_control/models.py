from django.db import models
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File


class Pass(models.Model):
    PASS_TYPES = (
        ('employee', 'Сотрудник'),
        ('guest', 'Гость'),
        ('temporary', 'Временный'),
    )

    qr_code_data = models.CharField(max_length=100, unique=True, verbose_name="Данные QR-кода")
    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    pass_type = models.CharField(max_length=20, choices=PASS_TYPES, verbose_name="Тип пропуска")
    organization = models.CharField(max_length=100, blank=True, verbose_name="Организация")

    # Фото сотрудника
    photo = models.ImageField(upload_to='photos/', blank=True, null=True, verbose_name="Фото сотрудника")

    # Сгенерированный QR-код (картинка)
    qr_code_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True, verbose_name="QR-код (изображение)")

    valid_from = models.DateTimeField(default=timezone.now, verbose_name="Действует с")
    valid_until = models.DateTimeField(verbose_name="Действует до")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.get_pass_type_display()}"

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until

    def save(self, *args, **kwargs):
        # Сначала сохраняем, чтобы получить id
        super().save(*args, **kwargs)

        # Генерируем QR-код если его еще нет
        if not self.qr_code_image:
            try:
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(self.qr_code_data)
                qr.make(fit=True)

                qr_image = qr.make_image(fill_color="black", back_color="white")

                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                buffer.seek(0)

                filename = f'qr_{self.qr_code_data}_{self.id}.png'
                self.qr_code_image.save(filename, File(buffer), save=False)
                super().save(*args, **kwargs)

            except Exception as e:
                print(f"Ошибка генерации QR-кода: {e}")


# 👇 ВОТ ЭТОТ КЛАСС ОБЯЗАТЕЛЬНО ДОЛЖЕН БЫТЬ!
class AccessLog(models.Model):
    """Логи доступа"""
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