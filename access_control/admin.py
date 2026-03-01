from django.contrib import admin
from .models import Pass, AccessLog
from rangefilter.filters import DateRangeFilter

@admin.register(Pass)
class PassAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'pass_type', 'organization', 'is_active', 'valid_until')
    list_filter = ('pass_type', 'is_active')
    search_fields = ('full_name', 'qr_code_data', 'organization')
    fieldsets = (
        ('Владелец', {
            'fields': ('full_name', 'pass_type', 'organization', 'photo')
        }),
        ('QR-код', {
            'fields': ('qr_code_data',)
        }),
        ('Срок действия', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
    )


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('access_time', 'pass_data', 'access_result', 'qr_code_scanned', 'ip_address')
    list_filter = (
        'access_result',
        ('access_time', DateRangeFilter),  # удобный фильтр по датам
    )
    search_fields = ('qr_code_scanned', 'pass_data__full_name')
    readonly_fields = ('access_time',)  # чтобы нельзя было изменить время
    date_hierarchy = 'access_time'  # навигация по датам

    fieldsets = (
        ('Основное', {
            'fields': ('access_time', 'access_result', 'ip_address')
        }),
        ('Данные пропуска', {
            'fields': ('pass_data', 'qr_code_scanned')
        }),
    )