from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib import messages
import qrcode
from io import BytesIO
import base64
from .models import Pass, AccessLog


@admin.register(Pass)
class PassAdmin(admin.ModelAdmin):
    list_display = ('qr_code_data', 'full_name', 'pass_type', 'organization', 'is_active', 'show_photo', 'show_qr_code',
                    'print_button')
    list_filter = ('pass_type', 'is_active')
    search_fields = ('qr_code_data', 'full_name', 'organization')
    readonly_fields = ('qr_code_image', 'show_qr_code_preview', 'created_at', 'print_button_detail')

    fieldsets = (
        ('Основная информация', {
            'fields': ('qr_code_data', 'full_name', 'pass_type', 'organization')
        }),
        ('Фото и QR-код', {
            'fields': ('photo', 'show_photo_preview', 'qr_code_image', 'show_qr_code_preview'),
            'classes': ('wide',)
        }),
        ('Срок действия', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Печать', {
            'fields': ('print_button_detail',),
            'classes': ('wide',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('print-pass/<int:pass_id>/', self.admin_site.admin_view(self.print_pass_view), name='print-pass'),
        ]
        return custom_urls + urls

    def print_button(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">🖨️ Печать</a>',
            f'/admin/access_control/pass/print-pass/{obj.id}/'
        )

    print_button.short_description = 'Печать'
    print_button.allow_tags = True

    def print_button_detail(self, obj):
        if obj.id:
            return format_html(
                '<a class="button" href="{}" target="_blank" style="background: #28a745; padding: 10px 20px; font-size: 16px;">🖨️ Распечатать пропуск</a>',
                f'/admin/access_control/pass/print-pass/{obj.id}/'
            )
        return "Сохраните пропуск перед печатью"

    print_button_detail.short_description = ''

    def show_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 5px;" />', obj.photo.url)
        return "📷 Нет фото"

    show_photo.short_description = "Фото"

    def show_photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 200px; border-radius: 10px;" />', obj.photo.url)
        return "Фото не загружено"

    show_photo_preview.short_description = "Предпросмотр фото"

    def show_qr_code(self, obj):
        if obj.qr_code_image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.qr_code_image.url)
        return "🔳 Нет QR"

    show_qr_code.short_description = "QR-код"

    def show_qr_code_preview(self, obj):
        if obj.qr_code_image:
            return format_html('<img src="{}" style="max-width: 200px; border: 1px solid #ddd; padding: 5px;" />',
                               obj.qr_code_image.url)
        return "QR-код будет сгенерирован автоматически"

    show_qr_code_preview.short_description = "Предпросмотр QR-кода"

    def print_pass_view(self, request, pass_id):
        try:
            pass_obj = Pass.objects.get(id=pass_id)

            # Подготавливаем данные для шаблона
            context = {
                'pass_obj': pass_obj,
                'title': f'Пропуск - {pass_obj.full_name}',
                'opts': self.model._meta,
                'media': self.media,
            }

            return TemplateResponse(request, 'admin/print_pass.html', context)

        except Pass.DoesNotExist:
            messages.error(request, 'Пропуск не найден')
            return redirect('admin:access_control_pass_changelist')